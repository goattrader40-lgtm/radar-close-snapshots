#!/usr/bin/env python3
"""Check: Yahoo 5-minute bar volume vs the consolidated volume (daily bar / live quote), per day and today so far.
  python3 radar/probe_vol.py <out.json> SYM ..."""
import datetime, json, sys, urllib.request, zoneinfo
NY = zoneinfo.ZoneInfo("America/New_York")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=25) as r:
        return json.load(r)["chart"]["result"][0]
out = {}
for s in sys.argv[2:]:
    b = f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?includePrePost=false"
    i5, d1 = get(b + "&range=30d&interval=5m"), get(b + "&range=3mo&interval=1d")
    full = {str(datetime.datetime.fromtimestamp(t, NY).date()): v for t, v in zip(d1["timestamp"], d1["indicators"]["quote"][0]["volume"]) if v}
    days = {}
    for t, v in zip(i5["timestamp"], i5["indicators"]["quote"][0]["volume"]):
        ts = datetime.datetime.fromtimestamp(t, NY); d = str(ts.date())
        e = days.setdefault(d, {"sum": 0, "last_bar": 0, "first_bar": 0, "n": 0})
        e["sum"] += v or 0; e["n"] += 1
        if (ts.hour, ts.minute) == (15, 55): e["last_bar"] = v or 0
        if (ts.hour, ts.minute) == (9, 30): e["first_bar"] = v or 0
    out[s] = {"meta_volume_today": i5["meta"].get("regularMarketVolume"), "meta_time": i5["meta"].get("regularMarketTime"),
              "days": {d: dict(e, daily=full.get(d)) for d, e in sorted(days.items())}}
json.dump(out, open(sys.argv[1], "w"), indent=1)
