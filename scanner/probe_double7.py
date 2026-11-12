#!/usr/bin/env python3
"""A study, not part of the portal: Connors' Double 7s on trending, high-ADR index stocks (the user, Nov 12 2026).

  python3 scanner/probe_double7.py --stocks stocks.json --out probe_double7.json [--bars long_bars.json] [--since 2010]

The idea as the user gave it: S&P 500 / Nasdaq-100 stocks with an ADR of 4%+ in an uptrend (10 EMA over the 21, the 21
over the 50, the 50 EMA higher than the day before); buy the close that is the lowest close of the last 7 sessions, sell
the close that is the highest close of the last 7 sessions.
Tested here: that filter, the same with the book's "over the 200 SMA", and the book's rule alone; bought at the signal
close or at the next open; with no stop (the book), a stop under the signal day's low, 1 / 2 ADRs under the entry, a
close under the 50 EMA, and a 10-session time limit. Then a small account simulation (10 positions of 10%).
Daily bars from Yahoo back to 2010 (split-adjusted), for TODAY's index members: stocks that left the indexes are missing,
which flatters the result (survivorship). Earnings days are not filtered (no earnings dates in history).
"""
import argparse, concurrent.futures as cf, datetime, json, statistics, sys, time, urllib.parse, urllib.request, zoneinfo
import numpy as np

NY = zoneinfo.ZoneInfo("America/New_York")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
ADR_MIN, N7, ADR_N, COST = 4.0, 7, 20, 0.05          # COST: % a side in the account simulation
FILTERS = ("user", "user200", "book_adr4", "book_all")
ENTRIES = ("close", "open")
EXITS = ("none", "daylow", "adr1", "adr2", "ema50", "time10")


def fetch(sym, since):
    p1 = int(datetime.datetime(since, 1, 1, tzinfo=NY).timestamp())
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym.replace('.', '-').replace('/', '-'))}"
           f"?period1={p1}&period2={int(time.time())}&interval=1d&includePrePost=false")
    for attempt in range(4):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60))["chart"]["result"][0]
            q = r["indicators"]["quote"][0]
            return sym, [[datetime.datetime.fromtimestamp(t, NY).date().isoformat(), o, h, l, c, v]
                         for t, o, h, l, c, v in zip(r["timestamp"], q["open"], q["high"], q["low"], q["close"], q["volume"])
                         if None not in (o, h, l, c) and l > 0]
        except Exception:
            time.sleep(3 * (attempt + 1))
    return sym, None


def ema(x, n):
    a, o = 2 / (n + 1), np.empty_like(x)
    o[0] = x[0]
    for i in range(1, x.size):
        o[i] = a * x[i] + (1 - a) * o[i - 1]
    return o


def roll(x, n, f):
    o = np.full(x.size, np.nan)
    if x.size >= n:
        w = np.lib.stride_tricks.sliding_window_view(x, n)
        o[n - 1:] = f(w, axis=1)
    return o


class S:
    def __init__(self, sym, rows):
        self.sym = sym
        self.d = [r[0] for r in rows]
        a = np.array([r[1:5] for r in rows], dtype=float)
        self.o, self.h, self.l, self.c = a[:, 0], a[:, 1], a[:, 2], a[:, 3]
        c = self.c
        self.e10, self.e21, self.e50 = ema(c, 10), ema(c, 21), ema(c, 50)
        self.s200 = roll(c, 200, np.mean)
        self.adr = roll(self.h / self.l - 1, ADR_N, np.mean) * 100
        self.lo7 = c <= roll(c, N7, np.min)
        self.hi7 = c >= roll(c, N7, np.max)
        r63 = np.full(c.size, np.nan)
        r63[63:] = c[63:] / c[:-63] - 1
        self.r63 = r63
        up = np.zeros(c.size, bool)
        up[1:] = self.e50[1:] > self.e50[:-1]
        trend = (self.e10 > self.e21) & (self.e21 > self.e50) & up
        over200 = c > self.s200
        ok = np.arange(c.size) >= 200
        hi_adr = self.adr >= ADR_MIN
        self.f = {"user": ok & self.lo7 & trend & hi_adr, "user200": ok & self.lo7 & trend & hi_adr & over200,
                  "book_adr4": ok & self.lo7 & over200 & hi_adr, "book_all": ok & self.lo7 & over200}


def trade(s, t, entry, ex):
    """one trade from the signal at day t: (entry index, exit index, entry price, exit price, risk per share or None)"""
    n = s.c.size
    if entry == "close":
        e, px = t, s.c[t]
    else:
        e = t + 1
        if e >= n: return None
        px = s.o[e]
    adr = s.adr[t] / 100
    stop = None
    if ex == "daylow": stop = min(s.l[t], px * (1 - 0.25 * adr))      # at least a quarter ADR of room
    elif ex == "adr1": stop = px * (1 - adr)
    elif ex == "adr2": stop = px * (1 - 2 * adr)
    risk = px - stop if stop is not None else None
    for u in range(e + 1 if entry == "close" else e, n):
        if stop is not None and u > e:
            if s.o[u] <= stop: return e, u, px, s.o[u], risk
            if s.l[u] <= stop: return e, u, px, stop, risk
        if stop is not None and u == e and entry == "open" and s.l[u] <= stop:
            return e, u, px, stop, risk
        if u > e or entry == "open":
            if s.hi7[u] and u > t: return e, u, px, s.c[u], risk
            if ex == "ema50" and s.c[u] < s.e50[u]: return e, u, px, s.c[u], risk
            if ex == "time10" and u - e >= 10: return e, u, px, s.c[u], risk
    return None            # still open at the end of the data


