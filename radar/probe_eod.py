#!/usr/bin/env python3
"""After the close: today's full volume (Yahoo quote) vs the 20-session average full-day volume (Alpaca SIP daily bars)."""
import datetime, json, os, sys, urllib.parse, urllib.request, zoneinfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live import Yahoo
NY = zoneinfo.ZoneInfo("America/New_York")
hdr = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
syms = sys.argv[2:]
now = datetime.datetime.now(NY)
y = Yahoo(); y.login(); q = y.quotes(syms)
url = "https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode({"symbols": ",".join(syms), "timeframe": "1Day", "feed": "sip",
      "limit": 10000, "adjustment": "raw", "start": (now - datetime.timedelta(days=40)).strftime("%Y-%m-%d"), "end": (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")})
with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=60) as r:
    res = json.load(r)
out = {"now": now.isoformat()}
for s in syms:
    d = [b["v"] for b in res["bars"].get(s, [])][-20:]
    out[s] = {"today_vol": q[s][2] if s in q else None, "avg20_daily": round(sum(d) / len(d)) if d else None, "days": len(d)}
json.dump(out, open(sys.argv[1], "w"), indent=1)
