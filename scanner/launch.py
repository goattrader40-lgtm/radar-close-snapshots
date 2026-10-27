"""Trend launches: the first day of a new trend, the group it belongs to, and the bases that follow.

Launch day (from your examples: DELL Feb 27 2026, TEAM and APPN Aug 7 2026, the cyber names Sep 14 2026, AMD 2016):
  must have   opened up (any gap), closed up 5%+ in the top half of the day's range (a power day may close lower
              if it holds half its gap: FSLR Jul 28 2022; tagged "faded", since in 2 years such days bought at the
              open with a stop under the day's low were stopped out 9 times in 10, though 13% ran 50%+), volume 1.5x+ the
              previous 20 days' average, closed above the 200 SMA, and was still near it the day before (at most
              28% above it: a neglected stock or one coming out of a correction, not a trend already running;
              your launches were -6% to +25% from it, the continuation days of MU / DELL / APPN +30% to +77%),
              and closed at least 30% above its 52-week low (your standard filter; your launches were 57-166% above).
              A power day (an episodic pivot: volume 4x+, a 10%+ gap, a 15%+ day) may start up to 50% above the
              200 SMA: SMCI May 3 2023 launched at an all-time high 32% over it; 2 years of these: 54% ran 20%+
  earnings    tagged when the stock reported that day or the evening before (Yahoo's earnings date, from the live job)
  ingredients volume 3x+ · gap 3%+ · base breakout (closed above the previous 20 days' high) ·
              its group is trending · within 30% of the 52-week high · neglected (40+ days since its high,
              or a 25%+ correction)
  grade       the launch itself, from 4 ingredients: volume 3x+, gap 3%+, base breakout (closed above the previous
              20 days' high), a 10%+ day.
              A+ = volume 3x+, a 6%+ gap and a base breakout, jumping from under the 200 SMA to above it (your
                   "go day"; 2 years: 65% of these ran 20%+ when the theme confirmed, vs 52% for other A's)
              A = volume 3x+ and a base breakout, with a 3%+ gap or a 10%+ day · B = two of the four · C = the rest
  news        tagged when the 8:47 pre-market grading gave the stock an A or B gap-up grade that morning
  legs        the launch is leg 1; each later leg = a new high, then a pause of 5+ sessions without a new high that
              pulls back 1.25+ of the stock's own ADRs (or a flag), then a close above that high or the flag's
              falling trendline. Depths are in each stock's own ADR: every ticker has its own character. One leg per pullback. A
              breakout after a rest of 40+ sessions without a new high starts a new run at leg 1 (SMCI rested
              about 114 sessions before its Jan 19 2024 launch).
              Flag = after a 25%+ rise, a 5-20 session pullback 1.25-4 ADRs deep that stays above the 50 EMA; its trendline
              runs from the top along the lower highs, and its buy point is tomorrow's value of that line (SMCI 2023:
              launch May 3, leg 2 May 16, leg 3 the flag breakout at the end of June). Breakouts got worse leg by leg (ran 20%+: leg 2 26%, leg 3 17%, leg 4 17%, leg 5+ 7%), so
              leg 4+ is flagged late; most launches never made a second leg
  new listings a stock listed less than 200 sessions ago uses its average close since listing in place of the 200
              SMA, once it has 60+ sessions (RDDT Oct 30 2024, its 155th day: a 28% gap, +42% on 7.9x volume to a new
              all-time high, +72% by the end of January)
  delayed     a gap of 3%+ on 3x+ volume above the 200 SMA that faded (closed in the bottom half or up less
              than 5%) is remembered for 10 sessions; if the stock holds its old base (no close more than 3%
              under the lower of the base top and the 200 SMA) and then launches, that launch gets the gap day's
              volume and gap, and its breakout is measured against the base before the gap (ACN: earnings gap
              Oct 1 2026 on 5.4x volume faded, held the base 4 days, launched Oct 8 and trended)
  follower    a breakout in the leader's wake: within 10 sessions of an A or B launch by another member of one
              of its themes, the stock closes up 2%+ above its previous 20 days' high on 2x+ volume, in the top half
              of the range, above the 200 SMA and still near it (DXC Oct 8 2026 after ACN's earnings launch)
  theme       shown beside the grade, not in it: its group's status on the launch day, now, and the day it
              turned up. A leader launches before its theme (DELL Feb 27 2026 while semis were still
              correcting; its group led by April). "Lone wolf" = no group of it trending, then or since.
Group = each of its themes on the portal (or its industry when it has none), and one level up its area
  (AI & Semis, Software, Energy... or its sector), since a theme's leader launches before the rest of the
  theme follows (DELL led AI servers by weeks). A group or area is
  Leading     when 60%+ of its members close above their 50 EMA and its median 1-month change is +8% or more
  Turning up  when half or more close above their 21 EMA and its median 1-week change is positive
Exit signal = the first close below the 21 EMA after the launch. A launch is followed until 2 closes in a
row below the 50 EMA or 120 sessions, with your MSF patterns (flags, pennants, triangles, flat bases,
breakouts) and their buy points as they form.

  python3 scanner/launch.py --bars BARS.json.gz --stocks radar-data/stocks.json [--out setups/launch.json]
                            [--backtest setups/launch_backtest.json] [--entry open|close]
  (themes.json from the same folder as stocks.json gives each theme's area)
"""
import argparse
import collections
import datetime
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import msf  # noqa: E402
import run  # noqa: E402
from screens import roll_mean  # noqa: E402

