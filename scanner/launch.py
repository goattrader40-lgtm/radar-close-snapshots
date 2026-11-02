"""Trend launches: the first day of a new trend, the group it belongs to, and the bases that follow.

Launch day (from your examples: DELL Feb 27 2026, TEAM and APPN Aug 7 2026, the cyber names Sep 14 2026, AMD 2016):
  must have   opened up (any gap), closed up 5%+ in the top half of the day's range (a power day may close lower
              if it holds half its gap: FSLR Jul 28 2022; tagged "faded", since in 2 years such days bought at the
              open with a stop under the day's low were stopped out 9 times in 10, though 13% ran 50%+), volume 1.5x+ the
              previous 20 days' average, closed above the 200 SMA, and was still near it the day before (at most
              28% above it: a neglected stock or one coming out of a correction, not a trend already running;
              your launches were -6% to +25% from it, the continuation days of MU / DELL / APPN +30% to +77%),
              and closed at least 30% above its 52-week low (your standard filter; your launches were 57-166% above).
              A power day (an episodic pivot: volume 4x+, an 8%+ gap, a 10%+ day; your Nov 1 2026 rule, was a 10%+ gap and
              a 15%+ day: ARM Mar 25 2026, a 9.9% gap, +16.4% on 6.1x; since Nov 2 2026 it must also close over its 1-month
              high, the previous 20 sessions' highest high) may start up to 50% above the 200 SMA: SMCI May 3
              2023 launched at an all-time high 32% over it
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
              still in the gap (over the day before's high) on 2x+ volume and cleared at least its 1-month base, though up less
              than 5% or not in the top half of its range (GMAB Aug 7 2026: earnings, a 5.4% gap, +4.8%). Kept
              night to night in launch.json's catalyst_days
  reversal    opened under the day before's close, closed up 8%+ in the top half of its range on 2x+ volume and over its
              1-month high (the previous 20 sessions' highest high, wicks and bodies), with the same 200 SMA, 52-week-low and liquidity rules (GDDY Oct 30 2026). Like a
              catalyst launch it comes on top of the regular ones and never blocks one
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
  laggard     a launch that closed UNDER the 200 SMA (the portal's Launch Laggards tab; your rule, Nov 2 2026): the same
              launch day otherwise (opened up, up 5%+ in the top half of the range, 30%+ over the 52-week low, liquid),
              on 2x+ volume, closing over its 1-month high (the previous 20 sessions' highest high), and only on a catalyst: earnings that day or the evening before, or company news the 8:47
              pre-market grading gave an A or B (a confirmed fundamental change). Followed like a launch (legs, buy points);
              after 5 closes in a row over the 200 SMA it moves to the launch list, marked "promoted" with that day
  theme       shown beside the grade, not in it: its group's status on the launch day, now, and the day it
              turned up. A leader launches before its theme (DELL Feb 27 2026 while semis were still
              correcting; its group led by April). "Lone wolf" = no group of it trending, then or since.
Group = each of its themes on the portal (or its industry when it has none), and one level up its area
  (AI & Semis, Software, Energy... or its sector), since a theme's leader launches before the rest of the
  theme follows (DELL led AI servers by weeks). A group or area is
  Leading     when 60%+ of its members close above their 50 EMA and its median 1-month change is +8% or more
  Turning up  when half or more close above their 21 EMA and its median 1-week change is positive
Exit signal = the first close below the 21 EMA after the launch. A launch is followed until 2 closes in a
row below the 50 EMA, 62 sessions from its highest point without a new high (your picks too), or its ADR under
3.2% (TECH 2026: 0.2% after a buyout-like gap; a launch day needs 3.5%+), with your MSF patterns (flags, pennants, triangles, flat bases,
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

L = dict(bo_adr=0, bo_rv=1, leg_adr=1.25, flag_adr_min=1.25, flag_adr_max=4, min_sessions=60, rest_days=40, power_rv=4, power_gap=8, power_chg=10, power_ext200=50, aplus_gap=6, leg_pause=5, late_leg=4, min_chg=5, min_clpos=0.5, min_rv=1.5, max_ext200=28, min_above_low52=30, rv_big=3, gap_big=3, chg_big=10, base_days=20,
         near_high=70, neglect_days=40, neglect_depth=25, follow_days=120, dedupe_days=20, ep_gap=5, watch_under200=25,
         near_gap=2, near_rv=1.2, flag_run_adr=4, flag_max_days=22, flag_relax_rv=1.3, flag_relax_drop=0.5, flag_vol_avg=1.1, try_adr=0.2, max_run_pct=0, pennant_low=0.0, flag_legs=1, flag_surf=3, flag_down_days=3, flag_days=4, caution_pct=0.5, tight_near=0.85, inner_span=20, inner_big=20, base_spans=(63, 21), retest_days=20, retest_need_ema=0, bo_decisive=0, catalyst_launch=1, cat_rv=2, reversal_launch=1, rev_rv=2, rev_chg=8, off_days=62, off_adr=3.2, s3_ready_adr=0.7, s3_min_adr=4, gob_min_adr=4, gob_min_shares=600000, gob_min_dv=30, gob_min_mcap=700, gob_rv=1, gob_rv20=2, leg_decisive=0.5, dry_max=0.85, pop_tight=0.8, tight_body=0.5, rest_body=0.5,
         lag_rv=2, lag_under200=60)
STATUS = {2: "Leading", 1: "Turning up", 0: "Not trending"}
LIQ = dict(min_price=10, min_dollar_vol_20d_millions=20, min_avg_vol_20d=600000, min_adr=3.5)   # settings.json "launch"
BASES = (120, 63, 21)  # the bases a launch can clear: 6, 3 and 1 month(s)
CATALYST_DAYS = {}     # {(symbol, date): "earnings" / the news}: the days a catalyst launch can come on
NEWS_DAYS = {}         # the same tags without the 5%-gap filter: the days a laggard launch can come on
RES_A = {}             # the loaded stocks, for the watchlist's resistance column
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
        self.liq_noadr = np.array([c[i] >= LQ["min_price"] and avgv20[i] >= LQ["min_avg_vol_20d"]
                                   and dv20[i] >= LQ["min_dollar_vol_20d_millions"] for i in range(n)])
        self.liquid = self.liq_noadr & (st.adr >= LQ["min_adr"])
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
                    and self.rv[i] >= L["cat_rv"] and self.cleared(i) >= BASES[-1] and (self.sym, st.dates[i]) in CATALYST_DAYS)

    def reversal(self, i):
        """a reversal day (your rule, Nov 1 2026, from GDDY Oct 30 2026): it opens under the day before's close, then closes
        up 8%+ in the top half of the day's range on 2x+ volume, over its 1-month high (the highest high of the previous
        20 sessions, wicks and bodies: a regular breakout, the close has to be over it)"""
        st = self.st
        return bool(L["reversal_launch"] and self.gap[i] < 0 and self.chg[i] >= L["rev_chg"] and self.clpos[i] >= L["min_clpos"]
                    and self.rv[i] >= L["rev_rv"] and st.c[i] > self.hi20[i])

    def candidate(self, i, catalyst=True):
        """the must-haves of a launch day (catalyst=False: the regular launch only, without the catalyst and reversal days)"""
        st = self.st
        return bool(i >= self.start and self.liquid[i]
                    and ((self.gap[i] > 0 and self.chg[i] >= L["min_chg"] and self.held(i))
                         or (catalyst and (self.catalyst(i) or self.reversal(i))))
                    and self.rv[i] >= L["min_rv"] and st.c[i] > self.s200[i]
                    and (self.ext200_prev[i] <= L["max_ext200"] or (self.power(i) and self.ext200_prev[i] <= L["power_ext200"]))
                    and st.c[i] >= st.low52[i] * (1 + L["min_above_low52"] / 100))

    def laggard(self, i):
        """a launch day under the 200 SMA, on 2x+ volume and a catalyst (earnings or graded company news), closing over its
        1-month high (the previous 20 sessions' highest high: your rule, Nov 2 2026)"""
        st = self.st
        return bool(i >= self.start and self.liquid[i] and self.gap[i] > 0 and self.chg[i] >= L["min_chg"] and self.held(i)
                    and self.rv[i] >= L["lag_rv"] and st.c[i] <= self.s200[i] and st.c[i] > self.hi20[i]
                    and st.c[i] >= st.low52[i] * (1 + L["min_above_low52"] / 100) and (self.sym, st.dates[i]) in NEWS_DAYS)

    def power(self, i):
        """a power day (an episodic pivot): volume 4x+, an 8%+ gap and a 10%+ day, closing over its 1-month high (the
        previous 20 sessions' highest high: your rule, Nov 2 2026)"""
        return bool(self.rv[i] >= L["power_rv"] and self.gap[i] >= L["power_gap"] and self.chg[i] >= L["power_chg"]
                    and self.st.c[i] > self.hi20[i])

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
        reversal=a.reversal(i),                                                            # opened down, closed up 8%+
    )


def flag_at(a, i):
    """a bull flag with a falling trendline (your SMCI June 2023 example): the top is at least a 1-month high (21
    sessions; a 3- or 6-month high counts too), the highest high of the last 25 sessions, 4 to 20 sessions back (the
    high and 4+ pullback days: a 5-day base, TTAN Oct 23-29 2026); the pole is the run into it (flag_run: 4+ ADRs);
    the pullback is 1.25-4 of the stock's own ADRs deep (SMCI June 2023: 21% = 3.2 ADRs) and closes stay above the
    50 EMA.
    The trendline runs from the top along the lower highs (the flattest line that keeps every high since under it).
    Returns (top index, depth %, line today, line tomorrow) or None."""
    st = a.st
    h, l, c = st.h, st.l, st.c
    if i < 50:
        return None
    t = i - 24 + int(np.argmax(h[i - 24:i + 1]))
    # 4 to 22 sessions from its top (your count, Nov 1 2026: AEHR's Mar 4 2026 top, the break Apr 2 on the 21st session)
    if not L["flag_days"] <= i - t <= L["flag_max_days"] or h[t] < h[max(0, t - 21):t].max():
        return None
    depth = 100 * (1 - l[t + 1:i + 1].min() / h[t])
    adr = st.adr[t] if st.adr[t] > 0 else 5.0
    if not L["flag_adr_min"] <= depth / adr <= L["flag_adr_max"]:
        return None
    # a flag pulls back in a controlled way: no violent drop, a gap down of 0.7+ ADR that closes 1+ ADR down on 1.3x+
    # volume, sellers with conviction (ARM Apr 27-28 2026 after its Apr 24 top: -1.3 ADR twice on 1.6x, gapping -0.7 and
    # -1.4 ADR; May 7 after the May 6 top: -1.5 ADR on 2.3x, gap -0.9 ADR: an ascending triangle, no flag. ARM Mar 27
    # gapped only -0.4 ADR: its flag Apr 13)
    if any(100 * (st.o[k] / c[k - 1] - 1) <= -0.7 * _adr(st, k) and a.chg[k] <= -_adr(st, k) and a.rv[k] >= 1.3 for k in range(t + 1, i + 1)):
        return None
    slope = flag_line(a, t, i - 1)                 # today's line: through the highs up to yesterday
    if slope >= 0:
        return None
    line = h[t] + slope * (i - t)
    # it holds its 21 EMA (no close half an ADR under it: APPN Sep 8-11 2026 fell 1.4 ADRs under it from its Aug 31
    # high, a drop and bounce, no flag; SMCI Jun 2023 -0.2, ANF Aug 2026 -0.4) and closes above the 50 EMA; unless (your
    # rule, Nov 1 2026) its falling line is intact (no close over it since the top) and the line is in the upper half of
    # the pole, its run into the top: AEHR Mar 26-30 2026 closed 1.4 ADRs under the 21 EMA and under the 50 EMA, the line
    # held, and broke at 40.65 on Apr 2, 74% up its 22.66 - 46.95 pole. The breakout says when it closed under the 50 EMA.
    # And the drop came on light volume: no day down half an ADR+ on 1.3x+ volume (AEHR's down days 0.7-1.0x; APPN Sep 4
    # 2026 -1.2 ADR on 1.4x and Sep 8 -1.8 ADR on 2.4x, LIFE Sep 16-17 -0.6 / -0.8 ADR on 2.1x / 2.3x: sellers with
    # conviction, no flag)
    if any(c[k] < a.e50[k] or 100 * (c[k] / a.e21[k] - 1) < -0.5 * _adr(st, k) for k in range(t + 1, i + 1)):
        pk = pole_of(a, t)
        if pk is None or line < st.l[pk] + 0.5 * (h[t] - st.l[pk]) or not line_intact(a, t, i) \
                or any(a.chg[k] <= -L["flag_relax_drop"] * _adr(st, k) and a.rv[k] >= L["flag_relax_rv"] for k in range(t + 1, i + 1)):
            return None
    shape = flag_shape(a, t, i)
    if not shape:
        return None
    return t, depth, line, h[t] + flag_line(a, t, i) * (i + 1 - t), shape     # tomorrow's: and today's; "bull flag" / "pennant"


