#!/usr/bin/env python3
"""The gap retest (the user's rule, Nov 1 2026): a big gap-up launch-type day, then the retest of its gap holding the 10
or the 21 EMA.

  python3 scanner/probe_gapretest.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json
  (with ALPACA_KEY_ID / ALPACA_SECRET: also the next morning's 5-minute entry)

  the gap day   a 6%+ gap on volume that is one of the launch days: a power day (4x+, 8%+ gap, 10%+ day), a launch day
                (opened up, closed up 5%+ in the top half on 1.5x+, the 200 SMA rules) or a big gap-up day (2x+ volume,
                closed over the day before's high: the gap held); liquid ($20M+ a day, 600K+ shares, ADR 3.5%+, $10+)
  the gap       from the day before's high (where the gap starts) up to the gap day's low
  the retest    within 30 sessions, after the stock first closed an ADR+ over the gap: the first day whose low comes back
                into the gap (from half an ADR under the day before's high to a quarter ADR over the gap day's low) and
                closes back over the day before's high: the gap held. A close under the day before's high first = the gap
                filled, no retest
  with an EMA   the 10 or the 21 EMA at the gap (within an ADR of it), that day's low touching it and the close over it
                (retest_with: "10 EMA", "21 EMA", "10 EMA & 21 EMA" or "no EMA")
  the buy       at the retest day's close, the stop its low; and the next morning over the 5-minute opening range high, the
                stop the 5-minute low; your management (scanner/mgmt.py: 1/3 at +2 ADR, 1/3 at +5 ADR, the runners out on a
                daily close under the 21 or the 10 EMA)
"""
import argparse, collections, datetime, json, multiprocessing, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402
import mgmt  # noqa: E402

L = launch.L
A = {}


def one(s):
    a = A[s]
    st = a.st
    c, h, l = st.c, st.h, st.l
    n = c.size
    out = []
    for g in range(max(a.start, 201), n - 3):
        if not (a.gap[g] >= 6 and a.liquid[g]):
            continue
        kind = ("power day" if a.power(g) else "launch day" if a.candidate(g)
                else "big gap-up day" if a.rv[g] >= 2 and c[g] > h[g - 1] else None)
        if not kind:
            continue
        lvl = float(h[g - 1])                       # where the gap starts
        gtop = max(float(l[g]), lvl)                # the gap's top: the gap day's low
        adr = float(st.adr[g]) if st.adr[g] > 0 else 5.0
        z_lo, z_hi = lvl * (1 - 0.5 * adr / 100), gtop * (1 + adr / 400)
        away = False
        for k in range(g + 1, min(n - 1, g + 31)):
            if c[k] < lvl:
                break                               # the gap filled at a close
            if not away:
                away = bool(c[k] >= gtop * (1 + adr / 100))
                continue
            if l[k] > z_hi:
                continue
            if l[k] < z_lo:
                break                               # through the gap, deeper than half an ADR: no retest of it
            with_ = [nm for nm, e in (("10 EMA", a.e10), ("21 EMA", a.e21))
                     if lvl * (1 - adr / 100) <= e[k] <= gtop * (1 + adr / 100) and l[k] <= e[k] * (1 + adr / 400) and c[k] > e[k]]
            buy, stop = float(c[k]), float(l[k])
            if buy <= stop:
                break
            x21, x10 = mgmt.run(a, k, buy, stop, runner=21), mgmt.run(a, k, buy, stop, runner=10)
            r = dict(symbol=s, gap_date=st.dates[g], gap_day=kind, gap_pct=round(float(a.gap[g]), 2), rvol_gap_day=round(float(a.rv[g]), 2),
                     gap_day_change_pct=round(float(a.chg[g]), 2), date=st.dates[k], sessions_after_gap=k - g,
                     level=round(lvl, 2), gap_top=round(gtop, 2), retest_low=round(float(l[k]), 2),
                     low_vs_level_adr=round(100 * (l[k] / lvl - 1) / adr, 2), retest_with=" & ".join(with_) or "no EMA",
                     rvol_day=round(float(a.rv[k]), 2), day_change_pct=round(float(a.chg[k]), 2), adr_pct=round(float(st.adr[k - 1]), 2),
                     close_in_range_pct=round(100 * float(a.clpos[k])))
            r.update(mgmt.liquidity(a, k))
            r.update(mgmt.reset(a, k))
            r.update(mgmt.cols(x21, "close_"))
            r.update(mgmt.cols(x10, "close_", "_10"))
            out.append(r)
            break                                   # once per gap
    return out


