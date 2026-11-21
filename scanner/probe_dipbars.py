"""Daily bars for the DIP list's study (the user, Nov 21 2026: "show me last 22 months, only 2025 and 2026 until now"):
Yahoo's 5-year daily bars from 2023-11-01 on, for the stocks that were liquid at some point since Dec 2024 (price $5+,
20-day average volume 500K+ and $20M+ a day: looser than the 📈 box's numbers, so the study can vary them), plus SPY and
QQQ. Usage: python scanner/probe_dipbars.py OUT.json.gz   (radar-tools `dipbars` -> radar-data dip_bars.json.gz).
A study file: the portal does not read it."""
import concurrent.futures as cf
import datetime
import gzip
import json
import sys
import time
import urllib.error

import fetch

FROM, LIQ_FROM = "2023-11-01", "2024-12-01"


def bars(sym):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + sym.replace("/", "-").replace(".", "-") + "?range=5y&interval=1d"
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
                if d < FROM:
                    continue
                row = [d, round(o, 3), round(h, 3), round(l, 3), round(c, 3), int(v or 0)]
                if out and out[-1][0] == d:
                    out[-1] = row
                else:
                    out.append(row)
            return sym, out if len(out) >= 60 else None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return sym, None
            time.sleep(4 * (attempt + 1))
        except Exception:
            time.sleep(4 * (attempt + 1))
    return sym, None


def liquid(b):
    """liquid on any day since LIQ_FROM: close $5+, the 20 sessions' average volume 500K+ and $ volume $20M+"""
    for i in range(19, len(b)):
        if b[i][0] < LIQ_FROM or b[i][4] < 5:
            continue
        w = b[i - 19:i + 1]
        if sum(x[5] for x in w) / 20 >= 500e3 and sum(x[4] * x[5] for x in w) / 20 >= 20e6:
            return True
    return False


def main(path):
    caps, exch = fetch.symbols()
    syms = sorted(caps) + ["SPY", "QQQ"]
    data, got = {}, 0
    with cf.ThreadPoolExecutor(10) as pool:
        for sym, b in pool.map(bars, syms):
            if b:
                got += 1
                if sym in ("SPY", "QQQ") or liquid(b):
                    data[sym] = b
    print(f"{len(syms)} symbols, {got} downloaded, {len(data)} kept (liquid since {LIQ_FROM}); last bar {data['SPY'][-1][0]}")
    if "SPY" not in data or got < 0.8 * len(syms):
        sys.exit(f"only {got} of {len(syms)} came back")
    with gzip.open(path, "wt") as f:
        json.dump({"saved_at": datetime.datetime.now(fetch.NY).isoformat(timespec="seconds"),
                   "fields": ["date", "open", "high", "low", "close", "volume"],
                   "market_cap": {s: caps.get(s) for s in data}, "bars": data}, f, separators=(",", ":"))


if __name__ == "__main__":
    main(sys.argv[1])
