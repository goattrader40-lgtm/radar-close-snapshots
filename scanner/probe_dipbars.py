"""Daily bars for the DIP list's study (the user, Nov 21 2026: "show me last 22 months, only 2025 and 2026 until now"):
Yahoo's 5-year daily bars from 2023-11-01 on, for the stocks that were liquid at some point since Dec 2024 (price $5+,
20-day average volume 500K+ and $20M+ a day: looser than the 📈 box's numbers, so the study can vary them), plus SPY and
QQQ. Usage: python scanner/probe_dipbars.py OUT.json.gz   (radar-tools `dipbars` -> radar-data dip_bars.json.gz).
The longer study (the user, Nov 22 2026: "do you have numbers for 2022 until now?"):
  python scanner/probe_dipbars.py OUT_PREFIX 2020-12-01 2021-12-01 10y   -> OUT_PREFIX_a.json.gz (tickers A-L) and _b (M-Z),
two files to stay well under GitHub's file limit (radar-tools `dipbars22` -> radar-data dip_bars22_a / _b.json.gz).
A study file: the portal does not read it."""
import concurrent.futures as cf
import datetime
import gzip
import json
import sys
import time
import urllib.error

import fetch

FROM, LIQ_FROM, RANGE = "2023-11-01", "2024-12-01", "5y"


def bars(sym):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + sym.replace("/", "-").replace(".", "-") + "?range=" + RANGE + "&interval=1d"
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
    saved = datetime.datetime.now(fetch.NY).isoformat(timespec="seconds")
    parts = [(path, data)] if path.endswith(".gz") else [(path + "_a.json.gz", {k: v for k, v in data.items() if k < "M"}),
                                                          (path + "_b.json.gz", {k: v for k, v in data.items() if k >= "M"})]
    for p_, d_ in parts:
        with gzip.open(p_, "wt") as f:
            json.dump({"saved_at": saved, "fields": ["date", "open", "high", "low", "close", "volume"],
                       "market_cap": {s: caps.get(s) for s in d_}, "bars": d_}, f, separators=(",", ":"))


if __name__ == "__main__":
    if len(sys.argv) > 2:
        FROM, LIQ_FROM = sys.argv[2], sys.argv[3]
        RANGE = sys.argv[4] if len(sys.argv) > 4 else "10y"
    main(sys.argv[1])