L = dict(leg_adr=1.25, flag_adr_min=1.25, flag_adr_max=4, min_sessions=60, rest_days=40, power_rv=4, power_gap=10, power_chg=15, power_ext200=50, aplus_gap=6, leg_pause=5, late_leg=4, min_chg=5, min_clpos=0.5, min_rv=1.5, max_ext200=28, min_above_low52=30, rv_big=3, gap_big=3, chg_big=10, base_days=20,
         near_high=70, neglect_days=40, neglect_depth=25, follow_days=120, dedupe_days=20, min_adr=4)
STATUS = {2: "Leading", 1: "Turning up", 0: "Not trending"}
ENTRY = "open"          # history test: "open" (launch-day open, stop under its low) or "close" (launch-day close)


def ema(x, n):
    a, o = 2 / (n + 1), np.empty_like(x)
    o[0] = x[0]
    for i in range(1, x.size):
        o[i] = a * x[i] + (1 - a) * o[i - 1]
    return o


def fnum(x, nd=2):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), nd)


class Arr:
    """one stock's daily arrays, plus the launch-day tests for every bar"""

    def __init__(self, st, S, new_listing=False):
        self.st = st
        self.start = L["min_sessions"] if new_listing else 200     # first bar a launch can be judged on
        c, h, l, o, v = st.c, st.h, st.l, st.o, st.v
        n = c.size
        self.e5, self.e10, self.e21, self.e50 = ema(c, 5), ema(c, 10), st.ema21, st.ema50
        # a stock listed less than 200 sessions ago: its average close since listing stands in for the 200 SMA
        since = np.cumsum(c) / np.arange(1, n + 1)
        self.s200 = np.where(np.isnan(st.sma200) | (st.sma200 <= 0), since, st.sma200) if new_listing else st.sma200
        prev = np.full(n, np.nan)
        prev[1:] = c[:-1]
        self.gap = 100 * (o / prev - 1)
        self.chg = 100 * (c / prev - 1)
        rng = h - l
        self.clpos = np.where(rng > 0, (c - l) / np.where(rng > 0, rng, 1), 1.0)
        avg20 = np.full(n, np.nan)
        avg20[1:] = roll_mean(v, 20)[:-1]
        self.rv = v / avg20
        self.hi20 = np.full(n, np.nan)          # highest high of the previous 20 days = the top of the base
        for i in range(L["base_days"], n):
            self.hi20[i] = h[i - L["base_days"]:i].max()
        self.ext200_prev = np.full(n, np.nan)
        self.ext200_prev[1:] = 100 * (c[:-1] / self.s200[:-1] - 1)
        self.liquid = np.array([c[i] >= S["min_price"] and st.avgv30[i] > S["min_avg_vol_30d"]
                                and st.dv30[i] > S["min_dollar_vol_30d_millions"] and st.adr[i] >= L["min_adr"] for i in range(n)])
        self.ret21 = np.full(n, np.nan)
        self.ret21[21:] = 100 * (c[21:] / c[:-21] - 1)
        self.ret5 = np.full(n, np.nan)
        self.ret5[5:] = 100 * (c[5:] / c[:-5] - 1)
        # the last faded high-volume gap within 10 sessions whose base has held since (-1 = none)
        self.mem = np.full(n, -1)
        g = -1
        for i in range(1, n):
            if g >= 0 and (i - g > 10 or c[i - 1] < min(self.hi20[g], self.s200[g]) * 0.97):
                g = -1
            self.mem[i] = g
            if (self.gap[i] >= L["gap_big"] and self.rv[i] >= L["rv_big"] and c[i] > self.s200[i]
                    and self.ext200_prev[i] <= L["max_ext200"] and (not self.held(i) or self.chg[i] < L["min_chg"])):
                g = i

    def follower(self, i):
        """a smaller breakout that counts when a leader of its group has just launched"""
        st = self.st
        return bool(i >= self.start and self.liquid[i] and self.chg[i] >= 2 and st.c[i] > self.hi20[i] and self.rv[i] >= 2
                    and self.clpos[i] >= L["min_clpos"] and st.c[i] > self.s200[i] and self.ext200_prev[i] <= L["max_ext200"]
                    and st.c[i] >= st.low52[i] * (1 + L["min_above_low52"] / 100))

    def held(self, i):
        """closed in the top half of the day's range, or on a power day held at least half of its gap
        (FSLR Jul 28 2022: a 16.8% gap on 4.7x volume that closed +15.3%, low in the day's range)"""
        if self.clpos[i] >= L["min_clpos"]:
            return True
        return self.power(i) and self.chg[i] >= self.gap[i] / 2

    def candidate(self, i):
        """the must-haves of a launch day"""
        st = self.st
        return bool(i >= self.start and self.liquid[i] and self.gap[i] > 0 and self.chg[i] >= L["min_chg"]
                    and self.held(i) and self.rv[i] >= L["min_rv"] and st.c[i] > self.s200[i]
                    and (self.ext200_prev[i] <= L["max_ext200"] or (self.power(i) and self.ext200_prev[i] <= L["power_ext200"]))
                    and st.c[i] >= st.low52[i] * (1 + L["min_above_low52"] / 100))

    def power(self, i):
        """a power day (an episodic pivot): volume 4x+, a 10%+ gap and a 15%+ day"""
        return bool(self.rv[i] >= L["power_rv"] and self.gap[i] >= L["power_gap"] and self.chg[i] >= L["power_chg"])

    def neglect(self, i):
        """days since the highest high of the last 250 sessions (the base can be long), and the correction from it (%)"""
        h, l = self.st.h, self.st.l
        w = h[max(0, i - 250):i]
        k = int(np.argmax(w))
        days = w.size - k
        depth = 100 * (1 - l[i - days:i].min() / w[k]) if days > 1 else 0.0
        return days, depth


