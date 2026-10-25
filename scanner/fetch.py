"""Downloads 2 years of daily bars for every US stock over the scanner's minimum market cap, plus SPY.
Usage: python scanner/fetch.py OUT.json.gz
Symbol list, market cap and exchange come from Nasdaq's screener; bars from Yahoo Finance."""
import concurrent.futures as cf
import datetime
import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.request
import zoneinfo

NY = zoneinfo.ZoneInfo("America/New_York")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
     "Accept": "application/json, text/plain, */*", "Accept-Language": "en-US,en;q=0.9"}
SETTINGS = json.load(open(os.path.join(os.path.dirname(__file__), "settings.json")))


def get(url, headers=H, timeout=30):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as r:
        return json.load(r)


def symbols():
    NH = dict(H, Origin="https://www.nasdaq.com", Referer="https://www.nasdaq.com/")
    caps, exch = {}, {}
    for ex in ("nasdaq", "nyse", "amex"):
        url = f"https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&offset=0&exchange={ex}&download=true"
        rows = None
        for attempt in range(3):
            try:
                rows = get(url, NH, 60)["data"]["rows"]
                break
            except Exception as e:
                print(f"{ex} list: attempt {attempt + 1} failed: {e}")
                time.sleep(10)
        if not rows:
            sys.exit(f"could not download the {ex} list")
        for r in rows:
            try:
                mc = float(r.get("marketCap") or 0)
            except ValueError:
                mc = 0
            s = (r.get("symbol") or "").strip()
            if s and mc >= SETTINGS["standard"]["min_mcap"] and "^" not in s:
                caps[s] = mc
                exch[s] = ex.upper()
    return caps, exch


def bars(sym):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + sym.replace("/", "-").replace(".", "-") + "?range=2y&interval=1d"
    for attempt in range(5):
        try:
            res = get(url)["chart"]["result"][0]
            q = res["indicators"]["quote"][0]
            out = []
            for t, o, h, l, c, v in zip(res.get("timestamp") or [], q.get("open") or [], q.get("high") or [],
                                        q.get("low") or [], q.get("close") or [], q.get("volume") or []):
                if None in (o, h, l, c):
                    continue
                d = datetime.datetime.fromtimestamp(t, NY).date().isoformat()
                if out and out[-1][0] == d:
                    out[-1] = [d, round(o, 4), round(h, 4), round(l, 4), round(c, 4), int(v or 0)]
                else:
                    out.append([d, round(o, 4), round(h, 4), round(l, 4), round(c, 4), int(v or 0)])
            return sym, out if len(out) >= 30 else None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return sym, None
            time.sleep(4 * (attempt + 1))
        except Exception:
            time.sleep(4 * (attempt + 1))
    return sym, None


def main(path):
    caps, exch = symbols()
    syms = sorted(caps) + ["SPY"]
    print(f"{len(syms)} symbols")
    data = {}
    with cf.ThreadPoolExecutor(10) as pool:
        for sym, b in pool.map(bars, syms):
            if b:
                data[sym] = b
    print(f"{len(data)} symbols downloaded")
    if "SPY" not in data or len(data) < 0.8 * len(syms):
        sys.exit(f"only {len(data)} of {len(syms)} came back")
    with gzip.open(path, "wt") as f:
        json.dump({"saved_at": datetime.datetime.now(NY).isoformat(timespec="seconds"),
                   "fields": ["date", "open", "high", "low", "close", "volume"],
                   "market_cap": caps, "exchange": exch, "bars": data}, f, separators=(",", ":"))


if __name__ == "__main__":
    main(sys.argv[1])
