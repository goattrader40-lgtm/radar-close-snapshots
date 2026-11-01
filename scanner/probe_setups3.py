#!/usr/bin/env python3
"""The 2-year check of the new 3-SETUPS (your Nov 1 2026 design): are its buy points, on stocks without a launch day,
as good as the Launches ones?

  python3 scanner/probe_setups3.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json

The Watchlist's feeder lists don't exist for past years, so they are rebuilt from the daily bars with each list's entry
rule (scanner/settings.json): 1-EP/GAP a gap over 5% on 2.5x volume, 1-UPDAY up 4%+ on 1x+ volume, 2-POOL the first close
back over the 50 EMA after 2+ under it or a momentum leader (1W 10%+, 1M 25%+, 3M 50%+, 6M 50%+ over the 200 SMA); all
with the standard filters (price $10+, liquid, ADR 3.5%+, over the 50 EMA, 30%+ over the 52-week low). A stock is then
read every day by the same rules as the evening scan (launch.s3_read) until it leaves: the 1-lists' gap / up-day low
lost, 15 sessions without reaching 3-SETUPS, 2-POOL under the 200 SMA, or the 3-SETUPS exits (2 closes under the 50 EMA,
62 sessions without a new high, ADR under 3.2%); 120 sessions at most.

Scored (ran 10% / 20% = the high within 20 sessions; failed = a close under the entry day's low within 5 sessions):
  Triggered today  bought at that day's close, by setup
  Ready            bought the next day if it trades over the trigger (at the open when it gaps over it), by setup;
                   how often the trigger is hit the next day
  Setting up       how often it reaches Ready or Triggered within 10 sessions
"""
import argparse, collections, datetime, json, multiprocessing, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402

L = launch.L
A = {}
FIRST = 0


def feeder(a, i):
    """the feeder list a stock would come on at bar i (None = none)"""
    st = a.st
    c = st.c
    std = bool(a.liq_noadr[i] and st.adr[i] >= 3.5 and c[i] > a.e50[i] and c[i] >= st.low52[i] * 1.3)
    if std and a.gap[i] > 5 and a.rv[i] >= 2.5:
        return "1-EP/GAP"
    if std and a.chg[i] >= 4 and a.rv[i] >= 1:
        return "1-UPDAY"
    if a.liq_noadr[i] and st.adr[i] >= 3.5 and c[i] > a.e50[i] and c[i - 1] < a.e50[i - 1] and c[i - 2] < a.e50[i - 2]:
        return "2-POOL"
    if std and i >= 126 and ((c[i] / c[i - 5] - 1) >= 0.10 or (c[i] / c[i - 21] - 1) >= 0.25 or (c[i] / c[i - 63] - 1) >= 0.50
                             or ((c[i] / c[i - 126] - 1) >= 0.50 and c[i] > a.s200[i] and c[i] >= st.low52[i] * 1.5)):
        return "2-POOL"
    return None


def outcome(st, k, e):
    n = st.c.size
    hi = st.h[k:min(n, k + 20)].max()
    return dict(ran10=bool(hi >= e * 1.1), ran20=bool(hi >= e * 1.2), fail5=bool((st.c[k:min(n, k + 6)] < st.l[k]).any()),
                r20=float(100 * (st.c[k + 20] / e - 1)) if k + 20 < n else None)


def one(sym):
    a = A[sym]
    st = a.st
    n = st.c.size
    trig, ready, setting, seq = [], [], [], []
    i0, src, was_in, ever = None, None, False, False
    for j in range(max(a.start, FIRST), n - 21):
        if i0 is not None:
            end = (j - i0 > 120 or (st.c[j] < a.e50[j] and st.c[j - 1] < a.e50[j - 1])
                   or (src != "2-POOL" and st.c[j] < st.l[i0]) or (src != "2-POOL" and not ever and j - i0 >= 15)
                   or (src == "2-POOL" and st.c[j] < a.s200[j]) or (was_in and st.adr[j] < L["off_adr"]))
            if end:
                i0, was_in = None, False
        if i0 is None:
            f = feeder(a, j)
            if f:
                i0, src, was_in, ever = j, f, False, False
            continue
        x = launch.s3_read(a, i0, j, was_in)
        if x is None:
            was_in = False
            continue
        sec, setup, f, bp, away_adr, c, adr, tight, z = x
        was_in = ever = True
        seq.append((j, sec))
        if sec == "Triggered today":
            trig.append(dict(setup=setup, src=src, **outcome(st, j, st.c[j])))
        elif sec == "Ready" and bp:
            k = j + 1
            hit = bool(st.h[k] > bp)
            r = dict(setup=setup.split(" (")[0], src=src, hit=hit, tight=tight >= 2)
            if hit:
                r.update(outcome(st, k, max(float(st.o[k]), float(bp))))
            ready.append(r)
        else:
            setting.append(dict(setup=setup, j=j))
    # Setting up: reached Ready or Triggered within 10 sessions
    later = [j for j, s in seq if s != "Setting up"]
    for r in setting:
        r["became"] = any(r["j"] < j <= r["j"] + 10 for j in later)
    return sym, trig, ready, setting


def summ(rs):
    rs = [r for r in rs if "ran20" in r]
    if not rs:
        return dict(n=0)
    r20 = [r["r20"] for r in rs if r["r20"] is not None]
    return dict(n=len(rs), ran10=round(100 * np.mean([r["ran10"] for r in rs])), ran20=round(100 * np.mean([r["ran20"] for r in rs])),
                fail5=round(100 * np.mean([r["fail5"] for r in rs])), med20=round(float(np.median(r20)), 1) if r20 else None)


def main():
    global A, FIRST
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    FIRST = 200
    with multiprocessing.get_context("fork").Pool(os.cpu_count() or 2) as pool:
        res = pool.map(one, sorted(A), chunksize=8)
    trig = [r for _, t, _, _ in res for r in t]
    ready = [r for _, _, rd, _ in res for r in rd]
    setting = [r for _, _, _, s in res for r in s]
    by = lambda rs, key: {k: summ([r for r in rs if r[key] == k]) for k in sorted({r[key] for r in rs})}
    hits = [r for r in ready if r["hit"]]
    out = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), first=cal[FIRST], last=cal[-22],
               triggered=dict(all=summ(trig), by_setup=by(trig, "setup"), by_list=by(trig, "src")),
               ready=dict(days=len(ready), hit_next_day_pct=round(100 * len(hits) / len(ready)) if ready else None, all=summ(hits),
                          by_setup=by(hits, "setup"), by_list=by(hits, "src"),
                          tight=summ([r for r in hits if r["tight"]]), not_tight=summ([r for r in hits if not r["tight"]])),
               setting_up=dict(days=len(setting), became_ready_or_triggered_10d_pct=round(100 * np.mean([r["became"] for r in setting])) if setting else None,
                               by_setup={k: dict(days=sum(1 for r in setting if r["setup"] == k),
                                                 became_pct=round(100 * np.mean([r["became"] for r in setting if r["setup"] == k])))
                                         for k in sorted({r["setup"] for r in setting})}))
    json.dump(out, open(a_.out, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    try:
        main()
    except Exception:                            # the run's log isn't readable from the session: the error goes out instead
        import traceback
        json.dump(dict(error=traceback.format_exc()[-3000:]), open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
        raise