def groups_of(stocks_json, themes_json):
    """{symbol: ([group, ...], [area, ...])}: its portal themes and their areas, else its industry and sector"""
    area = {t["theme"]: t["category"] for t in themes_json if t.get("category") != "Auto groups"}
    out = {}
    for r in stocks_json:
        th = [t for t in (r.get("themes") or "").split(" | ") if t]
        if th:
            out[r["symbol"]] = (th, sorted({area[t] for t in th if t in area}))
        else:
            out[r["symbol"]] = ([r["industry"]] if r.get("industry") else [], [r["sector"]] if r.get("sector") else [])
    return out


def group_status(A, groups, cal):
    """{group: (members, status array over cal)}; status 2 = Leading, 1 = Turning up, 0 = not trending"""
    pos = {d: k for k, d in enumerate(cal)}
    members = collections.defaultdict(list)
    for s, (gs, ars) in groups.items():
        if s in A:
            for g in gs + ["area:" + x for x in ars]:
                members[g].append(s)
    out = {}
    for g, ms in members.items():
        if len(ms) < 3:
            continue
        T = len(cal)
        a50, a21, r21, r5, cnt = (np.full((len(ms), T), np.nan) for _ in range(5))
        for j, s in enumerate(ms):
            a = A[s]
            idx = [pos[d] for d in a.st.dates if d in pos]
            if len(idx) != len(a.st.dates):
                continue
            a50[j, idx] = a.st.c > a.e50
            a21[j, idx] = a.st.c > a.e21
            r21[j, idx] = a.ret21
            r5[j, idx] = a.ret5
        with np.errstate(all="ignore"):
            import warnings
            warnings.simplefilter("ignore", RuntimeWarning)
            n = np.sum(~np.isnan(a50), axis=0)
            sh50, sh21 = np.nanmean(a50, axis=0), np.nanmean(a21, axis=0)
            m21, m5 = np.nanmedian(r21, axis=0), np.nanmedian(r5, axis=0)
        stt = np.where((n >= 3) & (sh50 >= 0.6) & (m21 >= 8), 2, np.where((n >= 3) & (sh21 >= 0.5) & (m5 > 0), 1, 0))
        out[g] = (ms, stt, sh21, m21)
    return out


def best_group(sym, k, groups, GS):
    """(status, name) of the best-trending group the stock belongs to on calendar day k: its themes first,
    then its area ("AI & Semis area"); -1 when it has none"""
    gs, ars = groups.get(sym, ([], []))
    best = (-1, "")
    for g in gs + ["area:" + x for x in ars]:
        if g in GS:
            s = int(GS[g][1][k])
            if s > best[0]:
                best = (s, g[5:] + " area" if g.startswith("area:") else g)
    return best


