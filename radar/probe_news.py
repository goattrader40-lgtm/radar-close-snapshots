#!/usr/bin/env python3
"""Which headline source has a stock's news (the user, Nov 6 2026: FLY gapped on news with AST, and the SEC had nothing).

  python3 radar/probe_news.py <out.json> <from ISO> <to ISO> SYM [SYM ...]

Alpaca's news API (Benzinga, the keys the pre-market volume uses) for all the symbols in the window, and Yahoo's search
news per symbol, saved side by side to compare what each one has and when.
"""
import datetime, json, os, sys, time, urllib.parse, urllib.request

out, t_from, t_to, syms = sys.argv[1], sys.argv[2], sys.argv[3], [s.upper() for s in sys.argv[4:]]
NY = datetime.timezone(datetime.timedelta(hours=-5))
iso = lambda s: datetime.datetime.fromisoformat(s).replace(tzinfo=datetime.datetime.fromisoformat(s).tzinfo or NY)
a, b = iso(t_from), iso(t_to)
res = {"from": a.isoformat(), "to": b.isoformat(), "symbols": syms}

hdr = {"APCA-API-KEY-ID": os.environ.get("ALPACA_KEY_ID", ""), "APCA-API-SECRET-KEY": os.environ.get("ALPACA_SECRET", "")}
items, tok, t0 = [], None, time.time()
try:
    for _ in range(20):
        q = {"symbols": ",".join(syms), "start": a.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "end": b.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "limit": 50, "sort": "desc"}
        if tok:
            q["page_token"] = tok
        rq = urllib.request.Request("https://data.alpaca.markets/v1beta1/news?" + urllib.parse.urlencode(q), headers=hdr)
        with urllib.request.urlopen(rq, timeout=30) as r:
            d = json.load(r)
        items += [{k: n.get(k) for k in ("created_at", "headline", "summary", "source", "author", "url", "symbols")} for n in d.get("news", [])]
        tok = d.get("next_page_token")
        if not tok:
            break
    res["alpaca"] = {"ok": True, "n": len(items), "secs": round(time.time() - t0, 1), "items": items}
except Exception as e:
    res["alpaca"] = {"ok": False, "error": repr(e)[:300], "items": items}

ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
yh = {}
for s in syms:
    try:
        u = "https://query1.finance.yahoo.com/v1/finance/search?" + urllib.parse.urlencode({"q": s, "quotesCount": 0, "newsCount": 12})
        with urllib.request.urlopen(urllib.request.Request(u, headers=ua), timeout=20) as r:
            d = json.load(r)
        yh[s] = [{"at": datetime.datetime.fromtimestamp(n.get("providerPublishTime", 0), NY).isoformat(), "title": n.get("title"),
                  "publisher": n.get("publisher"), "link": n.get("link"), "tickers": n.get("relatedTickers")} for n in d.get("news", [])]
    except Exception as e:
        yh[s] = {"error": repr(e)[:200]}
    time.sleep(0.3)
res["yahoo"] = yh
json.dump(res, open(out, "w"), indent=1)
print(json.dumps({"alpaca": {k: v for k, v in res["alpaca"].items() if k != "items"}, "yahoo": {s: (len(v) if isinstance(v, list) else v) for s, v in yh.items()}}))
for n in items[:40]:
    print(n["created_at"], ",".join(n["symbols"] or [])[:40], "|", n["headline"][:140])
