#!/usr/bin/env python3
"""The catalyst launch (a 5%+ gap that closes net positive, still in the gap and over its 3- and 6-month bases by the
candle bodies, at least the 1-month one, though up less than 5%) against the current launch rules, on the last 2 years; the catalyst
launches also split by the longest base they cleared (1, 3 or 6 months).

  python3 scanner/probe_catalyst.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json

Scored like the launch backtest: bought at the launch day's open (and, apart, at its close: a catalyst day often
closes under its open), stopped under that day's low from the next day, otherwise sold on the first close under the
21 EMA; plus ran 20% / 50% (the high before the exit).
"""
import argparse, datetime, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402

L = launch.L


def trade(a, i, at="open"):
    st, c, o, lo = a.st, a.st.c, a.st.o, a.st.l
    buy, stop = (o if at == "open" else c)[i], lo[i]
    for j in range(i + 1, c.size):
        if lo[j] <= stop:
            return 100 * (min(stop, o[j]) / buy - 1), 100 * (st.h[i:j + 1].max() / buy - 1)
        if c[j] < a.e21[j]:
            return 100 * (c[j] / buy - 1), 100 * (st.h[i:j + 1].max() / buy - 1)
    return None


def both(A, keys):
    return dict(open=summ([trade(A[s], i) for s, i in keys]), close=summ([trade(A[s], i, "close") for s, i in keys]))


def summ(rs):
    rs = [r for r in rs if r]
    if not rs:
        return None
    ret, mg = np.array([r[0] for r in rs]), np.array([r[1] for r in rs])
    return dict(n=len(rs), win=round(100 * float(np.mean(ret > 0))), avg=round(float(ret.mean()), 1), med=round(float(np.median(ret)), 1),
                ran20=round(100 * float(np.mean(mg >= 20))), ran50=round(100 * float(np.mean(mg >= 50))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    sets = {}
    for flag in (0, 1):
        L["catalyst_launch"] = flag
        sets[flag] = {(s, i) for s, i, k, gs, gn in launch.detect(A, groups, GS, cal, S)}
    new = sets[1] - sets[0]
    gone = sets[0] - sets[1]
    cat = [(s, i) for s, i in sets[1] if A[s].chg[i] < L["min_chg"] or not A[s].held(i)]
    out = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), first=cal[200], last=cal[-1],
               current=both(A, sets[0]), with_catalyst=both(A, sets[1]), catalyst_launches=both(A, cat), added=len(new), replaced=len(gone),
               replaced_launches=both(A, gone),
               catalyst_by_base={f"{n} sessions": both(A, [(s, i) for s, i in cat if A[s].cleared(i) == n]) for n in launch.BASES},
               all_by_base={f"{n} sessions": both(A, [(s, i) for s, i in sets[1] if A[s].cleared(i) == n]) for n in launch.BASES + (0,)},
               examples=sorted((A[s].st.dates[i], s, round(float(A[s].gap[i]), 1), round(float(A[s].chg[i]), 1), round(float(A[s].rv[i]), 1), A[s].cleared(i)) for s, i in cat)[-25:])
    json.dump(out, open(a_.out, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