def grade(a, i):
    vol3, gap3, big = a.rv[i] >= L["rv_big"], a.gap[i] >= L["gap_big"], a.chg[i] >= L["chg_big"]
    bo = a.st.c[i] > a.hi20[i]
    gap6, under = a.gap[i] >= L["aplus_gap"], a.ext200_prev[i] < 0
    g = a.mem[i]
    if g >= 0:                                       # a delayed launch: credit the faded gap day
        vol3, gap3, big = True, True, big or a.chg[g] >= L["chg_big"]
        bo = bo or a.st.c[i] > a.hi20[g]
        gap6, under = a.gap[g] >= L["aplus_gap"], a.ext200_prev[g] < 0
    if vol3 and bo and gap6 and under:
        return "A+"
    if vol3 and bo and (gap3 or big):
        return "A"
    if int(vol3) + int(bo) + int(gap3) + int(big) >= 2:
        return "B"
    return "C"


def launch_row(sym, a, i, gstat, gname, S):
    st = a.st
    days, depth = a.neglect(i)
    h52 = st.high52[i]
    return dict(
        symbol=sym, tv=run.tv_symbol(sym, st.exchange), date=st.dates[i], grade=grade(a, i),
        gap_pct=fnum(a.gap[i], 1), chg_pct=fnum(a.chg[i], 1), rel_vol=fnum(a.rv[i], 1), close_in_range=fnum(100 * a.clpos[i], 0),
        faded=bool(a.clpos[i] < L["min_clpos"]), power=a.power(i),
        base_breakout=bool(st.c[i] > a.hi20[i] or (a.mem[i] >= 0 and st.c[i] > a.hi20[a.mem[i]])),
        delayed_from=st.dates[a.mem[i]] if a.mem[i] >= 0 else None, group=gname, group_status=STATUS.get(gstat, "No group"),
        pct_of_52w_high=fnum(100 * st.c[i] / h52, 0), near_high=bool(100 * st.c[i] / h52 >= L["near_high"]),
        days_since_high=days, correction_pct=fnum(depth, 0), above_52w_low_pct=fnum(100 * (st.c[i] / st.low52[i] - 1), 0), neglected=bool(days >= L["neglect_days"] or depth >= L["neglect_depth"]),
        vs_200_pct=fnum(100 * (st.c[i] / a.s200[i] - 1), 0), close=fnum(st.c[i]), low=fnum(st.l[i]),
    )


def flag_at(a, i):
    """a flag with a falling trendline (your SMCI June 2023 example): the top is the highest high of the last 25
    sessions, 5 to 20 sessions back, after a 25%+ rise; the pullback is 1.25-4 of the stock's own ADRs deep (SMCI
    June 2023: 21% = 3.2 ADRs) and closes stay above the 50 EMA.
    The trendline runs from the top along the lower highs (the flattest line that keeps every high since under it).
    Returns (top index, depth %, line today, line tomorrow) or None."""
    st = a.st
    h, l, c = st.h, st.l, st.c
    if i < 50:
        return None
    t = i - 24 + int(np.argmax(h[i - 24:i + 1]))
    if not 5 <= i - t <= 20:
        return None
    if h[t] / l[max(0, t - 25):t + 1].min() - 1 < 0.25:
        return None
    depth = 100 * (1 - l[t + 1:i + 1].min() / h[t])
    adr = st.adr[t] if st.adr[t] > 0 else 5.0
    if not L["flag_adr_min"] <= depth / adr <= L["flag_adr_max"] or any(c[k] < a.e50[k] for k in range(t + 1, i + 1)):
        return None
    slope = max((h[k] - h[t]) / (k - t) for k in range(t + 1, i))      # through the highs up to yesterday
    if slope >= 0:
        return None
    return t, depth, h[t] + slope * (i - t), h[t] + slope * (i + 1 - t)


