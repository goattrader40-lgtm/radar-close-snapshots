#!/usr/bin/env python3
"""The two earnings gap-down shorts head to head (the user, Nov 28 2026): 1. the break of the opening range low; 2. opens,
goes up, sometimes hits a previous low, fades, breaks down VWAP. Win rate, average win and loss, expected value, total R.

  python3 vwap_bd_report.py trades_out.json features.json gaps_clean.json reasons.json scen.json vwap_bd.json"""
import collections, json, math, sys
bd_path = sys.argv[6]
sys.argv = sys.argv[:6]
import scen_report as S
BD = json.load(open(bd_path))
R, up, dn, MD = S.R, S.up, S.dn, S.MD
COST = 0.001


def bd_trades(size):
    S.SC = {k: {"vwap": v[size]} for k, v in BD.items() if size in v}
    return S.trades("vwap")


def ev(ts):
    rs = [t[3]["r"] for t in ts]
    n = len(rs)
    if n < 25:
        return None
    w, l = [r for r in rs if r > 0], [r for r in rs if r <= 0]
    y = collections.defaultdict(float)
    for t in ts:
        y[t[0][:4]] += t[3]["r"]
    mean = sum(rs) / n
    sd = math.sqrt(sum((r - mean) ** 2 for r in rs) / (n - 1))
    net = sum(t[3]["r"] - COST * t[3]["entry"] / (t[3]["stop"] - t[3]["entry"]) for t in ts) / n
    o = [t[3]["r"] for t in ts if t[2]["day"] not in MD]
    return {"n": n, "win": 100 * len(w) / n, "aw": sum(w) / len(w) if w else 0, "al": sum(l) / len(l) if l else 0, "ev": mean, "total": sum(rs),
            "years": [y.get(k, 0.0) for k in ("2023", "2024", "2025", "2026")], "t": mean / (sd / math.sqrt(n)) if sd else 0, "net": net,
            "risk": sorted(t[3]["risk_pct"] for t in ts)[n // 2], "ord": sum(o) / len(o) if o else 0, "top10": sum(sorted(rs)[-10:])}


HEAD = ("| Set | Trades | Win | Avg win | Avg loss | Expected value (R a trade) | Total R | After costs | R by year 23/24/25/26 | Stop distance | Top 10 R |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|")


def line(label, ts):
    s = ev(ts)
    if not s:
        return f"| {label} | {len(ts)} | | | | | | | | | |"
    return (f"| {label} | {s['n']:,} | {s['win']:.1f}% | {s['aw']:+.2f}R | {s['al']:+.2f}R | {s['ev']:+.2f} | {s['total']:+.0f} | {s['net']:+.2f} | "
            f"{'/'.join(f'{v:+.0f}' for v in s['years'])} | {s['risk']:.1f}% | {s['top10']:+.0f} |")


E8 = lambda d: d["earn"] == 1 and d["gap"] <= -8
E58 = lambda d: d["earn"] == 1 and d["gap"] > -8
if __name__ == "__main__":
    A = S.trades("orb")
    print("### 1. Break of the opening range low (first 3-minute candle), earnings days")
    print(HEAD)
    for lab, c in (("earnings, gap 8%+", E8), ("earnings, gap 8%+, strong yesterday", lambda d: E8(d) and up(d)), ("earnings, gap 8%+, not strong", lambda d: E8(d) and not up(d)),
                   ("earnings, gap 5-8%", E58), ("earnings, every gap", lambda d: d["earn"] == 1)):
        print(line(lab, [t for t in A if c(t[2])]))
    for lab, f in (("earnings 8%+: straight down (never over the first candle's high)", lambda t: not S.popped(t)), ("earnings 8%+: popped over the first candle's high, then broke the low", S.popped)):
        print(line(lab, [t for t in A if E8(t[2]) and f(t)]))
    for size in ("5", "3"):
        T = bd_trades(size)
        pop = lambda t: t[3]["pop_pct"]
        print(f"\n### 2. Opens, goes up, fades, closes under VWAP ({size}-minute candles), earnings days")
        print(HEAD)
        for lab, c in (("earnings, gap 8%+", E8), ("earnings, gap 8%+, strong yesterday", lambda d: E8(d) and up(d)), ("earnings, gap 8%+, not strong", lambda d: E8(d) and not up(d)),
                       ("earnings, gap 5-8%", E58), ("earnings, every gap", lambda d: d["earn"] == 1), ("not earnings, gap 8%+", lambda d: d["earn"] == 0 and d["gap"] <= -8)):
            print(line(lab, [t for t in T if c(t[2])]))
        e8 = [t for t in T if E8(t[2])]
        print(f"| -- earnings, gap 8%+ ({size}-minute), by how far it popped over the open | | | | | | | | | | |")
        for lab, lo, hi in (("pop 0.5-1%", 0.5, 1), ("pop 1-2%", 1, 2), ("pop 2-3%", 2, 3), ("pop 3-5%", 3, 5), ("pop 5%+", 5, 999), ("pop 1%+", 1, 999), ("pop 2%+", 2, 999)):
            print(line(lab, [t for t in e8 if lo <= pop(t) < hi]))
        print("| -- by the time of the close under VWAP | | | | | | | | | | |")
        for lab, lo, hi in (("9:33-9:45", 0, 15), ("9:45-10:00", 15, 30), ("10:00-10:30", 30, 60), ("10:30-11:30", 60, 120), ("11:30-15:00", 120, 400), ("before 10:00", 0, 30), ("before 10:30", 0, 60)):
            print(line(lab, [t for t in e8 if lo <= t[2]["m"] < hi]))
        print("| -- did the pop reach a previous low (the gap had opened under it)? | | | | | | | | | | |")
        print(line("reached a previous low", [t for t in e8 if t[3].get("tag")]))
        print(line("  ... and stopped within 1% over it", [t for t in e8 if t[3].get("tag") and t[3]["over_pct"] <= 1]))
        print(line("  ... and went 1%+ over it", [t for t in e8 if t[3].get("tag") and t[3]["over_pct"] > 1]))
        print(line("did not reach any", [t for t in e8 if not t[3].get("tag")]))
        for lv in ("yesterday's low", "3-day low", "5-day low", "10-day low", "1-month low", "21-day closing low"):
            print(line("reached " + lv, [t for t in e8 if lv in (t[3].get("tag") or [])]))
        print("| -- was the first candle's low already broken? | | | | | | | | | | |")
        print(line("not broken yet (the pop came first)", [t for t in e8 if not t[3]["orl"]]))
        print(line("already broken", [t for t in e8 if t[3]["orl"]]))
        print("| -- the best-looking cut | | | | | | | | | | |")
        print(line("pop 1%+, before 10:30", [t for t in e8 if pop(t) >= 1 and t[2]["m"] < 60]))
        print(line("pop 1%+, before 10:30, strong yesterday", [t for t in e8 if pop(t) >= 1 and t[2]["m"] < 60 and up(t[2])]))
        print(line("pop 1%+, before 10:30, reached a previous low", [t for t in e8 if pop(t) >= 1 and t[2]["m"] < 60 and t[3].get("tag")]))
    # the same days: 1 and 2
    T = bd_trades("5")
    a = {t[0]: t for t in A if E8(t[2])}
    b = {t[0]: t for t in T if E8(t[2])}
    days = sum(1 for k, r in R.ROWS.items() if r["o"] >= 10 and S.RS.get(k, {}).get("earn") == 1 and r["gap"] <= -8)
    both = set(a) & set(b)
    print(f"\nearnings gap 8%+ days: {days}; 1 fires on {len(a)}, 2 (5-minute) on {len(b)}, both on {len(both)}; on those 1 avg {sum(a[k][3]['r'] for k in both) / len(both):+.2f}R, 2 avg {sum(b[k][3]['r'] for k in both) / len(both):+.2f}R; "
          f"2 came first on {sum(1 for k in both if b[k][2]['m'] < a[k][2]['m'])}")
    o1, o2 = set(a) - set(b), set(b) - set(a)
    print(f"only 1: {len(o1)} trades avg {sum(a[k][3]['r'] for k in o1) / max(1, len(o1)):+.2f}R; only 2: {len(o2)} trades avg {sum(b[k][3]['r'] for k in o2) / max(1, len(o2)):+.2f}R")
