#!/usr/bin/env python3
"""Time a few Alpaca SIP bar requests and save what happened (out.json)."""
import datetime, json, os, sys, time, urllib.error, urllib.parse, urllib.request
out = {"steps": []}
hdr = {"APCA-API-KEY-ID": os.environ.get("ALPACA_KEY_ID", ""), "APCA-API-SECRET-KEY": os.environ.get("ALPACA_SECRET", ""),
       "Accept": "application/json"}
out["have_keys"] = bool(hdr["APCA-API-KEY-ID"]) and bool(hdr["APCA-API-SECRET-KEY"])
now = datetime.datetime.now(datetime.timezone.utc)
start = (now - datetime.timedelta(days=40)).strftime("%Y-%m-%dT%H:%M:%SZ")
end = (now - datetime.timedelta(minutes=16)).strftime("%Y-%m-%dT%H:%M:%SZ")
syms = sys.argv[2].split(",")
for feed in ("sip", "iex"):
    token, pages, nb = None, 0, 0
    t0 = time.time()
    while pages < 4:
        q = {"symbols": ",".join(syms), "timeframe": "5Min", "start": start, "end": end, "limit": 10000, "feed": feed, "adjustment": "raw"}
        if token: q["page_token"] = token
        try:
            t1 = time.time()
            with urllib.request.urlopen(urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q), headers=hdr), timeout=60) as r:
                res = json.load(r)
            n = sum(len(v) for v in (res.get("bars") or {}).values())
            nb += n; pages += 1
            out["steps"].append({"feed": feed, "page": pages, "bars": n, "secs": round(time.time() - t1, 2), "symbols_in_page": list((res.get("bars") or {}).keys())[:3]})
            token = res.get("next_page_token")
            if not token: break
        except urllib.error.HTTPError as e:
            out["steps"].append({"feed": feed, "error": e.code, "body": e.read().decode(errors="replace")[:300]}); break
        except Exception as e:
            out["steps"].append({"feed": feed, "error": str(e)}); break
    out[feed] = {"pages": pages, "bars": nb, "secs": round(time.time() - t0, 1), "more": bool(token)}
# daily volume check for NVDA: SIP daily bars vs what Yahoo reported
try:
    q = {"symbols": "NVDA,CRWD,CIEN", "timeframe": "1Day", "start": start, "end": end, "feed": "sip", "adjustment": "raw"}
    with urllib.request.urlopen(urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q), headers=hdr), timeout=60) as r:
        res = json.load(r)
    out["daily"] = {s: [(b["t"][:10], b["v"]) for b in v[-5:]] for s, v in res["bars"].items()}
except Exception as e:
    out["daily_error"] = str(e)
json.dump(out, open(sys.argv[1], "w"), indent=1)
