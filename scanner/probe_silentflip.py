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
    a = ap.parse_args()
    res = {"saved_at": datetime.datetime.now(NY).isoformat(timespec="seconds")}
    try:
        syms = universe(a.bars, a.n)
        hdr = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
        now = datetime.datetime.now(datetime.timezone.utc)
        start = (now - datetime.timedelta(days=740)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end = (now - datetime.timedelta(minutes=20)).strftime("%Y-%m-%dT%H:%M:%SZ")
        data, errors = {}, []
        with cf.ThreadPoolExecutor(6) as pool:
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
        strict = run(data, BASE)
        res["his_rules"] = report(strict)
        res["wick_may_poke_0.1atr"] = report(run(data, dict(BASE, pierce=0.10)))
        res["stronger_candle_0.3atr"] = report(run(data, dict(BASE, strong_atr=0.30)))
        res["target_2R_or_more"] = report(run(data, dict(BASE, minR=2.0)))
        res["loose_first_test"] = report(run(data, dict(BASE, starts=(570, 585, 600), c1close=0.25)))
        res["trades"] = [[x["t"], x["day"], x["side"], x["lvl"], x["L"], x["ep"], x["stop"], x["T"], x["ex"], x["why"],
                          round(x["pnl"] / x["risk"], 2), x["adr"]] for x in strict]
        res["trade_fields"] = ["ticker", "day", "side", "level", "level_price", "entry", "stop", "target", "exit", "why", "gross_R", "adr"]
    except Exception:
        res["error"] = traceback.format_exc()[-1500:]
    with open(a.out, "w") as f:
        json.dump(res, f, separators=(",", ":"))
    print(json.dumps({k: v for k, v in res.items() if k != "trades"})[:3000])


if __name__ == "__main__":
    main()
