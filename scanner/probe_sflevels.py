#!/usr/bin/env python3
"""Daily and 15-minute bars for a few tickers, to read the Silent Flip lines by hand (a test only).
  python3 scanner/probe_sflevels.py <out.json> SYM ..."""
import datetime, json, os, sys, traceback, urllib.parse, urllib.request, zoneinfo
NY = zoneinfo.ZoneInfo("America/New_York")
hdr = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
now = datetime.datetime.now(datetime.timezone.utc)
z = lambda d: d.strftime("%Y-%m-%dT%H:%M:%SZ")
def alp(sym, tf, days):
    q = {"symbols": sym, "timeframe": tf, "feed": "sip", "adjustment": "split", "limit": 10000,
         "start": z(now - datetime.timedelta(days=days)), "end": z(now - datetime.timedelta(minutes=16))}
    out = []
    while True:
        with urllib.request.urlopen(urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q), headers=hdr), timeout=60) as r:
            res = json.load(r)
        for b in (res.get("bars") or {}).get(sym, []):
            dt = datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(NY)
            out.append([dt.strftime("%Y-%m-%d %H:%M"), b["o"], b["h"], b["l"], b["c"], b["v"]])
        if not res.get("next_page_token"):
            return out
        q["page_token"] = res["next_page_token"]
res = {"saved_at": datetime.datetime.now(NY).isoformat(timespec="seconds")}
for s in sys.argv[2:]:
    try:
        res[s] = {"daily": alp(s, "1Day", 120), "m15": [b for b in alp(s, "15Min", 45) if "09:30" <= b[0][11:] < "16:00"]}
    except Exception:
        res[s] = {"error": traceback.format_exc()[-600:]}
json.dump(res, open(sys.argv[1], "w"), separators=(",", ":"))
