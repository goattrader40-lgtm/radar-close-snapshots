#!/usr/bin/env python3
"""Gap out of base (Zanger / Qullamaggie, the user's rules, Nov 1 2026).

  python3 scanner/probe_gapbase.py --bars BARS.json.gz --stocks radar-data/stocks.json --volprofile radar-data/volprofile.json --out OUT.json
  (needs ALPACA_KEY_ID / ALPACA_SECRET: the 1-minute bars)

  the setup     a Launches stock (the 60 sessions after its launch, until 2 closes under the 50 EMA) that closed in its base
                yesterday, under its base high (the base top or an MSF pattern's pivot: ascending triangle, flat base, cup...;
                not a flag line, not a pop), and opens today ABOVE that base high
  the entry     1-minute: over the first 1-minute bar's high, the stop its low; 5-minute: over the first 5-minute bar's high,
                the stop its low; RVOL at the buy 1x+ (the volume from 9:30 / the stock's usual volume by that minute: its
                20-day average x its intraday curve, radar-data volprofile.json)
  two exits     "out if RVOL < 2x at 20 min": at 9:50, if the RVOL isn't 2x, out at that price whatever the trade (a buy
                after 9:50 only with RVOL 2x+ at 9:50); "hold": no volume exit
  then          your management (scanner/probe_pb1h.py trade on the 1-minute or 5-minute bars, then daily): +2R breakeven,
                1/3 at +3R, 1/3 at +5R, the runners out on a daily close under the 21 EMA or at breakeven
"""
import argparse, collections, datetime, json, multiprocessing, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402

L = launch.L
A = {}
GROUPS, GS, POS = {}, {}, {}


def one(key):
    """the gap-out-of-base days of one launch's follow"""
    s, i0 = key
    a = A[s]
    st = a.st
    c, o = st.c, st.o
    out, prev = [], None
    for j in range(i0 + 1, min(c.size, i0 + 61)):
        f = launch.follow(a, i0, j)
        if f["lost_50ema"]:
            break
        if prev:
            top, pat = prev.get("buy_point"), prev.get("pattern") or ""
            if top and not pat.startswith(("Flag", "Pop")) and c[j - 1] <= top < o[j]:
                gs = launch.best_group(s, POS[st.dates[j]], GROUPS, GS)[0] if st.dates[j] in POS else -1
                pbo, pvb = prev.get("breakouts") or 0, prev.get("vol_build") or 0
                early, lead, build = pbo < 2 and (j - i0) < 50, gs == 2, pvb >= 1.1
                out.append(dict(symbol=s, j=j, date=st.dates[j], base_high=round(float(top), 2), pattern=pat, launch_date=st.dates[i0],
                                launch_grade=launch.grade(a, i0), sessions_since_launch=j - i0, leg=prev.get("leg"),
                                gap_pct=round(float(a.gap[j]), 2), gap_over_base_high_pct=round(100 * float(o[j] / top - 1), 2),
                                rvol_day=round(float(a.rv[j]), 2), adr_pct=round(float(st.adr[j - 1]), 2),
                                theme_status={2: "Leading", 1: "Turning up", 0: "Not trending"}.get(gs, "no theme"),
                                breakout_grade="A" if early and lead and build else "B" if early and (lead or build) else "C",
                                volume_building_5d=pvb, tight_days_before=prev.get("tight_days") or 0))
        prev = f
    return out


def five(b1):
    """5-minute bars from 1-minute bars (9:30-9:35 ...)"""
    out = {}
    for x in b1:
        t = datetime.datetime.fromisoformat(x["t"].replace("Z", "+00:00"))
        key = t.replace(minute=t.minute - t.minute % 5, second=0)
        if key in out:
            y = out[key]
            y.update(h=max(y["h"], x["h"]), l=min(y["l"], x["l"]), c=x["c"], v=y["v"] + x["v"])
        else:
            out[key] = dict(t=x["t"][:14] + f"{key.minute:02d}:00Z", o=x["o"], h=x["h"], l=x["l"], c=x["c"], v=x["v"])
    return [out[k] for k in sorted(out)]


def mins_of(x, NY):
    t = datetime.datetime.fromisoformat(x["t"].replace("Z", "+00:00")).astimezone(NY)
    return t.hour * 60 + t.minute - 570


