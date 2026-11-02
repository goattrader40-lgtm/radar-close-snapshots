#!/usr/bin/env python3
"""Live pre-market scanner for Theme & Group Radar (every 5 minutes, 7:00-9:29 AM ET).

  python3 radar/pmlive.py <stocks.json> <out premarket_live.json>

For every stock in stocks.json with a $300M+ market cap and 300K+ shares a day, today's pre-market 5-minute bars
(4:00-9:30 AM ET) from Yahoo give, the way TradingView's screener defines them:
  pm_last   latest pre-market price
  pm_chg    pre-market change % = pm_last vs the previous close
  pm_gap    pre-market gap %    = the first pre-market trade vs the previous close
The previous close is the last close in stocks.json (the after-close rebuild, the portal's Price column). Not
Yahoo's chartPreviousClose: until the open it is the close the day before that (Oct 28 2026: HRI showed +21.3%
against Monday's 127.13 instead of -1.1% against Tuesday's 156.00).
  pm_vol    pre-market volume (shares), pm_dvol = price x volume ($), pm_high / pm_low
Yahoo's pre-market bars carry no volume (always 0, checked Oct 26, 2026), so the volume comes from Alpaca's
consolidated-tape (SIP) 5-minute bars from 4:00 AM. The free Alpaca plan only serves SIP data older than 15 minutes,
so pre-market volume runs about 15 minutes behind the price ("vol_asof" in the file says to when).
The price is the newest of three: Yahoo's 5-minute bars, Yahoo's quote (preMarketPrice, live) and Alpaca's last SIP bar
(15 minutes old). Since the clock change on Nov 1 2026 Yahoo's pre-market bars stop at 8:30 AM ET (NXT and ENPH were
5%+ gappers by 9:00 that the 9:25 scan still showed at their 8:29 / 8:24 prices), so the quote is what keeps it current.
Writes {"saved_at", "date", "scanned", "vol_asof", "rows": {SYM: [pm_last, pm_chg, pm_gap, pm_vol, pm_dvol, pm_high, pm_low, "HH:MM"]}}
for every stock that has traded pre-market today. The portal applies your filters on top.
"""
import os
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


def scan(sym, today, prev):
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
    if not bars or not prev:
        return None
    last = bars[-1][4]
    vol = sum(b[5] for b in bars)
    return [round(last, 4), round((last / prev - 1) * 100, 2), round((bars[0][1] / prev - 1) * 100, 2), int(vol),
            round(sum(b[4] * b[5] for b in bars)), round(max(b[2] for b in bars), 4), round(min(b[3] for b in bars), 4),
            bars[-1][0].strftime("%H:%M")]


