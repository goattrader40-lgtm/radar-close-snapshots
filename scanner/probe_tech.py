#!/usr/bin/env python3
"""Tech review (the user, Nov 3 2026: "I'm focused on tech ... as long as you got it right"). Study only.

  python3 scanner/probe_tech.py --bars BARS.json.gz --stocks stocks.json --themes themes.json --groups groups.json --out OUT.json

Same co-movement measure as radar/pipeline.py (120 sessions, market move removed, z-scored, clipped 3 SD).
For every tech / growth stock $2B+ in no tight industry group and no theme: its best theme / group and score, and
the 5 stocks it moves with most. Then new groups among the uncovered names: seeded by the closest pair, grown by the
name tracking the group best, every member 0.6+ with the rest, 3+ names.
"""
import argparse, collections, json, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402

FLOOR, WIN = 0.6, 120
TECH_SECTORS = {"Information Technology", "Communication Services"}
GROWTH_IND = re.compile(r"Internet|Online|Software|Fintech|Payment|Semiconductor|Electronic|Computer|Aerospace|Space|EV|Electric Vehicle", re.I)


def corr(a, b):
    a = a - a.mean(); b = b - b.mean(); dd = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / dd) if dd else 0.0


def main():
    ap = argparse.ArgumentParser()
    for k in ("bars", "stocks", "themes", "groups", "out"):
        ap.add_argument("--" + k, required=True)
    a_ = ap.parse_args()
    A, _, _, cal, _ = launch.load(a_.bars, a_.stocks)
    rows = json.load(open(a_.stocks))
    stocks = {r["symbol"]: r for r in rows}
    themes = json.load(open(a_.themes)); groups = json.load(open(a_.groups))
    win = cal[-WIN:]; pos = {d: k for k, d in enumerate(win)}
    univ = [s for s in stocks if s in A]
    R = np.full((WIN, len(univ)), np.nan)
    for j, s in enumerate(univ):
        st = A[s].st
        for i in range(1, len(st.dates)):
            k = pos.get(st.dates[i])
            if k is not None:
                R[k, j] = 100 * (st.c[i] / st.c[i - 1] - 1)
    keep = np.isfinite(R).mean(0) >= 0.9
    short = sorted(s for s, k in zip(univ, keep) if not k)
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
    C = np.corrcoef(Z.T)

    def loo(names):
        Zm = Z[:, [col[x] for x in names]]; tot = Zm.sum(1)
        return {x: corr(Zm[:, i], (tot - Zm[:, i]) / (len(names) - 1)) for i, x in enumerate(names)}

    def avg_pair(names):
        idx = [col[x] for x in names]; n = len(idx)
        return round(float((C[np.ix_(idx, idx)].sum() - n) / (n * (n - 1))), 2) if n > 1 else None

    def is_tech(r):
        return r.get("sector") in TECH_SECTORS or bool(GROWTH_IND.search(r.get("industry") or "")) or bool(GROWTH_IND.search(r.get("industry_detail") or ""))

    targets = {}
    for t in themes:
        m = [x for x in (t["members"] + " " + t.get("ext", "")).split() if x in col]
        if len(m) >= 3: targets["theme: " + t["theme"]] = m
    for g in groups:
        m = [x for x in g["members"].split() if x in col]
        if len(m) >= 3: targets["group: " + g["group"]] = m
    tsum = {k: Z[:, [col[x] for x in v]].sum(1) for k, v in targets.items()}

    def fits(x, n=3):
        v = Z[:, col[x]]; out = []
        for k, m in targets.items():
            sc = corr(v, (tsum[k] - v) / (len(m) - 1)) if x in m else corr(v, tsum[k] / len(m))
            out.append((round(sc, 2), k))
        return sorted(out, reverse=True)[:n]

    tech = [s for s in univ if is_tech(stocks[s]) and (stocks[s].get("mcap_b") or 0) >= 2]
    unc = [s for s in tech if not stocks[s].get("group") and not stocks[s].get("themes")]
    pool = [s for s in univ if is_tech(stocks[s]) and (stocks[s].get("mcap_b") or 0) >= 1
            and not stocks[s].get("group") and not stocks[s].get("themes")]
    # new groups among the uncovered (pool: $1B+ may join a group seeded by $2B+ names)
    free = set(pool); new = []
    while True:
        best = None
        for x in unc:
            if x not in free: continue
            for y in unc:
                if y <= x or y not in free: continue
                c = C[col[x], col[y]]
                if c >= FLOOR and (best is None or c > best[0]): best = (c, x, y)
        if not best: break
        g = [best[1], best[2]]
        while True:
            gs = Z[:, [col[x] for x in g]].sum(1)
            cand = sorted(((corr(Z[:, col[z]], gs / len(g)), z) for z in free if z not in g), reverse=True)
            added = False
            for sc, z in cand[:5]:
                if sc < FLOOR: break
                if min(loo(g + [z]).values()) >= FLOOR:
                    g.append(z); added = True; break
            if not added: break
        for x in g: free.discard(x)
        if len(g) >= 3:
            sc = loo(g)
            new.append({"members": sorted(((round(v, 2), x) for x, v in sc.items()), reverse=True), "strength": avg_pair(g),
                        "industries": collections.Counter(stocks[x].get("industry_detail") or stocks[x].get("industry") for x in g).most_common(3)})
        else:
            for x in g: free.add(x)
            free.discard(best[1]); free.discard(best[2])   # the pair alone: not a group; stop reseeding it
    in_new = {x for g in new for _, x in g["members"]}
    out = {"window": [win[0], win[-1]], "floor": FLOOR, "tech_total": len(tech), "uncovered": len(unc),
           "too_short": [s for s in short if is_tech(stocks[s]) and (stocks[s].get("mcap_b") or 0) >= 2],
           "new_groups": new, "stocks": {}}
    for x in sorted(unc, key=lambda s: -(stocks[s].get("mcap_b") or 0)):
        v = C[col[x]].copy(); v[col[x]] = -9
        top = [(round(float(v[i]), 2), univ[i]) for i in np.argsort(-v)[:5]]
        r = stocks[x]
        out["stocks"][x] = {"name": r.get("name"), "mcap_b": r.get("mcap_b"), "sector": r.get("sector"),
                            "industry": r.get("industry_detail") or r.get("industry"), "best": fits(x), "moves_with": top,
                            "new_group": next((i for i, g in enumerate(new) if x in {y for _, y in g["members"]}), None)}
    json.dump(out, open(a_.out, "w"), indent=1)
    print(f"tech {len(tech)}, uncovered {len(unc)}, new groups {len(new)} ({len(in_new)} names), too short {len(out['too_short'])}")


if __name__ == "__main__":
    main()
