#!/usr/bin/env python3
"""Today's regular-session volume, Yahoo quote vs Alpaca SIP bars (same cut-off), plus Yahoo daily vs Alpaca daily for past days."""
import datetime, json, os, sys, urllib.parse, urllib.request, zoneinfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live import Yahoo
NY = zoneinfo.ZoneInfo("America/New_York")
hdr = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
syms = sys.argv[2:]
now = datetime.datetime.now(NY)
cut = now - datetime.timedelta(minutes=16)
d = now.date()
t0 = datetime.datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY)
def alp(path, q):
    with urllib.request.urlopen(urllib.request.Request("https://data.alpaca.markets/v2/stocks/" + path + "?" + urllib.parse.urlencode(q), headers=hdr), timeout=60) as r:
        return json.load(r)
out = {"now": now.isoformat(), "cut": cut.isoformat()}
y = Yahoo(); y.login()
q = y.quotes(syms)
bars = alp("bars", {"symbols": ",".join(syms), "timeframe": "1Min", "feed": "sip", "limit": 10000, "adjustment": "raw",
                    "start": t0.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "end": cut.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
daily = alp("bars", {"symbols": ",".join(syms), "timeframe": "1Day", "feed": "sip", "limit": 10000, "adjustment": "raw",
                     "start": (now - datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "end": (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")})
for s in syms:
    al = sum(b["v"] for b in (bars.get("bars") or {}).get(s, []))
    yq = q.get(s)
    ych = json.loads(y.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?range=1mo&interval=1d"))["chart"]["result"][0]
    yd = {datetime.datetime.fromtimestamp(t, NY).date().isoformat(): v for t, v in zip(ych["timestamp"], ych["indicators"]["quote"][0]["volume"])}
    ad = {b["t"][:10]: b["v"] for b in (daily.get("bars") or {}).get(s, [])}
    out[s] = {"yahoo_quote_vol_now": yq[2] if yq else None, "yahoo_quote_time": yq[3] if yq else None,
              "alpaca_sip_to_cut": al, "daily": {k: [yd.get(k), ad.get(k)] for k in sorted(ad)}}
json.dump(out, open(sys.argv[1], "w"), indent=1)
