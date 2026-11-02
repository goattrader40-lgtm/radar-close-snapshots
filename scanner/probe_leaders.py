#!/usr/bin/env python3
"""Is the LEADER inside a group worth more? (the user, Nov 2 2026: AMD ran best among the CPU/GPU names though NVDA is
the big one; SNDK led MU in memory; DELL led AI servers.) Tested on 2 years of gap-ups and launches.

  python3 scanner/probe_leaders.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json

Groups as in probe_grouprank.py: every theme and every industry with 3+ stocks; the group's rank (qull: its median 1-,
3- and 6-month returns, each ranked among the groups of its kind, averaged, ranked again).
A stock's place INSIDE a group: its own 1-, 3- and 6-month returns, each ranked among the group's stocks, averaged and
ranked again: #1 = the group's leader. Also its rank against the whole market (the same score among all stocks).
Each gap-up (5%+, liquid; ranks at the close before) and launch (ranks on the launch day) is put in buckets:
  - by its place in its best-ranked group: #1, #2-3, rest of the top third, the rest (groups of 5+ stocks)
  - the same, only when that group is Top or Strong (top 10%)
  - by its rank against the whole market: top 3%, 3-10%, 10-20%, the rest
Plus the examples: month by month (2025-2026), the top 3 stocks inside the groups of AMD, NVDA, SNDK, MU and DELL, and
where those five stood, with each one's return over the next month.
"""
import argparse, collections, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402
from probe_gapgroups import summ  # noqa: E402

EXAMPLES = ("AMD", "NVDA", "SNDK", "MU", "DELL")


def pct_cols(X, need=3):
    """percentile rank 0-1 of each row within each column (NaN stays NaN; a column with fewer than `need` values: NaN)"""
    ok = ~np.isnan(X)
    k = ok.sum(axis=0)
    Xf = np.where(ok, X, -np.inf)
    order = Xf.argsort(axis=0, kind="stable").argsort(axis=0, kind="stable") - (X.shape[0] - k)[None, :]
    with np.errstate(all="ignore"):
        P = order / np.maximum(k - 1, 1)[None, :]
    P = np.where(ok & (k >= need)[None, :], P, np.nan)
    return P


