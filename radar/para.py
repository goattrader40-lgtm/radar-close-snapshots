#!/usr/bin/env python3
"""Parabolic shorts (the user, Nov 27-28 2026: "build something in our radar to catch parabolic short setups"; their
examples CAR Apr 22 2026, BYND Oct 22 2025, NMAX Apr 1 2025: "so many others out there happened as well"; "find me good
setup for this kind of runs, when we should short"). The rule comes from the study of Nov 28 2026: every US stock on
NASDAQ / NYSE / AMEX in Alpaca's list (6,429), Dec 2020 - Nov 2026, 1-minute SIP bars of the trade days.

  The list (evening)  a stock that closed UP 3+ sessions in a row, those 3 sessions adding 50%+ (the close 3 sessions ago
                      -> today's close), on $20M+ traded today. It is on the list for the next session only.
  The trade day       it opens 3%+ over that close AND 130%+ over its lowest close of the 20 sessions before, at $5+
                      ("gapped up, armed"). No gap = no trade (a 1-3% gap had no edge; under 130% the same shorts earned
                      +0.14R to +0.17R instead of +0.5R; under $5: +0.06R).
  The short           the first trade under the low of the opening 5-minute candle (9:30-9:35), until 3:30 PM: short at
                      that low (at the bar's open when it opens under it). The user's own entry upside down (they buy the
                      5-minute opening range high, stop the day's low).
  The stop            the day's high up to the short.
  One re-entry        stopped out the same day: the next 5-minute candle that CLOSES under VWAP after one closed over it
                      (short at that close, stop = the day's new high). BYND Oct 22 2025: the 9:39 short was stopped on
                      the run to 230.70, VWAP was lost for good near 11:05 and it closed at 107.40.
  The cover           the next session's close (the stop stays: a trade at it the next day = out).

  The study, $5+, both halves of the period alike: the opening-low short 400 trades, 55% won, +1.77R / -0.97R,
  +0.56R (+6.7%) a trade at the next close (same-day close +0.32R); with the one re-entry +0.66R a trade day. The first
  VWAP break as the first short: 425 trades, 48%, +0.55R. Longest run of losers: 8. Not in the test: whether the shares
  can be borrowed, halts, the fills (the short is counted at the trigger price); delisted stocks are mostly missing.
  CAR Apr 22 2026: gap +8.5% to 774.99 after +59% in 3 sessions; the opening low 770.31 broke at 9:51, stop 847.70; the
  close 443.94 (+42.6%), the next close 229.14 (+70.4%, 7R). The day before (Apr 21) the same short was stopped.

The evening list is scanner/parabolic.py (setups/parabolic.json); radar/alerts.py find_para reads it with today's 1-minute
chart; this module is the rule the list, the alerts and the tests all use."""

RULES = {
    "up_days": 3,            # closes up in a row, at least
    "gain3_pct": 50.0,       # those 3 sessions added at least this much
    "min_dvol_m": 20.0,      # $ traded on the last session, millions
    "run20_pct": 130.0,      # the open over the lowest close of the 20 sessions before, at least
    "gap_pct": 3.0,          # the open over the last close, at least
    "min_price": 5.0,        # the open, at least
    "range_min": 5,          # minutes of the opening candle
    "last_entry_min": 360,   # no new short from 3:30 PM (minutes after 9:30)
    "reentry": True,         # one re-entry after a stop-out the same day
}


def list_row(bars, rules=RULES):
    """the evening list's test on a stock's daily bars [(date, open, high, low, close, volume)] (oldest first, the last
    one = the session just closed). Returns None, or the row: the 3-session gain, the up days, the run so far, and the
    open it needs tomorrow (need_open: 3%+ over the close, 130%+ over the 20-session low close, $5+)"""
    if len(bars) < 5:
        return None
    c = [b[4] for b in bars]
    v = [b[5] for b in bars]
    if not (c[-1] and c[-4]):
        return None
    ups, j = 0, len(c) - 1
    while j > 0 and c[j] > c[j - 1]:
        ups += 1
        j -= 1
    if ups < rules["up_days"]:
        return None
    g3 = (c[-1] / c[-4] - 1) * 100
    dvol = c[-1] * v[-1] / 1e6
    if g3 < rules["gain3_pct"] or dvol < rules["min_dvol_m"]:
        return None
    lo20 = min(x for x in c[-20:] if x)
    need = max(c[-1] * (1 + rules["gap_pct"] / 100), lo20 * (1 + rules["run20_pct"] / 100), rules["min_price"])
    return {"close": c[-1], "gain3": round(g3, 1), "up_days": ups, "dvol_m": round(dvol, 1), "lo20": lo20,
            "run20": round((c[-1] / lo20 - 1) * 100, 1), "need_open": round(need + 0.004999, 2),
            "gap_need": round((need / c[-1] - 1) * 100, 1), "high": bars[-1][2]}


