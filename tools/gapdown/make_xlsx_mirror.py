#!/usr/bin/env python3
"""The gap-down short study with the gap-up rules mirrored, as a spreadsheet: the mirrored sets, every trade with its chart
facts of the evening before, the top winners of the two sets that held up.

  python3 make_xlsx_mirror.py trades_out.json features.json gaps_clean.json OUT.xlsx"""
import sys
out_path = sys.argv[4]
sys.argv = sys.argv[:4]
import mirror as M
from make_xlsx import sheet
from openpyxl import Workbook
from openpyxl.styles import Font
R, sel, F, G = M.R, M.sel, M.F, M.G
up = lambda d: (not d["u50"]) and d["u200"] is False
dn = lambda d: d["u50"] and d["u200"] is True
p1b = lambda d, r, t: up(d) and d["o_u50"] and d["o_u200"] is True and d["o_u1m"]
p1 = lambda d, r, t: -20 <= r["gap"] <= -5 and d["u50"] and d["o_u1m"] and d["o_u200"] is True and d["room3m"] is not None and d["room3m"] >= 5

SETS = [
    ("Every 5%+ gap-down (no chart rule)", lambda d, r, t: True),
    ("Gap 8%+ (no chart rule)", lambda d, r, t: r["gap"] <= -8),
    ("-- yesterday's close", None),
    ("Yesterday under the 50 EMA", lambda d, r, t: d["u50"]),
    ("Yesterday over the 50 EMA", lambda d, r, t: not d["u50"]),
    ("Yesterday under the 50 EMA and the 200 SMA (downtrend)", lambda d, r, t: dn(d)),
    ("Yesterday under the 50 EMA, over the 200 SMA", lambda d, r, t: d["u50"] and d["u200"] is False),
    ("Yesterday over the 50 EMA and the 200 SMA (uptrend)", lambda d, r, t: up(d)),
    ("Yesterday over the 50 EMA, under the 200 SMA", lambda d, r, t: not d["u50"] and d["u200"] is True),
    ("-- where the gap opens", None),
    ("Opens under the 1-month low", lambda d, r, t: d["o_u1m"]),
    ("Opens over the 1-month low", lambda d, r, t: not d["o_u1m"]),
    ("Opens under the 21-day closing low", lambda d, r, t: d["o_ucl21"]),
    ("Opens over the 21-day closing low", lambda d, r, t: not d["o_ucl21"]),
    ("Opens under the 3-month low", lambda d, r, t: d["o_u3m"] is True),
    ("Opens under the 52-week low", lambda d, r, t: d["o_u52w"] is True),
    ("Opens under the 200 SMA", lambda d, r, t: d["o_u200"] is True),
    ("Opens over the 200 SMA", lambda d, r, t: d["o_u200"] is False),
    ("-- room down to the 3-month low at the short price", None),
    ("Already under the 3-month low", lambda d, r, t: d["room3m"] is not None and d["room3m"] <= 0),
    ("0-5% over the 3-month low", lambda d, r, t: d["room3m"] is not None and 0 < d["room3m"] < 5),
    ("5-15% over the 3-month low", lambda d, r, t: d["room3m"] is not None and 5 <= d["room3m"] < 15),
    ("15%+ over the 3-month low", lambda d, r, t: d["room3m"] is not None and d["room3m"] >= 15),
    ("-- the gap-up plays mirrored", None),
    ("Mirror of play 1: yesterday under the 50 EMA, gap 5-20% opens under the 1-month low and the 200 SMA, 5%+ room to the 3-month low", p1),
    ("Mirror of play 1 without the room rule", lambda d, r, t: -20 <= r["gap"] <= -5 and d["u50"] and d["o_u1m"] and d["o_u200"] is True),
    ("Mirror of play 1b: yesterday over the 50 EMA and the 200 SMA, the gap opens under both and under the 1-month low", p1b),
    ("Mirror of play 1b, gap 5-20% only", lambda d, r, t: p1b(d, r, t) and -20 <= r["gap"] <= -5),
    ("Mirror of the skip: yesterday over the 50 EMA, under the 200 SMA (gap 5-20%)", lambda d, r, t: -20 <= r["gap"] <= -5 and not d["u50"] and d["u200"] is True),
    ("-- the uptrend stock (yesterday over the 50 EMA and the 200 SMA) by gap", None),
    ("Uptrend, gap 5-8%", lambda d, r, t: up(d) and r["gap"] > -8),
    ("Uptrend, gap 8%+", lambda d, r, t: up(d) and r["gap"] <= -8),
    ("Uptrend, gap 8%+, opens under the 50 EMA", lambda d, r, t: up(d) and r["gap"] <= -8 and d["o_u50"]),
    ("Uptrend, gap 8%+, opens still over the 50 EMA", lambda d, r, t: up(d) and r["gap"] <= -8 and not d["o_u50"]),
    ("Uptrend, opens under the 50 EMA and the 200 SMA (any gap)", lambda d, r, t: up(d) and d["o_u50"] and d["o_u200"] is True),
    ("Uptrend, gap 8%+, first candle green", lambda d, r, t: up(d) and r["gap"] <= -8 and t["color"] == "green"),
    ("Uptrend, gap 8%+, first candle red", lambda d, r, t: up(d) and r["gap"] <= -8 and t["color"] == "red"),
    ("-- the other trends with a gap of 8%+", None),
    ("Downtrend (under both), gap 8%+", lambda d, r, t: dn(d) and r["gap"] <= -8),
    ("Under the 50 EMA, over the 200 SMA, gap 8%+", lambda d, r, t: d["u50"] and d["u200"] is False and r["gap"] <= -8),
    ("Over the 50 EMA, under the 200 SMA, gap 8%+", lambda d, r, t: not d["u50"] and d["u200"] is True and r["gap"] <= -8),
]


