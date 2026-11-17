#!/usr/bin/env python3
"""The morning breakout's rules on the last N sessions' 1-minute bars, split by the trend rules: how did the stocks that
are NOT in an uptrend do the same day, against the ones that are (the user, Nov 16 2026: an alert like the morning
breakout for the stocks it leaves out; "check last 30-40 days see how it was, which failed same day or not").

  python3 radar/probe_mover.py <stocks.json> <volprofile.json> <out.json> [days=35]     (needs ALPACA_KEY_ID / ALPACA_SECRET)

Every stock that could pass the liquidity rules gets ~420 days of daily bars (Alpaca, split-adjusted). For each of the
last N sessions, at the close before it: 200 SMA, 10 / 21 / 50 EMA, 20-day ADR, average shares and $ volume, the 52-week
low, yesterday's high; the market cap = today's, moved with the price. A stock-day whose daily high was 5%+ over the
close before and over yesterday's high gets its 1-minute bars (SIP). Then each minute from 9:35 to 10:30, as the live
check does: price = the minute's close, up 5%+, Rel vol 1x+ for the time of day (the volume so far against today's
volume curve scaled to that day's 20-day average: an approximation, the curves of past days are not kept), price $5+,
30%+ over the 52-week low, over yesterday's high and over the 5-minute opening range high (9:30-9:35). The first minute
all of these pass is the alert. "uptrend" = that minute it also passes the morning breakout's trend rules (over the 200
SMA and the 50 EMA, 10 EMA > 21 EMA > 50 EMA, the EMAs moved to the price as the alert does); else "other".
The same day after the alert: entry = that minute's close, stop = the day's low so far; stop_hit = a later low under
it; close_pct = the day's close vs the entry; max_pct = the best later high; r = -1 when the stop was hit, else the
close in risks; under_entry = closed under the entry; under_orh = closed under the opening range high.
"""
import datetime, json, os, sys, time, urllib.parse, urllib.request, zoneinfo

NY = zoneinfo.ZoneInfo("America/New_York")
UTC = datetime.timezone.utc
HDR = {"APCA-API-KEY-ID": os.environ.get("ALPACA_KEY_ID", ""), "APCA-API-SECRET-KEY": os.environ.get("ALPACA_SECRET", "")}
M = {"min_chg": 5.0, "min_rv": 1.0, "price": 5.0, "mcap_b": 0.7, "avgvol_k": 700.0, "dvol_m": 30.0, "adr": 4.0, "low52": 30.0}
START, END = 5, 60          # minutes since 9:30: the checks from 9:35 (the first with the opening range: 9:36) to 10:30


def alpaca(params):
    """all pages of /v2/stocks/bars -> {symbol: [bar, ...]}"""
    out, q = {}, dict(params)
    while True:
        url = "https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q)
        for attempt in range(5):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=90) as r:
                    res = json.load(r)
                break
            except Exception as e:
                if attempt == 4:
                    raise
                time.sleep(3 * (attempt + 1) if "429" not in str(e) else 20)
        for s, rows in (res.get("bars") or {}).items():
            out.setdefault(s, []).extend(rows)
        if not res.get("next_page_token"):
            return out
        q["page_token"] = res["next_page_token"]


def ema(vals, n):
    k, e, out = 2 / (n + 1), None, []
    for v in vals:
        e = v if e is None else e + k * (v - e)
        out.append(e)
    return out


def day_stats(bars, i):
    """the alert's base numbers at the close before session i (bars: daily, oldest first), or None"""
    if i < 60:
        return None
    b = bars[:i]
    c = [x["c"] for x in b]
    last20 = b[-20:]
    return {"prev_close": c[-1], "pdh": b[-1]["h"], "sma200": sum(c[-200:]) / 200 if len(c) >= 200 else None,
            "e10": ema(c, 10)[-1], "e21": ema(c, 21)[-1], "e50": ema(c, 50)[-1],
            "adr": 100 * sum(x["h"] / x["l"] - 1 for x in last20 if x["l"]) / len(last20),
            "avg_vol": sum(x["v"] for x in last20) / len(last20),
            "dvol_m": sum(x["v"] * x["c"] for x in last20) / len(last20) / 1e6,
            "low52": min(x["l"] for x in b[-252:])}


def static_ok(s, mcap_b):
    return (mcap_b >= M["mcap_b"] and s["avg_vol"] >= M["avgvol_k"] * 1000 and s["dvol_m"] >= M["dvol_m"] and s["adr"] >= M["adr"])


def expected(curve, scale, m):
    """the average volume from 9:30 to m minutes later (radar/live.py rvol_at's curve: a value every 5 minutes)"""
    if not curve or m < 1:
        return None
    pos = m / 5
    j = int(pos)
    lo = curve[j - 1] if j >= 1 else 0
    hi = curve[min(j, len(curve) - 1)]
    e = lo + (hi - lo) * (pos - j) if j < len(curve) else curve[-1]
    return e * scale if e > 0 else None


