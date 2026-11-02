#!/usr/bin/env python3
"""Group RANKING definitions for Leading / Emerging / Lagging, tested on 2 years of gap-ups and launches (the user,
Nov 2 2026: momentum traders focus on the top few groups; "emerging" = moving up the ranking fast).

  python3 scanner/probe_grouprank.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json

Groups: every theme on the portal and every industry (a stock counts in each of its themes AND its industry), 3+
members. Each day each group's score from its members' MEDIAN returns, ranked as a percentile among its kind (themes
among themes, industries among industries):
  score "mix":  0.5 x 1-month + 0.3 x 3-month + 0.2 x 1-week
  score "qull": the average of its percentile ranks on 1-month, 3-month and 6-month (Qullamaggie's 1/3/6-month lists)
Labels, for each cut-off X (top 3% / 5% / 10%):
  Leading   rank in the top X and 60%+ of its members above their 50 EMA
  Emerging  not Leading, rank in the top 25% now and in the bottom half at some close in the last 10 sessions, half
            or more of its members above their 21 EMA
  Lagging   rank in the bottom half
  Neutral   the rest
A stock takes the best label of its groups. Gap-ups (5%+, liquid) by the label at the close BEFORE the gap; launches by
the label on the launch day. Also: how many groups are Leading / Emerging on an average day (how selective it is).
"""
import argparse, collections, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402
from probe_gapgroups import summ  # noqa: E402

ORDER = {"Leading": 3, "Emerging": 2, "Neutral": 1, "Lagging": 0}


def ret(c, n):
    r = np.full(c.size, np.nan)
    r[n:] = 100 * (c[n:] / c[:-n] - 1)
    return r


