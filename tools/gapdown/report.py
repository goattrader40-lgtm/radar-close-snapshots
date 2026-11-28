#!/usr/bin/env python3
"""The gap-down short study's tables, from trades.py's output.

  python3 report.py trades_out.json [--json grid.json]

One rule set everywhere: the stock opened at $10+; the range low broke after the range (any time of the day); the stop
at least MIN_RISK % from the entry; bought back at the stop, else at the day's last price. One trade per stock-day and
setting. "after costs" takes COST (0.1% of the price) off every trade for slippage and fees."""
import collections, json, statistics, sys

D = json.load(open(sys.argv[1]))
ROWS = D["rows"]
RANGES, STOPS, COLORS, GAPS = ("3", "5"), ("rh", "dh"), ("either", "red", "green"), (5, 8, 10)
RVOLS = (0, 2, 3, 5, 10)
STOP_NAME = {"rh": "range high", "dh": "day's high"}
COST = 0.001          # the cost check: 0.1% of the price for the round trip (0.05% a side)
MIN_RISK = 0.5        # a stop closer than 0.5% of the price is no trade (a late open's one-print "range": WAL Apr 3 2025, a 1-cent stop)

per_day = collections.Counter(k.split()[0] for k, r in ROWS.items() if r["o"] >= 10)
MARKET_DAYS = {d for d, n in per_day.items() if n >= 50}


def trades(n, stop, color="either", gap=5, rvol=0, extra=None, min_risk=None):
    out = []
    mr = MIN_RISK if min_risk is None else min_risk
    for key, row in ROWS.items():
        tr = row.get(n)
        if row["o"] < 10 or not tr or "t" not in tr or not tr.get(stop):
            continue
        if tr[stop]["risk_pct"] < mr:
            continue
        if row["gap"] > -gap or tr["rvol"] < rvol:
            continue
        if color != "either" and tr["color"] != color:
            continue
        if extra and not extra(key, row, tr):
            continue
        out.append((key, row, tr, tr[stop]))
    return out


def stats(ts):
    if not ts:
        return None
    rs = [t[3]["r"] for t in ts]
    net = [t[3]["r"] - COST * t[2]["entry"] / (t[3]["stop"] - t[2]["entry"]) for t in ts]
    pct = [(t[2]["entry"] - t[3]["exit"]) / t[2]["entry"] * 100 for t in ts]
    return {"n": len(rs), "win": round(100 * sum(1 for r in rs if r > 0) / len(rs), 1), "avg": round(sum(rs) / len(rs), 3),
            "total": round(sum(rs), 1), "stopped": round(100 * sum(t[3]["stopped"] for t in ts) / len(ts), 1),
            "risk": round(statistics.median(t[3]["risk_pct"] for t in ts), 2), "net_avg": round(sum(net) / len(net), 3),
            "net_total": round(sum(net), 1), "pct": round(sum(pct) / len(pct), 3)}


def line(label, s):
    if not s:
        return f"{label:<46} no trades"
    return (f"{label:<46} {s['n']:>5}  win {s['win']:>5.1f}%  avg {s['avg']:>+6.3f}R  total {s['total']:>+7.1f}R  "
            f"stopped {s['stopped']:>4.1f}%  risk {s['risk']:>4.2f}%  avg move {s['pct']:>+5.2f}%  after costs {s['net_avg']:>+6.3f}R / {s['net_total']:>+7.1f}R")


def years(ts):
    by = collections.defaultdict(list)
    for t in ts:
        by[t[0][:4]].append(t)
    return {y: stats(v) for y, v in sorted(by.items())}


def capped(ts, k=4):
    """at most k trades a day, in the order they trigger; trades of the same minute share the places left (their average)"""
    by = collections.defaultdict(list)
    for t in ts:
        by[t[0].split()[0]].append(t)
    total, n = 0.0, 0.0
    for day, v in by.items():
        left = k
        mins = collections.defaultdict(list)
        for t in v:
            mins[t[2]["m"]].append(t[3]["r"])
        for m in sorted(mins):
            if left <= 0:
                break
            take = min(left, len(mins[m]))
            total += sum(mins[m]) / len(mins[m]) * take
            n += take
            left -= take
    return {"n": round(n), "avg": round(total / n, 3) if n else 0, "total": round(total, 1)}


def ylabel(y):
    return "  ".join(f"{k} {v['n']}/{v['avg']:+.2f}R/{v['total']:+.0f}R" for k, v in y.items())