def follow(a, i0, i):
    """what happened from the launch close (i0) to bar i: status, gain, exit signal, current base and pattern"""
    st, c = a.st, a.st.c
    exit_k = next((k for k in range(i0 + 1, i + 1) if c[k] < a.e21[k]), None)
    out50 = next((k for k in range(i0 + 2, i + 1) if c[k] < a.e50[k] and c[k - 1] < a.e50[k - 1]), None)
    r = st.df.iloc[i]
    code = int(r.code)

    def surf(e):
        n = 0
        for k in range(i, i0, -1):
            if c[k] < e[k]:
                break
            n += 1
        return n
    dry = st.v[i - 4:i + 1].mean() / st.v[i - 50:i].mean() if i >= 50 else np.nan
    # a leg = a new high, then a pause of 5+ sessions (or a flag), then a close above the high or the flag's
    # trendline; one leg per pullback, and the new high after a flag breakout belongs to the same leg
    H, last_new, leg, armed, rested = st.h[i0], i0, 1, False, None
    for j in range(i0 + 1, i + 1):
        if armed and j - last_new >= L["leg_pause"]:
            f = flag_at(a, j)
            # a real base pulls back 1.25+ of the stock's own ADRs (each ticker has its own character)
            deep = 100 * (1 - st.l[last_new:j].min() / H) >= L["leg_adr"] * (st.adr[last_new] if st.adr[last_new] > 0 else 5.0)
            if (f and c[j] > f[2]) or (c[j] > H and deep):
                # after a rest of 40+ sessions without a new high, the breakout starts a new run: leg 1 again
                leg, armed = (1, False) if j - last_new >= L["rest_days"] else (leg + 1, False)
                if leg == 1:
                    rested = j
        if st.h[j] > H:
            H, last_new, armed = st.h[j], j, True
    hi = st.h[i0:i + 1].max()
    status = "Riding" if c[i] >= a.e21[i] else "Below 21 EMA"
    fl = flag_at(a, i)
    flag_bo = bool(fl and c[i] > fl[2] and c[i - 1] <= (flag_at(a, i - 1) or (0, 0, np.inf))[2])
    return dict(
        sessions=i - i0, gain_pct=fnum(100 * (c[i] / c[i0] - 1), 1), max_gain_pct=fnum(100 * (hi / c[i0] - 1), 1),
        status=status, first_exit=st.dates[exit_k] if exit_k is not None else None,
        exit_gain_pct=fnum(100 * (c[exit_k] / c[i0] - 1), 1) if exit_k is not None else None,
        lost_50ema=st.dates[out50] if out50 is not None else None,
        price=fnum(c[i]), chg_today_pct=fnum(a.chg[i], 1), rel_vol_today=fnum(a.rv[i], 1),
        pattern=msf.NAMES[code] if code else ("Flag (trendline)" if fl else ""),
        buy_point=fnum(r.pivot) if code else (fnum(fl[3]) if fl else None),
        to_buy_point_pct=fnum(r.dist, 1) if code else (fnum(100 * (fl[3] / c[i] - 1), 1) if fl else None),
        base_days=fnum(r.cN, 0) if code else (i - fl[0] if fl else None),
        base_depth_pct=fnum(r.cDep, 1) if code else (fnum(fl[1], 1) if fl else None),
        flag_breakout_today=flag_bo,
        base_depth_adr=fnum((r.cDep if code else (fl[1] if fl else np.nan)) / (st.adr[i] if st.adr[i] > 0 else np.nan), 1), surf10=surf(a.e10), surf21=surf(a.e21),
        vol_dryup=fnum(dry, 2), off_high_pct=fnum(100 * (1 - c[i] / hi), 1), ema21=fnum(a.e21[i]),
        breakout_today=bool(code and msf.is_pat(code) and r.bo == 1), leg=leg, late=leg >= L["late_leg"],
        new_run_after_rest=st.dates[rested] if rested is not None else None,
        days_since_new_high=i - last_new,
    )


def load(bars_path, stocks_path):
    cfg = json.load(open(os.path.join(HERE, "settings.json")))
    D = run.load_bars(bars_path)
    stocks, P = run.build(D, cfg)
    cal = [b[0] for b in D["bars"]["SPY"]]
    S = cfg["standard"]
    # a stock whose bars start after the file's first session listed during it (the file reaches 2 years back)
    A = {s: Arr(st, S, new_listing=st.dates[0] > cal[5]) for s, st in stocks.items()}
    themes_path = os.path.join(os.path.dirname(stocks_path or ""), "themes.json")
    groups = groups_of(json.load(open(stocks_path)), json.load(open(themes_path)) if os.path.exists(themes_path) else []) \
        if stocks_path and os.path.exists(stocks_path) else {}
    GS = group_status(A, groups, cal)
    return A, groups, GS, cal, S