def momentum_start(a, i):
    """the low the stock's current run started from (the user, Nov 1 2026): the lowest low of its last rest, 40+ sessions
    without a new 6-month high (the new-run rule); without one in the data, the lowest low of the last year. AEHR: Nov 21
    2025 (18.70); SMCI 2023: Jan 19"""
    st = a.st
    h, l = st.h, st.l
    if getattr(a, "_newhi120", None) is None:
        nh = np.zeros(h.size, dtype=bool)
        if h.size > 120:
            prev = np.lib.stride_tricks.sliding_window_view(h, 120).max(axis=1)[:-1]
            nh[120:] = h[120:] > prev
        a._newhi120 = nh
    k0 = max(120, i - 600)
    newhi = k0 + np.flatnonzero(a._newhi120[k0:i + 1])
    for x in range(newhi.size - 1, 0, -1):
        if newhi[x] - newhi[x - 1] >= L["rest_days"]:
            return int(newhi[x - 1] + np.argmin(l[newhi[x - 1]:newhi[x] + 1]))
    k0 = max(0, i - 252)
    return int(k0 + np.argmin(l[k0:i + 1]))


def flag_shape(a, t, i):
    """the consolidation from the top t to the day before i (your definitions, Nov 1 2026), or None:
    "bull flag"  a descending channel: lower highs on at least half and lower lows on more than half of the days down to
                 its low (ACN Oct 23-28 2026: 2 of 4, a pause then a V, the user's "drop and bounce": none), no higher
                 swing low after that low, and that drift down a controlled, lower-volume pullback: at or under 1.1x the
                 20-day average volume (APLD Apr 24-28 2026 0.82x, AEHR Mar 4-30 0.81x, SMCI, CAI, VEEV, ZS, TTAN, ANF
                 0.71-1.04x; not APPN Aug 31 - Sep 10 1.17x, ARM Mar 25-30 1.75x, VEEV Aug 27-31 1.62x: drops on heavy volume)
    "pennant"    converging, a symmetrical triangle: after its first low a higher swing low (any low over it: ARM Apr 7 2026, 137.58 over Mar 30's 136.00) while the
                 highs keep stepping down, the volume after that first low at or under 1.1x (ARM Mar 25 - Apr 10 2026:
                 highs Mar 25, Apr 1 down, lows Mar 30, Apr 2 / 7 up, 0.91x after Mar 30)
    Both ride the 10 or the 21 EMA (3+ days closing within an ADR of one: follow, flag_surf); the user, Nov 1 2026: it
    takes none of the agreed patterns off."""
    st = a.st
    h, l = st.h, st.l
    if i - t < 2:
        return None
    lo = t + 1 + int(np.argmin(l[t + 1:i]))

    def avg_rv(k0, k1):
        x = a.rv[k0:k1]
        x = x[np.isfinite(x)]
        return float(x.mean()) if x.size else None
    adr = _adr(st, lo)
    if any(l[x] <= l[x - 1] and l[x] <= l[x + 1] and l[x] >= l[lo] * (1 + L["pennant_low"] * adr / 100) for x in range(lo + 2, i - 1)):
        v_ = avg_rv(lo + 1, i)
        return "pennant" if v_ is not None and v_ <= L["flag_vol_avg"] else None
    drift = range(t + 1, lo + 1)
    lh = sum(1 for x in drift if h[x] < h[x - 1])
    ll = sum(1 for x in drift if l[x] < l[x - 1])
    v_ = avg_rv(t + 1, lo + 1)
    return "bull flag" if 2 * lh >= len(drift) and 2 * ll > len(drift) and v_ is not None and v_ <= L["flag_vol_avg"] else None


def line_intact(a, t, i):
    """no close over a flag's falling line from the day it can break (5 sessions after its top t, like a flag break) to
    the day before i (each day's line: through the highs up to the day before it); AEHR Mar 9 2026 closed over its 2-day
    line, before there was a flag"""
    st = a.st
    for k in range(t + L["flag_days"] + 1, i):
        s_ = flag_line(a, t, k - 1)
        if s_ is not None and st.c[k] > st.h[t] + s_ * (k - t):
            return False
    return True


def flag_line(a, t, upto):
    """slope of the falling line from the top t through the highs t+1..upto. A high a little over the line redraws it
    (ARM Apr 8 2026: 153.42, 0.2 ADR over); a try that pokes half an ADR+ over and closes back under it is a failed try
    and the line stays (ARM Apr 10: 159.29, closed 148.93 under 150.48; Apr 13 closed 157.58 over 149.00)"""
    st = a.st
    h, c = st.h, st.c
    s = None
    for k in range(t + 1, upto + 1):
        sk = (h[k] - h[t]) / (k - t)
        if s is None:
            s = sk
            continue
        line = h[t] + s * (k - t)
        if h[k] > line and not (c[k] <= line and h[k] - line > 0.5 * _adr(st, k) / 100 * line):
            s = max(s, sk)
    return s


def flag_run(a, t):
    """the run into a flag's top t: from the lowest low of the 25 sessions before it, 4+ of the stock's ADRs, and made
    by the trend, no single day 50%+ of it (CAI Aug 18 - 25 2026: 20.78 to 28.32, 5 ADRs, its biggest day a quarter of
    it; ANF's Aug 26 2026 gap day was most of its run: no flag after it, the Oct 5 pop is the entry)"""
    return pole_of(a, t) is not None


def pole_of(a, t):
    """the pole of a flag's top t (flag_run): the index of the low its run starts from, or None (AEHR's Mar 4 2026 top:
    from Feb 5's 22.66)"""
    st, c = a.st, a.st.c
    lo0 = max(1, t - 25)
    for m in range(t - 5, lo0 - 1, -1):     # an earlier high at that level with a pullback since: the pole starts after it
        if st.h[m] >= st.h[t] * (1 - 0.5 * _adr(st, t) / 100) and st.l[m + 1:t].min() <= st.h[m] * (1 - 1.25 * _adr(st, t) / 100):
            lo0 = m + 1
            break
    k = lo0 + int(np.argmin(st.l[lo0:t + 1]))
    run = st.h[t] - st.l[k]
    if k >= t or run <= 0 or 100 * run / st.l[k] < L["flag_run_adr"] * _adr(st, t):
        return None
    return k if max(c[m] - c[m - 1] for m in range(k + 1, t + 1)) <= 0.5 * run else None


def surfing(a, t, j):
    """days from t+1 to j closing within an ADR of the 10 or the 21 EMA: the flag consolidating at its EMAs, riding the
    10 EMA counts (SMCI Jun 16-27 2023, then the Jun 28 break of its line; TTAN Oct 26-29 2026 riding its 10 EMA, the 21
    EMA 5% under; ACN Oct 23-28 2026: 2 days, it fell and bounced)"""
    st, c = a.st, a.st.c
    return sum(1 for k in range(t + 1, j + 1) if min(abs(c[k] / a.e10[k] - 1), abs(c[k] / a.e21[k] - 1)) * 100 <= _adr(st, k))


def lower_highs(a, t, j):
    """days from t+1 to j making a lower high than the day before: the flag's downward move (3+ needed; TTAN Oct 26-29
    2026: 87.00, 83.92, 83.82, 81.07 under its Oct 23 high 87.75)"""
    h = a.st.h
    return sum(1 for k in range(t + 1, j + 1) if h[k] < h[k - 1])


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
    # and the closes pulled back too, or chopped sideways (2+ down closes): a one-day dip in an advance is no base
    # (GMAB Sep 23-30 2026: the closes 2% under the top at most and every one higher than the day before; Sep 30's
    # close over it was no breakout). ATRC Aug 24 - Sep 1 2026: closes 0.9 ADR under its 49.88, 4 down closes: a
    # base, broken out of Sep 2
    down = int((st.c[k + 1:j] < st.c[k:j - 1]).sum())
    if 100 * (1 - st.c[k + 1:j].min() / top) < L["leg_adr"] * _adr(st, k) and down < 2:
        return None
    return top, k


def reach(a, j, top):
    """how far back a top on day j reaches: 6, 3 or 1 month(s) (the highest high of the last 120, 63 or 21 sessions,
    leaving out the last 3), 0 if none. VEEV Oct 9 2026: 291.40 a 1-month high inside its base under 296.24, the
    6-month high (Aug 27)"""
    h = a.st.h
    for span, m in ((120, 6), (63, 3), (21, 1)):
        lo, hi = max(0, j - span), j - 3
        if hi > lo and top >= h[lo:hi].max() * 0.999:
            return m
    return 0


def top_tries(a, i, top, lo):
    """the tries of a base's top up to day i: the high itself is the 1st, then each high within 0.2 ADR of the top (CAI Oct
    16 2026 at 0.23 ADR under was no try, Oct 21 at 0.06 the 3rd)
    after a pullback of 1.25+ ADRs from it (ARM 2026: 166.69 on Mar 25 and Apr 16, the 3rd try Apr 17; 237.68-239.50 on
    Apr 24 and May 6, the 3rd May 20). Returns the days, and whether it is an ascending triangle: after the last try a
    real pullback (1.25+ ADRs), shallower than the one before it"""
    st = a.st
    h, l = st.h, st.l
    # the base of this top starts after any clearly higher high (VEEV Oct 2026: its Aug 27 high 296.24 is the bigger
    # base's, not a try of the 291.40 top)
    over = [k for k in range(lo, i + 1) if h[k] > top * (1 + 0.25 * _adr(st, k) / 100)]
    lo = over[-1] + 1 if over else lo
    tries = []
    for k in range(lo, i + 1):
        if h[k] < top * (1 - L["try_adr"] * _adr(st, k) / 100):
            continue
        if not tries or (k - tries[-1] >= 2 and l[tries[-1] + 1:k].min() <= top * (1 - 1.25 * _adr(st, k) / 100)):
            tries.append(k)
    rising = False
    if len(tries) >= 2 and i - tries[-1] >= 2:
        before, after = l[tries[-2] + 1:tries[-1]].min(), l[tries[-1] + 1:i + 1].min()
        # the lows clearly rising: the 2nd pullback's low a quarter ADR+ over the 1st's (VEEV Aug 2026: 238.93 after
        # 238.32, a falling wedge from its 253.49 top, no triangle)
        rising = bool(before * (1 + 0.25 * _adr(st, i) / 100) < after <= top * (1 - 1.25 * _adr(st, i) / 100))
    return tries, rising


