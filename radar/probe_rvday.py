#!/usr/bin/env python3
"""Replay a session's relative volume at time, minute by minute: the portal's method vs the exact number.

  python3 radar/probe_rvday.py <out.json> SYM ...   (run after the close; needs ALPACA_KEY_ID / ALPACA_SECRET)

exact  = Alpaca SIP volume 9:30 -> minute / the previous 20 sessions' SIP volume 9:30 -> the same minute
portal = Yahoo volume 9:30 -> minute (1-minute bars, which add up to the live quote) / the 5-minute curve
         from those same 20 sessions, interpolated, as radar/live.py does
Also the full day (Yahoo quote now vs SIP daily bar) and the after-close number live.py now shows.
"""
import datetime, json, os, statistics, sys, urllib.parse, urllib.request, zoneinfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live import Yahoo, rvol_at

NY = zoneinfo.ZoneInfo("America/New_York")
UTC = datetime.timezone.utc
hdr = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
syms = sys.argv[2:]
z = lambda t: t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def alp(q):
    out, q = {}, dict(q, feed="sip", adjustment="raw", limit=10000)
    while True:
        with urllib.request.urlopen(urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q),
                                                           headers=hdr), timeout=60) as r:
            res = json.load(r)
        for s, rows in (res.get("bars") or {}).items():
            out.setdefault(s, []).extend(rows)
        if not res.get("next_page_token"):
            return out
        q["page_token"] = res["next_page_token"]


now = datetime.datetime.now(NY)
spy = alp({"symbols": "SPY", "timeframe": "1Day", "start": z(now - datetime.timedelta(days=45)), "end": z(now - datetime.timedelta(minutes=16))})["SPY"]
sess = [datetime.date.fromisoformat(b["t"][:10]) for b in spy]
day = sess[-1]                       # the session to replay (today, once it has closed)
prev = sess[-21:-1]
print("replaying", day, "against", prev[0], "..", prev[-1], file=sys.stderr)


def minutes(rows):
    """{date: [390 per-minute volumes 9:30-3:59]}"""
    d = {}
    for b in rows:
        t = datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(NY)
        m = t.hour * 60 + t.minute - 570
        if 0 <= m < 390:
            d.setdefault(t.date(), [0] * 390)[m] += b["v"]
    return d


def cum(v):
    out, a = [0], 0
    for x in v:
        a += x
        out.append(a)
    return out                        # out[m] = volume from 9:30 to 9:30 + m minutes


bars = {}
for d in prev + [day]:
    t0 = datetime.datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY)
    for s, rows in alp({"symbols": ",".join(syms), "timeframe": "1Min", "start": z(t0), "end": z(t0 + datetime.timedelta(minutes=390))}).items():
        bars.setdefault(s, []).extend(rows)
daily = alp({"symbols": ",".join(syms), "timeframe": "1Day", "start": str(prev[0]), "end": z(now - datetime.timedelta(minutes=16))})
y = Yahoo()
y.login()
quote = y.quotes(syms)
out = {"now": now.isoformat(timespec="seconds"), "day": str(day), "prev": [str(prev[0]), str(prev[-1])], "rows": {}}
for s in syms:
    md = minutes(bars.get(s, []))
    have = [d for d in prev if d in md]
    if day not in md or len(have) < 10:
        out["rows"][s] = "not enough SIP bars"
        continue
    curves = [cum(md[d]) for d in have]
    avg1 = [sum(c[m] for c in curves) / len(curves) for m in range(391)]
    curve5 = [round(avg1[5 * (j + 1)]) for j in range(78)]          # what volprofile.py saves
    sip = cum(md[day])
    ych = json.loads(y.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?range=5d&interval=1m&includePrePost=false"))["chart"]["result"][0]
    yv = [0] * 390
    for t, v in zip(ych.get("timestamp") or [], ych["indicators"]["quote"][0].get("volume") or []):
        ts = datetime.datetime.fromtimestamp(t, NY)
        m = ts.hour * 60 + ts.minute - 570
        if ts.date() == day and 0 <= m < 390:
            yv[m] += v or 0
    yc = cum(yv)
    pts, diffs = [], []
    for m in range(5, 391):
        t = datetime.datetime(day.year, day.month, day.day, 9, 30, tzinfo=NY) + datetime.timedelta(minutes=m)
        exact = sip[m] / avg1[m] if avg1[m] else None
        portal = rvol_at(yc[m], t.timestamp() - 1e-3 if m == 390 else t.timestamp(), curve5)
        if exact and portal:
            diffs.append(portal / exact - 1)
            if m % 30 == 0 or m in (5, 15, 385, 390):
                pts.append([t.strftime("%H:%M"), round(exact, 2), portal, round(yc[m] / sip[m], 3)])
    dd = {b["t"][:10]: b["v"] for b in daily.get(s, [])}
    prev_full = [dd[str(d)] for d in prev if str(d) in dd]
    q = quote.get(s)
    out["rows"][s] = {
        "times [time, exact, portal, yahoo/sip volume]": pts,
        "portal_vs_exact_pct": {"median": round(100 * statistics.median(diffs), 1), "worst_low": round(100 * min(diffs), 1),
                                "worst_high": round(100 * max(diffs), 1), "minutes": len(diffs)},
        "after_close": {"yahoo_quote_vol": q[2] if q else None, "sip_daily_vol": dd.get(str(day)),
                        "exact_full_day": round(dd[str(day)] / statistics.mean(prev_full), 2) if str(day) in dd and prev_full else None},
    }
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps({s: (r["portal_vs_exact_pct"] if isinstance(r, dict) else r) for s, r in out["rows"].items()}))
