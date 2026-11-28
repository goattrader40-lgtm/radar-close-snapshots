#!/usr/bin/env python3
"""The gap-down short study as a spreadsheet: the rules, the 180 combinations, every trade, the top winners.

  python3 make_xlsx.py trades_out.json OUT.xlsx"""
import sys
if __name__ == "__main__":
    out_path = sys.argv[2]
    sys.argv = sys.argv[:2]
import report as R                       # reads trades_out.json (sys.argv[1])
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

HEAD = PatternFill("solid", fgColor="1F2937")
GOOD, BAD = PatternFill("solid", fgColor="D1FAE5"), PatternFill("solid", fgColor="FEE2E2")


def sheet(wb, title, header, rows, widths=None, r_cols=()):
    ws = wb.create_sheet(title)
    ws.append(header)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = HEAD
        c.alignment = Alignment(wrap_text=True, vertical="center")
    for row in rows:
        ws.append(row)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for i, h in enumerate(header, 1):
        ws.column_dimensions[get_column_letter(i)].width = (widths or {}).get(h, max(9, min(22, len(str(h)) + 2)))
    for ci in r_cols:
        for row in ws.iter_rows(min_row=2, min_col=ci, max_col=ci):
            c = row[0]
            if isinstance(c.value, (int, float)):
                c.fill = GOOD if c.value > 0 else BAD if c.value < 0 else PatternFill()
    return ws


