#!/usr/bin/env python3
"""The proposed industry groups put through the portal's own co-movement test (the user, Nov 3 2026: "analyze your
spreadsheet the way the portal shows Cybersecurity").

  python3 scanner/probe_prune.py --bars BARS.json.gz --stocks stocks.json --themes themes.json --profiles profiles.json --out OUT.json

Same as radar/pipeline.py: the last 120 sessions, each stock's daily move with the market's move (beta-adjusted)
removed, z-scored and clipped at 3 SD; a member's score = its correlation with the average of the OTHER members (the
number under each ticker on the portal); Strength = the average correlation between every pair (the portal's theme
Strength). Each group is pruned like the portal's auto groups: the weakest member out until everyone scores 0.6+.
A stock that drops out is offered to the group (or theme) it tracks best, if that score is 0.6+.
"""
import argparse, collections, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402
import subgroups  # noqa: E402

FLOOR, WIN = 0.6, 120


def corr(a, b):
    a = a - a.mean(); b = b - b.mean(); dd = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / dd) if dd else 0.0


def main():
    ap = argparse.ArgumentParser()
    for k in ("bars", "stocks", "themes", "profiles", "out"):
        ap.add_argument("--" + k, required=True)
    a_ = ap.parse_args()
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    stocks = {r["symbol"]: r for r in json.load(open(a_.stocks))}
    prof = json.load(open(a_.profiles))["rows"]
    themes = json.load(open(a_.themes))
    win = cal[-WIN:]
    pos = {d: k for k, d in enumerate(win)}
    univ = [s for s in stocks if s in A]
    R = np.full((WIN, len(univ)), np.nan)
    for j, s in enumerate(univ):
        st = A[s].st
        for i in range(1, len(st.dates)):
            k = pos.get(st.dates[i])
            if k is not None:
                R[k, j] = 100 * (st.c[i] / st.c[i - 1] - 1)
    keep = np.isfinite(R).mean(0) >= 0.9
    univ = [s for s, k in zip(univ, keep) if k]
    R = np.clip(R[:, keep], -25, 25)
    mkt = np.nanmean(R, axis=1); mc = mkt - mkt.mean()
    cols = []
    for j in range(R.shape[1]):
        y = R[:, j]; f = np.isfinite(y)
        b = np.dot(y[f] - y[f].mean(), mc[f]) / max(1e-9, (mc[f] ** 2).sum())
        e = y - b * mkt; sd = np.nanstd(e) or 1.0; e = np.clip(e, -3 * sd, 3 * sd)
        cols.append(np.nan_to_num((e - np.nanmean(e)) / (np.nanstd(e) or 1.0)))
    Z = np.array(cols).T
    col = {s: j for j, s in enumerate(univ)}

    def loo(names):
        Zm = Z[:, [col[x] for x in names]]; tot = Zm.sum(1)
        return {x: corr(Zm[:, i], (tot - Zm[:, i]) / (len(names) - 1)) for i, x in enumerate(names)}

    def avg_pair(names):
        if len(names) < 2:
            return None
        C = np.corrcoef(Z[:, [col[x] for x in names]].T); n = len(names)
        return round(float((C.sum() - n) / (n * (n - 1))), 3)

    gmap = {s: subgroups.group_of(s, prof.get(s) or {}, stocks[s]) for s in univ}
    gmap = {s: g for s, g in gmap.items() if g not in subgroups.EXCLUDE}
    mem = collections.defaultdict(list)
    for s, g in gmap.items():
        mem[g].append(s)
    out = {"window": [win[0], win[-1]], "floor": FLOOR, "groups": {}, "themes": {}}
    kept_all, dropped = {}, {}
    for g, names in mem.items():
        if len(names) < 3:
            out["groups"][g] = {"n": len(names), "too_small": True, "members": names}
            continue
        before = avg_pair(names)
        cur = list(names)
        while len(cur) >= 3:
            sc = loo(cur)
            w = min(sc, key=sc.get)
            if sc[w] >= FLOOR:
                break
            cur.remove(w)
            dropped[w] = (g, round(sc[w], 2))
        if len(cur) < 3:                             # nothing tight left in it
            for x in cur:
                dropped[x] = (g, None)
            cur = []
        sc = loo(cur) if len(cur) >= 3 else {}
        for x in cur:
            kept_all[x] = g
        out["groups"][g] = {"n": len(names), "kept": len(cur), "strength_before": before, "strength_after": avg_pair(cur),
                            "members": sorted(((round(v, 2), x) for x, v in sc.items()), reverse=True),
                            "dropped": sorted(x for x in names if x not in cur), "hand_made": g in subgroups.G}
    # where do the dropped ones fit best? (any kept group or theme, 0.6+)
    tsets = {t["theme"]: [x for x in (t["members"] + " " + t.get("ext", "")).split() if x in col] for t in themes}
    targets = {("group", g): [x for x in v["members"]] for g, v in out["groups"].items() if v.get("kept", 0) >= 3}
    targets = {k: [x for _, x in v] for k, v in targets.items()}
    targets.update({("theme", t): v for t, v in tsets.items() if len(v) >= 3})
    tsum = {k: Z[:, [col[x] for x in v]].sum(1) for k, v in targets.items()}
    moves = {}
    for x, (g0, s0) in dropped.items():
        best = None
        for k, v in targets.items():
            vv = Z[:, col[x]]
            sc = corr(vv, (tsum[k] - vv) / (len(v) - 1)) if x in v else corr(vv, tsum[k] / len(v))
            if best is None or sc > best[0]:
                best = (sc, k)
        moves[x] = {"from": g0, "score_in_it": s0, "best": f"{best[1][0]}: {best[1][1]}", "best_score": round(best[0], 2), "move": best[0] >= FLOOR}
    out["moves"] = moves
    for t, v in tsets.items():
        if len(v) >= 3:
            sc = loo(v)
            out["themes"][t] = {"n": len(v), "strength": avg_pair(v), "below_floor": sorted(x for x, y in sc.items() if y < FLOOR)}
    gs = [v for v in out["groups"].values() if v.get("strength_after") is not None]
    out["summary"] = {"stocks": len(gmap), "kept": len(kept_all), "dropped": len(dropped),
                      "moved_elsewhere": sum(1 for m in moves.values() if m["move"]),
                      "groups_before": sum(1 for v in out["groups"].values() if v["n"] >= 3), "groups_after": len(gs),
                      "avg_strength_groups_after": round(float(np.mean([v["strength_after"] for v in gs])), 3) if gs else None,
                      "avg_strength_themes": round(float(np.mean([v["strength"] for v in out["themes"].values()])), 3)}
    json.dump(out, open(a_.out, "w"), indent=1)
    print(json.dumps(out["summary"]))


if __name__ == "__main__":
    main()