def run(stocks, filt, entry, ex):
    out = []
    for s in stocks:
        last = -1
        for t in np.flatnonzero(s.f[filt]):
            if t <= last: continue
            r = trade(s, int(t), entry, ex)
            if not r: continue
            e, u, px, xp, risk = r
            last = u
            out.append((s.sym, s.d[e], s.d[u], (xp / px - 1) * 100, u - e, (xp - px) / risk if risk else None,
                        float(s.r63[t]) if not np.isnan(s.r63[t]) else 0.0))
    return out


def stats(tr):
    if not tr: return {"n": 0}
    p = np.array([x[3] for x in tr])
    w, lo = p[p > 0], p[p <= 0]
    o = {"n": int(p.size), "win_pct": round(100 * w.size / p.size, 1), "avg_pct": round(float(p.mean()), 2),
         "median_pct": round(float(np.median(p)), 2), "avg_win": round(float(w.mean()), 2) if w.size else None,
         "avg_loss": round(float(lo.mean()), 2) if lo.size else None,
         "profit_factor": round(float(w.sum() / -lo.sum()), 2) if lo.size and lo.sum() < 0 else None,
         "avg_hold": round(float(np.mean([x[4] for x in tr])), 1), "median_hold": int(np.median([x[4] for x in tr])),
         "worst": round(float(p.min()), 1), "best": round(float(p.max()), 1),
         "lost_10pct_plus": round(100 * float((p <= -10).mean()), 1), "lost_20pct_plus": round(100 * float((p <= -20).mean()), 1)}
    rs = [x[5] for x in tr if x[5] is not None]
    if rs:
        o["avg_R"] = round(float(np.mean(rs)), 2)
        o["stopped_pct"] = round(100 * sum(1 for x in rs if x <= -0.95) / len(rs), 1)
    yr = {}
    for x in tr: yr.setdefault(x[1][:4], []).append(x[3])
    o["by_year"] = {y: [len(v), round(100 * sum(1 for a in v if a > 0) / len(v)), round(sum(v) / len(v), 2)] for y, v in sorted(yr.items())}
    return o