def alpaca_pm_volume(syms, today):
    """{sym: (volume, $ volume, last close, its bar time "HH:MM", first open)} from 4:00 AM to min(now - 16 min, 9:30)
    on the consolidated tape, plus that cut-off."""
    key, sec = os.environ.get("ALPACA_KEY_ID"), os.environ.get("ALPACA_SECRET")
    if not key or not sec:
        return {}, None
    hdr = {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": sec, "Accept": "application/json", "User-Agent": UA}
    t0 = datetime.datetime(today.year, today.month, today.day, 4, 0, tzinfo=NY)
    t1 = min(datetime.datetime.now(NY) - datetime.timedelta(minutes=16),
             datetime.datetime(today.year, today.month, today.day, 9, 29, 59, tzinfo=NY))
    if t1 <= t0:
        return {}, None
    out = {}
    names = [x.replace("/", ".") for x in syms]
    back = dict(zip(names, syms))
    for i in range(0, len(names), 200):
        q = {"symbols": ",".join(names[i:i + 200]), "timeframe": "5Min", "feed": "sip", "adjustment": "raw", "limit": 10000,
             "start": t0.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "end": t1.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
        while True:
            res = None
            for attempt in range(4):
                try:
                    url = "https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q)
                    with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=60) as r:
                        res = json.load(r)
                    break
                except Exception as e:
                    print(f"alpaca: {e}", file=sys.stderr)
                    time.sleep(2 * (attempt + 1))
            if res is None:
                return out, t1
            for a, rows in (res.get("bars") or {}).items():
                if not rows:
                    continue
                v = sum(b.get("v") or 0 for b in rows)
                dv = sum((b.get("vw") or b.get("c") or 0) * (b.get("v") or 0) for b in rows)
                s = back.get(a, a)
                pv, pd, _, _, fo = out.get(s, (0, 0, None, None, rows[0].get("o")))
                lt = datetime.datetime.fromisoformat(rows[-1]["t"].replace("Z", "+00:00")).astimezone(NY)
                out[s] = (pv + v, pd + dv, rows[-1].get("c"), (lt + datetime.timedelta(minutes=5)).strftime("%H:%M"), fo)
            if not res.get("next_page_token"):
                break
            q["page_token"] = res["next_page_token"]
            time.sleep(0.3)
    return out, t1


def plus5(hm):
    h, m = map(int, hm.split(":"))
    return f"{h + (m + 5) // 60:02d}:{(m + 5) % 60:02d}"


def yahoo_pm_quotes(syms):
    """{sym: (pre-market price, its time "HH:MM")} from Yahoo's quote, live, for today's pre-market trades"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from live import Yahoo, yahoo_sym                                 # noqa: E402
    y = Yahoo()
    if not y.login():
        print("yahoo quote: no crumb", file=sys.stderr)
        return {}
    ymap, out, today = {yahoo_sym(s): s for s in syms}, {}, datetime.datetime.now(NY).date()
    keys = list(ymap)
    for i in range(0, len(keys), 150):
        q = urllib.parse.urlencode({"symbols": ",".join(keys[i:i + 150]), "crumb": y.crumb, "fields": "preMarketPrice,preMarketTime"})
        try:
            res = json.loads(y.get("https://query2.finance.yahoo.com/v7/finance/quote?" + q))["quoteResponse"]["result"]
        except Exception as e:
            print(f"yahoo quote: {e}", file=sys.stderr)
            continue
        for r in res:
            p, tm = r.get("preMarketPrice"), r.get("preMarketTime")
            if p and tm:
                ts = datetime.datetime.fromtimestamp(tm, NY)
                if ts.date() == today and (ts.hour, ts.minute) < (9, 30):
                    out[ymap.get(r["symbol"], r["symbol"])] = (p, ts.strftime("%H:%M"))
    return out


def main():
    stocks_p, out_p = sys.argv[1], sys.argv[2]
    now = datetime.datetime.now(NY)
    stocks = json.load(open(stocks_p))
    syms = [r["symbol"] for r in stocks if (r.get("mcap_b") or 0) >= 0.3 and (r.get("avg_vol_30d") or 0) >= 300_000]
    close = {r["symbol"]: r.get("price") for r in stocks}          # the last close: what the pre-market change is from
    t0 = time.time()
    with cf.ThreadPoolExecutor(12) as pool:
        got = {s: v for s, v in zip(syms, pool.map(lambda x: scan(x, now.date(), close.get(x)), syms)) if v}
    if len(syms) and len(got) < 0.2 * len(syms):
        sys.exit(f"only {len(got)} of {len(syms)} had pre-market data, not saving")
    vols, vol_asof = alpaca_pm_volume(syms, now.date())
    quotes = yahoo_pm_quotes(syms)
    for s in syms:
        prev = close.get(s)
        if not prev:
            continue
        row = got.get(s)
        # the newest pre-market price of the three sources, each by when its price was printed (a 5-minute bar's close: its end)
        cands = ([(plus5(row[7]), row[0])] if row else []) + ([(vols[s][3], vols[s][2])] if s in vols and vols[s][2] else []) \
            + ([(quotes[s][1], quotes[s][0])] if s in quotes else [])
        if not cands:
            continue
        tm, px = max(cands)
        if row is None:                                           # no Yahoo bars: the first trade from Alpaca's bars
            fo = vols[s][4] if s in vols else None
            row = got[s] = [px, 0, round((fo / prev - 1) * 100, 2) if fo else None, 0, 0, px, px, tm]
        row[0], row[1], row[7] = round(px, 4), round((px / prev - 1) * 100, 2), tm
        row[5], row[6] = round(max(row[5], px), 4), round(min(row[6], px), 4)
        if s in vols:
            row[3], row[4] = int(vols[s][0]), round(vols[s][1])
    json.dump({"saved_at": now.isoformat(timespec="seconds"), "date": now.date().isoformat(), "scanned": len(syms),
               "vol_asof": vol_asof.strftime("%H:%M") if vol_asof else None, "vol_source": "alpaca sip" if vols else "none", "quotes": len(quotes),
               "rows": got}, open(out_p, "w"), separators=(",", ":"))
    print(json.dumps({"saved_at": now.isoformat(timespec="seconds"), "scanned": len(syms), "with_premarket": len(got),
                      "with_volume": sum(1 for r in got.values() if r[3]), "yahoo_quotes": len(quotes), "vol_asof": vol_asof.strftime("%H:%M") if vol_asof else None,
                      "seconds": round(time.time() - t0)}))


if __name__ == "__main__":
    main()