def detect(A, groups, GS, cal, S, upto=None):
    """every launch day up to calendar index `upto`, one per stock per dedupe window"""
    pos = {d: k for k, d in enumerate(cal)}
    events = []
    rank = {"A+": -1, "A": 0, "B": 1, "C": 2}
    for s, a in A.items():
        last = -10 ** 9
        for i in range(L["min_sessions"], len(a.st.dates)):
            k = pos.get(a.st.dates[i])
            if k is None or (upto is not None and k > upto) or not a.candidate(i):
                continue
            gs, gn = best_group(s, k, groups, GS)
            # one launch at a time: another within 20 sessions counts only after the last one closed below the
            # 21 EMA, or replaces it when it is the stronger day (APPN: a C on Aug 5 2026, the real launch, a B, on Aug 7)
            if i - last > L["dedupe_days"] or any(a.st.c[j] < a.e21[j] for j in range(last + 1, i)):
                events.append((s, i, k, gs, gn))
                last = i
            elif rank[grade(a, i)] < rank[grade(a, last)]:
                events[-1] = (s, i, k, gs, gn)
                last = i
    return events


def detect_followers(A, groups, GS, cal, events):
    """breakouts in a leader's wake: (sym, i, k, gs, gn, leader) for each follower day"""
    pos = {d: k for k, d in enumerate(cal)}
    led = collections.defaultdict(list)                      # theme -> [(calendar k, leader)] of A / B launches
    own = collections.defaultdict(list)
    for s, i, k, gs, gn in events:
        own[s].append(i)
        if grade(A[s], i) in ("A+", "A", "B"):
            for g in groups.get(s, ([], []))[0]:
                led[g].append((k, s))
    out = []
    for s, a in A.items():
        last = -10 ** 9
        for i in range(L["min_sessions"], len(a.st.dates)):
            k = pos.get(a.st.dates[i])
            if k is None or i - last <= L["dedupe_days"] or any(abs(i - j) <= L["dedupe_days"] for j in own[s]) or not a.follower(i):
                continue
            leaders = sorted({x for g in groups.get(s, ([], []))[0] for kk, x in led.get(g, []) if x != s and 0 <= k - kk <= 10})
            if leaders:
                gs, gn = best_group(s, k, groups, GS)
                out.append((s, i, k, gs, gn, " ".join(leaders)))
                last = i
    return out


def news_of(path):
    """{(symbol, date): "A: catalyst"} for gap-ups the pre-market grading gave an A or B"""
    try:
        rows = json.load(open(path))
    except Exception:
        return {}
    rows = rows.get("rows", rows) if isinstance(rows, dict) else rows
    return {(r["symbol"], r["date"]): (r["grade"] + (": " + r["catalyst"] if r.get("catalyst") else ""))
            for r in rows if isinstance(r, dict) and r.get("grade") in ("A", "B") and r.get("direction", "up") == "up" and r.get("symbol")}


def earnings_of(path, cal):
    """{symbol: the session its last earnings fell on} from the day's live quotes (an after-close report counts
    for the next session, the day the market reacts)"""
    try:
        rows = json.load(open(path))["rows"]
    except Exception:
        return {}
    import zoneinfo
    ny = zoneinfo.ZoneInfo("America/New_York")
    out = {}
    for s, q in rows.items():
        if len(q) > 6 and q[6]:
            t = datetime.datetime.fromtimestamp(q[6], ny)
            d = t.date().isoformat()
            if t.hour >= 16:                                   # reported after the close: the market reacts the next session
                d = next((x for x in cal if x > d), d)
            out[s] = d
    return out