def account(tr, cal, px, slots=10):
    """10 positions of a tenth of the account each; on a day with more signals than free slots the strongest stocks
    (3-month gain) first; costs COST% a side; marked to the close every day"""
    by_in, idx = {}, {d: i for i, d in enumerate(cal)}
    for x in tr: by_in.setdefault(x[1], []).append(x)
    cash, pos, eq, taken, expo = 1.0, [], [], 0, []
    for i, d in enumerate(cal):
        keep = []
        for sym, sh, xd, xr in pos:
            if xd == d: cash += sh * xr * (1 - COST / 100)
            else: keep.append((sym, sh, xd, xr))
        pos = keep
        val = cash + sum(sh * px[sym][i] for sym, sh, _, _ in pos)
        for x in sorted(by_in.get(d, []), key=lambda x: -x[6]):
            if len(pos) >= slots: break
            if x[2] not in idx or any(p[0] == x[0] for p in pos): continue
            amt = min(val / slots, cash)
            if amt <= val / slots * 0.5: break
            ep = px[x[0]][i] if not np.isnan(px[x[0]][i]) else None
            if not ep: continue
            # buy at the trade's own entry price (close or open); the exit at its own exit price
            taken += 1
            if x[2] == d:                  # in and out the same day (a next-open entry that closed at a 7-day high or stopped)
                cash += amt * ((1 - COST / 100) ** 2 * (1 + x[3] / 100) - 1)
                continue
            sh = amt * (1 - COST / 100) / ep
            cash -= amt
            pos.append((x[0], sh, x[2], ep * (1 + x[3] / 100)))
        val = cash + sum(sh * px[sym][i] for sym, sh, _, _ in pos)
        eq.append(val); expo.append(1 - cash / val if val else 0)
    eq = np.array(eq)
    yrs = (datetime.date.fromisoformat(cal[-1]) - datetime.date.fromisoformat(cal[0])).days / 365.25
    dd = float((eq / np.maximum.accumulate(eq) - 1).min())
    by = {}
    for i, d in enumerate(cal): by.setdefault(d[:4], [None, None]); by[d[:4]][1] = eq[i]; by[d[:4]][0] = by[d[:4]][0] or (eq[i - 1] if i else 1.0)
    return {"slots": slots, "trades_taken": taken, "of_signals": len(tr), "end_value": round(float(eq[-1]), 2),
            "cagr_pct": round((float(eq[-1]) ** (1 / yrs) - 1) * 100, 1), "max_drawdown_pct": round(dd * 100, 1),
            "avg_invested_pct": round(100 * float(np.mean(expo)), 0),
            "by_year_pct": {y: round((b / a - 1) * 100, 1) for y, (a, b) in sorted(by.items())}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stocks", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--bars"); ap.add_argument("--since", type=int, default=2010)
    a = ap.parse_args()
    rows = json.load(open(a.stocks))
    member = {r["symbol"]: r.get("index") for r in rows if r.get("index")}
    if a.bars:
        raw = json.load(open(a.bars))
        raw = {k: v for k, v in raw.items() if k in member or k in ("SPY", "QQQ")}
    else:
        raw = {}
        with cf.ThreadPoolExecutor(8) as pool:
            for sym, b in pool.map(lambda s: fetch(s, a.since), sorted(member) + ["SPY", "QQQ"]):
                if b and len(b) >= 260: raw[sym] = b
        print(f"{len(raw)} of {len(member) + 2} downloaded")
        if "SPY" not in raw or len(raw) < 0.8 * len(member): sys.exit("too few symbols came back")
    etf = {k: S(k, raw[k]) for k in ("SPY", "QQQ") if k in raw}
    stocks = [S(k, v) for k, v in sorted(raw.items()) if k in member and len(v) >= 260]
    cal = etf["SPY"].d[200:]
    ci = {d: i for i, d in enumerate(cal)}
    px = {}
    for s in stocks:                       # closes on SPY's calendar, gaps carried forward (the account's daily value)
        v = np.full(len(cal), np.nan)
        for d, c in zip(s.d, s.c):
            if d in ci: v[ci[d]] = c
        for i in range(1, len(v)):
            if np.isnan(v[i]): v[i] = v[i - 1]
        px[s.sym] = v
    res, keep = {}, {}
    for f in FILTERS:
        for en in ENTRIES:
            for ex in EXITS:
                tr = [x for x in run(stocks, f, en, ex) if x[1] in ci]
                res[f"{f}|{en}|{ex}"] = stats(tr)
                keep[(f, en, ex)] = tr
    # the account: priced at the close of the entry day; for a next-open entry the first day's move from the open is lost
    # in the daily marks only, not in the trade's result (the exit value is entry price x the trade's own result)
    acct = {f"{f}|{en}|{ex}": account(keep[(f, en, ex)], cal, px) for f, en, ex in
            (("user", "close", "none"), ("user", "close", "adr2"), ("user", "close", "time10"), ("user", "open", "none"),
             ("user200", "close", "none"), ("book_adr4", "close", "none"), ("book_all", "close", "none"))}
    base = {}
    for k, s in etf.items():
        tr = [x for x in run([s], "book_all", "close", "none") if x[1] in ci]
        i0 = s.d.index(cal[0])
        eq = s.c[i0:] / s.c[i0]
        yrs = (datetime.date.fromisoformat(cal[-1]) - datetime.date.fromisoformat(cal[0])).days / 365.25
        base[k] = {"double7": stats(tr), "buy_hold_cagr_pct": round((float(eq[-1]) ** (1 / yrs) - 1) * 100, 1),
                   "buy_hold_max_drawdown_pct": round(float((eq / np.maximum.accumulate(eq) - 1).min()) * 100, 1)}
    main_tr = keep[("user", "close", "none")]
    per_day = {}
    for x in main_tr: per_day[x[1]] = per_day.get(x[1], 0) + 1
    today = []
    for s in stocks:
        if s.d[-1] == etf["SPY"].d[-1] and s.f["user"][-1]:
            today.append({"symbol": s.sym, "close": round(float(s.c[-1]), 2), "adr": round(float(s.adr[-1]), 1),
                          "over_200": bool(s.c[-1] > s.s200[-1]), "index": member[s.sym]})
    json.dump({"built": datetime.datetime.now(NY).isoformat(timespec="seconds"), "from": cal[0], "to": cal[-1],
               "universe": len(stocks), "adr_min": ADR_MIN, "cost_pct_a_side_account": COST,
               "note": "today's index members only (survivorship); earnings days not filtered; prices split-adjusted, no dividends",
               "results": res, "account": acct, "etf": base,
               "signal_days": {"days_with_a_signal": len(per_day), "most_in_one_day": max(per_day.values()) if per_day else 0,
                               "median_a_day": statistics.median(per_day.values()) if per_day else 0},
               "today": {"date": etf["SPY"].d[-1], "signals": today},
               "trades_user_close_none": [[x[0], x[1], x[2], round(x[3], 2), x[4]] for x in main_tr]},
              open(a.out, "w"), separators=(",", ":"))
    for k in ("user|close|none", "user|open|none", "user|close|adr2", "user200|close|none", "book_adr4|close|none", "book_all|close|none"):
        r = {kk: vv for kk, vv in res[k].items() if kk != "by_year"}
        print(k, r)
    print("account", json.dumps(acct)); print("etf", json.dumps(base))


if __name__ == "__main__":
    main()
