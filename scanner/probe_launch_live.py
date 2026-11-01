#!/usr/bin/env python3
"""Launch days without hindsight (Nov 1 2026): the opening range trade on every stock that looked like a launch at the
moment of the buy, whether or not the day closed as a launch.

  python3 scanner/probe_launch_live.py --bars BARS.json.gz --stocks radar-data/stocks.json --volprofile radar-data/volprofile.json --out OUT.json
  (needs ALPACA_KEY_ID / ALPACA_SECRET: the 5-minute bars)

  the night before  on the launch watch list: liquid ($10+, $20M+ and 600K+ shares a day, ADR 3.5%+), from 25% under the
                    200 SMA to 28% over it (50% when it gaps 8%+, a power day's room), no launch in the last 20 sessions
                    (the price over the 200 SMA and 30%+ over the 52-week low at the buy)
  the day           it gaps up; the buy = the first 5-minute bar trading over both the 5-minute opening range high and
                    5% over the day before's close (the live "Launching today" needs +5%): at the higher of the two (or
                    the bar's open when it jumps over them); the risk = the opening range low
  volume            "pace": the volume from 9:30 to that bar's end / the stock's usual volume by then (its 20-day
                    average x its own intraday volume curve, radar-data volprofile.json); the live check needs 1.5x+
  managed           your management (scanner/mgmt.py): 1/3 at +2 ADR, 1/3 at +5 ADR, then breakeven; the runners out on a
                    daily close under the 21 EMA (columns without a suffix) or the 10 EMA (_10)
Days whose high never reached +5% are left out before the 5-minute bars are read (no buy was possible on them).
"""
import argparse, collections, datetime, json, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402
import probe_catalyst as pc  # noqa: E402
import probe_pb1h as pb  # noqa: E402
import mgmt  # noqa: E402

L = launch.L


