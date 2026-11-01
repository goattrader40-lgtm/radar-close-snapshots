#!/usr/bin/env python3
"""Every test's results in one spreadsheet for the user (tools/test-results.xlsx), from the radar-data branch.

  git fetch -q origin +refs/heads/radar-data:refs/remotes/origin/radar-data
  python3 tools/test_results.py            # rebuild after a new test

Sheets: Read me (what each test is, its rules and caveats), Summary (one line per test and variant), then one sheet per
test with every split it reports.
"""
import json, os, subprocess

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tools", "test-results.xlsx")

TESTS = [
    ("probe_catalyst", "2-year check", "Launches buy points after the launch (breakouts, flags, pops, retests, 21 EMA entries...) bought at the close: ran 10% / 20% within 20 sessions, failed = closed under that day's low within 5 sessions. Also the launch-day opening-range trades of the launches (hindsight: the launch is known at the close).", "cmd catalyst"),
    ("probe_setups3", "3-SETUPS check", "The Watchlist 3-SETUPS (Triggered today / Ready / Setting up) on rebuilt feeder lists. Triggered bought at the close; Ready bought the next day at the trigger; ready_orh = Ready bought the next day on the 5-minute opening range high, three exits (A stop at the 5-minute low + 21 EMA close, B stop under the day's low, C half at +2R and breakeven) and the splits.", "cmd setups3"),
    ("probe_pb1h", "1-hour 21 EMA pullback", "Uptrend (10 > 21 > 50 EMA, a new 20-day high in the last 10 sessions, at most 50% over the 200 SMA, over it, 30%+ over the 52-week low), ADR 4%+, $30M / 700K a day, $700M+ market cap. A day closing under the 1-hour 21 EMA, the next day gaps up with the 5-minute opening range over that EMA: buy the 5-minute high, risk the 5-minute low; +2R breakeven, 1/3 at +3R, 1/3 at +5R, runners on the daily 21 EMA close.", "cmd pb1h"),
    ("probe_launch_orh", "Launch days, WITH HINDSIGHT", "Launch days (regular, power, reversal, catalyst) bought on the 5-minute opening range high, risk the 5-minute low. Uses days known to close as launches: an upper bound, NOT tradable as is. managed = your rules; simple = the 5-minute low stop and the daily 21 EMA close.", "cmd launchorh"),
    ("probe_launch_live", "Launch days, fair (no hindsight)", "Every stock on the launch watch list (from 25% under to 28% over the 200 SMA, 50% for 8%+ gaps, liquid, ADR 3.5%+, no launch in 20 sessions) that gaps up and trades over both the 5-minute high and +5%: bought there, risk the 5-minute low, your management. Split by what the day closed as, gap, buy time, coming from under the 200 SMA, volume pace.", "cmd launchlive"),
    ("probe_earnings", "Earnings-day high breakout", "An earnings day (company earnings news) that closed over its 1-month high, over the 200 SMA, 30%+ over the 52-week low, liquid ($10+, $30M and 700K a day, $700M+ market cap, ADR 4%+); a later day (within 10 sessions) breaking the earnings-day high: bought over both the 5-minute high and the earnings-day high, risk the 5-minute low, your management.", "cmd earnings"),
]

METRIC_HINTS = {"n", "trades", "setups", "days"}
LABELS = {"n": "count", "trades": "trades", "setups": "setups", "win": "winners %", "avg": "average %", "avg_pct": "average %",
          "med": "median %", "med_pct": "median %", "avg_R": "average R", "med_R": "median R", "total_R": "total R",
          "ran10": "ran 10%+ %", "ran20": "ran 20%+ %", "ran50": "ran 50%+ %", "fail5": "failed in 5 days %", "med20": "median after 20 days %",
          "reached_2R": "reached +2R %", "reached_3R": "reached +3R %", "reached_5R": "reached +5R %",
          "stopped_same_day": "stopped same day %", "stopped_same_day_pct": "stopped same day %", "broke_orh_pct": "broke the 5-min high %",
          "risk_med_pct": "typical risk %", "days_med": "typical days held", "C_win": "half-at-2R winners %", "C_avg": "half-at-2R average %",
          "took_half_at_2R_pct": "took half at 2R %", "hit_next_day_pct": "trigger hit next day %", "became_pct": "became Ready/Triggered %"}


def data(name):
    try:
        return json.loads(subprocess.run(["git", "show", f"origin/radar-data:{name}.json"], cwd=ROOT, check=True,
                                         capture_output=True, text=True).stdout)
    except Exception:
        return None


