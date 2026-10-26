#!/usr/bin/env python3
"""Relative volume at 15:55 today for a few stocks, computed several ways from Alpaca SIP 1-minute bars."""
import datetime, json, os, sys, urllib.parse, urllib.request, zoneinfo
NY = zoneinfo.ZoneInfo("America/New_York")
hdr = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
syms = sys.argv[2:]
now = datetime.datetime.now(NY)
start = (now - datetime.timedelta(days=45)).astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
end = (now - datetime.timedelta(minutes=16)).astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
out = {}
for s in syms:
    q = {"symbols": s, "timeframe": "1Min", "feed": "sip", "limit": 10000, "adjustment": "raw", "start": start, "end": end}
    days = {}
    while True:
        with urllib.request.urlopen(urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q), headers=hdr), timeout=60) as r:
            res = json.load(r)
        for b in (res.get("bars") or {}).get(s, []):
            ts = datetime.datetime.fromisoformat(b["t"][:19] + "+00:00").astimezone(NY)
            m = ts.hour * 60 + ts.minute
            if 570 <= m < 960:
                days.setdefault(ts.date().isoformat(), {})[m] = days.setdefault(ts.date().isoformat(), {}).get(m, 0) + b["v"]
        if not res.get("next_page_token"): break
        q["page_token"] = res["next_page_token"]
    out[s] = days
json.dump(out, open(sys.argv[1], "w"))
