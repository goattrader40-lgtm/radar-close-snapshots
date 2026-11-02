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
LIVE=1 (cmd buypointsx, Nov 2 2026): each launch followed as the live tab does (no 60-session cap: off at the 3rd close under
the 50 EMA, 62 sessions without a new high, ADR under 3.2% or a newer launch), and every buy point measured for how late in
its run it is and how clean its trend is (scanner/feats.py), plus the market (SPY).
"""
import argparse, collections, datetime, json, multiprocessing, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402
import mgmt  # noqa: E402
import feats  # noqa: E402

L = launch.L
A = {}
GROUPS, GS, POS = {}, {}, {}
NEXT, SPY = {}, None
LIVE = os.environ.get("LIVE") == "1"
KINDS = (("follow-through", "Breakout follow-through", "close"), ("retest", "Retest", "close"), ("push", "Push out", "open"),
         ("21 EMA retest", "21 EMA retest", "close"), ("21 EMA undercut & reclaim", "21 EMA undercut", "close"),
         ("50 EMA undercut & reclaim", "50 EMA undercut", "close"), ("breakout undercut & reclaim", "Breakout undercut", "close"))
# the level buy points: every day the price crosses the day before's buy point is a buy, whatever the close (no hindsight)
LEVEL = (("Base top", "base breakout"), ("Bull flag", "bull flag breakout"), ("Flag", "bull flag breakout"), ("Bull pennant", "bull pennant breakout"),
         ("Pop", "pop"), ("", "pattern pivot"))


def manage(a, j, buy, stop, same_day_high, runner=21):
    """your management (scanner/mgmt.py) from the buy on day j, the stop the day's low"""
    return mgmt.run(a, j, buy, stop, same_day_high=same_day_high, runner=runner)