def simulate(mins, s, curve, scale, min_chg=None, day=None):
    """mins: [(minute since 9:30, o, h, l, c, v)] of one session, sorted. The first minute the rules pass -> a result row"""
    if not mins or mins[0][0] > 2:
        return None                                     # no bar at the open (a halt, a late open)
    rng = [x for x in mins if x[0] < 5]
    orh = max(x[2] for x in rng)
    vol, low = 0, 1e18
    for k, x in enumerate(mins):
        m, o, h, l, c, v = x
        vol += v
        low = min(low, l)
        if m < START or m >= END:
            if m >= END:
                break
            continue
        chg = 100 * (c / s["prev_close"] - 1)
        exp = expected(curve, scale, m + 1)
        rv = vol / exp if exp else None
        if chg < (M["min_chg"] if min_chg is None else min_chg) or rv is None or rv < M["min_rv"] or c < M["price"] or c < s["low52"] * (1 + M["low52"] / 100):
            continue
        if not (c > s["pdh"] and c > orh):
            continue
        mv = lambda e, n: e + (2 / (n + 1)) * (c - e)
        e10, e21, e50 = mv(s["e10"], 10), mv(s["e21"], 21), mv(s["e50"], 50)
        why = []
        if s["sma200"] and c <= s["sma200"]:
            why.append("under the 200 SMA")
        if c <= e50:
            why.append("under the 50 EMA")
        if e10 <= e21:
            why.append("10 EMA not over the 21")
        if e21 <= e50:
            why.append("21 EMA not over the 50")
        after = mins[k + 1:]
        if day:                                         # the session's own close and low (the minute bars end at 10:31)
            close, hit, mx = day["c"], day["l"] < low, None
        else:
            if not after:
                return None
            close, hit, mx = after[-1][4], any(y[3] < low for y in after), max(y[2] for y in after)
        risk = c - low
        gap = 100 * (mins[0][1] / s["prev_close"] - 1)
        return {"time": f"{9 + (30 + m + 1) // 60}:{(30 + m + 1) % 60:02d}", "entry": round(c, 2), "chg": round(chg, 1), "rv": round(rv, 2),
                "orh": round(orh, 2), "stop": round(low, 2), "risk_pct": round(100 * risk / c, 1), "group": "other" if why else "uptrend", "why": why,
                "no_sma200": s["sma200"] is None, "stop_hit": hit, "close_pct": round(100 * (close / c - 1), 1),
                "max_pct": round(100 * (mx / c - 1), 1) if mx else None, "gap": round(gap, 1),
                "r": -1.0 if hit else (round((close - c) / risk, 2) if risk > 0 else 0.0),
                "under_entry": close < c, "under_orh": close < orh, "adr": round(s["adr"], 1)}
    return None


