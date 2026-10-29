#!/usr/bin/env python3
"""1-minute quotes for the stocks that can alert, between the 5-minute live updates.

  python3 radar/fast.py <launch.json> <stocks.json> <volprofile.json> <sipcal.json> <out.json>

The launch watch list (setups/launch.json, a few hundred stocks), so a big gap-up on volume (a catalyst gap, a power
day, an A+/A launch) alerts within a minute instead of up to five (HRI crossed its 200 SMA between the 9:35 and the
9:40 update on Oct 27, 2026). Breakouts of the launches being followed stay on the 5-minute update. Writes live.json-shaped rows for those stocks only, Rel vol as radar/live.py works it out,
with the volume correction the last live update measured (radar/sipcal.py). radar/alerts.py reads it like live.json.
"""
import datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sipcal  # noqa: E402
from live import NY, Yahoo, fill_opens, rvol_at, yahoo_sym  # noqa: E402


def main():
    launch_p, stocks_p, prof_p, cal_p, out_p = sys.argv[1:6]
    now = datetime.datetime.now(NY)
    doc = json.load(open(launch_p))
    syms = sorted(doc.get("watch", {}))
    try:
        prof = json.load(open(prof_p))["rows"]
    except Exception:
        prof = {}
    avg20 = {r["symbol"]: r.get("avg_vol_20") for r in json.load(open(stocks_p))}
    off = sipcal.saved(cal_p, now.date())
    ymap = {yahoo_sym(s): s for s in syms}
    y = Yahoo()
    if not y.login():
        sys.exit("fast: no Yahoo crumb")
    rows = {}
    got = y.quotes(list(ymap))
    opened = fill_opens(y, got, now)                    # the movers' opens from the chart in the first 20 minutes (NYSE)
    for k, v in got.items():
        s = ymap.get(k)
        if not s:
            continue
        price, chg, vol, qt, op, ern = v
        fv = sipcal.corrected(vol, qt, off.get(s))
        vol = vol if fv is None else fv
        rows[s] = [price, chg, vol, qt, rvol_at(vol, qt, prof.get(s), avg20.get(s)), op, ern]
    if len(rows) < 0.5 * len(syms):
        sys.exit(f"fast: only {len(rows)} of {len(syms)} quotes")
    times = sorted(v[3] for v in rows.values() if v[3])
    session = datetime.datetime.fromtimestamp(times[len(times) // 2], NY).date().isoformat() if times else now.date().isoformat()
    json.dump({"saved_at": now.isoformat(timespec="seconds"), "date": now.date().isoformat(), "session": session,
               "n": len(rows), "source": "yahoo quote (1-minute watch list)", "rows": rows}, open(out_p, "w"), separators=(",", ":"))
    print(f"fast: {len(rows)} quotes, {sum(1 for s in rows if s in off)} volume-corrected, open from the chart: {' '.join(f'{ymap.get(k, k)} {o}' + (f' (quote {q})' if q != o else '') for k, q, o in opened) or '-'}")


if __name__ == "__main__":
    main()