def base_breakout(a, j, used=()):
    """(top, its index) of the base a close on day j breaks out of, the larger base first; a breakout = a close half an
    ADR or more over the top on 1x+ volume (a weaker close over it mostly fell back: 60-70% within 5 days; GMAB Aug 14,
    Sep 18 2026), fresh (no such close in the 3 days before, not already run an ADR past it)"""
    st, c = a.st, a.st.c
    # once launched, the 3-month and the 1-month base (63 / 21 sessions; not 6 / 2 months: the bases after a launch are
    # shorter), the larger first
    for span in L["base_spans"]:
        b = base_ok(a, j, span)
        if not b or b[1] in used:
            continue
        top, k = b
        dec = top * (1 + L["bo_decisive"] * _adr(st, j) / 100)
        # whatever the volume (ATRC Aug 7 2026 over its 41.29 base high on 0.6x; ACN Oct 16 on 0.9x): the status says
        # when it was light, the alert during the day still wants 1x+ volume for the time of day
        # inside a bigger base (a higher high in the last 3 months, 20+ sessions old) it has to be decisive, on 1x+ volume
        # (APPN Oct 9 2026 over its 1-month high 39.67, under the Aug 31 high 44.06: 0.2 ADR on 0.9x, no; VEEV Oct 9
        # over 291.40, under its Aug 27 high 296.24: 0.5 ADR on 1.2x)
        m = j - 63 + int(np.argmax(st.h[j - 63:j])) if j >= 63 else None
        inside = m is not None and st.h[m] > top * 1.001 and j - m >= L["inner_big"]
        if inside and not (c[j] > top * (1 + 0.5 * _adr(st, j) / 100) and a.rv[j] >= 1):
            continue
        if (c[j] > dec and max(c[j - 3:j]) <= dec
                and st.h[j - 3:j].max() < top * (1 + _adr(st, j - 1) / 100)):
            return b
    return inner_breakout(a, j, used)


def inner_base(a, j):
    """(top, its index) of the base inside a big base, before day j: when the stock has been in a base for a while (its
    high 20+ sessions old), the last 20 sessions' high is a level too, 2+ sessions old with a pullback after it
    (2+ down closes or 1.25 ADRs). APPN Oct 2026: under its Aug 31 high 44.06, the last 20 days' high 40.98 (Oct 12),
    Oct 13-14 pulling back tight under it; VEEV: under its Aug 27 high 296.24, 291.40 (Oct 1)"""
    st, c, h = a.st, a.st.c, a.st.h
    if j < 125:
        return None
    big = j - 120 + int(np.argmax(h[j - 120:j]))
    k = j - L["inner_span"] + int(np.argmax(h[j - L["inner_span"]:j]))
    if j - big < L["inner_big"] or k == big or j - k < 2 or h[k] >= h[big]:
        return None
    down = int((c[k + 1:j] < c[k:j - 1]).sum())
    if down < 2 and 100 * (1 - c[k + 1:j].min() / h[k]) < L["leg_adr"] * _adr(st, k):
        return None
    return h[k], k


