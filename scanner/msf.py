"""Momentum Setup Finder (MSF) daily engine — a line-by-line Python port of the Pine script.

The Pine script runs once per daily bar, oldest to newest; so does `run()` below. Offsets in the
comments ("o bars ago") map to index i - o. Every setting from the Pine inputs is in DEFAULTS
(v29.1) and V28 holds the old values, so both versions can be run on the same charts.

Differences from TradingView that cannot be avoided:
  * Relative volume on daily bars = day volume / average of the previous `volLook` days (on closed
    daily bars the Pine time-of-day RVOL works out to the same thing).
  * 52-week high / low use the bars available when a stock has less than 252 bars of history.
"""
import math

import numpy as np
from numba import njit

NAN = np.nan
NAI = -1_000_000_000  # "na" for integer bar indexes

# ───────────────────────────── settings ─────────────────────────────
DEFAULTS = dict(
    # Filters
    req200=1, minPrice=10.0, minDolVol=20.0, dolVolLen=30, nearHiPct=25.0, nhMom=50.0, nhMomBars=30,
    gapAboveLo=30.0, nearPct=5.0, calcBars=400,
    # Your entries: 2nd-pullback tight day, coil
    swAdrX=1.5, swMinPct=6.0, swMaxPct=12.0, pbMin=2, pbMaxDepth=30.0, tightBodyX=0.35, tightUseRng=0,
    tightRangeX=0.8, coilInside=1, coilEntryMother=0, coilBodyX=0.5, coilBodyAdr=0.5, coilOpenReq=0,
    # Base finder
    maxLook=150, sigPct=30.0, olderNear=15.0, mergeDep=35.0, topTol=2.0, minBase=5, maxDep=37.0,
    priorLook=60, crashX=1.75, crashBars=15, bigOn=1, rearm=5,
    # 1 High tight flag
    htfPole=80.0, htfPoleBars=45, htfMin=12, htfMax=30, htfDepMin=10.0, htfDep=25.0,
    # 8/9 Bull flag / pennant
    flOn=1, flMin=5, flMax=15, flDepMin=10.0, flDepMax=20.0, flAnchor=2.5, flChan=2.5, flPar=0.5,
    flConv=0.7, flPole=30.0, flPoleBars=20, flTouch=1.5, flSlope=3.0, flVol=1.5,
    # 12 Tight flag
    tfOn=1, tfTouch=3, tfTol=1.5, tfWide=1.0,
    # 2/3 Cup
    cupMin=35, cupDepMin=12.0, cupDepMax=35.0, cupPrior=50.0, hdlMin=5, hdlMax=20, hdlDep=12.0, hdlNear=15.0,
    # 4 Ascending triangle
    atMin=10, atMax=65, atTol=2.0, atDep=30.0,
    # 5 Qullamaggie
    qMin=10, qMax=40, qPrior=30.0, qDep=30.0, q50=85.0, qUndercut=3.0, qOne=1, qOnePct=80.0,
    q50All=1,   # v29: the q50 rule applies to every pattern
    qUseEma=1,  # v29: counted on the daily 50 EMA (v28: 50 SMA)
    # 6 Flat base
    fbMin=25, fbLong=25, fbDep=15.0, fbShortDep=10.0, fbTop=3.0, fbPrior=20.0,
    # 7 Base breakout
    genOn=1, genMin=15, genDep=35.0, genPrior=20.0,
    # 11 Deep base
    deepOn=1, deepMin=15, deepMax=37.0, deepPrior=20.0,
    # Level breakout
    lvlOn=1, lvlGap=10, lvlAfter=10, lvlPb=12.0, lvlRun=30.0, lvlRunBars=30, lvlDep=50.0,
    # Flat-top breakout
    ftOn=1, ftMin=10, ftMax=30, ftTouch=3, ftTol=2.0, ftSpan=5, ftDep=25.0, ftCool=5, ftMerge=1, ftVisTop=4.0,
    # EP / gap out of base
    epGap=10.0, gbGap=5.0, gbClearOpen=0, gbBaseLen=30, gbMaxDep=30.0,
    # Volume
    volLook=20, volEpX=2.0, volGbX=2.0, volHTF=3.0, volFP=0.0, volTF=0.7, volCup=0.0, volAT=0.0, volQ=0.0,
    volFB=2.0, volGen=0.0, volDeep=0.0, volLvl=0.0, volBig=0.0, volFT=0.0,
    # Grade
    grAplLo=10.0, grAplHi=15.0, grAHi=20.0, grBHi=30.0, grHiAdr=8.0, gr200=0, grHHHL=1,
)
V28 = dict(DEFAULTS, minPrice=5.0, minDolVol=10.0, dolVolLen=20, coilInside=2, maxDep=50.0, deepMax=50.0,
           q50=80.0, q50All=0, qUseEma=0)

KEYS = list(DEFAULTS)
for _n, _k in enumerate(KEYS):
    globals()["K_" + _k] = _n   # numba reads these as constants


def params(over=None, base=DEFAULTS):
    d = dict(base, **(over or {}))
    return np.array([float(d[k]) for k in KEYS])


NAMES = ["None", "High tight flag", "Cup with handle", "Cup (no handle)", "Ascending triangle", "Qullamaggie breakout",
         "Flat base", "Base breakout", "Bull flag", "Pennant", "Base forming (no pattern yet)", "Deep base breakout",
         "Tight flag"]

# output columns
OUT = ["code", "pivot", "cS", "cT", "cN", "cDep", "cPri", "cEP", "cLow", "cQ", "cH", "tlLive",
       "bo", "boCode", "boBuy", "boS", "boClosedAbove", "bigBO", "bigBuy", "bigS", "ftBO", "ftBuy", "ftS",
       "lvBO", "lvBuy", "lvLevel", "lvSame", "lvCup", "flHit", "flHitLvl",
       "early", "earlyStop", "coilMark", "earlyTrig", "earlyTry", "inCnt",
       "hlTrig", "hlStop", "hlDone", "pbMarked", "hlHit", "hlPbNum",
       "cLvTrig", "cLvR", "cLvJ", "cLvCup", "cBigBuy", "cBigS", "cBigCode", "cFTBuy", "cFTS",
       "grade", "hhhl", "trendA", "pb20", "score", "dist", "liquid", "above200", "isGap", "isGapBase",
       "adr", "ema10", "ema21", "ema50", "sma50", "sma200", "rvol", "dolVol", "gapPct", "boStop"]
for _n, _k in enumerate(OUT):
    globals()["C_" + _k] = _n
NOUT = len(OUT)


