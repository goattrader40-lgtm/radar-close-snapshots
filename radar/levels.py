#!/usr/bin/env python3
"""Today's 5-minute opening range (9:30-9:35) of the movers, for the portal's + Filter "5-min opening range high (ORH)".

  python3 radar/levels.py <live.json> <levels.json> [min_chg]

The user (Nov 9 2026): the criteria of the morning breakout alert (over yesterday's high, over the 5-minute opening range
high ...) as + Filter choices on the Gainers & losers tab, "so I can track the list there". Yesterday's high is in
stocks.json (high_1d) and the 21-day closing high too (close_high_21); the opening range needs today's chart, so this
reads it from Yahoo's 5-minute chart for every stock up min_chg% or more (2 by default) in the live prices, once a day per
stock (the range is final at 9:35), and keeps them in levels.json {date, saved_at, rows: {sym: [high, low]}} on
radar-data, next to live.json. Run by radar/day.py after each 5-minute live update from 9:36. A stock not in it (not up
2%+ yet) has no value: the + Filter leaves it out while that filter is set.
"""
import concurrent.futures, datetime, json, os, sys, urllib.request, zoneinfo

NY = zoneinfo.ZoneInfo("America/New_York")
MAX_NEW = 1200            # new stocks a run (a market-wide gap day: the biggest movers first, the rest at the next update)


def opening_range(sym, today):
    """(high, low) of today's 9:30 5-minute bar from Yahoo's chart; False = no 9:30 bar today; None = not read (try again)"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym.replace('/', '-').replace('.', '-'))}?range=1d&interval=5m"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.load(r)["chart"]["result"][0]
        qd = res["indicators"]["quote"][0]
        for t, hi, lo in zip(res.get("timestamp") or [], qd.get("high") or [], qd.get("low") or []):
            d = datetime.datetime.fromtimestamp(t, NY)
            if d.date() == today and (d.hour, d.minute) == (9, 30) and hi and lo:
                return round(hi, 4), round(lo, 4)
        return False
    except Exception:
        return None


def main():
    live_p, out_p = sys.argv[1], sys.argv[2]
    min_chg = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    now = datetime.datetime.now(NY)
    if (now.hour, now.minute) < (9, 36):
        print("levels: the opening range isn't final before 9:36")
        return
    live = json.load(open(live_p))
    today = now.date()
    if live.get("session") != today.isoformat():
        print("levels: no live prices for today")
        return
    try:
        doc = json.load(open(out_p))
        if doc.get("date") != today.isoformat():
            doc = None
    except Exception:
        doc = None
    doc = doc or {"date": today.isoformat(), "rows": {}, "none": []}
    have = set(doc["rows"]) | set(doc.get("none") or [])
    movers = sorted(((s, q[1]) for s, q in (live.get("rows") or {}).items() if q and len(q) > 1 and q[1] is not None and q[1] >= min_chg and s not in have),
                    key=lambda x: -x[1])[:MAX_NEW]
    syms = [s for s, _ in movers]
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        got = dict(zip(syms, ex.map(lambda s: opening_range(s, today), syms)))
    for s, v in got.items():
        if v:
            doc["rows"][s] = list(v)
        elif v is False:
            doc.setdefault("none", []).append(s)            # no 9:30 bar (a late open, a halt): not asked again today
    doc["saved_at"] = now.isoformat(timespec="seconds")
    json.dump(doc, open(out_p, "w"), separators=(",", ":"))
    print(f"levels: {sum(1 for v in got.values() if v)} new opening ranges ({len(syms)} asked), {len(doc['rows'])} today")


if __name__ == "__main__":
    main()
