#!/usr/bin/env python3
"""Download bars from Alpaca (SIP) for the stock-days of the fast-move backtest on the Watchlist lists. NOT part of the portal.

  python3 tools/fastmove_fetch_days.py <outdir> days  <start YYYY-MM-DD> <end YYYY-MM-DD> <tag>
  python3 tools/fastmove_fetch_days.py <outdir> hours <start YYYY-MM-DD> <end YYYY-MM-DD> <tag>

The request is tools/fastmove_days.json.gz: {"days": {date: [symbols]}, "symbols": [...]}.
days:  for each date from start up to (not including) end, the listed symbols' regular session: 1-minute bars for the first
       hour, 5-minute bars after it. Files days_<tag>_<nn>.csv.gz with lines symbol,date,minute(0 = 9:30),open,high,low,close,volume.
hours: for every symbol, the hourly closes of the regular session (10:30, 11:30 ... 15:30, 16:00) from 30-minute bars.
       Files hours_<tag>_<nn>.csv.gz with lines symbol,date,hour(0-6),close.
Both write status_<tag>.json.
"""
import datetime, gzip, json, os, sys, threading, time, urllib.error, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
HDR = {"APCA-API-KEY-ID": os.environ.get("ALPACA_KEY_ID", ""), "APCA-API-SECRET-KEY": os.environ.get("ALPACA_SECRET", ""),
       "Accept": "application/json"}
outdir, mode, start, end, tag = sys.argv[1:6]
REQ = json.load(gzip.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fastmove_days.json.gz"), "rt"))
os.makedirs(outdir, exist_ok=True)
status = {"mode": mode, "start": start, "end": end, "feed": "sip", "errors": [], "tasks": 0, "done": 0, "pages": 0, "rows": 0, "began": time.time()}
lock = threading.Lock()
DEADLINE = time.time() + 46 * 60
PART = [0, 0, None]                                   # file number, rows in it, handle


def write(lines):
    with lock:
        if PART[2] is None or PART[1] >= 1500000:
            if PART[2] is not None:
                PART[2].close(); PART[0] += 1
            PART[2] = gzip.open(os.path.join(outdir, f"{mode}_{tag}_{PART[0]:02d}.csv.gz"), "wt", compresslevel=6); PART[1] = 0
        PART[2].write("\n".join(lines) + "\n"); PART[1] += len(lines); status["rows"] += len(lines)


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


def pages(q):
    token = None
    while True:
        if time.time() > DEADLINE:
            raise RuntimeError("out of time")
        if token:
            q["page_token"] = token
        res = get(q)
        with lock:
            status["pages"] += 1
        yield res.get("bars") or {}
        token = res.get("next_page_token")
        if not token:
            return


def day_task(day, syms):
    acc = {}
    q = {"symbols": ",".join(syms), "timeframe": "1Min", "start": day + "T13:00:00Z", "end": day + "T21:30:00Z", "limit": 10000,
         "feed": "sip", "adjustment": "split"}
    for bars in pages(q):
        for sym, bs in bars.items():
            d = acc.setdefault(sym, {})
            for b in bs:
                t = datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(NY)
                m = t.hour * 60 + t.minute - 570
                if 0 <= m < 390 and t.date().isoformat() == day:
                    k = m if m < 60 else 60 + (m - 60) // 5 * 5
                    if k not in d:
                        d[k] = [b["o"], b["h"], b["l"], b["c"], b["v"]]
                    else:
                        x = d[k]; x[1] = max(x[1], b["h"]); x[2] = min(x[2], b["l"]); x[3] = b["c"]; x[4] += b["v"]
    lines = [f"{sym},{day},{k},{round(x[0], 3)},{round(x[1], 3)},{round(x[2], 3)},{round(x[3], 3)},{int(x[4])}"
             for sym in sorted(acc) for k, x in sorted(acc[sym].items())]
    if lines:
        write(lines)


KEEP = {(10, 0): 0, (11, 0): 1, (12, 0): 2, (13, 0): 3, (14, 0): 4, (15, 0): 5, (15, 30): 6}      # 30-minute bars that end an hour of the session


def hour_task(_, syms):
    lines = []
    q = {"symbols": ",".join(syms), "timeframe": "30Min", "start": start + "T00:00:00Z", "end": end + "T00:00:00Z", "limit": 10000,
         "feed": "sip", "adjustment": "split"}
    for bars in pages(q):
        for sym, bs in bars.items():
            for b in bs:
                t = datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(NY)
                k = KEEP.get((t.hour, t.minute))
                if k is not None:
                    lines.append(f"{sym},{t.date().isoformat()},{k},{round(b['c'], 3)}")
    if lines:
        write(lines)


if mode == "days":
    tasks = [(d, s[i:i + 40]) for d, s in sorted(REQ["days"].items()) if start <= d < end for i in range(0, len(s), 40)]
    run = day_task
else:
    s = REQ["symbols"]
    tasks = [("", s[i:i + 8]) for i in range(0, len(s), 8)]
    run = hour_task
status["tasks"] = len(tasks)
queue = list(tasks)


def worker():
    while True:
        with lock:
            if not queue:
                return
            t = queue.pop(0)
        try:
            run(*t)
            with lock:
                status["done"] += 1
        except Exception as e:
            with lock:
                status["errors"].append({"task": [t[0], t[1][:3]], "error": str(e)[:200]})


threads = [threading.Thread(target=worker) for _ in range(3)]
for t in threads: t.start()
for t in threads: t.join()
if PART[2] is not None:
    PART[2].close()
status["seconds"] = round(time.time() - status.pop("began"), 1)
status["have_keys"] = bool(HDR["APCA-API-KEY-ID"]) and bool(HDR["APCA-API-SECRET-KEY"])
status["errors"] = status["errors"][:40]
json.dump(status, open(os.path.join(outdir, f"status_{tag}.json"), "w"), indent=1)
print(json.dumps(status))
