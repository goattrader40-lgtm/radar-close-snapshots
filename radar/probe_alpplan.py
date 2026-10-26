#!/usr/bin/env python3
"""Which Alpaca market-data plan the keys have: asks for the last 10 minutes of SIP bars, which only paid plans allow."""
import datetime, json, os, sys, urllib.error, urllib.parse, urllib.request
hdr = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
now = datetime.datetime.now(datetime.timezone.utc)
out = {"now": now.isoformat(timespec="seconds")}
for feed in ("sip", "iex"):
    q = {"symbols": "SPY,AAPL", "timeframe": "1Min", "feed": feed, "start": (now - datetime.timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")}
    try:
        with urllib.request.urlopen(urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q), headers=hdr), timeout=30) as r:
            res = json.load(r)
        out[feed] = {"ok": True, "bars": {s: len(v) for s, v in (res.get("bars") or {}).items()}}
    except urllib.error.HTTPError as e:
        out[feed] = {"ok": False, "status": e.code, "body": e.read().decode(errors="replace")[:300]}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out))
