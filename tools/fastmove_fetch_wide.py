#!/usr/bin/env python3
"""Download bars from Alpaca (SIP) for the wide stock list of the fast-move backtest. NOT part of the Radar portal.

  python3 tools/fastmove_fetch_wide.py <outdir> <start YYYY-MM-DD> <end YYYY-MM-DD> <tag>

Symbols: tools/fastmove_universe.txt. Regular session only. To keep the files small: 1-minute bars for the first hour
(9:30 - 10:30 ET), 5-minute bars after that. Files wide_<tag>_<nn>.csv.gz (40 symbols each) with lines
symbol,date,minute(0 = 9:30),open,high,low,close,volume, plus status_<tag>.json.
"""
import datetime, gzip, json, os, sys, threading, time, urllib.error, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
HDR = {"APCA-API-KEY-ID": os.environ.get("ALPACA_KEY_ID", ""), "APCA-API-SECRET-KEY": os.environ.get("ALPACA_SECRET", ""),
       "Accept": "application/json"}
outdir, start, end, tag = sys.argv[1:5]
syms = [l.strip() for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fastmove_universe.txt")) if l.strip() and not l.startswith("#")]
os.makedirs(outdir, exist_ok=True)
status = {"start": start, "end": end, "feed": "sip", "symbols": {}, "errors": [], "began": time.time()}
lock = threading.Lock(); data = {}
DEADLINE = time.time() + 48 * 60


def get(q):
    for attempt in range(6):
        try:
            req = urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q), headers=HDR)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5 + 5 * attempt); continue
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:200]}")
        except Exception:
            time.sleep(2 + 2 * attempt)
    raise RuntimeError("no answer after 6 tries")


def one(sym):
    days, token, pages = {}, None, 0
    try:
        while True:
            if time.time() > DEADLINE:
                raise RuntimeError("out of time")
            q = {"symbols": sym, "timeframe": "1Min", "start": start + "T00:00:00Z", "end": end + "T00:00:00Z", "limit": 10000,
                 "feed": "sip", "adjustment": "split"}
            if token:
                q["page_token"] = token
            res = get(q); pages += 1
            for b in (res.get("bars") or {}).get(sym, []):
                t = datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(NY)
                m = t.hour * 60 + t.minute - 570
                if 0 <= m < 390:
                    k = m if m < 60 else 60 + (m - 60) // 5 * 5          # 1-minute for the first hour, 5-minute buckets after
                    d = days.setdefault(t.date().isoformat(), {})
                    if k not in d:
                        d[k] = [b["o"], b["h"], b["l"], b["c"], b["v"]]
                    else:
                        x = d[k]; x[1] = max(x[1], b["h"]); x[2] = min(x[2], b["l"]); x[3] = b["c"]; x[4] += b["v"]
            token = res.get("next_page_token")
            if not token:
                break
        rows = [f"{sym},{day},{k},{x[0]:.4g},{x[1]:.4g},{x[2]:.4g},{x[3]:.4g},{int(x[4])}" if False else f"{sym},{day},{k},{round(x[0], 3)},{round(x[1], 3)},{round(x[2], 3)},{round(x[3], 3)},{int(x[4])}"
                for day in sorted(days) for k, x in sorted(days[day].items())]
        with lock:
            data[sym] = rows; status["symbols"][sym] = {"bars": len(rows), "pages": pages, "days": len(days)}
    except Exception as e:
        with lock:
            status["errors"].append({"symbol": sym, "error": str(e)})


queue = list(syms)


def worker():
    while True:
        with lock:
            if not queue:
                return
            s = queue.pop(0)
        one(s)


threads = [threading.Thread(target=worker) for _ in range(3)]
for t in threads: t.start()
for t in threads: t.join()
done = sorted(data)
for n in range(0, len(done), 40):
    with gzip.open(os.path.join(outdir, f"wide_{tag}_{n // 40:02d}.csv.gz"), "wt", compresslevel=9) as f:
        for s in done[n:n + 40]:
            f.write("\n".join(data[s]) + "\n")
status["seconds"] = round(time.time() - status.pop("began"), 1)
status["have_keys"] = bool(HDR["APCA-API-KEY-ID"]) and bool(HDR["APCA-API-SECRET-KEY"])
json.dump(status, open(os.path.join(outdir, f"status_{tag}.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in status.items() if k != "symbols"}), len(status["symbols"]), "symbols")
