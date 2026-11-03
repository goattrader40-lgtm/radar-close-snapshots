#!/usr/bin/env python3
"""The fair test of the pruned business-line groups (the user's go, Nov 3 2026): every 21 sessions the groups are
pruned the portal's way using ONLY the 120 sessions before that day (no look-ahead), then ranked as live.

  python3 scanner/probe_rolling.py --bars BARS.json.gz --stocks stocks.json --profiles profiles.json --out OUT.json

Versions (themes unchanged in all):
  current   today's 73 broad industries
  pruned    scanner/subgroups.py groups, pruned each month (score vs the rest of the group 0.6+, as radar/pipeline.py);
            a stock that drops out has no industry group that month (it can still have a theme)
  pruned + loose ranked, no tier   the same, but the dropped stocks keep their broad industry with a rank and no tier
Gap-ups (5%+, liquid, rank at the close before) and launches (rank on the launch day), by band; also year 2 only.
"""
import argparse, collections, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402
import subgroups  # noqa: E402
from probe_gapgroups import summ  # noqa: E402
from probe_leaders import pct_cols  # noqa: E402

FLOOR, WIN, EVERY, START = 0.6, 120, 21, 131


def corr(a, b):
    a = a - a.mean(); b = b - b.mean(); dd = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / dd) if dd else 0.0


def zscores(Rw):
    """radar/pipeline.py: market (beta-adjusted) removed, clipped at 3 SD, z-scored; Rw = days x stocks (NaN ok)"""
    mkt = np.nanmean(Rw, axis=1); mc = mkt - mkt.mean()
    out = np.zeros(Rw.shape)
    for j in range(Rw.shape[1]):
        y = Rw[:, j]; f = np.isfinite(y)
        if f.sum() < 0.9 * len(y):
            out[:, j] = np.nan
            continue
        b = np.dot(y[f] - y[f].mean(), mc[f]) / max(1e-9, (mc[f] ** 2).sum())
        e = y - b * mkt; sd = np.nanstd(e) or 1.0; e = np.clip(e, -3 * sd, 3 * sd)
        out[:, j] = np.nan_to_num((e - np.nanmean(e)) / (np.nanstd(e) or 1.0))
    return out


def prune(names, Z, col):
    cur = [x for x in names if x in col]
    while len(cur) >= 3:
        Zm = Z[:, [col[x] for x in cur]]; tot = Zm.sum(1)
        sc = {x: corr(Zm[:, i], (tot - Zm[:, i]) / (len(cur) - 1)) for i, x in enumerate(cur)}
        w = min(sc, key=sc.get)
        if sc[w] >= FLOOR:
            return cur
        cur.remove(w)
    return []