def inner_breakout(a, j, used=()):
    """a decisive close (half an ADR+) over the inner base's high on 1x+ volume (APPN Oct 15 2026 over 40.98, 1.3 ADRs on
    1.7x; VEEV Oct 9 over 291.40 on 1.2x; APPN's Oct 9 poke, 0.2 ADR on 0.9x, no): (top, index, "inner")"""
    b = inner_base(a, j)
    if not b or b[1] in used:
        return None
    c = a.st.c
    if c[j] > b[0] * (1 + 0.5 * _adr(a.st, j) / 100) and a.rv[j] >= 1 and max(c[j - 3:j]) <= b[0]:
        return b[0], b[1], "inner"
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
    # the 50 EMA undercut (your rule, Nov 1 2026): after 2 closes in a row under the 50 EMA a launch waits in the 50 EMA
    # undercut tab; the next session has to close back over it (the reclaim: AEHR Mar 31 2026 after Mar 27 & 30), a 3rd
    # close under takes it off the list
    off50 = next((k for k in range(i0 + 3, i + 1) if all(c[m] < a.e50[m] for m in (k - 2, k - 1, k))), None)
    under50 = bool(i >= i0 + 2 and c[i] < a.e50[i] and c[i - 1] < a.e50[i - 1] and off50 is None)
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
    used_flags = set()            # a flag's line break and the later close over its top are two entries (CAI Sep 14 / 15 2026)
    # the level a retest comes back to: the broken base's top, by the candle bodies (each day the higher of its open and
    # close) or by the wicks, either one (SPOT Oct 2026: the bodies topped at $536.98 under the $540.82 wick).
    # rlv = (breakout day, bodies' top, wick top). A launch that closed out of its base broke that base too (SPOT Oct 22
    # over its October base, back to it Oct 28)
    body = lambda lo, hi: float(np.maximum(st.o[lo:hi], st.c[lo:hi]).max())
    rlv = (i0, min(body(i0 - 20, i0), st.h[i0 - 20:i0].max()), float(st.h[i0 - 20:i0].max())) \
        if i0 >= 20 and c[i0] > st.h[i0 - 20:i0].max() else None
    dry_done, dry_day, flag_day, fline = False, None, None, None        # one dry-up entry per base (ANF: Oct 5 2026, not again)
    ftop, fshape = None, None
    weak_bo, thru_day = None, None                          # a weak breakout (day, top) waiting for its follow-through
    inner_day = None                                        # the day of the last inner base breakout
    lvl = H                                                 # the level the leg broke out of: the launch day's high, then the base top
    nbo = 0                                                 # breakouts since the launch (for the grade: the 1st and 2nd work best)
    for j in range(i0 + 1, i + 1):
        if not dry_done and dry_armed(a, j - 1, H):
            lv = pop_level(a, j - 1)
            if lv and st.o[j] > lv:
                dry_done, dry_day = True, j
        f = flag_at(a, j)               # after any recent high, not only a new high of the run (each flag top once)
        # a flag at the highs, after the leg has run 4+ of the stock's own ADRs from its start (SMCI Jun 2023: 85%,
        # 13 ADRs, then the flag); a trendline break in the base right after a launch is an entry, not a new leg
        # (ANF Sep 16 2026: 5% past its Aug 26 launch close; Oct 5, after the volume dried up, your entry in the base)
        # a flag after a recent high, at the top of a base or inside a bigger one (TTAN Oct 2026 under its Aug 28 high
        # 102.95), wedging down: 3+ lower highs, after a run made by the trend
        at_highs = bool(f and flag_run(a, f[0]) and lower_highs(a, f[0], j - 1) >= L["flag_down_days"])
        # the flag buy: the high and 4+ pullback days (a 5-day base), consolidating at the 10 / 21 EMA (3+ days surfing
        # them), then the close over its falling line and the 10 & 21 EMA (SMCI Jun 28 2023; TTAN Oct 30 2026 after its
        # Oct 23 high). An entry inside the base, not a new leg: the leg comes with the close over the base top (CAI
        # Sep 14 2026 the flag, Sep 15 the base breakout). Without the surfing it is no flag (ACN Oct 29 2026, a drop
        # and bounce under its Oct 22 high 259.39)
        flag_go = bool(L["flag_legs"] and f and at_highs and f[0] not in used_flags and j - f[0] > L["flag_days"] and c[j] > f[2] and c[j - 1] <= (flag_at(a, j - 1) or (0, 0, np.inf))[2]
                       and surfing(a, f[0], j - 1) >= L["flag_surf"] and c[j] > a.e10[j] and c[j] > a.e21[j])
        b = base_breakout(a, j, used)
        if b and bo and j - bo[0] < L["leg_pause"] and (c[bo[0]:j] >= bo[1]).all():
            used.add(b[1])               # continuation of that breakout, no new one (ATRC Jul 28 2026 over its Feb high
            b = None                     # 38.32 the day after Jul 27's breakout of 36.33: the retest level stays 36.33)
        # the follow-through of a caution breakout (closed within 0.5% over the top), within 3 sessions: it opens over
        # the day before's close and closes more than 0.5% over the top, the low may dip back under it: the new leg
        # starts here (ARM Apr 17 2026 closed 166.73 over 166.69; Apr 20 opened 167.41, low 164.10, closed 175.10: leg 2.
        # GMAB Aug 14 2026 -> Aug 17; ATRC Aug 7 -> Aug 11. GMAB's Sep 18 got none: Sep 22 closed 1.7% over but opened
        # under the day before's close; still inside its 34.7 range until Oct 5)
        if weak_bo and not b and j - weak_bo[0] <= 3 and st.o[j] > c[j - 1] \
                and c[j] > weak_bo[1] * (1 + L["caution_pct"] / 100):
            if leg == 0 or j - last_leg >= L["leg_pause"]:
                leg = 1 if j - last_new >= L["rest_days"] else leg + 1
                last_leg, armed, thru_day = j, False, j
            weak_bo = None
        if flag_go:                                       # an entry in the base: the leg and its level stay
            flag_day, fline, ftop, fshape = j, f[2], f[0], f[4]
            used_flags.add(f[0])
        if b:
            nbo += 1
            used.add(b[1])                                # each base top gives at most one breakout
            inner_day = j if len(b) > 2 else inner_day
            b = b[:2]
            bo, lvl = (j, b[0], b[1]), b[0]
            rlv = (j, min(body(max(0, b[1] - 20), max(b[1] + 1, j - 3)), b[0]), float(b[0]))   # the base's bodies, not the push into it
            # a close more than 0.5% over the top is a breakout and a new leg; within 0.5% (but over it) a breakout with
            # caution, still the same leg until it follows through (GMAB 2026: Aug 14 0.47%, Sep 18 0.23%; ARM Apr 17
            # 0.02%; CAI Oct 27 2.4%: a breakout, leg 4)
            weak = bool(c[j] <= b[0] * (1 + L["caution_pct"] / 100))
            # its follow-through starts the leg (a leg runs from a breakout through the run and the pullback until the
            # next breakout: GMAB 2026 Aug 14 over the launch day's high, Oct 5 out of the 34.7 range, Oct 23)
            weak_bo = (j, b[0]) if weak else None
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
    flag_leg = bool(fl and flag_run(a, fl[0]) and lower_highs(a, fl[0], i) >= L["flag_down_days"])
    if not flag_leg or not L["flag_legs"] or surfing(a, fl[0], i) < L["flag_surf"]:
        fl = None
    flag_bo = flag_day == i
    # tomorrow's base tops (the smaller and the larger base): buy points when above today's close
    tops = [b for b in (base_ok(a, i + 1, sp) for sp in L["base_spans"]) if b and c[i] < b[0]]
    if len(tops) == 2 and max(tops)[0] <= min(tops)[0] * (1 + 0.5 * _adr(st, i) / 100):
        tops = [max(tops)]          # two highs within half an ADR are one level, the higher (CAI Oct 2026: 32.77 / 32.89)
    # the buy point = the nearest trigger above today's close: your MSF pattern's pivot, the flag's trendline or
    # the base top (RPD Oct 23 2026 had closed just over its MSF pivot of 14.80; the base top trigger 15.02 is what
    # Oct 26 broke on 3.3x volume)
    cands = []
    nb = min(t for t, k in tops) if tops else None     # the nearest base high over the close
    # a pattern's pivot inside the base (under its high) is no buy point: the breakout is of the base high (ATRC Aug 4-5
    # 2026: its "Tight flag" pivot 39.83 under the Jul 29 base high 41.29, broken Aug 7)
    if code and msf.is_pat(code) and r.pivot == r.pivot and c[i] < r.pivot and (nb is None or r.pivot >= nb * (1 - _adr(st, i) / 400)):
        cands.append((float(r.pivot), msf.NAMES[code], r.cN, r.cDep))        # that's only a recent high (ANF Oct 26 2026)
    # until it breaks, then the base top is next (ARM Apr 13 2026 closed 5.8% over its line). A break within 0.5% over
    # the line (caution, like a base breakout) keeps the line as the next trigger, then the base top (TTAN Oct 30 2026
    # closed 84.26 over 84.00: 84.28 next, then 87.75)
    flag_caution = bool(fl and fl[2] < c[i] <= fl[2] * (1 + L["caution_pct"] / 100))
    if fl and (fl[0] not in used_flags or (flag_day == i and flag_caution)) and c[i] < fl[3] and (c[i] <= fl[2] or flag_caution):
        cands.append((fl[3], ("Bull pennant" if fl[4] == "pennant" else "Bull flag") + " (trendline)", i - fl[0], fl[1]))
    if not dry_done and dry_armed(a, i, H) and pop_level(a, i):
        cands.append((float(pop_level(a, i)), "Pop out of the consolidation (in base)", i - last_new, 100 * (1 - st.l[last_new:i + 1].min() / H)))
    for top, k in tops:
        cands.append((top, "Base top", below_since(a, i + 1, top, k), 100 * (1 - st.l[k:i + 1].min() / top)))
    ib = inner_base(a, i + 1)
    if ib and c[i] < ib[0]:             # the inner base's high (APPN Oct 14 2026 night: 40.98 under its Aug 31 high 44.06)
        cands.append((ib[0], "Inner base (last 20 days)", i + 1 - ib[1], 100 * (1 - st.l[ib[1]:i + 1].min() / ib[0])))
    bp, pat, bdays, bdep = min(cands) if cands else (None, msf.NAMES[code] if code else "", r.cN if code else None, r.cDep if code else None)
    top_date = next((st.dates[k] for t, k in tops if bp is not None and t == bp), None)
    # gap out of base (your rule, Nov 1 2026; Zanger / Qullamaggie): the nearest base high over the close, the base top or a
    # pattern's pivot, not a flag line or a pop; an open above it tomorrow is a gap out of the base (radar/alerts.py)
    gb = min((x for x in cands if not x[1].startswith(("Flag", "Bull flag", "Bull pennant", "Pennant", "Pop"))), default=None)
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
        # held: over the bodies' top and the 21 EMA, and over the 10 EMA unless the low tested the 21 EMA and the close
        # reclaimed it (ARM Mar 30 2026 closed at its low under the 10 EMA, the 21 EMA 2.6% lower: no; Apr 7 down to
        # 137.58 under the 21 EMA 138.84, closed 143.86: the retest + 21 EMA; Mar 31 over the 10 EMA: a retest too)
        ok = touch_on(k) and c[k] > rlv[1] and c[k] > a.e21[k] \
            and (c[k] > a.e10[k] or st.l[k] <= a.e21[k] * (1 + ak / 400))
        conf = [n for n, e in (("10 EMA", a.e10), ("21 EMA", a.e21), ("50 EMA", a.e50))
                if ok and rlv[1] * (1 - ak / 100) <= e[k] <= rlv[2] * (1 + ak / 100) and st.l[k] <= e[k] * (1 + ak / 400) and c[k] > e[k]]
        return ok, conf
    held = bool(rlv and 1 <= i - rlv[0] <= L["retest_days"] and not (c[rlv[0] + 1:i + 1] < rlv[1] * (1 - adr / 100)).any())
    hit = lambda k: bool(retest_on(k)[1]) if L["retest_need_ema"] else retest_on(k)[0]
    first = next((k for k in range(rlv[0] + 1, i + 1) if touch_on(k)), None) if rlv else None     # the first touch
    # the retest's day: the pullback's new low reclaimed (GMAB Oct 2), or testing the level while every close since the
    # first touch held over the 21 EMA (ACN Oct 5-7 2026 at its old base top 195.00-197.63, closes over the 21 EMA
    # 187-188: Oct 7 closed 196.64 back over 195.00, the buy at the close; ANF Aug 17-18 closed under it: no retest)
    rday = lambda k: bool(hit(k) and (st.l[k] <= st.l[rlv[0] + 1:k].min()
                                      or (first is not None and first <= k and (c[first:k + 1] > a.e21[first:k + 1]).all())))
    rdays = [k for k in range(rlv[0] + 1, i + 1) if rday(k)] if rlv else []
    done = rdays[0] if rdays else None
    # one per breakout, unless a later one undercuts the earlier's low and reclaims again (CAI 2026: Sep 3 at 23.62, then
    # Sep 10 down to 23.20 under the 23.66 base high and the 21 EMA, closed back over both)
    retest = bool(held and rdays and rdays[-1] == i and all(st.l[i] < st.l[k] for k in rdays[:-1]))
    retest_ema = retest_on(i)[1] if retest else []

    # the two 21 EMA entries in the base, once per pullback (none after a retest of the breakout level in it)
    def ema_back(k):
        """the day trades down through the 21 EMA (the low under it and under the open) and closes back over it in the
        upper half of its range, over the 50 EMA, in the base (pulled back 1.25+ ADRs from its high, under it).
        "retest": the closes since the high held over it (a quarter ADR) and the 3 days before were no advance (a
        controlled pullback into it: VEEV Sep 15 2026 gapped down after 3 up days, no; Sep 21 yes; TTAN Oct 29, NTSK Oct 1,
        ARM May 18). "undercut": the 2 days before closed under it, within half an ADR (momentum traders out after 2
        closes under, a shakeout: SMCI Jun 23 & 26 2023, Jun 27 undercut & reclaim, Jun 28 its flag; APPN Sep 8-11 2026
        closed 1.3 ADRs under: a breakdown, no)"""
        ak, top = _adr(st, k), st.h[i0:k].max()
        if not (st.l[k] < a.e21[k] and st.l[k] < st.o[k] and c[k] > a.e21[k] and c[k] > a.e50[k] and c[k] < top
                and c[k] - st.l[k] >= 0.5 * (st.h[k] - st.l[k]) and st.l[last_new:k + 1].min() <= top * (1 - 1.25 * ak / 100)):
            return None
        if all(a.e21[m] * (1 - ak / 200) <= c[m] < a.e21[m] for m in (k - 2, k - 1)):
            return "undercut"
        if (c[last_new:k] >= a.e21[last_new:k] * (1 - ak / 400)).all() and not all(c[m] > c[m - 1] for m in (k - 3, k - 2, k - 1)):
            return "retest"
        return None
    reclaim = ema_back(i) if i - last_new >= 4 and not any(k > last_new for k in rdays) and not any(ema_back(k) for k in range(last_new + 4, i)) else None
    # the breakout undercut & reclaim (the user's name; CAI Oct 9 2026): after a breakout, 2+ closes back under its level (the broken base's top,
    # its bodies: Oct 6 closed 27.45 under 28.01), the closes since holding over the 50 EMA (Oct 7-8, tight), then the close
    # back over the level (Oct 9, 29.70): an entry, within 5 sessions of the first close under it, once per breakout. One
    # close under and back is a retest held (GMAB Oct 2, ACN Oct 7 2026). Only after the stock first closed 1.25+ ADRs over
    # the level (not AEHR Feb 20 2026: its Feb 11 breakout fell right back)
    def under_since(k_):
        if not rlv or k_ <= rlv[0] or c[k_] >= rlv[1]:
            return None
        m = k_
        while m - 1 > rlv[0] and c[m - 1] < rlv[1]:
            m -= 1
        return m

    def bo_reclaim(k_):
        m = under_since(k_ - 1)
        return bool(m is not None and 2 <= k_ - m <= 5 and c[k_] > rlv[1] and all(c[x] > a.e50[x] for x in range(m, k_ + 1))
                    and c[rlv[0] + 1:m].max(initial=0) >= rlv[1] * (1 + 1.25 * _adr(st, m) / 100))   # it advanced first
    reclaim_bo = bool(rlv and bo_reclaim(i) and not any(bo_reclaim(x) for x in range(rlv[0] + 2, i)))
    m_bo = under_since(i - 1) if reclaim_bo else None
    m_now = under_since(i)
    # tomorrow's: under the level now (within 5 sessions), holding over the 50 EMA, no reclaim of this breakout yet
    # (tomorrow's reclaim needs 2+ closes under by then: today at least the 2nd; the stock advanced first; within 5 sessions)
    reclaim_level = rlv[1] if (m_now is not None and 1 <= i - m_now <= 4 and all(c[x] > a.e50[x] for x in range(m_now, i + 1))
                               and c[rlv[0] + 1:m_now].max(initial=0) >= rlv[1] * (1 + 1.25 * _adr(st, m_now) / 100)
                               and not any(bo_reclaim(x) for x in range(rlv[0] + 2, i + 1))) else None
    # the 50 EMA undercut & reclaim (an entry, like the 21 EMA one): the 2 closes before under the 50 EMA (no depth limit,
    # your OK Nov 1 2026), today the low under it and under the open, the close back over it in the upper half of the day,
    # in the base (AEHR Mar 31 2026: Mar 27 & 30 under 33.79 / 33.64, down to 33.00, closed 37.08 over 33.78)
    reclaim50 = bool(i >= i0 + 3 and c[i - 2] < a.e50[i - 2] and c[i - 1] < a.e50[i - 1] and st.l[i] < a.e50[i] and st.l[i] < st.o[i]
                     and c[i] > a.e50[i] and c[i] - st.l[i] >= 0.5 * (st.h[i] - st.l[i]) and c[i] < st.h[i0:i].max())
    # tomorrow's 21 EMA setup (radar/alerts.py: the heads-up when it trades down to the 21 EMA, the alert from 3:45 PM
    # when it holds back over it): "undercut" after 2 closes under it (today and yesterday, within half an ADR), "retest"
    # while the closes held over it after a pullback that was no advance
    ema21_watch = None
    if i - last_new >= 3 and not any(k > last_new for k in rdays) and not any(ema_back(k) for k in range(last_new + 4, i + 1)) \
            and c[i] < st.h[i0:i + 1].max() and c[i] > a.e50[i]:
        if all(a.e21[m] * (1 - adr / 200) <= c[m] < a.e21[m] for m in (i - 1, i)):
            ema21_watch = "undercut"
        elif (c[last_new:i + 1] >= a.e21[last_new:i + 1] * (1 - adr / 400)).all() and not all(c[m] > c[m - 1] for m in (i - 2, i - 1, i)) \
                and c[i] <= a.e21[i] * (1 + 1.5 * adr / 100):
            ema21_watch = "retest"
    # tomorrow's zone, for the heads-up during the day (the buy alert itself waits for the close): until a retest held
    zone = [fnum(rlv[1] * (1 - 1.5 * adr / 100)), fnum(max(rlv[2], rlv[1] * (1 + adr / 400)))] \
        if held and 2 <= i - rlv[0] < L["retest_days"] else None
    # the push out of the 10 / 21 EMA with a gap, within 5 sessions of the retest's first touch, held or not: the day
    # before still at the EMAs (closing within an ADR of the 10 EMA, over the 50 EMA), it opens over that day's candle
    # (its open and close) and closes over the trigger, the highest of that candle, the 10 and 21 EMA and the breakout
    # level (the wick top: both reclaimed), on 1x+ volume. Once per breakout. ANF Aug 21 2026 after touching 105.16 on
    # Aug 17 (trigger 107.04, its 10 EMA); ACN Oct 8 after Oct 6 (trigger 197.63, the old base top, 1.7x volume);
    # GMAB Oct 5 after Oct 2
    push_lv = lambda k: max(st.o[k], c[k], a.e10[k], a.e21[k], rlv[2])

    def under_flag(k, tomorrow=False):
        f_ = flag_at(a, k)
        if not (f_ and flag_run(a, f_[0]) and lower_highs(a, f_[0], k - 1) >= L["flag_down_days"] and surfing(a, f_[0], k - 1) >= L["flag_surf"]):
            return False
        return f_[3] > push_lv(k) if tomorrow else c[k] <= f_[2]
    push_armed = lambda k: bool(held and first is not None and first <= k <= first + 5 and abs(c[k] / a.e10[k] - 1) * 100 <= _adr(st, k)
                                and c[k] > a.e50[k])
    push_day = next((j for j in range(first + 1, min(i, first + 6) + 1) if push_armed(j - 1) and not under_flag(j) and st.o[j] > max(st.o[j - 1], c[j - 1])
                     and c[j] > push_lv(j - 1)), None) if first is not None else None     # whatever the volume (CAI Oct 9 2026, 0.98x)
    push_level = push_lv(i) if push_armed(i) and push_day is None and not under_flag(i, True) else None     # what tomorrow's open has to clear
    # tight under the buy point (a level: a base top or a pattern's pivot, not a falling flag line): closes within an
    # ADR under it, 2+ tight days in a row: tight bodies (half an ADR or less) close to the base high, whatever the
    # wicks (ANF Oct 15-16 2026: 2.1% and 1.3% under its 155.22 base top, bodies 0.00 and 0.05 ADR; broke out Oct 19),
    # the day's move under half an ADR
    tight = 0
    tlv = nb or (bp if bp and pat in tuple(msf.NAMES[k] for k in range(1, 13) if msf.is_pat(k)) else None)
    if tlv:                          # under the base high (ATRC Aug 4-5 2026: 5% under 41.29, no tight days)
        for k in range(i, max(i0, i - 10), -1):
            if not (tlv * (1 - L["tight_near"] * _adr(st, k) / 100) <= c[k] < tlv and abs(a.chg[k]) <= _adr(st, k) / 2
                    and abs(c[k] - st.o[k]) <= L["tight_body"] * _adr(st, k) / 100 * c[k - 1]
                    # stacked, not stepping: all the days' opens and closes within half an ADR (ANF Oct 15-16 2026:
                    # 0.24 ADR, ACN Oct 5-7 0.44, SG Oct 5-7 0.46; GMAB Sep 17-21 0.96 and Oct 20-22 1.02: no tight days)
                    and max(c[k:i + 1].max(), st.o[k:i + 1].max()) - min(c[k:i + 1].min(), st.o[k:i + 1].min()) <= _adr(st, i) / 200 * c[i]):
                break
            tight += 1
    # advancing is not tight: every one of those days a higher high, higher low and higher close than the day before
    # (GMAB Oct 20-22 2026, a staircase into $40.17; ANF Oct 16 made a lower high, so Oct 15-16 was tight)
    # and not drifting down: the last close at most 0.1 ADR under the first (VEEV Aug 20-25 2026, a falling wedge)
    if tight >= 2 and 100 * (c[i] / c[i - tight + 1] - 1) < -0.1 * _adr(st, i):
        tight = 0
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
    if blen is not None and blen < L["leg_pause"]:
        tight = 0                    # under a high set a few sessions ago there is no base yet (GMAB Sep 21 2026: 1 session)
    msf_pat = msf.NAMES[code] if code and msf.is_pat(code) else None
    # the stock's stage after the close, the first that applies
    rest = 0
    while i - rest > i0 and resting(a, i - rest):
        rest += 1
    since = None
    bday = None                       # the base's day as the status counts it, from the day of its high
    if i == i0 and not pick:
        cb = {120: "6-month", 63: "3-month", 21: "1-month"}.get(a.cleared(i))
        stage = "Launch day" + (f", cleared its {cb} base" if cb else "")
    elif bo and bo[0] == i and inner_day == i:
        ov = (c[i] / bo[1] - 1) * 100 / _adr(st, i)
        stage = f"Breakout of the inner base (leg {leg}), the last 20 days' high {bo[1]:.2f}, closed {ov:.1f} ADR over it" \
            + (f", on light volume ({a.rv[i]:.2f}x)" if a.rv[i] < 1 else "")
    elif bo and bo[0] == i:
        # how far it closed over the top, in % and in its ADR; within 0.5% a breakout with caution, the next leg only
        # when it follows through (ATRC Aug 7 2026 0.24%, leg 2 from Aug 11; ARM Apr 17 0.02%, leg 2 from Apr 20)
        ov = (c[i] / bo[1] - 1) * 100 / _adr(st, i)
        pc = 100 * (c[i] / bo[1] - 1)
        rm = reach(a, i, bo[1])
        hi_txt = f"the base high {bo[1]:.2f}" + (f" (a {rm}-month high)" if rm else "")
        stage = (f"Base breakout (leg {leg}), closed {pc:.1f}% ({ov:.1f} ADR) over {hi_txt}" if pc > L["caution_pct"] else
                 f"Base breakout with caution ({f'leg {leg + 1} if it follows through' if leg == 0 or i - last_leg >= L['leg_pause'] else f'leg {leg}'}): "
                 f"closed {pc:.2f}% over {hi_txt}, within {L['caution_pct']}%: not decisive") \
            + (f", on light volume ({a.rv[i]:.2f}x)" if a.rv[i] < 1 else "")
        kb, dbl = bo[2], False
        if i - kb >= 6 and kb not in used_flags:
            # the double breakout: squeezing under a falling line from the base top (the line through its highs, no close
            # over it yet; a flag breakout from that top broke it already: ARM Apr 13 2026, so Apr 17 is no double) with
            # higher lows, the line and the top broken the same day. The days before stayed under the top (GMAB Oct 22
            # 2026 was already at its 40.17 top, the right side of a U: no squeeze). ARM May 20 2026 (from its May 6 high
            # 239.50), ATRC Aug 7 (Jul 29 41.29), CAI Oct 27 (Sep 23 32.89), VEEV Oct 9 (Oct 1 291.40)
            sl = max((st.h[k] - st.h[kb]) / (k - kb) for k in range(kb + 1, i))
            mid = kb + (i - kb) // 2
            if sl < 0 and all(c[k] <= st.h[kb] + sl * (k - kb) for k in range(kb + 1, i)) \
                    and st.h[i - 3:i].max() <= st.h[kb] * (1 - 0.1 * _adr(st, i) / 100) and st.l[mid:i].min() > st.l[kb + 1:mid].min():
                dbl = True
                stage += (f" · double breakout: also out of the falling line from its {st.dates[kb]} high {st.h[kb]:.2f}, squeezing with higher lows"
                          + (f", gapped up {100 * (st.o[i] / c[i - 1] - 1):.1f}%" if st.o[i] > c[i - 1] else ""))
        # the main base's high right above (VEEV Oct 9 2026: a double breakout, out of its 1-month base 291.40 and the
        # falling line from Oct 1; it traded through its 6-month high 296.24 of Aug 27 to 297.45 but closed 296.13 under
        # it: not out of the main base yet, a close over it would have made it a triple breakout)
        mt, mk = base_top(a, i, 120)
        if mt and mt > bo[1] * 1.001 and mt * (1 - 0.5 * _adr(st, i) / 100) <= c[i] <= mt * (1 + L["caution_pct"] / 100):
            mn = f"the {reach(a, i, mt) or 6}-month high {mt:.2f} ({st.dates[i - mk]})"
            if c[i] <= mt:
                stage += (f"; {mn} right above: traded to {st.h[i]:.2f} but closed {c[i]:.2f} under it, not out of it yet ("
                          + ("a close over it makes it a triple breakout)" if dbl else "a close over it is the main base's breakout)")
                          if st.h[i] > mt else f"; {mn} right above: closed {c[i]:.2f} under it, not out of it yet")
            else:
                stage += (f"; {'a triple breakout: ' if dbl else ''}also over {mn}, closed {100 * (c[i] / mt - 1):.2f}% over it, "
                          f"within {L['caution_pct']}%: caution")
        tr, up = top_tries(a, i - 1, bo[1], max(i0, i - 60))
        if len(tr) == 2 and up:
            stage += f" · the 3rd try of the top: an ascending triangle (tried {st.dates[tr[0]]} and {st.dates[tr[1]]}, the 2nd pullback shallower)"
    elif thru_day == i:
        stage = f"Breakout follow-through (leg {leg}): opened over the day before's close" \
            + (f" and held over {bo[1]:.2f} all day" if st.l[i] > bo[1] else "") \
            + f", closed {100 * (c[i] / bo[1] - 1):.1f}% ({(c[i] / bo[1] - 1) * 100 / _adr(st, i):.1f} ADR) over {bo[1]:.2f}"
    elif flag_bo:
        fname = "Bull pennant" if fshape == "pennant" else "Bull flag"
        stage = (f"{fname} breakout: closed over its falling line {fline:.2f} and the 10 & 21 EMA, an entry in the base (leg {leg})"
                 if c[i] > fline * (1 + L["caution_pct"] / 100) else
                 f"{fname} breakout with caution: closed {100 * (c[i] / fline - 1):.2f}% over its falling line {fline:.2f}, within "
                 f"{L['caution_pct']}%, and over the 10 & 21 EMA, an entry in the base (leg {leg}): the line is the next trigger again") \
            + (f", the volume dried up the 2 days before ({a.rv[i - 2]:.2f}x, {a.rv[i - 1]:.2f}x)" if max(a.rv[i - 2], a.rv[i - 1]) < 1 else "") \
            + ((" · closed under the 50 EMA during the flag (" + ", ".join(st.dates[k] for k in u50) + "): you judge the grade")
               if (u50 := [k for k in range(ftop + 1, i) if c[k] < a.e50[k]]) else "")
    elif dry_day == i:
        stage = "Pop out of the consolidation (entry in base)"
    elif reclaim_bo:
        stage = (f"Breakout undercut & reclaim (entry): {i - m_bo} closes under the breakout level {rlv[1]:.2f} since {st.dates[m_bo]}, "
                 f"holding over the 50 EMA, closed {c[i]:.2f} back over it")
    elif push_day == i:
        stage = f"Push out of the 21 EMA with a gap, after the retest of {rlv[1]:.2f}" + (f"-{rlv[2]:.2f}" if rlv[2] > rlv[1] * 1.001 else "") \
            + (f", on light volume ({a.rv[i]:.2f}x)" if a.rv[i] < 1 else "")
    elif retest:
        lv_txt = f"{rlv[1]:.2f}" if rlv[2] <= rlv[1] * 1.001 else f"{rlv[1]:.2f}-{rlv[2]:.2f} (bodies-wicks)"
        stage = f"Retest of the breakout level {lv_txt} held" + (" + confluence: " + " & ".join(retest_ema) if retest_ema else "")
    elif reclaim50:
        stage = (f"50 EMA undercut & reclaim (entry): 2 closes under the 50 EMA ({st.dates[i - 2]}, {st.dates[i - 1]}), today down to "
                 f"{st.l[i]:.2f}, closed {c[i]:.2f} back over {a.e50[i]:.2f} in the upper half of the day")
    elif reclaim:
        stage = (f"21 EMA retest in the base (entry): dipped to {st.l[i]:.2f} under the 21 EMA {a.e21[i]:.2f}, closed {c[i]:.2f} back over it"
                 if reclaim == "retest" else
                 f"21 EMA undercut & reclaim (entry, strong): 2 closes under the 21 EMA, today down to {st.l[i]:.2f}, closed {c[i]:.2f} back over {a.e21[i]:.2f}")
    elif tight >= 2:
        stage = f"Tight under {tlv:.2f}, the base high ({tight} days)" + (
            f" · base {blen} sessions, {bdeep:.0f}% deep ({bdeep_adr:.1f} ADRs)" + (f", {msf_pat}" if msf_pat else "") if blen else "")
    elif rest >= 3:
        since = st.dates[i - rest + 1]
        stage = f"Consolidation, surfing the 10 & 21 EMA on dry volume ({rest} days)" + (f", {100 * (1 - c[i] / H):.0f}% under the top {H:.2f}" if c[i] < H * 0.99 else "")
    elif c[i] < a.e21[i]:
        stage = "Below the 21 EMA"
    elif tops:
        # a base formed under a new high: it starts the day of that high (ACN: its Oct 22 2026 high 259.39, pulled back),
        # whatever buy point is nearer (ATRC Oct 5 2026: the flag line 58.66 under its Sep 24 top 61.70)
        tb, kt = min(tops)
        bday = i - kt + 1
        stage = f"In the base, day {bday}, {100 * (1 - c[i] / tb):.0f}% under the top {tb:.2f} (set {st.dates[kt]})"
    elif c[i] > lvl and c[i] >= H * (1 - 1.25 * adr / 100):     # closing above what the leg broke out of (ANF: never over
        stage = f"Running (leg {leg}), {100 * (c[i] / lvl - 1):.0f}% over {lvl:.2f}"   # the Aug 26 high until Oct 19)
    else:
        bday = i - last_new + 1
        stage = f"In the base, day {bday}, {100 * (1 - c[i] / H):.0f}% under the top {H:.2f}"   # from the day of that high
    tries_txt, ntries = None, 0
    if tops and not (bo and bo[0] == i):
        tb, kt = min(tops)
        tr, up = top_tries(a, i, tb, max(i0, i - 60))
        if len(tr) >= 2 and up:
            ntries = len(tr)
            nth = {2: "3rd", 3: "4th"}.get(len(tr), f"{len(tr) + 1}th")
            tries_txt = (f"{len(tr)} tries of the top {tb:.2f} ({', '.join([st.dates[kt]] + [st.dates[k] for k in tr[1:]])}), the last pullback shallower: "
                         f"an ascending triangle, the {nth} try usually breaks out")
            if stage.startswith(("In the base", "Tight", "Consolidation")):
                stage += " · " + tries_txt
        else:
            # the try day's own read, of the main base's top only (the user: RPD Oct 8 2026 tried its 13.25 1-month top right
            # under the 13.87 main base, resistance: no 3rd try; CAI Oct 21 the 3rd try of its 32.89 main top)
            tm, km = max(tops)
            trm, _ = top_tries(a, i, tm, max(i0, i - 60)) if (tm, km) != (tb, kt) else (tr, up)
            if len(trm) >= 3 and trm[-1] == i and stage.startswith(("In the base", "Tight", "Consolidation")):
                ntries = len(trm)
                nth = {3: "3rd", 4: "4th"}.get(len(trm), f"{len(trm)}th")
                tries_txt = f"the {nth} try of the top {tm:.2f} today (tried {', '.join([st.dates[km]] + [st.dates[k] for k in trm[1:-1]])}): a heads-up"
                stage += " · " + tries_txt
            elif (tm, km) != (tb, kt) and len(tr) >= 3 and tr[-1] == i and stage.startswith(("In the base", "Tight", "Consolidation")):
                # a smaller base's top tried under the main base (the user: RPD Oct 8 2026, the 3rd try of its 13.25 1-month
                # top, the 13.87 main base right above it)
                ntries = len(tr)
                nth = {3: "3rd", 4: "4th"}.get(len(tr), f"{len(tr)}th")
                rm_ = reach(a, i, tb)
                # the main base's top: the highest level between the bigger base's top and this one, its latest touch (RPD:
                # 13.90 Aug 14 / 13.87 Aug 27, a double top: Aug 27; the bigger base's 14.80 of Aug 11)
                hl_ = st.h[km + 1:kt].max() if kt - km > 1 else 0
                kmid = next((k for k in range(kt - 1, km, -1) if st.h[k] >= hl_ * (1 - 0.15 * _adr(st, k) / 100) and st.h[k] >= st.h[k - 1]
                             and st.h[k] >= st.h[k + 1]), None) if hl_ > tb else None
                above = (f"the main base's top {st.h[kmid]:.2f} ({st.dates[kmid]}) and the bigger base's {tm:.2f} ({st.dates[km]}) above"
                         if kmid is not None and tb < st.h[kmid] < tm else f"the main base's top {tm:.2f} ({st.dates[km]}) above")
                tries_txt = (f"the {nth} try of its {str(rm_) + '-month' if rm_ else 'smaller'} base's top {tb:.2f} today (tried "
                             f"{', '.join([st.dates[kt]] + [st.dates[k] for k in tr[1:-1]])}), {above}: a heads-up")
                stage += " · " + tries_txt
    if reclaim_level:
        stage += (f" · under its breakout level {rlv[1]:.2f} since {st.dates[m_now]} ({i - m_now + 1} closes), holding over the 50 EMA: "
                  f"a breakout undercut & reclaim setup, the buy is a close back over it")
    elif m_now is not None and i - m_now <= 4:
        # before the setup (the user, Nov 1 2026: the status should say it): the 1st close back under the level after an
        # advance (CAI Oct 6 2026), or back under it without having advanced (W Oct 30 2026, AEHR Feb 12: the base stays valid)
        if c[rlv[0] + 1:m_now].max(initial=0) < rlv[1] * (1 + 1.25 * _adr(st, m_now) / 100):
            stage += f" · back under its breakout level {rlv[1]:.2f}: the breakout didn't advance, the base is still valid"
        elif i == m_now and c[i] > a.e50[i]:
            stage += (f" · closed back under its breakout level {rlv[1]:.2f} (1st close): a 2nd close under, holding over the 50 EMA, "
                      f"sets up a breakout undercut & reclaim")
    out = dict(
        stage=stage, stage_since=since, msf_pattern=msf_pat, breakouts=nbo, top_tries=ntries, top_tries_note=tries_txt,
        ema21_today=reclaim, ema21_watch=ema21_watch,
        breakout_caution=bool(bo and bo[0] == i and c[i] <= bo[1] * (1 + L["caution_pct"] / 100)),
        double_breakout="double breakout" in stage, flag_dry="volume dried up" in stage,
        # the base forming now, as your MSF engine names it (High tight flag, Bull flag, Pennant, Ascending triangle,
        # Flat base, Cup with handle, ... or Base forming (no pattern yet))
        base_pattern=msf.NAMES[code] if code else None,
        # the day of the base: sessions since the launch or the leg's breakout (ANF: Aug 26 = day 0, Sep 10 day 10,
        # Sep 24 day 20; Oct 19, leg 2, day 0 again), and whether today it turned up: back over a rising 10 EMA after
        # closing under it (ANF Oct 1, day 25)
        # in a base: the same day the status names (TTAN, your pick from Oct 30 2026: day 6 of the base under its Oct 23
        # top 87.75, not day 0 of the follow); otherwise sessions since the leg's breakout, as before
        base_day=bday if bday is not None else i - last_leg,
        turned_up=bool(i > last_leg and c[i] > a.e10[i] > a.e10[i - 1] and not (c[i - 1] > a.e10[i - 1] > a.e10[i - 2])),
        vol_build=fnum(st.v[i - 4:i + 1].mean() / st.v[i - 54:i - 4].mean(), 2) if i >= 54 else None,
        base_from=bfrom, base_len=blen, base_low_pct=fnum(bdeep, 1) if bdeep is not None else None,
        base_low_adr=fnum(bdeep_adr, 1) if bdeep_adr is not None else None,
        breakout_reclaim_today=reclaim_bo, reclaim_level=fnum(reclaim_level) if reclaim_level else None,
        retest_today=retest, retest_ema=retest_ema, retest_level=fnum(rlv[1]) if rlv else None, retest_level_wick=fnum(rlv[2]) if rlv else None,
        retest_from=st.dates[rlv[0]] if rlv else None, retest_zone=zone, tight_days=tight, tight_level=fnum(tlv) if tight >= 2 else None,
        # for the retest alerts during the day (radar/alerts.py), with the zone: the low has to get this far under the
        # high since the breakout (a real pullback, 1.5 ADRs), and whether it already closed 1.25 ADRs away from the level
        retest_need_low=fnum(st.h[rlv[0]:i + 1].max() * (1 - 1.5 * adr / 100)) if zone else None,
        retest_away=bool(c[rlv[0]:i + 1].max() >= rlv[1] * (1 + 1.25 * adr / 100)) if zone else None,
        retest_tried=st.dates[first] if first is not None else None,
        retest_low=fnum(st.l[rlv[0] + 1:i + 1].min()) if zone else None,          # tomorrow's low has to undercut it,
        retest_testing=bool(zone and first is not None and (c[first:i + 1] > a.e21[first:i + 1]).all()),   # unless testing over the 21 EMA
        push_level=fnum(push_level) if push_level else None, push_today=push_day == i,
        adr_pct=fnum(adr, 2), ema10=fnum(a.e10[i]), ema50=fnum(a.e50[i]), day_open=fnum(st.o[i]),
        sessions=i - i0, gain_pct=fnum(100 * (c[i] / c[i0] - 1), 1), max_gain_pct=fnum(100 * (hi / c[i0] - 1), 1),
        status=status, first_exit=st.dates[exit_k] if exit_k is not None else None,
        exit_gain_pct=fnum(100 * (c[exit_k] / c[i0] - 1), 1) if exit_k is not None else None,
        lost_50ema=st.dates[out50] if out50 is not None else None,
        off_50ema=st.dates[off50] if off50 is not None else None, ema50_under2=under50, ema50_today=reclaim50,
        ema50_under_dates=[st.dates[i - 1], st.dates[i]] if under50 else None,
        ema50_under_adr=[fnum(100 * (c[m] / a.e50[m] - 1) / _adr(st, m), 1) for m in (i - 1, i)] if under50 else None,
        price=fnum(c[i]), chg_today_pct=fnum(a.chg[i], 1), rel_vol_today=fnum(a.rv[i], 1),
        gap_base_level=fnum(gb[0]) if gb else None, gap_base_pattern=gb[1] if gb else None,
        pattern=pat, buy_point=fnum(bp) if bp else None, to_buy_point_pct=fnum(100 * (bp / c[i] - 1), 1) if bp else None,
        buy_point_top_date=top_date,
        base_breakout_today=bool(bo and bo[0] == i),
        last_breakout_date=st.dates[bo[0]] if bo else None, last_breakout_top=fnum(bo[1]) if bo else None,
        last_breakout_top_date=st.dates[bo[2]] if bo else None, last_breakout_days_ago=i - bo[0] if bo else None,
        last_breakout_base_days=below_since(a, bo[0], bo[1], bo[2]) if bo else None,
        base_days=fnum(bdays, 0) if bdays is not None else None, base_depth_pct=fnum(bdep, 1) if bdep is not None else None,
        flag_breakout_today=flag_bo, dry_entry_today=dry_day == i,
        flag_shape=fshape if flag_bo else (fl[4] if fl else None),
        base_depth_adr=fnum((bdep if bdep is not None else np.nan) / (st.adr[i] if st.adr[i] > 0 else np.nan), 1), surf10=surf(a.e10), surf21=surf(a.e21),
        vol_dryup=fnum(dry, 2), off_high_pct=fnum(100 * (1 - c[i] / hi), 1), ema21=fnum(a.e21[i]),
        breakout_today=bool(code and msf.is_pat(code) and r.bo == 1), leg=leg, late=leg >= L["late_leg"],
        new_run_after_rest=st.dates[rested] if rested is not None else None,
        days_since_new_high=i - last_new,
    )
    # too far from its momentum's start (the user, Nov 1 2026): 300%+ over that low, no buy points of any kind (2 years of
    # buy points: past it -0.4 to -0.8R whatever the entry; AEHR May 2026 +358-451%, SMCI Jul 20 / Aug 4 2023 +340 / +365%)
    ms = momentum_start(a, i)
    run_ = 100 * (c[i] / st.l[ms] - 1)
    out.update(momentum_start=st.dates[ms], momentum_start_low=fnum(st.l[ms]), run_from_start_pct=fnum(run_, 0), extended=bool(L["max_run_pct"] and run_ >= L["max_run_pct"]))
    if out["extended"]:
        out.update(buy_point=None, to_buy_point_pct=None, pattern=None, retest_zone=None, ema21_watch=None, push_level=None, reclaim_level=None,
                   gap_base_level=None, stage=out["stage"] + f" · EXTENDED: +{run_:.0f}% from its momentum start ({st.dates[ms]}, {st.l[ms]:.2f}), no buy points")
    return out


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
            # 21 EMA, or replaces it when it is the stronger day (APPN: a C on Aug 5 2026, the real launch, a B, on Aug 7).
            # A power day is never replaced: the days after it are its continuation (INFQ May 21 2026, a 20.8% gap, +31.5%
            # on 8.9x; May 22, +11.2% on a gap of 8.2%, was its 2nd day, not the launch; HLIT May 22 and May 26)
            if i - last > L["dedupe_days"] or any(a.st.c[j] < a.e21[j] for j in range(last + 1, i)):
                own.append((s, i, k, gs, gn))
                last = i
            elif rank[grade(a, i)] < rank[grade(a, last)] and not a.power(last):
                own[-1] = (s, i, k, gs, gn)
                last = i
        # a catalyst or reversal launch comes on top and never blocks a regular one (those stay exactly as they were): it counts
        # when no launch came in the 20 sessions before it, or the last one closed below the 21 EMA since
        for i, k in cat:
            prev = max((e[1] for e in own if e[1] < i), default=-10 ** 9)
            if i - prev > L["dedupe_days"] or any(a.st.c[j] < a.e21[j] for j in range(prev + 1, i)):
                gs, gn = best_group(s, k, groups, GS)
                own.append((s, i, k, gs, gn))
        events.extend(sorted(own, key=lambda e: e[1]))
    return events


