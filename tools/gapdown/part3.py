#!/usr/bin/env python3
"""The gap-down short study, part 3 (the user, Nov 24 2026): how far gap-downs move in the day, other exits, earnings days.

  python3 part3.py trades_out.json features.json gaps_clean.json reasons.json"""
import json, statistics, sys
reasons_path = sys.argv[4]
sys.argv = sys.argv[:4]
import mirror as M
R, F, G, show, sel = M.R, M.F, M.G, M.show, M.sel
RS = json.load(open(reasons_path))
up = lambda d: (not d["u50"]) and d["u200"] is False
dn = lambda d: d["u50"] and d["u200"] is True
p1b = lambda d, r, t: up(d) and d["o_u50"] and d["o_u200"] is True and d["o_u1m"]
EXITS = ["close", "t10:00", "t10:30", "t11:00", "t12:00", "t13:00", "t14:00", "t15:00", "r1", "r2", "r3", "r5", "p3", "p5", "p8", "p10", "p15", "be", "half2"]


def q(a, p):
    a = sorted(a)
    return a[min(len(a) - 1, int(len(a) * p))]


def moves():
    days = [(k, r) for k, r in R.ROWS.items() if r["o"] >= 10]
    ol = [(1 - r["l"] / r["o"]) * 100 for k, r in days]
    oc = [(r["c"] / r["o"] - 1) * 100 for k, r in days]
    print(f"== how far a 5%+ gap-down moves after its open ({len(days)} stock-days) ==")
    print(f"open -> the day's low: median -{q(ol, .5):.1f}%, a quarter fall -{q(ol, .75):.1f}% or more, 1 in 10 -{q(ol, .9):.1f}% or more; "
          f"low 5%+ under the open on {100 * sum(1 for x in ol if x >= 5) / len(ol):.0f}%, 10%+ on {100 * sum(1 for x in ol if x >= 10) / len(ol):.0f}%")
    print(f"open -> the close: median {q(oc, .5):+.1f}%; closed under the open {100 * sum(1 for x in oc if x < 0) / len(oc):.0f}%; "
          f"closed 3%+ under it {100 * sum(1 for x in oc if x <= -3) / len(oc):.0f}%, 5%+ {100 * sum(1 for x in oc if x <= -5) / len(oc):.0f}%, 10%+ {100 * sum(1 for x in oc if x <= -10) / len(oc):.0f}%; "
          f"closed 3%+ OVER it {100 * sum(1 for x in oc if x >= 3) / len(oc):.0f}%")
    for name, cond in (("gap 5-8%", lambda r: r["gap"] > -8), ("gap 8-15%", lambda r: -15 < r["gap"] <= -8), ("gap 15%+", lambda r: r["gap"] <= -15)):
        a = [(r["c"] / r["o"] - 1) * 100 for k, r in days if cond(r)]
        b = [(1 - r["l"] / r["o"]) * 100 for k, r in days if cond(r)]
        print(f"  {name}: {len(a)} days; open->low median -{q(b, .5):.1f}%; open->close median {q(a, .5):+.1f}%, under the open {100 * sum(1 for x in a if x < 0) / len(a):.0f}%, "
              f"5%+ under {100 * sum(1 for x in a if x <= -5) / len(a):.0f}%, 3%+ over {100 * sum(1 for x in a if x >= 3) / len(a):.0f}%")
    ts = R.trades("3", "rh")
    mfe = [t[3]["ox"]["mfe"] for t in ts]
    fin = [(t[2]["entry"] - t[3]["exit"]) / t[2]["entry"] * 100 for t in ts]
    print(f"the short ({len(ts)} trades): the furthest it went our way before the stop or the close: median {q(mfe, .5):.1f}%, a quarter {q(mfe, .75):.1f}%+, 1 in 10 {q(mfe, .9):.1f}%+; "
          f"3%+ on {100 * sum(1 for x in mfe if x >= 3) / len(mfe):.0f}%, 5%+ on {100 * sum(1 for x in mfe if x >= 5) / len(mfe):.0f}%, 10%+ on {100 * sum(1 for x in mfe if x >= 10) / len(mfe):.0f}%")
    print(f"  what it kept at the exit (stop or close): median {q(fin, .5):+.1f}%; 3%+ on {100 * sum(1 for x in fin if x >= 3) / len(fin):.0f}%, 5%+ on {100 * sum(1 for x in fin if x >= 5) / len(fin):.0f}%, 10%+ on {100 * sum(1 for x in fin if x >= 10) / len(fin):.0f}%")
    print("the biggest moves from the short price to the close (3-min range, stop range high):")
    for key, row, tr, st in sorted(ts, key=lambda t: -(t[2]["entry"] - t[3]["exit"]) / t[2]["entry"])[:15]:
        d, s = key.split()
        e = RS.get(key, {})
        print(f"  {d} {s:<5} gap {row['gap']:>6.1f}%  short {tr['t']} at {tr['entry']:<8} -> {st['exit']:<8} {100 * (tr['entry'] - st['exit']) / tr['entry']:>5.1f}%  {st['r']:+.1f}R  "
              f"{'earnings' if e.get('earn') else ''}  from the close before: {100 * (st['exit'] / row['pc'] - 1):+.1f}%")


