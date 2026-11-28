#!/usr/bin/env python3
"""The gap-down day's shorts side by side, in tables: the opening-range break and the pop-then-fail scenarios, by gap size,
earnings day and yesterday's trend.

  python3 scen_report.py trades_out.json features.json gaps_clean.json reasons.json scen.json"""
import collections, json, math, sys
scen_path = sys.argv[5]
sys.argv = sys.argv[:5]
import part3 as P
M, R, RS, F, G, up, dn, p1b = P.M, P.R, P.RS, P.M.F, P.M.G, P.up, P.dn, P.p1b
SC = json.load(open(scen_path))
MD = M.MD
NAMES = [("orb", "A. Break of the opening low (first 3-minute candle)"), ("vwap", "B. Pop to VWAP, fails"), ("level", "C. Pop to a broken daily level, fails"),
         ("orlre", "D. Opening low broken, retested from below, fails"), ("r2g", "E. Pop 1.5%+ over the open, then loses the open"),
         ("lod", "F. Bounce 1.5%+, then a new low of the day")]


def trades(kind, cond=None):
    """[(key, row, facts, trade)] with the stop 0.5%+ away, the open $10+"""
    out = []
    for key, row in R.ROWS.items():
        if row["o"] < 10:
            continue
        tr3 = row.get("3")
        if kind == "orb":
            if not tr3 or "t" not in tr3 or not tr3.get("rh"):
                continue
            t = dict(tr3["rh"], entry=tr3["entry"], m=tr3["m"], t=tr3["t"])
        else:
            t = SC.get(key, {}).get(kind)
            if not t:
                continue
        if t["risk_pct"] < R.MIN_RISK or not tr3:
            continue
        d = M.facts(key, row, dict(tr3, entry=t["entry"]))
        if d is None:
            continue
        d = dict(d, gap=row["gap"], earn=RS.get(key, {}).get("earn"), color=tr3["color"], rvol=tr3["rvol"], m=t["m"], day=key.split()[0])
        if cond and not cond(d):
            continue
        out.append((key, row, d, t))
    return out


