#!/usr/bin/env python3
"""Pre-market trades (Alpaca SIP) for a few stocks: total volume vs volume without odd lots (<100 shares), by time."""
import datetime, json, os, sys, urllib.parse, urllib.request, zoneinfo
NY = zoneinfo.ZoneInfo("America/New_York")
hdr = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
d = datetime.datetime.now(NY).date()
t0 = datetime.datetime(d.year, d.month, d.day, 4, 0, tzinfo=NY).astimezone(datetime.timezone.utc)
t1 = datetime.datetime(d.year, d.month, d.day, 9, 29, 59, tzinfo=NY).astimezone(datetime.timezone.utc)
out = {}
for s in sys.argv[2:]:
    q = {"start": t0.strftime("%Y-%m-%dT%H:%M:%SZ"), "end": t1.strftime("%Y-%m-%dT%H:%M:%SZ"), "limit": 10000, "feed": "sip"}
    tot, big, conds, by = 0, 0, {}, {}
    while True:
        with urllib.request.urlopen(urllib.request.Request(f"https://data.alpaca.markets/v2/stocks/{s}/trades?" + urllib.parse.urlencode(q), headers=hdr), timeout=60) as r:
            res = json.load(r)
        for t in res.get("trades") or []:
            sz = t["s"]; tot += sz
            if sz >= 100: big += sz
            for c in t.get("c") or []: conds[c] = conds.get(c, 0) + sz
            hm = datetime.datetime.fromisoformat(t["t"][:19] + "+00:00").astimezone(NY).strftime("%H:%M")
            b = by.setdefault(hm, [0, 0]); b[0] += sz; b[1] += sz if sz >= 100 else 0
        if not res.get("next_page_token"): break
        q["page_token"] = res["next_page_token"]
    cum, a, bb = {}, 0, 0
    for hm in sorted(by):
        a += by[hm][0]; bb += by[hm][1]; cum[hm] = [a, bb]
    out[s] = {"trades": sum(1 for _ in ()), "total": tot, "no_odd_lots": big, "conditions": conds, "cum": cum}
json.dump(out, open(sys.argv[1], "w"))