def main():
    global A, GROUPS, GS, POS
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--volprofile", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    A, GROUPS, GS, cal, S = launch.load(a_.bars, a_.stocks)
    POS = {d: k for k, d in enumerate(cal)}
    L["catalyst_launch"] = 0
    launch.CATALYST_DAYS.clear()
    keys = sorted({(s, i) for s, i, k, gs, gn in launch.detect(A, GROUPS, GS, cal, S) if i >= 200})
    with multiprocessing.get_context("fork").Pool(os.cpu_count() or 2) as pool:
        cands = [t for r in pool.map(one, keys, chunksize=8) for t in r]
    seen, uniq = set(), []
    for t in cands:                                         # a day once (two launches of a stock can share it)
        if (t["symbol"], t["date"]) not in seen:
            seen.add((t["symbol"], t["date"]))
            uniq.append(t)
    print(len(uniq), "gap-out-of-base days")
    import probe_catalyst as pc
    import probe_pb1h as pb
    curve = {}
    for s, row in json.load(open(a_.volprofile)).get("rows", {}).items():
        if row and row[-1]:
            curve[s] = np.array(row, dtype=float) / float(row[-1])
    by_day = collections.defaultdict(list)
    for t in uniq:
        by_day[t["date"]].append(t)
    rows = []
    for d, ts in sorted(by_day.items()):
        t0 = datetime.datetime.fromisoformat(d + "T09:30").replace(tzinfo=pc.NY)
        b1s = pb.bars(sorted({t["symbol"] for t in ts}), t0, t0 + datetime.timedelta(minutes=390), "1Min")
        for t in ts:
            b1 = b1s.get(pc.alp(t["symbol"]))
            if not b1 or not b1[0]["t"].startswith(pc.iso(t0)[:16]):
                continue
            a = A[t["symbol"]]
            j = t["j"]
            av = float(launch.roll_mean(a.st.v, 20)[j - 1])
            cv_ = curve.get(t["symbol"])

            def pace(b, n):                                 # RVOL from 9:30 to the end of bar n
                m_ = min(389, mins_of(b[n], pc.NY) + (5 if b is not b1 else 1) - 1)
                frac = cv_[m_] if cv_ is not None and len(cv_) > m_ else (m_ + 1) / 390
                return sum(x["v"] for x in b[:n + 1]) / (av * frac) if av and frac else None
            for orb, b in (("1-min", b1), ("5-min", five(b1))):
                orh, orl = b[0]["h"], b[0]["l"]
                m = next((x for x in range(1, len(b)) if b[x]["h"] > orh), None)
                if m is None:
                    continue
                p_buy = pace(b, m)
                if not p_buy or p_buy < 1:
                    continue                                # RVOL under 1x at the buy: no trade
                buy = max(orh, b[m]["o"])
                hold = pb.trade(a, j, b, -1e9, {}, entry=(m, buy))
                if not hold or not hold.get("broke"):
                    continue
                # the 9:50 check: RVOL 2x by 20 minutes, else out at that price (if still in)
                e = next((x for x in range(len(b)) if mins_of(b[x], pc.NY) + (5 if orb == "5-min" else 1) >= 20), None)
                p20 = pace(b, e) if e is not None else None
                R = buy - orl
                if mins_of(b[m], pc.NY) >= 20:
                    rv_out = None if (p20 or 0) >= 2 else "skip"     # bought after 9:50: only with RVOL 2x+ by then
                else:
                    rv_out = None if (p20 or 0) >= 2 else "out"
                res_rv = None
                if rv_out == "out":
                    stop, got, left, be = orl, 0.0, 1.0, False
                    for n in range(m, e + 1):
                        x = b[n]
                        if x["l"] <= stop:
                            res_rv = (got + left * min(stop, x["o"] if n > m else buy), "stop before 9:50"); break
                        if x["h"] >= buy + 3 * R and left > 0.67:
                            got += (buy + 3 * R) / 3; left -= 1 / 3
                        if x["h"] >= buy + 2 * R:
                            stop, be = max(stop, buy), True
                    if res_rv is None:
                        res_rv = (got + left * b[e]["c"], "out at 9:50: RVOL under 2x")
                base = {k: v for k, v in t.items() if k != "j"}
                base.update(rvol_at_buy=round(p_buy, 2), rvol_at_20min=round(p20, 2) if p20 else None,
                            buy_minutes_after_open=mins_of(b[m], pc.NY) + (5 if orb == "5-min" else 1))
                for var, res in (("hold", None), ("out if RVOL < 2x at 20 min", res_rv if rv_out == "out" else None)):
                    if var != "hold" and rv_out == "skip":
                        continue
                    if res:
                        ret, Rr, how, r3 = 100 * (res[0] / buy - 1), (res[0] - buy) / R, res[1], 0
                    else:
                        ret, Rr, how, r3 = float(hold["ret"]), float(hold["R"]), hold["how"], int(hold["r3"])
                    rows.append(dict(base, **{"entry tactic": f"{orb} ORB, {var}", "stop": f"{orb} low", "risk_pct": round(100 * R / buy, 2),
                                              "result_pct": round(ret, 2), "R": round(Rr, 2), "win": int(ret > 0), "reached_3R": r3, "exit": how}))
    def summ(rs):
        if not rs:
            return dict(trades=0)
        R_ = np.array([r["R"] for r in rs])
        return dict(trades=len(rs), win=round(100 * float(np.mean([r["win"] for r in rs]))), avg_pct=round(float(np.mean([r["result_pct"] for r in rs])), 2),
                    avg_R=round(float(R_.mean()), 2), med_R=round(float(np.median(R_)), 2), total_R=round(float(R_.sum()), 1),
                    risk_med_pct=round(float(np.median([r["risk_pct"] for r in rs])), 2))
    tac = sorted({r["entry tactic"] for r in rows})
    out = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), first=cal[200], last=cal[-1],
               gap_out_of_base_days=len(uniq), by_tactic={k: summ([r for r in rows if r["entry tactic"] == k]) for k in tac},
               trades=rows)
    json.dump(out, open(a_.out, "w"))
    print(json.dumps({k: v for k, v in out.items() if k != "trades"}, indent=1))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        json.dump(dict(error=traceback.format_exc()[-3000:]), open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
        raise
