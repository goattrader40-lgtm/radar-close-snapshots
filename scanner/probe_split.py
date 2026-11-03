#!/usr/bin/env python3
"""Split the big industries into sub-groups that move together (the user, Nov 3 2026: regional banks move differently
from the money-center banks, gene therapy from other biotech, software has many kinds), and test whether ranking the
sub-groups beats the broad industries on 2 years of gap-ups and launches.

  python3 scanner/probe_split.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json

Industries with 60+ stocks are split; every 21 sessions, from the 120 sessions BEFORE that day only (no look-ahead):
each stock's daily move minus the whole market's median move that day, correlated with every other stock of the
industry, clustered (average linkage) at a correlation cut of 0.25 / 0.35 / 0.45; clusters of 5+ stocks become their
own groups, the rest stay as "<industry> (other)". Themes are unchanged. The rank is the same as live (median 1/3/6-month
return, ranked among the industries / sub-groups, averaged, ranked again; Top = top 3%, Strong = 3-10%).
Also: the clusters on the last day, by member, so they can be named.
"""
import argparse, collections, json, os, sys
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402
from probe_gapgroups import summ  # noqa: E402
from probe_leaders import pct_cols  # noqa: E402

BIG, LOOK, EVERY, MIN_CL = 60, 120, 21, 5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    import warnings
    warnings.simplefilter("ignore", RuntimeWarning)
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    stocks = json.load(open(a_.stocks))
    pos = {d: k for k, d in enumerate(cal)}
    T = len(cal)
    themes, ind = collections.defaultdict(list), {}
    for r in stocks:
        s = r["symbol"]
        if s not in A or any(d not in pos for d in A[s].st.dates):
            continue
        for t in [x for x in (r.get("themes") or "").split(" | ") if x]:
            themes[t].append(s)
        if r.get("industry"):
            ind[s] = r["industry"]
    syms = sorted(ind)
    si = {s: j for j, s in enumerate(syms)}
    C = np.full((len(syms), T), np.nan)
    for s in syms:
        C[si[s], [pos[d] for d in A[s].st.dates]] = A[s].st.c
    R = {n: np.full(C.shape, np.nan) for n in (21, 63, 126)}
    for n in R:
        R[n][:, n:] = 100 * (C[:, n:] / C[:, :-n] - 1)
    D = np.full(C.shape, np.nan)
    D[:, 1:] = C[:, 1:] / C[:, :-1] - 1
    D = D - np.nanmedian(D, axis=0)[None, :]                  # the market's move removed
    by_ind = collections.defaultdict(list)
    for s in syms:
        by_ind[ind[s]].append(s)
    bigs = [g for g, ms in by_ind.items() if len(ms) >= BIG]
    theme_rows = {t: [si[s] for s in ms] for t, ms in themes.items() if len(ms) >= 3}

    def med3(rows, k0, k1):
        return [np.nanmedian(R[n][rows, k0:k1], axis=0) for n in (21, 63, 126)]

    def rank_matrix(groups_by_block):
        """groups_by_block: [(k0, k1, {group name: [rows]})] -> ({group: P over days}, {(sym, k): [group names]})"""
        P = collections.defaultdict(lambda: np.full(T, np.nan))
        for k0, k1, gb in groups_by_block:
            names = [g for g, rows in gb.items() if len(rows) >= 3]
            if not names:
                continue
            meds = {g: med3(gb[g], k0, k1) for g in names}
            M = {n: np.array([meds[g][j] for g in names]).reshape(len(names), k1 - k0) for j, n in enumerate((21, 63, 126))}
            Pi = pct_cols(np.nanmean([pct_cols(M[n], 5) for n in M], axis=0), 5)
            for j, g in enumerate(names):
                P[g][k0:k1] = Pi[j]
        return P

    variants = {"current": None, "split 0.25": 0.25, "split 0.35": 0.35, "split 0.45": 0.45}
    out = {"big_industries": {g: len(by_ind[g]) for g in bigs}, "bands": {}, "groups_per_variant": {}, "clusters_last": {}}
    starts = list(range(130, T, EVERY))
    ev = launch.detect(A, groups, GS, cal, S)
    for vn, cut in variants.items():
        blocks, member_of = [], {}
        last_clusters = {}
        for b, k0 in enumerate(starts):
            k1 = min(T, k0 + EVERY)
            gb = {}
            for g, ms in by_ind.items():
                rows = [si[s] for s in ms]
                if cut is None or g not in bigs:
                    gb["ind:" + g] = rows
                    continue
                X = D[rows, k0 - LOOK:k0]
                ok = [j for j in range(len(rows)) if np.isfinite(X[j]).sum() >= LOOK - 5]
                lab = {}
                if len(ok) >= 2 * MIN_CL:
                    Xo = np.nan_to_num(X[ok])
                    cm = np.corrcoef(Xo)
                    cm = np.nan_to_num(cm)
                    np.fill_diagonal(cm, 1)
                    dist = squareform(np.clip(1 - cm, 0, 2), checks=False)
                    fc = fcluster(linkage(dist, "average"), t=1 - cut, criterion="distance")
                    cnt = collections.Counter(fc)
                    for jj, c_ in zip(ok, fc):
                        if cnt[c_] >= MIN_CL:
                            lab[jj] = c_
                for j, r_ in enumerate(rows):
                    key = f"ind:{g} #{lab[j]}" if j in lab else f"ind:{g} (other)"
                    gb.setdefault(key, []).append(r_)
                if k1 == T:
                    last_clusters[g] = {k: sorted(syms[x] for x in v) for k, v in gb.items() if k.startswith(f"ind:{g}")}
            for t, rows in theme_rows.items():
                gb["theme:" + t] = rows
            blocks.append((k0, k1, gb))
            for gname, rows in gb.items():
                for r_ in rows:
                    member_of.setdefault((syms[r_], b), []).append(gname)
        # ranks: themes among themes, industries / sub-groups among themselves
        P = {}
        for pref in ("theme:", "ind:"):
            P.update(rank_matrix([(k0, k1, {g: r for g, r in gb.items() if g.startswith(pref)}) for k0, k1, gb in blocks]))
        out["groups_per_variant"][vn] = int(np.mean([sum(1 for g in gb if g.startswith("ind:") and len(gb[g]) >= 3) for _, _, gb in blocks]))
        if cut is not None:
            out["clusters_last"][vn] = last_clusters

        def best(s, k):
            b = (k - 130) // EVERY
            ps = [P[g][k] for g in member_of.get((s, b), []) if g in P and not np.isnan(P[g][k])]
            return max(ps) if ps else None

        def band(p):
            return None if p is None else "1 Top 3%" if p >= 0.97 else "2 Strong 3-10%" if p >= 0.90 else "3 10-50%" if p >= 0.5 else "4 bottom half"
        res = {w: collections.defaultdict(list) for w in ("gaps", "gaps 10%+", "launches")}
        for s in syms:
            a = A[s]
            st = a.st
            n_ = len(st.dates)
            for i in range(max(a.start, 21), n_ - 21):
                if not (a.gap[i] >= 5 and a.liquid[i - 1]):
                    continue
                k = pos[st.dates[i]]
                if k < 131:
                    continue
                o = st.o[i]
                r = dict(day=100 * (st.c[i] / o - 1), r5=100 * (st.c[i + 5] / o - 1), r20=100 * (st.c[i + 20] / o - 1), mx=100 * (st.h[i:i + 21].max() / o - 1))
                bd = band(best(s, k - 1))
                if bd:
                    res["gaps"][bd].append(r)
                    if a.gap[i] >= 10:
                        res["gaps 10%+"][bd].append(r)
        for s, i, k, gs, gn in ev:
            if s not in si:
                continue
            st = A[s].st
            if i + 20 >= len(st.dates) or k < 131:
                continue
            c0 = st.c[i]
            bd = band(best(s, k))
            if bd:
                res["launches"][bd].append(dict(day=0.0, r5=100 * (st.c[i + 5] / c0 - 1), r20=100 * (st.c[i + 20] / c0 - 1), mx=100 * (st.h[i + 1:i + 21].max() / c0 - 1)))
        out["bands"][vn] = {w: {k: summ(v) for k, v in sorted(d.items())} for w, d in res.items()}
        print(vn, json.dumps({w: {k: (v["n"], v.get("ran20_pct")) for k, v in d.items()} for w, d in out["bands"][vn].items()}))
    json.dump(out, open(a_.out, "w"), indent=1)


if __name__ == "__main__":
    main()
