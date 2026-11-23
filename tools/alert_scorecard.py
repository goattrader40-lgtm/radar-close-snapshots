# The final scorecard, one rule for every table (read-only analysis).
#   python3 final.py <data dir> <out.xlsx>
# good    = after the alert the stock never traded under the day's low it had at the alert, and closed over the alert price
# lower   = never under that low, but closed at or under the alert price
# stopped = traded under that low after the alert
# Left out: alerts whose quoted price is 0.3%+ outside the tape's minute bars around the alert (a stale quote).
import collections, gzip, json, re, sys

D = sys.argv[1].rstrip("/") + "/"
rows = json.load(open(D + "score_2.json"))["rows"]
B = json.load(gzip.open(D + "probe_alertbars_2.json.gz", "rt"))["rows"]
items = {it["key"]: it for it in json.load(open(D + "alerts.json"))["items"]}

keep, bad = [], []
for r in rows:
    hh, mm = map(int, r["time"].split(":"))
    ma = hh * 60 + mm - 570
    near = [b for b in B[r["sym"]] if ma - 2 <= b[0] <= ma]
    lo, hi = min(b[3] for b in near), max(b[2] for b in near)
    d = 0 if lo <= r["entry"] <= hi else min(abs(r["entry"] / lo - 1), abs(r["entry"] / hi - 1)) * 100
    (bad if d > 0.3 else keep).append(r)
    it = items[r["sym"] + ":" + r["kind"]]
    r["tag"] = next((t for t in ("FULL TREND", "NEW TREND", "CAUTION", "NO TREND") if " · " + t in it["msg"]), "")
    m = re.search(r"([+-][\d.]+)%\s*$", it["title"])
    r["chg"] = float(m.group(1)) if m else None
    r["title"] = it["title"]
    r["themes"] = ", ".join(it.get("groups") or [])
    r["res"] = -r["risk_pct"] if r["stopped"] else r["close_pct"]        # the trade's result in %: the stop, or the close
print("left out for a stale quote:", [(r["sym"], r["kind"], r["time"], r["entry"]) for r in bad])
rows = keep

ORDER = ["Episodic pivot", "Power day", "Morning breakout (in trend)", "Breakout, not in trend", "Pattern breakout (Launches)",
         "Gap out of base (1-min high)", "Gap out of base (5-min high)", "Catalyst gap", "Push out of the 10 / 21 EMA", "Start day",
         "Falling-range breakout", "21 EMA reclaim, strong day (heads-up)"]
table = []


def line(name, rs):
    n = len(rs)
    if not n:
        return
    g = sum(r["result"] == "worked" for r in rs)
    s = sum(r["result"] == "failed" for r in rs)
    low = n - g - s
    s_up = sum(1 for r in rs if r["result"] == "failed" and r["close_pct"] > 0)
    up = sum(r["close_pct"] > 0 for r in rs)
    res = sum(r["res"] for r in rs) / n
    table.append([name, n, g, low, s, s_up, up, round(res, 2)])
    print(f"{name:40} {n:4} | good {g:3} ({100 * g / n:3.0f}%) | lower, no stop {low:3} ({100 * low / n:3.0f}%) | stopped {s:3} ({100 * s / n:3.0f}%; {s_up} closed higher anyway) | closed over the alert {up:3} ({100 * up / n:3.0f}%) | avg result {res:+.2f}%")


for fam in ORDER:
    line(fam, [r for r in rows if r["fam"] == fam])
print()
line("ALL BUY ALERTS", rows)
first = {}
for r in sorted(rows, key=lambda r: r["time"]):
    first.setdefault(r["sym"], r)
line("BY STOCK (its first buy alert)", list(first.values()))
print()
mb = [r for r in rows if r["kind"] in ("mbo", "mbo2")]
for t in ("FULL TREND", "NEW TREND", "CAUTION", "NO TREND"):
    line("morning boxes, " + t, [r for r in mb if r["tag"] == t])
print()
line("morning boxes, up under 5% at the alert", [r for r in mb if r["chg"] is not None and r["chg"] < 5])
line("morning boxes, up 5-10%", [r for r in mb if r["chg"] is not None and 5 <= r["chg"] < 10])
line("morning boxes, up 10%+", [r for r in mb if r["chg"] is not None and r["chg"] >= 10])
print()
ai = ("Neoclouds & AI Hosting", "Quantum Computing", "AI Cloud & Data-Center Hosting", "Bitcoin Miners")
line("morning boxes, AI hosting / quantum / miners", [r for r in mb if any(g in r["themes"] for g in ai)])
line("morning boxes, everything else", [r for r in mb if not any(g in r["themes"] for g in ai)])
print()
for name, lo, hi in (("9:35-9:44", "09:35", "09:44"), ("9:45-9:59", "09:45", "09:59"), ("10:00 on", "10:00", "16:00")):
    line("all, alerted " + name, [r for r in rows if lo <= r["time"] <= hi])
print()
best = sorted(rows, key=lambda r: -r["res"])[:8]
worst = sorted(rows, key=lambda r: r["close_pct"])[:8]
print("best:", [(r["sym"], r["kind"], r["time"], f"{r['res']:+.1f}%") for r in best])
print("worst (close vs the alert):", [(r["sym"], r["kind"], r["time"], f"{r['close_pct']:+.1f}%", r["stopped"]) for r in worst])
print("stocks:", len(first), "| alerts:", len(rows))

if len(sys.argv) > 2:
    from openpyxl import Workbook
    from openpyxl.styles import Font
    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws.append(["Alert scorecard, Mon Nov 23 2026 (same-day result; exact 1-minute bars of the consolidated tape)"])
    ws.append(["Bought at the price in the alert; stop under the day's low at that moment; result at the close."])
    ws.append(["Good = never under that low and closed over the alert price. Lower = never under that low, closed at or under the alert price. Stopped = traded under that low after the alert."])
    ws.append([])
    ws.append(["Alert", "Alerts", "Good", "Closed lower, no stop", "Stopped", "of them closed higher anyway", "Closed over the alert price", "Average result %"])
    for t in table:
        ws.append(t)
    for c in ws[5]:
        c.font = Font(bold=True)
    ws.column_dimensions["A"].width = 46
    w2 = wb.create_sheet("Every alert")
    head = ["Time", "Ticker", "Alert", "Trend tag", "Up % at the alert", "Alert price", "Stop (day's low then)", "Risk %", "Result", "Stopped at", "Best gain % before the stop / close",
            "Best at", "Close", "Close vs alert %", "Trade result %", "Day low", "Day high", "Themes", "Alert title"]
    w2.append(head)
    for c in w2[1]:
        c.font = Font(bold=True)
    names = {"worked": "good", "held, no gain": "closed lower, no stop", "failed": "stopped"}
    for r in sorted(rows, key=lambda r: (ORDER.index(r["fam"]), r["time"])):
        w2.append([r["time"], r["sym"], r["fam"], r["tag"], r["chg"], r["entry"], r["stop"], r["risk_pct"], names[r["result"]], r["stopped"] or "", r["peak_pct"], r["peak_at"] or "",
                   r["close"], r["close_pct"], round(r["res"], 2), r["day_low"], r["day_high"], r["themes"], r["title"]])
    for col, wd in zip("ABCDEFGHIJKLMNOPQRS", (7, 8, 34, 11, 9, 10, 10, 7, 20, 9, 10, 8, 9, 9, 9, 9, 9, 30, 50)):
        w2.column_dimensions[col].width = wd
    w2.freeze_panes = "C2"
    wb.save(sys.argv[2])
    print("saved", sys.argv[2])
