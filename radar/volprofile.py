#!/usr/bin/env python3
"""Average intraday volume curve per stock, for relative volume at time.

  python3 radar/volprofile.py <stocks.json> <out volprofile.json> [--days 20]

For each stock: the last 20 complete regular sessions of Yahoo 5-minute bars (9:30-4:00 ET) give the
volume traded from 9:30 up to each 5-minute mark. Checked Oct 26, 2026: during the session the 5-minute bars
add up to the live quote's volume (0.995-0.999 for most stocks); what they miss of the full day (about 13%)
is the closing auction and late prints after 4:00, so the curves are NOT scaled up to the daily volume.
A day whose bars add up to less than 60% or more than 110% of that day's daily-bar volume is a Yahoo data
glitch and is skipped. Output: {"date": last session used, "days": 20, "rows": {SYM: [78 numbers]}}, where
number j is the 20-day average volume from 9:30 to 9:30 + 5*(j+1) minutes.

Relative volume at time = today's volume so far / that average at the same minute (interpolated).

With ALPACA_KEY_ID and ALPACA_SECRET set (GitHub secrets), the curves come from Alpaca's historical 5-minute
bars on the consolidated tape (feed=sip: every US exchange plus off-exchange prints, the same volume TradingView
counts). The free plan allows SIP history except the latest 15 minutes, which this never needs. Without keys,
or if Alpaca fails, it falls back to Yahoo's 5-minute bars (rougher: some days are 1.2-2.8x too high).
"""
import os
import concurrent.futures as cf, datetime, json, sys, time, urllib.error, urllib.parse, urllib.request, zoneinfo

