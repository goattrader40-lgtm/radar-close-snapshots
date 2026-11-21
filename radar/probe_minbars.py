#!/usr/bin/env python3
"""TEST ONLY: 1-minute SIP bars (Alpaca) of a few stocks between two dates, regular hours.
  python3 radar/probe_minbars.py <out.json> FROM TO SYM ...
"""
import datetime, json, os, sys, urllib.parse, urllib.request
out, d0, d1, syms = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
hdr = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
q = {"symbols": ",".join(syms), "timeframe": "1Min", "feed": "sip", "adjustment": "raw", "limit": 10000,
     "start": d0 + "T13:00:00Z", "end": d1 + "T22:00:00Z"}
bars = {}
while True:
    with urllib.request.urlopen(urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q), headers=hdr), timeout=60) as r:
        res = json.load(r)
    for s, rows in (res.get("bars") or {}).items():
        bars.setdefault(s, []).extend(rows)
    if not res.get("next_page_token"):
        break
    q["page_token"] = res["next_page_token"]
json.dump({"from": d0, "to": d1, "bars": bars}, open(out, "w"), separators=(",", ":"))
print({s: len(v) for s, v in bars.items()})
