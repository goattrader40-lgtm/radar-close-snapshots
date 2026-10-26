#!/usr/bin/env python3
"""Pre-market volume by time (Alpaca SIP 1-minute bars, 4:00-9:30 today), to compare with TradingView.
  python3 radar/probe_pmvol.py <out.json> SYM ..."""
import datetime, json, os, sys, urllib.parse, urllib.request, zoneinfo
NY = zoneinfo.ZoneInfo("America/New_York")
hdr = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
d = datetime.datetime.now(NY).date()
t0 = datetime.datetime(d.year, d.month, d.day, 4, 0, tzinfo=NY).astimezone(datetime.timezone.utc)
t1 = datetime.datetime(d.year, d.month, d.day, 9, 29, 59, tzinfo=NY).astimezone(datetime.timezone.utc)
out = {}
for feed in ("sip", "iex"):
    q = {"symbols": ",".join(sys.argv[2:]), "timeframe": "1Min", "feed": feed, "adjustment": "raw", "limit": 10000,
         "start": t0.strftime("%Y-%m-%dT%H:%M:%SZ"), "end": t1.strftime("%Y-%m-%dT%H:%M:%SZ")}
    bars = {}
    while True:
        with urllib.request.urlopen(urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q), headers=hdr), timeout=60) as r:
            res = json.load(r)
        for s, rows in (res.get("bars") or {}).items():
            bars.setdefault(s, []).extend([(b["t"], b["v"], b.get("n")) for b in rows])
        if not res.get("next_page_token"): break
        q["page_token"] = res["next_page_token"]
    for s, rows in bars.items():
        cum, acc = {}, 0
        for t, v, n in rows:
            acc += v
            cum[datetime.datetime.fromisoformat(t.replace("Z", "+00:00")).astimezone(NY).strftime("%H:%M")] = acc
        out.setdefault(s, {})[feed] = cum
json.dump(out, open(sys.argv[1], "w"))
