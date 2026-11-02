#!/usr/bin/env python3
"""Does a gap-up hold or fade depending on its theme / industry group's trend? (the user, Nov 2 2026)

  python3 scanner/probe_gapgroups.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json

1. Every gap-up of 5%+ in 2 years of daily bars, in liquid stocks (the launch list's minimums), split by its group at
   the close BEFORE the gap: the best of its themes (or its industry) and its area, as the Launches use them:
   Leading / Turning up / Not trending, and the group's median 1-week and 1-month change. Per bucket: how many, how
   many faded (closed under the open), held (closed over the open), the gap day bought at the open, and the 5- and
   20-session result from the open, and how many ran 20%+ (highest high in 20 sessions vs the open).
2. The launches (detect()) split the same way by their group on the launch day, and whether it confirmed (turned
   Turning up / Leading within 10 sessions after): ran 20%+ in 20 sessions from the launch close, 20-session result.
No news or earnings dates this far back: every gap counts, good news and bad; today's theme lists are applied to the past.
"""
import argparse, collections, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402

L = launch.L


def group_perf(A, groups, cal):
    """{group: (median 1-week %, median 1-month %) arrays over cal}"""
    pos = {d: k for k, d in enumerate(cal)}
    members = collections.defaultdict(list)
    for s, (gs, ars) in groups.items():
        if s in A:
            for g in gs + ["area:" + x for x in ars]:
                members[g].append(s)
    out = {}
    T = len(cal)
    for g, ms in members.items():
        if len(ms) < 3:
            continue
        r5, r21 = np.full((len(ms), T), np.nan), np.full((len(ms), T), np.nan)
        for j, s in enumerate(ms):
            a = A[s]
            idx = [pos[d] for d in a.st.dates if d in pos]
            if len(idx) != len(a.st.dates):
                continue
            r5[j, idx], r21[j, idx] = a.ret5, a.ret21
        with np.errstate(all="ignore"):
            import warnings
            warnings.simplefilter("ignore", RuntimeWarning)
            out[g] = (np.nanmedian(r5, axis=0), np.nanmedian(r21, axis=0))
    return out


def best(sym, k, groups, GS, GP):
    """(status, name, 1-week, 1-month) of its best-trending group at calendar day k (its themes, then its area)"""
    gs, ars = groups.get(sym, ([], []))
    b = (-1, "", None, None)
    for g in gs + ["area:" + x for x in ars]:
        if g in GS and g in GP:
            s = int(GS[g][1][k])
            if s > b[0]:
                b = (s, g, float(GP[g][0][k]), float(GP[g][1][k]))
    return b


def summ(rs):
    if not rs:
        return dict(n=0)
    f = lambda k: [r[k] for r in rs if r[k] is not None and not np.isnan(r[k])]
    avg = lambda x: round(float(np.mean(x)), 2) if x else None
    return dict(n=len(rs), faded_pct=round(100 * sum(r["day"] < 0 for r in rs) / len(rs), 1),
                held_pct=round(100 * sum(r["day"] > 0 for r in rs) / len(rs), 1),
                avg_day_from_open=avg(f("day")), avg_5d_from_open=avg(f("r5")), avg_20d_from_open=avg(f("r20")),
                ran20_pct=round(100 * sum((r["mx"] or 0) >= 20 for r in rs) / len(rs), 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    GP = group_perf(A, groups, cal)
    pos = {d: k for k, d in enumerate(cal)}
    ST = {2: "Leading", 1: "Turning up", 0: "Not trending", -1: "No group"}
    gaps = []
    for s, a in A.items():
        st = a.st
        n = len(st.dates)
        for i in range(max(a.start, 21), n - 1):
            if not (a.gap[i] >= 5 and a.liquid[i - 1]):
                continue
            k = pos.get(st.dates[i])
            if k is None or k < 1:
                continue
            gs, gn, w1, m1 = best(s, k - 1, groups, GS, GP)
            o = st.o[i]
            j5, j20 = min(i + 5, n - 1), min(i + 20, n - 1)
            gaps.append(dict(sym=s, date=st.dates[i], gap=round(float(a.gap[i]), 1), status=ST[gs], w1=w1, m1=m1,
                             day=100 * (st.c[i] / o - 1), r5=100 * (st.c[j5] / o - 1) if i + 5 < n else None,
                             r20=100 * (st.c[j20] / o - 1) if i + 20 < n else None,
                             mx=100 * (st.h[i:j20 + 1].max() / o - 1)))
    out = {"gaps_total": len(gaps), "note": "gap-ups 5%+, liquid stocks, 2 years; group at the close before the gap"}
    by = collections.defaultdict(list)
    for r in gaps:
        by["status: " + r["status"]].append(r)
        if r["w1"] is not None and not np.isnan(r["w1"]):
            by["group 1-week: " + ("up 2%+" if r["w1"] >= 2 else "0 to +2%" if r["w1"] >= 0 else "down")].append(r)
        if r["m1"] is not None and not np.isnan(r["m1"]):
            by["group 1-month: " + ("up 8%+" if r["m1"] >= 8 else "0 to +8%" if r["m1"] >= 0 else "down")].append(r)
            if r["w1"] is not None and not np.isnan(r["w1"]):
                both = "both up" if r["w1"] > 0 and r["m1"] > 0 else "both down" if r["w1"] <= 0 and r["m1"] <= 0 else "mixed"
                by["group 1-week & 1-month: " + both].append(r)
        by["gap size " + ("10%+" if r["gap"] >= 10 else "5-10%") + " · " + r["status"]].append(r)
    out["gaps"] = {k: summ(v) for k, v in sorted(by.items())}
    # 2. launches by their group
    ev = launch.detect(A, groups, GS, cal, S)
    lr = collections.defaultdict(list)
    for s, i, k, gs, gn in ev:
        a = A[s]
        st = a.st
        n = len(st.dates)
        if i + 20 >= n:
            continue
        c0 = st.c[i]
        conf = any(launch.best_group(s, kk, groups, GS)[0] >= 1 for kk in range(k, min(k + 11, len(cal))))
        g = launch.grade(a, i)
        r = dict(day=0.0, r5=100 * (st.c[i + 5] / c0 - 1), r20=100 * (st.c[i + 20] / c0 - 1), mx=100 * (st.h[i + 1:i + 21].max() / c0 - 1))
        lr["launch day status: " + ST[gs]].append(r)
        lr["confirmed within 10 sessions: " + ("yes" if conf else "no")].append(r)
        lr["grade " + g + " · confirmed " + ("yes" if conf else "no")].append(r)
    out["launches"] = {k: {kk: vv for kk, vv in summ(v).items() if kk not in ("faded_pct", "held_pct", "avg_day_from_open")}
                       for k, v in sorted(lr.items())}
    json.dump(out, open(a_.out, "w"), indent=1)
    print(json.dumps(out)[:3000])


if __name__ == "__main__":
    main()