def pct_rank(M):
    """percentile rank (0-1) of each row within each column, NaN-safe"""
    out = np.full(M.shape, np.nan)
    for t in range(M.shape[1]):
        col = M[:, t]
        ok = ~np.isnan(col)
        k = ok.sum()
        if k >= 5:
            order = col[ok].argsort().argsort()
            out[ok, t] = order / (k - 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    stocks = json.load(open(a_.stocks))
    pos = {d: k for k, d in enumerate(cal)}
    T = len(cal)
    mem = collections.defaultdict(list)
    sg = collections.defaultdict(list)
    for r in stocks:
        s = r["symbol"]
        if s not in A:
            continue
        for t in [x for x in (r.get("themes") or "").split(" | ") if x]:
            mem["theme:" + t].append(s); sg[s].append("theme:" + t)
        if r.get("industry"):
            mem["ind:" + r["industry"]].append(s); sg[s].append("ind:" + r["industry"])
    names = [g for g, ms in mem.items() if len(ms) >= 3]
    gi = {g: j for j, g in enumerate(names)}
    G = len(names)
    m5, m21, m63, m126, b50, b21 = (np.full((G, T), np.nan) for _ in range(6))
    import warnings
    warnings.simplefilter("ignore", RuntimeWarning)
    for g in names:
        ms = mem[g]
        R = {n: np.full((len(ms), T), np.nan) for n in (5, 21, 63, 126)}
        a50, a21 = np.full((len(ms), T), np.nan), np.full((len(ms), T), np.nan)
        for j, s in enumerate(ms):
            a = A[s]
            idx = [pos[d] for d in a.st.dates if d in pos]
            if len(idx) != len(a.st.dates):
                continue
            for n in R:
                R[n][j, idx] = ret(a.st.c, n)
            a50[j, idx] = a.st.c > a.e50
            a21[j, idx] = a.st.c > a.e21
        j = gi[g]
        m5[j], m21[j], m63[j], m126[j] = (np.nanmedian(R[n], axis=0) for n in (5, 21, 63, 126))
        b50[j], b21[j] = np.nanmean(a50, axis=0), np.nanmean(a21, axis=0)
    kinds = {"theme": [gi[g] for g in names if g.startswith("theme:")], "ind": [gi[g] for g in names if g.startswith("ind:")]}
    scores = {"mix": 0.5 * m21 + 0.3 * m63 + 0.2 * m5}
    rk = {}
    for nm in ("mix", "qull"):
        P = np.full((G, T), np.nan)
        for kind, rows in kinds.items():
            if nm == "mix":
                P[rows] = pct_rank(scores["mix"][rows])
            else:
                P[rows] = np.nanmean([pct_rank(m21[rows]), pct_rank(m63[rows]), pct_rank(m126[rows])], axis=0)
                P[rows] = pct_rank(P[rows])
        rk[nm] = P
    variants = [(nm, x) for nm in ("mix", "qull") for x in (0.03, 0.05, 0.10)]
    out = {"groups": {"themes": len(kinds["theme"]), "industries": len(kinds["ind"])}, "variants": {}}
    ev = launch.detect(A, groups, GS, cal, S)
    for nm, x in variants:
        P = rk[nm]
        low10 = np.full(P.shape, np.nan)
        for t in range(T):
            low10[:, t] = np.nanmin(P[:, max(0, t - 10):t + 1], axis=1)
        lead = (P >= 1 - x) & (b50 >= 0.6)
        emer = ~lead & (P >= 0.75) & (low10 <= 0.5) & (b21 >= 0.5)
        lag = P < 0.5
        lab = np.where(lead, 3, np.where(emer, 2, np.where(lag, 0, 1)))
        lab = np.where(np.isnan(P), -1, lab)

        def label(s, k):
            v = max((int(lab[gi[g], k]) for g in sg.get(s, []) if g in gi), default=-1)
            return {3: "Leading", 2: "Emerging", 1: "Neutral", 0: "Lagging", -1: "No group"}[v]
        gaps = collections.defaultdict(list)
        for s, a in A.items():
            st = a.st
            n = len(st.dates)
            for i in range(max(a.start, 21), n - 1):
                if not (a.gap[i] >= 5 and a.liquid[i - 1]):
                    continue
                k = pos.get(st.dates[i])
                if k is None or k < 130:
                    continue
                o = st.o[i]
                j20 = min(i + 20, n - 1)
                r = dict(day=100 * (st.c[i] / o - 1), r5=100 * (st.c[min(i + 5, n - 1)] / o - 1) if i + 5 < n else None,
                         r20=100 * (st.c[j20] / o - 1) if i + 20 < n else None, mx=100 * (st.h[i:j20 + 1].max() / o - 1))
                L0 = label(s, k - 1)
                gaps[L0].append(r)
                gaps[("10%+ gap · " if a.gap[i] >= 10 else "5-10% gap · ") + L0].append(r)
        lr = collections.defaultdict(list)
        for s, i, k, gs, gn in ev:
            a = A[s]
            st = a.st
            if i + 20 >= len(st.dates) or k < 130:
                continue
            c0 = st.c[i]
            r = dict(day=0.0, r5=100 * (st.c[i + 5] / c0 - 1), r20=100 * (st.c[i + 20] / c0 - 1), mx=100 * (st.h[i + 1:i + 21].max() / c0 - 1))
            lr[label(s, k)].append(r)
            lr["grade " + launch.grade(a, i)[0] + " · " + label(s, k)].append(r)
        th, ind = kinds["theme"], kinds["ind"]
        per_day = {"leading_themes": round(float(np.mean(lead[th][:, 130:].sum(axis=0))), 1),
                   "leading_industries": round(float(np.mean(lead[ind][:, 130:].sum(axis=0))), 1),
                   "emerging_themes": round(float(np.mean(emer[th][:, 130:].sum(axis=0))), 1),
                   "emerging_industries": round(float(np.mean(emer[ind][:, 130:].sum(axis=0))), 1)}
        today = {"leading": sorted(g for g in names if lab[gi[g], -1] == 3), "emerging": sorted(g for g in names if lab[gi[g], -1] == 2)}
        out["variants"][f"{nm} top {int(x * 100)}%"] = {
            "groups_per_day": per_day, "today": today,
            "gaps": {k: summ(v) for k, v in sorted(gaps.items())},
            "launches": {k: {kk: vv for kk, vv in summ(v).items() if kk not in ("faded_pct", "held_pct", "avg_day_from_open")}
                         for k, v in sorted(lr.items())}}
    # separate bands (not cumulative), by the stock's best group rank: overall, its best theme, its best industry;
    # top bands also split by breadth (60%+ of the group over its 50 EMA)
    def band(p):
        return None if p is None or np.isnan(p) else "1 top 3%" if p >= 0.97 else "2 3-10%" if p >= 0.90 else "3 10-20%" if p >= 0.80 \
            else "4 20-50%" if p >= 0.50 else "5 bottom half"
    out["bands"] = {}
    for nm in ("qull", "mix"):
        P = rk[nm]

        def best_p(s, k, pref):
            c = [(P[gi[g], k], b50[gi[g], k]) for g in sg.get(s, []) if g in gi and g.startswith(pref) and not np.isnan(P[gi[g], k])]
            return max(c) if c else (None, None)
        res = {w: collections.defaultdict(list) for w in ("gaps", "gaps 10%+", "launches")}
        def add(where, s, k, r):
            for lab_, pref in (("best group", ""), ("best theme", "theme:"), ("best industry", "ind:")):
                p, br = best_p(s, k, pref)
                bd = band(p)
                if bd is None:
                    continue
                res[where][lab_ + " · " + bd].append(r)
                if bd < "3":
                    res[where][lab_ + " · " + bd + (" · breadth 60%+" if br >= 0.6 else " · breadth under 60%")].append(r)
        for s, a in A.items():
            st = a.st
            n = len(st.dates)
            for i in range(max(a.start, 21), n - 1):
                if not (a.gap[i] >= 5 and a.liquid[i - 1]):
                    continue
                k = pos.get(st.dates[i])
                if k is None or k < 130:
                    continue
                o = st.o[i]
                j20 = min(i + 20, n - 1)
                r = dict(day=100 * (st.c[i] / o - 1), r5=100 * (st.c[min(i + 5, n - 1)] / o - 1) if i + 5 < n else None,
                         r20=100 * (st.c[j20] / o - 1) if i + 20 < n else None, mx=100 * (st.h[i:j20 + 1].max() / o - 1))
                add("gaps", s, k - 1, r)
                if a.gap[i] >= 10:
                    add("gaps 10%+", s, k - 1, r)
        for s, i, k, gs, gn in ev:
            a = A[s]
            st = a.st
            if i + 20 >= len(st.dates) or k < 130:
                continue
            c0 = st.c[i]
            add("launches", s, k, dict(day=0.0, r5=100 * (st.c[i + 5] / c0 - 1), r20=100 * (st.c[i + 20] / c0 - 1),
                                       mx=100 * (st.h[i + 1:i + 21].max() / c0 - 1)))
        out["bands"][nm] = {w: {k: summ(v) for k, v in sorted(d.items())} for w, d in res.items()}
    json.dump(out, open(a_.out, "w"), indent=1)
    print(json.dumps(out)[:2000])


if __name__ == "__main__":
    main()
