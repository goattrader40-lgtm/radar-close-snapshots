#!/usr/bin/env python3
"""Daily bars of the scanner's universe from a start date, for the multi-year EP / gap study (a test tool only: the
scanner keeps reading its own 2-year download).

  python3 radar/probe_bars.py OUT.json.gz 2020-12-01

The same symbol list (Nasdaq's screener, the scanner's minimum market cap) and the same source (Yahoo's daily bars,
adjusted for splits) as scanner/fetch.py; only the start date differs. Today's listings and today's market caps: a stock
delisted since is not in it, and a stock is in or out of the size range by its size today."""
import concurrent.futures as cf, datetime, gzip, json, os, sys, time, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scanner"))
import fetch  # noqa: E402


def bars(sym, p1):
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/" + sym.replace("/", "-").replace(".", "-")
           + f"?period1={p1}&period2={int(time.time())}&interval=1d&includePrePost=false")
    for attempt in range(5):
        try:
            res = fetch.get(url)["chart"]["result"][0]
            q = res["indicators"]["quote"][0]
            out = []
            for t, o, h, l, c, v in zip(res.get("timestamp") or [], q.get("open") or [], q.get("high") or [],
                                        q.get("low") or [], q.get("close") or [], q.get("volume") or []):
                if None in (o, h, l, c):
                    continue
                d = datetime.datetime.fromtimestamp(t, fetch.NY).date().isoformat()
                row = [d, round(o, 4), round(h, 4), round(l, 4), round(c, 4), int(v or 0)]
                if out and out[-1][0] == d:
                    out[-1] = row
                else:
                    out.append(row)
            return sym, out if len(out) >= 30 else None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return sym, None
            time.sleep(4 * (attempt + 1))
        except Exception:
            time.sleep(4 * (attempt + 1))
    return sym, None


def main(path, start):
    p1 = int(datetime.datetime.fromisoformat(start).replace(tzinfo=fetch.NY).timestamp())
    caps, exch = fetch.symbols()
    syms = sorted(caps) + ["SPY", "QQQ"]
    print(f"{len(syms)} symbols from {start}")
    data = {}
    with cf.ThreadPoolExecutor(10) as pool:
        for sym, b in pool.map(lambda s: bars(s, p1), syms):
            if b:
                data[sym] = b
    print(f"{len(data)} symbols downloaded; SPY {data['SPY'][0][0]} - {data['SPY'][-1][0]}" if "SPY" in data else "no SPY")
    if "SPY" not in data or len(data) < 0.8 * len(syms):
        sys.exit(f"only {len(data)} of {len(syms)} came back")
    with gzip.open(path, "wt") as f:
        json.dump({"saved_at": datetime.datetime.now(fetch.NY).isoformat(timespec="seconds"),
                   "fields": ["date", "open", "high", "low", "close", "volume"],
                   "market_cap": caps, "exchange": exch, "bars": data}, f, separators=(",", ":"))
    print("size MB", round(os.path.getsize(path) / 1e6, 1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
