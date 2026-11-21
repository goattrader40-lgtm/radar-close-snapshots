#!/usr/bin/env python3
"""A 2-year test of the "Silent Flip" setup (prorealalgos.com/silentflip) on 5-minute Alpaca bars. A test only:
it reads prices and writes one result file; nothing in the scanner, the portal or the alerts uses it.

  python3 scanner/probe_silentflip.py --bars history/bars_2y.json.gz --out /tmp/probe_silentflip.json [--n 100]

The rules, on 15-minute candles built from the 5-minute bars:
  levels   range high / low = yesterday's high / low; flip high / low = the nearest earlier swing high above
           the range high / swing low under the range low (60 days back)
  candle 1 the 9:30 candle: strong (range 0.2+ of the 14-day ATR, body half its range or more), reaches a level
           and closes on the inside of it (shorts at the two upper levels, longs at the two lower ones)
  candle 2 the "silent" candle: closes against candle 1 and on the inside of the level
  candle 3 entry on a break of the silent candle's low (short) / high (long), in that candle only
  stop     just past the high / low of candles 1-2; target = the opposite level; out at the close otherwise
Stocks: the N most traded ($ volume, $10+) in the scanner's daily file. Costs are shown both light and heavy.
"""
import argparse, concurrent.futures as cf, datetime, gzip, json, os, sys, time, traceback
import urllib.parse, urllib.request, zoneinfo

import numpy as np

NY = zoneinfo.ZoneInfo("America/New_York")
BASE = dict(strong_atr=0.20, body=0.5, touch=0.05, buf=0.02, minR=1.0, piv=3, look=60,
            starts=(570,), c1close=0.0, pierce=9.0)
COSTS = {"none": (0.0, 0.0), "light": (1.0, 0.005), "heavy": (3.0, 0.01)}   # basis points and $ per side


def universe(path, n):
    with gzip.open(path, "rt") as f:
        D = json.load(f)
    rows = []
    for s, b in D["bars"].items():
        if s in ("SPY", "QQQ", "IWM") or len(b) < 260 or not s.isalpha():
            continue
        last = b[-20:]
        if last[-1][4] < 10:
            continue
        rows.append((sum(x[4] * x[5] for x in last) / len(last), s))
    rows.sort(reverse=True)
    return [s for _, s in rows[:n]]


def fetch(sym, start, end, hdr):
    """{day: [(minute of the day, open, high, low, close), ...]} for the regular session, 5-minute bars"""
    q = {"symbols": sym, "timeframe": "5Min", "feed": "sip", "adjustment": "split", "limit": 10000,
         "start": start, "end": end}
    days = {}
    while True:
        res = None
        for attempt in range(5):
            try:
                rq = urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q), headers=hdr)
                with urllib.request.urlopen(rq, timeout=60) as r:
                    res = json.load(r)
                break
            except Exception as e:
                err = str(e)
                time.sleep(3 * (attempt + 1))
        if res is None:
            raise RuntimeError(f"{sym}: {err}")
        for b in (res.get("bars") or {}).get(sym, []):
            dt = datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(NY)
            m = dt.hour * 60 + dt.minute
            if 570 <= m < 960:
                days.setdefault(dt.date().isoformat(), []).append((m, b["o"], b["h"], b["l"], b["c"]))
        if not res.get("next_page_token"):
            return days
        q["page_token"] = res["next_page_token"]


