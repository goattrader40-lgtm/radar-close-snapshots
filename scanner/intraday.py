"""Saves today's 5-minute bars for every stock whose day came near its 21 or 50 EMA under the 21 / 50 EMA
pullback trigger's daily rules, so the triggers can be tested on more and more real days.
Usage: python scanner/intraday.py BARS.json.gz   →  appends to history/intraday/YYYY-MM.json.gz"""
import concurrent.futures as cf
import datetime
import gzip
import json
import os
import sys
import time
import urllib.request
import zoneinfo

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import msf  # noqa: E402

NY = zoneinfo.ZoneInfo("America/New_York")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def candidates(D):
    """stocks whose day today touched within 1% of yesterday's 21 / 50 EMA after opening above it, with the
    trigger's daily gates (liquid, above the 200 SMA, 4th+ day since the 20-day high, within 20 / 25% of it)"""
    bench = {b[0]: b[4] for b in D["bars"]["SPY"]}
    day = D["bars"]["SPY"][-1][0]
    p = msf.params()
    out = []
    for s, bars in D["bars"].items():
        if s == "SPY" or len(bars) < 260 or bars[-1][0] != day:
            continue
        df = msf.run_symbol(bars, bench, p)
        i = len(df) - 1; y = i - 1
        Hh = df.high.values
        w = Hh[y - 19:y + 1]
        hb = 19 - np.where(w == w.max())[0][-1]
        hi20 = w.max()
        o, l, c = df.open.values[i], df.low.values[i], df.close.values[i]
        if not (df.liquid.values[y] == 1 and c > df.sma200.values[y] and hb + 1 >= 4):
            continue
        e10, e21, e50 = df.ema10.values[y], df.ema21.values[y], df.ema50.values[y]
        ok21 = e10 > e21 > e50 and o > e21 and l <= e21 * 1.01 and l >= hi20 * 0.80
        ok50 = o > e50 and l <= e50 * 1.01 and l >= hi20 * 0.75
        if ok21 or ok50:
            out.append(s)
    return day, out


def bars5(sym, day):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + sym.replace("/", "-").replace(".", "-") + "?range=5d&interval=5m"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30) as r:
                res = json.load(r)["chart"]["result"][0]
            q = res["indicators"]["quote"][0]
            rows = []
            for t, o, h, l, c, v in zip(res.get("timestamp") or [], q["open"], q["high"], q["low"], q["close"], q["volume"]):
                if None in (o, h, l, c):
                    continue
                dt = datetime.datetime.fromtimestamp(t, NY)
                if dt.date().isoformat() == day:
                    rows.append([dt.strftime("%H:%M"), round(o, 4), round(h, 4), round(l, 4), round(c, 4), int(v or 0)])
            return sym, rows
        except Exception:
            time.sleep(3 * (attempt + 1))
    return sym, None


def main(path):
    with gzip.open(path, "rt") as f:
        D = json.load(f)
    day, syms = candidates(D)
    print(day, len(syms), "candidates")
    got = {}
    with cf.ThreadPoolExecutor(8) as pool:
        for s, rows in pool.map(lambda x: bars5(x, day), syms):
            if rows:
                got[s] = rows
    os.makedirs(os.path.join(os.path.dirname(HERE), "history", "intraday"), exist_ok=True)
    out = os.path.join(os.path.dirname(HERE), "history", "intraday", day[:7] + ".json.gz")
    doc = {"fields": ["time", "open", "high", "low", "close", "volume"], "bars": {}}
    if os.path.exists(out):
        with gzip.open(out, "rt") as f:
            doc = json.load(f)
    for s, rows in got.items():
        doc["bars"].setdefault(s, {})[day] = rows
    with gzip.open(out, "wt") as f:
        json.dump(doc, f, separators=(",", ":"))
    print(len(got), "saved to", out)


if __name__ == "__main__":
    main(sys.argv[1])