def cx_launch(t, A):
    """the same 5-minute buy, sold at the close of the day when it didn't close as a launch (you know at 4 PM)"""
    a = A[t["sym"]]
    k = a.st.dates.index(t["date"])
    out = {}
    for x, suf in ((t, ""), (t["x10"], "_10")):
        y = mgmt.sold_at_close(x, a, k, t["buy"], x["risk"], "sold at the close: not a launch") if t["closed_as"] == "not a launch" else x
        out.update(mgmt.cols(y, "cx_", suf))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--volprofile", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    first = 200
    L["catalyst_launch"] = 0
    launch.CATALYST_DAYS.clear()
    launched = collections.defaultdict(set)                 # the days that closed as launches (regular, power, reversal)
    for s, i, k, gs, gn in launch.detect(A, groups, GS, cal, S):
        launched[s].add(i)
    curve = {}
    for s, row in json.load(open(a_.volprofile)).get("rows", {}).items():
        if row and row[-1]:
            curve[s] = np.array(row, dtype=float) / float(row[-1])   # the share of a day's volume by each minute
    cand = []
    for s, a in A.items():
        st = a.st
        c, h, o, v = st.c, st.h, st.o, st.v
        av20 = launch.roll_mean(v, 20)
        for k in range(max(a.start, first) + 1, c.size):
            j = k - 1
            if not (a.liquid[j] and o[k] > c[j] and h[k] >= 1.05 * c[j] and h[k] > a.s200[j]):
                continue
            ext = 100 * (c[j] / a.s200[j] - 1)                  # the day before: up to 25% under the 200 SMA (an A+ "go day")
            if ext < -L["watch_under200"] or ext > (L["power_ext200"] if a.gap[k] >= L["power_gap"] else L["max_ext200"]):
                continue
            if any(k - L["dedupe_days"] < x < k for x in launched[s]):
                continue
            cand.append((s, k, float(av20[j])))
    print(len(cand), "candidate days")
    by_day = collections.defaultdict(list)
    for s, k, av in cand:
        by_day[A[s].st.dates[k]].append((s, k, av))
    tm = []
    for d, ks in sorted(by_day.items()):
        t0 = datetime.datetime.fromisoformat(d + "T09:30").replace(tzinfo=pc.NY)
        b5 = pb.bars(sorted({s for s, k, av in ks}), t0, t0 + datetime.timedelta(minutes=390), "5Min")
        for s, k, av in ks:
            b = b5.get(pc.alp(s))
            if not b or not b[0]["t"].startswith(pc.iso(t0)[:16]):
                continue
            a = A[s]
            st = a.st
            prev = float(st.c[k - 1])
            lvl = max(b[0]["h"], 1.05 * prev)
            m = next((x for x in range(1, len(b)) if b[x]["h"] > lvl), None)
            if m is None:
                continue
            lvl = max(lvl, float(a.s200[k - 1]) * 1.0001)          # over the 200 SMA at the buy
            m = next((x for x in range(1, len(b)) if b[x]["h"] > lvl), None)
            if m is None:
                continue
            buy = max(lvl, b[m]["o"])
            if buy < st.low52[k - 1] * 1.3:
                continue
            tt = datetime.datetime.fromisoformat(b[m]["t"].replace("Z", "+00:00")).astimezone(pc.NY)
            mins = min(389, tt.hour * 60 + tt.minute + 5 - 570 - 1)
            cv = sum(x["v"] for x in b[:m + 1])
            frac = curve[s][mins] if s in curve and len(curve[s]) > mins else (mins + 1) / 390
            pace = cv / (av * frac) if av and frac else None
            t = pb.trade(a, k, b, -1e9, {}, entry=(m, buy))
            t10 = pb.trade(a, k, b, -1e9, {}, entry=(m, buy), runner=10)
            if t is None or not t.get("broke"):
                continue
            t["buy"], t["x10"] = float(buy), t10
            t.update(sym=s, date=d, pace=pace, minutes=mins + 1, gap=float(a.gap[k]), under200=bool(st.c[k - 1] < a.s200[k - 1]),
                     rvol_day=float(a.rv[k]), chg_day=float(a.chg[k]), ext200_prev=float(a.ext200_prev[k]), adr=float(st.adr[k - 1]),
                     grade=launch.grade(a, k),
                     closed_as=("power day" if a.power(k) else "reversal day" if a.reversal(k) else "regular") if k in launched[s] else "not a launch")
            tm.append(t)
    vol = [t for t in tm if (t["pace"] or 0) >= 1.5]
    out = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), first=cal[first], last=cal[-1],
               candidate_days=len(cand),
               all=pb.summ(tm), volume_pace_1_5x=pb.summ(vol), volume_pace_under_1_5x=pb.summ([t for t in tm if (t["pace"] or 0) < 1.5]),
               closed_as={k: pb.summ([t for t in vol if t["closed_as"] == k]) for k in ("regular", "power day", "not a launch")},
               closed_as_all_trades={k: pb.summ([t for t in tm if t["closed_as"] == k]) for k in ("regular", "power day", "reversal day", "not a launch")},
               from_under_the_200sma={k: pb.summ([t for t in tm if f(t)]) for k, f in (("under the 200 SMA the day before", lambda t: t["under200"]),
                                                                                      ("over it the day before", lambda t: not t["under200"]))},
               by_gap_all_trades={k: pb.summ([t for t in tm if f(t["gap"])]) for k, f in (("gap under 2%", lambda g: g < 2), ("gap 2-5%", lambda g: 2 <= g < 5),
                                                                                         ("gap 5-8%", lambda g: 5 <= g < 8), ("gap 8%+", lambda g: g >= 8))},
               by_time_all_trades={k: pb.summ([t for t in tm if f(t["minutes"])]) for k, f in (("bought by 10:00", lambda x: x <= 30), ("10:00-11:00", lambda x: 30 < x <= 90),
                                                                                              ("after 11:00", lambda x: x > 90))},
               by_gap={k: pb.summ([t for t in vol if f(t["gap"])]) for k, f in (("gap under 2%", lambda g: g < 2), ("gap 2-5%", lambda g: 2 <= g < 5),
                                                                               ("gap 5-8%", lambda g: 5 <= g < 8), ("gap 8%+", lambda g: g >= 8))},
               by_time={k: pb.summ([t for t in vol if f(t["minutes"])]) for k, f in (("bought by 10:00", lambda x: x <= 30), ("10:00-11:00", lambda x: 30 < x <= 90),
                                                                                    ("after 11:00", lambda x: x > 90))},
               by_pace={k: pb.summ([t for t in tm if f(t["pace"] or 0)]) for k, f in (("pace 1.5-3x", lambda x: 1.5 <= x < 3), ("pace 3-6x", lambda x: 3 <= x < 6),
                                                                                    ("pace 6x+", lambda x: x >= 6))})
    # every trade, for the spreadsheet's own filters (RVOL, gap...)
    out["trades"] = [dict(date=t["date"], symbol=t["sym"], closed_as=t["closed_as"], grade_if_launch=t["grade"],
                          gap_pct=round(t["gap"], 2), day_change_pct=round(t["chg_day"], 2), rvol_day=round(t["rvol_day"], 2),
                          rvol_pace_at_buy=round(t["pace"], 2) if t["pace"] else None, buy_minutes_after_open=t["minutes"],
                          from_under_200sma=t["under200"], vs_200sma_day_before_pct=round(t["ext200_prev"], 1), adr_pct=round(t["adr"], 2),
                          days_held=t["days"], **mgmt.cols(t), **mgmt.cols(t["x10"], suf="_10"), **cx_launch(t, A))
                     for t in tm]
    json.dump(out, open(a_.out, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        json.dump(dict(error=traceback.format_exc()[-3000:]), open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
        raise
