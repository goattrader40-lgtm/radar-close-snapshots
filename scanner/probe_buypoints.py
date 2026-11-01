#!/usr/bin/env python3
"""Our Launches buy points, bought the way the alerts fire, the risk the low of that day (Nov 1 2026).

  python3 scanner/probe_buypoints.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json

  buy points   every launch (regular, power, reversal) followed day by day for 60 sessions (until 2 closes under the 50
               EMA), as the Launches tab reads it: base breakout, breakout follow-through, flag breakout, pop out of the
               consolidation, retest held, push out of the 21 EMA, 21 EMA retest, 21 EMA undercut & reclaim
  the buy      at the level when it breaks (base breakout, flag, pop: the day before's buy point, or the open when it gaps
               over it); a push at the open; the close for the rest (retest, follow-through, 21 EMA entries: their signal
               is the close)
  the risk     the low of that day (your stop under the day's low)
  managed      your rules: +2R the stop to breakeven, 1/3 at +3R, 1/3 at +5R, the runners out on a daily close under the
               21 EMA or at breakeven (that close takes whatever is open); on daily bars, the stop first when a day touches
               both; on the buy day only a level / open buy can reach a target (its high came after the buy)
  also         ran 10% / 20% within 20 sessions, failed = a close under that day's low within 5 sessions (the old check)
Every buy point is saved with its RVOL (that day's volume / the 20-day average) and gap, for the spreadsheet's filters.
"""
import argparse, collections, datetime, json, multiprocessing, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402

L = launch.L
A = {}
KINDS = (("follow-through", "Breakout follow-through", "close"), ("retest", "Retest", "close"), ("push", "Push out", "open"),
         ("21 EMA retest", "21 EMA retest", "close"), ("21 EMA undercut & reclaim", "21 EMA undercut", "close"))
# the level buy points: every day the price crosses the day before's buy point is a buy, whatever the close (no hindsight)
LEVEL = (("Base top", "base breakout"), ("Flag", "flag breakout"), ("Pop", "pop"), ("", "pattern pivot"))


def manage(a, j, buy, stop, same_day_high):
    """your management from the buy on day j: (result %, R, reached 2R / 3R / 5R, exit, days held)"""
    c, o, h, l, e21 = a.st.c, a.st.o, a.st.h, a.st.l, a.e21
    R = buy - stop
    t2, t3, t5 = buy + 2 * R, buy + 3 * R, buy + 5 * R
    S = dict(stop=stop, left=1.0, got=0.0, be=False, s3=False, s5=False, r2=False)

    def targets(bo, bh):
        if bh >= t2:
            S["r2"] = True
        if bh >= t3 and not S["s3"]:
            S["got"] += max(t3, bo) / 3; S["left"] -= 1 / 3; S["s3"] = True
        if bh >= t5 and not S["s5"]:
            S["got"] += max(t5, bo) / 3; S["left"] -= 1 / 3; S["s5"] = True
        if S["r2"] and not S["be"]:
            S["stop"], S["be"] = max(S["stop"], buy), True
    if same_day_high is not None:
        targets(buy, same_day_high)
    how, end = None, j
    if c[j] < e21[j]:
        S["got"] += S["left"] * c[j]; S["left"] = 0; how = "daily 21 EMA close"
    else:
        for k in range(j + 1, c.size):
            end = k
            if l[k] <= S["stop"]:
                S["got"] += S["left"] * min(S["stop"], o[k]); S["left"] = 0; how = "breakeven" if S["be"] else "stop"; break
            targets(o[k], h[k])
            if c[k] < e21[k]:
                S["got"] += S["left"] * c[k]; S["left"] = 0; how = "daily 21 EMA close"; break
        if how is None:
            S["got"] += S["left"] * c[-1]; how = "open at the end"
    return 100 * (S["got"] / buy - 1), (S["got"] - buy) / R, S["r2"], S["s3"], S["s5"], how, end - j


