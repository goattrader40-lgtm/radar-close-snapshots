#!/usr/bin/env python3
"""The levels design (scanner/levels.py) against the current one, on every launch of the last 2 years.

  python3 scanner/probe_levels.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json

Each launch is followed from the day after it to 120 sessions on (or 2 closes under the 50 EMA). The current design's
entries: base breakouts (a close over the 2- or 6-month base top on 1x+ volume), flag breakouts, retests within 10
sessions. The new one's: breakouts of any clear level (with the tight days before it and 1-year highs apart),
failed breakouts, retests of the broken level and 21 EMA tests at the close, the sloping line under a flat top.
Each entry bought at that day's close; then the next 20 sessions: ran 10% / 20% (the high), the close 20 sessions
on, and failed within 5 (a breakout closing back under its level; the others closing under the entry day's low).
"""
import argparse, collections, datetime, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402
import levels  # noqa: E402

L = launch.L


def old_events(a, i0, i1):
    """the current design's entries, as follow() finds them day by day"""
    st, c = a.st, a.st.c
    out = []
    H, last_new, armed, last_leg = st.h[i0], i0, False, i0
    used, bo = set(), None
    for j in range(i0 + 1, i1 + 1):
        f = launch.flag_at(a, j) if armed else None
        at_highs = bool(f and st.h[f[0]] >= st.h[max(0, f[0] - 120):f[0] + 1].max()
                        and st.h[f[0]] >= c[last_leg] * (1 + L["flag_run_adr"] * launch._adr(st, last_leg) / 100))
        flag_go = bool(f and at_highs and f[0] not in used and c[j] > f[2] and c[j - 1] <= (launch.flag_at(a, j - 1) or (0, 0, np.inf))[2])
        b = launch.base_breakout(a, j, used)
        if flag_go:
            out.append((j, "flag", dict(line=float(f[2]))))
        if b:
            out.append((j, "breakout", dict(level=float(b[0]))))
        if flag_go or b:
            used.add(f[0] if flag_go else b[1])
            if b:
                bo = (j, b[0], b[1])
            if j - last_leg >= L["leg_pause"]:
                last_leg, armed = j, False
        if st.h[j] > H:
            H, last_new, armed = st.h[j], j, True
        adr = launch._adr(st, j)
        if bo and 1 <= j - bo[0] <= L["retest_days"] and c[j] > bo[1] and bo[1] * (1 - adr / 100) <= st.l[j] <= bo[1] * (1 + adr / 400):
            out.append((j, "retest", dict(level=float(bo[1]))))
    return out


def outcome(a, j, kind, det):
    st = a.st
    c, h, lo = st.c, st.h, st.l
    n = c.size
    if j + 5 >= n:
        return None
    e = c[j]
    hi = h[j + 1:min(n, j + 21)].max()
    ref = det.get("level") if kind == "breakout" and det.get("level") else lo[j]
    return dict(ran10=hi >= e * 1.1, ran20=hi >= e * 1.2, r20=100 * (c[j + 20] / e - 1) if j + 20 < n else None,
                fail5=bool((c[j + 1:j + 6] < ref).any()), full=j + 20 < n)


def grade_at(a, s, j, i0, nbo, groups, GS, pos):
    """the breakout grade's ingredients on day j (radar/alerts.py grade_breakout): early = the 1st or 2nd breakout since
    the launch, within 50 sessions of it; the theme Leading; the volume building the 5 days before (1.1x+ the 50 before)"""
    v = a.st.v
    early = nbo < 2 and j - i0 < 50
    lead = launch.best_group(s, pos[a.st.dates[j]], groups, GS)[0] == 2
    build = j >= 55 and v[j - 5:j].mean() / max(1.0, v[j - 55:j - 5].mean()) >= 1.1
    return "A" if early and lead and build else "B" if early and (lead or build) else "C"


def summ(rs):
    rs = [r for r in rs if r]
    if not rs:
        return None
    r20 = [r["r20"] for r in rs if r["r20"] is not None]
    return dict(n=len(rs), ran10=round(100 * np.mean([r["ran10"] for r in rs])), ran20=round(100 * np.mean([r["ran20"] for r in rs])),
                avg20=round(float(np.mean(r20)), 1) if r20 else None, fail5=round(100 * np.mean([r["fail5"] for r in rs])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    ev = launch.detect(A, groups, GS, cal, S)
    old, new = collections.defaultdict(list), collections.defaultdict(list)
    pos = {d: k for k, d in enumerate(cal)}
    base = collections.defaultdict(list)
    same = collections.Counter()
    per_launch_old, per_launch_new = [], []
    for s, i0, k, gs, gn in ev:
        a = A[s]
        c = a.st.c
        n = c.size
        i1 = min(n - 1, i0 + L["follow_days"])
        out50 = next((m for m in range(i0 + 2, i1 + 1) if c[m] < a.e50[m] and c[m - 1] < a.e50[m - 1]), None)
        if out50 is not None:
            i1 = out50
        if i1 <= i0 + 1:
            continue
        oe = old_events(a, i0, i1)
        ne, _ = levels.walk(a, i0, i1)
        per_launch_old.append(len(oe))
        per_launch_new.append(len([e for e in ne if e[1] != "failed"]))
        odays = {(j, kind) for j, kind, _ in oe}
        nb = 0
        for j, kind, det in oe:
            o = outcome(a, j, kind, det)
            old[kind].append(o)
            if kind == "breakout":
                old["breakout, grade " + grade_at(a, s, j, i0, nb, groups, GS, pos)].append(o)
                nb += 1
        # the baseline: any day in the same stocks and windows, bought at the close
        for j in range(i0 + 1, i1 + 1):
            o = outcome(a, j, "day", {})
            base["any day"].append(o)
            base["any day above the 21 EMA" if c[j] > a.e21[j] else "any day under the 21 EMA"].append(o)
        nb = 0
        for j, kind, det in ne:
            if kind == "failed":
                new["failed (no entry)"].append(None)
                continue
            o = outcome(a, j, kind, det)
            new[kind].append(o)
            g = grade_at(a, s, j, i0, nb, groups, GS, pos)
            new[kind + ", grade " + g].append(o)
            if kind == "breakout":
                nb += 1
                new["breakout, tight 2+ days before" if det["tight"] >= 2 else "breakout, not tight"].append(o)
                if det["year_high"]:
                    new["breakout, 1-year high"].append(o)
                was = any(oj == j and ok == "breakout" for oj, ok in odays)
                new["breakout the current design also had" if was else "breakout only the new design has"].append(o)
                same["breakout days in both"] += int(was)
            if kind in ("retest", "ema21"):
                new["retest or 21 EMA test (end of day)"].append(o)
                new["retest or 21 EMA test, grade " + g].append(o)
    months = len(cal[200:]) / 21
    res = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), first=cal[200], last=cal[-1],
               launches=len(ev), months=round(months, 1),
               entries_per_launch=dict(current=round(float(np.mean(per_launch_old)), 2), new=round(float(np.mean(per_launch_new)), 2)),
               baseline={k: summ(v) for k, v in sorted(base.items())},
               current={k: summ(v) for k, v in sorted(old.items())},
               new={k: (summ(v) if k != "failed (no entry)" else dict(n=len(v))) for k, v in sorted(new.items())},
               same=dict(same), rules=levels.LV)
    json.dump(res, open(a_.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "rules"}, indent=1))


if __name__ == "__main__":
    main()
