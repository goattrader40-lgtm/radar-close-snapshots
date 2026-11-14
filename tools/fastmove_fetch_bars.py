#!/usr/bin/env python3
"""Download 1-minute bars from Alpaca (SIP) for the fast-move backtest. NOT part of the Radar portal.

  python3 tools/fastmove_fetch_bars.py <outdir> <start YYYY-MM-DD> <end YYYY-MM-DD> <tag> <SYM,SYM,...>

Regular session only (9:30 - 16:00 ET). One gzip CSV per symbol: <SYM>_<tag>.csv.gz with lines
date,minute(0 = 9:30),open,high,low,close,volume, plus status_<tag>.json (what was fetched, any errors).
Run by radar-tools.yml (cmd "bars ..."), which has the Alpaca keys; the files go to the fastmove-data branch.
"""
import datetime, gzip, json, os, sys, threading, time, urllib.error, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
HDR = {"APCA-API-KEY-ID": os.environ.get("ALPACA_KEY_ID", ""), "APCA-API-SECRET-KEY": os.environ.get("ALPACA_SECRET", ""),
       "Accept": "application/json"}
outdir, start, end, tag, syms = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5].split(",")
os.makedirs(outdir, exist_ok=True)
status = {"start": start, "end": end, "feed": "sip", "symbols": {}, "errors": [], "began": time.time()}
lock = threading.Lock()
DEADLINE = time.time() + 50 * 60          # the job is cut at 60 minutes: stop cleanly before that


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
    rows, token, pages = [], None, 0
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
                    rows.append(f"{t.date().isoformat()},{m},{b['o']},{b['h']},{b['l']},{b['c']},{b['v']}")
            token = res.get("next_page_token")
            if not token:
                break
        if rows:
            with gzip.open(os.path.join(outdir, f"{sym}_{tag}.csv.gz"), "wt") as f:
                f.write("\n".join(rows) + "\n")
        with lock:
            status["symbols"][sym] = {"bars": len(rows), "pages": pages, "days": len({r[:10] for r in rows})}
    except Exception as e:
        with lock:
            status["errors"].append({"symbol": sym, "error": str(e), "bars_so_far": len(rows)})


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
status["seconds"] = round(time.time() - status.pop("began"), 1)
status["have_keys"] = bool(HDR["APCA-API-KEY-ID"]) and bool(HDR["APCA-API-SECRET-KEY"])
json.dump(status, open(os.path.join(outdir, f"status_{tag}.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in status.items() if k != "symbols"}), len(status["symbols"]), "symbols")
