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
    ("probe_buypoints", "Buy points, bought at the breakout", "Our Launches buy points (base breakout, follow-through, flag, pop, retest, push, 21 EMA retest, undercut & reclaim) for 60 sessions after each launch, bought as the alerts fire (at the level when it breaks, a push at the open, the close for close signals); the risk the low of that day; your management. Each one saved with its RVOL (the day's volume / 20-day average) and gap.", "cmd buypoints"),
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


GRADES = (
    ("Launch grade (grade, launch_grade, grade_if_launch)",
     "From 4 ingredients of the launch day: (1) volume 3x+ its 20-day average, (2) a gap of 3%+, (3) a base breakout = closed above the previous "
     "20 days' high, (4) a 10%+ day.  A+ = volume 3x+, a gap of 6%+ and a base breakout, jumping from UNDER the 200 SMA (the day before) to over it "
     "(your 'go day').  A = volume 3x+ and a base breakout, with a 3%+ gap or a 10%+ day.  B = any two of the four.  C = the rest.  A delayed launch "
     "(a faded high-volume gap that held its base, then launched within 10 sessions) gets that gap day's volume and gap."),
    ("Breakout grade (the portal's breakout alerts)",
     "A = an early breakout (the 1st or 2nd since the launch, within 50 sessions of it) in a Leading theme with the volume building the 5 days "
     "before (1.1x+).  B = early plus one of those two.  C = the rest.  (Not a column in these sheets: the theme status isn't in the tests.)"),
    ("Watchlist grade (Watchlist tab)",
     "The trend and pullback grade of the Watchlist (MSF): not used in these tests."),
)
COLUMNS = (
    ("date / symbol", "the day of the buy (or of the signal) and the stock"),
    ("entry tactic / stop", "how it was bought and where the stop was (see each sheet's row 1)"),
    ("buy_point / bought", "the Launches trigger; bought = at the level, at the open or at the close"),
    ("pattern / base_pattern", "what the buy point came from (Base top, Flag line, an MSF pattern: Ascending triangle, Flat base, Cup with handle...) and the base's MSF name"),
    ("retest_with", "for a retest: the EMAs at the level with it (10 / 21 / 50 EMA, or no EMA)"),
    ("level", "the buy point price (the day before's buy point)"),
    ("day_closed", "for a level buy: did that day close over the level (a breakout) or back under it"),
    ("caution_within_0_5pct / double_breakout / third_try / flag_volume_dried", "the Launches tags as of that day's close (1 = yes): a breakout closing within 0.5% of the top; out of a falling line and the top the same day; the 3rd try of the top (ascending triangle); the volume dried up the 2 days before a flag break"),
    ("tight_days_before", "tight days just under the buy point the day before"),
    ("volume_building_5d", "the last 5 days' volume / the 50 days before (over 1 = building)"),
    ("rvol_day", "that day's volume / its 20-day average (known at the close)"),
    ("rvol_pace_at_buy", "launch days: the volume from 9:30 to the buy / the stock's usual volume by that time (what you see live)"),
    ("gap_pct / day_change_pct", "the open vs the day before's close; the close vs the day before's close"),
    ("close_in_range_pct", "where the day closed in its range (100 = at the high)"),
    ("vs_200sma_day_before_pct / from_under_200sma", "how far over (+) or under (-) the 200 SMA it was the day before"),
    ("adr_pct", "average daily range of the last 20 days"),
    ("leg / sessions_since_launch / launch_date", "which leg of the move, and how long after its launch"),
    ("closed_as", "launch days: what the day closed as (regular, power day, not a launch) - known only at 4 PM"),
    ("risk_pct", "from the buy down to the stop, in %"),
    ("result_pct / R / win", "the trade's result in %, in R (result / risk) and 1 = it made money"),
    ("reached_2R / 3R / 5R", "1 = it got to 2 / 3 / 5 times the risk at some point"),
    ("exit / days_held", "how it ended (stop, breakeven, daily 21 EMA close, still open) and how many days"),
    ("ran20 / failed5", "the stock ran 20%+ within 20 sessions / closed under that day's low within 5 sessions"),
    ("min5_bought", "1 = the 5-minute entry happened (the 5-minute high broke)"),
)


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


