#!/usr/bin/env python3
"""Why each gap-down happened: the SEC's 8-Ks and the morning's headlines (the gap-down short study; the user, Nov 24 2026:
"we had one special thing shown, earnings day gap downs ... you need to look at those as well"). A test tool only.

  python3 radar/probe_gapnews.py history/gapdown_news_request.json /tmp/gapdown_news.json.gz

The request is {date: {"prev": the session before, "syms": [symbols]}}. Saved:
  sec    {SYMBOL: [[accepted (New York time), form, items], ...]}  every 8-K / 8-K/A / 6-K since Dec 2022 (item 2.02 =
         results of operations: the earnings release); null when the SEC doesn't know the ticker
  news   {"date SYMBOL": [[created (UTC), headline], ...]}  Alpaca's news (Benzinga) from the close of the session before
         to the open of the gap day"""
import datetime, gzip, json, os, sys, time, urllib.error, urllib.parse, urllib.request, zoneinfo
import codegrade as G

NY = zoneinfo.ZoneInfo("America/New_York")
HDR = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}


def headlines(syms, t_from, t_to):
    z = lambda t: t.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = {}
    for i in range(0, len(syms), 50):
        chunk, tok = set(syms[i:i + 50]), None
        for _ in range(60):
            q = {"symbols": ",".join(sorted(chunk)), "start": z(t_from), "end": z(t_to), "limit": 50, "sort": "asc"}
            if tok:
                q["page_token"] = tok
            for attempt in range(5):
                try:
                    with urllib.request.urlopen(urllib.request.Request("https://data.alpaca.markets/v1beta1/news?" + urllib.parse.urlencode(q), headers=HDR), timeout=40) as r:
                        d = json.load(r)
                    break
                except urllib.error.HTTPError as e:
                    if e.code == 429 or e.code >= 500:
                        time.sleep(5 * (attempt + 1))
                        continue
                    raise
            else:
                raise RuntimeError("alpaca news kept failing")
            for n in d.get("news", []):
                for s in set(n.get("symbols") or []) & chunk:
                    out.setdefault(s, []).append([n.get("created_at"), n.get("headline")])
            tok = d.get("next_page_token")
            time.sleep(0.32)
            if not tok:
                break
    return out


def main():
    req = json.load(open(sys.argv[1]))
    errors, sec, news = [], {}, {}
    syms = sorted({s for v in req.values() for s in v["syms"]})
    G.FILINGS_SINCE = "2022-12-01"
    t0, t1 = datetime.datetime(2022, 12, 1, tzinfo=NY), datetime.datetime.now(NY)
    for i, s in enumerate(syms):
        try:
            fs = G.filings(s.replace("/", "-"), t0, t1)
            sec[s] = None if fs is None else [[f["at"].strftime("%Y-%m-%dT%H:%M"), f["form"], f["items"]] for f in fs if f["form"] in ("8-K", "8-K/A", "6-K")]
        except Exception as e:
            errors.append(f"sec {s}: {e}")
        if i % 200 == 0:
            print("sec", i, len(syms), flush=True)
    for k, (date, v) in enumerate(sorted(req.items())):
        d, p = datetime.date.fromisoformat(date), datetime.date.fromisoformat(v["prev"])
        try:
            H = headlines([s.replace("/", ".") for s in v["syms"]], datetime.datetime(p.year, p.month, p.day, 16, 0, tzinfo=NY),
                          datetime.datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY))
        except Exception as e:
            errors.append(f"news {date}: {e}")
            continue
        for s, a in H.items():
            news[f"{date} {s.replace('.', '/')}"] = a
        if k % 50 == 0:
            print("news", date, len(news), flush=True)
    with gzip.open(sys.argv[2], "wt") as f:
        json.dump({"symbols": len(syms), "sec_known": sum(1 for v in sec.values() if v is not None), "stock_days_with_news": len(news),
                   "errors": errors[:80], "sec": sec, "news": news}, f, separators=(",", ":"))


if __name__ == "__main__":
    main()
