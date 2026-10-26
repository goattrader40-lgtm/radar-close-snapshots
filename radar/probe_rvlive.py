#!/usr/bin/env python3
"""Check the portal's live relative volume during market hours against the exact number.

  python3 radar/probe_rvlive.py <out.json> SYM ...   (run between 9:45 and 3:40 ET; needs ALPACA_KEY_ID / ALPACA_SECRET)

Takes the Yahoo quotes the 5-minute live job uses and the volume curves it uses (volprofile.json on radar-data),
works out Rel vol exactly as radar/live.py does, then waits 16 minutes (the free SIP plan's delay) and compares:
  volume:  Yahoo quote volume vs Alpaca SIP volume 9:30 -> the quote's second (all US exchanges + off-exchange)
  rel vol: portal vs exact = SIP volume to that second / the 20-day SIP average to the same second (1-minute bars)
"""
import datetime, json, os, statistics, sys, time, urllib.parse, urllib.request, zoneinfo
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


def minutes(rows):
    d = {}
    for b in rows:
        t = datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(NY)
        m = t.hour * 60 + t.minute - 570
        if 0 <= m < 390:
            d.setdefault(t.date(), [0] * 390)[m] += b["v"]
    return d


def at(per_min, x):
    """volume from 9:30 to x minutes after 9:30 (x may be fractional: the last minute counts in proportion)"""
    k = int(x)
    return sum(per_min[:k]) + (per_min[k] * (x - k) if k < 390 else 0)


prof = json.load(urllib.request.urlopen(
    "https://raw.githubusercontent.com/goattrader40-lgtm/radar-close-snapshots/refs/heads/radar-data/volprofile.json", timeout=60))
y = Yahoo()
y.login()
quote = y.quotes(syms)
now = datetime.datetime.now(NY)
qmax = max(q[3] for q in quote.values())
wait = qmax + 16.5 * 60 - time.time()
print(f"quotes at {now:%H:%M:%S}, curves through {prof['date']}; waiting {wait / 60:.1f} min for SIP", file=sys.stderr)
if wait > 0:
    time.sleep(wait)
day = now.date()
spy = alp({"symbols": "SPY", "timeframe": "1Day", "start": z(now - datetime.timedelta(days=45)), "end": z(now - datetime.timedelta(days=1))})["SPY"]
prev = [datetime.date.fromisoformat(b["t"][:10]) for b in spy if b["t"][:10] <= prof["date"]][-20:]
bars = {}
for d in prev + [day]:
    t0 = datetime.datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY)
    t1 = min(t0 + datetime.timedelta(minutes=390), datetime.datetime.now(NY) - datetime.timedelta(minutes=16))
    for s, rows in alp({"symbols": ",".join(syms), "timeframe": "1Min", "start": z(t0), "end": z(t1)}).items():
        bars.setdefault(s, []).extend(rows)
out = {"quotes_at": now.isoformat(timespec="seconds"), "curves_through": prof["date"], "avg_of": [str(prev[0]), str(prev[-1])], "rows": {}}
vr, rr = [], []
for s in syms:
    q, md = quote.get(s), minutes(bars.get(s, []))
    if not q or day not in md:
        out["rows"][s] = "no quote or no SIP bars"
        continue
    qt = datetime.datetime.fromtimestamp(q[3], NY)
    x = (qt.hour * 60 + qt.minute + qt.second / 60) - 570
    sip_vol = at(md[day], x)
    have = [md[d] for d in prev if d in md]
    avg = statistics.mean(at(v, x) for v in have)
    portal = rvol_at(q[2], q[3], prof["rows"].get(s))
    exact = round(sip_vol / avg, 2) if avg else None
    out["rows"][s] = {"quote_time": qt.strftime("%H:%M:%S"), "yahoo_vol": q[2], "sip_vol": round(sip_vol),
                      "yahoo_vs_sip_pct": round(100 * (q[2] / sip_vol - 1), 1), "portal": portal, "exact": exact,
                      "portal_vs_exact_pct": round(100 * (portal / exact - 1), 1) if portal and exact else None}
    vr.append(out["rows"][s]["yahoo_vs_sip_pct"])
    if out["rows"][s]["portal_vs_exact_pct"] is not None:
        rr.append(out["rows"][s]["portal_vs_exact_pct"])
out["summary"] = {"volume_yahoo_vs_sip_pct": {"median": statistics.median(vr), "min": min(vr), "max": max(vr)} if vr else None,
                  "relvol_portal_vs_exact_pct": {"median": statistics.median(rr), "min": min(rr), "max": max(rr)} if rr else None}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out["summary"]))
