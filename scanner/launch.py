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
  catalyst    a launch on earnings or meaningful news (the two tags above) that gapped 5%+, closed net positive and
              still in the gap (over the day before's high) and cleared at least its 1-month base, though up less
              than 5% or not in the top half of its range (GMAB Aug 7 2026: earnings, a 5.4% gap, +4.8%). Kept
              night to night in launch.json's catalyst_days
  legs        the launch is leg 1; each later leg = a close out of a base: above the base top (the highest high of
              the last ~6 months, at least 5 sessions old, with a pullback of 1.25+ of the stock's own ADRs from it)
              on 1x+ volume, from under it the day before; or a close above the falling trendline of a flag that formed at the highs. One leg per
              base (the next needs a new high first). RPD Oct 23 2026: a close of 14.91 over its Aug high of 14.80
              on 2.1x volume = leg 2 (Oct 26, +20% on 3.3x, confirmed it); its pokes inside the base are not legs. Depths are in each stock's own ADR: every ticker has its own character. One leg per pullback. A
              breakout after a rest of 40+ sessions without a new high starts a new run at leg 1 (SMCI rested
              about 114 sessions before its Jan 19 2024 launch).
              Flag = after a 25%+ rise, a 5-20 session pullback 1.25-4 ADRs deep that stays above the 50 EMA; its trendline
              runs from the top along the lower highs, and its buy point is tomorrow's value of that line (SMCI 2023:
              launch May 3, leg 2 May 16, leg 3 the flag breakout at the end of June). Breakouts got worse leg by leg (ran 20%+: leg 2 26%, leg 3 17%, leg 4 17%, leg 5+ 7%), so
              leg 4+ is flagged late; most launches never made a second leg
  new listings a stock listed less than 200 sessions ago uses its average close since listing in place of the 200
              SMA, once it has 60+ sessions (RDDT Oct 30 2024, its 155th day: a 28% gap, +42% on 7.9x volume to a new
              all-time high, +72% by the end of January)
  delayed     a gap of 3%+ on 3x+ volume above the 200 SMA that was not a launch itself (it faded, or failed a
              filter such as ADR 4%+) is remembered for 10 sessions; if the stock holds its old base (no close more than 3%
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

L = dict(bo_adr=0, bo_rv=1, leg_adr=1.25, flag_adr_min=1.25, flag_adr_max=4, min_sessions=60, rest_days=40, power_rv=4, power_gap=10, power_chg=15, power_ext200=50, aplus_gap=6, leg_pause=5, late_leg=4, min_chg=5, min_clpos=0.5, min_rv=1.5, max_ext200=28, min_above_low52=30, rv_big=3, gap_big=3, chg_big=10, base_days=20,
         near_high=70, neglect_days=40, neglect_depth=25, follow_days=120, dedupe_days=20, ep_gap=5, watch_under200=25,
         near_gap=2, near_rv=1.2, flag_run_adr=4, retest_days=20, retest_need_ema=0, bo_decisive=0, catalyst_launch=1, leg_decisive=0.5, dry_max=0.85, pop_tight=0.8, tight_body=0.5, rest_body=0.5)
STATUS = {2: "Leading", 1: "Turning up", 0: "Not trending"}
LIQ = dict(min_price=10, min_dollar_vol_20d_millions=20, min_avg_vol_20d=600000, min_adr=3.5)   # settings.json "launch"
BASES = (120, 63, 21)  # the bases a launch can clear: 6, 3 and 1 month(s)
CATALYST_DAYS = {}     # {(symbol, date): "earnings" / the news}: the days a catalyst launch can come on
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

    def __init__(self, st, S, new_listing=False, sym=None):
        self.st, self.sym = st, sym
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
        # your launch-list minimums (settings.json "launch"): price, 20-day average $ volume and shares, ADR
        LQ = dict(LIQ, **(S if S and "min_dollar_vol_20d_millions" in S else {}))
        avgv20, dv20 = roll_mean(v, 20), roll_mean(c * v, 20) / 1e6
        self.liquid = np.array([c[i] >= LQ["min_price"] and avgv20[i] >= LQ["min_avg_vol_20d"]
                                and dv20[i] >= LQ["min_dollar_vol_20d_millions"] and st.adr[i] >= LQ["min_adr"] for i in range(n)])
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
                    and self.ext200_prev[i] <= L["max_ext200"] and not self.candidate(i)):      # a big gap that was not a launch itself
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

    def cleared(self, i):
        """the longest base the close cleared, in sessions: 120 (6 months), 63 (3 months), 21 (1 month, the least a
        launch must clear) or 0. Cleared = over the top of its candle bodies (each day the higher of open and close;
        GMAB Aug 7 2026 closed 31.25 over 30.70, Feb 17's open, under that day's 31.41 wick). Older highs don't count:
        a launch is the stock's own inflection, not a new 1-year high"""
        st = self.st
        return next((n for n in BASES if i >= n and st.c[i] > np.maximum(st.o[i - n:i], st.c[i - n:i]).max()), 0)

    def catalyst(self, i):
        """a catalyst launch (earnings, news, a turnaround): a 5%+ gap that closes net positive, still in the gap
        (over the day before's high) and over at least its 1-month base, though up less than 5% (GMAB Aug 7 2026:
        a 5.4% gap, +4.8%, over its 6-month base)"""
        st = self.st
        return bool(L["catalyst_launch"] and self.gap[i] >= L["ep_gap"] and self.chg[i] > 0 and st.c[i] > st.h[i - 1]
                    and self.cleared(i) >= BASES[-1] and (self.sym, st.dates[i]) in CATALYST_DAYS)

    def candidate(self, i, catalyst=True):
        """the must-haves of a launch day (catalyst=False: the regular launch only)"""
        st = self.st
        return bool(i >= self.start and self.liquid[i] and self.gap[i] > 0
                    and ((self.chg[i] >= L["min_chg"] and self.held(i)) or (catalyst and self.catalyst(i)))
                    and self.rv[i] >= L["min_rv"] and st.c[i] > self.s200[i]
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
        # the longest base the launch day cleared (by the bodies): "6-month", "3-month", "1-month" or None
        cleared={120: "6-month", 63: "3-month", 21: "1-month"}.get(a.cleared(i)),
        catalyst=bool(a.catalyst(i) and not (a.chg[i] >= L["min_chg"] and a.held(i))),     # in on the catalyst rule only
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


def base_top(a, j, span=120):
    """the top of the base a breakout on day j clears: the highest high of the previous `span` sessions (120 = the
    larger base, ~6 months; 40 = the smaller one, ~2 months), leaving out the last 3 (the push into it), and how
    many sessions old that high is. RPD: the smaller base's top 13.87 (broken Oct 22 2026), the larger base's
    top 14.80, its Aug 11 high (broken Oct 23 on 2.1x volume, confirmed Oct 26)"""
    h = a.st.h
    lo, hi = max(0, j - span), j - 3
    if hi - lo < 10:
        return None, 0
    k = lo + int(np.argmax(h[lo:hi]))
    return h[k], j - k


def _adr(st, k):
    return st.adr[k] if st.adr[k] > 0 else 5.0


def base_ok(a, j, span):
    """(top, its index) when the base before day j is real: its top is 5+ sessions old and it pulled back 1.25+ of
    the stock's own ADRs from it (each ticker has its own character); else None"""
    st = a.st
    top, age = base_top(a, j, span)
    if not top or age < L["leg_pause"]:
        return None
    k = j - age
    if 100 * (1 - st.l[k:j].min() / top) < L["leg_adr"] * _adr(st, k):
        return None
    # and the closes pulled back too: a one-day dip in an advance is no base (GMAB Sep 23-30 2026: one down day,
    # Sep 24, the closes 2% under the top at most, then higher again; Sep 30's close over it was no breakout)
    if 100 * (1 - st.c[k + 1:j].min() / top) < L["leg_adr"] * _adr(st, k):
        return None
    return top, k


def base_breakout(a, j, used=()):
    """(top, its index) of the base a close on day j breaks out of, the larger base first; a breakout = a close half an
    ADR or more over the top on 1x+ volume (a weaker close over it mostly fell back: 60-70% within 5 days; GMAB Aug 14,
    Sep 18 2026), fresh (no such close in the 3 days before, not already run an ADR past it)"""
    st, c = a.st, a.st.c
    for span in (120, 40):
        b = base_ok(a, j, span)
        if not b or b[1] in used:
            continue
        top, k = b
        dec = top * (1 + L["bo_decisive"] * _adr(st, j) / 100)
        if (c[j] > dec and a.rv[j] >= L["bo_rv"] and max(c[j - 3:j]) <= dec
                and st.h[j - 3:j].max() < top * (1 + _adr(st, j - 1) / 100)):
            return b
    return None


def below_since(a, j, level, k):
    """the base's length on day j: sessions since anything last traded above `level` before its top was set on
    day k (RPD: 13.87, set Oct 12 2026, last exceeded Aug 11; 14.80, set Aug 11, last exceeded in January)"""
    h = a.st.h
    for m in range(k - 1, max(-1, k - 253), -1):
        if h[m] > level:
            return j - m - 1
    return j - max(0, k - 252)


def resting(a, k):
    """day k is part of a consolidation, the stock's resting time: the volume dried up (5-day average 0.85 or less of
    the 50-day) while it surfs the 10 and 21 EMA (closing within an ADR of both) above the 50 EMA, with no big candle
    (body half an ADR or less) (ANF Sep 17 - Oct 2 2026, your "Sep 18 - Oct 4 or so": bodies 0.06-0.47 ADR)"""
    st, c = a.st, a.st.c
    if k < 50:
        return False
    adr = _adr(st, k)
    dry = st.v[k - 4:k + 1].mean() / st.v[k - 50:k].mean()
    return bool(dry <= L["dry_max"] and abs(c[k] / a.e10[k] - 1) <= adr / 100 and abs(c[k] / a.e21[k] - 1) <= adr / 100 and c[k] > a.e50[k]
                and abs(c[k] - st.o[k]) <= L["rest_body"] * adr / 100 * c[k - 1])


def dry_armed(a, k, top):
    """a dry-up entry is set up at the close of day k (your rule: a regular consolidation, the volume drying up, surfing
    the 10 and 21 EMA; ANF Oct 2 2026): inside the base, an ADR+ under its top; 5-day volume 0.75 or less of the
    50-day; closing within an ADR of both the 10 and the 21 EMA, above the 50 EMA. Its trigger is the pop out of it,
    the price expanding after the contraction (Qullamaggie: a breakout from a tight flag): see pop_level."""
    return all(resting(a, k - m) for m in range(3)) and bool(a.st.c[k] <= top * (1 - _adr(a.st, k) / 100))   # 3+ days of rest


def pop_level(a, k):
    """the pop after a setup on day k: day k is a tight candle, its range 0.8 ADR or less and its body half an ADR or less
    (ANF Oct 2 2026: range 0.74 ADR, body 0.11; Oct 1, range 1.02, body 0.33, was none) and the next day opens above its open and close and above the 10 and 21 EMA, both rising: pushing out of
    the surf (ANF Oct 5: opened 136.97 over Oct 2's 136.49 / 135.91 and its 10 / 21 EMA of 135.72 / 135.03; Oct 1 was
    no tight candle, 4.0%, and Oct 2's open faded). Returns the price the open has to clear, or None."""
    st = a.st
    unit = _adr(st, k) / 100 * st.c[k - 1]                 # one ADR in dollars
    if (not (a.e10[k] > a.e10[k - 1] and a.e21[k] > a.e21[k - 1]) or st.h[k] - st.l[k] > L["pop_tight"] * unit
            or abs(st.c[k] - st.o[k]) > L["tight_body"] * unit):
        return None
    return max(st.o[k], st.c[k], a.e10[k], a.e21[k])


def follow(a, i0, i, pick=False):
    """what happened from the launch close (i0) to bar i: status, gain, exit signal, current base and pattern.
    pick: a stock you follow from the Watchlist tab, from the close you added it at (i0): no launch day, and its top
    starts at its base top when it was under it"""
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
    # a leg = a close out of a base: above the base top (the highest high of ~6 months, at least 5 sessions old)
    # on 1x+ volume, from under it the day before (RPD Oct 23 2026: 14.91 over its 14.80 Aug high on 2.1x); or a close above the trendline
    # of a flag that formed at the highs. A poke that falls back (RPD Oct 9, inside its base) is no leg.
    # One leg per base: after a leg, the next needs a new high first.
    # leg 1 = the launch when it closed out of its base (SMCI May 3 2023, at an all-time high); a launch inside its
    # base (RPD Sep 14 2026, under its Aug high) is leg 0 until the first breakout out of the base
    b0 = base_ok(a, i0, 120)
    leg = 1 if not b0 or c[i0] > b0[0] or a.cleared(i0) >= BASES[-1] else 0    # cleared at least its 1-month base by the bodies: leg 1 (GMAB Aug 7)
    H, last_new, armed, rested, last_leg = st.h[i0], i0, False, None, i0
    if pick and b0 and b0[0] > H:
        H = b0[0]
    used, bo = set(), None                                  # bo = (day, top, top index) of the last base breakout
    # the level a retest comes back to: the broken base's top, by the candle bodies (each day the higher of its open and
    # close) or by the wicks, either one (SPOT Oct 2026: the bodies topped at $536.98 under the $540.82 wick).
    # rlv = (breakout day, bodies' top, wick top). A launch that closed out of its base broke that base too (SPOT Oct 22
    # over its October base, back to it Oct 28)
    body = lambda lo, hi: float(np.maximum(st.o[lo:hi], st.c[lo:hi]).max())
    rlv = (i0, min(body(i0 - 20, i0), st.h[i0 - 20:i0].max()), float(st.h[i0 - 20:i0].max())) \
        if i0 >= 20 and c[i0] > st.h[i0 - 20:i0].max() else None
    dry_done, dry_day, flag_day = False, None, None         # one dry-up entry per base (ANF: Oct 5 2026, not again)
    lvl = H                                                 # the level the leg broke out of: the launch day's high, then the base top
    nbo = 0                                                 # breakouts since the launch (for the grade: the 1st and 2nd work best)
    for j in range(i0 + 1, i + 1):
        if not dry_done and dry_armed(a, j - 1, H):
            lv = pop_level(a, j - 1)
            if lv and st.o[j] > lv:
                dry_done, dry_day = True, j
        f = flag_at(a, j) if armed else None
        # a flag at the highs, after the leg has run 4+ of the stock's own ADRs from its start (SMCI Jun 2023: 85%,
        # 13 ADRs, then the flag); a trendline break in the base right after a launch is an entry, not a new leg
        # (ANF Sep 16 2026: 5% past its Aug 26 launch close; Oct 5, after the volume dried up, your entry in the base)
        at_highs = bool(f and st.h[f[0]] >= st.h[max(0, f[0] - 120):f[0] + 1].max()
                        and st.h[f[0]] >= c[last_leg] * (1 + L["flag_run_adr"] * _adr(st, last_leg) / 100))
        flag_go = bool(f and at_highs and f[0] not in used and c[j] > f[2] and c[j - 1] <= (flag_at(a, j - 1) or (0, 0, np.inf))[2])
        b = base_breakout(a, j, used)
        if flag_go:
            flag_day, lvl = j, st.h[f[0]]
        if flag_go or b:
            nbo += 1
            used.add(f[0] if flag_go else b[1])           # each base top gives at most one breakout
            if b:
                bo, lvl = (j, b[0], b[1]), b[0]
                rlv = (j, min(body(max(0, b[1] - 20), max(b[1] + 1, j - 3)), b[0]), float(b[0]))   # the base's bodies, not the push into it
            # a new leg needs a decisive close (half an ADR over the top): a weaker one is a breakout, still the same leg
            # (GMAB 2026: the launch Aug 7 leg 1; Aug 14 and Sep 18 closed just over their tops; Oct 5 leg 2, Oct 23 leg 3)
            weak = bool(b and not flag_go and c[j] < b[0] * (1 + L["leg_decisive"] * _adr(st, j) / 100))
            if not weak and (leg == 0 or j - last_leg >= L["leg_pause"]):  # breakouts a few days apart (Oct 22 / Oct 23) are one leg
                # after a rest of 40+ sessions without a new high, the breakout starts a new run: leg 1 again
                leg = 1 if j - last_new >= L["rest_days"] else leg + 1
                if leg == 1 and j - last_new >= L["rest_days"]:
                    rested = j
                last_leg, armed = j, False
        if st.h[j] > H:
            H, last_new, armed, dry_done = st.h[j], j, True, False
    hi = st.h[i0:i + 1].max()
    status = "Riding" if c[i] >= a.e21[i] else "Below 21 EMA"
    fl = flag_at(a, i)
    # a flag is a pattern only at the highs, after the leg ran 4+ ADRs (SMCI Jun 2023); a falling line inside the
    # base right after a launch is none (ANF Sep 2026: under the Aug 26 gap day's high the whole time, one structure)
    flag_leg = bool(fl and st.h[fl[0]] >= st.h[max(0, fl[0] - 120):fl[0] + 1].max()
                    and st.h[fl[0]] >= c[last_leg] * (1 + L["flag_run_adr"] * _adr(st, last_leg) / 100))
    if not flag_leg:
        fl = None
    flag_bo = flag_day == i
    # tomorrow's base tops (the smaller and the larger base): buy points when above today's close
    tops = [b for b in (base_ok(a, i + 1, 40), base_ok(a, i + 1, 120)) if b and c[i] < b[0]]
    # the buy point = the nearest trigger above today's close: your MSF pattern's pivot, the flag's trendline or
    # the base top (RPD Oct 23 2026 had closed just over its MSF pivot of 14.80; the base top trigger 15.02 is what
    # Oct 26 broke on 3.3x volume)
    cands = []
    if code and msf.is_pat(code) and r.pivot == r.pivot and c[i] < r.pivot:   # not "Base forming (no pattern yet)":
        cands.append((float(r.pivot), msf.NAMES[code], r.cN, r.cDep))        # that's only a recent high (ANF Oct 26 2026)
    if fl:
        cands.append((fl[3], "Flag (trendline)", i - fl[0], fl[1]))
    if not dry_done and dry_armed(a, i, H) and pop_level(a, i):
        cands.append((float(pop_level(a, i)), "Pop out of the consolidation (in base)", i - last_new, 100 * (1 - st.l[last_new:i + 1].min() / H)))
    for top, k in tops:
        cands.append((top, "Base top", below_since(a, i + 1, top, k), 100 * (1 - st.l[k:i + 1].min() / top)))
    bp, pat, bdays, bdep = min(cands) if cands else (None, msf.NAMES[code] if code else "", r.cN if code else None, r.cDep if code else None)
    top_date = next((st.dates[k] for t, k in tops if bp is not None and t == bp), None)
    adr = _adr(st, i)
    # retest held, at the close: within 20 sessions of a breakout, while it hasn't closed an ADR under the level, the
    # low comes back to the level, the bodies' top or the wick top (from 1.5 ADRs under the bodies' top up to the wick
    # top; a low that stays over it never touched: ANF Aug 14 2026, 106.19 over 105.16) and the close holds above the
    # bodies' top and the 21 EMA, on the day that makes the pullback's low: the undercut and reclaim (GMAB Oct 2 2026:
    # Oct 1 touched 34.51 and closed 34.55 under 34.63; Oct 2 down to 33.72, closed 34.75 over the level and the 21 EMA
    # 34.39). ANF Aug 2026: Aug 17 touched 105.16 and closed 105.16 under its 21 EMA 105.36, Aug 18 undercut to 100.43
    # and closed 103.38 under it again, Aug 19-20 no new low: consolidation, no retest. Once per breakout
    # (ANF Oct 23 2026: low 152.73, close 155.82 over 153.41; SPOT Oct 28: low 536.74, close 538.40 over 536.98).
    # It has to be a pullback (RPD Oct 26 2026 opened at its level and ran 20%: the confirmation, no retest). Confluence: the 10, 21 or 50 EMA at the level too (within an ADR of it), the low
    # at it and the close above it (SPOT: the 21 EMA $536.18)
    def touch_on(k):
        """the retest's try on day k: 3+ sessions after the breakout (a dip in the first two is the breakout settling at
        the base high, not a retest: GMAB Sep 24 2026), a real pullback (the low 1.5+ ADRs under the high since the
        breakout: drifting at the base high is consolidating, GMAB Sep 23 - Oct 1), after closing 1.25+ ADRs away from
        the level, the low at the level (undercut and reclaim: GMAB Oct 2, from 35.90 down to 33.72 under 34.63)"""
        ak = _adr(st, k)
        return bool(rlv and 3 <= k - rlv[0] <= L["retest_days"]
                    and rlv[1] * (1 - 1.5 * ak / 100) <= st.l[k] <= max(rlv[2], rlv[1] * (1 + ak / 400))
                    and st.l[k] <= st.h[rlv[0]:k].max() * (1 - 1.5 * ak / 100)
                    and c[rlv[0]:k].max() >= rlv[1] * (1 + 1.25 * ak / 100))

    def retest_on(k):
        ak = _adr(st, k)
        ok = touch_on(k) and c[k] > rlv[1] and c[k] > a.e21[k]       # held: over the bodies' top and the 21 EMA
        conf = [n for n, e in (("10 EMA", a.e10), ("21 EMA", a.e21), ("50 EMA", a.e50))
                if ok and rlv[1] * (1 - ak / 100) <= e[k] <= rlv[2] * (1 + ak / 100) and st.l[k] <= e[k] * (1 + ak / 400) and c[k] > e[k]]
        return ok, conf
    held = bool(rlv and 1 <= i - rlv[0] <= L["retest_days"] and not (c[rlv[0] + 1:i + 1] < rlv[1] * (1 - adr / 100)).any())
    hit = lambda k: bool(retest_on(k)[1]) if L["retest_need_ema"] else retest_on(k)[0]
    first = next((k for k in range(rlv[0] + 1, i + 1) if touch_on(k)), None) if rlv else None     # the first touch
    rday = lambda k: bool(hit(k) and st.l[k] <= st.l[rlv[0] + 1:k].min())          # the pullback's low, reclaimed
    done = next((k for k in range(rlv[0] + 1, i + 1) if rday(k)), None) if rlv else None
    retest = bool(held and done == i)
    retest_ema = retest_on(i)[1] if retest else []
    # tomorrow's zone, for the heads-up during the day (the buy alert itself waits for the close): until a retest held
    zone = [fnum(rlv[1] * (1 - 1.5 * adr / 100)), fnum(max(rlv[2], rlv[1] * (1 + adr / 400)))] \
        if held and 2 <= i - rlv[0] < L["retest_days"] and done is None else None
    # the push out of the 21 EMA with a gap, within 5 sessions of the retest's try, held or not (ANF Aug 21 2026 after
    # touching 105.16 on Aug 17: opened 107.24 over Aug 20's candle and its 10 / 21 EMA 107.04 / 105.19; GMAB Oct 5
    # after Oct 2): the day before still at the EMAs (closed at or under the 10 EMA, over the 50 EMA), it opens over
    # that day's open and close and its 10 and 21 EMA. Once per breakout
    push_lv = lambda k: max(st.o[k], c[k], a.e10[k], a.e21[k])
    push_armed = lambda k: bool(held and first is not None and first <= k <= first + 5 and c[k] <= a.e10[k] and c[k] > a.e50[k])
    push_day = next((j for j in range(first + 1, min(i, first + 6) + 1) if push_armed(j - 1) and st.o[j] > push_lv(j - 1)), None) \
        if first is not None else None
    push_level = push_lv(i) if push_armed(i) and push_day is None else None     # what tomorrow's open has to clear
    # tight under the buy point (a level: a base top or a pattern's pivot, not a falling flag line): closes within an
    # ADR under it, 2+ tight days in a row: tight bodies (half an ADR or less) close to the base high, whatever the
    # wicks (ANF Oct 15-16 2026: 2.1% and 1.3% under its 155.22 base top, bodies 0.00 and 0.05 ADR; broke out Oct 19),
    # the day's move under half an ADR
    tight = 0
    if bp and pat in ("Base top",) + tuple(msf.NAMES[k] for k in range(1, 13) if msf.is_pat(k)):
        for k in range(i, max(i0, i - 10), -1):
            if not (bp * (1 - _adr(st, k) / 100) <= c[k] < bp and abs(a.chg[k]) <= _adr(st, k) / 2
                    and abs(c[k] - st.o[k]) <= L["tight_body"] * _adr(st, k) / 100 * c[k - 1]
                    and max(c[k:i + 1]) - min(c[k:i + 1]) <= _adr(st, i) / 200 * c[i]):   # sideways, not advancing
                break
            tight += 1
    # advancing is not tight: every one of those days a higher high, higher low and higher close than the day before
    # (GMAB Oct 20-22 2026, a staircase into $40.17; ANF Oct 16 made a lower high, so Oct 15-16 was tight)
    if tight >= 2 and all(st.h[k] > st.h[k - 1] and st.l[k] > st.l[k - 1] and c[k] > c[k - 1] for k in range(i - tight + 1, i + 1)):
        tight = 0
    # the base under the buy point, for the heads-up: since the stock first came within a quarter ADR of that high in
    # this leg (ANF: the Aug 26 gap day's 154.58, with the 155.22 of Sep 9 as the top: 35 sessions), how deep it went,
    # and your MSF engine's pattern for it if it sees one
    bfrom = blen = bdeep = bdeep_adr = None
    if bp:
        near = [m for m in range(last_leg, i + 1) if st.h[m] >= bp * (1 - _adr(st, m) / 400)]
        if near:
            m0 = near[0]
            blen, bfrom = i - m0, st.dates[m0 + 1] if m0 + 1 <= i else st.dates[i]
            bdeep = 100 * (1 - st.l[min(m0 + 1, i):i + 1].min() / bp)       # from the day after (not the gap day's own low)
            bdeep_adr = bdeep / _adr(st, i)
    msf_pat = msf.NAMES[code] if code and msf.is_pat(code) else None
    # the stock's stage after the close, the first that applies
    rest = 0
    while i - rest > i0 and resting(a, i - rest):
        rest += 1
    since = None
    if i == i0 and not pick:
        cb = {120: "6-month", 63: "3-month", 21: "1-month"}.get(a.cleared(i))
        stage = "Launch day" + (f", cleared its {cb} base" if cb else "")
    elif bo and bo[0] == i:
        # how decisively it closed over the top (2 years, 906 breakouts: 0.5+ ADR over, about 30% fell back under
        # the top within 5 days; less, 60-70%)
        ov = (c[i] / bo[1] - 1) * 100 / _adr(st, i)
        stage = f"Base breakout (leg {leg}), closed {ov:.1f} ADR over the top" + (": decisive" if ov >= 0.5 else ": weak, most of these fell back")
    elif flag_bo:
        stage = f"Flag breakout (leg {leg})"
    elif dry_day == i:
        stage = "Pop out of the consolidation (entry in base)"
    elif push_day == i:
        stage = f"Push out of the 21 EMA with a gap, after the retest of {rlv[1]:.2f}" + (f"-{rlv[2]:.2f}" if rlv[2] > rlv[1] * 1.001 else "")
    elif retest:
        lv_txt = f"{rlv[1]:.2f}" if rlv[2] <= rlv[1] * 1.001 else f"{rlv[1]:.2f}-{rlv[2]:.2f} (bodies-wicks)"
        stage = f"Retest of the breakout level {lv_txt} held" + (" + confluence: " + " & ".join(retest_ema) if retest_ema else "")
    elif tight >= 2:
        stage = f"Tight under {bp:.2f}, the base high ({tight} days)" + (
            f" · base {blen} sessions, {bdeep:.0f}% deep ({bdeep_adr:.1f} ADRs)" + (f", {msf_pat}" if msf_pat else "") if blen else "")
    elif rest >= 3:
        since = st.dates[i - rest + 1]
        stage = f"Consolidation, surfing the 10 & 21 EMA on dry volume ({rest} days)" + (f", {100 * (1 - c[i] / H):.0f}% under the top {H:.2f}" if c[i] < H * 0.99 else "")
    elif c[i] < a.e21[i]:
        stage = "Below the 21 EMA"
    elif c[i] > lvl:                                       # closing above what the leg broke out of (ANF: never over
        stage = f"Running (leg {leg}), {100 * (c[i] / lvl - 1):.0f}% over {lvl:.2f}"   # the Aug 26 high until Oct 19)
    else:
        stage = f"In the base, {100 * (1 - c[i] / H):.0f}% under the top {H:.2f}"
    return dict(
        stage=stage, stage_since=since, msf_pattern=msf_pat, breakouts=nbo,
        # the base forming now, as your MSF engine names it (High tight flag, Bull flag, Pennant, Ascending triangle,
        # Flat base, Cup with handle, ... or Base forming (no pattern yet))
        base_pattern=msf.NAMES[code] if code else None,
        # the day of the base: sessions since the launch or the leg's breakout (ANF: Aug 26 = day 0, Sep 10 day 10,
        # Sep 24 day 20; Oct 19, leg 2, day 0 again), and whether today it turned up: back over a rising 10 EMA after
        # closing under it (ANF Oct 1, day 25)
        base_day=i - last_leg,
        turned_up=bool(i > last_leg and c[i] > a.e10[i] > a.e10[i - 1] and not (c[i - 1] > a.e10[i - 1] > a.e10[i - 2])),
        vol_build=fnum(st.v[i - 4:i + 1].mean() / st.v[i - 54:i - 4].mean(), 2) if i >= 54 else None,
        base_from=bfrom, base_len=blen, base_low_pct=fnum(bdeep, 1) if bdeep is not None else None,
        base_low_adr=fnum(bdeep_adr, 1) if bdeep_adr is not None else None,
        retest_today=retest, retest_ema=retest_ema, retest_level=fnum(rlv[1]) if rlv else None, retest_level_wick=fnum(rlv[2]) if rlv else None,
        retest_from=st.dates[rlv[0]] if rlv else None, retest_zone=zone, tight_days=tight,
        # for the retest alerts during the day (radar/alerts.py), with the zone: the low has to get this far under the
        # high since the breakout (a real pullback, 1.5 ADRs), and whether it already closed 1.25 ADRs away from the level
        retest_need_low=fnum(st.h[rlv[0]:i + 1].max() * (1 - 1.5 * adr / 100)) if zone else None,
        retest_away=bool(c[rlv[0]:i + 1].max() >= rlv[1] * (1 + 1.25 * adr / 100)) if zone else None,
        retest_tried=st.dates[first] if first is not None else None,
        retest_low=fnum(st.l[rlv[0] + 1:i + 1].min()) if zone else None,          # tomorrow's low has to undercut it
        push_level=fnum(push_level) if push_level else None, push_today=push_day == i,
        adr_pct=fnum(adr, 2), ema10=fnum(a.e10[i]), ema50=fnum(a.e50[i]), day_open=fnum(st.o[i]),
        sessions=i - i0, gain_pct=fnum(100 * (c[i] / c[i0] - 1), 1), max_gain_pct=fnum(100 * (hi / c[i0] - 1), 1),
        status=status, first_exit=st.dates[exit_k] if exit_k is not None else None,
        exit_gain_pct=fnum(100 * (c[exit_k] / c[i0] - 1), 1) if exit_k is not None else None,
        lost_50ema=st.dates[out50] if out50 is not None else None,
        price=fnum(c[i]), chg_today_pct=fnum(a.chg[i], 1), rel_vol_today=fnum(a.rv[i], 1),
        pattern=pat, buy_point=fnum(bp) if bp else None, to_buy_point_pct=fnum(100 * (bp / c[i] - 1), 1) if bp else None,
        buy_point_top_date=top_date,
        base_breakout_today=bool(bo and bo[0] == i),
        last_breakout_date=st.dates[bo[0]] if bo else None, last_breakout_top=fnum(bo[1]) if bo else None,
        last_breakout_top_date=st.dates[bo[2]] if bo else None, last_breakout_days_ago=i - bo[0] if bo else None,
        last_breakout_base_days=below_since(a, bo[0], bo[1], bo[2]) if bo else None,
        base_days=fnum(bdays, 0) if bdays is not None else None, base_depth_pct=fnum(bdep, 1) if bdep is not None else None,
        flag_breakout_today=flag_bo, dry_entry_today=dry_day == i,
        base_depth_adr=fnum((bdep if bdep is not None else np.nan) / (st.adr[i] if st.adr[i] > 0 else np.nan), 1), surf10=surf(a.e10), surf21=surf(a.e21),
        vol_dryup=fnum(dry, 2), off_high_pct=fnum(100 * (1 - c[i] / hi), 1), ema21=fnum(a.e21[i]),
        breakout_today=bool(code and msf.is_pat(code) and r.bo == 1), leg=leg, late=leg >= L["late_leg"],
        new_run_after_rest=st.dates[rested] if rested is not None else None,
        days_since_new_high=i - last_new,
    )


def load(bars_path, stocks_path):
    cfg = json.load(open(os.path.join(HERE, "settings.json")))
    D = run.load_bars(bars_path)
    # run during market hours (a manual rebuild), the bars end with today's unfinished session: leave it out, so
    # launches and the watch list come from the last close
    import zoneinfo
    now = datetime.datetime.now(zoneinfo.ZoneInfo("America/New_York"))
    if (now.hour, now.minute) < (16, 5):
        for b in D["bars"].values():
            if b and b[-1][0] == now.date().isoformat():
                b.pop()
    stocks, P = run.build(D, cfg)
    cal = [b[0] for b in D["bars"]["SPY"]]
    S = cfg["standard"]
    LIQ.update({k: v for k, v in cfg.get("launch", {}).items() if not k.startswith("_")})
    # a stock whose bars start after the file's first session listed during it (the file reaches 2 years back)
    A = {s: Arr(st, LIQ, new_listing=st.dates[0] > cal[5], sym=s) for s, st in stocks.items()}
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
        own, cat = [], []
        for i in range(L["min_sessions"], len(a.st.dates)):
            k = pos.get(a.st.dates[i])
            if k is None or (upto is not None and k > upto) or not a.candidate(i):
                continue
            if not a.candidate(i, catalyst=False):
                cat.append((i, k))
                continue
            gs, gn = best_group(s, k, groups, GS)
            # one launch at a time: another within 20 sessions counts only after the last one closed below the
            # 21 EMA, or replaces it when it is the stronger day (APPN: a C on Aug 5 2026, the real launch, a B, on Aug 7)
            if i - last > L["dedupe_days"] or any(a.st.c[j] < a.e21[j] for j in range(last + 1, i)):
                own.append((s, i, k, gs, gn))
                last = i
            elif rank[grade(a, i)] < rank[grade(a, last)]:
                own[-1] = (s, i, k, gs, gn)
                last = i
        # a catalyst launch comes on top and never blocks a regular one (those stay exactly as they were): it counts
        # when no launch came in the 20 sessions before it, or the last one closed below the 21 EMA since
        for i, k in cat:
            prev = max((e[1] for e in own if e[1] < i), default=-10 ** 9)
            if i - prev > L["dedupe_days"] or any(a.st.c[j] < a.e21[j] for j in range(prev + 1, i)):
                gs, gn = best_group(s, k, groups, GS)
                own.append((s, i, k, gs, gn))
        events.extend(sorted(own, key=lambda e: e[1]))
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


def picks_of(path):
    """{symbol: when you added it (ISO time, New York)} from setups/picks.json (the portal's Follow button)"""
    try:
        return {s.upper(): p["added"] for s, p in json.load(open(path)).get("picks", {}).items() if p.get("added")}
    except Exception:
        return {}


def daily(A, groups, GS, cal, S, out_path, news=None, earnings=None, picks=None):
    pos = {d: k for k, d in enumerate(cal)}
    today = cal[-1]
    T = len(cal) - 1
    rows = []
    # the earnings and news days a catalyst launch can come on: tonight's tags plus the ones kept from earlier nights
    # (Yahoo's earnings date moves on to the next report; the grade log keeps only the last days)
    try:
        kept = {(d[0], d[1]): d[2] for d in json.load(open(out_path)).get("catalyst_days", [])}
    except Exception:
        kept = {}
    tags = dict(kept)
    for s, d in (earnings or {}).items():
        a = A.get(s)
        if a is not None and d in a.st.dates[-200:]:
            k = a.st.dates.index(d)
            for m in range(k, min(k + 2, len(a.st.dates))):    # and the session after: GMAB raised its guidance at 3:52 PM
                tags[(s, a.st.dates[m])] = "earnings"           # on Aug 6 2026, the gap came Aug 7
    tags.update({k: "news " + v for k, v in (news or {}).items()})
    CATALYST_DAYS.clear()
    for (s, d), w in tags.items():
        a = A.get(s)
        k = a.st.dates.index(d) if a is not None and d in a.st.dates[-200:] else None
        if k is not None and a.gap[k] >= L["ep_gap"]:
            CATALYST_DAYS[(s, d)] = w
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
        r["earnings"] = (earnings or {}).get(s) == r["date"] or CATALYST_DAYS.get((s, r["date"])) == "earnings"
        if r["catalyst"]:
            r["catalyst"] = CATALYST_DAYS.get((s, r["date"]))
        cgs, cgn = best_group(s, T, groups, GS)
        r["group_now"], r["group_status_now"] = cgn, STATUS.get(cgs, "No group")
        up = next((kk for kk in range(k, T + 1) if best_group(s, kk, groups, GS)[0] >= 1), None)
        r["theme_up_since"] = cal[up] if up is not None else None      # first day from the launch its theme was trending
        r["lone_wolf"] = up is None
        rows.append(r)
    order = {"A+": -1, "A": 0, "B": 1, "C": 2}
    rows.sort(key=lambda r: (order[r["grade"]], -r["rel_vol"]))
    rows.sort(key=lambda r: r["date"], reverse=True)              # newest first, best grade first within a day
    # one launch per stock: the newest (ANF: the Aug 26 2026 power day replaced the Aug 3 C launch, which had
    # closed below the 21 EMA on Aug 17; both followed gave two alerts with different legs)
    seen = set()
    rows = [r for r in rows if not (r["symbol"] in seen or seen.add(r["symbol"]))]
    # your picks (the portal's Follow button on the Watchlist tab), followed like a launch from the close you added
    # them at (that day's close after 4 PM, else the session before), until you remove them. A stock already
    # followed as a launch keeps its launch row, marked as yours too
    have = {r["symbol"]: r for r in rows}
    for s, added in (picks or {}).items():
        if s in have:
            have[s]["pick"] = added
            continue
        a = A.get(s)
        if a is None:
            continue
        last = len(a.st.dates) - 1
        try:
            t = datetime.datetime.fromisoformat(added)
        except ValueError:
            continue
        d = t.date().isoformat()
        i0 = max((k for k in range(last + 1) if a.st.dates[k] < d or (a.st.dates[k] == d and t.hour >= 16)), default=None)
        if a.st.dates[last] != today or i0 is None or i0 < 60:
            continue
        k0 = pos.get(a.st.dates[i0], T)
        gs, gn = best_group(s, k0, groups, GS)
        r = launch_row(s, a, i0, gs, gn, S)
        r.update(follow(a, i0, last, pick=True))
        cgs, cgn = best_group(s, T, groups, GS)
        r.update(grade="You", pick=added, follows=None, news=None, earnings=False, group_now=cgn,
                 group_status_now=STATUS.get(cgs, "No group"), theme_up_since=None, lone_wolf=False)
        rows.append(r)
    # watch list for the intraday trigger: liquid, from 25% under to 50% over the 200 SMA (over 28%: power days
    # only; under it: only once it trades back above it, e.g. a catalyst gap), no launch in 20 days
    launched = {r["symbol"] for r in rows if r["sessions"] < L["dedupe_days"] and not r["first_exit"] and r["grade"] != "You"}
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
        if ext > L["power_ext200"] or ext < -L["watch_under200"]:  # 28-50% over: power days only (the trigger checks)
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
                    " ".join(sorted({x for t in groups.get(s, ([], []))[0] for x in leaders.get(t, ()) if x != s})) or None,
                    fnum(st.c[i - 49:i + 1].mean()) if i >= 49 else None]
    G = []
    for g, (ms, stt, sh21, m21) in GS.items():
        hist = [int(x) for x in stt[-20:]]
        since = next((len(hist) - j for j in range(len(hist) - 1, -1, -1) if hist[j] < 1), None) if hist[-1] >= 1 else None
        name = g[5:] + " area" if g.startswith("area:") else g
        launches = sorted({r["symbol"] for r in rows if name in (r["group"], r["group_now"]) and r["sessions"] <= 20})
        G.append(dict(group=g[5:] + " area" if g.startswith("area:") else g, status=STATUS[int(stt[-1])], members=len(ms), above_21ema_pct=fnum(100 * sh21[-1], 0),
                      median_1m_pct=fnum(m21[-1], 1), trending_days=since if since is not None else 0, recent_launches=launches))
    G.sort(key=lambda x: (-["Not trending", "Turning up", "Leading"].index(x["status"]), -(x["median_1m_pct"] or -999)))
    doc = dict(date=today, made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), rules=L, liquidity=dict(LIQ),
               watch_fields=["close", "base_high_20d", "sma200", "ema21", "ema50", "high_52w", "days_since_high",
                             "correction_pct", "group", "group_status", "tv", "faded_gap [date, base high before it]", "leaders launched in its themes (10 sessions)",
                             "sma50"],
               launches=rows, watch=watch, groups=[g for g in G if g["status"] != "Not trending"],
               catalyst_days=sorted([s, d, w] for (s, d), w in CATALYST_DAYS.items()))
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
    ap.add_argument("--picks", help="setups/picks.json: the stocks you follow (the portal's Follow button)")
    a = ap.parse_args()
    global ENTRY
    ENTRY = a.entry
    A, groups, GS, cal, S = load(a.bars, a.stocks)
    daily(A, groups, GS, cal, S, a.out, news_of(a.gradelog) if a.gradelog else {}, earnings_of(a.live, cal) if a.live else {},
          picks_of(a.picks) if a.picks else {})
    if a.backtest:
        backtest(A, groups, GS, cal, S, a.backtest)


if __name__ == "__main__":
    main()
