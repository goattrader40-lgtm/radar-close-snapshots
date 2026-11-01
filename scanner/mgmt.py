"""The user's trade management (Nov 1 2026), shared by every test.

  targets   sell 1/3 when the price is 2 ADRs over the buy (the stock's ADR the day before), 1/3 at 5 ADRs
  stop      the entry stop; after the first 1/3 is sold, the rest at breakeven (from the next bar)
  runners   out on a daily close under the 10 EMA (a strong stock) or the 21 EMA: both tested (runner=10 / 21); that close
            takes whatever is still open, at any time
  order     a bar (5-minute, 1-minute or a day) that touches both the stop and a target counts the stop first
"""


def run(a, k, buy, stop, bars=None, same_day_high=None, runner=21):
    """the trade bought at `buy` on day k: on `bars` (the intraday bars from the buy's bar on) or, without them, the
    day's high for the targets (a stop under the day's low can't be hit that day); then day by day"""
    st = a.st
    c, o, h, l = st.c, st.o, st.h, st.l
    ema = a.e10 if runner == 10 else a.e21
    adr = float(st.adr[k - 1])
    t1, t2 = buy * (1 + 2 * adr / 100), buy * (1 + 5 * adr / 100)
    R = buy - stop
    S = dict(stop=stop, left=1.0, got=0.0, be=False, s1=False, s2=False, how=None)

    def out(px, how):
        S["got"] += S["left"] * px
        S["left"] = 0.0
        S["how"] = how
        return True

    def step(bo, bh, bl):
        if bl is not None and bl <= S["stop"]:
            return out(min(S["stop"], bo), "breakeven" if S["be"] else "stop")
        if bh >= t1 and not S["s1"]:
            S["got"] += max(t1, bo) / 3; S["left"] -= 1 / 3; S["s1"] = True
        if bh >= t2 and not S["s2"]:
            S["got"] += max(t2, bo) / 3; S["left"] -= 1 / 3; S["s2"] = True
        if S["s1"] and not S["be"]:
            S["stop"], S["be"] = max(S["stop"], buy), True
        return False
    done, end = False, k
    if bars:
        for n, x in enumerate(bars):
            if step(buy if n == 0 else x["o"], x["h"], x["l"]):
                done = True
                break
    elif same_day_high is not None:
        step(buy, same_day_high, None)
    if not done and c[k] < ema[k]:
        done = out(c[k], f"daily {runner} EMA close")
    j = k + 1
    while not done and j < c.size:
        end = j
        if step(o[j], h[j], l[j]):
            done = True
        elif c[j] < ema[j]:
            done = out(c[j], f"daily {runner} EMA close")
        j += 1
    if not done:
        out(c[-1], "open at the end")
    return dict(ret=100 * (S["got"] / buy - 1), R=(S["got"] - buy) / R if R > 0 else 0.0, risk=100 * R / buy, how=S["how"],
                days=end - k, t1=S["s1"], t2=S["s2"], same_day=end == k and S["how"] in ("stop", "breakeven"),
                mg=float(100 * (h[k:end + 1].max() / buy - 1)))


def cols(x, pre="", suf=""):
    """the result columns of a trade for the spreadsheet: risk %, result %, R, win, reached +2 / +5 ADR, exit"""
    return {f"{pre}risk_pct{suf}": round(x["risk"], 2), f"{pre}result_pct{suf}": round(x["ret"], 2), f"{pre}R{suf}": round(x["R"], 2),
            f"{pre}win{suf}": int(x["ret"] > 0), f"{pre}reached_2ADR{suf}": int(x["t1"]), f"{pre}reached_5ADR{suf}": int(x["t2"]),
            f"{pre}exit{suf}": x["how"]}


def sold_at_close(x, a, k, buy, risk_pct, why="sold at the close"):
    """the same buy sold at day k's close (a failed breakout / not a launch), unless already out that day; a +2 / +5 ADR
    target reached that day (its high) is sold there first"""
    if x["days"] == 0 and x["how"] in ("stop", "breakeven"):
        return x
    st = a.st
    adr = float(st.adr[k - 1])
    t1, t2, hi, px = buy * (1 + 2 * adr / 100), buy * (1 + 5 * adr / 100), float(st.h[k]), float(st.c[k])
    got, left = 0.0, 1.0
    if hi >= t1:
        got += t1 / 3; left -= 1 / 3
    if hi >= t2:
        got += t2 / 3; left -= 1 / 3
    got += left * px
    R = buy * risk_pct / 100
    return dict(x, ret=100 * (got / buy - 1), R=(got - buy) / R if R > 0 else 0.0, how=why, t1=hi >= t1, t2=hi >= t2, days=0)


_DV = {}