def run(data, P):
    out = []
    for t, days in data.items():
        ds = sorted(d for d, b in days.items() if len(b) >= 60)
        if len(ds) < 80:
            continue
        D = np.array([[days[d][0][1], max(x[2] for x in days[d]), min(x[3] for x in days[d]), days[d][-1][4]] for d in ds])
        for i in range(70, len(ds)):
            day, b = ds[i], days[ds[i]]
            h = D[:i]
            tr = np.maximum(h[-14:, 1] - h[-14:, 2], np.abs(h[-14:, 1] - h[-15:-1, 3]))
            atr = tr.mean()
            RH, RL = h[-1, 1], h[-1, 2]
            w = h[-P["look"] - 1:-1]; k = P["piv"]; FH = FL = None
            for j in range(len(w) - k - 1, k - 1, -1):
                if FH is None and w[j, 1] > RH and w[j, 1] == w[j - k:j + k + 1, 1].max():
                    FH = w[j, 1]
                if FL is None and w[j, 2] < RL and w[j, 2] == w[j - k:j + k + 1, 2].min():
                    FL = w[j, 2]
                if FH and FL:
                    break

            def c15(s):
                g = [x for x in b if s <= x[0] < s + 15]
                return (g[0][1], max(x[2] for x in g), min(x[3] for x in g), g[-1][4]) if len(g) >= 2 else None

            for s in P["starts"]:
                c1, c2 = c15(s), c15(s + 15)
                if not c1 or not c2:
                    continue
                o1, h1, l1, cl1 = c1; o2, h2, l2, cl2 = c2
                rng = h1 - l1
                if rng < P["strong_atr"] * atr or abs(cl1 - o1) < P["body"] * rng:
                    continue
                cand = None
                if cl1 > o1 and cl2 < o2:
                    for nm, L, T in (("flipH", FH, RH), ("rangeH", RH, RL)):
                        if (L and h1 >= L - P["touch"] * atr and l1 < L and cl2 < L and h2 <= max(h1, L) + P["touch"] * atr
                                and cl1 <= L + P["c1close"] * atr and h1 <= L + P["pierce"] * atr):
                            cand = (-1, nm, L, T, l2, max(h1, h2) + P["buf"] * atr); break
                if cl1 < o1 and cl2 > o2:
                    for nm, L, T in (("flipL", FL, RL), ("rangeL", RL, RH)):
                        if (L and l1 <= L + P["touch"] * atr and h1 > L and cl2 > L and l2 >= min(l1, L) - P["touch"] * atr
                                and cl1 >= L - P["c1close"] * atr and l1 >= L - P["pierce"] * atr):
                            cand = (1, nm, L, T, h2, min(l1, l2) - P["buf"] * atr); break
                if not cand:
                    continue
                side, nm, L, T, trig, stop = cand
                if (trig - stop) * side <= 0 or (T - trig) * side < P["minR"] * (trig - stop) * side:
                    continue
                f = [x for x in b if x[0] >= s + 30]; e = None
                for n, x in enumerate(f):
                    if x[0] >= s + 45:
                        break
                    if (side == 1 and x[2] >= trig) or (side == -1 and x[3] <= trig):
                        e = n; ep = max(trig, x[1]) if side == 1 else min(trig, x[1]); break
                if e is None:
                    continue
                risk = (ep - stop) * side
                if risk <= 0:
                    continue
                ex = None
                for n, x in enumerate(f[e:]):
                    if (side == 1 and x[3] <= stop) or (side == -1 and x[2] >= stop):   # stop first when both are in one bar
                        ex = stop if n == 0 else (min(stop, x[1]) if side == 1 else max(stop, x[1])); why = "stop"; break
                    if (side == 1 and x[2] >= T) or (side == -1 and x[3] <= T):
                        ex = T; why = "target"; break
                if ex is None:
                    ex = f[-1][4]; why = "close"
                out.append(dict(t=t, day=day, side=side, lvl=nm, L=round(float(L), 2), ep=round(float(ep), 2),
                                stop=round(float(stop), 2), T=round(float(T), 2), ex=round(float(ex), 2), why=why,
                                risk=float(risk), pnl=float((ex - ep) * side), adr=round(float(atr / ep * 100), 2)))
                break
    return out


