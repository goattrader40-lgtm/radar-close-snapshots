#!/usr/bin/env python3
"""Which came first inside one minute: the break of the range low or the touch of the stop (the gap-down short study, the
user, Nov 23 2026). A 1-minute bar can't order its own high and low, so for the entries whose own minute also traded at
or over the stop this reads that minute's trades (Alpaca, SIP). A test tool only: nothing live reads it.

  python3 radar/probe_ticks.py history/gapdown_ticks.json /tmp/gapdown_ticks_out.json

The request is {"date SYMBOL minute": [range low, the bar's low, the bar's high, stop, stop ...]} (minute = minutes
after 9:30; prices as in the split-adjusted 1-minute bars). Saved per key: {"n": trades used, "lo": lowest, "hi": highest,
"f": the factor from the trades' prices (as traded) to the bars' (1 unless the stock split since), "ok": 1 when the
trades' high matches the bar's, "entry": seconds into the minute of the first trade under the range low (null if none),
"pre_hi": the minute's highest trade before it, "stops": {stop: 1 if a trade at or over it came after that first trade,
else 0}}.
Trades used: 100 shares or more, without the sale conditions that don't set a bar's high and low."""
import datetime, json, sys, time, urllib.error, urllib.parse, urllib.request, zoneinfo
import probe_orh

NY = zoneinfo.ZoneInfo("America/New_York")
SKIP = set("CHIMNQRTUVW7")


def ticks(sym, date, minute):
    d = datetime.date.fromisoformat(date)
    t0 = datetime.datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY) + datetime.timedelta(minutes=minute)
    q0 = {"feed": "sip", "limit": 10000, "start": t0.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
          "end": (t0 + datetime.timedelta(seconds=59, milliseconds=999)).astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.999Z")}
    out, token = [], None
    while True:
        q = dict(q0, **({"page_token": token} if token else {}))
        for attempt in range(5):
            try:
                with urllib.request.urlopen(urllib.request.Request(f"https://data.alpaca.markets/v2/stocks/{urllib.parse.quote(sym)}/trades?" + urllib.parse.urlencode(q), headers=probe_orh.HDR), timeout=60) as r:
                    res = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 or e.code >= 500:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise
        else:
            raise RuntimeError("alpaca kept failing")
        for t in res.get("trades") or []:
            if t.get("s", 0) >= 100 and not (set(t.get("c") or []) & SKIP):
                out.append((t["t"], t["p"]))
        token = res.get("next_page_token")
        time.sleep(0.35)
        if not token:
            return out, t0                   # the API's own order (by time): the timestamps' text doesn't sort (":05Z" vs ":05.5Z")


def main():
    req = json.load(open(sys.argv[1]))
    out, errors = {}, []
    for i, (key, v) in enumerate(sorted(req.items())):
        date, sym, minute = key.split()
        try:
            ts, t0 = ticks(sym.replace("/", "."), date, int(minute))
        except Exception as e:
            errors.append(f"{key}: {e}")
            continue
        low, bar_lo, bar_hi, stops = v[0], v[1], v[2], v[3:]
        if not ts:
            out[key] = {"n": 0}
            continue
        lo, hi = min(p for t, p in ts), max(p for t, p in ts)
        f = bar_lo / lo
        if abs(f - 1) < 0.005:
            f = 1.0
        ts = [(t, p * f) for t, p in ts]
        j = next((n for n, (t, p) in enumerate(ts) if p < low), None)
        sec = None
        if j is not None:
            tt = datetime.datetime.fromisoformat(ts[j][0][:19] + "+00:00")
            sec = int((tt - t0.astimezone(datetime.timezone.utc)).total_seconds())
        out[key] = {"n": len(ts), "lo": lo, "hi": hi, "f": round(f, 5), "ok": 1 if abs(hi * f / bar_hi - 1) < 0.005 else 0, "entry": sec,
                    "pre_hi": max((p for t, p in ts[:j]), default=None) if j is not None else None,   # the minute's high before that trade: the day's-high stop
                    "stops": {str(s): (1 if j is not None and any(p >= s for t, p in ts[j + 1:]) else 0) for s in stops}}
        if i % 25 == 0:
            print(i, key, out[key], flush=True)
    json.dump({"requested": len(req), "found": len(out), "errors": errors[:50], "rows": out}, open(sys.argv[2], "w"), separators=(",", ":"))


if __name__ == "__main__":
    main()