def place_cols(X):
    """1 = the highest value in each column (NaN rows: NaN)"""
    ok = ~np.isnan(X)
    Xf = np.where(ok, -X, np.inf)
    pl = Xf.argsort(axis=0, kind="stable").argsort(axis=0, kind="stable") + 1.0
    return np.where(ok, pl, np.nan)


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
    mem = collections.defaultdict(list)
    sg = collections.defaultdict(list)
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
    syms = sorted({s for g in names for s in mem[g]})
    si = {s: j for j, s in enumerate(syms)}
    # each stock's 1-, 3-, 6-month returns on the market calendar
    R = {n: np.full((len(syms), T), np.nan) for n in (21, 63, 126)}
    C = np.full((len(syms), T), np.nan)
    for s in syms:
        st = A[s].st
        idx = [pos[d] for d in st.dates]
        C[si[s], idx] = st.c
        for n in R:
            r = np.full(st.c.size, np.nan)
            r[n:] = 100 * (st.c[n:] / st.c[:-n] - 1)
            R[n][si[s], idx] = r
    # the market rank of each stock (the same score among all stocks)
    MK = pct_cols(np.nanmean([pct_cols(R[n], 5) for n in R], axis=0), 5)
    # group ranks (as the live rank) and each stock's place inside each group
    G = len(names)
    med = {n: np.full((G, T), np.nan) for n in R}
    place, size = {}, {}
    for g in names:
        rows = [si[s] for s in mem[g]]
        for n in R:
            med[n][gi[g]] = np.nanmedian(R[n][rows], axis=0)
        sc = np.nanmean([pct_cols(R[n][rows], 3) for n in R], axis=0)
        pl = place_cols(sc)
        cnt = (~np.isnan(sc)).sum(axis=0)
        for j, s in enumerate(mem[g]):
            place[(s, g)] = pl[j]
        size[g] = cnt
    P = np.full((G, T), np.nan)
    for pref in ("theme:", "ind:"):
        rows = [gi[g] for g in names if g.startswith(pref)]
        P[rows] = pct_cols(np.nanmean([pct_cols(med[n][rows], 5) for n in R], axis=0), 5)

    def best(s, k):
        c = [(P[gi[g], k], g) for g in sg.get(s, []) if g in gi and not np.isnan(P[gi[g], k])]
        return max(c) if c else (None, None)

    def inside(s, g, k):
        pl, n = place[(s, g)][k], size[g][k]
        if np.isnan(pl) or n < 5:                 # a leader of 3 or 4 stocks says little
            return None
        return "1 leader (#1)" if pl == 1 else "2 #2-3" if pl <= 3 else "3 rest of top third" if pl <= max(3, n / 3) else "4 the rest"

    def mband(p):
        return None if np.isnan(p) else "1 top 3%" if p >= 0.97 else "2 3-10%" if p >= 0.90 else "3 10-20%" if p >= 0.80 else "4 the rest"

    res = {w: collections.defaultdict(list) for w in ("gaps", "launches")}

    def add(where, s, k, r):
        p, g = best(s, k)
        if g is None:
            return
        tier = "Top" if p >= 0.97 else "Strong" if p >= 0.90 else "other"
        ins = inside(s, g, k)
        if ins:
            res[where]["in best group · " + ins].append(r)
            res[where][("in a Top/Strong group · " if tier != "other" else "in other groups · ") + ins].append(r)
            if tier == "Top":
                res[where]["in a Top group · " + ins].append(r)
        # its place in ANY of its groups: #1 in at least one
        any1 = any(place[(s, x)][k] == 1 and size[x][k] >= 5 for x in sg[s] if x in gi)
        res[where]["#1 in any of its groups (5+ stocks)" if any1 else "not #1 in any group"].append(r)
        mb = mband(MK[si[s], k])
        if mb:
            res[where]["market rank · " + mb].append(r)
            res[where][("Top/Strong group · " if tier != "other" else "other groups · ") + "market rank " + mb].append(r)

    for s in syms:
        a = A[s]
        st = a.st
        n = len(st.dates)
        for i in range(max(a.start, 21), n - 21):
            if not (a.gap[i] >= 5 and a.liquid[i - 1]):
                continue
            k = pos[st.dates[i]]
            if k < 130:
                continue
            o = st.o[i]
            add("gaps", s, k - 1, dict(day=100 * (st.c[i] / o - 1), r5=100 * (st.c[i + 5] / o - 1), r20=100 * (st.c[i + 20] / o - 1),
                                       mx=100 * (st.h[i:i + 21].max() / o - 1)))
    for s, i, k, gs, gn in launch.detect(A, groups, GS, cal, S):
        if s not in si:
            continue
        st = A[s].st
        if i + 20 >= len(st.dates) or k < 130:
            continue
        c0 = st.c[i]
        add("launches", s, k, dict(day=0.0, r5=100 * (st.c[i + 5] / c0 - 1), r20=100 * (st.c[i + 20] / c0 - 1),
                                   mx=100 * (st.h[i + 1:i + 21].max() / c0 - 1)))
    out = {"stocks": len(syms), "groups": len(names),
           "results": {w: {k: summ(v) for k, v in sorted(d.items())} for w, d in res.items()}}
    # examples: month-ends from the first with 6 months of data
    ex = {}
    ends = [k for k in range(130, T) if k == T - 1 or cal[k][:7] != cal[k + 1][:7]]
    for s in EXAMPLES:
        if s not in si:
            continue
        for g in sg[s]:
            if g not in gi or g in ex:
                continue
            rowsg = mem[g]
            lines = []
            for k in ends:
                k21 = min(k + 21, T - 1)
                fwd = {x: (None if np.isnan(C[si[x], k]) or np.isnan(C[si[x], k21]) or k21 == k else round(float(100 * (C[si[x], k21] / C[si[x], k] - 1)), 1))
                       for x in rowsg}
                ranked = sorted((x for x in rowsg if not np.isnan(place[(x, g)][k])), key=lambda x: place[(x, g)][k])
                lines.append(dict(month_end=cal[k], group_rank_pct=None if np.isnan(P[gi[g], k]) else round(100 * float(P[gi[g], k]), 1),
                                  top3=[[x, round(float(R[21][si[x], k]), 1), round(float(R[63][si[x], k]), 1) if not np.isnan(R[63][si[x], k]) else None,
                                         round(float(R[126][si[x], k]), 1) if not np.isnan(R[126][si[x], k]) else None, fwd[x]] for x in ranked[:3]],
                                  examples={x: [int(place[(x, g)][k]) if not np.isnan(place[(x, g)][k]) else None, int(size[g][k]), fwd[x]]
                                            for x in EXAMPLES if x in rowsg},
                                  group_median_next_month=None if not [v for v in fwd.values() if v is not None] else round(float(np.median([v for v in fwd.values() if v is not None])), 1)))
            ex[g] = dict(members=len(rowsg), months=lines,
                         note="top3 = [stock, 1M %, 3M %, 6M %, next month %]; examples = {stock: [place in group, of, next month %]}")
    out["examples"] = ex
    json.dump(out, open(a_.out, "w"), indent=1)
    print(json.dumps(out["results"])[:3000])


if __name__ == "__main__":
    main()
