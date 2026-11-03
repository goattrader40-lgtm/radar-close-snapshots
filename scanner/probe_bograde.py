#!/usr/bin/env python3
"""Breakout alert grade: the old "Leading theme" vs the new group rank (the user, Nov 3 2026: "it should replace with new").

  python3 scanner/probe_bograde.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json

Every base breakout after a launch in 2 years, as the Launches tab follows it (scanner/probe_buypoints.py: the day's
high crosses the base top; bought at the top, or the open when it gaps over). The alert grade:
  early  the 1st or 2nd breakout since the launch, within 50 sessions of it
  build  the volume building the 5 days before (1.1x+ the 50 before)
  group  OLD: its theme Leading (60%+ over the 50 EMA, median 1-month +8%)
         NEW: its best group's rank (themes vs themes, industries vs industries, 1/3/6-month) at the close before:
              Top or Strong (top 10%), or Top only (top 3%)
  A = early + group + build, B = early + one of the two, C = the rest
Outcomes: ran 10% / 20% within 20 sessions of the buy, the user's management (R, win), on all base-breakout crosses and on
the ones that closed as a breakout (the engine's read that evening).
"""
import argparse, collections, json, multiprocessing, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402
import probe_buypoints as pbp  # noqa: E402


def pct_cols(X, need=5):
    ok = ~np.isnan(X)
    k = ok.sum(axis=0)
    Xf = np.where(ok, X, -np.inf)
    order = Xf.argsort(axis=0, kind="stable").argsort(axis=0, kind="stable") - (X.shape[0] - k)[None, :]
    with np.errstate(all="ignore"):
        P = order / np.maximum(k - 1, 1)[None, :]
    return np.where(ok & (k >= need)[None, :], P, np.nan)


def rank_history(A, cal, stocks):
    """P[group][day]: the live group rank (launch.group_rank) on every day; and each stock's groups"""
    pos = {d: k for k, d in enumerate(cal)}
    T = len(cal)
    mem, sg = collections.defaultdict(list), collections.defaultdict(list)
    for r in stocks:
        s = r["symbol"]
        if s not in A or any(d not in pos for d in A[s].st.dates):
            continue
        for t in [x for x in (r.get("themes") or "").split(" | ") if x]:
            mem["theme:" + t].append(s); sg[s].append("theme:" + t)
        if r.get("industry"):
            mem["ind:" + r["industry"]].append(s); sg[s].append("ind:" + r["industry"])
    names = [g for g, ms in mem.items() if len(ms) >= 3]
    gi = {g: j for j, g in enumerate(names)}
    med = {n: np.full((len(names), T), np.nan) for n in (21, 63, 126)}
    import warnings
    warnings.simplefilter("ignore", RuntimeWarning)
    for g in names:
        R = {n: np.full((len(mem[g]), T), np.nan) for n in med}
        for j, s in enumerate(mem[g]):
            st = A[s].st
            idx = [pos[d] for d in st.dates]
            for n in med:
                r = np.full(st.c.size, np.nan)
                r[n:] = 100 * (st.c[n:] / st.c[:-n] - 1)
                R[n][j, idx] = r
        for n in med:
            med[n][gi[g]] = np.nanmedian(R[n], axis=0)
    P = np.full((len(names), T), np.nan)
    for pref in ("theme:", "ind:"):
        rows = [gi[g] for g in names if g.startswith(pref)]
        P[rows] = pct_cols(np.nanmean([pct_cols(med[n][rows]) for n in med], axis=0))
    return P, gi, sg, pos


def summ(ts):
    if not ts:
        return dict(n=0)
    m = lambda k: round(100 * float(np.mean([t[k] for t in ts])), 1)
    return dict(n=len(ts), ran10=m("ran10"), ran20=m("ran20"), win=m("win"), avg_R=round(float(np.mean([t["R"] for t in ts])), 2),
                total_R=round(float(np.sum([t["R"] for t in ts])), 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    pbp.A, pbp.GROUPS, pbp.GS, pbp.POS = A, groups, GS, {d: k for k, d in enumerate(cal)}
    launch.L["catalyst_launch"] = 0
    launch.CATALYST_DAYS.clear()
    keys = sorted({(s, i) for s, i, k, gs, gn in launch.detect(A, groups, GS, cal, S) if i >= 200})
    with multiprocessing.get_context("fork").Pool(os.cpu_count() or 2) as pool:
        ts = [t for r in pool.map(pbp.one, keys, chunksize=8) for t in r]
    best = {}
    for t in ts:
        k_ = (t["symbol"], t["date"], t["buy_point"], t["bought"])
        if k_ not in best or t["launch_date"] > best[k_]["launch_date"]:
            best[k_] = t
    bo = [t for t in best.values() if t["buy_point"] == "base breakout"]
    P, gi, sg, pos = rank_history(A, cal, json.load(open(a_.stocks)))
    rows = []
    for t in bo:
        a = A[t["symbol"]]
        st = a.st
        j = st.dates.index(t["date"])
        k = pos[t["date"]]
        buy = max(float(t["level"]), float(st.o[j]))
        hi = float(st.h[j + 1:min(st.c.size, j + 21)].max()) if j + 1 < st.c.size else buy
        ps = [P[gi[g], k - 1] for g in sg.get(t["symbol"], []) if g in gi and not np.isnan(P[gi[g], k - 1])]
        p = max(ps) if ps else None
        old_prev = launch.best_group(t["symbol"], k - 1, groups, GS)[0]       # the old status at the close before
        early, build = bool(t["early_breakout"]), (t.get("volume_building_5d") or 0) >= 1.1
        g = lambda lead: "A" if early and lead and build else "B" if early and (lead or build) else "C"
        rows.append(dict(symbol=t["symbol"], date=t["date"], confirmed=int(t.get("engine_confirmed", 1)),
                         ran10=int(hi >= buy * 1.1), ran20=int(hi >= buy * 1.2), R=t["R"], win=t["win"],
                         early=int(early), build=int(build), group_pct=None if p is None else round(100 * float(p), 1),
                         old=t["breakout_grade"], old_prev=g(old_prev == 2), new10=g(p is not None and p >= 0.90), new3=g(p is not None and p >= 0.97),
                         lead_old=int(t["theme_status"] == "Leading"), lead10=int(p is not None and p >= 0.90), lead3=int(p is not None and p >= 0.97)))
    out = {"first": cal[200], "last": cal[-1], "base_breakouts": len(rows), "results": {}}
    for scope, rs in (("all base-breakout crosses", rows), ("closed as a breakout", [r for r in rows if r["confirmed"]])):
        res = {}
        for nm in ("old", "old_prev", "new10", "new3"):
            res[nm] = {gr: summ([r for r in rs if r[nm] == gr]) for gr in ("A", "B", "C")}
        for nm in ("lead_old", "lead10", "lead3"):
            res["group alone: " + nm] = {"yes": summ([r for r in rs if r[nm]]), "no": summ([r for r in rs if not r[nm]])}
            res["early + group: " + nm] = {"yes": summ([r for r in rs if r[nm] and r["early"]]), "no": summ([r for r in rs if not r[nm] and r["early"]])}
        res["all"] = summ(rs)
        out["results"][scope] = res
    out["rows"] = rows
    json.dump(out, open(a_.out, "w"))
    print(json.dumps(out["results"], indent=1)[:4000])


if __name__ == "__main__":
    main()