def main():
    wb = Workbook()
    ws = wb.active
    ws.title = "Read me"
    days = [k for k, r in R.ROWS.items() if r["o"] >= 10]
    base = R.stats(R.trades("3", "rh"))
    pick = R.stats(R.trades("3", "rh", gap=8))
    lines = [
        "Gap-down short study: shorting the break of the opening-range low on 5%+ gap-down days (research only, nothing live)",
        "",
        f"Data: {len(days)} stock-days, {min(k.split()[0] for k in days)} to {max(k.split()[0] for k in days)}, 1-minute bars from Alpaca (consolidated tape).",
        "Universe: gap of -5% or more at the open; the close before $10+ and the open $10+; 20-day average volume 700K+ shares and $20M+ a day; market cap $700M+.",
        "Range: the first 3-minute (or 5-minute) candle. Entry: sold short when a later 1-minute bar trades under the range low, at the range low (at the bar's open if it opens under it).",
        "Stop: the range high, or the day's high at the moment of the entry. Exit: the stop, else the day's last price. R = (entry - exit) / (stop - entry).",
        "Left out: a stop closer than 0.5% of the price (a late open's one-print candle; not tradable).",
        "First candle: red = the range candle closed under its open, green = over it.",
        "Early rel vol: the range's volume / the stock's normal volume for those minutes (20-day average day x its usual share in the first 5 minutes).",
        "After costs: 0.1% of the price taken off every trade (slippage and fees, both sides together).",
        "Market-wide day: 50+ stocks of the universe gapped down 5%+ that morning (26 days).",
        "",
        f"The plain short (3-minute range, stop at the range high, every gap): {base['n']} trades, {base['win']}% won, {base['avg']:+.3f}R a trade, {base['total']:+.0f}R in all.",
        "  ... but +697R of it is one day (Apr 3 2025). Without the 26 market-wide days: +0.013R a trade.",
        f"The one that held up every year (gap 8%+): {pick['n']} trades, {pick['win']}% won, {pick['avg']:+.3f}R a trade, {pick['total']:+.0f}R in all, {pick['net_avg']:+.3f}R after costs.",
        "",
        "Limits: today's listings only (stocks delisted since are missing); today's market cap; no borrow cost; on a stock down 10%+ the short-sale rule only lets a short fill on an uptick.",
        "Checked: every stock-day's minute bars against its daily bar; 61 fake gaps removed (ex-dividend and spin-off mornings); Jan 24 2023 (the NYSE opening glitch) left out;",
        "  entries whose own minute also touched the stop were ordered with that minute's actual trades.",
    ]
    for i, t in enumerate(lines, 1):
        ws.cell(row=i, column=1, value=t)
    ws["A1"].font = Font(bold=True, size=13)
    ws.column_dimensions["A"].width = 160

    # the combinations
    rows = []
    for n in R.RANGES:
        for s in R.STOPS:
            for c in R.COLORS:
                for g in R.GAPS:
                    for v in R.RVOLS:
                        ts = R.trades(n, s, c, g, v)
                        st = R.stats(ts)
                        if not st:
                            continue
                        y = R.years(ts)
                        ex = R.stats([t for t in ts if t[0].split()[0] not in R.MARKET_DAYS])
                        rows.append([f"{n}-min", R.STOP_NAME[s], c, f"{g}%+", "any" if not v else f"{v}x+", st["n"], st["win"], st["avg"], st["total"],
                                     st["net_avg"], st["stopped"], st["risk"],
                                     *[(y[k]["total"] if k in y else None) for k in ("2023", "2024", "2025", "2026")],
                                     sum(1 for k in y.values() if k["total"] > 0), ex["n"] if ex else 0, ex["avg"] if ex else None, ex["total"] if ex else None])
    rows.sort(key=lambda r: -r[8])
    sheet(wb, "Combinations", ["Range", "Stop", "First candle", "Gap", "Early rel vol", "Trades", "Win %", "Avg R", "Total R", "Avg R after costs",
                               "Stopped %", "Median stop distance %", "2023 R", "2024 R", "2025 R", "2026 R", "Years up (of 4)",
                               "Trades without market-wide days", "Avg R without them", "Total R without them"], rows, r_cols=(8, 9, 10, 13, 14, 15, 16, 19, 20))

    # every trade
    for n in R.RANGES:
        rows = []
        for key, row in sorted(R.ROWS.items()):
            tr = row.get(n)
            if row["o"] < 10 or not tr or "t" not in tr:
                continue
            d, sym = key.split()
            rh, dh = tr.get("rh"), tr.get("dh")
            ok = lambda x: x and x["risk_pct"] >= R.MIN_RISK
            rows.append([d, sym, row["gap"], row["pc"], row["o"], tr["color"], tr["rvol"], tr["rlo"], tr["rhi"], tr["t"], tr["entry"],
                         rh["stop"] if rh else None, rh["risk_pct"] if rh else None, rh["exit"] if rh else None, ("stop" if rh["stopped"] else "close") if rh else None,
                         rh["r"] if ok(rh) else None,
                         dh["stop"] if dh else None, dh["exit"] if dh else None, ("stop" if dh["stopped"] else "close") if dh else None, dh["r"] if ok(dh) else None,
                         row["c"], "yes" if d in R.MARKET_DAYS else "", "" if ok(rh) or ok(dh) else "stop under 0.5%: left out"])
        sheet(wb, f"Trades {n}-min", ["Date", "Ticker", "Gap %", "Close before", "Open", "First candle", "Early rel vol", "Range low", "Range high", "Short at (time)",
                                      "Short price", "Stop: range high", "Stop distance %", "Exit", "Exit by", "R (stop range high)",
                                      "Stop: day's high", "Exit ", "Exit by ", "R (stop day's high)", "Day's last price", "Market-wide day", "Note"], rows, r_cols=(16, 20))

    # the top winners
    rows = []
    for label, ts in (("every 5%+ gap", R.trades("3", "rh")), ("gap 8%+", R.trades("3", "rh", gap=8))):
        for key, row, tr, st in sorted(ts, key=lambda t: -t[3]["r"])[:30]:
            d, sym = key.split()
            rows.append([label, d, sym, row["gap"], tr["color"], tr["rvol"], tr["t"], tr["entry"], st["stop"], st["risk_pct"], st["exit"],
                         round(100 * (tr["entry"] - st["exit"]) / tr["entry"], 1), st["r"], "yes" if d in R.MARKET_DAYS else ""])
    sheet(wb, "Top winners", ["Set (3-min range, stop range high)", "Date", "Ticker", "Gap %", "First candle", "Early rel vol", "Short at (time)", "Short price", "Stop",
                              "Stop distance %", "Day's last price", "Move %", "R", "Market-wide day"], rows, widths={"Set (3-min range, stop range high)": 34}, r_cols=(13,))
    wb.save(out_path)
    print("saved", out_path)


if __name__ == "__main__":
    main()
