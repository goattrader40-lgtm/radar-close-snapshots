#!/usr/bin/env python3
"""Live pre-market scanner for Theme & Group Radar (every 5 minutes, 7:00-9:29 AM ET).

  python3 radar/pmlive.py <stocks.json> <out premarket_live.json>

For every stock in stocks.json with a $300M+ market cap and 300K+ shares a day, today's pre-market 5-minute bars
(4:00-9:30 AM ET) from Yahoo give, the way TradingView's screener defines them:
  pm_last   latest pre-market price
  pm_chg    pre-market change % = pm_last vs the previous close
  pm_gap    pre-market gap %    = the first pre-market trade vs the previous close
  pm_vol    pre-market volume (shares), pm_dvol = price x volume ($), pm_high / pm_low
Writes {"saved_at", "date", "scanned", "rows": {SYM: [pm_last, pm_chg, pm_gap, pm_vol, pm_dvol, pm_high, pm_low, "HH:MM"]}}
for every stock that has traded pre-market today. The portal applies your filters on top.
"""
import concurrent.futures as cf, datetime, json, sys, time, urllib.error, urllib.parse, urllib.request, zoneinfo

NY = zoneinfo.ZoneInfo("America/New_York")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, text/plain, */*"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.load(r)["chart"]["result"][0]
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(2 * (attempt + 1))
        except Exception:
            time.sleep(2 * (attempt + 1))
    return None


def scan(sym, today):
    ys = urllib.parse.quote(sym.replace("/", "-").replace(".", "-"))
    r = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{ys}?range=1d&interval=5m&includePrePost=true")
    if not r:
        return None
    q = r["indicators"]["quote"][0]
    bars = []
    for t, o, h, l, c, v in zip(r.get("timestamp") or [], q.get("open") or [], q.get("high") or [], q.get("low") or [],
                                q.get("close") or [], q.get("volume") or []):
        ts = datetime.datetime.fromtimestamp(t, NY)
        if ts.date() == today and (ts.hour, ts.minute) < (9, 30) and c is not None:
            bars.append((ts, o or c, h or c, l or c, c, v or 0))
    prev = (r.get("meta") or {}).get("chartPreviousClose") or (r.get("meta") or {}).get("previousClose")
    if not bars or not prev:
        return None
    last = bars[-1][4]
    vol = sum(b[5] for b in bars)
    return [round(last, 4), round((last / prev - 1) * 100, 2), round((bars[0][1] / prev - 1) * 100, 2), int(vol),
            round(sum(b[4] * b[5] for b in bars)), round(max(b[2] for b in bars), 4), round(min(b[3] for b in bars), 4),
            bars[-1][0].strftime("%H:%M")]


def main():
    stocks_p, out_p = sys.argv[1], sys.argv[2]
    now = datetime.datetime.now(NY)
    syms = [r["symbol"] for r in json.load(open(stocks_p))
            if (r.get("mcap_b") or 0) >= 0.3 and (r.get("avg_vol_30d") or 0) >= 300_000]
    t0 = time.time()
    with cf.ThreadPoolExecutor(12) as pool:
        got = {s: v for s, v in zip(syms, pool.map(lambda x: scan(x, now.date()), syms)) if v}
    if len(syms) and len(got) < 0.2 * len(syms):
        sys.exit(f"only {len(got)} of {len(syms)} had pre-market data, not saving")
    json.dump({"saved_at": now.isoformat(timespec="seconds"), "date": now.date().isoformat(), "scanned": len(syms),
               "rows": got}, open(out_p, "w"), separators=(",", ":"))
    print(json.dumps({"saved_at": now.isoformat(timespec="seconds"), "scanned": len(syms), "with_premarket": len(got),
                      "seconds": round(time.time() - t0)}))


if __name__ == "__main__":
    main()
