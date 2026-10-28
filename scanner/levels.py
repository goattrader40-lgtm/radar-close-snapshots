"""Levels design (on test, not live yet): the buy points of a stock being followed, read the way you read a chart.

  levels   every clear prior peak overhead is a level: the highest high within 5 sessions either side, 5+
           sessions old, with a pullback of 1.25+ of the stock's own ADRs after it, no close above it since (a
           breakout that failed within 3 sessions puts it back). The buy point is the nearest level above the
           close; levels within half an ADR of each other are one (the higher). SG Oct 2026: the June-July high
           $9.49 under the May high $10.63, the cup's rim (the 6-month base top missed the $9.49 shelf).
  tight    the tell before a breakout: tight candles in a row (the day's move and its body half an ADR or less)
           closing within an ADR under the level (SG Oct 5-7 under $9.49, then the Oct 8 breakout).
  breakout a close over the level on 1x+ volume; failed when it closes back under it within 3 sessions (SG: Oct 20
           over $10.63, back under Oct 21); a 1-year high when nothing traded above the level for 250 sessions.
  retest   end of day, after a breakout that held: the low comes back to the broken level (from an ADR under it to
           a quarter ADR over) and the close holds above it (SG Oct 26 at $9.49; ANF Oct 23 at $155.22); or a
           21 EMA test: the low at or under the 21 EMA, the close back above it in the upper half of the day's
           range, above the 50 EMA. One per pullback (the next needs a new high first).
  line     the sloping line across the pullback's highs under a flat top: the top is the run's high, 5-20
           sessions old, the pullback 1.25-4 ADRs deep above the 50 EMA; a close over tomorrow's value of the
           line (SG Oct 28: about $10.36 under the $10.77 top).
  run      counted from its start, the lowest low since the stock last closed under its 50 EMA, and it must be
           4+ ADRs and made by the trend: no single day 50%+ of it. A gap launch first needs its rest: ANF ran on
           its Aug 26 gap alone, so its Sep 16 pullback is no entry (the pop out of the consolidation, Oct 5, is).
"""
import numpy as np
import msf

LV = dict(peak_win=5, peak_age=5, peak_pull=1.25, lookback=250, merge=0.5, bo_rv=1.0, fail_days=3,
          tight_move=0.5, tight_body=0.5, near=1.0, retest_above=0.25, retest_below=1.0,
          run_adr=4.0, gap=5.0, gap_rv=3.0, line_min=5, line_max=20, line_depth_min=1.25, line_depth_max=4.0)


def _adr(st, k):
    return st.adr[k] if st.adr[k] > 0 else 5.0


def run_from(a, j):
    """where the run on day j is counted from: the lowest low since the stock last closed under its 50 EMA (within
    a year), or, when a big gap came after that (5%+ on 3x+ volume: a gap launch), that gap day's close: what the
    gap itself did is no run (ANF Aug 26 2026: its pullbacks under the gap day's high were the base, not entries)"""
    st, c = a.st, a.st.c
    k = j
    while k > max(0, j - LV["lookback"]) and c[k] >= a.e50[k]:
        k -= 1
    s = k + int(np.argmin(st.l[k:j + 1]))
    g = max((m for m in range(s, j + 1) if a.gap[m] >= LV["gap"] and a.rv[m] >= LV["gap_rv"]), default=None)
    return (g, c[g]) if g is not None else (s, st.l[s])


def run_adrs(a, j, top):
    """how far the run went to `top`, in the stock's own ADRs"""
    s, base = run_from(a, j)
    return 100 * (top / base - 1) / _adr(a.st, j) if base > 0 else 0.0


