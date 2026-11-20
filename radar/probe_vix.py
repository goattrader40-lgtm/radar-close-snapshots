#!/usr/bin/env python3
"""Daily closes back to 1990 for the VIX + market-drop study (a one-off check; nothing live reads it).

  python3 radar/probe_vix.py <out.json> SYM ...   -> {SYM: [[date, close, adjclose], ...]}
Yahoo's daily chart; adjclose includes dividends (total return) where Yahoo has it, else = close.
Rows are kept whenever the close exists (index rows such as ^VIX have no volume).
"""
import datetime, json, sys, time, urllib.parse, urllib.request, zoneinfo
NY = zoneinfo.ZoneInfo("America/New_York")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
START = 631152000  # 1990-01-01
out = {}
for s in sys.argv[2:]:
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(s)}"
           f"?period1={START}&period2={int(time.time())}&interval=1d&includePrePost=false&events=div%2Csplit")
    for attempt in range(3):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60))["chart"]["result"][0]
            q = r["indicators"]["quote"][0]
            adj = (r["indicators"].get("adjclose") or [{}])[0].get("adjclose") or q["close"]
            out[s] = [[datetime.datetime.fromtimestamp(t, NY).date().isoformat(), round(c, 4), round(a if a is not None else c, 4)]
                      for t, c, a in zip(r["timestamp"], q["close"], adj) if c is not None]
            break
        except Exception as e:
            print(s, "attempt", attempt + 1, "failed:", e, file=sys.stderr)
            time.sleep(3)
json.dump(out, open(sys.argv[1], "w"), separators=(",", ":"))
print({s: (len(v), v[0][0] if v else None, v[-1][0] if v else None) for s, v in out.items()})
