#!/usr/bin/env python3
"""Where buy points stop working, measured from the momentum's starting point (the user, Nov 1 2026: "from its starting
point of momentum, what percentage and timeframe").

  git fetch -q origin +refs/heads/radar-data:refs/remotes/origin/radar-data
  python3 tools/momentum_cutoff.py [probe_buypoints.json]      # prints the grid and the cutoffs, saves tools/momentum_cutoff.json

The starting point (scanner/mgmt.py reset): the lowest low of the stock's last rest of 40+ sessions without a new 6-month
high (AEHR: Nov 21 2025, 18.70). run_from_start_pct = from it to the close the day before the buy; sessions_from_start = its
age. The grid: net R (0.15% costs, risk floored at 1%) by run x time, with both halves; the cutoffs "run X%+ within Y
months" past vs under, with the luck test (tools/reset_analysis.py).
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import reset_analysis as ra  # noqa: E402

RUN = ((None, 100), (100, 200), (200, 300), (300, 400), (400, None))
TIME = ((None, 63, "up to 3 months"), (63, 126, "3-6 months"), (126, 189, "6-9 months"), (189, None, "9+ months"))
CUT_RUN = (200, 250, 300, 400, 500)
CUT_TIME = ((63, "3 months"), (126, "6 months"), (168, "8 months"), (252, "12 months"), (10 ** 6, "any time"))


def inb(x, lo, hi):
    return x is not None and (lo is None or x >= lo) and (hi is None or x < hi)


def main():
    d = ra.load(sys.argv[1] if len(sys.argv) > 1 else None)
    ts = [t for t in d["trades"] if t.get("run_from_start_pct") is not None]
    dates = sorted(t["date"] for t in ts)
    mid = dates[len(dates) // 2]
    out = dict(made_at=d.get("made_at"), middle_date=mid, tactics={})

    def f(s, short=False):
        if not s:
            return "-"
        if short:
            return f"{s['avgR']:+.2f}R ({s['n']})"
        h = f" halves {s['half1']:+.2f}/{s['half2']:+.2f}" if s["half1"] is not None and s["half2"] is not None else ""
        return f"{s['n']:5d} {s['win']:3d}% {s['avgR']:+.3f}R t{s['t']:+5.1f}{h}"
    for name, pre in ra.TACTICS:
        rs = ra.rows(ts, pre)
        if not rs:
            continue
        T = out["tactics"][name] = {"grid": {}, "cutoffs": {}}
        print(f"\n== {name} ({len(rs)} buy points): average R (trades) by the run from the momentum start x its age")
        print("  run \\ age       " + "".join(f"{lbl:>20s}" for _, _, lbl in TIME))
        for rlo, rhi in RUN:
            rl = f"under {rhi}%" if rlo is None else f"{rlo}%+" if rhi is None else f"{rlo}-{rhi}%"
            cells = []
            for tlo, thi, tl in TIME:
                s = ra.st([r for r in rs if inb(r["run_from_start_pct"], rlo, rhi) and inb(r["sessions_from_start"], tlo, thi)], mid)
                T["grid"][f"{rl} / {tl}"] = s
                cells.append(f(s, True))
            print(f"  {rl:15s}" + "".join(f"{c:>20s}" for c in cells))
        print("  cutoffs: run X%+ reached within Y (past it | under it | luck p)")
        for x in CUT_RUN:
            for y, yl in CUT_TIME:
                past = [r for r in rs if r["run_from_start_pct"] >= x and r["sessions_from_start"] <= y]
                under = [r for r in rs if not (r["run_from_start_pct"] >= x and r["sessions_from_start"] <= y)]
                p = ra.luck([r["Rn"] for r in under], [r["Rn"] for r in past], n=1000) if len(past) >= 10 else None
                T["cutoffs"][f"{x}%+ within {yl}"] = dict(past=ra.st(past, mid), under=ra.st(under, mid), p=p)
                print(f"    {x:4d}%+ within {yl:10s} past: {f(ra.st(past, mid))} | under: {f(ra.st(under, mid))} | p {p}")
    json.dump(out, open(os.path.join(ROOT, "tools", "momentum_cutoff.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