def one(key):
    s, i0 = key
    a = A[s]
    st = a.st
    c, o, h, l = st.c, st.o, st.h, st.l
    n = c.size
    out, prev = [], None
    for j in range(i0 + 1, n - 6 if LIVE else min(n - 6, i0 + 61)):
        if LIVE and (j >= NEXT.get((s, i0), 10 ** 9) or launch.stale(a, i0, j) or st.adr[j] < L["off_adr"]):
            break                       # the live tab drops it: 62 sessions without a new high, ADR under 3.2%, a newer launch
        f = launch.follow(a, i0, j)
        if f.get("off_50ema") or (f["lost_50ema"] and "off_50ema" not in f):
            break                       # off the list: the 3rd close in a row under the 50 EMA (after 2: the 50 EMA undercut tab)
        stage = f["stage"]
        pbp, ppat = (prev.get("buy_point"), prev.get("pattern") or "") if prev else (None, "")
        ptight = (prev.get("tight_days") or 0) if prev else 0
        pbo, pvb, pses = ((prev.get("breakouts") or 0), (prev.get("vol_build") or 0), prev.get("sessions")) if prev else (0, 0, None)
        pleg = (prev.get("leg") or 0) if prev else 0
        prev = f
        cands = []
        # a day whose high crosses a base top (the 6- or 3-month base the engine calls a breakout of) is a base breakout,
        # bought at that top, whatever smaller trigger it crossed first (AEHR Apr 6 2026: over its inner-base pivot 45.75,
        # then its base top 46.95 set Mar 4: a base breakout, not an inner base)
        bt = next((float(b_[0]) for b_ in (launch.base_ok(a, j, sp) for sp in (120, 63)) if b_ and c[j - 1] <= b_[0] < h[j]), None)
        also = None
        if bt:
            cands.append(("base breakout", max(bt, float(o[j])), "level", float(h[j])))
            if pbp and abs(pbp - bt) > 0.005 * bt and h[j] > pbp and c[j - 1] <= pbp:
                also = f"{ppat or 'buy point'} {pbp:.2f}"
            pbp_used = bt
        elif pbp and h[j] > pbp and c[j - 1] <= pbp:
            k = next(nm for w, nm in LEVEL if ppat.startswith(w))
            if k != "pop" or o[j] > pbp:                    # a pop opens over its level
                cands.append((k, max(float(pbp), float(o[j])), "level", float(h[j])))
            pbp_used = pbp
        else:
            pbp_used = pbp
        kind = next(((k, how) for k, w, how in KINDS if stage.startswith(w)), None)
        if kind:
            k, how = kind
            cands.append((k, float(o[j]), "open", float(h[j])) if how == "open" else (k, float(c[j]), "close", None))
        closed = ("closed as a breakout" if stage.startswith(("Base breakout", "Flag breakout", "Bull flag breakout", "Bull pennant breakout", "Breakout")) else
                  "closed as a pop" if stage.startswith("Pop out") else "closed back under / no breakout")
        for k, buy, entry, same_high in cands:
            stop = float(l[j])
            if buy <= stop:
                continue
            x21, x10 = manage(a, j, buy, stop, same_high, 21), manage(a, j, buy, stop, same_high, 10)
            hi20 = h[j + 1:min(n, j + 21)].max()
            r_ = row(s, st, a, f, i0, j, k, entry, buy, stop, x21, x10, hi20, c, n, closed if entry == "level" else "")
            r_["level"] = round(float(pbp_used), 2) if entry == "level" else None
            r_["leg_before"] = pleg
            # known before the buy day's volume and close (for an intraday buy): the volume building the 5 days to the day
            # before, and the theme's status the day before
            r_["volume_building_prev"] = pvb or None
            if st.dates[j - 1] in POS:
                gp = launch.best_group(s, POS[st.dates[j - 1]], GROUPS, GS)[0]
                r_["theme_prev"] = {2: "Leading", 1: "Turning up", 0: "Not trending"}.get(gp, "no theme")
            if LIVE:
                r_.update(feats.late(a, j))
                r_.update(feats.trend(a, j, i0))
                if SPY is not None:
                    r_.update(feats.market(SPY, st.dates[j]))
            r_["also_crossed"] = also if entry == "level" else None
            # what the engine (the Launches tab) reads that day after the close, and whether it read this very breakout: a
            # flag breakout = the close over the line and the 10 & 21 EMA, not a poke over it during the day (the user,
            # Nov 1 2026: "I checked flag breakouts, nothing matches": 537 of 877 were pokes that closed back under)
            r_["engine_read"] = stage[:180]
            r_["engine_confirmed"] = int(bool({"bull flag breakout": f.get("flag_breakout_today"), "bull pennant breakout": f.get("flag_breakout_today"), "base breakout": f.get("base_breakout_today"),
                                               "pop": f.get("dry_entry_today"),
                                               "pattern pivot": f.get("breakout_today") or f.get("base_breakout_today")}.get(k, True))) \
                if entry == "level" else 1
            # the theme that day and the breakout grade the alerts give (early = 1st / 2nd breakout within 50 sessions of the
            # launch; a Leading theme; the volume building the 5 days before, 1.1x+)
            gs = launch.best_group(s, POS[st.dates[j]], GROUPS, GS)[0] if st.dates[j] in POS else -1
            early, lead, build = pbo < 2 and (j - i0) < 50, gs == 2, pvb >= 1.1
            r_.update(theme_status={2: "Leading", 1: "Turning up", 0: "Not trending"}.get(gs, "no theme"),
                      breakout_grade="A" if early and lead and build else "B" if early and (lead or build) else "C",
                      early_breakout=int(early))
            # as the alert fires, sold at the close when that day closes back under the buy point (a level buy)
            if entry == "level":
                for x, suf in ((x21, ""), (x10, "_10")):
                    y = mgmt.sold_at_close(x, a, j, buy, x["risk"], "sold at the close: back under the buy point") if c[j] <= pbp_used else x
                    r_.update(mgmt.cols(y, "alertcx_", suf))
            # the tags the Launches tab shows (as of that day's close)
            r_.update(caution_within_0_5pct=int(bool(f.get("breakout_caution"))), double_breakout=int(bool(f.get("double_breakout"))),
                      third_try=int("3rd try of the top" in stage), flag_volume_dried=int(bool(f.get("flag_dry"))),
                      tight_days_before=int(ptight), volume_building_5d=f.get("vol_build"),
                      # what the buy point came from: the trigger's pattern (base top, flag line, an MSF pattern's pivot: ascending
                      # triangle, flat base, cup with handle...), the base's MSF name, and the EMAs with a retest (10 / 21 / 50)
                      pattern=("Base top" if bt and k == "base breakout" else (ppat or None)) if entry == "level" else (f.get("pattern") or None),
                      base_pattern=f.get("base_pattern"),
                      retest_with=(" & ".join(f.get("retest_ema") or []) or "no EMA") if k == "retest" else None)
            out.append(r_)
    return out