def run_user(data, P, target="range_far", sides=(-1,), back=20, near=0.10):
    """The user's read (Nov 19 2026): candle 1 closes green ABOVE yesterday's high and its high runs into an earlier
    15-minute swing high above yesterday's high (within `near` of the ATR, the last `back` sessions) without closing
    through it; the silent candle closes red under that resistance; short the break of its low. The long is the mirror.
    target: "range_near" = yesterday's high (low for longs), "range_far" = yesterday's low (high for longs)."""
    out = []
    for t, days in data.items():
        ds = sorted(d for d, b in days.items() if len(b) >= 60)
        if len(ds) < 80:
            continue
        D = np.array([[days[d][0][1], max(x[2] for x in days[d]), min(x[3] for x in days[d]), days[d][-1][4]] for d in ds])
        piv = []                                    # per day: the 15-minute swing highs and lows (3 candles each side)
        ser = []
        for di, d in enumerate(ds):
            b = days[d]
            for s in range(570, 960, 15):
                g = [x for x in b if s <= x[0] < s + 15]
                if g:
                    ser.append((di, max(x[2] for x in g), min(x[3] for x in g)))
        ph = [[] for _ in ds]; pl = [[] for _ in ds]
        for j in range(3, len(ser) - 3):
            w = ser[j - 3:j + 4]
            if ser[j][1] == max(x[1] for x in w):
                ph[ser[j][0]].append(ser[j][1])
            if ser[j][2] == min(x[2] for x in w):
                pl[ser[j][0]].append(ser[j][2])
        for i in range(70, len(ds)):
            day, b = ds[i], days[ds[i]]
            h = D[:i]
            atr = np.maximum(h[-14:, 1] - h[-14:, 2], np.abs(h[-14:, 1] - h[-15:-1, 3])).mean()
            RH, RL = h[-1, 1], h[-1, 2]

            def c15(s):
                g = [x for x in b if s <= x[0] < s + 15]
                return (g[0][1], max(x[2] for x in g), min(x[3] for x in g), g[-1][4]) if len(g) >= 2 else None
            c1, c2 = c15(570), c15(585)
            if not c1 or not c2:
                continue
            o1, h1, l1, cl1 = c1; o2, h2, l2, cl2 = c2
            rng = h1 - l1
            if rng < P["strong_atr"] * atr or abs(cl1 - o1) < P["body"] * rng:
                continue
            cand = None
            if -1 in sides and cl1 > o1 and cl1 > RH and cl2 < o2:
                lv = [x for k in range(i - back, i) for x in ph[k] if x > RH and abs(h1 - x) <= near * atr and cl1 < x]
                if lv:
                    L = min(lv, key=lambda x: abs(h1 - x))
                    if cl2 < L and h2 <= max(h1, L) + near * atr:
                        cand = (-1, L, RH if target == "range_near" else RL, l2, max(h1, h2) + P["buf"] * atr)
            if 1 in sides and cl1 < o1 and cl1 < RL and cl2 > o2:
                lv = [x for k in range(i - back, i) for x in pl[k] if x < RL and abs(l1 - x) <= near * atr and cl1 > x]
                if lv:
                    L = min(lv, key=lambda x: abs(l1 - x))
                    if cl2 > L and l2 >= min(l1, L) - near * atr:
                        cand = (1, L, RL if target == "range_near" else RH, h2, min(l1, l2) - P["buf"] * atr)
            if not cand:
                continue
            side, L, T, trig, stop = cand
            if (trig - stop) * side <= 0 or (T - trig) * side < P["minR"] * (trig - stop) * side:
                continue
            f = [x for x in b if x[0] >= 600]; e = None
            for n, x in enumerate(f):
                if x[0] >= 615:
                    break
                if (side == 1 and x[2] >= trig) or (side == -1 and x[3] <= trig):
                    e = n; ep = max(trig, x[1]) if side == 1 else min(trig, x[1]); break
            if e is None:
                continue
            risk = (ep - stop) * side
            if risk <= 0:
                continue
            ex = None
            for n, x in enumerate(f[e:]):
                if (side == 1 and x[3] <= stop) or (side == -1 and x[2] >= stop):
                    ex = stop if n == 0 else (min(stop, x[1]) if side == 1 else max(stop, x[1])); why = "stop"; break
                if (side == 1 and x[2] >= T) or (side == -1 and x[3] <= T):
                    ex = T; why = "target"; break
            if ex is None:
                ex = f[-1][4]; why = "close"
            out.append(dict(t=t, day=day, side=side, lvl="15m_res" if side == -1 else "15m_sup", L=round(float(L), 2),
                            ep=round(float(ep), 2), stop=round(float(stop), 2), T=round(float(T), 2), ex=round(float(ex), 2),
                            why=why, risk=float(risk), pnl=float((ex - ep) * side), adr=round(float(atr / ep * 100), 2)))
    return out


def agg(b, tf):
    if tf == 5:
        return b
    out = []
    for s in range(570, 960, tf):
        g = [x for x in b if s <= x[0] < s + tf]
        if g:
            out.append((s, g[0][1], max(x[2] for x in g), min(x[3] for x in g), g[-1][4]))
    return out


