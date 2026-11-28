#!/usr/bin/env python3
"""The gap-down short study, part 3, as a spreadsheet: the sets ranked, every trade with its earnings flag, trend, % move and
furthest move, and the biggest moves by %.

  python3 make_xlsx_part3.py trades_out.json features.json gaps_clean.json reasons.json OUT.xlsx"""
import sys
out_path = sys.argv[5]
sys.argv = sys.argv[:5]
import part3 as P
from make_xlsx import sheet
from openpyxl import Workbook
from openpyxl.styles import Font
M, R, RS, F, G, up, dn, p1b = P.M, P.R, P.RS, P.M.F, P.M.G, P.up, P.dn, P.p1b
earn = lambda key: RS.get(key, {}).get("earn")

SETS = [
    ("1. THE GAP-UP RULES MIRRORED", None, None),
    ("Mirror of play 1b: strong yesterday (over the 50 EMA and 200 SMA), the gap opens under both and the 1-month low", p1b, "any"),
    ("Strong yesterday, gap 8%+", lambda d, r, t: up(d) and r["gap"] <= -8, "any"),
    ("Strong yesterday, gap 8%+, opens under the 50 EMA", lambda d, r, t: up(d) and r["gap"] <= -8 and d["o_u50"], "any"),
    ("Opens under the 21-day closing low (alone)", lambda d, r, t: d["o_ucl21"], "any"),
    ("Opens under the 1-month low (alone)", lambda d, r, t: d["o_u1m"], "any"),
    ("Opens under the 3-month low (alone)", lambda d, r, t: d["o_u3m"] is True, "any"),
    ("Weak yesterday (under the 50 EMA)", lambda d, r, t: d["u50"], "any"),
    ("Mirror of play 1: weak yesterday, gap 5-20% opens under the 1-month low and 200 SMA, 5%+ room to the 3-month low",
     lambda d, r, t: -20 <= r["gap"] <= -5 and d["u50"] and d["o_u1m"] and d["o_u200"] is True and d["room3m"] is not None and d["room3m"] >= 5, "any"),
    ("2. EARNINGS DAYS", None, None),
    ("Earnings day, every 5%+ gap", lambda d, r, t: True, 1),
    ("Earnings day, gap 5-8%", lambda d, r, t: r["gap"] > -8, 1),
    ("Earnings day, gap 8%+", lambda d, r, t: r["gap"] <= -8, 1),
    ("Earnings day, strong yesterday, gap 8%+   <-- the one to trade", lambda d, r, t: up(d) and r["gap"] <= -8, 1),
    ("Earnings day, mirror of play 1b", p1b, 1),
    ("Earnings day, weak yesterday (under both), gap 8%+", lambda d, r, t: dn(d) and r["gap"] <= -8, 1),
    ("NOT an earnings day, every 5%+ gap", lambda d, r, t: True, 0),
    ("NOT an earnings day, gap 8%+", lambda d, r, t: r["gap"] <= -8, 0),
    ("NOT an earnings day, strong yesterday, gap 8%+", lambda d, r, t: up(d) and r["gap"] <= -8, 0),
    ("Foreign companies (earnings day not known), every 5%+ gap", lambda d, r, t: True, None),
    ("FOR REFERENCE", None, None),
    ("Every 5%+ gap-down, no rule", lambda d, r, t: True, "any"),
    ("Gap 8%+, no other rule", lambda d, r, t: r["gap"] <= -8, "any"),
]


def pick(n, cond, e):
    return M.sel(n, "rh", cond) if e == "any" else P.earn_sel(n, "rh", cond, e)