def rows_of(d, path=""):
    """every dict with result numbers, flattened: (path, {metric: value})"""
    out = []
    if not isinstance(d, dict):
        return out
    if METRIC_HINTS & set(d) and any(isinstance(v, (int, float)) for v in d.values()):
        vals = {k: v for k, v in d.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
        if isinstance(d.get("exits"), dict):
            vals.update({"exit: " + k: v for k, v in d["exits"].items()})
        out.append((path, vals))
    for k, v in d.items():
        if isinstance(v, dict) and k not in ("exits", "check"):
            out += rows_of(v, (path + " › " if path else "") + str(k))
    return out


def style(ws, widths):
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="2F5597")
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "B2"
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def main():
    wb = Workbook()
    rm = wb.active
    rm.title = "Read me"
    rm.append(["Test", "Sheet", "What it tests", "Period", "Rerun with (radar-tools.yml)"])
    for name, title, what, cmd in TESTS:
        d = data(name)
        rm.append([title, name.replace("probe_", ""), what, f"{d.get('first')} to {d.get('last')}" if d and "first" in d else "not run yet", cmd])
    rm.append([])
    rm.append(["How to read", "", "R = the trade's result divided by its risk (entry to stop). winners % = trades that made money. "
               "Your management = +2R stop to breakeven, 1/3 sold at +3R, 1/3 at +5R, runners out on a daily close under the 21 EMA "
               "or at breakeven. When one bar touches both the stop and a target, the stop counts first (the safe side). "
               "Costs and slippage are not included.", "", ""])
    style(rm, [30, 16, 110, 24, 22])
    for row in rm.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    sm = wb.create_sheet("Summary")
    head = ["Test", "Variant", "trades", "winners %", "average %", "median %", "average R", "total R", "reached +3R %", "stopped same day %", "typical risk %", "note"]
    sm.append(head)
    picks = [("probe_setups3", "ready_orh › all", "Ready, next-day 5-min high, exit A", ""),
             ("probe_setups3", "ready_orh › B_day_low_stop", "Ready, next-day 5-min high, stop under the day's low", ""),
             ("probe_setups3", "ready_orh › C_half_at_2R", "Ready, next-day 5-min high, half at +2R", ""),
             ("probe_pb1h", "all", "1-hour 21 EMA pullback, all", ""),
             ("probe_pb1h", "by_gap › gap 1-3%", "1-hour 21 EMA pullback, gap 1-3%", ""),
             ("probe_launch_orh", "managed › all", "Launch days, your management", "HINDSIGHT: upper bound"),
             ("probe_launch_orh", "managed › regular", "Launch days, regular", "HINDSIGHT"),
             ("probe_launch_live", "all", "Launch candidates, fair", "no hindsight"),
             ("probe_launch_live", "closed_as_all_trades › regular", "…that closed as a regular launch", "known only at the close"),
             ("probe_launch_live", "closed_as_all_trades › not a launch", "…that did not close as a launch", ""),
             ("probe_launch_live", "from_under_the_200sma › under the 200 SMA the day before", "…coming from under the 200 SMA", ""),
             ("probe_earnings", "all", "Earnings-day high breakout", "")]
    for name, path, variant, note in picks:
        d = data(name)
        if not d:
            continue
        r = dict(rows_of(d)).get(path)
        if not r:
            continue
        title = next(t for n, t, *_ in TESTS if n == name)
        sm.append([title, variant, r.get("trades", r.get("n")), r.get("win"), r.get("avg_pct", r.get("avg")), r.get("med_pct", r.get("med")),
                   r.get("avg_R"), r.get("total_R"), r.get("reached_3R"), r.get("stopped_same_day", r.get("stopped_same_day_pct")),
                   r.get("risk_med_pct"), note])
    style(sm, [28, 52] + [12] * 9 + [26])
    for name, title, what, cmd in TESTS:
        d = data(name)
        if not d or "error" in d:
            continue
        rows = rows_of(d)
        cols = []
        for _, v in rows:
            for k in v:
                if k not in cols:
                    cols.append(k)
        ws = wb.create_sheet(name.replace("probe_", "")[:31])
        ws.append(["split"] + [LABELS.get(k, k) for k in cols])
        for path, v in rows:
            ws.append([path or "all"] + [v.get(k) for k in cols])
        style(ws, [62] + [13] * len(cols))
    wb.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