def exits(label, ts):
    if len(ts) < 25:
        print(f"{label}: {len(ts)} trades")
        return
    cols = []
    for e in EXITS:
        rs = [t[3]["r"] if e == "close" else t[3]["ox"].get(e, t[3]["r"]) for t in ts]
        cols.append((e, 100 * sum(1 for r in rs if r > 0) / len(rs), sum(rs) / len(rs), sum(rs)))
    print(f"{label} ({len(ts)} trades)")
    print("   " + "  ".join(f"{e}: {w:.0f}%/{a:+.2f}/{t:+.0f}" for e, w, a, t in cols))
    return cols


def earn_sel(n, s, cond, earn, **kw):
    def extra(key, row, tr):
        d = M.facts(key, row, tr)
        e = RS.get(key, {}).get("earn")
        return d is not None and e == earn and bool(cond(d, row, tr))
    return R.trades(n, s, extra=extra, **kw)


if __name__ == "__main__":
    moves()
    print("\n== other exits for the same short (3-min range, stop range high): win % / avg R / total R ==")
    sets = [("every 5%+ gap", lambda d, r, t: True), ("gap 8%+", lambda d, r, t: r["gap"] <= -8),
            ("strong yesterday, gap 8%+", lambda d, r, t: up(d) and r["gap"] <= -8), ("mirror of play 1b", p1b)]
    for name, cond in sets:
        exits(name, sel("3", "rh", cond))
        exits(name + ", ordinary days", [t for t in sel("3", "rh", cond) if t[0].split()[0] not in M.MD])
    print("\n== earnings days (an 8-K with the results between the close before and the gap day) ==")
    n_e = sum(1 for k, r in R.ROWS.items() if r["o"] >= 10 and RS.get(k, {}).get("earn") == 1)
    n_n = sum(1 for k, r in R.ROWS.items() if r["o"] >= 10 and RS.get(k, {}).get("earn") == 0)
    n_u = sum(1 for k, r in R.ROWS.items() if r["o"] >= 10 and RS.get(k, {}).get("earn") is None)
    print(f"stock-days: earnings {n_e}, not earnings {n_n}, unknown (foreign companies, no 8-Ks) {n_u}")
    for n, s in (("3", "rh"), ("5", "rh")):
        print(f"-- {n}-minute range, stop {R.STOP_NAME[s]}")
        for lab, e in (("EARNINGS day", 1), ("NOT an earnings day", 0), ("unknown (foreign)", None)):
            show(f"{lab}: every gap", earn_sel(n, s, lambda d, r, t: True, e))
            for lo, hi in ((5, 8), (8, 10), (10, 15), (15, 100)):
                show(f"   gap {lo}-{hi}%", earn_sel(n, s, lambda d, r, t: -hi < r["gap"] <= -lo, e))
            show("   gap 8%+", earn_sel(n, s, lambda d, r, t: r["gap"] <= -8, e))
            show("   strong yesterday (over 50 EMA + 200 SMA)", earn_sel(n, s, lambda d, r, t: up(d), e))
            show("   strong yesterday, gap 8%+", earn_sel(n, s, lambda d, r, t: up(d) and r["gap"] <= -8, e))
            show("   strong yesterday, gap 8%+, opens under 50 EMA", earn_sel(n, s, lambda d, r, t: up(d) and r["gap"] <= -8 and d["o_u50"], e))
            show("   mirror of play 1b", earn_sel(n, s, lambda d, r, t: p1b(d, r, t), e))
            show("   downtrend yesterday (under both)", earn_sel(n, s, lambda d, r, t: dn(d), e))
            show("   downtrend yesterday, gap 8%+", earn_sel(n, s, lambda d, r, t: dn(d) and r["gap"] <= -8, e))
            show("   first candle green", earn_sel(n, s, lambda d, r, t: t["color"] == "green", e))
            show("   first candle red", earn_sel(n, s, lambda d, r, t: t["color"] == "red", e))
            show("   early rel vol 10x+", earn_sel(n, s, lambda d, r, t: t["rvol"] >= 10, e))
    print("\n== earnings days: other exits (3-min range, stop range high) ==")
    for name, cond in sets:
        exits("EARNINGS, " + name, earn_sel("3", "rh", cond, 1))
        exits("NOT earnings, " + name, earn_sel("3", "rh", cond, 0))