def run_sr(data, tf=5, target="2R", near=0.05, buf=0.02, last_entry=900):
    """The general idea (the user, Nov 20 2026): price runs into an earlier level, is rejected, and the rejection is
    traded, any time of the day, with the daily trend or against it.
    levels   yesterday's high and low, and the daily swing highs / lows of the last 120 days within 3 ATR of the open.
             A level over the price is resistance and one under it is support, whatever it was before (so an old low
             that the stock gapped under is resistance: "flipped").
    short    a bar comes up into a level from 0.25+ ATR below (high within `near` ATR of it) and doesn't close over it;
             within the next 3 bars a red bar closes under the level; sell the break of that bar's low (3 bars).
             Stop over the high of the test; target 2R or the next level; out at the close. Longs are the mirror.
             The first test of each level only; one trade at a time.
    trend    up = yesterday's close over the 20-day average and that over the 50-day; down = the reverse; else flat."""
    out = []
    for t, days in data.items():
        ds = sorted(d for d, b in days.items() if len(b) >= 60)
        if len(ds) < 80:
            continue
        D = np.array([[days[d][0][1], max(x[2] for x in days[d]), min(x[3] for x in days[d]), days[d][-1][4]] for d in ds])
        k = 3; ph = []; pl = []
        for j in range(k, len(ds) - k):
            if D[j, 1] == D[j - k:j + k + 1, 1].max():
                ph.append((j, D[j, 1]))
            if D[j, 2] == D[j - k:j + k + 1, 2].min():
                pl.append((j, D[j, 2]))
        for i in range(70, len(ds)):
            b = agg(days[ds[i]], tf)
            if len(b) < 20:
                continue
            h = D[:i]
            atr = np.maximum(h[-14:, 1] - h[-14:, 2], np.abs(h[-14:, 1] - h[-15:-1, 3])).mean()
            c, s20, s50 = h[-1, 3], h[-20:, 3].mean(), h[-50:, 3].mean()
            trend = "up" if c > s20 > s50 else "down" if c < s20 < s50 else "flat"
            YH, YL = h[-1, 1], h[-1, 2]; op = b[0][1]
            lv = [(YH, "yday", "H"), (YL, "yday", "L")]
            lv += [(p, "swing", "H") for j, p in ph if i - 120 <= j < i - k and abs(p - op) <= 3 * atr]
            lv += [(p, "swing", "L") for j, p in pl if i - 120 <= j < i - k and abs(p - op) <= 3 * atr]
            keep = []
            for x in lv:
                if all(abs(x[0] - y[0]) > 0.1 * atr for y in keep):
                    keep.append(x)
            used = set(); j = 0; n = len(b); tol = near * atr
            while j < n and b[j][0] < last_entry:
                m, o, hi, lo, cl = b[j]
                trade = None
                for li, (L, typ, org) in enumerate(keep):
                    if li in used:
                        continue
                    side = -1 if o < L else 1
                    if side == -1:
                        ref = min([x[3] for x in b[max(0, j - 6):j]] + [o])
                        if not (hi >= L - tol and ref <= L - 0.25 * atr):
                            continue
                    else:
                        ref = max([x[2] for x in b[max(0, j - 6):j]] + [o])
                        if not (lo <= L + tol and ref >= L + 0.25 * atr):
                            continue
                    used.add(li)
                    if (cl - L) * side < -tol:            # closed through the level: broken, no trade
                        continue
                    ext = hi if side == -1 else lo; kb = None
                    for q in range(j + 1, min(j + 4, n)):
                        x = b[q]
                        if (x[4] - L) * side < -tol:
                            break
                        ext = max(ext, x[2]) if side == -1 else min(ext, x[3])
                        if (x[4] - x[1]) * side > 0 and (x[4] - L) * side > 0 and (ext - L) * side >= -2 * tol:
                            kb = q; break
                    if kb is None:
                        continue
                    trig = b[kb][3] if side == -1 else b[kb][2]
                    stop = ext + buf * atr if side == -1 else ext - buf * atr
                    e = None
                    for q in range(kb + 1, min(kb + 4, n)):
                        x = b[q]
                        if (side == -1 and x[3] <= trig) or (side == 1 and x[2] >= trig):
                            e = q; ep = min(trig, x[1]) if side == -1 else max(trig, x[1]); break
                    if e is None:
                        continue
                    risk = (ep - stop) * side
                    if risk < 0.1 * atr:
                        continue
                    T = ep + 2 * risk * side
                    if target == "level":
                        nxt = [y[0] for y in keep if (y[0] - ep) * side >= risk]
                        if nxt:
                            T = min(nxt) if side == 1 else max(nxt)
                    ex = None
                    for q in range(e, n):
                        x = b[q]
                        if (side == 1 and x[3] <= stop) or (side == -1 and x[2] >= stop):
                            ex = stop if q == e else (min(stop, x[1]) if side == 1 else max(stop, x[1])); why = "stop"; break
                        if (side == 1 and x[2] >= T) or (side == -1 and x[3] <= T):
                            ex = T; why = "target"; break
                    if ex is None:
                        ex = b[-1][4]; why = "close"; q = n - 1
                    cls = "flat" if trend == "flat" else "with" if (trend == "up") == (side == 1) else "against"
                    trade = dict(t=t, day=ds[i], side=side, lvl=typ, flipped=(org == "L") == (side == -1), trend=trend, cls=cls,
                                 gap=bool(op > YH or op < YL), tm="first hour" if m < 630 else "10:30-12:00" if m < 720 else "afternoon",
                                 L=round(float(L), 2), ep=round(float(ep), 2), stop=round(float(stop), 2), T=round(float(T), 2),
                                 ex=round(float(ex), 2), why=why, risk=float(risk), pnl=float((ex - ep) * side),
                                 adr=round(float(atr / ep * 100), 2), at=m)
                    j = q
                    break
                if trade:
                    out.append(trade)
                j += 1
    return out