def detect_laggards(A, groups, GS, cal):
    """every laggard launch day (under the 200 SMA, on a catalyst), one per stock per dedupe window like a launch"""
    pos = {d: k for k, d in enumerate(cal)}
    events = []
    for s, a in A.items():
        last = -10 ** 9
        for i in range(L["min_sessions"], len(a.st.dates)):
            k = pos.get(a.st.dates[i])
            if k is None or not a.laggard(i):
                continue
            if i - last > L["dedupe_days"] or any(a.st.c[j] < a.e21[j] for j in range(last + 1, i)):
                gs, gn = best_group(s, k, groups, GS)
                events.append((s, i, k, gs, gn))
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


def picks_of(path):
    """{symbol: when you added it (ISO time, New York)} from setups/picks.json (the portal's Follow button)"""
    try:
        return {s.upper(): p["added"] for s, p in json.load(open(path)).get("picks", {}).items() if p.get("added")}
    except Exception:
        return {}


def removed_setups_of(path):
    """{symbol: the feeder-list day it came on} you removed from 3-SETUPS with ✕ (setups/picks.json "removed_setups")"""
    try:
        return {s.upper(): p["added"] for s, p in json.load(open(path)).get("removed_setups", {}).items() if p.get("added")}
    except Exception:
        return {}


