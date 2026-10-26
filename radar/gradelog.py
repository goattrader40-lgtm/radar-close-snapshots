#!/usr/bin/env python3
"""Track record of the pre-market grades (Theme & Group Radar).

  add <premarket.json> <log.json>
      Morning: appends today's graded gappers (one row per date + symbol; re-running replaces that day's rows).
  update <log.json> <stocks.json> <build.json>
      Evening: records each logged stock's close for the build's session date, then fills the outcome fields:
        d0_pct   gap-day close vs the previous close (%)
        held     gap-ups: closed at or above the pre-market price; gap-downs: closed at or below it
        r5, r20  close 5 and 20 sessions after the gap day vs the gap-day close (%)
"""
import json, os, sys

KEEP = ("symbol", "direction", "grade", "catalyst", "inflection", "inflection_score", "gap_pct", "prev_close", "pm_last")


PLACEHOLDER = {"key": "(none)", "placeholder": True, "date": "", "symbol": "", "direction": "", "grade": "", "closes": {}}


def load(p):
    rows = json.load(open(p)) if os.path.exists(p) and os.path.getsize(p) else []
    return [r for r in rows if not r.get("placeholder")]


def save(log, p):   # the dashboard needs at least one row, so an empty log keeps a placeholder
    json.dump(log or [PLACEHOLDER], open(p, "w"), separators=(",", ":"))


def add(pm_path, log_path):
    rows = json.load(open(pm_path))
    log = load(log_path)
    graded = [r for r in rows if r.get("graded")]
    if not graded:
        print(json.dumps({"added": 0, "log_rows": len(log)})); save(log, log_path); return
    date = graded[0]["scan_date"]
    log = [r for r in log if r["date"] != date]
    for r in graded:
        e = {k: r.get(k) for k in KEEP}
        e.update(date=date, key=date + " " + r["symbol"], closes={}, d0_close=None, d0_pct=None, held=None, r5=None, r20=None)
        log.append(e)
    save(log, log_path)
    print(json.dumps({"added": len(graded), "log_rows": len(log)}))


def update(log_path, stocks_path, build_path):
    log = load(log_path)
    px = {s["symbol"]: s.get("price") for s in json.load(open(stocks_path))}
    asof = json.load(open(build_path))[0]["asof"]
    n = 0
    for e in log:
        if asof < e["date"] or len(e["closes"]) > 20:
            continue
        p = px.get(e["symbol"])
        if p and asof not in e["closes"]:
            e["closes"][asof] = p; n += 1
        days = sorted(e["closes"])
        c = [e["closes"][d] for d in days]
        if days and days[0] == e["date"]:
            e["d0_close"] = c[0]
            if e.get("prev_close"):
                e["d0_pct"] = round((c[0] / e["prev_close"] - 1) * 100, 2)
            if e.get("pm_last"):
                e["held"] = c[0] >= e["pm_last"] if e["direction"] == "up" else c[0] <= e["pm_last"]
            if len(c) > 5:
                e["r5"] = round((c[5] / c[0] - 1) * 100, 2)
            if len(c) > 20:
                e["r20"] = round((c[20] / c[0] - 1) * 100, 2)
    save(log, log_path)
    print(json.dumps({"asof": asof, "closes_recorded": n, "log_rows": len(log)}))


if __name__ == "__main__":
    if sys.argv[1] == "add":
        add(sys.argv[2], sys.argv[3])
    else:
        update(sys.argv[2], sys.argv[3], sys.argv[4])
