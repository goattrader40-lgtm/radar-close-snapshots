#!/usr/bin/env python3
"""Momentum reset (the user's AEHR read, Nov 1 2026): do buy points that come before a reset do worse?

  git fetch -q origin +refs/heads/radar-data:refs/remotes/origin/radar-data
  python3 tools/reset_analysis.py [probe_buypoints.json]      # prints the tables, saves tools/reset_analysis.json

A reset, measured from the bars up to the day before the buy (scanner/mgmt.py reset):
  at the 50 EMA      since the latest top (the highest high of the 60 sessions before), a low came within a quarter ADR of
                     the 50 EMA or under it (AEHR Mar 30 2026)
  RSI under 45       the RSI(14) dipped under 45 since that top
  EMAs close         the 21 EMA at most 0.8 ADR over the 50 EMA the day before
  any                one of the three
Each comparison: the net R (0.15% costs, the risk floored at 1%), both halves of the period, and a luck test: the reset /
no-reset labels shuffled 2,000 times; p = how often luck alone made a gap as big as the real one.
"""
import json, math, os, random, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COST, FLOOR, MIN_DV = 0.15, 1.0, 20
TACTICS = (("at the close (fair)", "close_"), ("5-min entry (fair)", "min5_"), ("as the alert fires (upper limit)", ""))
RESETS = (("any reset", "reset_any"), ("at the 50 EMA", "reset_at_50ema"), ("RSI under 45", "reset_rsi_under_45"),
          ("EMAs close", "reset_emas_close"))


def load(path=None):
    if path:
        return json.load(open(path))
    return json.loads(subprocess.run(["git", "show", "origin/radar-data:probe_buypoints.json"], cwd=ROOT, check=True,
                                     capture_output=True, text=True).stdout)


def rows(ts, pre):
    out = []
    for t in ts:
        if t.get(pre + "R") is None or t.get(pre + "risk_pct") is None or "reset_any" not in t:
            continue
        if pre == "" and t.get("bought") != "level":
            continue                                    # the upper limit: level buys only
        if pre == "close_" and t.get("bought") == "open":
            continue
        if (t.get("dollar_vol_20d_m") or 0) < MIN_DV:
            continue
        net = t[pre + "result_pct"] - COST
        out.append(dict(t, Rn=net / max(t[pre + "risk_pct"], FLOOR), net=net))
    return out


def st(rs, mid):
    n = len(rs)
    if not n:
        return None
    R = [r["Rn"] for r in rs]
    m = sum(R) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in R) / (n - 1)) if n > 1 else 0
    h1 = [r["Rn"] for r in rs if r["date"] < mid]
    h2 = [r["Rn"] for r in rs if r["date"] >= mid]
    return dict(n=n, win=round(100 * sum(1 for r in rs if r["net"] > 0) / n), avgR=round(m, 3), t=round(m / (sd / math.sqrt(n)), 2) if sd else 0,
                half1=round(sum(h1) / len(h1), 3) if h1 else None, half2=round(sum(h2) / len(h2), 3) if h2 else None)


def luck(a, b, n=2000, seed=7):
    """p: how often shuffled labels give a reset-minus-no-reset gap at least as big as the real one"""
    if len(a) < 10 or len(b) < 10:
        return None
    real = sum(a) / len(a) - sum(b) / len(b)
    pool, k = a + b, len(a)
    rnd = random.Random(seed)
    hit = 0
    for _ in range(n):
        rnd.shuffle(pool)
        if sum(pool[:k]) / k - sum(pool[k:]) / (len(pool) - k) >= real:
            hit += 1
    return round(hit / n, 4)


def compare(rs, col, mid):
    yes, no = [r for r in rs if r.get(col)], [r for r in rs if not r.get(col)]
    return dict(reset=st(yes, mid), no_reset=st(no, mid), p=luck([r["Rn"] for r in yes], [r["Rn"] for r in no]))


def main():
    d = load(sys.argv[1] if len(sys.argv) > 1 else None)
    ts = d["trades"]
    dates = sorted(t["date"] for t in ts)
    mid = dates[len(dates) // 2]
    kinds = sorted({t["buy_point"] for t in ts})
    out = dict(made_at=d.get("made_at"), first=d.get("first"), last=d.get("last"), middle_date=mid, tactics={})
    for name, pre in TACTICS:
        rs = rows(ts, pre)
        if not rs:
            continue
        T = out["tactics"][name] = {}
        for rname, col in RESETS:
            T[rname] = {"all buy points": compare(rs, col, mid),
                        "after a big run (8+ ADRs into the top)": compare([r for r in rs if r.get("big_run_8adr")], col, mid),
                        "after a smaller run": compare([r for r in rs if not r.get("big_run_8adr")], col, mid)}
        T["by buy point (any reset)"] = {k: compare([r for r in rs if r["buy_point"] == k], "reset_any", mid) for k in kinds}
        T["by buy point, big runs (any reset)"] = {k: compare([r for r in rs if r["buy_point"] == k and r.get("big_run_8adr")], "reset_any", mid)
                                                   for k in kinds}
    json.dump(out, open(os.path.join(ROOT, "tools", "reset_analysis.json"), "w"), indent=1)

    def line(lbl, c):
        f = lambda s: "-" if not s else f"{s['n']:5d} {s['win']:3d}% {s['avgR']:+.3f}R t{s['t']:+5.1f} halves {s['half1']:+.2f}/{s['half2']:+.2f}" \
            if s['half1'] is not None and s['half2'] is not None else f"{s['n']:5d} {s['win']:3d}% {s['avgR']:+.3f}R t{s['t']:+5.1f}"
        print(f"  {lbl:44s} reset: {f(c['reset'])} | no reset: {f(c['no_reset'])} | luck p {c['p']}")
    for name, T in out["tactics"].items():
        print(f"\n== {name}")
        for rname, _ in RESETS:
            for grp, c in T[rname].items():
                line(f"{rname} / {grp}", c)
        print("  -- by buy point (any reset), all runs:")
        for k, c in T["by buy point (any reset)"].items():
            line(k, c)
        print("  -- by buy point (any reset), big runs only:")
        for k, c in T["by buy point, big runs (any reset)"].items():
            line(k, c)


if __name__ == "__main__":
    main()