def stale(a, i0, last, top=None):
    """off the list (your rule, Nov 1 2026): 62 sessions from its highest point without a new high, at any time since the
    launch (or your pick; top = the base top a pick started under). A $60 high 5 days ago with the stock at $55 today
    counts from the $60 day. Once off, it stays off (a new launch on a later day is a new row)"""
    h = a.st.h[i0:last + 1]
    m = np.maximum.accumulate(np.concatenate(([top if top else h[0]], h[1:])))
    new = [0] + [k for k in range(1, h.size) if m[k] > m[k - 1]] + [h.size - 1]
    return any(b - a_ >= L["off_days"] for a_, b in zip(new, new[1:]))


def removed_of(path):
    """{symbol: the launch day you removed (YYYY-MM-DD)} from setups/picks.json (the portal's ✕ on the Launches tab).
    Only that launch is left out: a new launch of the stock on a later day shows again"""
    try:
        return {s.upper(): p["launch"] for s, p in json.load(open(path)).get("removed", {}).items() if p.get("launch")}
    except Exception:
        return {}


S3_FEEDERS = ("1-EP/GAP", "1-UPDAY", "2-POOL")
S3_SECTIONS = ("Triggered today", "Ready", "Setting up")


def s3_read(a, i0, last, was_in=False):
    """3-SETUPS: where a feeder stock followed from i0 stands at bar `last` (None = not on the list): (section, setup,
    the follow, buy point, away in ADRs, close, ADR, tight days, retest zone)"""
    st = a.st
    if not a.liq_noadr[last] or st.adr[last] < (L["off_adr"] if was_in else L["s3_min_adr"]):
        return None
    b0 = base_ok(a, i0, 120)
    if stale(a, i0, last, b0[0] if b0 and b0[0] > st.h[i0] else None):
        return None
    f = follow(a, i0, last, pick=True)
    if f.get("lost_50ema"):
        return None
    c, adr = float(st.c[last]), float(f.get("adr_pct") or st.adr[last])
    bp = f.get("buy_point")
    away_adr = (100 * (bp / c - 1)) / adr if bp and adr else None
    stage, pat = f.get("stage") or "", f.get("pattern") or ""
    fired = next((t for t, on in (("Base breakout", f.get("base_breakout_today")), ("Bull pennant breakout" if f.get("flag_shape") == "pennant" else "Bull flag breakout", f.get("flag_breakout_today")),
                                  ("Pop out of the consolidation", f.get("dry_entry_today")),
                                  ("Breakout undercut & reclaim", f.get("breakout_reclaim_today")),        # the user, Nov 2 2026
                                  ("21 EMA undercut & reclaim" if f.get("ema21_today") == "undercut" else "21 EMA retest", f.get("ema21_today")),
                                  ("Retest held", f.get("retest_today")), ("Push out of the 21 EMA", f.get("push_today")),
                                  ("Breakout", f.get("breakout_today"))) if on), None)
    tight = f.get("tight_days") or 0
    z = f.get("retest_zone")
    if fired:
        sec, setup = "Triggered today", fired
    elif away_adr is not None and 0 <= away_adr <= L["s3_ready_adr"] and ((f.get("base_day") or 0) >= 5 or tight >= 2):
        sec, setup = "Ready", pat or "Buy point"
    elif pat.startswith(("Flag", "Bull flag", "Bull pennant", "Pennant")):
        sec, setup = "Setting up", ("Bull pennant" if pat.startswith(("Bull pennant", "Pennant")) else "Bull flag") + " forming"
    elif f.get("ema21_watch"):
        sec, setup = "Setting up", "21 EMA " + ("undercut & reclaim" if f["ema21_watch"] == "undercut" else "retest") + " setup"
    elif z and f.get("retest_away") and c <= z[1] * (1 + adr / 100) and (f.get("off_high_pct") or 0) >= 1.5 * adr:   # a real pullback
        sec, setup = "Setting up", "Near the retest zone"
    else:
        return None
    return sec, setup, f, bp, away_adr, c, adr, tight, z


