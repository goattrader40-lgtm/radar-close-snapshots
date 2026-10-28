#!/usr/bin/env python3
"""Replay today's alerts for a few stocks from the exact minute bars, as the 5-minute live job would have seen them.

  python3 radar/probe_replay.py <out.json> SYM ...   (needs ALPACA_KEY_ID / ALPACA_SECRET; the last 16 minutes aren't out yet)

At each 5-minute check (9:35:20, 9:40:20, ...; --every-minute: each minute from 9:31:20, with the early heads-ups
until 9:35): price = the last complete minute's close, volume = Alpaca SIP volume
from 9:30 to that minute, Rel vol from the volume curves (volprofile.json), the open = the first minute's open,
earnings time from the latest live.json; then radar/alerts.py's rules against last night's watch list
(setups/launch.json). Lists every check's numbers and each alert the first time it fires.
"""
import datetime, json, os, subprocess, sys, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alerts
from live import rvol_at

NY = alerts.NY
UTC = datetime.timezone.utc
hdr = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
syms = [a for a in sys.argv[2:] if not a.startswith("--")]
z = lambda t: t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
show = lambda name: subprocess.run(["git", "show", name], capture_output=True, text=True).stdout

subprocess.run(["git", "fetch", "-q", "--depth", "1", "origin", "+refs/heads/radar-data:refs/remotes/origin/radar-data"])
prof = json.loads(show("origin/radar-data:volprofile.json"))["rows"]
live = json.loads(show("origin/radar-data:live.json"))["rows"]
doc = json.load(open("setups/launch.json"))
now = datetime.datetime.now(NY)
t0 = now.replace(hour=9, minute=30, second=0, microsecond=0)
q = {"symbols": ",".join(syms), "timeframe": "1Min", "feed": "sip", "adjustment": "raw", "limit": 10000,
     "start": z(t0), "end": z(min(now - datetime.timedelta(minutes=16), t0 + datetime.timedelta(minutes=390)))}
bars = {}
while True:
    with urllib.request.urlopen(urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q),
                                                       headers=hdr), timeout=60) as r:
        res = json.load(r)
    for s, rows in (res.get("bars") or {}).items():
        bars.setdefault(s, []).extend(rows)
    if not res.get("next_page_token"):
        break
    q["page_token"] = res["next_page_token"]
for s in bars:
    for b in bars[s]:
        b["ts"] = datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).timestamp()
out, sent = {"date": str(now.date()), "watch_from": doc["date"], "checks": {s: [] for s in syms}, "alerts": []}, set()
every = "--every-minute" in sys.argv
t = t0 + datetime.timedelta(minutes=1 if every else 5, seconds=20)
step = datetime.timedelta(minutes=1 if every else 5)
while t.timestamp() + 60 <= now.timestamp() - 16 * 60 and t.hour < 16:
    rows = {}
    for s in syms:
        done = [b for b in bars.get(s, []) if b["ts"] + 60 <= t.timestamp()]          # minutes complete by the check
        w = doc["watch"].get(s)
        if not done or not w:
            continue
        price, vol, qt = done[-1]["c"], sum(b["v"] for b in done), done[-1]["ts"] + 60 - 1e-3
        op = bars[s][0]["o"]
        lv = live.get(s) or []
        row = [price, round(100 * (price / w[0] - 1), 3), vol, qt, rvol_at(vol, qt, prof.get(s)), op, lv[6] if len(lv) > 6 else None]
        rows[s] = row
        out["checks"][s].append([t.strftime("%H:%M"), price, row[1], round(100 * (op / w[0] - 1), 1), row[4], round(max(b["h"] for b in done), 2)])
    early = (t.hour, t.minute) < (9, 35)
    for a in (alerts.find_early if early else alerts.find)({"rows": rows}, doc, t):
        if a[0] not in sent:
            sent.add(a[0])
            out["alerts"].append([t.strftime("%H:%M"), a[1], a[2]])
    t += step
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out["alerts"], indent=1))