RV_B = ((None, 1), (1, 1.5), (1.5, 2), (2, 3), (3, 6), (6, None))
GAP_B = ((None, 0), (0, 2), (2, 5), (5, 8), (8, None))


def bname(lo, hi, unit=""):
    return f"under {hi}{unit}" if lo is None else f"{lo}{unit}+" if hi is None else f"{lo}-{hi}{unit}"


def inb(x, lo, hi):
    return x is not None and (lo is None or x >= lo) and (hi is None or x < hi)


TOT = (("win", "winners %", "=ROUND(100*SUBTOTAL(101,{r}),1)"), ("R", "average R", "=ROUND(SUBTOTAL(101,{r}),2)"),
       ("R", "total R", "=ROUND(SUBTOTAL(109,{r}),1)"), ("result_pct", "average %", "=ROUND(SUBTOTAL(101,{r}),2)"),
       ("reached_3R", "reached +3R %", "=ROUND(100*SUBTOTAL(101,{r}),1)"), ("failed5", "failed in 5 days %", "=ROUND(100*SUBTOTAL(101,{r}),1)"))
TOT_2 = tuple((p + c, lab_p + lab, f) for p, lab_p in (("min5_", "5-min: "), ("close_", "at close: ")) for c, lab, f in
              (("win", "winners %", "=ROUND(100*SUBTOTAL(101,{r}),1)"), ("R", "average R", "=ROUND(SUBTOTAL(101,{r}),2)"),
               ("R", "total R", "=ROUND(SUBTOTAL(109,{r}),1)"), ("result_pct", "average %", "=ROUND(SUBTOTAL(101,{r}),2)")))


TOT_3 = tuple((c, "as the alert: " + lab, f) for c, lab, f in TOT[:4]) + tuple(
    (p + c, lab_p + lab, f) for p, lab_p in (("close_", "at the close: "), ("min5_", "5-min entry: ")) for c, lab, f in
    (("win", "winners %", "=ROUND(100*SUBTOTAL(101,{r}),1)"), ("R", "average R", "=ROUND(SUBTOTAL(101,{r}),2)"),
     ("R", "total R", "=ROUND(SUBTOTAL(109,{r}),1)"), ("result_pct", "average %", "=ROUND(SUBTOTAL(101,{r}),2)")))


ENTRIES = ("Entry tactics: as the alert fires = at the level when it breaks (the open for a push, the close for close signals), stop the day's low; "
           "buy at the close = that day's close, stop the day's low; 5-min entry = over the 5-minute high and the buy point (close signals: the next "
           "morning), stop the 5-minute low. Your management. Row 3 = the totals of what you filter. Tags are as of that day's close.")
