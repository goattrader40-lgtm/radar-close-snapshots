#!/usr/bin/env python3
"""The gap-down day's plays as a spreadsheet: every scenario by gap size / earnings / trend, and the trades of the two plays.

  python3 make_xlsx_part4.py trades_out.json features.json gaps_clean.json reasons.json scen.json OUT.xlsx"""
import sys
out_path = sys.argv[6]
sys.argv = sys.argv[:6]
import scen_report as S
from make_xlsx import sheet
from openpyxl import Workbook
from openpyxl.styles import Font
R, up = S.R, S.up


def main():
    wb = Workbook()
    ws = wb.active
    ws.title = "Read me"
    lines = [
        "Gap-down short study, part 4: the scenarios side by side and two plays (research only, nothing live)",
        "",
        "5%+ gap-down days, Jan 2023 - Nov 2026, 1-minute bars. Out at the stop or the day's last price. R = (short price - exit) / (stop - short price).",
        "Earnings day = results filed (SEC 8-K item 2.02) between the close before and the gap day. Strong = yesterday's close over the 50 EMA and the 200 SMA.",
        "Ordinary days = without the 26 mornings when 50+ stocks gapped down at once (Apr 3 2025 alone made +697R on the plain short).",
        "",
        "PLAY 1, the earnings breakdown: an earnings gap-down of 8%+. Short the break of the first 3-minute candle's low (also when the price pops over that candle's high first",
        "   and breaks the low later). Stop: that candle's high. Out at the close. Best when the stock was strong yesterday.",
        "PLAY 2, the retest short: the same day, once the opening low is broken. A 5-minute candle pops back to VWAP (staying under the first candle's high); that candle or one of",
        "   the next two closes red back under VWAP: short at that close, before 10:00 for choice. Stop: the pop's high. Out at the close.",
        "Gap 5-8%: no scenario held up outside the market-wide days, with or without earnings.",
        "Limits: no costs, no borrow; a stock 10%+ under its close before only fills a short on an uptick; today's listings only.",
    ]
    for i, t in enumerate(lines, 1):
        ws.cell(row=i, column=1, value=t)
    ws["A1"].font = Font(bold=True, size=13)
    ws.column_dimensions["A"].width = 165

    rows = []
    kinds = S.NAMES + [("play2", "PLAY 2. The opening low broken, the pop to VWAP (under the range high) fails before 11:00")]
    for kind, name in kinds:
        ts = S.play2() if kind == "play2" else S.trades(kind)
        rows.append([name])
        for lab, cond in S.SUBSETS:
            sub = [t for t in ts if cond(t[2])]
            st = S.stat(sub)
            if not st or st["n"] < 25:
                rows.append(["   " + lab, len(sub)])
                continue
            rows.append(["   " + lab, st["n"], round(st["win"], 1), round(st["avg"], 3), round(st["total"], 1), st["ord_n"], round(st["ord_avg"], 3), round(st["ord_total"], 1),
                         *[round(v, 1) for v in st["years"]], sum(1 for v in st["years"] if v > 0), round(st["risk"], 2), round(st["stopped"], 0)])
    sheet(wb, "Scenarios", ["Scenario / set", "Trades", "Win %", "Avg R", "Total R", "Ordinary days: trades", "Ordinary days: avg R", "Ordinary days: total R",
                            "2023 R", "2024 R", "2025 R", "2026 R", "Years up (of 4)", "Median stop distance %", "Stopped %"],
          rows, widths={"Scenario / set": 80}, r_cols=(4, 5, 7, 8, 9, 10, 11, 12))

    yn = lambda v: "yes" if v else ""
    rows = []
    for key, row, d, t in sorted((x for x in S.trades("orb") if x[2]["earn"] == 1 and x[2]["gap"] <= -8), key=lambda x: x[0]):
        day, sym = key.split()
        rows.append([day, sym, row["gap"], yn(up(d)), yn(S.popped((key, row, d, t))), row["pc"], row["3"]["rlo"], row["3"]["rhi"], t["t"], t["entry"], t["stop"], t["risk_pct"],
                     t["exit"], "stop" if t["stopped"] else "close", round(100 * (t["entry"] - t["exit"]) / t["entry"], 1), t["r"]])
    sheet(wb, "Play 1 trades", ["Date", "Ticker", "Gap %", "Strong yesterday", "Popped over the range high first", "Close before", "First candle low", "First candle high",
                                "Short at (time)", "Short price", "Stop", "Stop distance %", "Exit", "Exit by", "Move %", "R"], rows, r_cols=(15, 16))
    rows = []
    for key, row, d, t in sorted((x for x in S.play2() if x[2]["earn"] == 1 and x[2]["gap"] <= -8), key=lambda x: x[0]):
        day, sym = key.split()
        r3 = row["3"]
        rows.append([day, sym, row["gap"], yn(up(d)), row["pc"], r3["t"], r3["rlo"], r3["rhi"], t["t"], t["entry"], t["stop"], t["risk_pct"], t["exit"],
                     "stop" if t["stopped"] else "close", round(100 * (t["entry"] - t["exit"]) / t["entry"], 1), t["r"]])
    sheet(wb, "Play 2 trades", ["Date", "Ticker", "Gap %", "Strong yesterday", "Close before", "Opening low broke at", "First candle low", "First candle high",
                                "Short at (time, the 5-min close)", "Short price", "Stop (the pop's high)", "Stop distance %", "Exit", "Exit by", "Move %", "R"], rows, r_cols=(15, 16))
    wb.save(out_path)
    print("saved", out_path)


if __name__ == "__main__":
    main()
