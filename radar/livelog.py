#!/usr/bin/env python3
"""The morning record: what the live data showed for the watch list's movers, update by update (test/livelog, Nov 4 2026).

  python3 radar/livelog.py <live.json> <launch.json> <live_history.json> [<sipcal.json>]

KD on Nov 4 2026 gapped +15% on earnings and ran +30%; on the exact minute data the alert rules fire it at 9:35
(POWER DAY, $15.30, +18.3%, volume pace 6.7x), but the live file keeps no history, so what the live update itself
saw could not be checked. So from 9:30 to 11:00, on every live update (and the 1-minute checks), each stock of last
night's watch list that gaps 5%+ or trades up 5%+ is recorded:
  time, price, change, gap, volume (as used: after the Alpaca correction), volume pace (rel vol, what every
  launch-type alert needs), the Alpaca correction in effect [Yahoo's surplus taken off, SIP volume at the
  calibration] (null = none yet: the first one lands about 9:51), and the alerts the rules fire right then
  (radar/alerts.py: find_early before 9:35, find from 9:35).
A watch-list stock missing from the live quotes is recorded as missing. The file is published with live.json.
"""
import datetime, json, os, sys, zoneinfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

NY = zoneinfo.ZoneInfo("America/New_York")
KEYS = ["time", "price", "chg", "gap", "volume", "rel_vol", "alpaca_fix", "would_fire"]


def main():
    live_p, launch_p, out_p = sys.argv[1:4]
    cal_p = sys.argv[4] if len(sys.argv) > 4 else None
    now = datetime.datetime.now(NY)
    if not ((9, 30) <= (now.hour, now.minute) < (11, 0)):
        return
    live, doc = json.load(open(live_p)), json.load(open(launch_p))
    rows = live.get("rows") or {}
    try:
        h = json.load(open(out_p))
        if h.get("date") != now.date().isoformat():
            raise ValueError
    except Exception:
        h = {"date": now.date().isoformat(), "keys": KEYS, "rows": {}, "missing": {}}
    off = {}
    if cal_p:
        try:
            import sipcal
            off = sipcal.saved(cal_p, now.date())
        except Exception:
            off = {}
    fire = {}
    try:
        import alerts
        early = (now.hour, now.minute) < (9, 35)
        for a in (alerts.find_early(live, doc, now) if early else alerts.find(live, doc, now)):
            s, k = a[0].split(":", 1)
            fire.setdefault(s, []).append(k)
    except Exception as e:
        h.setdefault("errors", {})[now.strftime("%H:%M:%S")] = repr(e)[:160]
    t = now.strftime("%H:%M:%S")
    for sym in (doc.get("watch") or {}):
        q = rows.get(sym)
        if not q:
            continue
        price, chg = q[0], q[1]
        op = q[5] if len(q) > 5 else None
        prev = price / (1 + chg / 100) if chg is not None else None
        gap = round((op / prev - 1) * 100, 2) if op and prev else None
        if not ((gap or 0) >= 5 or (chg or 0) >= 5):
            continue
        o = off.get(sym)
        h["rows"].setdefault(sym, []).append([t, price, round(chg, 2) if chg is not None else None, gap, q[2] if len(q) > 2 else None,
                                              q[4] if len(q) > 4 else None, list(o) if o else None, fire.get(sym, [])])
    miss = [s for s in (doc.get("watch") or {}) if s not in rows]
    if miss:
        h["missing"][t] = miss[:50]
    json.dump(h, open(out_p, "w"), separators=(",", ":"))


if __name__ == "__main__":
    main()