def check(bars, prev_close, lo20, now_min=None, rules=RULES):
    """the state of one list stock today from its 1-minute bars [(minute after 9:30, o, h, l, c, v)].
    prev_close / lo20: the list row's close and 20-session low close; now_min = minutes since 9:30 now (None = the whole
    day is known: the tests). Only finished minutes are read. Returns
      open, gap (%), run20 (% of the open over lo20), armed (the gap day's three tests), why (when not armed),
      orl (the opening candle's low, once it is over), hod, vwap, last (price),
      short   {"min", "px", "stop", "orl"} | None   the opening-low short
      stopped minute | None                           its stop was traded
      re      {"min", "px", "stop", "vwap"} | None   the one re-entry
      stopped2 minute | None
      on      "short" | "re" | None                   the short that is open now"""
    out = {"open": None, "gap": None, "run20": None, "armed": False, "why": "", "orl": None, "hod": None, "vwap": None, "last": None,
           "short": None, "stopped": None, "re": None, "stopped2": None, "on": None}
    bars = sorted(tuple(b) for b in bars if b and b[0] is not None and 0 <= b[0] < 390)
    if now_min is not None:
        bars = [b for b in bars if b[0] < now_min]
    if not bars or not prev_close:
        return out
    op = bars[0][1]
    out["open"], out["last"] = op, bars[-1][4]
    out["gap"] = (op / prev_close - 1) * 100
    out["run20"] = (op / lo20 - 1) * 100 if lo20 else None
    if out["gap"] < rules["gap_pct"]:
        out["why"] = f"gap {out['gap']:+.1f}%, under {rules['gap_pct']:g}%"
    elif out["run20"] is not None and out["run20"] < rules["run20_pct"]:
        out["why"] = f"only +{out['run20']:.0f}% over its 20-session low close (needs {rules['run20_pct']:g}%+)"
    elif op < rules["min_price"]:
        out["why"] = f"opened ${op:.2f}, under ${rules['min_price']:g}"
    else:
        out["armed"] = True
    cv = cpv = 0.0
    vw, hod, hi = [], [], 0.0
    for m, o, h, l, c, v in bars:
        cv += v
        cpv += v * (h + l + c) / 3
        vw.append(cpv / cv if cv else c)
        hi = max(hi, h)
        hod.append(hi)
    out["hod"], out["vwap"] = hod[-1], vw[-1]
    n = rules["range_min"]
    rng = [b for b in bars if b[0] < n]
    if not rng or (now_min is not None and now_min < n) or (now_min is None and bars[-1][0] < n):
        return out                                        # the opening candle is not over yet
    out["orl"] = min(b[3] for b in rng)
    if not out["armed"]:
        return out
    last = rules["last_entry_min"]
    js = next((j for j, b in enumerate(bars) if n <= b[0] < last and b[3] < out["orl"]), None)
    if js is None:
        return out
    px, stop = min(bars[js][1], out["orl"]), hod[js - 1] if js else bars[js][2]
    if stop <= px:
        return out
    out["short"], out["on"] = {"min": bars[js][0], "px": px, "stop": stop, "orl": out["orl"]}, "short"
    jx = next((j for j in range(js + 1, len(bars)) if bars[j][2] >= stop), None)
    if jx is None:
        return out
    out["stopped"], out["on"] = bars[jx][0], None
    if not rules.get("reentry"):
        return out
    # the 5-minute candles that are over: the last bar of each, in order
    ends = {}
    for j, b in enumerate(bars):
        ends[b[0] // 5] = j
    prev_over = False
    for k in sorted(ends):
        if (k + 1) * 5 > last or (now_min is not None and now_min < (k + 1) * 5):
            break
        j = ends[k]
        c, w = bars[j][4], vw[j]
        if j > jx and c < w and prev_over and hod[j] > c:
            out["re"], out["on"] = {"min": (k + 1) * 5, "px": c, "stop": hod[j], "vwap": w}, "re"
            j2 = next((i for i in range(j + 1, len(bars)) if bars[i][2] >= hod[j]), None)
            if j2 is not None:
                out["stopped2"], out["on"] = bars[j2][0], None
            return out
        prev_over = c > w
    return out


def hhmm(minute):
    """minutes after 9:30 -> "10:30" """
    t = 570 + minute
    return f"{t // 60:02d}:{t % 60:02d}"
