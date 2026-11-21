#!/usr/bin/env python3
"""The opening-range-high break on gap days (the user, Nov 21 2026: "do your test for orh (we can see 3min and 5min, and
their risk is low of day that time"). A test tool only: nothing live reads it.

  python3 radar/probe_orh.py history/orh_request.json /tmp/probe_orh.json

The request is {date: [symbols]} (the 5%+ gap-up days of the EP study). For each stock-day it reads the day's 1-minute SIP
bars from Alpaca (regular hours) and, for a 3- and a 5-minute opening range:
  entry   the first 1-minute bar after the range whose high goes over the range high: bought at the range high (at the
          bar's open when it opens over it)
  stop    the low of the day up to that bar (the bars before it, the range included)
  then, the rest of that day minute by minute: the stop (all out), or +15% over the entry first (1/3 sold, the stop of the
          rest moves to breakeven)
Saved per stock-day and range: [entry time, entry, stop, 1/3 sold (0/1), out (0/1), realised P&L per share of the whole
position, position left, the day's close]; null when the range high never broke. The days after are scored from the
daily bars (same management as the close study)."""
import datetime, json, os, sys, time, urllib.error, urllib.parse, urllib.request, zoneinfo

NY = zoneinfo.ZoneInfo("America/New_York")
HDR = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
RANGES = (3, 5)
TARGET = 0.15
SELL = 1 / 3


def bars(date, syms):
    """{symbol: [(minute after 9:30, o, h, l, c)]} for one session"""
    d = datetime.date.fromisoformat(date)
    start = datetime.datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY).astimezone(datetime.timezone.utc)
    end = datetime.datetime(d.year, d.month, d.day, 16, 0, tzinfo=NY).astimezone(datetime.timezone.utc)
    out, token = {}, None
    while True:
        q = {"symbols": ",".join(syms), "timeframe": "1Min", "feed": "sip", "adjustment": "split", "limit": 10000,
             "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"), "end": end.strftime("%Y-%m-%dT%H:%M:%SZ")}
        if token:
            q["page_token"] = token
        for attempt in range(5):
            try:
                with urllib.request.urlopen(urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q), headers=HDR), timeout=60) as r:
                    res = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 or e.code >= 500:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise
        else:
            raise RuntimeError("alpaca kept failing on " + date)
        for s, bs in (res.get("bars") or {}).items():
            for b in bs:
                t = datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(NY)
                m = (t.hour - 9) * 60 + t.minute - 30
                if 0 <= m < 390:
                    out.setdefault(s, []).append((m, b["o"], b["h"], b["l"], b["c"]))
        token = res.get("next_page_token")
        time.sleep(0.35)                     # the free plan's 200 requests a minute
        if not token:
            return out


def orh_trade(bs, n):
    bs = sorted(bs)
    rng = [b for b in bs if b[0] < n]
    after = [b for b in bs if b[0] >= n]
    if not rng or not after:
        return None
    orh = max(b[2] for b in rng)
    low = min(b[3] for b in rng)
    for j, b in enumerate(after):
        if b[2] > orh:
            entry = max(b[1], orh)
            stop = low
            if entry <= stop:
                return None
            pos, pnl, took, out = 1.0, 0.0, 0, 0
            for m, o, h, l, c in after[j + 1:]:
                if l <= stop:
                    px = min(o, stop)
                    pnl += pos * (px - entry); pos = 0.0; out = 1
                    break
                if not took and h >= entry * (1 + TARGET):
                    px = max(o, entry * (1 + TARGET))
                    pnl += SELL * (px - entry); pos -= SELL; took = 1; stop = max(stop, entry)
            day_close = bs[-1][4]
            t = 570 + b[0]
            return [f"{t // 60:02d}:{t % 60:02d}", round(entry, 4), round(stop, 4), took, out, round(pnl, 4), round(pos, 4), day_close]
        low = min(low, b[3])
    return None


def main():
    req = json.load(open(sys.argv[1]))
    res, errors, n = {}, [], 0
    for date, syms in sorted(req.items()):
        for k in range(0, len(syms), 50):
            try:
                B = bars(date, syms[k:k + 50])
            except Exception as e:
                errors.append(f"{date}: {e}")
                continue
            for s in syms[k:k + 50]:
                if s in B:
                    res[f"{date} {s}"] = {str(r): orh_trade(B[s], r) for r in RANGES}
                    n += 1
        print(date, n, flush=True)
    json.dump({"made_at": datetime.datetime.now(NY).isoformat(timespec="seconds"), "requested": sum(len(v) for v in req.values()),
               "found": n, "errors": errors[:50], "fields": "entry time, entry, stop, third sold, out, pnl per share, position left, day close",
               "trades": res}, open(sys.argv[2], "w"), separators=(",", ":"))


if __name__ == "__main__":
    main()
