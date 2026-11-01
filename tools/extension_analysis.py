#!/usr/bin/env python3
"""How far a stock can run before buy points stop working (the user, Nov 1 2026: "if price went too far from its
starting point, say 500%+ within 7-8 months, no buy points: we have to determine after what point we block them").

  git fetch -q origin +refs/heads/radar-data:refs/remotes/origin/radar-data
  python3 tools/extension_analysis.py [probe_buypoints.json]     # prints the tables, saves tools/extension_analysis.json

Each buy point carries (scanner/mgmt.py reset, from the bars up to the day before the buy): the % run from the lowest low
of the last 3 / 6 / 8 / 12 months and the sessions since that low, and the % over the 200 SMA. For each cutoff: the buy
points past it vs under it, net R (0.15% costs, risk floored at 1%), both halves, and the luck test (tools/reset_analysis.py).
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import reset_analysis as ra  # noqa: E402

CUTS = {"run_from_6m_low_pct": (100, 200, 300, 400, 500, 700), "run_from_8m_low_pct": (100, 200, 300, 400, 500, 700),
        "run_from_12m_low_pct": (200, 300, 500, 700, 1000), "over_200sma_pct": (50, 75, 100, 150, 200)}
BANDS = {"run_from_8m_low_pct": ((None, 100), (100, 200), (200, 300), (300, 500), (500, None)),
         "over_200sma_pct": ((None, 25), (25, 50), (50, 100), (100, 150), (150, None))}


def main():
    d = ra.load(sys.argv[1] if len(sys.argv) > 1 else None)
    ts = [t for t in d["trades"] if t.get("run_from_8m_low_pct") is not None]
    dates = sorted(t["date"] for t in ts)
    mid = dates[len(dates) // 2]
    out = dict(made_at=d.get("made_at"), middle_date=mid, tactics={})

    def f(s):
        if not s:
            return "      -"
        h = f" halves {s['half1']:+.2f}/{s['half2']:+.2f}" if s["half1"] is not None and s["half2"] is not None else ""
        return f"{s['n']:5d} {s['win']:3d}% {s['avgR']:+.3f}R t{s['t']:+5.1f}{h}"
    for name, pre in ra.TACTICS:
        rs = ra.rows(ts, pre)
        if not rs:
            continue
        T = out["tactics"][name] = {"bands": {}, "cutoffs": {}}
        print(f"\n== {name} ({len(rs)} buy points)")
        for col, bands in BANDS.items():
            print(f"  by {col}:")
            for lo, hi in bands:
                sel = [r for r in rs if (lo is None or r[col] >= lo) and (hi is None or r[col] < hi)]
                lbl = f"under {hi}%" if lo is None else f"{lo}%+" if hi is None else f"{lo}-{hi}%"
                s = ra.st(sel, mid)
                T["bands"][f"{col} {lbl}"] = s
                print(f"    {lbl:12s} {f(s)}")
        for col, cuts in CUTS.items():
            print(f"  cutoffs on {col} (past it | under it | luck p):")
            for x in cuts:
                past = [r for r in rs if r[col] is not None and r[col] >= x]
                under = [r for r in rs if r[col] is not None and r[col] < x]
                p = ra.luck([r["Rn"] for r in under], [r["Rn"] for r in past])      # under minus past
                T["cutoffs"][f"{col} {x}%"] = dict(past=ra.st(past, mid), under=ra.st(under, mid), p=p)
                print(f"    {x:5d}%+   past: {f(ra.st(past, mid))} | under: {f(ra.st(under, mid))} | p {p}")
    json.dump(out, open(os.path.join(ROOT, "tools", "extension_analysis.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
