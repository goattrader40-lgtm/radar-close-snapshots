#!/usr/bin/env python3
"""Launch days bought your way (Nov 1 2026): on the launch day, over the 5-minute opening range high, the risk the
5-minute opening range low; by launch type (regular, power day, reversal day, catalyst launch with news).

  python3 scanner/probe_launch_orh.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json
  (needs ALPACA_KEY_ID / ALPACA_SECRET: the news for the catalyst launches, the launch days' 5-minute bars)

  managed  your pullback-test management (scanner/probe_pb1h.py trade): +2R the stop to breakeven, 1/3 at +3R,
           1/3 at +5R, the runners out on a daily close under the 21 EMA or at breakeven (that close takes whatever
           is open); the entry day on 5-minute bars, the days after on daily bars (the stop first when a day
           touches both)
  simple   the stop at the 5-minute low the whole way, out on the first daily close under the 21 EMA
"""
import argparse, collections, datetime, json, os, sys, time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402
import probe_catalyst as pc  # noqa: E402
import probe_pb1h as pb  # noqa: E402

L = launch.L


def simple(a, k, b5):
    st, c, o, l, h, e21 = a.st, a.st.c, a.st.o, a.st.l, a.st.h, a.e21
    orh, orl = b5[0]["h"], b5[0]["l"]
    m = next((x for x in range(1, len(b5)) if b5[x]["h"] > orh), None)
    if m is None:
        return dict(broke=False)
    buy = max(orh, b5[m]["o"])
    R = buy - orl
    if R <= 0:
        return None
    if any(x["l"] <= orl for x in b5[m:]):
        sell, j_out, how = orl, k, "stop"
    elif c[k] < e21[k]:
        sell, j_out, how = c[k], k, "daily 21 EMA close"
    else:
        sell, j_out, how = c[-1], c.size - 1, "open at the end"
        for j in range(k + 1, c.size):
            if l[j] <= orl:
                sell, j_out, how = min(orl, o[j]), j, "stop"; break
            if c[j] < e21[j]:
                sell, j_out, how = c[j], j, "daily 21 EMA close"; break
    mg = float(100 * (h[k:j_out + 1].max() / buy - 1))
    return dict(broke=True, ret=100 * (sell / buy - 1), R=(sell - buy) / R, risk=100 * R / buy, days=j_out - k, how=how,
                same_day=j_out == k and how == "stop", r2=mg >= 200 * R / buy, r3=mg >= 300 * R / buy, r5=mg >= 500 * R / buy, mg=mg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    first = 200
    # regular launches (with power and reversal days): the catalyst rule off
    L["catalyst_launch"] = 0
    launch.CATALYST_DAYS.clear()
    reg = {(s, i) for s, i, k, gs, gn in launch.detect(A, groups, GS, cal, S) if i >= first}
    # catalyst launches with news (as scanner/probe_catalyst.py)
    every = {}
    for s, a in A.items():
        for i in range(max(a.start, first), a.st.c.size):
            if a.gap[i] >= L["ep_gap"] and a.chg[i] > 0 and not (a.chg[i] >= L["min_chg"] and a.held(i)):
                every[(s, a.st.dates[i])] = "?"
    L["catalyst_launch"] = 1
    launch.CATALYST_DAYS.update(every)
    maybe = [(s, i) for s, a in A.items() for i in range(max(a.start, first), a.st.c.size) if a.catalyst(i) and a.candidate(i)]
    news = {}
    for s, i in maybe:
        r = pc.news_on(s, A[s].st.dates[i], A[s].st.dates[i - 1])
        if r:
            news[(s, A[s].st.dates[i])] = r[0]
        time.sleep(0.3)
    launch.CATALYST_DAYS.clear()
    launch.CATALYST_DAYS.update(news)
    cat = {(s, i) for s, i, k, gs, gn in launch.detect(A, groups, GS, cal, S) if i >= first} - reg
    kind = {}
    for s, i in reg:
        a = A[s]
        kind[(s, i)] = "power day" if a.power(i) else "reversal day" if a.reversal(i) else "regular"
    for key in cat:
        kind[key] = "catalyst (news)"
    by_day = collections.defaultdict(list)
    for s, i in kind:
        if i < A[s].st.c.size:
            by_day[A[s].st.dates[i]].append((s, i))
    tm, ts = [], []
    for d, ks in sorted(by_day.items()):
        t0 = datetime.datetime.fromisoformat(d + "T09:30").replace(tzinfo=pc.NY)
        b5 = pb.bars(sorted({s for s, i in ks}), t0, t0 + datetime.timedelta(minutes=390), "5Min")
        for s, i in ks:
            b = b5.get(pc.alp(s))
            if not b or not b[0]["t"].startswith(pc.iso(t0)[:16]):
                continue
            x = pb.trade(A[s], i, b, -1e9, {})
            y = simple(A[s], i, b)
            for lst, t in ((tm, x), (ts, y)):
                if t is not None:
                    t.update(kind=kind[(s, i)], sym=s, date=d, grade=launch.grade(A[s], i))
                    lst.append(t)
    kinds = ["regular", "power day", "reversal day", "catalyst (news)"]
    out = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), first=cal[first], last=cal[-1],
               launches={k: sum(1 for v in kind.values() if v == k) for k in kinds},
               managed=dict(all=pb.summ(tm), **{k: pb.summ([t for t in tm if t["kind"] == k]) for k in kinds},
                            by_grade={g: pb.summ([t for t in tm if t["grade"] == g]) for g in ("A+", "A", "B", "C")}),
               simple=dict(all=pb.summ(ts), **{k: pb.summ([t for t in ts if t["kind"] == k]) for k in kinds}))
    json.dump(out, open(a_.out, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        json.dump(dict(error=traceback.format_exc()[-3000:]), open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
        raise