def one(key):
    s, i0 = key
    a = A[s]
    st = a.st
    c, o, h, l = st.c, st.o, st.h, st.l
    n = c.size
    out, prev = [], None
    for j in range(i0 + 1, min(n - 6, i0 + 61)):
        f = launch.follow(a, i0, j)
        if f["lost_50ema"]:
            break
        stage = f["stage"]
        pbp, ppat = (prev.get("buy_point"), prev.get("pattern") or "") if prev else (None, "")
        ptight = (prev.get("tight_days") or 0) if prev else 0
        prev = f
        cands = []
        if pbp and h[j] > pbp and c[j - 1] <= pbp:
            k = next(nm for w, nm in LEVEL if ppat.startswith(w))
            if k != "pop" or o[j] > pbp:                    # a pop opens over its level
                cands.append((k, max(float(pbp), float(o[j])), "level", float(h[j])))
        kind = next(((k, how) for k, w, how in KINDS if stage.startswith(w)), None)
        if kind:
            k, how = kind
            cands.append((k, float(o[j]), "open", float(h[j])) if how == "open" else (k, float(c[j]), "close", None))
        closed = ("closed as a breakout" if stage.startswith(("Base breakout", "Flag breakout", "Breakout")) else
                  "closed as a pop" if stage.startswith("Pop out") else "closed back under / no breakout")
        for k, buy, entry, same_high in cands:
            stop = float(l[j])
            if buy <= stop:
                continue
            ret, R, r2, r3, r5, ex, days = manage(a, j, buy, stop, same_high)
            hi20 = h[j + 1:min(n, j + 21)].max()
            r_ = row(s, st, a, f, i0, j, k, entry, buy, stop, ret, R, r2, r3, r5, ex, days, hi20, c, n, closed if entry == "level" else "")
            r_["level"] = round(float(pbp), 2) if entry == "level" else None
            # the tags the Launches tab shows (as of that day's close)
            r_.update(caution_within_0_5pct=int(bool(f.get("breakout_caution"))), double_breakout=int(bool(f.get("double_breakout"))),
                      third_try=int("3rd try of the top" in stage), flag_volume_dried=int(bool(f.get("flag_dry"))),
                      tight_days_before=int(ptight), volume_building_5d=f.get("vol_build"))
            out.append(r_)
    return out


def row(s, st, a, f, i0, j, k, entry, buy, stop, ret, R, r2, r3, r5, ex, days, hi20, c, n, closed):
        return (dict(date=st.dates[j], symbol=s, buy_point=k, bought=entry, day_closed=closed, leg=f.get("leg"), sessions_since_launch=j - i0,
                        launch_date=st.dates[i0], launch_grade=launch.grade(a, i0), rvol_day=round(float(a.rv[j]), 2),
                        gap_pct=round(float(a.gap[j]), 2), day_change_pct=round(float(a.chg[j]), 2), close_in_range_pct=round(100 * float(a.clpos[j])),
                        adr_pct=round(float(st.adr[j]), 2), risk_pct=round(100 * (buy - stop) / buy, 2), result_pct=round(ret, 2), R=round(R, 2),
                        win=int(ret > 0), reached_2R=int(r2), reached_3R=int(r3), reached_5R=int(r5), exit=ex, days_held=days,
                        ran20=int(hi20 >= buy * 1.2), failed5=int((c[j + 1:j + 6] < stop).any())))


def summ(ts):
    if not ts:
        return dict(trades=0)
    R = np.array([t["R"] for t in ts])
    return dict(trades=len(ts), win=round(100 * float(np.mean([t["win"] for t in ts]))), avg_pct=round(float(np.mean([t["result_pct"] for t in ts])), 2),
                avg_R=round(float(R.mean()), 2), med_R=round(float(np.median(R)), 2), total_R=round(float(R.sum()), 1),
                reached_3R=round(100 * float(np.mean([t["reached_3R"] for t in ts]))), reached_5R=round(100 * float(np.mean([t["reached_5R"] for t in ts]))),
                ran20=round(100 * float(np.mean([t["ran20"] for t in ts]))), failed5=round(100 * float(np.mean([t["failed5"] for t in ts]))),
                risk_med_pct=round(float(np.median([t["risk_pct"] for t in ts])), 2))


RV = (("RVOL under 1", 0, 1), ("RVOL 1-1.5", 1, 1.5), ("RVOL 1.5-2", 1.5, 2), ("RVOL 2-3", 2, 3), ("RVOL 3+", 3, 1e9))
GAP = (("gap down", -1e9, 0), ("gap 0-2%", 0, 2), ("gap 2-5%", 2, 5), ("gap 5%+", 5, 1e9))


