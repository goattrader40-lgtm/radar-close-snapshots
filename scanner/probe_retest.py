#!/usr/bin/env python3
"""Breakout levels from the candle bodies, and the retest of a breakout (the launch's own too), against the current
rules, on every launch of the last 2 years.

  python3 scanner/probe_retest.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json

current: the base top is the wick high, a retest counts within 10 sessions of a base breakout after the launch, every
day it qualifies. new: the base's level is the top of its candle bodies (each day the higher of open and close), a
retest counts within 20 sessions of a breakout, the launch's own included, once per pullback, and says when the 21
EMA was there too. Each entry bought at that day's close; then the next 20 sessions: ran 10% / 20% (the high), the
close 20 sessions on, and failed within 5 (a breakout closing back under its level; a retest under that day's low).
"""
import argparse, collections, datetime, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402

L = launch.L


def events(a, i0, i1):
    """the breakouts and retests the follow-through finds day by day under the rules in L"""
    st, c = a.st, a.st.c
    out, used, bo, H, last_new = [], set(), None, st.h[i0], i0
    lbo = None
    if L["retest_launch"] and i0 >= 20:
        tops0 = np.maximum(st.o[i0 - 20:i0], st.c[i0 - 20:i0]) if L["body_tops"] else st.h[i0 - 20:i0]
        if c[i0] > tops0.max():
            lbo = (i0, float(tops0.max()))
    once = bool(L["body_tops"])                           # the new rules: one retest per pullback
    done_since = None
    for j in range(i0 + 1, i1 + 1):
        b = launch.base_breakout(a, j, used)
        if b:
            used.add(b[1])
            bo = (j, b[0])
            out.append((j, "breakout", dict(level=b[0])))
        rb = bo or lbo
        adr = launch._adr(st, j)
        if rb and 1 <= j - rb[0] <= L["retest_days"] and c[j] > rb[1] and rb[1] * (1 - adr / 100) <= st.l[j] <= rb[1] * (1 + adr / 400) \
                and not (c[rb[0] + 1:j + 1] < rb[1] * (1 - adr / 100)).any() and not (once and done_since is not None and done_since >= last_new):
            ema = bool(st.l[j] <= a.e21[j] * (1 + adr / 400) and c[j] > a.e21[j])
            out.append((j, "retest", dict(level=rb[1], ema=ema, launch=rb is lbo)))
            done_since = j
        if st.h[j] > H:
            H, last_new = st.h[j], j
    return out


def outcome(a, j, kind, det):
    st = a.st
    c, h, lo = st.c, st.h, st.l
    n = c.size
    if j + 5 >= n:
        return None
    e = c[j]
    hi = h[j + 1:min(n, j + 21)].max()
    ref = det["level"] if kind == "breakout" else lo[j]
    return dict(ran10=hi >= e * 1.1, ran20=hi >= e * 1.2, r20=100 * (c[j + 20] / e - 1) if j + 20 < n else None,
                fail5=bool((c[j + 1:j + 6] < ref).any()))


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
    res = {}
    base = []
    for name, rules in (("current", dict(body_tops=0, retest_days=10, retest_launch=0)), ("new", dict(body_tops=1, retest_days=20, retest_launch=1))):
        L.update(rules)
        acc = collections.defaultdict(list)
        for s, i0, k, gs, gn in ev:
            a = A[s]
            c = a.st.c
            i1 = min(c.size - 1, i0 + L["follow_days"])
            out50 = next((m for m in range(i0 + 2, i1 + 1) if c[m] < a.e50[m] and c[m - 1] < a.e50[m - 1]), None)
            i1 = out50 if out50 is not None else i1
            if i1 <= i0 + 1:
                continue
            if name == "current":
                base.extend(outcome(a, j, "day", {"level": 0}) for j in range(i0 + 1, i1 + 1))
            for j, kind, det in events(a, i0, i1):
                o = outcome(a, j, kind, det)
                acc[kind].append(o)
                if kind == "retest":
                    acc["retest, 21 EMA there too" if det["ema"] else "retest, 21 EMA not there"].append(o)
                    acc["retest of the launch's own breakout" if det["launch"] else "retest of a later breakout"].append(o)
        res[name] = {k: summ(v) for k, v in sorted(acc.items())}
    out = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), first=cal[200], last=cal[-1],
               launches=len(ev), baseline=summ(base), **res)
    json.dump(out, open(a_.out, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
