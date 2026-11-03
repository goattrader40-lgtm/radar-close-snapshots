#!/usr/bin/env python3
"""Study (Nov 3 2026, the user: "combine group rank, RS and Trend with our buy points: which combination works best"):
tags every trade already tested (radar-data probe_buypoints.json = 5,783 buy points after launches, probe_launch_orh.json
= 1,441 launch days, Aug 2025 - Oct 2026, both with the user's management) with what the portal would have shown:

  group   the stock's best group percentile (launch.rank_history: themes vs themes, groups vs groups, 1/3/6-month;
          Top = 97+, Strong = 90-96.9; a loose "· other" group capped under Strong)
  rs      the market rank 0-1 (its own 1/3/6-month return vs every ranked stock; RS 97+ = 0.97)
  trend   the Trend (radar/pipeline.py trend_at: Negative / Reclaim / Turn up / Up / Resting / '') and sessions in it
  each at the close BEFORE the buy day ("prev") and at the buy day's close ("day"); a close buy knows "day", a level /
  open / 5-minute buy only "prev".

  python3 scanner/probe_combo_tags.py --bars BARS.json.gz --stocks stocks.json --bp probe_buypoints.json \
      --orh probe_launch_orh.json --out probe_combo_tags.json
Group membership is today's (stocks.json), as in the earlier group-rank tests.
"""
import argparse, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402


def trend_at(c, e5, e10, e21, e50, i):
    """radar/pipeline.py trend_at (the live Trend), on numpy arrays"""
    if i < 5:
        return None
    base = e10[i] > e21[i] > e50[i] and e50[i] > e50[i - 5]
    if c[i] < e21[i]: return "Negative"
    if not base: return ""
    if c[i - 1] < e21[i - 1]: return "Reclaim"
    if e5[i] > e10[i] and e5[i - 1] <= e10[i - 1]: return "Turn up"
    if c[i] > e50[i] and e10[i] > e10[i - 1] and e21[i] > e21[i - 1]: return "Up"
    return "Resting"


def main():
    ap = argparse.ArgumentParser()
    for k in ("bars", "stocks", "bp", "orh", "out"):
        ap.add_argument("--" + k, required=True)
    a_ = ap.parse_args()
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    rows = json.load(open(a_.stocks))
    best, MK = launch.rank_history(A, cal, rows)
    pos = {d: k for k, d in enumerate(cal)}
    want = set()
    for f in (a_.bp, a_.orh):
        for t in json.load(open(f)).get("trades", []):
            want.add((t["symbol"], t["date"]))
    r2 = lambda x: None if x is None or np.isnan(x) else round(float(x), 3)
    tags, miss = {}, 0
    tcache = {}
    for s, d in sorted(want):
        a = A.get(s)
        if a is None or d not in pos:
            miss += 1
            continue
        st = a.st
        try:
            j = st.dates.index(d)
        except ValueError:
            miss += 1
            continue
        k = pos[d]
        if s not in tcache:
            e5, e10 = a.e5, a.e10
            tcache = {s: (st.c, e5, e10, st.ema21, st.ema50)}
        c, e5, e10, e21, e50 = tcache[s]

        def tr(i):
            t = trend_at(c, e5, e10, e21, e50, i)
            n = 1
            while t is not None and n < 250 and i - n >= 5 and trend_at(c, e5, e10, e21, e50, i - n) == t:
                n += 1
            return t, n
        g, m = best.get(s), MK.get(s)
        tp, tpn = tr(j - 1)
        td, tdn = tr(j)
        tags[f"{s}|{d}"] = [r2(g[k - 1]) if g is not None else None, r2(g[k]) if g is not None else None,
                            r2(m[k - 1]) if m is not None else None, r2(m[k]) if m is not None else None, tp, tpn, td, tdn,
                            r2(100 * (c[j - 1] / e21[j - 1] - 1)), r2(100 * (c[j - 1] / e50[j - 1] - 1))]
    out = dict(fields=["group_prev", "group_day", "rs_prev", "rs_day", "trend_prev", "trend_prev_days", "trend_day", "trend_day_days",
                       "vs21_prev_pct", "vs50_prev_pct"], asked=len(want), missing=miss, first=cal[0], last=cal[-1], tags=tags)
    json.dump(out, open(a_.out, "w"), separators=(",", ":"))
    print(f"tagged {len(tags)} of {len(want)}, missing {miss}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        json.dump(dict(error=traceback.format_exc()[-3000:]), open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
        raise