def daily(A, groups, GS, cal, S, out_path, news=None, earnings=None):
    pos = {d: k for k, d in enumerate(cal)}
    today = cal[-1]
    T = len(cal) - 1
    rows = []
    ev = detect(A, groups, GS, cal, S)
    for s, i, k, gs, gn, leader in [e + ("",) for e in ev] + detect_followers(A, groups, GS, cal, ev):
        a = A[s]
        last = len(a.st.dates) - 1
        if a.st.dates[last] != today or last - i > L["follow_days"]:
            continue
        f = follow(a, i, last)
        if f["lost_50ema"]:
            continue
        r = launch_row(s, a, i, gs, gn, S)
        r.update(f)
        r["follows"] = leader or None
        r["news"] = (news or {}).get((s, r["date"]))
        r["earnings"] = (earnings or {}).get(s) == r["date"]
        cgs, cgn = best_group(s, T, groups, GS)
        r["group_now"], r["group_status_now"] = cgn, STATUS.get(cgs, "No group")
        up = next((kk for kk in range(k, T + 1) if best_group(s, kk, groups, GS)[0] >= 1), None)
        r["theme_up_since"] = cal[up] if up is not None else None      # first day from the launch its theme was trending
        r["lone_wolf"] = up is None
        rows.append(r)
    order = {"A+": -1, "A": 0, "B": 1, "C": 2}
    rows.sort(key=lambda r: (order[r["grade"]], -r["rel_vol"]))
    rows.sort(key=lambda r: r["date"], reverse=True)              # newest first, best grade first within a day
    # watch list for the intraday trigger: liquid, from 10% under to 28% over the 200 SMA, no launch in 20 days
    launched = {r["symbol"] for r in rows if r["sessions"] < L["dedupe_days"]}
    leaders = collections.defaultdict(set)              # theme -> A / B launches of the last 10 sessions (for followers)
    for r in rows:
        if r["grade"] in ("A+", "A", "B") and not r.get("follows") and r["sessions"] < 10:
            for g in groups.get(r["symbol"], ([], []))[0]:
                leaders[g].add(r["symbol"])
    watch = {}
    for s, a in A.items():
        st = a.st
        i = len(st.dates) - 1
        if st.dates[i] != today or s in launched or not a.liquid[i] or i < a.start:
            continue
        ext = 100 * (st.c[i] / a.s200[i] - 1)
        if ext > L["max_ext200"] or ext < -10:
            continue
        hi20 = st.h[i - L["base_days"] + 1:i + 1].max()          # tomorrow's "previous 20 days' high"
        hh = st.h[max(0, i - 119):i + 1]
        kk = int(np.argmax(hh))
        days = hh.size - 1 - kk
        depth = 100 * (1 - st.l[i - days:i + 1].min() / hh[kk]) if days > 0 else 0.0
        gs, gn = best_group(s, T, groups, GS)
        g = a.mem[i + 1] if i + 1 < st.c.size else -1
        if g < 0 and i - 9 >= 0:                    # tomorrow's memory: today may itself be a faded gap
            g2 = max((k for k in range(i - 9, i + 1) if a.gap[k] >= L["gap_big"] and a.rv[k] >= L["rv_big"] and st.c[k] > a.s200[k]
                      and a.ext200_prev[k] <= L["max_ext200"] and (a.clpos[k] < L["min_clpos"] or a.chg[k] < L["min_chg"])
                      and all(st.c[j] >= min(a.hi20[k], a.s200[k]) * 0.97 for j in range(k, i + 1))), default=-1)
            g = g2
        watch[s] = [fnum(st.c[i]), fnum(hi20), fnum(a.s200[i]), fnum(a.e21[i]), fnum(a.e50[i]), fnum(st.high52[i]),
                    int(days), fnum(depth, 0), gn, gs, run.tv_symbol(s, st.exchange),
                    [st.dates[g], fnum(a.hi20[g])] if g >= 0 else None,
                    " ".join(sorted({x for t in groups.get(s, ([], []))[0] for x in leaders.get(t, ()) if x != s})) or None]
    G = []
    for g, (ms, stt, sh21, m21) in GS.items():
        hist = [int(x) for x in stt[-20:]]
        since = next((len(hist) - j for j in range(len(hist) - 1, -1, -1) if hist[j] < 1), None) if hist[-1] >= 1 else None
        name = g[5:] + " area" if g.startswith("area:") else g
        launches = sorted({r["symbol"] for r in rows if name in (r["group"], r["group_now"]) and r["sessions"] <= 20})
        G.append(dict(group=g[5:] + " area" if g.startswith("area:") else g, status=STATUS[int(stt[-1])], members=len(ms), above_21ema_pct=fnum(100 * sh21[-1], 0),
                      median_1m_pct=fnum(m21[-1], 1), trending_days=since if since is not None else 0, recent_launches=launches))
    G.sort(key=lambda x: (-["Not trending", "Turning up", "Leading"].index(x["status"]), -(x["median_1m_pct"] or -999)))
    doc = dict(date=today, made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), rules=L,
               watch_fields=["close", "base_high_20d", "sma200", "ema21", "ema50", "high_52w", "days_since_high",
                             "correction_pct", "group", "group_status", "tv", "faded_gap [date, base high before it]", "leaders launched in its themes (10 sessions)"],
               launches=rows, watch=watch, groups=[g for g in G if g["status"] != "Not trending"])
    with open(out_path, "w") as f:
        json.dump(doc, f, separators=(",", ":"))
    n_today = sum(1 for r in rows if r["date"] == today)
    print(f"launch: {n_today} today, {len(rows)} followed, {len(watch)} on watch, {len(doc['groups'])} groups trending")


