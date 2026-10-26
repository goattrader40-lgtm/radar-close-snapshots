#!/usr/bin/env python3
"""Relative volume at time, several ways, for a few stocks (to compare with TradingView).
  python3 radar/probe_rvol.py <out.json> SYM ..."""
import datetime, json, sys, urllib.request, zoneinfo
NY = zoneinfo.ZoneInfo("America/New_York")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=25) as r:
        return json.load(r)["chart"]["result"][0]
out = {}
now = datetime.datetime.now(NY)
for s in sys.argv[2:]:
    for itv, rng, pp in (("5m", "60d", "false"), ("1m", "8d", "false"), ("5m_pp", "60d", "true")):
        b = f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?includePrePost={pp}&interval={itv.split('_')[0]}&range={rng}"
        r = get(b); q = r["indicators"]["quote"][0]
        days = {}
        for t, v in zip(r["timestamp"], q["volume"]):
            ts = datetime.datetime.fromtimestamp(t, NY)
            mins = ts.hour * 60 + ts.minute
            if (240 if pp == "true" else 570) <= mins < 960:
                days.setdefault(str(ts.date()), []).append((mins, v or 0))
        out.setdefault(s, {})[itv] = {d: v for d, v in sorted(days.items())}
    d1 = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?interval=1d&range=3mo")
    out[s]["daily"] = {str(datetime.datetime.fromtimestamp(t, NY).date()): v for t, v in zip(d1["timestamp"], d1["indicators"]["quote"][0]["volume"])}
    out[s]["meta_volume"] = r["meta"].get("regularMarketVolume")
out["_saved"] = now.isoformat()
json.dump(out, open(sys.argv[1], "w"), separators=(",", ":"))
