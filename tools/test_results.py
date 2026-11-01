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


def trades(wb, title, rows):
    """every trade, a filter on each column; row 2 = the totals of what the filters show"""
    ws = wb.create_sheet(title[:31])
    cols = list(rows[0].keys())
    n = len(rows) + 3
    L_ = {c: get_column_letter(i + 1) for i, c in enumerate(cols)}
    tot = [("trades shown", f"=SUBTOTAL(103,{L_[cols[0]]}4:{L_[cols[0]]}{n})")]
    for c, lab, f in (("win", "winners %", "=ROUND(100*SUBTOTAL(101,{r}),1)"), ("R", "average R", "=ROUND(SUBTOTAL(101,{r}),2)"),
                      ("R", "total R", "=ROUND(SUBTOTAL(109,{r}),1)"), ("result_pct", "average %", "=ROUND(SUBTOTAL(101,{r}),2)"),
                      ("reached_3R", "reached +3R %", "=ROUND(100*SUBTOTAL(101,{r}),1)"), ("failed5", "failed in 5 days %", "=ROUND(100*SUBTOTAL(101,{r}),1)")):
        if c in L_:
            tot.append((lab, f.format(r=f"{L_[c]}4:{L_[c]}{n}")))
    ws.append([t[0] for t in tot])
    ws.append([t[1] for t in tot])
    ws.append(cols)
    for r in rows:
        ws.append([r.get(c) for c in cols])
    for c in ws[1]:
        c.font = Font(bold=True)
    for c in ws[2]:
        c.font = Font(bold=True, color="C00000")
    for c in ws[3]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="2F5597")
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.auto_filter.ref = f"A3:{get_column_letter(len(cols))}{n}"
    ws.freeze_panes = "C4"
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
    style(rm, [30, 16, 110, 24, 22])
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
    for name, label, rvcol in (("probe_launch_live", "Launch trades", ("rvol_pace_at_buy", "rvol_day")), ("probe_buypoints", "Buy point trades", ("rvol_day",))):
        d = data(name)
        if not d or not d.get("trades"):
            continue
        trades(wb, label, d["trades"])
        for rv in rvcol:
            grid(wb, f"{label.split()[0]} {'pace' if 'pace' in rv else 'RVOL'} x gap", d["trades"], rv)
    wb.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
