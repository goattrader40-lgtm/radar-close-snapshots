#!/usr/bin/env python3
"""The earnings breakdown alert (radar/alerts.py ebd_*) replayed on the gap-down study's days, minute by minute, as the live
job sees them: a check every minute 9:31-12:00 and 3:00-4:00, every 5 minutes in between; the quote = the last finished
minute's close; the 1-minute chart = the finished minutes.

  python3 tools/gapdown/sim_ebd.py <work dir> <data dir> OUT.json      (the study's files: out_final3.json, features.json,
                                                                         gaps_v2.json, reasons.json; bars_6y, raw_gapdown_*)
  python3 tools/gapdown/sim_report.py OUT.json <work dir>               the tables

For every earnings gap-down of the study (and the non-earnings and 5-8% ones as a control): did it alert, when, at what
price, and how its box ended (stopped / over the low / under it at the close). tools/gapdown/test_ebd.py replays the days
kept in ebd_cases.json the same way (no study files needed)."""
import datetime, gzip, json, os, sys, zoneinfo
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "radar"))
os.environ.setdefault("NTFY_TOPIC", "")
import alerts as A  # noqa: E402

NY = zoneinfo.ZoneInfo("America/New_York")
HALF = {"2023-07-03", "2023-11-24", "2024-07-03", "2024-11-29", "2024-12-24", "2025-07-03", "2025-11-28", "2025-12-24", "2026-07-02"}


def polls(last):
    """the minutes after 9:30 the job checks at (radar/day.py fast_window)"""
    return [m for m in range(1, last + 2) if m <= 150 or m >= 330 or m % 5 == 0]


def replay_day(date, sym, st, bars, earn, last_day):
    """one stock-day through alerts.ebd_run: st = its stocks.json row at the last close (price, ema50, sma200, adr_20,
    mcap_b, avg_vol_20, dvol_20_m), bars = the day's 1-minute bars [(minute after 9:30, o, h, l, c, v)], earn = the
    Earnings tab's row for it (or None). Returns {alert, back, stopped, lost, skip, close}"""
    d, pc = datetime.date.fromisoformat(date), st["price"]
    S, E = {sym: st}, ({sym: earn} if earn else {})
    state, res = {"date": date, "sent": [], "items": []}, {"alert": None}
    for m in polls(bars[-1][0]):
        done = [b for b in bars if b[0] < m]
        if not done:
            continue
        now = datetime.datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY) + datetime.timedelta(minutes=m)
        price = done[-1][4]
        q = [price, 100 * (price / pc - 1), sum(b[5] for b in done), now.timestamp(), 2.0, done[0][1], None, max(b[2] for b in done)]
        new, back = A.ebd_run({"rows": {sym: q}}, "/nonexistent/launch.json", {"date": last_day}, state, now, set(state["sent"]), S, E, bars_of=lambda s_: done)
        for a in new + back:
            state["items"].append({"key": a[0], "time": f"{now:%H:%M}", "title": a[1], "msg": a[2], "kind": "trigger"})
            state["sent"].append(a[0])
            if a[0].endswith(":ebd"):
                res["alert"] = {"m": m, "t": f"{now:%H:%M}", "price": price, "title": a[1], "msg": a[2], "lv": dict(state["ebd_lv"][sym])}
            else:
                res.setdefault("back", []).append(f"{now:%H:%M}")
    res["stopped"] = (state.get("ebd_stopped") or {}).get(f"{sym}:ebd")
    res["lost"] = (state.get("lost") or {}).get(f"{sym}:ebd")
    res["skip"] = (state.get("ebd_skip") or {}).get(sym)
    res["close"] = bars[-1][4]
    if res["alert"]:
        a = res["alert"]
        # the alert as a trade: short at the alert's price, stop at the candle's high (on the minute bars), out at the close
        stop, exit_, stp = a["lv"]["orh"], bars[-1][4], 0
        for b in bars:
            if b[0] >= a["m"] and b[2] >= stop:
                exit_, stp = max(b[1], stop), 1
                break
        a["r"] = round((a["price"] - exit_) / (stop - a["price"]), 4) if stop > a["price"] else None
        a["stopped_bars"] = stp
        a["risk_pct"] = round((stop / a["price"] - 1) * 100, 3)
    return res


def study_day(key, rows, feats, gaps):
    """the stocks.json row of one study day (prices on the minute bars' scale)"""
    row, f, g = rows[key], feats.get(key) or {}, gaps[key]
    k = row["scale"]
    return {"symbol": key.split()[1], "price": g["pc"] * k, "ema50": (f.get("ema50") or 0) * k or None, "sma200": (f.get("sma200") or 0) * k or None,
            "adr_20": row["adr"], "mcap_b": 5.0, "avg_vol_20": g["av20"], "dvol_20_m": g["adv20"] / 1e6, "tv_symbol": key.split()[1]}


def main():
    work, data, out_path = sys.argv[1:4]
    rows = json.load(open(os.path.join(work, "out_final3.json")))["rows"]
    feats = json.load(open(os.path.join(work, "features.json")))
    gaps = json.load(open(os.path.join(work, "gaps_v2.json")))
    reasons = json.load(open(os.path.join(work, "reasons.json")))
    spy = [b[0] for b in json.load(gzip.open(os.path.join(data, "bars_6y.json.gz"), "rt"))["bars"]["SPY"]]
    prev_day = {d: spy[i - 1] for i, d in enumerate(spy) if i}
    out = {}
    for y in (2023, 2024, 2025, 2026):
        d = json.load(gzip.open(os.path.join(data, f"raw_gapdown_{y}.json.gz"), "rt"))["bars"]
        for key, bs in d.items():
            date, sym = key.split()
            key = f"{date} {sym.replace('.', '/')}"
            row = rows.get(key)
            e = reasons.get(key, {}).get("earn")
            if not row or row["o"] < 10 or e is None:
                continue
            bs = sorted(b for b in bs if b[0] < (210 if date in HALF else 390))
            earn = {"react_day": date, "reported": True, "read": "Bearish", "why": "EPS miss"} if e == 1 else None
            out[key] = dict(replay_day(date, sym, study_day(key, rows, feats, gaps), bs, earn, prev_day[date]), earn=e, gap=row["gap"])
    json.dump(out, open(out_path, "w"), separators=(",", ":"))
    al = [v for v in out.values() if v["alert"]]
    print("stock-days replayed", len(out), "| alerts", len(al), "| on earnings days", sum(1 for v in al if v["earn"] == 1), "| on non-earnings days", sum(1 for v in al if v["earn"] == 0))


if __name__ == "__main__":
    main()