DESC = {
    "Launch trades": "LAUNCH DAYS, fair (no hindsight). ENTRY: the gap-up day, over both the 5-minute opening range high and +5%. STOP: the 5-minute low. "
                     "Then your management (+2R breakeven, 1/3 at +3R, 1/3 at +5R, runners on the daily 21 EMA close).",
    "Launch 5-min vs close": "LAUNCH DAYS (days that closed as launches). min5_ = ENTRY over the 5-minute high on the launch day, STOP the 5-minute low "
                             "(hindsight: only days that turned out to be launches). close_ = ENTRY at the launch day's close, STOP the day's low (fair). Your management.",
    "Launch - compare entries": "LAUNCH DAYS, one row per launch and ENTRY TACTIC: filter 'entry tactic' (5-min entry = over the 5-minute high, stop the "
                               "5-minute low, only days that turned out to be launches; buy at the close = the launch day's close, stop the day's low), then RVOL / gap. "
                               "Row 3 = the totals of what you filter. Your management.",
    "Buy points - compare entries": "BUY POINTS after the launch (all triggers), one row per buy point and ENTRY TACTIC: filter 'entry tactic', 'buy_point', "
                                   "then RVOL / gap. " + ENTRIES,
    "Buy point trades": "BUY POINTS after the launch. Plain columns (R, win, result_pct, risk_pct) = ENTRY as the alert fires (at the level when it breaks, "
                        "the open for a push, the close for close signals), STOP the day's low. close_ = ENTRY at that day's close, STOP the day's low. "
                        "min5_ = ENTRY over the 5-minute high (and the buy point), STOP the 5-minute low (close signals: the next morning). Your management.",
}
HEAD = {
    "Launch trades": {"risk_pct": "risk % (stop: 5-min low)", "R": "R (5-min entry, stop 5-min low)", "result_pct": "result % (5-min entry)", "win": "win (5-min entry)"},
    "Launch 5-min vs close": {"min5_risk_pct": "5-min entry: risk % (stop 5-min low)", "min5_R": "5-min entry: R", "min5_result_pct": "5-min entry: result %",
                              "min5_win": "5-min entry: win", "close_risk_pct": "close entry: risk % (stop day's low)", "close_R": "close entry: R",
                              "close_result_pct": "close entry: result %", "close_win": "close entry: win"},
    "Buy point trades": {"risk_pct": "alert entry: risk % (stop day's low)", "R": "alert entry: R", "result_pct": "alert entry: result %", "win": "alert entry: win",
                         "close_risk_pct": "close entry: risk % (stop day's low)", "close_R": "close entry: R", "close_result_pct": "close entry: result %",
                         "close_win": "close entry: win", "min5_risk_pct": "5-min entry: risk % (stop 5-min low)", "min5_R": "5-min entry: R",
                         "min5_result_pct": "5-min entry: result %", "min5_win": "5-min entry: win"},
}


TACTICS = {
    "launch": (("min5_", "5-min entry", "5-min low"), ("close_", "buy at the close", "day's low")),
    "buypoint": (("", "as the alert fires", "day's low"), ("close_", "buy at the close", "day's low"), ("min5_", "5-min entry", "5-min low")),
}
RESULT = ("risk_pct", "result_pct", "R", "win", "reached_3R", "exit")


def long_rows(rows, tactics):
    """one row per trade and entry tactic, so the tactic is a column to filter on"""
    out = []
    for r in rows:
        base = {k: v for k, v in r.items() if not k.startswith(("min5_", "close_")) and k not in RESULT + ("reached_2R", "reached_5R", "days_held",
                                                                                                       "ran20", "failed5", "min5_bought")}
        for pre, name, stop in tactics:
            if r.get(pre + "R") is None:
                continue
            x = dict(base)
            x.update({"entry tactic": name, "stop": stop})
            x.update({k: r.get(pre + k) for k in RESULT})
            out.append(x)
    return out


def tactic_grid(wb, title, rows):
    """each tactic's results by RVOL band and by gap band"""
    ws = wb.create_sheet(title[:31])
    tac = sorted({r["entry tactic"] for r in rows})
    for what, key, bands, unit in (("RVOL (the day's)", "rvol_day", RV_B, "x"), ("gap", "gap_pct", GAP_B, "%")):
        for stat in ("average R", "winners %", "average %", "trades"):
            ws.append([f"{stat} by {what}"] + tac)
            for c in ws[ws.max_row]:
                c.font = Font(bold=True)
            for lo, hi in bands + ((None, None),):
                line = [bname(lo, hi, unit) if (lo, hi) != (None, None) else "all"]
                for t in tac:
                    sel = [r for r in rows if r["entry tactic"] == t and r.get("R") is not None
                           and ((lo, hi) == (None, None) or inb(r.get(key), lo, hi))]
                    line.append(None if not sel else round(sum(r["R"] for r in sel) / len(sel), 2) if stat == "average R" else
                                round(100 * sum(r["win"] for r in sel) / len(sel)) if stat == "winners %" else
                                round(sum(r["result_pct"] for r in sel) / len(sel), 2) if stat == "average %" else len(sel))
                ws.append(line)
            ws.append([])
    ws.column_dimensions["A"].width = 30
    for i in range(2, 6):
        ws.column_dimensions[get_column_letter(i)].width = 20