def stat(ts):
    if not ts:
        return None
    rs = [t[3]["r"] for t in ts]
    n = len(rs)
    mean = sum(rs) / n
    sd = math.sqrt(sum((r - mean) ** 2 for r in rs) / (n - 1)) if n > 1 else 0
    o = [t[3]["r"] for t in ts if t[2]["day"] not in MD]
    y = collections.defaultdict(float)
    for t in ts:
        y[t[0][:4]] += t[3]["r"]
    return {"n": n, "win": 100 * sum(1 for r in rs if r > 0) / n, "avg": mean, "total": sum(rs), "t": mean / (sd / math.sqrt(n)) if sd else 0,
            "ord_n": len(o), "ord_avg": sum(o) / len(o) if o else 0, "ord_total": sum(o), "years": [y.get(k, 0.0) for k in ("2023", "2024", "2025", "2026")],
            "risk": sorted(t[3]["risk_pct"] for t in ts)[n // 2], "stopped": 100 * sum(t[3]["stopped"] for t in ts) / n}


def line(label, ts, minimum=25):
    s = stat(ts)
    if not s or s["n"] < minimum:
        return f"| {label} | {len(ts)} | | | | | |"
    return (f"| {label} | {s['n']:,} | {s['win']:.1f}% | {s['avg']:+.2f} | {s['total']:+.0f} | {s['ord_avg']:+.2f} ({s['ord_n']:,}) | "
            f"{'/'.join(f'{v:+.0f}' for v in s['years'])} |")


def popped(t):
    """the opening-low short whose price went over the opening range's high before the low broke"""
    r3 = R.ROWS[t[0]]["3"]
    return bool(r3.get("dh")) and r3["dh"]["stop"] > r3["rhi"] * 1.0005


def vwap_state(t):
    """where the day stands when the pop to VWAP fails: 'none' the opening low not broken yet; 'under' it is broken and the
    pop stayed under the opening range's high; 'over' the pop went over that high"""
    r3 = R.ROWS[t[0]]["3"]
    if "m" not in r3 or r3["m"] >= t[3]["m"] or not r3.get("rh"):
        return "none"
    return "over" if t[3]["stop"] >= r3["rhi"] else "under"


def play2(before=90):
    """PLAY 2, the retest short: the opening low already broken, the first pop to VWAP (under the range high) fails before 11:00"""
    return [t for t in trades("vwap") if vwap_state(t) == "under" and t[2]["m"] < before]


SUBSETS = [("every 5%+ gap", lambda d: True), ("gap 5-8%", lambda d: d["gap"] > -8), ("gap 8-10%", lambda d: -10 < d["gap"] <= -8),
           ("gap 10-15%", lambda d: -15 < d["gap"] <= -10), ("gap 15%+", lambda d: d["gap"] <= -15),
           ("earnings day", lambda d: d["earn"] == 1), ("not an earnings day", lambda d: d["earn"] == 0),
           ("earnings, gap 5-8%", lambda d: d["earn"] == 1 and d["gap"] > -8), ("earnings, gap 8%+", lambda d: d["earn"] == 1 and d["gap"] <= -8),
           ("not earnings, gap 5-8%", lambda d: d["earn"] == 0 and d["gap"] > -8), ("not earnings, gap 8%+", lambda d: d["earn"] == 0 and d["gap"] <= -8),
           ("strong yesterday", lambda d: up(d)), ("weak yesterday (under 50 EMA + 200 SMA)", lambda d: dn(d)),
           ("strong, gap 5-8%", lambda d: up(d) and d["gap"] > -8), ("strong, gap 8%+", lambda d: up(d) and d["gap"] <= -8),
           ("earnings + strong, gap 5-8%", lambda d: d["earn"] == 1 and up(d) and d["gap"] > -8),
           ("earnings + strong, gap 8%+", lambda d: d["earn"] == 1 and up(d) and d["gap"] <= -8),
           ("earnings + weak, gap 8%+", lambda d: d["earn"] == 1 and dn(d) and d["gap"] <= -8)]
HEAD = "| Set | Trades | Win | Avg R | Total R | Ordinary days avg R (trades) | R by year 23/24/25/26 |\n|---|---|---|---|---|---|---|"

if __name__ == "__main__":
    days = sum(1 for r in R.ROWS.values() if r["o"] >= 10)
    for kind, name in NAMES:
        ts = trades(kind)
        s = stat(ts)
        print(f"\n### {name}  ({len(ts):,} of {days:,} gap-down days; median stop distance {s['risk']:.1f}%, stopped {s['stopped']:.0f}%)")
        print(HEAD)
        for lab, cond in SUBSETS:
            print(line(lab, [t for t in ts if cond(t[2])]))
        if kind != "orb":
            for lab, lo, hi in (("signal before 10:00", 0, 30), ("signal 10:00-11:00", 30, 90), ("signal 11:00-13:00", 90, 210), ("signal after 13:00", 210, 400)):
                print(line(lab, [t for t in ts if lo <= t[2]["m"] < hi]))
        if kind == "level":
            for lv in ("yesterday's low", "21-day closing low", "1-month low", "50 EMA", "200 SMA", "yesterday's close"):
                print(line("the level: " + lv, [t for t in ts if t[3].get("level") == lv]))
    print("\n### B, split by where the opening low stands when the pop to VWAP fails")
    print(HEAD)
    vw = trades("vwap")
    for lab, st in (("the opening low not broken yet", "none"), ("the low broken, the pop stays under the range high", "under"), ("the low broken, the pop goes over the range high", "over")):
        for lab2, c2 in ((", every gap", lambda d: True), (", gap 5-8%", lambda d: d["gap"] > -8), (", earnings + gap 8%+", lambda d: d["earn"] == 1 and d["gap"] <= -8)):
            print(line(lab + lab2, [t for t in vw if vwap_state(t) == st and c2(t[2])]))
    print("\n### PLAY 2, the retest short: the opening low already broken, the pop to VWAP (under the range high) fails before 11:00")
    print(HEAD)
    p2 = play2()
    for lab, cond in SUBSETS:
        print(line(lab, [t for t in p2 if cond(t[2])]))
    for lab, lo, hi in (("earnings + gap 8%+, signal 9:40-10:00", 0, 30), ("earnings + gap 8%+, signal 10:00-10:30", 30, 60), ("earnings + gap 8%+, signal 10:30-11:00", 60, 90)):
        print(line(lab, [t for t in p2 if lo <= t[2]["m"] < hi and t[2]["earn"] == 1 and t[2]["gap"] <= -8]))
    # the opening-low break: did it pop first?
    print("\n### A, split by what happened before the low broke")
    print(HEAD)
    ts = trades("orb")
    for lab, f in (("straight down: the low broke before the range high", lambda t: not popped(t)), ("popped over the range high first, then broke the low", popped),
                   ("first candle green", lambda t: t[2]["color"] == "green"), ("first candle red", lambda t: t[2]["color"] == "red"),
                   ("low broke 9:33-9:45", lambda t: t[2]["m"] < 15), ("low broke 9:45-10:30", lambda t: 15 <= t[2]["m"] < 60), ("low broke after 10:30", lambda t: t[2]["m"] >= 60)):
        for lab2, c2 in (("", lambda d: True), (", earnings + gap 8%+", lambda d: d["earn"] == 1 and d["gap"] <= -8)):
            print(line(lab + lab2, [t for t in ts if f(t) and c2(t[2])]))
