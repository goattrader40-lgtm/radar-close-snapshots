#!/usr/bin/env python3
"""Named groups by business line vs today's broad industries (the user, Nov 3 2026).

  python3 scanner/probe_named.py --bars BARS.json.gz --stocks stocks.json --profiles profiles.json --out OUT.json

Industry-level groups compared (themes unchanged in all of them):
  current  the 73 broad industries (FinanceDatabase)
  yahoo    Yahoo's 143 industries
  named    scanner/subgroups.py: hand-made business-line groups for the big buckets + Yahoo's industry for the rest
1) Do they move together? Each stock's daily move minus the market's median move, the last 250 sessions; for each
   group (3+ stocks) the average correlation between its members, and each member's average correlation with the rest
   (its fit). Stock-weighted average fit per version; per named group: size, fit, the 3 weakest members.
2) The rank (same as live: median 1/3/6-month return, ranked among the groups, averaged, ranked again; Top = top 3%,
   Strong = 3-10%) on 2 years of gap-ups and launches, by band.
"""
import argparse, collections, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402
import subgroups  # noqa: E402
from probe_gapgroups import summ  # noqa: E402
from probe_leaders import pct_cols  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--profiles", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    import warnings
    warnings.simplefilter("ignore", RuntimeWarning)
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    stocks = json.load(open(a_.stocks))
    prof = json.load(open(a_.profiles))["rows"]
    pos = {d: k for k, d in enumerate(cal)}
    T = len(cal)
    rows_by = {r["symbol"]: r for r in stocks}
    syms = sorted(s for s in rows_by if s in A and all(d in pos for d in A[s].st.dates))
    si = {s: j for j, s in enumerate(syms)}
    C = np.full((len(syms), T), np.nan)
    for s in syms:
        C[si[s], [pos[d] for d in A[s].st.dates]] = A[s].st.c
    R = {n: np.full(C.shape, np.nan) for n in (21, 63, 126)}
    for n in R:
        R[n][:, n:] = 100 * (C[:, n:] / C[:, :-n] - 1)
    D = np.full(C.shape, np.nan)
    D[:, 1:] = C[:, 1:] / C[:, :-1] - 1
    D = D - np.nanmedian(D, axis=0)[None, :]
    themes = collections.defaultdict(list)
    for s in syms:
        for t in [x for x in (rows_by[s].get("themes") or "").split(" | ") if x]:
            themes["theme:" + t].append(si[s])
    versions = {
        "current": {s: rows_by[s].get("industry") or "Other" for s in syms},
        "yahoo": {s: (prof.get(s) or {}).get("industry") or rows_by[s].get("industry") or "Other" for s in syms},
        "named": {s: subgroups.group_of(s, prof.get(s) or {}, rows_by[s]) for s in syms},
    }
    out = {"stocks": len(syms), "versions": {}, "named_groups": {}}
    X = D[:, T - 250:]
    for vn, gmap in versions.items():
        mem = collections.defaultdict(list)
        for s, g in gmap.items():
            mem[g].append(si[s])
        fits, per = [], {}
        for g, rows in mem.items():
            if len(rows) < 3:
                continue
            Xg = X[rows]
            ok = np.isfinite(Xg).sum(axis=1) >= 200
            rows_ok = [r for r, o in zip(rows, ok) if o]
            if len(rows_ok) < 3:
                continue
            cm = np.corrcoef(np.nan_to_num(X[rows_ok]))
            np.fill_diagonal(cm, np.nan)
            f = np.nanmean(cm, axis=1)
            fits += list(f)
            per[g] = (len(rows), float(np.nanmean(f)), sorted(zip(f, [syms[r] for r in rows_ok]))[:3])
        n_groups = sum(1 for g, r in mem.items() if len(r) >= 3)
        # the rank over time, industries / groups among themselves, themes among themselves
        names = [g for g, r in mem.items() if len(r) >= 3]
        M = {n: np.array([np.nanmedian(R[n][mem[g]], axis=0) for g in names]) for n in R}
        P = pct_cols(np.nanmean([pct_cols(M[n], 5) for n in M], axis=0), 5)
        tn = list(themes)
        MT = {n: np.array([np.nanmedian(R[n][themes[t]], axis=0) for t in tn]) for n in R}
        PT = pct_cols(np.nanmean([pct_cols(MT[n], 5) for n in MT], axis=0), 5)
        gi, ti = {g: j for j, g in enumerate(names)}, {t: j for j, t in enumerate(tn)}
        sym_themes = collections.defaultdict(list)
        for t, rows in themes.items():
            for r in rows:
                sym_themes[syms[r]].append(t)

        def best(s, k):
            c = [PT[ti[t], k] for t in sym_themes.get(s, []) if not np.isnan(PT[ti[t], k])]
            g = gmap.get(s)
            if g in gi and not np.isnan(P[gi[g], k]):
                c.append(P[gi[g], k])
            return max(c) if c else None

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
        for s, i, k, gs, gn in launch.detect(A, groups, GS, cal, S):
            if s not in si:
                continue
            st = A[s].st
            if i + 20 >= len(st.dates) or k < 131:
                continue
            c0 = st.c[i]
            bd = band(best(s, k))
            if bd:
                res["launches"][bd].append(dict(day=0.0, r5=100 * (st.c[i + 5] / c0 - 1), r20=100 * (st.c[i + 20] / c0 - 1), mx=100 * (st.h[i + 1:i + 21].max() / c0 - 1)))
        top_now = sorted(((float(P[gi[g], -1]), g) for g in names if not np.isnan(P[gi[g], -1])), reverse=True)[:15]
        out["versions"][vn] = {"groups_3plus": n_groups, "avg_fit": round(float(np.nanmean(fits)), 3), "median_fit": round(float(np.nanmedian(fits)), 3),
                               "bands": {w: {k: summ(v) for k, v in sorted(d.items())} for w, d in res.items()},
                               "top_groups_today": [[g, round(100 * p, 1)] for p, g in top_now]}
        if vn == "named":
            out["named_groups"] = {g: {"n": v[0], "fit": round(v[1], 3), "weakest": [[s_, round(float(f_), 3)] for f_, s_ in v[2]]} for g, v in sorted(per.items(), key=lambda x: -x[1][1])}
        if vn == "current":
            out["current_groups"] = {g: {"n": v[0], "fit": round(v[1], 3)} for g, v in sorted(per.items(), key=lambda x: -x[1][1])}
        print(vn, out["versions"][vn]["avg_fit"], n_groups, json.dumps({w: {k: (v["n"], v.get("ran20_pct")) for k, v in d.items()} for w, d in out["versions"][vn]["bands"].items()}))
    json.dump(out, open(a_.out, "w"), indent=1)


if __name__ == "__main__":
    main()