def trades(wb, title, rows, spec=TOT):
    """every trade, a filter on each column; row 1 = what the entry and stop are, row 3 = the totals of what the filters show"""
    ws = wb.create_sheet(title[:31])
    ws.append([DESC.get(title, "")])
    ws["A1"].font = Font(bold=True, color="2F5597")
    cols = []
    for r in rows:
        for c in r:
            if c not in cols:
                cols.append(c)
    n = len(rows) + 4
    L_ = {c: get_column_letter(i + 1) for i, c in enumerate(cols)}
    tot = [("trades shown", f"=SUBTOTAL(103,{L_[cols[0]]}5:{L_[cols[0]]}{n})")]
    for c, lab, f in spec:
        if c in L_:
            tot.append((lab, f.format(r=f"{L_[c]}5:{L_[c]}{n}")))
    ws.append([t[0] for t in tot])
    ws.append([t[1] for t in tot])
    ws.append([HEAD.get(title, {}).get(c, c) for c in cols])
    for r in rows:
        ws.append([r.get(c) for c in cols])
    for c in ws[2]:
        c.font = Font(bold=True)
        c.alignment = Alignment(wrap_text=True, vertical="top")
    for c in ws[3]:
        c.font = Font(bold=True, color="C00000")
    for c in ws[4]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="2F5597")
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.auto_filter.ref = f"A4:{get_column_letter(len(cols))}{n}"
    ws.freeze_panes = "C5"
    for i in range(1, len(cols) + 1):
        ws.column_dimensions[get_column_letter(i)].width = 14


