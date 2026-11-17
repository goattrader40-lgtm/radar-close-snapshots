#!/usr/bin/env python3
"""What the Watchlist's relative volume on 20 days (was 10) changes: for each of the last N sessions, the stocks that
pass 1-EP/GAP (gap, 2x, close up 5%) and 1-UPDAY (up 4%, 1x) on one average and not on the other.

  python3 scanner/probe_rvdays.py --bars /tmp/bars.json.gz --out /tmp/probe_rvdays.json [--days 30]

radar-tools cmd `rvdays` -> radar-data probe_rvdays.json (the user, Nov 17 2026: "for rvol it should 20").
"""
import argparse, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run, screens  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True); ap.add_argument("--out", required=True); ap.add_argument("--days", type=int, default=30)
    a = ap.parse_args()
    cfg = json.load(open(os.path.join(HERE, "settings.json")))
    D = run.load_bars(a.bars)
    stocks, _ = run.build(D, cfg)
    S, X = cfg["standard"], cfg["screeners"]
    E, U = X["EP-GAPUP-BREAKOUT"], X["HOTTEST STOCKS"]
    days = [b[0] for b in D["bars"]["SPY"]][-a.days:]
    out = dict(days=days, n_stocks=len(stocks), by_day={}, totals={})
    tot = dict(ep10=0, ep20=0, ep_added=0, ep_dropped=0, up10=0, up20=0, up_added=0, up_dropped=0)

    def rv(st, i, n):
        return float(st.v[i] / np.mean(st.v[i - n:i])) if i >= n and np.mean(st.v[i - n:i]) > 0 else float("nan")

    for d in days:
        row = dict(ep_added=[], ep_dropped=[], up_added=[], up_dropped=[])
        for sym, st in stocks.items():
            i = st.pos.get(d)
            if i is None or i < 21 or not st.standard(i, S):
                continue
            gap = 100 * (st.o[i] / st.c[i - 1] - 1); chg = 100 * (st.c[i] / st.c[i - 1] - 1)
            r10, r20 = rv(st, i, 10), rv(st, i, 20)
            item = dict(sym=sym, gap=round(gap, 1), chg=round(chg, 1), rv10=round(r10, 2), rv20=round(r20, 2))
            if gap > E["gap_pct"] and chg >= E.get("close_chg_pct", 0):
                a10, a20 = r10 >= E["rel_vol"], r20 >= E["rel_vol"]
                tot["ep10"] += a10; tot["ep20"] += a20
                if a20 and not a10: row["ep_added"].append(item); tot["ep_added"] += 1
                if a10 and not a20: row["ep_dropped"].append(item); tot["ep_dropped"] += 1
            if chg >= U["chg_pct"]:
                a10, a20 = r10 >= U["rel_vol"], r20 >= U["rel_vol"]
                tot["up10"] += a10; tot["up20"] += a20
                if a20 and not a10: row["up_added"].append(item); tot["up_added"] += 1
                if a10 and not a20: row["up_dropped"].append(item); tot["up_dropped"] += 1
        out["by_day"][d] = row
    out["totals"] = {k: int(v) for k, v in tot.items()}
    json.dump(out, open(a.out, "w"))
    print(json.dumps(out["totals"]))


if __name__ == "__main__":
    main()