def summ(ts, m="close_"):
    ts = [t for t in ts if m + "R" in t]
    if not ts:
        return dict(trades=0)
    R = np.array([t[m + "R"] for t in ts])
    return dict(trades=len(ts), win=round(100 * float(np.mean([t[m + "win"] for t in ts]))),
                avg_pct=round(float(np.mean([t[m + "result_pct"] for t in ts])), 2), avg_R=round(float(R.mean()), 2),
                med_R=round(float(np.median(R)), 2), total_R=round(float(R.sum()), 1),
                reached_2ADR=round(100 * float(np.mean([t[m + "reached_2ADR"] for t in ts]))),
                risk_med_pct=round(float(np.median([t[m + "risk_pct"] for t in ts])), 2))


def main():
    global A
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    L["catalyst_launch"] = 0
    launch.CATALYST_DAYS.clear()
    with multiprocessing.get_context("fork").Pool(os.cpu_count() or 2) as pool:
        ts = [t for r in pool.map(one, sorted(A), chunksize=16) for t in r]
    print(len(ts), "gap retests")
    # the next morning's 5-minute entry: over the 5-minute opening range high, the stop its low
    if os.environ.get("ALPACA_KEY_ID"):
        import probe_catalyst as pc
        import probe_pb1h as pb
        by_day = collections.defaultdict(list)
        for t in ts:
            a = A[t["symbol"]]
            k = a.st.dates.index(t["date"]) + 1
            if k < a.st.c.size:
                by_day[a.st.dates[k]].append((t, k))
        for d, tk in sorted(by_day.items()):
            t0 = datetime.datetime.fromisoformat(d + "T09:30").replace(tzinfo=pc.NY)
            b5 = pb.bars(sorted({t["symbol"] for t, k in tk}), t0, t0 + datetime.timedelta(minutes=390), "5Min")
            for t, k in tk:
                b = b5.get(pc.alp(t["symbol"]))
                t["min5_bought"] = 0
                if not b or not b[0]["t"].startswith(pc.iso(t0)[:16]):
                    continue
                m = next((x for x in range(1, len(b)) if b[x]["h"] > b[0]["h"]), None)
                if m is None:
                    continue
                buy5 = max(b[0]["h"], b[m]["o"])
                for runner, suf in ((21, ""), (10, "_10")):
                    x = pb.trade(A[t["symbol"]], k, b, -1e9, {}, entry=(m, buy5), runner=runner)
                    if x and x.get("broke"):
                        t["min5_bought"] = 1
                        t.update(mgmt.cols(x, "min5_", suf))
    groups_ = sorted({t["retest_with"] for t in ts})
    out = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), first=cal[200], last=cal[-1],
               all={m: summ(ts, m) for m in ("close_", "min5_")},
               by_gap_day={k: {m: summ([t for t in ts if t["gap_day"] == k], m) for m in ("close_", "min5_")}
                           for k in ("power day", "launch day", "big gap-up day")},
               by_retest_with={k: {m: summ([t for t in ts if t["retest_with"] == k], m) for m in ("close_", "min5_")} for k in groups_},
               trades=ts)
    json.dump(out, open(a_.out, "w"))
    print(json.dumps({k: v for k, v in out.items() if k != "trades"}, indent=1))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        json.dump(dict(error=traceback.format_exc()[-3000:]), open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
        raise