def main():
    used = [k for k, r in ROWS.items() if r["o"] >= 10]
    print(f"stock-days with good bars {len(ROWS)}; opened at $10+ {len(used)}; dates {min(k.split()[0] for k in ROWS)} to {max(k.split()[0] for k in ROWS)}")
    print(f"dropped by the data checks {len(D['bad'])}, no 1-minute bars {len(D['missing'])}, fetch errors {len(D['errors'])}")
    print(f"per year: {dict(sorted(collections.Counter(k[:4] for k in used).items()))}")
    print(f"market-wide days (50+ gap-downs): {len(MARKET_DAYS)} days = {sum(per_day[d] for d in MARKET_DAYS)} stock-days; the biggest {per_day.most_common(6)}")
    for n in RANGES:
        base = [r for k, r in ROWS.items() if r["o"] >= 10 and r.get(n)]
        trig = [r for r in base if "t" in r[n]]
        col = collections.Counter(r[n]["color"] for r in base)
        rv = sorted(r[n]["rvol"] for r in base)
        q = lambda p: rv[int(len(rv) * p)]
        print(f"\n{n}-minute range: {len(base)} days, range low broken on {len(trig)} ({100 * len(trig) / len(base):.0f}%); first candle {dict(col)}")
        print(f"  early rel vol: p10 {q(.1):.1f}x  p25 {q(.25):.1f}x  median {q(.5):.1f}x  p75 {q(.75):.1f}x  p90 {q(.9):.1f}x")
        for s in STOPS:
            same = collections.Counter(r[n][s]["same"] for r in trig if r[n].get(s) and r[n][s]["amb"])
            tiny = sum(1 for r in trig if r[n].get(s) and r[n][s]["risk_pct"] < MIN_RISK)
            print(f"  stop {STOP_NAME[s]}: entry minute also at / over the stop {sum(same.values())} {dict(same)}; stop under {MIN_RISK}% away (left out) {tiny}")

    print("\n== the base: every 5%+ gap-down, either candle, any volume ==")
    for n in RANGES:
        for s in STOPS:
            ts = trades(n, s)
            print(line(f"{n}-min range, stop {STOP_NAME[s]}", stats(ts)))
            print(f"{'':<46} by year: {ylabel(years(ts))}")
            ex = stats([t for t in ts if t[0].split()[0] not in MARKET_DAYS])
            cp = capped(ts)
            print(f"{'':<46} without the {len(MARKET_DAYS)} market-wide days: {ex['n']} trades {ex['win']}% {ex['avg']:+.3f}R {ex['total']:+.1f}R;  at most 4 trades a day: {cp['n']} trades {cp['avg']:+.3f}R {cp['total']:+.1f}R")
    print("\n== first candle ==")
    for n in RANGES:
        for s in STOPS:
            for c in COLORS:
                print(line(f"{n}-min, stop {STOP_NAME[s]}, candle {c}", stats(trades(n, s, c))))
    print("\n== gap size ==")
    for n in RANGES:
        for s in STOPS:
            for g in GAPS:
                print(line(f"{n}-min, stop {STOP_NAME[s]}, gap {g}%+", stats(trades(n, s, gap=g))))
    print("\n== gap bands ==")
    for n in RANGES:
        for s in STOPS:
            for lo, hi in ((5, 8), (8, 10), (10, 15), (15, 100)):
                print(line(f"{n}-min, stop {STOP_NAME[s]}, gap {lo}-{hi}%", stats(trades(n, s, extra=lambda k, r, t: -hi < r["gap"] <= -lo))))
    print("\n== early relative volume (at least) ==")
    for n in RANGES:
        for s in STOPS:
            for v in RVOLS:
                print(line(f"{n}-min, stop {STOP_NAME[s]}, rel vol {v}x+", stats(trades(n, s, rvol=v))))
    print("\n== early relative volume bands ==")
    for n in RANGES:
        for s in STOPS:
            for lo, hi in ((0, 2), (2, 3), (3, 5), (5, 10), (10, 20), (20, 1e9)):
                print(line(f"{n}-min, stop {STOP_NAME[s]}, rel vol {lo}-{hi if hi < 1e9 else ''}x", stats(trades(n, s, extra=lambda k, r, t: lo <= t["rvol"] < hi))))
    print("\n== entry time ==")
    for n in RANGES:
        for s in STOPS:
            for lo, hi, name in ((0, 15, "9:30-9:45"), (15, 30, "9:45-10:00"), (30, 60, "10:00-10:30"), (60, 120, "10:30-11:30"), (120, 400, "after 11:30")):
                print(line(f"{n}-min, stop {STOP_NAME[s]}, entry {name}", stats(trades(n, s, extra=lambda k, r, t: lo <= t["m"] < hi))))
    print("\n== the stop's distance from the entry ==")
    for n in RANGES:
        for s in STOPS:
            for lo, hi in ((0, 0.5), (0.5, 1), (1, 1.5), (1.5, 2.5), (2.5, 4), (4, 100)):
                print(line(f"{n}-min, stop {STOP_NAME[s]}, risk {lo}-{hi}%", stats(trades(n, s, min_risk=0, extra=lambda k, r, t, s=s: lo <= t[s]["risk_pct"] < hi))))

    grid = []
    for n in RANGES:
        for s in STOPS:
            for c in COLORS:
                for g in GAPS:
                    for v in RVOLS:
                        ts = trades(n, s, c, g, v)
                        st = stats(ts)
                        if st:
                            y = years(ts)
                            ex = stats([t for t in ts if t[0].split()[0] not in MARKET_DAYS])
                            grid.append({"range": n, "stop": s, "candle": c, "gap": g, "rvol": v, **st,
                                         "years": {k: [x["n"], x["avg"], x["total"]] for k, x in y.items()},
                                         "pos_years": sum(1 for x in y.values() if x["total"] > 0),
                                         "ex_market": [ex["n"], ex["win"], ex["avg"], ex["total"]] if ex else None,
                                         "cap4": capped(ts)})
    name = lambda x: f"{x['range']}-min {STOP_NAME[x['stop']]} {x['candle']} gap {x['gap']}%+ vol {x['rvol']}x+"
    print(f"\n== all {len(grid)} combinations: top 15 by total R ==")
    for x in sorted(grid, key=lambda x: -x["total"])[:15]:
        print(line(name(x), x), "| years", x["years"], "| ex market days", x["ex_market"], "| cap4", x["cap4"])
    print("\n== top 15 by average R (200+ trades) ==")
    for x in sorted((x for x in grid if x["n"] >= 200), key=lambda x: -x["avg"])[:15]:
        print(line(name(x), x), "| years", x["years"], "| ex market days", x["ex_market"], "| cap4", x["cap4"])
    print("\n== worst 8 by total R ==")
    for x in sorted(grid, key=lambda x: x["total"])[:8]:
        print(line(name(x), x), "| years", x["years"])
    if "--json" in sys.argv:
        json.dump(grid, open(sys.argv[sys.argv.index("--json") + 1], "w"))


if __name__ == "__main__":
    main()
