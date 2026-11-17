#!/usr/bin/env python3
"""The movers' prices every minute, between the 5-minute live updates, for the portal's tables (the Gainers tab).

  python3 radar/movers.py <live.json> <live_fast.json> <levels.json> <volprofile.json> <sipcal.json> <stocks.json> <out live.json> [min_chg]

The user (Nov 16 2026), with "up 4%+ and Above ORH-5min" set on the Gainers tab: AVEX broke its opening range high at
9:37 and showed with the 9:40 update; "is there any way we can have every 1 min after the 5 min close". The whole market
is read every 5 minutes (radar/live.py, ~3,400 quotes); this reads, each minute in between, only the stocks that are
already moving: up min_chg% or more (2 by default, the list radar/levels.py reads the opening ranges for) in the last
full update, in an earlier minute's read, or already holding an opening range today. Their rows, and the 1-minute watch
list's rows radar/fast.py just read (live_fast.json), replace the last full update's rows; every other stock keeps the
price of the last full update. The result is live.json as the portal reads it, with "fast_at" (this read's time) and
"fast_n" (how many rows are from it); "saved_at" stays the full update's time. Run by radar/day.py after fast.py, from
9:31 to 10:30 (9:36 until Nov 17 2026: "start 931", for the 1- and 2-minute opening range highs); day.py then reads the new movers' opening ranges (levels.py) and publishes both. A stock that jumps from
under min_chg% inside one 5-minute gap waits for the next full update. Nothing here feeds the alerts: they keep
reading live.json's full update and live_fast.json as before.
"""
import datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sipcal  # noqa: E402
from live import NY, Yahoo, rvol_at, yahoo_sym  # noqa: E402

MAX_MOVERS = 900          # a market-wide up day: the biggest movers first (9 quote requests of 100)


def load(p, d=None):
    try:
        return json.load(open(p))
    except Exception:
        return d


def pick(live, fast, lev, prev, min_chg, today):
    """the stocks to read now: up min_chg%+ in the last full update or in the last minute's merged file, or with an opening
    range today; not the ones fast.py just read. The biggest movers first, MAX_MOVERS at most"""
    rows = dict((live or {}).get("rows") or {})
    if prev and prev.get("session") == today:
        rows.update(prev.get("rows") or {})
    up = {s: q[1] for s, q in rows.items() if q and len(q) > 1 and q[1] is not None and q[1] >= min_chg}
    for s in ((lev or {}).get("rows") or {}) if (lev or {}).get("date") == today else ():
        if s in rows:
            up.setdefault(s, (rows[s][1] if rows[s] and rows[s][1] is not None else 0))
    have = set(((fast or {}).get("rows") or {})) if (fast or {}).get("session") == today else set()
    return [s for s, _ in sorted(up.items(), key=lambda x: -x[1]) if s not in have][:MAX_MOVERS]


def merge(live, fast, got, now, today):
    """the last full update with the fresher rows on top: fast.py's, then this read's. A fresher row without an open
    keeps the full update's open (Yahoo leaves an NYSE stock's open empty for its first minutes)"""
    rows = dict(live.get("rows") or {})
    n = 0
    for src in ((fast or {}).get("rows") or {} if (fast or {}).get("session") == today else {}, got):
        for s, q in src.items():
            old = rows.get(s)
            if old is None or not q or not q[0]:
                continue                                    # only stocks of the full update (the portal's universe)
            if q[3] and old[3] and q[3] < old[3]:
                continue                                    # an older quote than the full update's
            q = list(q)
            if len(q) > 5 and q[5] is None and len(old) > 5:
                q[5] = old[5]
            rows[s] = q
            n += 1
    out = dict(live)
    out.update(rows=rows, fast_at=now.isoformat(timespec="seconds"), fast_n=n)
    return out


def main():
    live_p, fast_p, lev_p, prof_p, cal_p, stocks_p, out_p = sys.argv[1:8]
    min_chg = float(sys.argv[8]) if len(sys.argv) > 8 else 2.0
    now = datetime.datetime.now(NY)
    today = now.date().isoformat()
    live = load(live_p)
    if not live or live.get("session") != today:
        sys.exit("movers: no full live update for today")
    fast, lev, prev = load(fast_p), load(lev_p), load(out_p)
    syms = pick(live, fast, lev, prev, min_chg, today)
    got = {}
    if syms:
        prof = (load(prof_p) or {}).get("rows") or {}
        avg20 = {r["symbol"]: r.get("avg_vol_20") for r in load(stocks_p, [])}
        off = sipcal.saved(cal_p, now.date())
        ymap = {yahoo_sym(s): s for s in syms}
        y = Yahoo()
        if not y.login():
            sys.exit("movers: no Yahoo crumb")
        for k, v in y.quotes(list(ymap)).items():
            s = ymap.get(k)
            if not s:
                continue
            price, chg, vol, qt, op, ern, hi = v
            fv = sipcal.corrected(vol, qt, off.get(s))
            vol = vol if fv is None else fv
            got[s] = [price, chg, vol, qt, rvol_at(vol, qt, prof.get(s), avg20.get(s)), op, ern, hi]
        if len(got) < 0.5 * len(syms):
            sys.exit(f"movers: only {len(got)} of {len(syms)} quotes")
    out = merge(live, fast, got, now, today)
    json.dump(out, open(out_p, "w"), separators=(",", ":"))
    print(f"movers: {len(got)} of {len(syms)} movers read, {out['fast_n']} rows fresher than the {str(live.get('saved_at'))[11:16]} update")


if __name__ == "__main__":
    main()