def summary(rows):
    n = len(rows)
    if not n:
        return {"n": 0}
    med = lambda v: sorted(v)[len(v) // 2]
    return {"n": n, "stop_hit_pct": round(100 * sum(r["stop_hit"] for r in rows) / n), "closed_under_entry_pct": round(100 * sum(r["under_entry"] for r in rows) / n),
            "closed_under_orh_pct": round(100 * sum(r["under_orh"] for r in rows) / n), "avg_close_pct": round(sum(r["close_pct"] for r in rows) / n, 2),
            "median_close_pct": med([r["close_pct"] for r in rows]), "avg_max_pct": round(sum(r["max_pct"] or 0 for r in rows) / n, 2),
            "avg_r": round(sum(r["r"] for r in rows) / n, 2), "closed_up_2pct_plus": round(100 * sum(r["close_pct"] >= 2 for r in rows) / n)}


def report(rows):
    out = {}
    for g in ("uptrend", "other"):
        R = [r for r in rows if r["group"] == g]
        out[g] = {"all": summary(R), "vol_1x_to_2x": summary([r for r in R if r["rv"] < 2]), "vol_2x_to_3x": summary([r for r in R if 2 <= r["rv"] < 3]),
                  "vol_3x_plus": summary([r for r in R if r["rv"] >= 3]), "vol_2x_plus": summary([r for r in R if r["rv"] >= 2])}
    O = [r for r in rows if r["group"] == "other"]
    out["other_by_reason"] = {w: summary([r for r in O if w in r["why"]]) for w in
                              ("under the 200 SMA", "under the 50 EMA", "10 EMA not over the 21", "21 EMA not over the 50")}
    out["other_over_200_sma"] = summary([r for r in O if "under the 200 SMA" not in r["why"]])
    return out


def main():
    stocks_p, prof_p, out_p = sys.argv[1:4]
    days = int(sys.argv[4]) if len(sys.argv) > 4 else 35
    thr = [float(x) for x in sys.argv[5].split(",")] if len(sys.argv) > 5 else None     # "2,3,4,5": each as the rule's % up
    lo_chg = min(thr) if thr else M["min_chg"]
    S = {s["symbol"]: s for s in json.load(open(stocks_p))}
    prof = json.load(open(prof_p))["rows"]
    uni = sorted(k for k, s in S.items() if (s.get("mcap_b") or 0) >= 0.4 and (s.get("avg_vol_20") or 0) >= 350000 and (s.get("price") or 0) >= 3
                 and "." not in k and "/" not in k)
    now = datetime.datetime.now(NY)
    t0 = (now - datetime.timedelta(days=430)).strftime("%Y-%m-%d")
    daily = {}
    for i in range(0, len(uni), 150):
        daily.update(alpaca({"symbols": ",".join(uni[i:i + 150]), "timeframe": "1Day", "feed": "sip", "adjustment": "split", "limit": 10000,
                             "start": t0, "end": (now - datetime.timedelta(minutes=20)).astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")}))
    print(len(uni), "stocks asked,", len(daily), "with daily bars", flush=True)
    for s in daily:
        for b in daily[s]:
            b["d"] = b["t"][:10]
    all_days = sorted({b["d"] for bars in daily.values() for b in bars})
    today = now.date().isoformat()
    sess = [d for d in all_days if d < today or now.hour >= 17][-days:]
    cands = {d: {} for d in sess}                         # day -> {sym: stats}
    for sym, bars in daily.items():
        idx = {b["d"]: i for i, b in enumerate(bars)}
        st = S[sym]
        for d in sess:
            i = idx.get(d)
            if i is None:
                continue
            s = day_stats(bars, i)
            if not s or not static_ok(s, (st.get("mcap_b") or 0) * s["prev_close"] / (st.get("price") or s["prev_close"])):
                continue
            if bars[i]["h"] >= s["prev_close"] * (1 + lo_chg / 100) and bars[i]["h"] > s["pdh"]:
                s["day"] = {"c": bars[i]["c"], "l": bars[i]["l"], "h": bars[i]["h"]}
                s["scale"] = s["avg_vol"] / st["avg_vol_20"] if st.get("avg_vol_20") else 1
                cands[d][sym] = s
    print("candidates a day:", {d: len(v) for d, v in cands.items()}, flush=True)
    rows = []
    for d in sess:
        syms = sorted(cands[d])
        if not syms:
            continue
        o = datetime.datetime.fromisoformat(d + "T09:30:00").replace(tzinfo=NY)
        c = datetime.datetime.fromisoformat(d + "T16:00:00").replace(tzinfo=NY)
        z = lambda t: t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        got = {}
        for i in range(0, len(syms), 25):
            got.update(alpaca({"symbols": ",".join(syms[i:i + 25]), "timeframe": "1Min", "feed": "sip", "adjustment": "split", "limit": 10000,
                               "start": z(o), "end": z((o + datetime.timedelta(minutes=62)) if thr else (c - datetime.timedelta(seconds=1)))}))
        for sym in syms:
            mins = []
            for b in got.get(sym) or []:
                t = datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(NY)
                m = t.hour * 60 + t.minute - 570
                if 0 <= m < 390:
                    mins.append((m, b["o"], b["h"], b["l"], b["c"], b["v"]))
            mins.sort()
            for th in (thr or [None]):
                r = simulate(mins, cands[d][sym], prof.get(sym), cands[d][sym]["scale"], th, cands[d][sym]["day"] if thr else None)
                if r:
                    r.update(date=d, sym=sym, thr=th)
                    rows.append(r)
        print(d, len(syms), "candidates,", sum(1 for r in rows if r["date"] == d), "alerts", flush=True)
    if thr:
        out = {"built_at": now.isoformat(timespec="seconds"), "sessions": sess, "rules": M, "thresholds": thr, "window": "9:35-10:30",
               "note": "each threshold is the rule's % up on its own: the first minute that passes it; the outcome from the session's close and low",
               "summary": {str(th): report([r for r in rows if r["thr"] == th]) for th in thr}, "rows": rows}
        json.dump(out, open(out_p, "w"), separators=(",", ":"))
        print(json.dumps({k: {g: v[g]["all"] for g in ("uptrend", "other")} for k, v in out["summary"].items()}, indent=1))
        return
    out = {"built_at": now.isoformat(timespec="seconds"), "sessions": sess, "rules": M, "window": "9:35-10:30",
           "note": "Rel vol from today's volume curves scaled to each day's 20-day average (an approximation); market cap = today's moved with the price",
           "summary": report(rows), "per_day": {d: {g: sum(1 for r in rows if r["date"] == d and r["group"] == g) for g in ("uptrend", "other")} for d in sess},
           "rows": rows}
    json.dump(out, open(out_p, "w"), separators=(",", ":"))
    print(json.dumps(out["summary"], indent=1))


if __name__ == "__main__":
    main()