def main():
    global A
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    L["catalyst_launch"] = 0
    launch.CATALYST_DAYS.clear()
    keys = sorted({(s, i) for s, i, k, gs, gn in launch.detect(A, groups, GS, cal, S) if i >= 200})
    with multiprocessing.get_context("fork").Pool(os.cpu_count() or 2) as pool:
        ts = [t for r in pool.map(one, keys, chunksize=8) for t in r]
    # 2) the same buy point bought at that day's close, the risk the day's low (your management)
    for t in ts:
        a = A[t["symbol"]]
        j = a.st.dates.index(t["date"])
        cb, cl = float(a.st.c[j]), float(a.st.l[j])
        if cb > cl:
            ret, R, r2, r3, r5, ex, days = manage(a, j, cb, cl, None)
            t.update(close_risk_pct=round(100 * (cb - cl) / cb, 2), close_result_pct=round(ret, 2), close_R=round(R, 2), close_win=int(ret > 0),
                     close_reached_3R=int(r3), close_reached_5R=int(r5), close_exit=ex)
    # 3) your 5-minute entry: over the 5-minute opening range high (and over the buy point for a level buy) on the day,
    # the next morning for a close signal; the risk the 5-minute low; your management (scanner/probe_pb1h.py trade)
    if os.environ.get("ALPACA_KEY_ID"):
        import probe_catalyst as pc
        import probe_pb1h as pb
        by_day = collections.defaultdict(list)
        for t in ts:
            a = A[t["symbol"]]
            j = a.st.dates.index(t["date"])
            k = j if t["bought"] in ("level", "open") else j + 1
            if k < a.st.c.size:
                by_day[a.st.dates[k]].append((t, k))
        for d, tk in sorted(by_day.items()):
            t0 = datetime.datetime.fromisoformat(d + "T09:30").replace(tzinfo=pc.NY)
            b5 = pb.bars(sorted({t["symbol"] for t, k in tk}), t0, t0 + datetime.timedelta(minutes=390), "5Min")
            for t, k in tk:
                b = b5.get(pc.alp(t["symbol"]))
                t["min5_bought"] = 0
                if not b or not b[0]["t"].startswith(pc.iso(t0)[:16]):
                    continue
                lvl = max(b[0]["h"], t["level"] or 0)
                m = next((x for x in range(1, len(b)) if b[x]["h"] > lvl), None)
                if m is None:
                    continue
                x = pb.trade(A[t["symbol"]], k, b, -1e9, {}, entry=(m, max(lvl, b[m]["o"])))
                if x and x.get("broke"):
                    t.update(min5_bought=1, min5_day=d, min5_risk_pct=round(x["risk"], 2), min5_result_pct=round(float(x["ret"]), 2),
                             min5_R=round(float(x["R"]), 2), min5_win=int(x["ret"] > 0), min5_reached_3R=int(x["r3"]), min5_reached_5R=int(x["r5"]), min5_exit=x["how"])
    kinds = [nm for _, nm in LEVEL] + [k for k, _, _ in KINDS]
    out = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), first=cal[200], last=cal[-1], launches=len(keys),
               all=summ(ts), by_buy_point={k: summ([t for t in ts if t["buy_point"] == k]) for k in kinds},
               by_rvol={nm: summ([t for t in ts if lo <= t["rvol_day"] < hi]) for nm, lo, hi in RV},
               by_gap={nm: summ([t for t in ts if lo <= t["gap_pct"] < hi]) for nm, lo, hi in GAP},
               by_entry={m: {k: summ([dict(t, R=t[m + "R"], win=t[m + "win"], result_pct=t[m + "result_pct"], reached_3R=t[m + "reached_3R"],
                                             reached_5R=t[m + "reached_5R"], risk_pct=t[m + "risk_pct"]) for t in ts if (k == "all" or t["buy_point"] == k) and m + "R" in t])
                             for k in ["all"] + kinds} for m in ("close_", "min5_")},
               level_buys_by_close={x: summ([t for t in ts if t["day_closed"] == x]) for x in ("closed as a breakout", "closed as a pop", "closed back under / no breakout")},
               by_buy_point_and_rvol={k: {nm: summ([t for t in ts if t["buy_point"] == k and lo <= t["rvol_day"] < hi]) for nm, lo, hi in RV} for k in kinds},
               trades=ts)
    json.dump(out, open(a_.out, "w"))
    print(json.dumps({k: v for k, v in out.items() if k != "trades"}, indent=1))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        json.dump(dict(error=traceback.format_exc()[-3000:]), open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
        raise