def walk(a, i0, i1):
    """day by day from i0 + 1 to i1: the events [(day index, kind, details)] and each evening's state
    {day index: (buy point, what, tight days, line for tomorrow)}"""
    st = a.st
    h, l, c, o = st.h, st.l, st.c, st.o
    n, w = c.size, LV["peak_win"]
    events, state = [], {}
    levels = {}                    # peak index -> [price, status: "on" / "broken", broken on]
    held = None                    # (level, broken on) of the last breakout that held
    done = None                    # (the pullback's high, the kinds already signalled in it)
    used_line = set()
    first = max(i0 + 1, 60)
    for j in range(first, min(i1, n - 1) + 1):
        adr = _adr(st, j - 1)
        # the levels known at yesterday's close: clear peaks 5+ sessions old with a 1.25+ ADR pullback after them
        # (on the first day, all of the last year's)
        for p in (range(max(w, j - 1 - LV["lookback"]), j - LV["peak_age"]) if j == first else (j - 1 - LV["peak_age"],)):
            if p - w >= 0 and p not in levels and h[p] >= h[max(0, p - w):p + w + 1].max() \
                    and 100 * (1 - l[p + 1:j].min() / h[p]) >= LV["peak_pull"] * _adr(st, p) and not (c[p + 1:j] > h[p]).any():
                levels[p] = [h[p], "on", None]
        for q in [q for q in levels if q < j - LV["lookback"]]:
            del levels[q]
        on = sorted({v[0] for v in levels.values() if v[1] == "on" and v[0] > c[j - 1]})
        # one level per half ADR: the higher of a cluster
        lv = max(x for x in on if x <= on[0] * (1 + LV["merge"] * adr / 100)) if on else None
        # tight days just under it (the tell)
        tight = 0
        if lv:
            for k in range(j - 1, max(i0, j - 11), -1):
                ak = _adr(st, k)
                if not (lv * (1 - LV["near"] * ak / 100) <= c[k] < lv and abs(a.chg[k]) <= LV["tight_move"] * ak
                        and abs(c[k] - o[k]) <= LV["tight_body"] * ak / 100 * c[k - 1]):
                    break
                tight += 1
        # the sloping line across the pullback's highs, under a flat top that is the run's high
        line = None
        t = j - 1 - 24 + int(np.argmax(h[j - 25:j]))
        if LV["line_min"] <= j - 1 - t <= LV["line_max"] and t not in used_line and h[t] >= h[max(0, t - 120):t + 1].max():
            depth = 100 * (1 - l[t + 1:j].min() / h[t])
            if LV["line_depth_min"] <= depth / _adr(st, t) <= LV["line_depth_max"] and not any(c[k] < a.e50[k] for k in range(t + 1, j)):
                if run_adrs(a, t, h[t]) >= LV["run_adr"]:
                    slope = max((h[k] - h[t]) / (k - t) for k in range(t + 1, j))
                    if slope < 0:
                        line = (h[t] + slope * (j - t), t)
        state[j - 1] = (lv, tight, line[0] if line else None)
        # today's events, at the close
        if line and c[j] > line[0]:
            events.append((j, "line", dict(line=round(float(line[0]), 2), top=round(float(h[line[1]]), 2))))
            used_line.add(line[1])
        broke = []
        for q, v in levels.items():
            if v[1] == "on" and c[j] > v[0]:
                v[1], v[2] = "broken", j                   # on light volume it is gone without a breakout
                if a.rv[j] >= LV["bo_rv"]:
                    broke.append((v[0], q))
            elif v[1] == "broken" and j - v[2] <= LV["fail_days"] and c[j] < v[0]:
                v[1], v[2] = "on", None
                events.append((j, "failed", dict(level=round(float(v[0]), 2))))
                if held and abs(held[0] - v[0]) < 1e-9:
                    held = None
            elif v[1] == "broken" and j - v[2] == LV["fail_days"] and (held is None or v[2] >= held[1]):
                held = (v[0], v[2])                         # it held 3 sessions: the level to retest
        if broke:
            top, q = max(broke)
            # the base under the level: sessions since anything last traded above it before its peak (RPD's 13.87, set
            # Oct 12 2026, last exceeded Aug 11); and the pattern your MSF engine saw at yesterday's close
            m = next((m for m in range(q - 1, max(-1, q - 500), -1) if h[m] > top), None)
            r = st.df.iloc[j - 1]
            code = int(r.code)
            pat = msf.NAMES[code] if code and msf.is_pat(code) else None
            piv = bool(pat and r.pivot == r.pivot and abs(r.pivot - top) <= _adr(st, j - 1) / 100 * top)
            events.append((j, "breakout", dict(level=round(float(top), 2), tight=tight if lv and top <= lv * (1 + 1e-9) and top >= lv * (1 - 1e-9) else 0,
                                               year_high=bool(h[max(0, j - 250):j].max() <= top * 1.0001), rv=round(float(a.rv[j]), 1),
                                               base_len=j - m - 1 if m is not None else 500, msf=pat, msf_pivot=piv)))
        if held and c[j] < held[0] * (1 - _adr(st, j) / 100):
            held = None                                     # lost the level
        # retest of the broken level / 21 EMA test, end of day, each once per pullback (the next needs a new high)
        if done and h[j] > done[0]:
            done = None
        ad = _adr(st, j)
        top = h[max(0, j - 20):j].max()
        if top >= c[j] * (1 + ad / 100):                     # it pulled back an ADR+ from the recent high
            lvl_test = bool(held and j - held[1] >= 2 and held[0] * (1 - LV["retest_below"] * ad / 100) <= l[j] <= held[0] * (1 + LV["retest_above"] * ad / 100)
                            and c[j] > held[0])
            ema_test = bool(a.e21[j] * (1 - LV["retest_below"] * ad / 100) <= l[j] <= a.e21[j] * (1 + LV["retest_above"] * ad / 100)
                            and c[j] > a.e21[j] and c[j] > a.e50[j] and h[j] > l[j] and (c[j] - l[j]) / (h[j] - l[j]) >= 0.5)
            # the retest is the trade; the 21 EMA counts when it is there too (SG Oct 26: the June high $9.49 and the
            # 21 EMA $9.52 together); a 21 EMA test with no broken level under it is kept apart (no pattern, no trade)
            ema_conf = bool(lvl_test and abs(a.e21[j] - held[0]) <= ad / 100 * held[0])
            for kind, ok in (("retest", lvl_test), ("ema21", ema_test and not lvl_test and run_adrs(a, j, top) >= LV["run_adr"])):
                if ok and not (done and kind in done[1]):
                    events.append((j, kind, dict(level=round(float(held[0]), 2) if kind == "retest" else None, ema21=round(float(a.e21[j]), 2),
                                                 ema_conf=ema_conf)))
                    done = (top, (done[1] if done else set()) | {kind})
    return events, state