NY = zoneinfo.ZoneInfo("America/New_York")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
SLOTS = 78
MIN_DAYS = 10


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, text/plain, */*"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.load(r)["chart"]["result"][0]
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(2 * (attempt + 1))
        except Exception:
            time.sleep(2 * (attempt + 1))
    return None


def profile(sym, days):
    ys = urllib.parse.quote(sym.replace("/", "-").replace(".", "-"))
    base = f"https://query1.finance.yahoo.com/v8/finance/chart/{ys}?includePrePost=false"
    intra, daily = get(base + "&range=60d&interval=5m"), get(base + "&range=3mo&interval=1d")
    if not intra or not daily:
        return None
    full = {}
    for t, v in zip(daily.get("timestamp") or [], (daily["indicators"]["quote"][0].get("volume") or [])):
        if v:
            full[datetime.datetime.fromtimestamp(t, NY).date()] = v
    by_day = {}
    q = intra["indicators"]["quote"][0]
    for t, v in zip(intra.get("timestamp") or [], q.get("volume") or []):
        ts = datetime.datetime.fromtimestamp(t, NY)
        j = ((ts.hour * 60 + ts.minute) - 570) // 5
        if 0 <= j < SLOTS:
            by_day.setdefault(ts.date(), [0] * SLOTS)[j] += v or 0
    now = datetime.datetime.now(NY)
    unfinished = now.date() if (now.hour, now.minute) < (16, 5) else None   # today's session isn't complete yet
    curves = []
    for d in sorted(by_day, reverse=True):
        if d == unfinished:
            continue
        bars = by_day[d]
        tot = sum(bars)
        if d not in full or tot <= 0 or sum(1 for b in bars if b) < 60:   # skip half days and gappy days
            continue
        if not 0.6 <= tot / full[d] <= 1.1:                                 # Yahoo glitch day
            continue
        acc, cum = 0, []
        for b in bars:
            acc += b
            cum.append(acc)
        curves.append((d, cum))
        if len(curves) == days:
            break
    if len(curves) < MIN_DAYS:
        return None
    avg = [round(sum(c[j] for _, c in curves) / len(curves)) for j in range(SLOTS)]
    return curves[0][0], avg


ALPACA = "https://data.alpaca.markets/v2/stocks/bars"


def alpaca_curves(syms, days):
    """{sym: (last date, [78 cumulative averages])} from Alpaca SIP 5-minute bars, or None if unavailable."""
    key, sec = os.environ.get("ALPACA_KEY_ID"), os.environ.get("ALPACA_SECRET")
    if not key or not sec:
        return None
    hdr = {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": sec, "Accept": "application/json", "User-Agent": UA}
    now = datetime.datetime.now(datetime.timezone.utc)
    start = (now - datetime.timedelta(days=days * 7 // 5 + 12)).strftime("%Y-%m-%dT%H:%M:%SZ")
    end = (now - datetime.timedelta(minutes=16)).strftime("%Y-%m-%dT%H:%M:%SZ")
    asym = {s.replace("/", "."): s for s in syms}
    bars = {}                                   # sym -> date -> [78 slot volumes]
    calls, t_last = 0, 0.0
    names = sorted(set(asym) | {"SPY"})
    for i in range(0, len(names), 200):
        chunk = names[i:i + 200]
        token = None
        while True:
            q = {"symbols": ",".join(chunk), "timeframe": "5Min", "start": start, "end": end, "limit": 10000,
                 "feed": "sip", "adjustment": "raw", "sort": "asc"}
            if token:
                q["page_token"] = token
            url = ALPACA + "?" + urllib.parse.urlencode(q)
            for attempt in range(5):
                wait = 0.31 - (time.time() - t_last)          # stay under 200 calls a minute
                if wait > 0:
                    time.sleep(wait)
                t_last = time.time()
                try:
                    with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=60) as r:
                        res = json.load(r)
                    break
                except urllib.error.HTTPError as e:
                    body = e.read().decode(errors="replace")[:300]
                    if e.code in (401, 403):
                        print(f"alpaca refused ({e.code}): {body}", file=sys.stderr)
                        return None
                    if attempt == 4:
                        print(f"alpaca failed ({e.code}): {body}", file=sys.stderr)
                        return None
                    time.sleep(3 * (attempt + 1))
                except Exception as e:
                    if attempt == 4:
                        print(f"alpaca failed: {e}", file=sys.stderr)
                        return None
                    time.sleep(3 * (attempt + 1))
            calls += 1
            for sym, rows in (res.get("bars") or {}).items():
                for b in rows:
                    ts = datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(NY)
                    j = ((ts.hour * 60 + ts.minute) - 570) // 5
                    if 0 <= j < SLOTS:
                        bars.setdefault(sym, {}).setdefault(ts.date(), [0] * SLOTS)[j] += b.get("v") or 0
            token = res.get("next_page_token")
            if not token:
                break
    # full sessions = days SPY traded through the 3:55 PM bar (drops half days); today only once it's complete
    spy = bars.get("SPY", {})
    unfinished = datetime.datetime.now(NY).date() if hm_now() < (16, 5) else None
    full = sorted((d for d, v in spy.items() if v[-1] > 0 and d != unfinished), reverse=True)[:days]
    print(f"alpaca: {calls} calls, {len(bars)} symbols with bars, sessions {full[-1] if full else '-'}..{full[0] if full else '-'}",
          file=sys.stderr)
    if len(full) < MIN_DAYS:
        return None
    out = {}
    for a, s in asym.items():
        dd = bars.get(a)
        if not dd or sum(1 for d in full if d in dd) < MIN_DAYS:   # too new or too thin to average
            continue
        acc = [0.0] * SLOTS
        for d in full:
            v = dd.get(d, [0] * SLOTS)
            c = 0
            for j in range(SLOTS):
                c += v[j]
                acc[j] += c
        out[s] = (full[0], [round(x / len(full)) for x in acc])
    return out


def hm_now():
    t = datetime.datetime.now(NY)
    return (t.hour, t.minute)


def main():
    stocks_p, out_p = sys.argv[1], sys.argv[2]
    days = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 20
    syms = [r["symbol"] for r in json.load(open(stocks_p))]
    rows, last = {}, None
    t0 = time.time()
    got = alpaca_curves(syms, days)
    source = "alpaca sip"
    if got and len(got) >= 0.5 * len(syms):
        for s, (d, avg) in got.items():
            rows[s] = avg
            last = max(last, d) if last else d
    else:
        source = "yahoo"
        with cf.ThreadPoolExecutor(12) as pool:
            for s, res in zip(syms, pool.map(lambda x: profile(x, days), syms)):
                if res:
                    d, avg = res
                    rows[s] = avg
                    last = max(last, d) if last else d
    if len(rows) < 0.5 * len(syms):
        sys.exit(f"only {len(rows)} of {len(syms)} volume curves came back, not saving")
    json.dump({"date": str(last), "days": days, "source": source, "built_at": datetime.datetime.now(NY).isoformat(timespec="seconds"),
               "rows": rows}, open(out_p, "w"), separators=(",", ":"))
    print(json.dumps({"date": str(last), "source": source, "stocks": len(rows), "of": len(syms), "seconds": round(time.time() - t0)}))


if __name__ == "__main__":
    main()