def setups3(A, today, wl, prev=(), removed=None):
    """3-SETUPS (your design, Nov 1 2026): every stock on 1-EP/GAP, 1-UPDAY and 2-POOL read by the Launches engine, like a
    pick from the day it came on its list (the gap or up day; the day it entered 2-POOL), with its buy points and
    triggers. Sections:
      Triggered today  a base breakout, bull flag / pennant breakout, breakout undercut & reclaim, pop, 21 EMA retest or undercut & reclaim, retest held or push today
      Ready            a trigger within 0.7 ADR over the close, in a base of 5+ days or tight 2+ days under it: tomorrow's buys
      Setting up       a flag forming (its line more than 0.7 ADR away), a pullback set up for the 21 EMA, or a pullback
                       near the retest zone of its last breakout
    In: liquid with an ADR of 4%+ (3.2%+ once on the list). Off: 2 closes in a row under the 50 EMA, 62 sessions from its
    highest point without a new high, its ADR under 3.2%, or your ✕ (until it comes on a feeder list again)."""
    seen, rows = {}, []
    for name in S3_FEEDERS:
        for r in wl.get("lists", {}).get(name, []):
            seen.setdefault(r["symbol"], (name, r))
    for sym, (src, w) in seen.items():
        a = A.get(sym)
        added = w.get("added") or w.get("section")
        if a is None or not added:
            continue
        st = a.st
        last = len(st.dates) - 1
        if st.dates[last] != today or (removed or {}).get(sym, "") >= added:
            continue
        i0 = max((k for k in range(last + 1) if st.dates[k] <= added), default=None)
        if i0 is None or i0 < 60:
            continue
        x = s3_read(a, i0, last, sym in prev)
        if x is None:
            continue
        sec, setup, f, bp, away_adr, c, adr, tight, z = x
        stage, pat = f.get("stage") or "", f.get("pattern") or ""
        e21 = f.get("ema21")
        if setup.startswith("21 EMA") and sec == "Setting up" and e21:      # the level that matters here is the 21 EMA
            why = setup + f": the 21 EMA {fnum(e21)}, the close {(100 * (c / e21 - 1)) / adr:.1f} ADR over it"
        elif setup == "Near the retest zone" and z:
            why = setup + f" {fnum(z[0])}-{fnum(z[1])}, the close {(100 * (c / z[1] - 1)) / adr:.1f} ADR over it"
        else:
            why = setup + (f" {fnum(bp)}" if bp and sec != "Triggered today" else "") \
                + (f", {away_adr:.1f} ADR away" if away_adr is not None and sec != "Triggered today" else "")
        why += (f" · tight ×{tight}" if tight >= 2 else "") + f" (from {src} {added})"
        row = {k: v for k, v in w.items() if k not in ("section", "setups", "why", "promoted", "ema_triggers_tomorrow")}   # the old PB screens' note
        row.update(section=sec, setup=setup, setups=[], source=src, added=added, last_hit=None, why=why, stage=stage,
                   pattern=pat or w.get("pattern"), buy_point=fnum(bp) if bp else None,
                   to_buy_point_pct=fnum(100 * (bp / c - 1), 1) if bp else None, away_adr=fnum(away_adr, 2) if away_adr is not None else None,
                   base_day=f.get("base_day"), base_depth_adr=f.get("base_depth_adr"), tight_days=tight, vol_dryup=f.get("vol_dryup"),
                   adr_pct=fnum(adr, 2), leg=f.get("leg"))
        rows.append(row)
    rows.sort(key=lambda r: (S3_SECTIONS.index(r["section"]), r["away_adr"] if r["away_adr"] is not None else 99, r["symbol"]))
    return rows


RES_SPANS = ((63, "3m"), (126, "6m"), (189, "9m"), (252, "52w"))


def resistance(a, i, floor=None):
    """the highs overhead the stock still has to clear (your rule, Nov 2 2026): the 3-, 6-, 9-month and 52-week highs
    over the close and over the buy point (shown on its own), lowest first, [[label, level]]; a high that is the top of
    several spans takes the shortest one's label"""
    st = a.st
    lo = max(float(st.c[i]), float(floor or 0)) * 1.005
    out = []
    for n, lab in RES_SPANS:
        hi = float(st.h[max(0, i - n + 1):i + 1].max())
        if hi > lo and not any(abs(hi / x[1] - 1) < 0.005 for x in out):
            out.append([lab, round(hi, 2)])
    return out


def write_watchlist(rows, wl_path, wl):
    """the new 3-SETUPS into the Watchlist's files: latest.json, the day's history file, the TradingView import file and
    the README (run.py builds the other three lists before this)"""
    wl["lists"]["3-SETUPS"] = rows
    wl["counts"]["3-SETUPS"] = len(rows)
    for lst in wl["lists"].values():                    # the overhead highs, on every list
        for r in lst:
            a = RES_A.get(r.get("symbol"))
            if a is not None:
                r["resistance"] = resistance(a, len(a.st.dates) - 1, r.get("buy_point"))
    json.dump(wl, open(wl_path, "w"), indent=1)
    out = os.path.dirname(wl_path)
    hp = os.path.join(out, "history", wl["date"] + ".json")
    if os.path.exists(hp):
        h = json.load(open(hp))
        h["setups"] = rows
        h.setdefault("lists", {})["3-SETUPS"] = [r["symbol"] for r in rows]
        h.setdefault("counts", {})["3-SETUPS"] = len(rows)
        json.dump(h, open(hp, "w"), separators=(",", ":"))
    lines = []
    for sec in S3_SECTIONS:
        tv = [r["tv"] for r in rows if r["section"] == sec]
        if tv:
            lines += ["###" + sec] + tv
    os.makedirs(os.path.join(out, "tradingview"), exist_ok=True)
    open(os.path.join(out, "tradingview", "3-SETUPS.txt"), "w").write("\n".join(lines) + "\n")
    try:
        open(os.path.join(out, "README.md"), "w").write(run.summary_md(wl))
    except Exception as e:                              # the README is a convenience: never fail the scan on it
        print("README not rewritten:", e)