def liquidity(a, k):
    """the 20-day averages the day before day k: $ traded (in $M) and shares, for the spreadsheet's filters"""
    key = id(a)
    if key not in _DV:
        import numpy as np
        c, v = a.st.c, a.st.v
        n = c.size
        cs, vs = np.concatenate(([0.0], np.cumsum(c * v))), np.concatenate(([0.0], np.cumsum(v)))
        dv, av = np.full(n, np.nan), np.full(n, np.nan)
        dv[19:] = (cs[20:] - cs[:-20]) / 20 / 1e6
        av[19:] = (vs[20:] - vs[:-20]) / 20
        _DV[key] = (dv, av)
    dv, av = _DV[key]
    j = k - 1
    return dict(dollar_vol_20d_m=round(float(dv[j]), 1) if j >= 19 else None, avg_shares_20d=int(av[j]) if j >= 19 else None)


_RSI = {}


def rsi14(a):
    """Wilder's 14-day RSI of a stock's closes (cached)"""
    key = id(a)
    if key not in _RSI:
        import numpy as np
        c = a.st.c
        d = np.diff(c, prepend=c[0])
        up, dn = np.where(d > 0, d, 0.0), np.where(d < 0, -d, 0.0)
        au, ad = np.zeros(c.size), np.zeros(c.size)
        if c.size > 15:
            au[14], ad[14] = up[1:15].mean(), dn[1:15].mean()
            for k in range(15, c.size):
                au[k] = (au[k - 1] * 13 + up[k]) / 14
                ad[k] = (ad[k - 1] * 13 + dn[k]) / 14
        _RSI[key] = 100 - 100 / (1 + au / np.where(ad > 0, ad, 1e-9))
    return _RSI[key]


def reset(a, j):
    """the momentum reset before a buy on day j, from the bars up to the day before (no hindsight; the user's AEHR read,
    Nov 1 2026: its Mar 6-19 and May 6-26 2026 buy points came before any reset, Mar 31 - Apr 6 after the shakeout under
    the 50 EMA). The latest top = the highest high of the 60 sessions before j; its run = from the lowest low of the 25
    sessions before it, in the stock's ADRs; the pullback since it, how close its lows came to the 50 EMA, the 21 EMA's
    spread over the 50 EMA, and the lowest RSI(14) since the top"""
    import numpy as np
    st = a.st
    c, h, l = st.c, st.h, st.l
    p = j - 1
    if j < 90:
        return {}
    top = j - 60 + int(np.argmax(h[j - 60:j]))
    adr_t = float(st.adr[top]) if st.adr[top] > 0 else 5.0
    adr_p = float(st.adr[p]) if st.adr[p] > 0 else 5.0
    lo0 = top - 25 + int(np.argmin(l[top - 25:top]))
    rs = rsi14(a)
    after = range(top + 1, j)
    near50 = min((100 * (l[k] / a.e50[k] - 1) / (st.adr[k] if st.adr[k] > 0 else 5.0) for k in after), default=None)
    out = dict(days_since_top=j - top, run_into_top_adr=round(100 * (h[top] / l[lo0] - 1) / adr_t, 1),
               pullback_adr=round(100 * (1 - l[top + 1:j].min() / h[top]) / adr_t, 1) if j - top > 1 else 0.0,
               ema21_over_50_adr=round(100 * (a.e21[p] / a.e50[p] - 1) / adr_p, 2),
               close_over_50_adr=round(100 * (c[p] / a.e50[p] - 1) / adr_p, 2),
               pullback_low_vs_50_adr=round(near50, 2) if near50 is not None else None,
               rsi_min_since_top=round(float(rs[top + 1:j].min() if j - top > 1 else rs[p]), 1), rsi_day_before=round(float(rs[p]), 1))
    out.update(reset_at_50ema=int(near50 is not None and near50 <= 0.25), reset_rsi_under_45=int(out["rsi_min_since_top"] <= 45),
               reset_emas_close=int(out["ema21_over_50_adr"] <= 0.8), big_run_8adr=int(out["run_into_top_adr"] >= 8))
    out["reset_any"] = int(out["reset_at_50ema"] or out["reset_rsi_under_45"] or out["reset_emas_close"])
    # how far the stock has run (the user, Nov 1 2026: "over 500% within 7-8 months, no buy points"): from the lowest low of
    # the last 3 / 6 / 8 / 12 months to the close the day before, and the sessions since that low; the % over the 200 SMA
    for nm, w in (("3m", 63), ("6m", 126), ("8m", 168), ("12m", 252)):
        k0 = max(0, j - w)
        kl = k0 + int(np.argmin(l[k0:j]))
        out[f"run_from_{nm}_low_pct"] = round(float(100 * (c[p] / l[kl] - 1)), 1)
        out[f"sessions_from_{nm}_low"] = j - kl
    s200 = getattr(a, "s200", None)
    out["over_200sma_pct"] = round(float(100 * (c[p] / s200[p] - 1)), 1) if s200 is not None and s200[p] > 0 else None
    return out
