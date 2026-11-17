#!/usr/bin/env python3
"""Today's 1-, 2- and 5-minute opening ranges of the movers, for the portal's + Filter "Above ORH" (1min / 2min / 5min).

  python3 radar/levels.py <live.json> <levels.json> [min_chg]

The user (Nov 9 2026): the criteria of the morning breakout alert (over yesterday's high, over the 5-minute opening range
high ...) as + Filter choices on the Gainers & losers tab, "so I can track the list there". Nov 17 2026: one filter,
"above orh, then when i put it does 1min, if i put 2min it does 2 mins, if i put 5min it does 5min", "start 931".
Yesterday's high is in stocks.json (high_1d) and the 21-day closing high too (close_high_21); the opening range needs
today's chart, so this reads Yahoo's 1-minute chart (the 1- and 2-minute highs) and, as before, its 5-minute chart (the
5-minute range) for every stock up min_chg% or more (2 by default) in the live prices
and keeps levels.json {date, saved_at, rows: {sym: [high 5-min, low 5-min, high 1-min, high 2-min]}, part: {sym: minutes
read so far}} on radar-data, next to live.json (the 5-minute pair first, as before; a range not finished yet is null).
The 1-minute high (the 9:30 bar) is read from 9:31, the 2-minute one (9:30-9:32) from 9:32, the 5-minute one (9:30-9:35)
from 9:36: a stock first read before 9:36 is read again when its next range is finished (9:32, 9:36), then never again
that day. Run by radar/day.py after each 5-minute live update and each minute's movers read, from 9:31. A stock not in it
(not up 2%+ yet) has no value: the + Filter leaves it out while that filter is set.
"""
import concurrent.futures, datetime, json, os, sys, urllib.request, zoneinfo

NY = zoneinfo.ZoneInfo("America/New_York")
MAX_NEW = 1200            # new stocks a run (a market-wide gap day: the biggest movers first, the rest at the next update)


RANGES = (1, 2, 5)          # the opening ranges kept, in minutes


def ranges_of(bars, done):
    """[high 5, low 5, high 1, high 2] from today's 1-minute bars [(minutes after 9:30, high, low)]; a range longer than
    `done` (the minutes finished so far) or without a bar is None"""
    def rng(n):
        x = [b for b in bars if b[0] < n] if done >= n else []
        return (round(max(b[1] for b in x), 4), round(min(b[2] for b in x), 4)) if x else (None, None)
    return [*rng(5), rng(1)[0], rng(2)[0]]


def chart(sym, interval, today):
    """today's first 5 minutes from Yahoo's chart: [(minutes after 9:30, high, low)]"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym.replace('/', '-').replace('.', '-'))}?range=1d&interval={interval}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"})
    with urllib.request.urlopen(req, timeout=15) as r:
        res = json.load(r)["chart"]["result"][0]
    qd = res["indicators"]["quote"][0]
    bars = []
    for t, hi, lo in zip(res.get("timestamp") or [], qd.get("high") or [], qd.get("low") or []):
        d = datetime.datetime.fromtimestamp(t, NY)
        m = (d.hour - 9) * 60 + d.minute - 30
        if d.date() == today and 0 <= m < 5 and hi and lo:
            bars.append((m, hi, lo))
    return bars


def opening_range(sym, today, done=5):
    """[high 5, low 5, high 1, high 2] of today's first minutes: the 1- and 2-minute highs from Yahoo's 1-minute chart
    (ranges_of); the 5-minute pair, from 9:36, from its 5-minute chart's 9:30 bar as before (the two charts' 5-minute highs
    differed for 15 of 201 stocks on Nov 17 2026, by 0.1-1%: the 5-minute filter keeps its source). False = no 9:30
    5-minute bar (asked at 9:36 or later); None = not read (try again)"""
    try:
        row = ranges_of(chart(sym, "1m", today), min(done, 4))
        if done >= 5:
            b5 = [b for b in chart(sym, "5m", today) if b[0] == 0]
            if not b5:
                return False
            row[0], row[1] = round(b5[0][1], 4), round(b5[0][2], 4)
        return row if any(v is not None for v in row) else None
    except Exception:
        return None


def due(part, done):
    """a stock read when `part` minutes were finished is read again once its next range is (1 -> 2 at 9:32, 2-4 -> 5 at 9:36)"""
    return part < max([n for n in RANGES if n <= done], default=0)


def main():
    live_p, out_p = sys.argv[1], sys.argv[2]
    min_chg = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    now = datetime.datetime.now(NY)
    el = (now.hour - 9) * 60 + now.minute - 30           # minutes since the open
    done = el if el < 5 else 4 if el == 5 else 5         # the minutes finished so far: 9:31 -> 1 ... the 5-minute range from 9:36, as before
    if done < 1:
        print("levels: no opening range is finished before 9:31")
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
    part = doc.setdefault("part", {})                   # the rows read before 9:36: the minutes finished at their read
    have = {s for s in doc["rows"] if not due(part.get(s, 5), done)} | set(doc.get("none") or [])
    movers = sorted(((s, q[1]) for s, q in (live.get("rows") or {}).items() if q and len(q) > 1 and q[1] is not None and q[1] >= min_chg and s not in have),
                    key=lambda x: -x[1])[:MAX_NEW]
    syms = [s for s, _ in movers]
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        got = dict(zip(syms, ex.map(lambda s: opening_range(s, today, done), syms)))
    for s, v in got.items():
        if v:
            doc["rows"][s] = list(v)
            part.pop(s, None)
            if done < 5:
                part[s] = done
        elif v is False:
            doc.setdefault("none", []).append(s)            # no 9:30 bar (a late open, a halt): not asked again today
    doc["saved_at"] = now.isoformat(timespec="seconds")
    json.dump(doc, open(out_p, "w"), separators=(",", ":"))
    print(f"levels: {sum(1 for v in got.values() if v)} opening ranges read ({len(syms)} asked, {done} min finished), {len(doc['rows'])} today")


if __name__ == "__main__":
    main()