def report_sr(tr):
    rep = {"all": {k: stats(tr, k) for k in COSTS}, "exits": {}}
    for x in tr:
        rep["exits"][x["why"]] = rep["exits"].get(x["why"], 0) + 1
    def split(name, key, sub=None):
        g = {}
        for x in (sub if sub is not None else tr):
            g.setdefault(key(x), []).append(x)
        rep[name] = {str(k): {"none": stats(v, "none"), "light": stats(v, "light")} for k, v in sorted(g.items())}
    sd = lambda x: "long" if x["side"] == 1 else "short"
    split("by_trend_class", lambda x: x["cls"])
    split("by_trend_and_side", lambda x: x["trend"] + " trend, " + sd(x))
    split("by_level", lambda x: x["lvl"] + (" flipped" if x["flipped"] else ""))
    split("by_gap", lambda x: "gap outside yesterday's range" if x["gap"] else "opened inside")
    split("by_time", lambda x: x["tm"])
    split("etf_vs_stocks", lambda x: "SPY QQQ IWM" if x["t"] in ("SPY", "QQQ", "IWM") else "stocks")
    w = [x for x in tr if x["cls"] == "with"]
    split("with_trend_by_half_year", lambda x: x["day"][:4] + ("H1" if x["day"][5:7] <= "06" else "H2"), w)
    split("with_trend_by_time", lambda x: x["tm"], w)
    split("with_trend_by_level", lambda x: x["lvl"] + (" flipped" if x["flipped"] else ""), w)
    split("with_trend_by_gap", lambda x: "gap" if x["gap"] else "inside", w)
    split("with_trend_by_adr", lambda x: "adr 3.5+" if x["adr"] >= 3.5 else "adr under 3.5", w)
    return rep


def stats(tr, cost="heavy"):
    bp, c = COSTS[cost]
    if not tr:
        return {"n": 0}
    r = np.array([(x["pnl"] - 2 * (bp / 1e4 * x["ep"] + c)) / x["risk"] for x in tr])
    byday = {}
    for x, v in zip(tr, r):
        byday[x["day"]] = byday.get(x["day"], 0) + v
    eq = np.cumsum([byday[d] for d in sorted(byday)])
    w, l = r[r > 0].sum(), -r[r <= 0].sum()
    return {"n": len(r), "win_pct": round(float((r > 0).mean() * 100), 1), "avg_R": round(float(r.mean()), 3),
            "profit_factor": round(float(w / l), 2) if l > 0 else None, "total_R": round(float(r.sum()), 1),
            "max_drawdown_R": round(float((eq - np.maximum.accumulate(eq)).min()), 1),
            "t_stat": round(float(r.mean() / (r.std() / len(r) ** 0.5)), 2) if len(r) > 2 and r.std() > 0 else None}