def main():
    wb = Workbook()
    ws = wb.active
    ws.title = "Read me"
    lines = [
        "Gap-down short study, part 2: the gap-up rules mirrored for the short side (research only, nothing live)",
        "",
        "Same trades and rules as part 1: 5%+ gap-down, short the break of the first 3- / 5-minute candle's low, stop at the range high, out at the stop or the day's last price.",
        "New: each stock-day's chart the evening before, mirrored from the gap-up rules:",
        "  yesterday's close vs the 50 EMA and the 200 SMA; where the gap opens vs the 50 EMA, the 200 SMA, the 1-month low (lowest low of 21 sessions),",
        "  the 21-day closing low, the 3-month low (63 sessions), the 52-week low; the room from the short price down to the 3-month low.",
        "Ordinary days = without the 26 mornings when 50+ stocks gapped down at once (Apr 3 2025 alone made +697R of the plain short's +678R).",
        "",
        "What it shows: the straight mirror of play 1 (a weak stock gapping to new lows) does not work; the mirror of play 1b does:",
        "a stock that was over its 50 EMA and 200 SMA yesterday and gaps down. Best with a gap of 8%+, or opening under both averages and the 1-month low.",
    ]
    for i, t in enumerate(lines, 1):
        ws.cell(row=i, column=1, value=t)
    ws["A1"].font = Font(bold=True, size=13)
    ws.column_dimensions["A"].width = 150

    for n in ("3", "5"):
        rows = []
        for name, cond in SETS:
            if cond is None:
                rows.append([name.strip("- ").upper()])
                continue
            # the two rows without a chart rule: every trade, as in part 1 (one stock-day has no chart facts)
            ts = R.trades(n, "rh", gap=8 if name.startswith("Gap 8%+") else 5) if "(no chart rule)" in name else sel(n, "rh", cond)
            if not ts:
                rows.append([name, 0])
                continue
            s, y = R.stats(ts), R.years(ts)
            ex = R.stats([t for t in ts if t[0].split()[0] not in M.MD])
            rows.append([name, s["n"], s["win"], s["avg"], s["total"], s["net_avg"], *[(y[k]["total"] if k in y else None) for k in ("2023", "2024", "2025", "2026")],
                         sum(1 for v in y.values() if v["total"] > 0), ex["n"] if ex else 0, ex["win"] if ex else None, ex["avg"] if ex else None, ex["total"] if ex else None])
        sheet(wb, f"Mirrored rules {n}-min", ["Set (stop at the range high)", "Trades", "Win %", "Avg R", "Total R", "Avg R after costs", "2023 R", "2024 R", "2025 R", "2026 R",
                                               "Years up (of 4)", "Ordinary days: trades", "Ordinary days: win %", "Ordinary days: avg R", "Ordinary days: total R"],
              rows, widths={"Set (stop at the range high)": 95}, r_cols=(4, 5, 6, 7, 8, 9, 10, 14, 15))

    for n in ("3", "5"):
        rows = []
        for key, row in sorted(R.ROWS.items()):
            tr = row.get(n)
            if row["o"] < 10 or not tr or "t" not in tr:
                continue
            st = tr.get("rh")
            d = M.facts(key, row, tr)
            f, g = F.get(key), G.get(key)
            if not d or not st:
                continue
            day, sym = key.split()
            yn = lambda v: "" if v is None else ("yes" if v else "no")
            tag = ("play 1b mirror" if p1b(d, row, tr) else "uptrend, gap 8%+" if up(d) and row["gap"] <= -8 else "play 1 mirror" if p1(d, row, tr) else "")
            trend = ("uptrend" if up(d) else "downtrend" if dn(d) else "under 50 EMA, over 200 SMA" if d["u50"] and d["u200"] is False
                     else "over 50 EMA, under 200 SMA" if d["u200"] is True else "no 200 SMA yet")
            rows.append([day, sym, row["gap"], f["pc"], g["o"], trend, f["ema50"], f["sma200"], f["low21"], f["clow21"], f["low63"],
                         yn(d["o_u50"]), yn(d["o_u200"]), yn(d["o_u1m"]), yn(d["o_ucl21"]), yn(d["o_u3m"]),
                         None if d["room3m"] is None else round(d["room3m"], 1), tr["color"], tr["rvol"], tr["t"], tr["entry"], st["stop"], st["risk_pct"], st["exit"],
                         st["r"] if st["risk_pct"] >= R.MIN_RISK else None, tag, "yes" if day in M.MD else ""])
        sheet(wb, f"Trades {n}-min", ["Date", "Ticker", "Gap %", "Close before", "Open", "Trend yesterday", "50 EMA", "200 SMA", "1-month low", "21-day closing low", "3-month low",
                                      "Opens under 50 EMA", "Opens under 200 SMA", "Opens under 1-month low", "Opens under 21-day closing low", "Opens under 3-month low",
                                      "Short price over 3-month low %", "First candle", "Early rel vol", "Short at (time)", "Short price", "Stop (range high)", "Stop distance %",
                                      "Exit", "R", "Set", "Market-wide day"], rows, widths={"Trend yesterday": 26, "Set": 18}, r_cols=(25,))

    rows = []
    for label, cond in (("Mirror of play 1b", p1b), ("Uptrend yesterday, gap 8%+", lambda d, r, t: up(d) and r["gap"] <= -8)):
        for key, row, tr, st in sorted(sel("3", "rh", cond), key=lambda t: -t[3]["r"])[:30]:
            day, sym = key.split()
            f, g = F[key], G[key]
            rows.append([label, day, sym, row["gap"], f["pc"], f["ema50"], f["sma200"], f["low21"], g["o"], tr["t"], tr["entry"], st["stop"], st["exit"],
                         round(100 * (tr["entry"] - st["exit"]) / tr["entry"], 1), st["r"]])
    sheet(wb, "Top winners", ["Set (3-min range, stop range high)", "Date", "Ticker", "Gap %", "Close before", "50 EMA", "200 SMA", "1-month low", "Open", "Short at (time)",
                              "Short price", "Stop", "Day's last price", "Move %", "R"], rows, widths={"Set (3-min range, stop range high)": 30}, r_cols=(15,))
    wb.save(out_path)
    print("saved", out_path)


if __name__ == "__main__":
    main()