def main():
    ap = argparse.ArgumentParser()
    for k in ("bars", "stocks", "profiles", "out"):
        ap.add_argument("--" + k, required=True)
    a_ = ap.parse_args()
    import warnings
    warnings.simplefilter("ignore", RuntimeWarning)
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    rows_by = {r["symbol"]: r for r in json.load(open(a_.stocks))}
    prof = json.load(open(a_.profiles))["rows"]
    pos = {d: k for k, d in enumerate(cal)}
    T = len(cal)
    syms = sorted(s for s in rows_by if s in A and all(d in pos for d in A[s].st.dates))
    si = {s: j for j, s in enumerate(syms)}
    C = np.full((len(syms), T), np.nan)
    for s in syms:
        C[si[s], [pos[d] for d in A[s].st.dates]] = A[s].st.c
    R = {n: np.full(C.shape, np.nan) for n in (21, 63, 126)}
    for n in R:
        R[n][:, n:] = 100 * (C[:, n:] / C[:, :-n] - 1)
    D = np.full(C.shape, np.nan)
    D[:, 1:] = np.clip(100 * (C[:, 1:] / C[:, :-1] - 1), -25, 25)
    themes = collections.defaultdict(list)
    for s in syms:
        for t in [x for x in (rows_by[s].get("themes") or "").split(" | ") if x]:
            themes[t].append(s)
    broad = {s: rows_by[s].get("industry") or "Other" for s in syms}
    named = {s: subgroups.group_of(s, prof.get(s) or {}, rows_by[s]) for s in syms}
    named = {s: g for s, g in named.items() if g not in subgroups.EXCLUDE}
    nmem = collections.defaultdict(list)
    for s, g in named.items():
        nmem[g].append(s)
    bmem = collections.defaultdict(list)
    for s, g in broad.items():
        bmem[g].append(s)
    starts = list(range(START, T, EVERY))
    # each month: the pruned members of every named group
    blocks = []
    stats = []
    for k0 in starts:
        k1 = min(T, k0 + EVERY)
        Z = zscores(D[:, k0 - WIN:k0].T)
        okc = ~np.isnan(Z).any(axis=0)
        col = {s: j for s, j in si.items() if okc[j]}
        kept = {g: prune(ms, Z, col) for g, ms in nmem.items() if len(ms) >= 3}
        kept = {g: v for g, v in kept.items() if len(v) >= 3}
        blocks.append((k0, k1, kept))
        stats.append((cal[k0], len(kept), sum(len(v) for v in kept.values())))

    def rank_P(mem_by_block):
        """[(k0, k1, {group: [syms]})] -> {group: P over days} (rank among the groups present in each block)"""
        P = collections.defaultdict(lambda: np.full(T, np.nan))
        for k0, k1, gm in mem_by_block:
            names = [g for g, ms in gm.items() if len(ms) >= 3]
            if len(names) < 5:
                continue
            M = {n: np.array([np.nanmedian(R[n][[si[s] for s in gm[g]], k0:k1], axis=0) for g in names]).reshape(len(names), k1 - k0) for n in R}
            Pi = pct_cols(np.nanmean([pct_cols(M[n], 5) for n in M], axis=0), 5)
            for j, g in enumerate(names):
                P[g][k0:k1] = Pi[j]
        return P
    tn = [t for t, v in themes.items() if len(v) >= 3]
    PT = rank_P([(k0, k1, {t: themes[t] for t in tn}) for k0, k1, _ in blocks])
    sym_t = collections.defaultdict(list)
    for t in tn:
        for s in themes[t]:
            sym_t[s].append(t)
    vers = {}
    vers["current"] = (rank_P([(k0, k1, dict(bmem)) for k0, k1, _ in blocks]), lambda s, b: broad.get(s), set())
    Pn = rank_P([(k0, k1, kept) for k0, k1, kept in blocks])
    kept_of = [{s: g for g, ms in kept.items() for s in ms} for _, _, kept in blocks]
    vers["pruned"] = (Pn, lambda s, b: kept_of[b].get(s), set())
    # pruned + the dropped keep their broad industry, ranked among everything, no tier
    mix = []
    for (k0, k1, kept), ko in zip(blocks, kept_of):
        gm = {("N:" + g): ms for g, ms in kept.items()}
        for s in syms:
            if s not in ko:
                gm.setdefault("B:" + broad[s], []).append(s)
        mix.append((k0, k1, gm))
    Pm = rank_P(mix)
    vers["pruned + loose ranked, no tier"] = (Pm, lambda s, b: ("N:" + kept_of[b][s]) if s in kept_of[b] else "B:" + broad[s], {"B:"})
    out = {"blocks": stats, "bands": {}}
    ev = launch.detect(A, groups, GS, cal, S)
    for vn, (P, gof, notier) in vers.items():
        def best(s, k):
            b = (k - START) // EVERY
            if b < 0:
                return None
            c = [PT[t][k] for t in sym_t.get(s, []) if t in PT and not np.isnan(PT[t][k])]
            g = gof(s, b)
            if g and g in P and not np.isnan(P[g][k]):
                p = P[g][k]
                c.append(min(p, 0.89) if any(g.startswith(x) for x in notier) else p)
            return max(c) if c else None

        def band(p):
            return None if p is None else "1 Top 3%" if p >= 0.97 else "2 Strong 3-10%" if p >= 0.90 else "3 10-50%" if p >= 0.5 else "4 bottom half"
        res = {w: collections.defaultdict(list) for w in ("gaps", "gaps 10%+", "launches", "gaps · 2nd year", "launches · 2nd year")}
        for s in syms:
            a = A[s]; st = a.st; n_ = len(st.dates)
            for i in range(max(a.start, 21), n_ - 21):
                if not (a.gap[i] >= 5 and a.liquid[i - 1]):
                    continue
                k = pos[st.dates[i]]
                if k < START + 1:
                    continue
                o = st.o[i]
                r = dict(day=100 * (st.c[i] / o - 1), r5=100 * (st.c[i + 5] / o - 1), r20=100 * (st.c[i + 20] / o - 1), mx=100 * (st.h[i:i + 21].max() / o - 1))
                bd = band(best(s, k - 1))
                if bd:
                    res["gaps"][bd].append(r)
                    if a.gap[i] >= 10:
                        res["gaps 10%+"][bd].append(r)
                    if k >= 251:
                        res["gaps · 2nd year"][bd].append(r)
        for s, i, k, gs, gn in ev:
            if s not in si:
                continue
            st = A[s].st
            if i + 20 >= len(st.dates) or k < START + 1:
                continue
            c0 = st.c[i]
            bd = band(best(s, k))
            if bd:
                rr = dict(day=0.0, r5=100 * (st.c[i + 5] / c0 - 1), r20=100 * (st.c[i + 20] / c0 - 1), mx=100 * (st.h[i + 1:i + 21].max() / c0 - 1))
                res["launches"][bd].append(rr)
                if k >= 251:
                    res["launches · 2nd year"][bd].append(rr)
        out["bands"][vn] = {w: {k: summ(v) for k, v in sorted(d.items())} for w, d in res.items()}
        print(vn, json.dumps({w: {k: (v["n"], v.get("ran20_pct")) for k, v in d.items()} for w, d in out["bands"][vn].items()}))
    json.dump(out, open(a_.out, "w"), indent=1)


if __name__ == "__main__":
    main()