def gap_base_fields(a, i, prev=None):
    """gap out of base (your rule, Nov 1 2026): whether the stock qualifies at this close (ADR 4%+, 600K+ shares and
    $30M+ traded a day, 20-day averages, market cap $700M+) and whether today opened above last night's base high
    (prev: last night's row of it) from a close at or under it"""
    st = a.st
    c, v = st.c, st.v
    dv = float(np.dot(c[i - 19:i + 1], v[i - 19:i + 1])) / 20 / 1e6 if i >= 19 else 0.0
    av = float(v[i - 19:i + 1].mean()) if i >= 19 else 0.0
    ok = bool(st.adr[i] >= L["gob_min_adr"] and av >= L["gob_min_shares"] and dv >= L["gob_min_dv"]
              and (getattr(st, "mcap", None) or 0) >= L["gob_min_mcap"] * 1e6)
    out = dict(dollar_vol_20d_m=fnum(dv, 1), avg_vol_20d=int(av), gap_base_ok=ok, gap_out_today=None)
    lv = (prev or {}).get("gap_base_level")
    if lv and prev.get("gap_base_ok") and i >= 1 and c[i - 1] <= lv < st.o[i]:
        out["gap_out_today"] = dict(level=lv, pattern=prev.get("gap_base_pattern"), open_pct=fnum(100 * (st.o[i] / lv - 1), 1),
                                    closed_over=bool(c[i] > lv))
    return out


def daily(A, groups, GS, cal, S, out_path, news=None, earnings=None, picks=None, removed=None, s3=None):
    pos = {d: k for k, d in enumerate(cal)}
    today = cal[-1]
    T = len(cal) - 1
    rows = []
    # the earnings and news days a catalyst launch can come on: tonight's tags plus the ones kept from earlier nights
    # (Yahoo's earnings date moves on to the next report; the grade log keeps only the last days)
    try:
        old_doc = json.load(open(out_path))
    except Exception:
        old_doc = {}
    kept = {(d[0], d[1]): d[2] for d in old_doc.get("catalyst_days", []) + old_doc.get("news_days", [])}
    prev_s3 = old_doc.get("setups3", [])
    old_rows = {r_["symbol"]: r_ for r_ in old_doc.get("launches", [])}
    same_day = old_doc.get("date") == today

    def gap_fields(s_, a_, i_):
        if same_day:
            g_ = gap_base_fields(a_, i_)
            g_["gap_out_today"] = old_rows.get(s_, {}).get("gap_out_today")
            return g_
        return gap_base_fields(a_, i_, old_rows.get(s_) if len(cal) > 1 and old_doc.get("date") == cal[-2] else None)
    tags = dict(kept)
    for s, d in (earnings or {}).items():
        a = A.get(s)
        if a is not None and d in a.st.dates[-200:]:
            k = a.st.dates.index(d)
            for m in range(k, min(k + 2, len(a.st.dates))):    # and the session after: GMAB raised its guidance at 3:52 PM
                tags[(s, a.st.dates[m])] = "earnings"           # on Aug 6 2026, the gap came Aug 7
    tags.update({k: "news " + v for k, v in (news or {}).items()})
    CATALYST_DAYS.clear()
    NEWS_DAYS.clear()
    for (s, d), w in tags.items():
        a = A.get(s)
        if a is not None and d in a.st.dates[-200:]:
            NEWS_DAYS[(s, d)] = w
    for (s, d), w in tags.items():
        a = A.get(s)
        k = a.st.dates.index(d) if a is not None and d in a.st.dates[-200:] else None
        if k is not None and a.gap[k] >= L["ep_gap"]:
            CATALYST_DAYS[(s, d)] = w

    def build(s, i, k, gs, gn, leader):
        """a launch's row for the list, or None when it is off the list"""
        a = A[s]
        last = len(a.st.dates) - 1
        if a.st.dates[last] != today or a.st.dates[i] <= (removed or {}).get(s, ""):    # removed by you (✕), with any older launch of it
            return None
        # off the list: 3 closes in a row under the 50 EMA (after 2 it waits in the 50 EMA undercut tab for the reclaim:
        # your rule, Nov 1 2026), 62 sessions from its highest point without a new high, or its ADR (20 days) now under
        # 3.2% (a launch day needs 3.5%+; TECH Jun 25 2026, a buyout-like 19% gap, then 0.2%)
        c_, e50_ = a.st.c, a.e50
        if (np.any((c_[i + 3:last + 1] < e50_[i + 3:last + 1]) & (c_[i + 2:last] < e50_[i + 2:last]) & (c_[i + 1:last - 1] < e50_[i + 1:last - 1]))
                or stale(a, i, last) or a.st.adr[last] < L["off_adr"]):
            return None
        f = follow(a, i, last)
        if f["off_50ema"]:
            return None
        r = launch_row(s, a, i, gs, gn, S)
        r.update(f)
        r["follows"] = leader or None
        r.update(gap_fields(s, a, last))
        r["news"] = (news or {}).get((s, r["date"]))
        r["earnings"] = (earnings or {}).get(s) == r["date"] or CATALYST_DAYS.get((s, r["date"])) == "earnings"
        if r["catalyst"]:
            r["catalyst"] = CATALYST_DAYS.get((s, r["date"]))
        cgs, cgn = best_group(s, T, groups, GS)
        r["group_now"], r["group_status_now"] = cgn, STATUS.get(cgs, "No group")
        up = next((kk for kk in range(k, T + 1) if best_group(s, kk, groups, GS)[0] >= 1), None)
        r["theme_up_since"] = cal[up] if up is not None else None      # first day from the launch its theme was trending
        r["lone_wolf"] = up is None
        r["resistance"] = resistance(a, last, r.get("buy_point"))
        return r

    ev = detect(A, groups, GS, cal, S)
    for e in [e + ("",) for e in ev] + detect_followers(A, groups, GS, cal, ev):
        r = build(*e)
        if r is not None:
            rows.append(r)
    order = {"A+": -1, "A": 0, "B": 1, "C": 2}
    rows.sort(key=lambda r: (order[r["grade"]], -r["rel_vol"]))
    rows.sort(key=lambda r: r["date"], reverse=True)              # newest first, best grade first within a day
    # one launch per stock: the newest (ANF: the Aug 26 2026 power day replaced the Aug 3 C launch, which had
    # closed below the 21 EMA on Aug 17; both followed gave two alerts with different legs)
    seen = set()
    rows = [r for r in rows if not (r["symbol"] in seen or seen.add(r["symbol"]))]
    # the 50 EMA undercut tab: 2 closes in a row under the 50 EMA at this close, the reclaim has to come next session
    under50 = [r for r in rows if r.get("ema50_under2")]
    rows = [r for r in rows if not r.get("ema50_under2")]
    # Launch Laggards: launches under the 200 SMA on a catalyst (earnings or graded news), followed the same way; a stock
    # already on the launch list stays there only
    # Once a laggard closes over the 200 SMA 5 sessions in a row it moves to the launch list, marked with the day it
    # did (your rule, Nov 2 2026)
    lag, promoted = [], []
    for e in detect_laggards(A, groups, GS, cal):
        r = build(*e, "")
        if r is None:
            continue
        w = NEWS_DAYS.get((r["symbol"], r["date"]), "")
        r["laggard_catalyst"] = w
        r["earnings"] = r["earnings"] or w == "earnings"
        r["news"] = r["news"] or (w[5:] if w.startswith("news ") else None)
        a, i = A[e[0]], e[1]
        above = a.st.c > a.s200
        j = next((m for m in range(i + 5, len(a.st.dates)) if above[m - 4:m + 1].all()), None)
        r["promoted"] = a.st.dates[j] if j is not None else None
        (promoted if j is not None else lag).append(r)
    on_list = {r["symbol"] for r in rows} | {r["symbol"] for r in under50}
    for grp in (lag, promoted):
        grp.sort(key=lambda r: (order[r["grade"]], -r["rel_vol"]))
        grp.sort(key=lambda r: r["date"], reverse=True)
    seen = set()
    promoted = [r for r in promoted if r["symbol"] not in on_list and not (r["symbol"] in seen or seen.add(r["symbol"]))]
    lag = [r for r in lag if r["symbol"] not in on_list and not (r["symbol"] in seen or seen.add(r["symbol"]))]
    rows = sorted(rows + promoted, key=lambda r: r["date"], reverse=True)
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
        b0 = base_ok(a, i0, 120)
        if stale(a, i0, last, b0[0] if b0 and b0[0] > a.st.h[i0] else None):   # 62 sessions from its highest point, no new high
            continue
        r = launch_row(s, a, i0, gs, gn, S)
        r.update(follow(a, i0, last, pick=True))
        cgs, cgn = best_group(s, T, groups, GS)
        r.update(grade="You", pick=added, follows=None, news=None, earnings=False, group_now=cgn,
                 group_status_now=STATUS.get(cgs, "No group"), theme_up_since=None, lone_wolf=False)
        r.update(gap_fields(s, a, last))
        r["resistance"] = resistance(a, last, r.get("buy_point"))
        rows.append(r)
    # watch list for the intraday trigger: liquid, from 25% under to 50% over the 200 SMA (over 28%: power days
    # only; under it: only once it trades back above it, e.g. a catalyst gap), no launch in 20 days
    launched = {r["symbol"] for r in rows + lag if r["sessions"] < L["dedupe_days"] and not r["first_exit"] and r["grade"] != "You"}
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
        # 28-50% over: power days only (the trigger checks); down to 60% under for a laggard launch on a catalyst
        if ext > L["power_ext200"] or ext < -max(L["watch_under200"], L["lag_under200"]):
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
                    fnum(st.c[i - 49:i + 1].mean()) if i >= 49 else None, fnum(st.low52[i])]
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
                             "sma50", "low_52w"],
               launches=rows, ema50_undercut=under50, laggards=lag, watch=watch, groups=[g for g in G if g["status"] != "Not trending"],
               catalyst_days=sorted([s, d, w] for (s, d), w in CATALYST_DAYS.items()),
               news_days=sorted([s, d, w] for (s, d), w in NEWS_DAYS.items()),
               # 3-SETUPS for the live alerts (desktop: every trigger; phone: Ready only); kept from the evening scan when
               # a Follow-button rebuild doesn't pass the Watchlist
               setups3=s3 if s3 is not None else prev_s3)
    with open(out_path, "w") as f:
        json.dump(doc, f, separators=(",", ":"))
    n_today = sum(1 for r in rows if r["date"] == today)
    print(f"launch: {n_today} today, {len(rows)} followed, {len(lag)} laggards, {len(under50)} in the 50 EMA undercut tab, {len(watch)} on watch, {len(doc['groups'])} groups trending")


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
    ap.add_argument("--watchlist", help="setups/latest.json (run.py, just before): 3-SETUPS is built from its other three lists")
    a = ap.parse_args()
    global ENTRY
    ENTRY = a.entry
    A, groups, GS, cal, S = load(a.bars, a.stocks)
    RES_A.update(A)
    s3 = None
    if a.watchlist:
        wl = json.load(open(a.watchlist))
        try:
            prev = {r["symbol"] for r in json.load(open(a.out)).get("setups3", [])}
        except Exception:
            prev = set()
        rows = setups3(A, cal[-1], wl, prev, removed_setups_of(a.picks) if a.picks else {})
        write_watchlist(rows, a.watchlist, wl)
        s3 = [dict(symbol=r["symbol"], tv=r.get("tv"), section=r["section"], setup=r["setup"], buy_point=r["buy_point"],
                   away_adr=r["away_adr"], adr_pct=r["adr_pct"], why=r["why"]) for r in rows]
        print("3-SETUPS:", {sec: sum(1 for r in rows if r["section"] == sec) for sec in S3_SECTIONS})
    daily(A, groups, GS, cal, S, a.out, news_of(a.gradelog) if a.gradelog else {}, earnings_of(a.live, cal) if a.live else {},
          picks_of(a.picks) if a.picks else {}, removed_of(a.picks) if a.picks else {}, s3)
    if a.backtest:
        backtest(A, groups, GS, cal, S, a.backtest)


if __name__ == "__main__":
    main()
