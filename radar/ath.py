#!/usr/bin/env python3
"""Each stock's ALL-TIME HIGH range, from Yahoo's full history, for the morning breakout boxes' "Above: ATH" level.

  python3 radar/ath.py <stocks.json> <out ath.json> [SYM ...]

The user, Nov 21 2026: the morning breakout boxes get tick boxes "1M / 3M / 6M / 9M / 52W / ATH / Broken support"; the
alert fires only over the top of a ticked level that was overhead at the last close. The scan's daily bars reach 2 years
back, so the all-time high comes from here: per stock Yahoo's monthly history (range=max; the high of the month with the
highest high = the all-time high), then the daily bars of that month and of every other month whose high is over the
highest daily close found, for the highest CLOSE (the bottom of the range, as the other levels: highest close to highest
high). Split-adjusted as Yahoo serves it; the row keeps a reference close (the last full session) so the scan can see a
split since and rescale (scanner/launch.py ath_range). Run every Saturday (.github/workflows/ath.yml) and by hand.
Rows: {SYM: {high, high_date, close, close_date, ref_date, ref_close}}.
"""
import concurrent.futures as cf, datetime, json, sys, time, urllib.error, urllib.parse, urllib.request, zoneinfo
NY = zoneinfo.ZoneInfo("America/New_York")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def chart(sym, q):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym.replace('/', '-').replace('.', '-'))}?{q}&includePrePost=false"
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30) as r:
                res = json.load(r)["chart"]["result"][0]
            qd = res["indicators"]["quote"][0]
            return [(datetime.datetime.fromtimestamp(t, NY).date(), h, c) for t, h, c in
                    zip(res.get("timestamp") or [], qd.get("high") or [], qd.get("close") or []) if h and c]
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(2 + 3 * attempt)
        except Exception:
            time.sleep(2 + 3 * attempt)
    return None


def month_span(d):
    a = datetime.datetime(d.year, d.month, 1, tzinfo=NY)
    b = datetime.datetime(d.year + (d.month == 12), d.month % 12 + 1, 1, tzinfo=NY)
    return int(a.timestamp()), int(b.timestamp()) + 86400 * 5     # (a few days over: Yahoo's month stamps sit on the 1st)


def one(sym, today):
    mo = chart(sym, "range=max&interval=1mo")
    if not mo:
        return None
    months = sorted(mo, key=lambda x: -x[1])
    best_h, best_hd, best_c, best_cd, seen = 0.0, None, 0.0, None, set()
    for d, mh, _ in months[:6]:                         # the months that can hold the highest close, highest high first
        if seen and mh <= best_c:
            break
        a, b = month_span(d)
        days = chart(sym, f"period1={a}&period2={b}&interval=1d")
        seen.add(d)
        for dd, h, c in days or []:
            if dd >= today:
                continue
            if h > best_h:
                best_h, best_hd = h, dd
            if c > best_c:
                best_c, best_cd = c, dd
    if not best_hd:
        return None
    last = chart(sym, "range=10d&interval=1d") or []
    ref = [x for x in last if x[0] < today]
    if not ref:
        return None
    return dict(high=round(best_h, 4), high_date=best_hd.isoformat(), close=round(best_c, 4), close_date=best_cd.isoformat(),
                ref_date=ref[-1][0].isoformat(), ref_close=round(ref[-1][2], 4))


def main():
    stocks_p, out_p = sys.argv[1:3]
    syms = sys.argv[3:] or sorted({r["symbol"] for r in json.load(open(stocks_p)) if r.get("symbol")})
    today = datetime.datetime.now(NY).date()
    rows, miss, t0 = {}, [], time.time()
    with cf.ThreadPoolExecutor(8) as ex:
        for s, r in zip(syms, ex.map(lambda s_: one(s_, today), syms)):
            if r:
                rows[s] = r
            else:
                miss.append(s)
    if len(rows) < 0.8 * len(syms):
        sys.exit(f"ath: only {len(rows)} of {len(syms)} stocks read: not saved")
    json.dump({"saved_at": datetime.datetime.now(NY).isoformat(timespec="seconds"), "n": len(rows), "missing": miss[:300],
               "rows": rows}, open(out_p, "w"), separators=(",", ":"))
    print(f"ath: {len(rows)} stocks in {time.time() - t0:.0f}s, {len(miss)} missing ({' '.join(miss[:20])})")


if __name__ == "__main__":
    main()
