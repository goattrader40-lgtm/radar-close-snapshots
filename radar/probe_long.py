#!/usr/bin/env python3
"""Long daily price history (back to 2010) for a few tickers, to check older launch examples.

  python3 radar/probe_long.py <out.json> SYM ...      -> {SYM: [[date, open, high, low, close, volume], ...]}
Yahoo's daily bars, adjusted for splits (not dividends), the same source as the scanner's 2-year file.
"""
import datetime, json, sys, time, urllib.parse, urllib.request, zoneinfo
NY = zoneinfo.ZoneInfo("America/New_York")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
out = {}
for s in sys.argv[2:] + ["SPY"]:
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(s.replace('.', '-'))}"
           f"?period1=1262304000&period2={int(time.time())}&interval=1d&includePrePost=false")
    for attempt in range(3):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60))["chart"]["result"][0]
            q = r["indicators"]["quote"][0]
            out[s] = [[datetime.datetime.fromtimestamp(t, NY).date().isoformat(), o, h, l, c, v]
                      for t, o, h, l, c, v in zip(r["timestamp"], q["open"], q["high"], q["low"], q["close"], q["volume"])
                      if None not in (o, h, l, c, v)]
            break
        except Exception as e:
            print(s, "attempt", attempt + 1, "failed:", e, file=sys.stderr)
            time.sleep(3)
json.dump(out, open(sys.argv[1], "w"), separators=(",", ":"))
print({s: len(v) for s, v in out.items()})