def grid(wb, title, rows, rv):
    """average R, trades and winners % for each RVOL band x gap band"""
    ws = wb.create_sheet(title[:31])
    gaps = [bname(lo, hi, "%") for lo, hi in GAP_B]
    for what in ("average R", "trades", "winners %", "total R"):
        ws.append([f"{what}: {rv} (rows) x gap (columns)"] + gaps + ["all gaps"])
        for c in ws[ws.max_row]:
            c.font = Font(bold=True)
        for rlo, rhi in RV_B + ((None, None),):
            line = [bname(rlo, rhi, "x") if (rlo, rhi) != (None, None) else "all"]
            for glo, ghi in GAP_B + ((None, None),):
                sel = [t for t in rows if (inb(t.get(rv), rlo, rhi) if (rlo, rhi) != (None, None) else t.get(rv) is not None)
                       and (inb(t.get("gap_pct"), glo, ghi) if (glo, ghi) != (None, None) else True)]
                if not sel:
                    line.append(None)
                elif what == "average R":
                    line.append(round(sum(t["R"] for t in sel) / len(sel), 2))
                elif what == "trades":
                    line.append(len(sel))
                elif what == "winners %":
                    line.append(round(100 * sum(t["win"] for t in sel) / len(sel)))
                else:
                    line.append(round(sum(t["R"] for t in sel), 1))
            ws.append(line)
        ws.append([])
    ws.column_dimensions["A"].width = 44
    for i in range(2, 9):
        ws.column_dimensions[get_column_letter(i)].width = 12


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
    rm.append([])
    rm.append(["HOW THE GRADES ARE MADE"])
    for a_, b_ in GRADES:
        rm.append([a_, "", b_])
    rm.append([])
    rm.append(["WHAT EACH COLUMN MEANS (trade sheets)"])
    for a_, b_ in COLUMNS:
        rm.append([a_, "", b_])
    style(rm, [30, 16, 110, 24, 22])
    for row in rm.iter_rows():
        if row[0].value in ("HOW THE GRADES ARE MADE", "WHAT EACH COLUMN MEANS (trade sheets)", "How to read"):
            row[0].font = Font(bold=True, color="2F5597", size=12)
    for row in rm.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    sm = wb.create_sheet("Summary")
    head = ["Test", "Group", "In plain words", "Trades", "Winners %", "Average result %", "Median result %", "Average R per trade",
            "Total R", "Reached +3R %", "Stopped out same day %", "Typical risk %", "Note"]
    sm.append(head)
    picks = [("probe_setups3", "ready_orh › all", "Ready, next-day 5-min high, exit A", ""),
             ("probe_setups3", "ready_orh › B_day_low_stop", "Ready, next-day 5-min high, stop under the day's low", ""),
             ("probe_setups3", "ready_orh › C_half_at_2R", "Ready, next-day 5-min high, half at +2R", ""),
             ("probe_pb1h", "all", "1-hour 21 EMA pullback, all", ""),
             ("probe_pb1h", "by_gap › gap 1-3%", "1-hour 21 EMA pullback, gap 1-3%", ""),
             ("probe_launch_orh", "managed › all", "Launch days, your management", "HINDSIGHT: upper bound"),
             ("probe_launch_orh", "managed › regular", "Launch days, regular", "HINDSIGHT"),
             ("probe_launch_orh", "bought_at_the_close", "the same launch days bought at their CLOSE, risk the day's low", "no hindsight: at 4 PM you know it's a launch"),
             ("probe_launch_live", "all", "ALL launch-day buys (what you could trade)", "no hindsight: this is the real result"),
             ("probe_launch_live", "closed_as_all_trades › regular", "split afterwards: the buys that closed as a regular launch", "you only know this at 4 PM, after the buy"),
             ("probe_launch_live", "closed_as_all_trades › not a launch", "split afterwards: the buys that did NOT close as a launch", "you only know this at 4 PM, after the buy"),
             ("probe_launch_live", "from_under_the_200sma › under the 200 SMA the day before", "…coming from under the 200 SMA", ""),
             ("probe_buypoints", "all", "ALL buy points (what you could trade)", "risk = the day's low; average R is pulled up by a few trades with a tiny risk: read average %"),
             ("probe_buypoints", "by_buy_point › base breakout", "base breakout (every cross of the base top)", ""),
             ("probe_buypoints", "by_buy_point › flag breakout", "flag breakout (every cross of the flag line)", ""),
             ("probe_buypoints", "by_buy_point › pop", "pop out of the consolidation", ""),
             ("probe_buypoints", "by_buy_point › retest", "retest held (bought at the close)", ""),
             ("probe_buypoints", "by_buy_point › push", "push out of the 21 EMA (bought at the open)", ""),
             ("probe_buypoints", "by_buy_point › 21 EMA retest", "21 EMA retest (bought at the close)", ""),
             ("probe_buypoints", "by_buy_point › 21 EMA undercut & reclaim", "21 EMA undercut & reclaim (bought at the close)", ""),
             ("probe_buypoints", "level_buys_by_close › closed as a breakout", "split afterwards: level buys whose day closed over the level", "you only know this at 4 PM, after the buy"),
             ("probe_buypoints", "level_buys_by_close › closed back under / no breakout", "split afterwards: level buys whose day closed back under", "you only know this at 4 PM, after the buy"),
             ("probe_earnings", "all", "Earnings-day high breakout", "")]
    for name, path, variant, note in picks:
        d = data(name)
        if not d:
            continue
        r = dict(rows_of(d)).get(path)
        if not r:
            continue
        title = next(t for n, t, *_ in TESTS if n == name)
        nt, w, av, ar = r.get("trades", r.get("n")), r.get("win"), r.get("avg_pct", r.get("avg")), r.get("avg_R")
        words = (f"{nt} trades; {w}% made money; on average {av:+}% a trade, " if None not in (nt, w, av) else "") \
            + (f"{ar:+} times the risk ({'a gain' if ar > 0 else 'a loss'} of {abs(ar)}R per trade)" if ar is not None else "")
        sm.append([title, variant, words, nt, w, av, r.get("med_pct", r.get("med")),
                   ar, r.get("total_R"), r.get("reached_3R"), r.get("stopped_same_day", r.get("stopped_same_day_pct")),
                   r.get("risk_med_pct"), note or None])
    style(sm, [26, 40, 56] + [11] * 9 + [24])
    for row in sm.iter_rows(min_row=2):
        row[2].alignment = Alignment(wrap_text=True, vertical="top")
    sm.append([])
    sm.append(["What the columns mean"])
    for a, b in (("Trades", "how many buys the test made"), ("Winners %", "of those, how many made money"),
                 ("Average / median result %", "the gain or loss per trade in %; the median is the middle trade"),
                 ("Average R per trade", "the result divided by the risk (buy to stop): +1R = made what you risked, -1R = full stop"),
                 ("Total R", "all trades added up, in R"), ("Reached +3R %", "how many got to 3 times the risk at some point"),
                 ("Stopped out same day %", "how many hit the stop on the day of the buy"),
                 ("Typical risk %", "the usual distance from the buy to the stop")):
        sm.append([a, b])
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
    d = data("probe_launch_orh")
    if d and d.get("trades") and any("close_R" in r for r in d["trades"]):
        lr = long_rows(d["trades"], TACTICS["launch"])
        trades(wb, "Launch - compare entries", lr)
        tactic_grid(wb, "Launch entries by RVOL, gap", lr)
    d = data("probe_buypoints")
    if d and d.get("trades") and any("close_R" in r for r in d["trades"]):
        br = long_rows(d["trades"], TACTICS["buypoint"])
        trades(wb, "Buy points - compare entries", br)
        tactic_grid(wb, "Buy pt entries by RVOL, gap", br)
        # one sheet per Launches trigger, the same layout as "Launch - compare entries"
        for k, short in (("base breakout", "Base breakout"), ("flag breakout", "Flag breakout"), ("pop", "Pop"), ("pattern pivot", "Pattern pivot"),
                         ("follow-through", "Follow-through"), ("retest", "Retest held"), ("push", "Push 21 EMA"),
                         ("21 EMA retest", "21 EMA retest"), ("21 EMA undercut & reclaim", "21 EMA undercut")):
            sel = [r for r in br if r["buy_point"] == k]
            if k == "pattern pivot":                       # the MSF patterns on their own sheets too (ascending triangle, flat base...)
                for pat in sorted({r.get("pattern") or "" for r in sel}):
                    ps = [r for r in sel if (r.get("pattern") or "") == pat]
                    if pat and len(ps) >= 30:
                        DESC[f"{pat[:18]} - entries"] = f"{pat.upper()} breakouts (an MSF pattern's pivot). " + ENTRIES
                        trades(wb, f"{pat[:18]} - entries", ps)
            if sel:
                DESC[f"{short} - entries"] = (f"{k.upper()} (a Launches trigger), one row per buy point and ENTRY TACTIC: filter 'entry tactic', then rvol_day, "
                                              "gap_pct, the pattern, retest_with (the EMAs with a retest: 10 / 21 / 50) and the tags (caution, double breakout, 3rd try = "
                                              "ascending triangle, flag volume dried, tight days before). " + ENTRIES)
                trades(wb, f"{short} - entries", sel)
    for name, label, rvcol in (("probe_launch_live", "Launch trades", ("rvol_pace_at_buy", "rvol_day")), ("probe_buypoints", "Buy point trades", ("rvol_day",))):
        d = data(name)
        if not d or not d.get("trades"):
            continue
        trades(wb, label, d["trades"], TOT_3 if name == "probe_buypoints" else TOT)
        for rv in rvcol:
            grid(wb, f"{label.split()[0]} {'pace' if 'pace' in rv else 'RVOL'} x gap", d["trades"], rv)
    wb.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