# ───────────────────────────── series helpers (Pine semantics) ─────────────────────────────
@njit(cache=True, error_model="numpy")
def sma(x, n):
    out = np.full(x.size, NAN)
    s = 0.0
    for i in range(x.size):
        s += x[i]
        if i >= n:
            s -= x[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


@njit(cache=True, error_model="numpy")
def ema(x, n):
    out = np.full(x.size, NAN)
    a = 2.0 / (n + 1)
    if x.size < n:
        return out
    s = 0.0
    for i in range(n):
        s += x[i]
    out[n - 1] = s / n
    for i in range(n, x.size):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


@njit(cache=True, error_model="numpy")
def highest(x, n, minp):
    out = np.full(x.size, NAN)
    for i in range(x.size):
        if i + 1 < minp:
            continue
        m = x[i]
        for k in range(1, n):
            if i - k < 0:
                break
            if x[i - k] > m:
                m = x[i - k]
        out[i] = m
    return out


@njit(cache=True, error_model="numpy")
def lowest(x, n, minp):
    out = np.full(x.size, NAN)
    for i in range(x.size):
        if i + 1 < minp:
            continue
        m = x[i]
        for k in range(1, n):
            if i - k < 0:
                break
            if x[i - k] < m:
                m = x[i - k]
        out[i] = m
    return out


@njit(cache=True, error_model="numpy")
def isna(x):
    return x != x


@njit(cache=True, error_model="numpy")
def nzi(x, d):
    return d if x == NAI else x


@njit(cache=True, error_model="numpy")
def fmin(a, b):  # running min where a may be na (Pine: na(a) ? b : math.min(a, b))
    return b if a != a else (a if a < b else b)


@njit(cache=True, error_model="numpy")
def fmax(a, b):
    return b if a != a else (a if a > b else b)


# ───────────────────────────── pattern functions ─────────────────────────────
@njit(cache=True, error_model="numpy")
def rise_into(H, L, i, jo, priorLook):
    T = H[i - jo]
    lo = L[i - jo]
    k = jo + 1
    while k <= i and k - jo <= priorLook:
        if H[i - k] > T:
            break
        if L[i - k] < lo:
            lo = L[i - k]
        k += 1
    return 100 * (T / lo - 1)


@njit(cache=True, error_model="numpy")
def flag_line(H, L, i, so, T, dMin, P):
    flAnchor = P[K_flAnchor]
    flOn = P[K_flOn] > 0
    flMin = int(P[K_flMin]); flMax = int(P[K_flMax])
    flPoleBars = int(P[K_flPoleBars]); flPole = P[K_flPole]
    flDepMax = P[K_flDepMax]; flTouch = P[K_flTouch]
    nb = so + 1
    lw = NAN
    for o in range(0, so + 1):
        lw = fmin(lw, L[i - o])
    dep = 100 * (1 - lw / T)
    tl = NAN
    if flAnchor > 0:
        if flOn and so >= 4 and nb >= flMin and nb <= flMax:
            pLo = NAN
            for o in range(so, min(so + flPoleBars, i) + 1):
                pLo = fmin(pLo, L[i - o])
            if 100 * (T / pLo - 1) >= flPole:
                ao = NAI
                for o in range(4, so + 1):
                    if H[i - o] >= T * (1 - flAnchor / 100):
                        ao = o
                        break
                if ao != NAI:
                    A = H[i - ao]
                    fl = NAN
                    for o in range(0, ao + 1):
                        fl = fmin(fl, L[i - o])
                    fdep = 100 * (1 - fl / A)
                    if fdep >= dMin and fdep <= flDepMax:
                        sl = NAN
                        for o in range(0, ao):
                            v = (H[i - o] - A) / (ao - o)
                            sl = fmax(sl, v)
                        if sl <= 0:
                            t = 1
                            for o in range(0, ao):
                                if H[i - o] >= (A + sl * (ao - o)) * (1 - flTouch / 100):
                                    t += 1
                            if t >= 2:
                                tl = A + sl * (ao + 1)
    elif flOn and so >= 1 and nb >= flMin and nb <= flMax and dep >= dMin and dep <= flDepMax:
        pLo = NAN
        for o in range(so, min(so + flPoleBars, i) + 1):
            pLo = fmin(pLo, L[i - o])
        if 100 * (T / pLo - 1) >= flPole:
            sl = NAN
            for o in range(0, so):
                v = (H[i - o] - T) / (so - o)
                sl = fmax(sl, v)
            if sl <= 0:
                t = 0
                for o in range(0, so):
                    if H[i - o] >= (T + sl * (so - o)) * (1 - flTouch / 100):
                        t += 1
                if t >= 2:
                    tl = T + sl * (so + 1)
    return tl


@njit(cache=True, error_model="numpy")
def flag_shape(H, L, i, so, P):
    flChan = P[K_flChan]; flPar = P[K_flPar]; flConv = P[K_flConv]
    m = so
    sx = 0.0; sxx = 0.0; sh = 0.0; sl = 0.0; sxh = 0.0; sxl = 0.0
    for o in range(so - 1, -1, -1):
        x = so - 1 - o
        sx += x; sxx += x * x
        sh += H[i - o]; sl += L[i - o]
        sxh += x * H[i - o]; sxl += x * L[i - o]
    den = m * sxx - sx * sx
    slH = (m * sxh - sx * sh) / den if den != 0 else 0.0
    slL = (m * sxl - sx * sl) / den if den != 0 else 0.0
    h = m // 2
    h1 = NAN; l1 = NAN; h2 = NAN; l2 = NAN
    for o in range(so - 1, so - h - 1, -1):
        h1 = fmax(h1, H[i - o]); l1 = fmin(l1, L[i - o])
    for o in range(so - h - 1, -1, -1):
        h2 = fmax(h2, H[i - o]); l2 = fmin(l2, L[i - o])
    r1 = h1 - l1
    r2 = h2 - l2
    mid = (sh + sl) / (2 * m)
    dh = -100 * slH * (m - 1) / mid
    dl = -100 * slL * (m - 1) / mid
    res = 0
    if dh >= flChan and dl >= flChan and slH != 0 and slL / slH >= flPar and slL / slH <= 1 / flPar and r2 >= r1 * flConv:
        res = 8
    elif dh >= flChan and dl <= -0.4 * flChan and r2 < r1 * flConv:
        res = 9
    return res


@njit(cache=True, error_model="numpy")
def tight_flag(H, L, i, so, T, P):
    flMin = int(P[K_flMin]); flMax = int(P[K_flMax])
    flPoleBars = int(P[K_flPoleBars]); flPole = P[K_flPole]; flAnchor = P[K_flAnchor]
    flDepMin = P[K_flDepMin]; tfWide = P[K_tfWide]; tfTol = P[K_tfTol]; tfTouch = int(P[K_tfTouch])
    nb = so + 1
    res = NAN
    if P[K_tfOn] > 0 and so >= 4 and nb >= flMin and nb <= flMax:
        pLo = NAN
        for o in range(so, min(so + flPoleBars, i) + 1):
            pLo = fmin(pLo, L[i - o])
        if 100 * (T / pLo - 1) >= flPole:
            ao = NAI
            A = T
            if flAnchor > 0:
                for o in range(4, so + 1):
                    if H[i - o] >= T * (1 - flAnchor / 100):
                        ao = o
                        break
                if ao != NAI:
                    A = H[i - ao]
            else:
                ao = so
            if ao != NAI:
                fl = NAN
                for o in range(0, ao + 1):
                    fl = fmin(fl, L[i - o])
                if 100 * (1 - fl / A) < flDepMin:
                    h = so // 2
                    h1 = NAN; l1 = NAN; h2 = NAN; l2 = NAN
                    for o in range(so - 1, so - h - 1, -1):
                        h1 = fmax(h1, H[i - o]); l1 = fmin(l1, L[i - o])
                    for o in range(so - h - 1, -1, -1):
                        h2 = fmax(h2, H[i - o]); l2 = fmin(l2, L[i - o])
                    if h2 - l2 <= (h1 - l1) * tfWide:
                        cl = NAN
                        for o in range(0, so + 1):
                            c = H[i - o]
                            if isna(cl) or c > cl:
                                n = 0
                                for q in range(0, so + 1):
                                    if H[i - q] >= c * (1 - tfTol / 100) and H[i - q] <= c:
                                        n += 1
                                if n >= tfTouch:
                                    cl = c
                        res = T if isna(cl) else cl
    return res


@njit(cache=True, error_model="numpy")
def find_base(H, L, C, i, isGap, loMom_i, hi52_i, lastBO, failS, failBar, P):
    maxLook = int(P[K_maxLook]); sigPct = P[K_sigPct]; olderNear = P[K_olderNear]; mergeDep = P[K_mergeDep]
    topTol = P[K_topTol]; minBase = int(P[K_minBase]); maxDep = P[K_maxDep]; priorLook = int(P[K_priorLook])
    nhMom = P[K_nhMom]; nearHiPct = P[K_nearHiPct]
    resSo = NAI; resJo = NAI; resT = NAN
    lim = min(maxLook - 1, i)
    cands = np.empty(lim + 1, np.int64)
    nC = 0
    M = NAN
    for o in range(0, lim + 1):
        if isna(M) or H[i - o] > M:
            M = H[i - o]
            cands[nC] = o
            nC += 1
    sigs = np.zeros(nC, np.bool_)
    for k in range(nC):
        sigs[k] = rise_into(H, L, i, cands[k], priorLook) >= sigPct
    for ci in range(nC):
        jo = cands[ci]
        T = H[i - jo]
        if sigs[ci]:
            older = NAN
            oOff = NAI
            for k in range(ci + 1, nC):
                if sigs[k]:
                    oOff = cands[k]
                    older = H[i - oOff]
                    break
            olderIsTop = False
            if not isna(older) and older <= T * (1 + olderNear / 100):
                oLow = NAN; oLowC = NAN
                for o in range(0, oOff + 1):
                    oLow = fmin(oLow, L[i - o]); oLowC = fmin(oLowC, C[i - o])
                olderIsTop = 100 * (1 - oLow / older) <= mergeDep or (older <= T * (1 + topTol / 100) and 100 * (1 - oLowC / C[i - oOff]) <= mergeDep)
            if not olderIsTop:
                so = jo
                maxBack = i if lastBO == NAI else i - lastBO
                kk = jo + 1
                while kk <= maxBack and kk - jo <= 60:
                    if H[i - kk] > T:
                        break
                    if H[i - kk] >= T * (1 - topTol / 100) and (kk == i or H[i - kk] >= H[i - kk - 1]) and rise_into(H, L, i, kk, priorLook) >= sigPct:
                        so = kk
                    kk += 1
                if failS != NAI and jo == i - failBar and i - failS > so:
                    so = i - failS
                ok = so + 1 >= minBase and (lastBO == NAI or i - so >= lastBO)
                if ok:
                    epNear = False
                    for o in range(so, min(so + 40, i) + 1):
                        if isGap[i - o]:
                            epNear = True
                    mom = 100 * (T / loMom_i - 1) >= nhMom
                    if not epNear and not mom and T < hi52_i * (1 - nearHiPct / 100):
                        ok = False
                if ok:
                    bl = NAN
                    for o in range(0, so + 1):
                        bl = fmin(bl, L[i - o])
                    if 100 * (1 - bl / T) > maxDep:
                        ok = False
                if ok:
                    resSo = so; resJo = jo; resT = T
                break
    return resSo, resJo, resT


@njit(cache=True, error_model="numpy")
def classify(O, H, L, C, i, so, T, ema50, sma50, sma20c, adr, isGap, thPct, P):
    code = 0
    buy = NAN
    nb = so + 1
    lowv = NAN
    li = NAI
    for o in range(so, -1, -1):
        if isna(lowv) or L[i - o] < lowv:
            lowv = L[i - o]
            li = o
    dep = 100 * (1 - lowv / T)
    pw = NAN
    for o in range(so, min(so + int(P[K_priorLook]), i) + 1):
        pw = fmin(pw, L[i - o])
    prior = 100 * (T / pw - 1)
    epPole = False
    for o in range(0, min(so + 40, i) + 1):
        if isGap[i - o]:
            epPole = True
    tlOut = NAN
    qAlso = False
    htfAlso = False
    crashX = P[K_crashX]
    adrPre = adr[i - min(so + 1, i)]
    blocked = False
    if nb < P[K_crashBars] and so >= 1:
        bd = 0.0
        for o in range(0, so):
            bd = max(bd, 100 * (1 - C[i - o] / C[i - o - 1]))
        if bd >= crashX * adrPre:
            blocked = True
    q50 = P[K_q50]
    if P[K_q50All] > 0 and not blocked:
        a50b = 0
        for o in range(0, so + 1):
            if C[i - o] >= ema50[i - o]:
                a50b += 1
        if 100.0 * a50b / nb < q50:
            blocked = True
    if not blocked:
        # High tight flag numbers
        htfB = NAN
        pl = NAN
        for o in range(so, min(so + int(P[K_htfPoleBars]), i) + 1):
            pl = fmin(pl, L[i - o])
        if so >= P[K_htfMin] and so <= P[K_htfMax] and 100 * (T / pl - 1) >= P[K_htfPole]:
            spike = so < i and O[i - so] >= C[i - so - 1] * 1.05 and H[i - so] == T
            fh = NAN; fl2 = NAN
            for o in range(0, so):
                fh = fmax(fh, H[i - o]); fl2 = fmin(fl2, L[i - o])
            hb = fh if spike else T
            flo = fl2 if spike else lowv
            if 100 * (1 - flo / hb) >= P[K_htfDepMin] and 100 * (1 - flo / hb) <= P[K_htfDep]:
                htfB = hb
        # 2/3 Cup with / without handle
        hdlNear = P[K_hdlNear]; hdlMin = int(P[K_hdlMin]); hdlMax = int(P[K_hdlMax])
        if code == 0 and nb >= P[K_cupMin] and dep >= P[K_cupDepMin] and dep <= P[K_cupDepMax] and prior >= P[K_cupPrior] and so - li >= 5 and li >= 5:
            rO = NAI
            rHi = NAN
            for o in range(li - 1, -1, -1):
                if isna(rHi) or H[i - o] > rHi:
                    rHi = H[i - o]
                    rO = o
            if rHi >= T * (1 - hdlNear / 100):
                if rO >= hdlMin and rO <= hdlMax:
                    hl = NAN
                    for o in range(rO - 1, -1, -1):
                        hl = fmin(hl, L[i - o])
                    if 100 * (1 - hl / rHi) <= P[K_hdlDep] and hl > (T + lowv) / 2:
                        code = 2
                        buy = rHi
                elif rO < hdlMin and rHi >= T * 0.95:
                    code = 3
                    buy = T
        up50 = C[i] > ema50[i]
        # 4 Ascending triangle
        if code == 0 and up50 and so >= 2 and nb >= P[K_atMin] and nb <= P[K_atMax] and dep <= P[K_atDep]:
            tests = 1
            aUp = True
            aHi = T
            aLo = NAN
            aN = 0
            aLast = NAN
            aInc = True
            counted = True
            atTol = P[K_atTol]
            for o in range(so - 1, -1, -1):
                h = H[i - o]; l = L[i - o]
                if aUp:
                    if h > aHi:
                        aHi = h
                    elif l <= aHi * (1 - thPct / 100):
                        aUp = False
                        aLo = l
                else:
                    if l < aLo:
                        aLo = l
                    elif h >= aLo * (1 + thPct / 100):
                        aUp = True
                        aHi = h
                        if aN > 0 and aLo <= aLast:
                            aInc = False
                        aLast = aLo
                        aN += 1
                        counted = False
                if aUp and not counted and h >= T * (1 - atTol / 100):
                    tests += 1
                    counted = True
            okL = aN >= 2 and aInc
            if okL and not aUp and not isna(aLo) and aLo <= aLast:
                okL = False
            if tests >= 2 and okL:
                code = 4
                buy = T
                htfAlso = not isna(htfB)
        # 12 Tight flag
        if code == 0 and P[K_tfOn] > 0 and so >= 4:
            tfb = tight_flag(H, L, i, so, T, P)
            if not isna(tfb):
                code = 12
                buy = tfb
                htfAlso = not isna(htfB)
                tl12 = flag_line(H, L, i, so, T, 0.0, P)
                if not isna(tl12) and tl12 <= T * (1 - P[K_flSlope] / 100) and tl12 < tfb:
                    tlOut = tl12
        # 8/9 Bull flag / pennant
        if code == 0 and so >= 4:
            fl = flag_line(H, L, i, so, T, P[K_flDepMin], P)
            if not isna(fl) and fl <= T * (1 - P[K_flSlope] / 100):
                shp = flag_shape(H, L, i, so, P)
                if shp > 0:
                    code = shp
                    buy = T
                    tlOut = fl
                    htfAlso = not isna(htfB)
        # 1 High tight flag
        if code == 0 and not isna(htfB):
            code = 1
            buy = htfB
        # 5 Qullamaggie breakout
        if (code == 0 or code == 1 or code == 4 or code == 8 or code == 9 or code == 12) and up50 and so >= 2 and nb >= P[K_qMin] and nb <= P[K_qMax] and prior >= P[K_qPrior] and dep <= P[K_qDep]:
            a50 = 0
            a20 = 0
            useE = P[K_qUseEma] > 0
            for o in range(0, so + 1):
                ma = ema50[i - o] if useE else sma50[i - o]
                if C[i - o] >= ma:
                    a50 += 1
                if C[i - o] > sma20c[i - o]:
                    a20 += 1
            above50 = 100.0 * a50 / nb
            qUp = True
            qHi = T
            qLo = NAN
            qN = 0
            qLast = NAN
            qMinP = NAN
            for o in range(so - 1, -1, -1):
                h = H[i - o]; l = L[i - o]
                if qUp:
                    if h > qHi:
                        qHi = h
                    elif l <= qHi * (1 - thPct / 100):
                        qUp = False
                        qLo = l
                else:
                    if l < qLo:
                        qLo = l
                    elif h >= qLo * (1 + thPct / 100):
                        qUp = True
                        qHi = h
                        if not isna(qLast):
                            qMinP = fmin(qMinP, qLast)
                        qLast = qLo
                        qN += 1
            dn = (not qUp) and not isna(qLo)
            nAll = qN + (1 if dn else 0)
            lastAll = qLo if dn else qLast
            minPrev = qMinP
            if dn:
                minPrev = qLast if isna(qMinP) else (qMinP if isna(qLast) else min(qMinP, qLast))
            okQ = nAll == 0 or (nAll >= 2 and not isna(minPrev) and lastAll >= minPrev * (1 - P[K_qUndercut] / 100))
            if not okQ and P[K_qOne] > 0 and nAll == 1:
                bd2 = 0.0
                for o in range(0, so):
                    bd2 = max(bd2, 100 * (1 - C[i - o] / C[i - o - 1]))
                okQ = 100.0 * a20 / nb >= P[K_qOnePct] and bd2 < crashX * adrPre
            if okQ and above50 >= q50:
                if code == 0:
                    code = 5
                    buy = T
                else:
                    qAlso = True
        # 6 Flat base
        if code == 0 and up50 and so >= 2 and nb >= P[K_fbMin] and dep <= (P[K_fbDep] if nb >= P[K_fbLong] else P[K_fbShortDep]) and prior >= P[K_fbPrior]:
            fO = so - (so + 1) // 2
            fH2 = NAN
            for o in range(fO - 1, -1, -1):
                fH2 = fmax(fH2, H[i - o])
            if fH2 >= T * (1 - P[K_fbTop] / 100):
                code = 6
                buy = T
        # 7 Any other base
        if code == 0 and up50 and P[K_genOn] > 0 and nb >= P[K_genMin] and dep <= P[K_genDep] and prior >= P[K_genPrior]:
            code = 7
            buy = T
        # 11 Deep base
        if code == 0 and P[K_deepOn] > 0 and nb >= P[K_deepMin] and dep > min(P[K_cupDepMax], P[K_genDep]) and dep <= P[K_deepMax] and prior >= P[K_deepPrior] and C[i] > ema50[i]:
            code = 11
            buy = T
    return code, buy, dep, prior, epPole, tlOut, lowv, qAlso, htfAlso


@njit(cache=True, error_model="numpy")
def find_level(H, L, C, i, P):
    maxLook = int(P[K_maxLook]); lvlGap = int(P[K_lvlGap]); lvlAfter = int(P[K_lvlAfter])
    topTol = P[K_topTol]; lvlPb = P[K_lvlPb]; lvlRun = P[K_lvlRun]; lvlRunBars = int(P[K_lvlRunBars])
    lvlDep = P[K_lvlDep]; sigPct = P[K_sigPct]; priorLook = int(P[K_priorLook])
    rR = NAN; rJ = NAI; rF = NAI; rT = NAN
    maxC = C[i]
    lim = min(maxLook - 1, i - 1)
    if lim >= 1:
        for jo in range(1, lim + 1):
            maxC = max(maxC, C[i - jo + 1])
            R = H[i - jo]
            if maxC < R and H[i - jo] >= H[i - jo - 1] and H[i - jo] >= H[i - jo + 1]:
                fo = NAI
                fs = min(jo - lvlGap, lvlAfter)
                if fs >= 1:
                    for t in range(fs, 0, -1):
                        if H[i - t] >= R * (1 - topTol / 100) and C[i - t] < R:
                            fo = t
                            break
                if fo != NAI:
                    lowF = NAN; hiF = NAN
                    for o in range(0, fo + 1):
                        lowF = fmin(lowF, L[i - o]); hiF = fmax(hiF, H[i - o])
                    runLo = NAN
                    for o in range(fo, min(fo + lvlRunBars, i) + 1):
                        runLo = fmin(runLo, L[i - o])
                    baseLo = NAN
                    for o in range(fo, jo + 1):
                        baseLo = fmin(baseLo, L[i - o])
                    if lowF >= R * (1 - lvlPb / 100) and 100 * (H[i - fo] / runLo - 1) >= lvlRun and 100 * (1 - baseLo / R) <= lvlDep and rise_into(H, L, i, jo, priorLook) >= sigPct:
                        rR = R; rJ = jo; rF = fo; rT = max(R, hiF)
                        break
    return rR, rJ, rF, rT


@njit(cache=True, error_model="numpy")
def lv_cup_ok(H, L, i, jo, R, P):
    ok = False
    if jo + 1 >= P[K_cupMin]:
        lw = NAN; li = NAI
        for o in range(jo, -1, -1):
            if isna(lw) or L[i - o] < lw:
                lw = L[i - o]; li = o
        pw = NAN
        for o in range(jo, min(jo + int(P[K_priorLook]), i) + 1):
            pw = fmin(pw, L[i - o])
        cDep = 100 * (1 - lw / R)
        if cDep >= P[K_cupDepMin] and cDep <= P[K_cupDepMax] and 100 * (R / pw - 1) >= P[K_cupPrior] and jo - li >= 5 and li >= 5:
            rO = NAI; rHi = NAN
            for o in range(li - 1, -1, -1):
                if isna(rHi) or H[i - o] > rHi:
                    rHi = H[i - o]; rO = o
            if rHi >= R * (1 - P[K_hdlNear] / 100) and rO >= P[K_hdlMin] and rO <= P[K_hdlMax]:
                hl = NAN
                for o in range(rO - 1, -1, -1):
                    hl = fmin(hl, L[i - o])
                ok = 100 * (1 - hl / rHi) <= P[K_hdlDep] and hl > (R + lw) / 2
    return ok


@njit(cache=True, error_model="numpy")
def find_big(H, L, i, isGap, loMom_i, hi52_i, lastBO, P):
    maxLook = int(P[K_maxLook]); sigPct = P[K_sigPct]; olderNear = P[K_olderNear]; maxDep = P[K_maxDep]
    topTol = P[K_topTol]; priorLook = int(P[K_priorLook]); nhMom = P[K_nhMom]; nearHiPct = P[K_nearHiPct]
    rSo = NAI; rJo = NAI; rT = NAN
    if lastBO != NAI:
        lboOff = i - lastBO
        M = NAN
        lim = min(maxLook - 1, i)
        for o in range(0, lim + 1):
            if isna(M) or H[i - o] > M:
                M = H[i - o]
                if o > lboOff and rise_into(H, L, i, o, priorLook) >= sigPct:
                    jo = o
                    M2 = H[i - o]
                    for o2 in range(o + 1, lim + 1):
                        if H[i - o2] > M2:
                            M2 = H[i - o2]
                            if H[i - o2] > H[i - jo] * (1 + olderNear / 100):
                                break
                            lo2 = NAN
                            for q in range(0, o2 + 1):
                                lo2 = fmin(lo2, L[i - q])
                            if rise_into(H, L, i, o2, priorLook) >= sigPct and 100 * (1 - lo2 / H[i - o2]) <= maxDep:
                                jo = o2
                    T = H[i - jo]
                    so = jo
                    kk = jo + 1
                    while kk <= i and kk - jo <= 60:
                        if H[i - kk] > T:
                            break
                        if H[i - kk] >= T * (1 - topTol / 100) and (kk == i or H[i - kk] >= H[i - kk - 1]) and rise_into(H, L, i, kk, priorLook) >= sigPct:
                            so = kk
                        kk += 1
                    bl = NAN
                    for q in range(0, so + 1):
                        bl = fmin(bl, L[i - q])
                    ok = 100 * (1 - bl / T) <= maxDep
                    if ok:
                        epN = False
                        for q in range(so, min(so + 40, i) + 1):
                            if isGap[i - q]:
                                epN = True
                        mom = 100 * (T / loMom_i - 1) >= nhMom
                        if not epN and not mom and T < hi52_i * (1 - nearHiPct / 100):
                            ok = False
                    if ok:
                        rSo = so; rJo = jo; rT = T
                    break
    return rSo, rJo, rT


@njit(cache=True, error_model="numpy")
def find_ft(H, L, C, i, ema50_i, P):
    ftMax = int(P[K_ftMax]); ftMin = int(P[K_ftMin]); ftTouch = int(P[K_ftTouch]); ftSpan = int(P[K_ftSpan])
    ftDep = P[K_ftDep]; ftVisTop = P[K_ftVisTop]; ftMerge = P[K_ftMerge] > 0
    rS = NAI; rR = NAN
    if C[i] > ema50_i:
        lim = min(2 * ftMax - 1, i)
        cs = np.empty(lim + 1, np.int64)
        nC = 0
        M = NAN
        for o in range(0, lim + 1):
            if isna(M) or H[i - o] > M:
                M = H[i - o]
                cs[nC] = o
                nC += 1
        tol = P[K_ftTol] / 100
        if nC >= 2:
            for idx in range(0, nC - 1):
                oj = cs[idx]
                R0 = H[i - oj]
                mSo = NAI
                if ftMerge:
                    m = idx
                    while m + 1 < nC and H[i - cs[m + 1]] <= H[i - cs[m]] * (1 + tol) and H[i - cs[m + 1]] <= R0 * (1 + 2 * tol):
                        m += 1
                    if m > idx:
                        mSo = cs[m]
                pSo = cs[idx + 1] - 1
                stop = False
                for k in range(2):
                    tso = mSo if k == 0 else pSo
                    if k == 1 and pSo + 1 > ftMax:
                        stop = True
                    if (not stop) and rS == NAI and tso != NAI:
                        tR = R0
                        zb = R0 * (1 - tol)
                        if k == 0:
                            tR = H[i - tso]
                            zb = max(R0 * (1 - tol), tR * (1 - ftVisTop / 100))
                        nb = tso + 1
                        if nb >= ftMin and nb <= ftMax:
                            visits = 0
                            firstT = NAI
                            lastT = NAI
                            mid = False
                            lo = NAN
                            for o in range(tso, -1, -1):
                                lo = fmin(lo, L[i - o])
                                if H[i - o] >= zb:
                                    if lastT == NAI or lastT - o >= 2:
                                        visits += 1
                                    if firstT == NAI:
                                        firstT = o
                                    lastT = o
                                    if tso - o >= 0.25 * nb and tso - o <= 0.75 * nb:
                                        mid = True
                            if visits >= ftTouch and mid and firstT - lastT >= ftSpan and 100 * (1 - lo / tR) <= ftDep:
                                rS = tso
                                rR = tR
                if stop or rS != NAI:
                    break
    return rS, rR


@njit(cache=True, error_model="numpy")
def replay_legs(H, L, i, off, piv, th):
    up = True
    hi = piv
    lo = NAN
    pb = 0
    if off > 0:
        for k in range(off - 1, -1, -1):
            if up:
                if H[i - k] > hi:
                    hi = H[i - k]
                elif L[i - k] <= hi * (1 - th / 100):
                    up = False
                    lo = L[i - k]
                    pb += 1
            else:
                if L[i - k] < lo:
                    lo = L[i - k]
                elif H[i - k] >= lo * (1 + th / 100):
                    up = True
                    hi = H[i - k]
    return up, lo, pb


@njit(cache=True, error_model="numpy")
def req_vol(c, P):
    if c == 1:
        return P[K_volHTF]
    if c == 2 or c == 3:
        return P[K_volCup]
    if c == 4:
        return P[K_volAT]
    if c == 5:
        return P[K_volQ]
    if c == 6:
        return P[K_volFB]
    if c == 7:
        return P[K_volGen]
    if c == 8 or c == 9:
        return P[K_volFP]
    if c == 11:
        return P[K_volDeep]
    if c == 12:
        return P[K_volTF]
    return 0.0


@njit(cache=True, error_model="numpy")
def is_pat(c):
    return (c >= 1 and c <= 9) or c == 11 or c == 12


@njit(cache=True, error_model="numpy")
def wperf(x, i):
    s = 0.0
    for k in range(4):
        lag = 63 * (k + 1)
        w = 0.4 if k == 0 else 0.2
        if i - lag >= 0 and x[i - lag] == x[i - lag]:
            s += w * (x[i] / x[i - lag] - 1)
    return s


# ───────────────────────────── the bar-by-bar run ─────────────────────────────
@njit(cache=True, error_model="numpy")
def run(O, H, L, C, V, B, P):
    n = C.size
    out = np.full((n, NOUT), NAN)
    # core metrics
    ema10 = ema(C, 10); ema21 = ema(C, 21); ema50 = ema(C, 50)
    sma50 = sma(C, 50); sma150 = sma(C, 150); sma200 = sma(C, 200)
    hi52 = highest(H, 252, 1); lo52 = lowest(L, 252, 1)
    loMom = lowest(L, int(P[K_nhMomBars]) + 1, int(P[K_nhMomBars]) + 1)
    avgVol = sma(V, 50)
    dolVol = sma(C * V, int(P[K_dolVolLen])) / 1e6
    adr = 100 * (sma(H / L, 20) - 1)
    vdu = sma(V, 5) / avgVol
    h5 = highest(H, 5, 5); l5 = lowest(L, 5, 5)
    tight5 = 100 * (h5 - l5) / h5
    coilLo = lowest(L, 3, 3)
    rng = H - L
    rngAvg10 = sma(rng, 10)
    sma20c = sma(C, 20)
    volLook = int(P[K_volLook])
    dAvgV = sma(V, volLook)
    hi20 = highest(H, 20, 20)
    gbLen = int(P[K_gbBaseLen])
    gbHi = highest(H, gbLen, gbLen); gbLo = lowest(L, gbLen, gbLen)
    rsLine = C / B
    rsHi63 = highest(rsLine, 63, 63)

    swAdrX = P[K_swAdrX]; swMin = P[K_swMinPct]; swMax = P[K_swMaxPct]
    req200 = P[K_req200] > 0
    calcStart = n - 1 - int(P[K_calcBars])

    todRV = np.full(n, NAN)
    isGap = np.zeros(n, np.bool_)
    isGapBase = np.zeros(n, np.bool_)
    gapPct = np.full(n, NAN)
    for i in range(1, n):
        todRV[i] = V[i] / dAvgV[i - 1]
        gapPct[i] = 100 * (O[i] / C[i - 1] - 1)
        isGap[i] = gapPct[i] >= P[K_epGap] and (P[K_volEpX] <= 0 or todRV[i] >= P[K_volEpX])
        bHi = gbHi[i - 1]; bLo = gbLo[i - 1]
        if bHi == bHi:
            dep = 100 * (bHi - bLo) / bHi
            clr = O[i] > bHi if P[K_gbClearOpen] > 0 else C[i] > bHi
            isGapBase[i] = gapPct[i] >= P[K_gbGap] and clr and dep <= P[K_gbMaxDep] and (P[K_volGbX] <= 0 or todRV[i] >= P[K_volGbX])

    # state (Pine `var`)
    motherHi = NAN; motherLo = NAN; motherC = NAN; inCnt = 0
    zzDir = 1; zzHi = NAN; zzLo = NAN; sh1 = NAN; sh2 = NAN; sl1 = NAN; sl2 = NAN
    lastBO = NAI; failS = NAI; failBar = NAI
    firedS = NAI; tlFiredS = NAI
    pS = NAI; pCode = 0; pBuy = NAN; pT = NAN; pN = NAI; pDep = NAN; pPri = NAN; pEP = False; pTL = NAN
    pBigBuy = NAN; pBigJ = NAI; pBigS = NAI; bigFailJ = NAI; bigFailBar = NAI
    pFTBuy = NAN; pFTS = NAI; ftLastBar = NAI; ftFailBar = NAI
    pLvTrig = NAN; pLvR = NAN; pLvJ = NAI; pLvCup = False
    hlTrig = NAN; hlStop = NAN; hlDone = False; hlPbNum = NAI; hlBase = NAI
    early = NAN; earlyStop = NAN; earlyMC = NAN

    for i in range(n):
        o_ = O[i]; h_ = H[i]; l_ = L[i]; c_ = C[i]
        above200 = (not req200) or c_ > sma200[i]
        liquid = c_ >= P[K_minPrice] and dolVol[i] >= P[K_minDolVol]
        inCalc = i >= calcStart
        rv = todRV[i]
        thPct = max(swMin, min(swMax, swAdrX * adr[i]))

        # coil: mother bar + inside days
        cBodyPct = 100 * (max(o_, c_) / min(o_, c_) - 1)
        insideTight = (not isna(motherHi)) and h_ <= motherHi and l_ >= motherLo and (P[K_coilBodyX] >= 1.0 or abs(c_ - o_) <= P[K_coilBodyX] * (h_ - l_)) and (P[K_coilBodyAdr] <= 0 or cBodyPct <= P[K_coilBodyAdr] * adr[i])
        if insideTight:
            inCnt += 1
        else:
            motherHi = h_; motherLo = l_; motherC = c_; inCnt = 0
        rngAvg = rngAvg10[i - 1] if i >= 1 else NAN
        tightDay = abs(c_ - o_) <= P[K_tightBodyX] * (h_ - l_) and ((P[K_tightUseRng] <= 0) or (h_ - l_) <= P[K_tightRangeX] * rngAvg)

        # grade: 20-day pullback + higher high / higher low
        hb20 = 0
        if i >= 19:
            m = H[i]
            for k in range(1, 20):
                if H[i - k] > m:
                    m = H[i - k]; hb20 = k
        lo20s = NAN
        for k in range(0, min(hb20, i) + 1):
            lo20s = fmin(lo20s, L[i - k])
        pb20 = 100 * (1 - lo20s / hi20[i])
        zzTh = thPct
        if zzDir == 1:
            if isna(zzHi) or h_ > zzHi:
                zzHi = h_
            elif l_ <= zzHi * (1 - zzTh / 100):
                sh2 = sh1; sh1 = zzHi; zzDir = -1; zzLo = l_
        else:
            if l_ < zzLo:
                zzLo = l_
            elif h_ >= zzLo * (1 + zzTh / 100):
                sl2 = sl1; sl1 = zzLo; zzDir = 1; zzHi = h_
        hhhl = (not isna(sh2)) and (not isna(sl2)) and sh1 > sh2 and sl1 > sl2 and (zzDir == 1 or zzLo > sl1)
        trendA = ema10[i] > ema21[i] and ema21[i] > ema50[i] and c_ > ema50[i] and c_ > sma200[i] and ((P[K_gr200] <= 0) or ema21[i] > sma200[i]) and ((P[K_grHHHL] <= 0) or hhhl)
        grade = 0
        if trendA:
            if pb20 >= P[K_grAplLo] and pb20 <= P[K_grAplHi]:
                grade = 1
            elif pb20 <= P[K_grAHi]:
                grade = 2
            elif pb20 <= P[K_grBHi] and adr[i] >= P[K_grHiAdr]:
                grade = 3

        # ③ breakouts today (yesterday's armed levels)
        bo = False; boCode = 0; boBuy = NAN; boS = NAI; boAbove = False
        flHit = False; flHitLvl = NAN
        bigBO = False; bigBuy = NAN; bigS = NAI
        ftBO = False; ftBuy = NAN; ftS = NAI
        if inCalc and liquid and above200:
            if is_pat(pCode) and (not isna(pBuy)) and h_ > pBuy and pS != nzi(firedS, -1) and not (pS == nzi(failS, -1) and i - nzi(failBar, -999) < P[K_rearm] and c_ <= pBuy) and (req_vol(pCode, P) <= 0 or rv >= req_vol(pCode, P)):
                bo = True; boCode = pCode; boBuy = pBuy; boS = pS
                if c_ > pBuy:
                    lastBO = i; firedS = pS; boAbove = True
                else:
                    failS = pS; failBar = i
            if P[K_bigOn] > 0 and (not isna(pBigBuy)) and h_ > pBigBuy and (P[K_volBig] <= 0 or rv >= P[K_volBig]) and not (pBigJ == nzi(bigFailJ, -1) and i - nzi(bigFailBar, -999) < P[K_rearm] and c_ <= pBigBuy) and not (bo and abs(boBuy - pBigBuy) / pBigBuy < 0.01):
                bigBO = True; bigBuy = pBigBuy; bigS = pBigS
                if c_ > pBigBuy:
                    lastBO = i
                else:
                    bigFailJ = pBigJ; bigFailBar = i
            if P[K_ftOn] > 0 and (not isna(pFTBuy)) and h_ > pFTBuy and (P[K_volFT] <= 0 or rv >= P[K_volFT]) and not (i - nzi(ftFailBar, -999) < P[K_rearm] and c_ <= pFTBuy) and not (bo and abs(boBuy - pFTBuy) / pFTBuy < 0.01) and not (bigBO and abs(bigBuy - pFTBuy) / pFTBuy < 0.01):
                ftBO = True; ftBuy = pFTBuy; ftS = pFTS
                if c_ > pFTBuy:
                    ftLastBar = i
                else:
                    ftFailBar = i
            if (not isna(pTL)) and pS != nzi(tlFiredS, -1) and h_ > pTL and (P[K_flVol] <= 0 or rv >= P[K_flVol]):
                flHit = True; flHitLvl = pTL; tlFiredS = pS

        # today's base → tomorrow's buy point
        cS = NAI; cCode = 0; cBuy = NAN; cT = NAN; cN = NAI; cDep = NAN; cPri = NAN; cEP = False; cTL = NAN
        cLow = NAN; cQ = False; cH = False
        if inCalc:
            so, jo, T = find_base(H, L, C, i, isGap, loMom[i], hi52[i], lastBO, failS, failBar, P)
            if so != NAI:
                c, b, d, pr, ep, tlv, lw, qa, ha = classify(O, H, L, C, i, so, T, ema50, sma50, sma20c, adr, isGap, thPct, P)
                cS = i - so; cCode = c; cBuy = b; cT = T; cN = so + 1; cDep = d; cPri = pr; cEP = ep
                cLow = lw; cQ = qa; cH = ha
                if c == 8 or c == 9:
                    cTL = flag_line(H, L, i, so, T, P[K_flDepMin], P)
                elif c == 12:
                    cTL = tlv
        pS = cS; pCode = cCode; pBuy = cBuy; pT = cT; pN = cN; pDep = cDep; pPri = cPri; pEP = cEP; pTL = cTL
        tlLive = cTL if ((not isna(cTL)) and cS != nzi(tlFiredS, -1)) else NAN

        # bigger base / flat-top levels for tomorrow
        cBigBuy = NAN; cBigJ = NAI; cBigS = NAI; cBigCode = 0
        if inCalc and P[K_bigOn] > 0:
            bso, bjo, bT = find_big(H, L, i, isGap, loMom[i], hi52[i], lastBO, P)
            if bso != NAI:
                bc, bb, bd, bpr, bep, btl, blw, bqa, bha = classify(O, H, L, C, i, bso, bT, ema50, sma50, sma20c, adr, isGap, thPct, P)
                if bc > 0:
                    cBigBuy = bT if bc == 12 else bb
                    cBigJ = i - bjo; cBigS = i - bso; cBigCode = bc
        pBigBuy = cBigBuy; pBigJ = cBigJ; pBigS = cBigS
        cFTBuy = NAN; cFTS = NAI
        if inCalc and P[K_ftOn] > 0 and i - nzi(ftLastBar, -999) >= P[K_ftCool]:
            fso, fR = find_ft(H, L, C, i, ema50[i], P)
            if fso != NAI:
                cFTBuy = fR; cFTS = i - fso
        pFTBuy = cFTBuy; pFTS = cFTS

        # ④ level breakout
        lvBO = False; lvCup = False; lvBuy = NAN; lvLevel = NAN
        if inCalc and liquid and above200 and P[K_lvlOn] > 0 and (not isna(pLvTrig)) and h_ > pLvTrig and (P[K_volLvl] <= 0 or rv >= P[K_volLvl]):
            lvBO = True; lvBuy = pLvTrig; lvLevel = pLvR; lvCup = pLvCup
        lvSame = lvBO and bo and abs(boBuy - lvBuy) / lvBuy < 0.01
        cLvTrig = NAN; cLvR = NAN; cLvJ = NAI; cLvCup = False
        if inCalc and P[K_lvlOn] > 0 and c_ > ema50[i]:
            lr, lj, lf, lt = find_level(H, L, C, i, P)
            if not isna(lr):
                cLvTrig = lt; cLvR = lr; cLvJ = i - lj; cLvCup = lv_cup_ok(H, L, i, lj, lr, P)
        pLvTrig = cLvTrig; pLvR = cLvR; pLvJ = cLvJ; pLvCup = cLvCup

        # ① 2nd-pullback tight day
        hlHit = False
        if (not isna(hlTrig)) and not hlDone:
            if h_ > hlTrig and above200:
                hlHit = True; hlDone = True
            elif l_ < hlStop:
                hlTrig = NAN
        if inCalc and (cS == NAI or cS != nzi(hlBase, -1)) and not hlHit:
            hlTrig = NAN; hlDone = False
        pbMarked = False
        if inCalc and cS != NAI:
            u0, l0, p0 = replay_legs(H, L, i, i - cS, cT, thPct)
            if above200 and (not u0) and p0 >= P[K_pbMin] and tightDay and l_ <= l0 and 100 * (cT - l_) / cT <= P[K_pbMaxDepth] and not (hlDone and hlPbNum == p0 and hlBase == cS):
                hlTrig = h_; hlStop = l_; hlPbNum = p0; hlDone = False; hlBase = cS; pbMarked = True

        # outputs
        code = 0; pivot = NAN
        if cS != NAI:
            code = cCode if cCode > 0 else 10
            pivot = cBuy if cCode > 0 else cT
        elif bo:
            code = boCode; pivot = boBuy

        # ② coil
        earlyTrig = False; earlyTry = False
        coilOpenOk = (P[K_coilOpenReq] <= 0) or o_ > earlyMC
        if (not isna(early)) and h_ > early and above200 and coilOpenOk:
            earlyTrig = True
            if insideTight:
                earlyTry = True
            else:
                early = NAN; earlyStop = NAN
        elif (not isna(early)) and (l_ < earlyStop or not insideTight):
            early = NAN; earlyStop = NAN
        coilMark = inCalc and above200 and inCnt == int(P[K_coilInside])
        coilExtend = inCalc and above200 and (not isna(early)) and inCnt > int(P[K_coilInside])
        if coilMark or coilExtend:
            early = motherHi if P[K_coilEntryMother] > 0 else h_
            earlyStop = motherLo
            earlyMC = motherC
        boStop = max(coilLo[i], pivot * (1 - adr[i] / 100)) if code > 0 else NAN
        dist = 100 * (pivot / c_ - 1) if code > 0 else NAN

        # score
        score = 0
        if code > 0:
            trendTT = c_ > sma50[i] and sma50[i] > sma150[i] and sma150[i] > sma200[i] and i >= 20 and sma200[i] > sma200[i - 20] and c_ >= lo52[i] * 1.30 and c_ >= hi52[i] * 0.75
            rsRel = 100 * (wperf(C, i) - wperf(B, i))
            score = 40 + (15 if trendTT else 0) + (10 if rsRel > 0 else 0) + (10 if rsLine[i] >= rsHi63[i] else 0)
            score += 10 if vdu[i] < 0.75 else 0
            score += 10 if tight5[i] <= adr[i] * 1.5 else 0
            score += 5 if (dist >= -1 and dist <= P[K_nearPct]) else 0

        r = out[i]
        r[C_code] = code; r[C_pivot] = pivot
        r[C_cS] = cS if cS != NAI else NAN; r[C_cT] = cT; r[C_cN] = cN if cN != NAI else NAN
        r[C_cDep] = cDep; r[C_cPri] = cPri; r[C_cEP] = cEP; r[C_cLow] = cLow; r[C_cQ] = cQ; r[C_cH] = cH
        r[C_tlLive] = tlLive
        r[C_bo] = bo; r[C_boCode] = boCode; r[C_boBuy] = boBuy; r[C_boS] = boS if boS != NAI else NAN
        r[C_boClosedAbove] = boAbove
        r[C_bigBO] = bigBO; r[C_bigBuy] = bigBuy; r[C_bigS] = bigS if bigS != NAI else NAN
        r[C_ftBO] = ftBO; r[C_ftBuy] = ftBuy; r[C_ftS] = ftS if ftS != NAI else NAN
        r[C_lvBO] = lvBO; r[C_lvBuy] = lvBuy; r[C_lvLevel] = lvLevel; r[C_lvSame] = lvSame; r[C_lvCup] = lvCup
        r[C_flHit] = flHit; r[C_flHitLvl] = flHitLvl
        r[C_early] = early; r[C_earlyStop] = earlyStop; r[C_coilMark] = coilMark; r[C_earlyTrig] = earlyTrig
        r[C_earlyTry] = earlyTry; r[C_inCnt] = inCnt
        r[C_hlTrig] = hlTrig; r[C_hlStop] = hlStop; r[C_hlDone] = hlDone; r[C_pbMarked] = pbMarked; r[C_hlHit] = hlHit
        r[C_hlPbNum] = hlPbNum if hlPbNum != NAI else NAN
        r[C_cLvTrig] = cLvTrig; r[C_cLvR] = cLvR; r[C_cLvJ] = cLvJ if cLvJ != NAI else NAN; r[C_cLvCup] = cLvCup
        r[C_cBigBuy] = cBigBuy; r[C_cBigS] = cBigS if cBigS != NAI else NAN; r[C_cBigCode] = cBigCode
        r[C_cFTBuy] = cFTBuy; r[C_cFTS] = cFTS if cFTS != NAI else NAN
        r[C_grade] = grade; r[C_hhhl] = hhhl; r[C_trendA] = trendA; r[C_pb20] = pb20
        r[C_score] = score; r[C_dist] = dist; r[C_liquid] = liquid; r[C_above200] = above200
        r[C_isGap] = isGap[i]; r[C_isGapBase] = isGapBase[i]
        r[C_adr] = adr[i]; r[C_ema10] = ema10[i]; r[C_ema21] = ema21[i]; r[C_ema50] = ema50[i]
        r[C_sma50] = sma50[i]; r[C_sma200] = sma200[i]; r[C_rvol] = rv; r[C_dolVol] = dolVol[i]
        r[C_gapPct] = gapPct[i]; r[C_boStop] = boStop
    return out



def run_symbol(bars, bench_close, p):
    """bars: list of [date, o, h, l, c, v]; bench_close: dict date -> close. Returns a pandas DataFrame."""
    import pandas as pd
    a = np.array([b[1:] for b in bars], dtype=float)
    dates = [b[0] for b in bars]
    B = np.array([bench_close.get(d, np.nan) for d in dates], dtype=float)
    B = pd.Series(B).ffill().bfill().to_numpy()
    out = run(a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4], B, p)
    df = pd.DataFrame(out, columns=OUT, index=pd.to_datetime(dates))
    df[["open", "high", "low", "close", "volume"]] = a
    return df
