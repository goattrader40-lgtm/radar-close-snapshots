#!/usr/bin/env python3
"""Check the portal's live relative volume during market hours against the exact number.

  python3 radar/probe_rvlive.py <out.json> SYM ...   (run between 9:45 and 3:40 ET; needs ALPACA_KEY_ID / ALPACA_SECRET)

Takes the Yahoo quotes the 5-minute live job uses and the volume curves it uses (volprofile.json on radar-data),
works out Rel vol as radar/live.py does without its SIP correction, then waits 16 minutes (the free SIP plan's
delay) and compares:
  volume:  Yahoo quote volume vs Alpaca SIP volume 9:30 -> the quote's second (all US exchanges + off-exchange)
  rel vol: raw vs exact = SIP volume to that second / the 20-day SIP average to the same second (1-minute bars)
  portal:  the same for the live.json the portal was showing at the start (volume corrected by radar/sipcal.py)
"""
import datetime, json, os, statistics, subprocess, sys, time, urllib.parse, urllib.request, zoneinfo
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
subprocess.run(["git", "fetch", "-q", "--depth", "1", "origin", "+refs/heads/radar-data:refs/remotes/origin/radar-data"])
live = json.loads(subprocess.run(["git", "show", "origin/radar-data:live.json"], capture_output=True, text=True).stdout)["rows"]
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
t4 = datetime.datetime(day.year, day.month, day.day, 4, 0, tzinfo=NY)
pre_vol = {s: sum(b["v"] for b in rows) for s, rows in alp({"symbols": ",".join(syms), "timeframe": "1Min", "start": z(t4),
                                                            "end": z(t4 + datetime.timedelta(minutes=330))}).items()}
out = {"quotes_at": now.isoformat(timespec="seconds"), "curves_through": prof["date"], "avg_of": [str(prev[0]), str(prev[-1])], "rows": {}}
vr, rr, pv, pr = [], [], [], []
for s in syms:
    q, md = quote.get(s), minutes(bars.get(s, []))
    if not q or day not in md:
        out["rows"][s] = "no quote or no SIP bars"
        continue
    qt = datetime.datetime.fromtimestamp(q[3], NY)
    x = (qt.hour * 60 + qt.minute + qt.second / 60) - 570
    sip_vol = at(md[day], x)
    pre = pre_vol.get(s)                       # SIP volume 4:00-9:30 today (pre-market)
    have = [md[d] for d in prev if d in md]
    avg = statistics.mean(at(v, x) for v in have)
    portal = rvol_at(q[2], q[3], prof["rows"].get(s))
    exact = round(sip_vol / avg, 2) if avg else None
    out["rows"][s] = {"quote_time": qt.strftime("%H:%M:%S"), "yahoo_vol": q[2], "sip_vol": round(sip_vol), "sip_premarket": pre,
                      "yahoo_minus_premarket_vs_sip_pct": round(100 * ((q[2] - pre) / sip_vol - 1), 1) if pre is not None else None,
                      "yahoo_vs_sip_pct": round(100 * (q[2] / sip_vol - 1), 1), "raw_rel_vol": portal, "exact": exact,
                      "raw_vs_exact_pct": round(100 * (portal / exact - 1), 1) if portal and exact else None}
    lv = live.get(s)                                 # what the portal showed: [price, chg, volume, time, rel vol, ...]
    if lv and lv[2] and lv[3] and lv[4]:
        xl = (datetime.datetime.fromtimestamp(lv[3], NY) - datetime.datetime(day.year, day.month, day.day, 9, 30, tzinfo=NY)).total_seconds() / 60
        if 1 <= xl < 390:
            sl, al_ = at(md[day], xl), statistics.mean(at(v, xl) for v in have)
            out["rows"][s]["portal_live"] = {"quote_time": datetime.datetime.fromtimestamp(lv[3], NY).strftime("%H:%M:%S"),
                                             "vol": lv[2], "sip_vol": round(sl), "vol_vs_sip_pct": round(100 * (lv[2] / sl - 1), 1),
                                             "rel_vol": lv[4], "exact": round(sl / al_, 2),
                                             "rel_vol_vs_exact_pct": round(100 * (lv[4] / (sl / al_) - 1), 1)}
            pv.append(out["rows"][s]["portal_live"]["vol_vs_sip_pct"])
            pr.append(out["rows"][s]["portal_live"]["rel_vol_vs_exact_pct"])
    vr.append(out["rows"][s]["yahoo_vs_sip_pct"])
    if out["rows"][s]["raw_vs_exact_pct"] is not None:
        rr.append(out["rows"][s]["raw_vs_exact_pct"])
rng = lambda a: {"median": statistics.median(a), "min": min(a), "max": max(a)} if a else None
out["summary"] = {"volume_yahoo_vs_sip_pct": rng(vr), "relvol_raw_vs_exact_pct": rng(rr),
                  "portal_volume_vs_sip_pct": rng(pv), "portal_relvol_vs_exact_pct": rng(pr)}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out["summary"]))