def report(tr):
    rep = {"all": {k: stats(tr, k) for k in COSTS}, "exits": {}}
    for x in tr:
        rep["exits"][x["why"]] = rep["exits"].get(x["why"], 0) + 1
    def split(name, key):
        g = {}
        for x in tr:
            g.setdefault(key(x), []).append(x)
        rep[name] = {str(k): {"light": stats(v, "light"), "heavy": stats(v, "heavy")} for k, v in sorted(g.items())}
    split("by_side", lambda x: "long" if x["side"] == 1 else "short")
    split("by_level", lambda x: x["lvl"])
    split("by_half_year", lambda x: x["day"][:4] + ("H1" if x["day"][5:7] <= "06" else "H2"))
    split("by_adr", lambda x: "adr 3.5+" if x["adr"] >= 3.5 else "adr under 3.5")
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--mode", default="flip")
    a = ap.parse_args()
    res = {"saved_at": datetime.datetime.now(NY).isoformat(timespec="seconds")}
    try:
        syms = universe(a.bars, a.n)
        if a.mode == "sr":
            syms += ["SPY", "QQQ", "IWM"]
        hdr = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
        now = datetime.datetime.now(datetime.timezone.utc)
        start = (now - datetime.timedelta(days=740)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end = (now - datetime.timedelta(minutes=20)).strftime("%Y-%m-%dT%H:%M:%SZ")
        data, errors = {}, []
        with cf.ThreadPoolExecutor(4) as pool:
            futs = {pool.submit(fetch, s, start, end, hdr): s for s in syms}
            for fu in cf.as_completed(futs):
                try:
                    data[futs[fu]] = fu.result()
                except Exception as e:
                    errors.append(str(e)[:200])
        alld = sorted({d for v in data.values() for d in v})
        res.update(symbols=len(data), asked=len(syms), fetch_errors=errors[:10],
                   first_day=alld[0] if alld else None, last_day=alld[-1] if alld else None, days=len(alld),
                   bars=sum(len(b) for v in data.values() for b in v.values()))
        if a.mode == "sr":
            base = run_sr(data, 5, "2R")
            res["sr_5min_target_2R"] = report_sr(base)
            res["sr_5min_target_next_level"] = report_sr(run_sr(data, 5, "level"))
            res["sr_15min_target_2R"] = report_sr(run_sr(data, 15, "2R"))
            res["sr_15min_target_next_level"] = report_sr(run_sr(data, 15, "level"))
            res["sr_trades_qqq"] = [[x["day"], x["at"], x["side"], x["lvl"], x["flipped"], x["trend"], x["L"], x["ep"], x["stop"], x["T"],
                                     x["ex"], x["why"], round(x["pnl"] / x["risk"], 2)] for x in base if x["t"] == "QQQ"][-60:]
            raise SystemExit
        strict = run(data, BASE)
        res["his_rules"] = report(strict)
        res["wick_may_poke_0.1atr"] = report(run(data, dict(BASE, pierce=0.10)))
        res["stronger_candle_0.3atr"] = report(run(data, dict(BASE, strong_atr=0.30)))
        res["target_2R_or_more"] = report(run(data, dict(BASE, minR=2.0)))
        res["loose_first_test"] = report(run(data, dict(BASE, starts=(570, 585, 600), c1close=0.25)))
        fmt = lambda tr: [[x["t"], x["day"], x["side"], x["lvl"], x["L"], x["ep"], x["stop"], x["T"], x["ex"], x["why"],
                           round(x["pnl"] / x["risk"], 2), x["adr"]] for x in tr]
        u_far = run_user(data, BASE, "range_far")
        res["user_short_target_yesterday_low"] = report(u_far)
        res["user_short_target_yesterday_high"] = report(run_user(data, BASE, "range_near"))
        res["user_short_any_candle_size"] = report(run_user(data, dict(BASE, strong_atr=0.0, body=0.0), "range_far"))
        res["user_short_looser_touch_0.25atr"] = report(run_user(data, BASE, "range_far", near=0.25))
        res["user_long_mirror_target_yesterday_high"] = report(run_user(data, BASE, "range_far", sides=(1,)))
        res["user_trades"] = fmt(u_far)
        res["trades"] = [[x["t"], x["day"], x["side"], x["lvl"], x["L"], x["ep"], x["stop"], x["T"], x["ex"], x["why"],
                          round(x["pnl"] / x["risk"], 2), x["adr"]] for x in strict]
        res["trade_fields"] = ["ticker", "day", "side", "level", "level_price", "entry", "stop", "target", "exit", "why", "gross_R", "adr"]
    except SystemExit:
        pass
    except Exception:
        res["error"] = traceback.format_exc()[-1500:]
    with open(a.out, "w") as f:
        json.dump(res, f, separators=(",", ":"))
    print(json.dumps({k: v for k, v in res.items() if k != "trades"})[:3000])


if __name__ == "__main__":
    main()