def backtest(A, groups, GS, cal, S, out_path):
    """each launch since the data starts: from the launch close to the first close below the 21 EMA"""
    res = []
    ev = detect(A, groups, GS, cal, S)
    for s, i, k, gs, gn, leader in [e + ("",) for e in ev] + detect_followers(A, groups, GS, cal, ev):
        a = A[s]
        c, o, lo = a.st.c, a.st.o, a.st.l
        n = c.size
        if ENTRY == "open":
            # bought in the launch day's first minutes (about the open; your opening-range-high entry is a bit higher),
            # stop under the launch day's low from the next day on, else out on the first close below the 21 EMA
            buy, stop = o[i], lo[i]
            exit_k, px = None, None
            for j in range(i + 1, n):
                if lo[j] <= stop:
                    exit_k, px = j, min(stop, o[j])
                    break
                if c[j] < a.e21[j]:
                    exit_k, px = j, c[j]
                    break
        else:
            buy = c[i]
            exit_k = next((j for j in range(i + 1, n) if c[j] < a.e21[j]), None)
            px = c[exit_k] if exit_k is not None else None
        if exit_k is None:
            continue                          # still open: no result yet
        g = grade(a, i)
        t10 = any(best_group(s, kk, groups, GS)[0] >= 1 for kk in range(k, min(k + 11, len(cal))))
        res.append(dict(sym=s, date=a.st.dates[i], grade=g, follower=bool(leader), theme=gs >= 1, theme10=t10, vol3=bool(a.rv[i] >= 3), bo=bool(c[i] > a.hi20[i]),
                        ret=100 * (px / buy - 1), days=exit_k - i, maxg=100 * (a.st.h[i:exit_k + 1].max() / buy - 1),
                        r20=100 * (c[min(i + 20, n - 1)] / buy - 1) if i + 20 < n else None))

    def summ(rs):
        if not rs:
            return None
        ret = np.array([r["ret"] for r in rs])
        mg = np.array([r["maxg"] for r in rs])
        r20 = np.array([r["r20"] for r in rs if r["r20"] is not None])
        return dict(n=len(rs), win_pct=fnum(100 * np.mean(ret > 0), 0), avg_exit_pct=fnum(ret.mean(), 1), median_exit_pct=fnum(np.median(ret), 1),
                    avg_days=fnum(np.mean([r["days"] for r in rs]), 1), ran_20pct=fnum(100 * np.mean(mg >= 20), 0),
                    ran_50pct=fnum(100 * np.mean(mg >= 50), 0), avg_20d_pct=fnum(r20.mean(), 1) if r20.size else None,
                    best=sorted(((round(r["ret"], 1), r["sym"], r["date"]) for r in rs), reverse=True)[:5])
    fol = [r for r in res if r["follower"]]
    res = [r for r in res if not r["follower"]]
    out = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), first=cal[200], last=cal[-1],
               rules=L, entry=ENTRY, all=summ(res), followers=summ(fol), by_grade={g: summ([r for r in res if r["grade"] == g]) for g in ("A+", "A", "B", "C")},
               trending_group=summ([r for r in res if r["theme"]]), not_trending_at_launch=summ([r for r in res if not r["theme"]]),
               theme_within_10d=summ([r for r in res if r["theme10"]]), lone_wolf_10d=summ([r for r in res if not r["theme10"]]),
               by_grade_theme10={g + (" theme" if t else " lone wolf"): summ([r for r in res if r["grade"] == g and r["theme10"] == t]) for g in ("A+", "A", "B", "C") for t in (True, False)},
               vol3=summ([r for r in res if r["vol3"]]), vol_under3=summ([r for r in res if not r["vol3"]]),
               base_breakout=summ([r for r in res if r["bo"]]), no_breakout=summ([r for r in res if not r["bo"]]))
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: (v if not isinstance(v, dict) or "n" not in v else {x: v[x] for x in ("n", "win_pct", "avg_exit_pct", "ran_20pct", "ran_50pct")})
                      for k, v in out.items() if k not in ("rules", "made_at")}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", help="the portal's stocks.json (radar-data branch), for themes and industries")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(HERE), "setups", "launch.json"))
    ap.add_argument("--backtest")
    ap.add_argument("--entry", choices=["open", "close"], default="open")
    ap.add_argument("--gradelog", help="the pre-market grade log (radar-data gradelog.json), for news tags")
    ap.add_argument("--live", help="the day's last live quotes (radar-data live.json), for earnings tags")
    a = ap.parse_args()
    global ENTRY
    ENTRY = a.entry
    A, groups, GS, cal, S = load(a.bars, a.stocks)
    daily(A, groups, GS, cal, S, a.out, news_of(a.gradelog) if a.gradelog else {}, earnings_of(a.live, cal) if a.live else {})
    if a.backtest:
        backtest(A, groups, GS, cal, S, a.backtest)


if __name__ == "__main__":
    main()