def main():
    wb = Workbook()
    ws = wb.active
    ws.title = "Read me"
    lines = [
        "Gap-down short study, part 3: earnings days, other exits, and how far gap-downs move (research only, nothing live)",
        "",
        "Same trades as parts 1 and 2: 5%+ gap-down, short the break of the first 3-minute candle's low, stop at the range high, out at the stop or the day's last price.",
        "Earnings day = the company filed its results (SEC 8-K item 2.02) between the close of the session before and the end of the gap day. Foreign companies file no 8-Ks: not known.",
        "Strong yesterday = yesterday's close over the 50 EMA and the 200 SMA.  Ordinary days = without the 26 mornings when 50+ stocks gapped down at once.",
        "Move % = from the short price to the exit.  Furthest move % = the lowest price reached before the stop or the close, from the short price.",
        "",
        "What it shows: earnings-day gap-downs work every year, the others lose outside the April 2025 crash. Best: an earnings gap-down of 8%+ in a stock that was strong yesterday.",
        "Other exits (targets, a time of day) were no better than the close; holding past the close with the EP exits mirrored adds R only on that best set.",
        "Limit: 369 of its 424 trades were already 10%+ under the close before at the short price, where the uptick rule only lets a short fill on an uptick.",
    ]
    for i, t in enumerate(lines, 1):
        ws.cell(row=i, column=1, value=t)
    ws["A1"].font = Font(bold=True, size=13)
    ws.column_dimensions["A"].width = 160

    rows = []
    for name, cond, e in SETS:
        if cond is None:
            rows.append([name])
            continue
        # the two reference rows: every trade, as in part 1 (one stock-day has no chart facts)
        ts = (R.trades("3", "rh", gap=8 if name.startswith("Gap 8%+") else 5) if name in ("Every 5%+ gap-down, no rule", "Gap 8%+, no other rule") else pick("3", cond, e))
        if not ts:
            rows.append([name, 0])
            continue
        s, y = R.stats(ts), R.years(ts)
        ex = R.stats([t for t in ts if t[0].split()[0] not in M.MD])
        rows.append([name, s["n"], s["win"], s["avg"], s["total"], s["net_avg"], *[(y[k]["total"] if k in y else None) for k in ("2023", "2024", "2025", "2026")],
                     sum(1 for v in y.values() if v["total"] > 0), ex["n"] if ex else 0, ex["avg"] if ex else None, ex["total"] if ex else None])
    sheet(wb, "Ranked sets", ["Set (3-min range, stop range high, out at the close)", "Trades", "Win %", "Avg R", "Total R", "Avg R after costs", "2023 R", "2024 R", "2025 R", "2026 R",
                              "Years up (of 4)", "Ordinary days: trades", "Ordinary days: avg R", "Ordinary days: total R"],
          rows, widths={"Set (3-min range, stop range high, out at the close)": 100}, r_cols=(4, 5, 6, 7, 8, 9, 10, 13, 14))

    rows = []
    for key, row, tr, st in sorted(R.trades("3", "rh"), key=lambda t: t[0]):
        d = M.facts(key, row, tr)
        if not d:
            continue
        day, sym = key.split()
        f, g, e = F[key], G[key], earn(key)
        trend = ("strong" if up(d) else "weak (under both)" if dn(d) else "under 50 EMA, over 200 SMA" if d["u50"] and d["u200"] is False
                 else "over 50 EMA, under 200 SMA" if d["u200"] is True else "no 200 SMA yet")
        tag = ("earnings + strong + gap 8%+" if e == 1 and up(d) and row["gap"] <= -8 else "")
        rows.append([day, sym, row["gap"], "yes" if e == 1 else "no" if e == 0 else "not known", trend, "yes" if p1b(d, row, tr) else "", f["pc"], g["o"], f["ema50"], f["sma200"],
                     tr["color"], tr["rvol"], tr["t"], tr["entry"], st["stop"], st["risk_pct"], st["exit"], "stop" if st["stopped"] else "close",
                     round(100 * (tr["entry"] - st["exit"]) / tr["entry"], 1), st["ox"]["mfe"], st["r"], round(100 * (st["exit"] / row["pc"] - 1), 1), tag,
                     "yes" if day in M.MD else ""])
    sheet(wb, "Trades 3-min", ["Date", "Ticker", "Gap %", "Earnings day", "Trend yesterday", "Play 1b mirror", "Close before", "Open", "50 EMA", "200 SMA", "First candle", "Early rel vol",
                               "Short at (time)", "Short price", "Stop (range high)", "Stop distance %", "Exit", "Exit by", "Move %", "Furthest move %", "R",
                               "Exit vs the close before %", "Set", "Market-wide day"], rows, widths={"Trend yesterday": 26, "Set": 28}, r_cols=(19, 21))

    rows = []
    for label, ts in (("Every trade", R.trades("3", "rh")), ("Earnings + strong yesterday + gap 8%+", P.earn_sel("3", "rh", lambda d, r, t: up(d) and r["gap"] <= -8, 1))):
        for key, row, tr, st in sorted(ts, key=lambda t: -(t[2]["entry"] - t[3]["exit"]) / t[2]["entry"])[:40]:
            day, sym = key.split()
            e = earn(key)
            rows.append([label, day, sym, row["gap"], "yes" if e == 1 else "no" if e == 0 else "not known", row["pc"], tr["t"], tr["entry"], st["stop"], st["exit"],
                         round(100 * (tr["entry"] - st["exit"]) / tr["entry"], 1), st["r"], round(100 * (st["exit"] / row["pc"] - 1), 1)])
    sheet(wb, "Biggest moves", ["Set", "Date", "Ticker", "Gap %", "Earnings day", "Close before", "Short at (time)", "Short price", "Stop", "Day's last price", "Move %", "R",
                                "Close vs the close before %"], rows, widths={"Set": 36}, r_cols=(11, 12))
    wb.save(out_path)
    print("saved", out_path)


if __name__ == "__main__":
    main()