def row(s, st, a, f, i0, j, k, entry, buy, stop, x21, x10, hi20, c, n, closed):
    r = dict(date=st.dates[j], symbol=s, buy_point=k, bought=entry, day_closed=closed, leg=f.get("leg"), sessions_since_launch=j - i0,
             launch_date=st.dates[i0], launch_grade=launch.grade(a, i0), rvol_day=round(float(a.rv[j]), 2),
             gap_pct=round(float(a.gap[j]), 2), day_change_pct=round(float(a.chg[j]), 2), close_in_range_pct=round(100 * float(a.clpos[j])),
             adr_pct=round(float(st.adr[j - 1]), 2), days_held=x21["days"],
             ran20=int(hi20 >= buy * 1.2), failed5=int((c[j + 1:j + 6] < stop).any()))
    r.update(mgmt.liquidity(a, j))
    r.update(mgmt.reset(a, j))                  # the momentum reset before the buy (your AEHR read, Nov 1 2026)
    r.update(mgmt.cols(x21))
    r.update(mgmt.cols(x10, suf="_10"))
    return r


def summ(ts):
    if not ts:
        return dict(trades=0)
    R = np.array([t["R"] for t in ts])
    return dict(trades=len(ts), win=round(100 * float(np.mean([t["win"] for t in ts]))), avg_pct=round(float(np.mean([t["result_pct"] for t in ts])), 2),
                avg_R=round(float(R.mean()), 2), med_R=round(float(np.median(R)), 2), total_R=round(float(R.sum()), 1),
                reached_2ADR=round(100 * float(np.mean([t["reached_2ADR"] for t in ts]))), reached_5ADR=round(100 * float(np.mean([t["reached_5ADR"] for t in ts]))),
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
    global GROUPS, GS, POS
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    GROUPS, POS = groups, {d: k for k, d in enumerate(cal)}
    L["catalyst_launch"] = 0
    launch.CATALYST_DAYS.clear()
    keys = sorted({(s, i) for s, i, k, gs, gn in launch.detect(A, groups, GS, cal, S) if i >= 200})
    global NEXT, SPY
    by = collections.defaultdict(list)
    for s_, i_ in keys:
        by[s_].append(i_)
    NEXT = {(s_, i_): (ii[x + 1] if x + 1 < len(ii) else 10 ** 9) for s_, ii in by.items() for x, i_ in enumerate(ii)}
    if LIVE:
        import gzip, types
        sb = json.load(gzip.open(a_.bars, "rt"))["bars"]["SPY"]
        c_ = np.array([b[4] for b in sb], float)
        SPY = types.SimpleNamespace(st=types.SimpleNamespace(dates=[b[0] for b in sb], c=c_), e21=launch.ema(c_, 21), e50=launch.ema(c_, 50),
                                    s200=np.array([c_[max(0, k - 199):k + 1].mean() for k in range(c_.size)]))
    with multiprocessing.get_context("fork").Pool(os.cpu_count() or 2) as pool:
        ts = [t for r in pool.map(one, keys, chunksize=8) for t in r]
    # one buy point per stock, day and kind: the newest launch's (the Launches tab follows only a stock's newest launch;
    # the run before this counted 440 of 5,816 twice, AEHR Feb 11 and Mar 31 2026 both reading Apr 2)
    best = {}
    for t in ts:
        k_ = (t["symbol"], t["date"], t["buy_point"], t["bought"])
        if k_ not in best or t["launch_date"] > best[k_]["launch_date"]:
            best[k_] = t
    ts = sorted(best.values(), key=lambda t: (t["date"], t["symbol"]))
    # 2) the same buy point bought at that day's close, the risk the day's low (your management)
    for t in ts:
        a = A[t["symbol"]]
        j = a.st.dates.index(t["date"])
        cb, cl = float(a.st.c[j]), float(a.st.l[j])
        if cb > cl and t.get("engine_confirmed", 1):      # a level buy only when the day closed as that breakout
            t.update(mgmt.cols(manage(a, j, cb, cl, None, 21), "close_"))
            t.update(mgmt.cols(manage(a, j, cb, cl, None, 10), "close_", "_10"))
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
                # the bot's level entry (Nov 2 2026): a buy-stop at the level, filled the first 5-minute bar that trades over it,
                # at the level (or that bar's open when it opens over it); the stop under the day's low so far (the bars before the
                # fill); then your management on the 5-minute bars that day and daily after. A level crossed in the first 5 minutes
                # has no low yet: flagged lvl_first5 (the 5-minute ORH entry covers it)
                if t.get("level") and t["bought"] in ("level", "open"):
                    lv = t["level"]
                    m0 = next((x for x in range(len(b)) if b[x]["h"] > lv), None)
                    if m0 == 0:
                        t["lvl_first5"] = 1
                    elif m0 is not None:
                        a_l = A[t["symbol"]]
                        buyL, stopL = max(lv, b[m0]["o"]), min(x["l"] for x in b[:m0]) - 0.01
                        if buyL > stopL:
                            t["lvl_first5"], t["lvl_minute"] = 0, 5 * m0
                            for runner, suf in ((21, ""), (10, "_10")):
                                x = mgmt.run(a_l, k, buyL, stopL, bars=b[m0:], runner=runner)
                                t.update(mgmt.cols(x, "lvl_", suf))
                                y = mgmt.sold_at_close(x, a_l, k, buyL, x["risk"], "sold at the close: back under the buy point") \
                                    if a_l.st.c[k] <= lv else x
                                t.update(mgmt.cols(y, "lvlcx_", suf))
                lvl = max(b[0]["h"], t["level"] or 0)
                m = next((x for x in range(1, len(b)) if b[x]["h"] > lvl), None)
                if m is None:
                    continue
                buy5 = max(lvl, b[m]["o"])
                a_s = A[t["symbol"]]
                for runner, suf in ((21, ""), (10, "_10")):
                    x = pb.trade(a_s, k, b, -1e9, {}, entry=(m, buy5), runner=runner)
                    if not (x and x.get("broke")):
                        continue
                    t["min5_bought"] = 1
                    t.update(mgmt.cols(x, "min5_", suf))
                    # the 5-minute buy of a level buy point, sold at the close when that day closes back under the buy point
                    if t["level"]:
                        y = mgmt.sold_at_close(x, a_s, k, buy5, x["risk"], "sold at the close: back under the buy point") \
                            if a_s.st.c[k] <= t["level"] else x
                        t.update(mgmt.cols(y, "min5cx_", suf))
    kinds = [nm for _, nm in LEVEL] + [k for k, _, _ in KINDS]
    out = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), first=cal[200], last=cal[-1], launches=len(keys),
               all=summ(ts), by_buy_point={k: summ([t for t in ts if t["buy_point"] == k]) for k in kinds},
               by_rvol={nm: summ([t for t in ts if lo <= t["rvol_day"] < hi]) for nm, lo, hi in RV},
               by_gap={nm: summ([t for t in ts if lo <= t["gap_pct"] < hi]) for nm, lo, hi in GAP},
               by_entry={m: {k: summ([dict(t, R=t[m + "R"], win=t[m + "win"], result_pct=t[m + "result_pct"], reached_2ADR=t[m + "reached_2ADR"],
                                             reached_5ADR=t[m + "reached_5ADR"], risk_pct=t[m + "risk_pct"]) for t in ts if (k == "all" or t["buy_point"] == k) and m + "R" in t])
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
