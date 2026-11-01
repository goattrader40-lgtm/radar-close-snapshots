#!/usr/bin/env python3
"""The deep analysis of every test's trades (Nov 1 2026): which strategy, entry, exit, runner and filters would have worked.

  git fetch -q origin +refs/heads/radar-data:refs/remotes/origin/radar-data
  python3 tools/analyze.py            # prints the findings, saves tools/analysis.json (tools/test_results.py puts them in the spreadsheet)

Honest rules, so a lucky combination doesn't look like an edge:
  - only what's known when the trade is taken: a filter known at the close (the day's RVOL, how the day closed, the closing
    tags) is used only for close buys and the sell-at-the-close exits
  - R with the risk floored at 1% (a tiny stop can't make a trade +40R) and 0.15% taken off every trade for slippage and costs
  - every combination split into two halves of the period (before / after the middle date): kept only when it made money in
    both, with enough trades in each; the t-value says how far from luck the average is (2+ = unlikely to be luck)
  - how much of the result the best 5% of trades made (without them, is it still positive?)
  - trades a month and the positions open at the same time (the capital it needs)
"""
import collections, datetime, itertools, json, math, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import test_results as tr  # noqa: E402

COST, FLOOR = 0.15, 1.0
MIN_N, MIN_HALF = 40, 15


def data(name):
    return tr.data(name)


def band(x, cuts, unit=""):
    if x is None:
        return None
    for lo, hi in cuts:
        if (lo is None or x >= lo) and (hi is None or x < hi):
            return f"under {hi}{unit}" if lo is None else f"{lo}{unit}+" if hi is None else f"{lo}-{hi}{unit}"
    return None


RVB = ((None, 1), (1, 1.5), (1.5, 2), (2, 3), (3, None))
GAPB = ((None, 0), (0, 2), (2, 5), (5, 8), (8, None))
ADRB = ((None, 4), (4, 5), (5, 7), (7, None))
DVB = ((20, 50), (50, 100), (100, None))


def prep(rows, kind):
    """adds the bands and the net R; tags each filter as known at the buy or only at the close"""
    out = []
    for r in rows:
        if r.get("R") is None or r.get("result_pct") is None or r.get("risk_pct") is None:
            continue
        if r.get("dollar_vol_20d_m") is not None and r["dollar_vol_20d_m"] < tr.MIN_DV:
            continue                                    # under your $20M a day minimum
        x = dict(r)
        net = r["result_pct"] - COST
        x["net_pct"] = net
        x["Rn"] = net / max(r["risk_pct"], FLOOR)
        x["gap"] = band(r.get("gap_pct"), GAPB, "%")
        x["$vol"] = band(r.get("dollar_vol_20d_m"), DVB, "M")
        x["ADR"] = band(r.get("adr_pct"), ADRB, "%")
        x["risk<=0.7ADR"] = "yes" if (r.get("risk_pct") or 99) <= 0.7 * (r.get("adr_pct") or 0.01) else "no"
        x["RVOL day"] = band(r.get("rvol_day"), RVB, "x")
        if kind == "launch":
            x["RVOL at buy"] = band(r.get("rvol_pace_at_buy"), RVB, "x")
            m = r.get("buy_minutes_after_open")
            x["buy time"] = None if m is None else "by 10:00" if m <= 30 else "10-11" if m <= 90 else "after 11"
            x["from under 200 SMA"] = "yes" if r.get("from_under_200sma") else "no"
        if kind == "gapbase":
            x["RVOL at buy"] = band(r.get("rvol_at_buy"), RVB, "x")
            x["RVOL at 9:50"] = band(r.get("rvol_at_20min"), RVB, "x")
            x["gap over base"] = band(r.get("gap_over_base_high_pct"), ((None, 1), (1, 3), (3, 6), (6, None)), "%")
        if kind == "buypoint":
            x["tight days before"] = "2+" if (r.get("tight_days_before") or 0) >= 2 else "0-1"
            vb = r.get("volume_building_5d")
            x["volume building"] = None if vb is None else "yes (1.1x+)" if vb >= 1.1 else "no"
            ss = r.get("sessions_since_launch")
            x["days since launch"] = None if ss is None else "1-10" if ss <= 10 else "11-30" if ss <= 30 else "31-60"
        out.append(x)
    return out


# the filters: known at the buy / known only at the close
AT_BUY = {"launch": ["gap", "RVOL at buy", "$vol", "ADR", "risk<=0.7ADR", "buy time", "from under 200 SMA"],
          "buypoint": ["gap", "$vol", "ADR", "risk<=0.7ADR", "theme_status", "breakout_grade", "early_breakout", "tight days before",
                       "volume building", "days since launch", "launch_grade"],
          "gapbase": ["RVOL at buy", "gap over base", "$vol", "ADR", "risk<=0.7ADR", "theme_status", "breakout_grade", "pattern"]}
AT_CLOSE = {"launch": ["RVOL day", "grade_if_launch"],
            "buypoint": ["RVOL day", "day_closed", "caution_within_0_5pct", "double_breakout", "third_try", "flag_volume_dried", "retest_with"],
            "gapbase": ["RVOL at 9:50", "RVOL day"]}


def realism(strategy, tactic):
    """fair = the trigger and the stop are known when the trade is taken; upper limit = an intraday buy with the day's-low
    stop (the low is only known at the close: no stop on the buy day, the size from later); hindsight = a push bought
    during the day (a push day is only known at its close)"""
    t = tactic or ""
    if strategy.endswith(": push") and ("alert" in t or "5-min" in t):
        return "hindsight"
    if "(the engine's breakout days)" in strategy and t != "buy at the close":
        return "hindsight"                          # bought during the day, but only days known at the close to be breakouts
    if t.startswith("as the alert fires"):
        return "upper limit"
    return "fair"


def stats(rs, mid):
    n = len(rs)
    if not n:
        return None
    R = [r["Rn"] for r in rs]
    m = sum(R) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in R) / (n - 1)) if n > 1 else 0
    h1 = [r["Rn"] for r in rs if r["date"] < mid]
    h2 = [r["Rn"] for r in rs if r["date"] >= mid]
    top = sorted(R, reverse=True)
    cut = max(1, n // 20)
    gains, losses = sum(x for x in R if x > 0), -sum(x for x in R if x < 0)
    months = len({r["date"][:7] for r in rs}) or 1
    return dict(n=n, win=round(100 * sum(1 for r in rs if r["net_pct"] > 0) / n), avg_pct=round(sum(r["net_pct"] for r in rs) / n, 2),
                avgR=round(m, 3), t=round(m / (sd / math.sqrt(n)), 2) if sd else 0, totalR=round(sum(R), 1),
                pf=round(gains / losses, 2) if losses else None, half1=(len(h1), round(sum(h1) / len(h1), 3) if h1 else None),
                half2=(len(h2), round(sum(h2) / len(h2), 3) if h2 else None),
                avgR_without_top5pct=round(sum(top[cut:]) / (n - cut), 3) if n > cut else None, per_month=round(n / months, 1))


def concurrency(rs):
    """the most and the average positions open at once (entry day to exit day, trading days approximated by calendar)"""
    ev = collections.Counter()
    for r in rs:
        d0 = datetime.date.fromisoformat(r["date"])
        for k in range(int(r.get("days_held") or 0) + 1):
            ev[d0 + datetime.timedelta(days=round(k * 7 / 5))] += 1
    return (max(ev.values()), round(sum(ev.values()) / len(ev), 1)) if ev else (0, 0)


def robust(s):
    return (s and s["n"] >= MIN_N and s["half1"][0] >= MIN_HALF and s["half2"][0] >= MIN_HALF
            and (s["half1"][1] or 0) > 0 and (s["half2"][1] or 0) > 0 and s["avgR"] > 0)


def scan(rows, kind, strategy, mid):
    """every tactic x runner, alone and with 1 or 2 filters"""
    out = []
    groups = collections.defaultdict(list)
    for r in rows:
        groups[(r.get("entry tactic"), r.get("runners"))].append(r)
    for (tac, run), rs in groups.items():
        # a filter known only at the close can pick trades only for a buy AT the close; an intraday buy can't be chosen by
        # what the day did after it (a sell-at-the-close exit uses the close to get out, not to choose the trade)
        close_known = (tac or "") == "buy at the close"
        dims = AT_BUY[kind] + (AT_CLOSE[kind] if close_known else [])
        base = stats(rs, mid)
        real = realism(strategy, tac)
        out.append(dict(strategy=strategy, tactic=tac, runners=run, filters="(none)", realism=real, **base))
        for d in dims:
            for v in sorted({r.get(d) for r in rs if r.get(d) is not None}, key=str):
                sel = [r for r in rs if r.get(d) == v]
                s = stats(sel, mid)
                if s and s["n"] >= MIN_N:
                    out.append(dict(strategy=strategy, tactic=tac, runners=run, filters=f"{d} = {v}", realism=real, **s))
        for d1, d2 in itertools.combinations(dims, 2):
            vals = collections.defaultdict(list)
            for r in rs:
                if r.get(d1) is not None and r.get(d2) is not None:
                    vals[(r[d1], r[d2])].append(r)
            for (v1, v2), sel in vals.items():
                if len(sel) >= MIN_N:
                    s = stats(sel, mid)
                    out.append(dict(strategy=strategy, tactic=tac, runners=run, filters=f"{d1} = {v1} & {d2} = {v2}", realism=real, **s))
    return out


def main():
    sets = []
    d = data("probe_launch_live")
    if d and d.get("trades"):
        sets.append(("Launch day (fair)", "launch", tr.long_rows(d["trades"], tr.TACTICS["launchlive"])))
    d = data("probe_launch_orh")
    if d and d.get("trades"):
        lr = [r for r in tr.long_rows(d["trades"], tr.TACTICS["launch"]) if r["entry tactic"] == "buy at the close"]
        sets.append(("Launch day, bought at the close", "launch", lr))
    d = data("probe_buypoints")
    if d and d.get("trades"):
        br = tr.long_rows(d["trades"], tr.TACTICS["buypoint"])
        for k in sorted({r["buy_point"] for r in br}):
            sel = [r for r in br if r["buy_point"] == k]
            if any(r.get("bought") == "level" for r in sel):
                # a level buy point: every cross bought during the day (you can't know the close yet), and the engine's own
                # breakout days bought at their close (the user, Nov 1 2026: the trigger sheets must match the engine)
                sets.append((f"Buy point: {k} (every cross, bought during the day)", "buypoint", [r for r in sel if r["entry tactic"] != "buy at the close"]))
                sets.append((f"Buy point: {k} (the engine's breakout days)", "buypoint", [r for r in sel if r.get("engine_confirmed", 1)]))
            else:
                sets.append((f"Buy point: {k}", "buypoint", sel))
    d = data("probe_gapretest")
    if d and d.get("trades"):
        gq = tr.long_rows(d["trades"], tr.TACTICS["gapretest"])
        sets.append(("Gap retest, holding the 10 / 21 EMA", "buypoint", [r for r in gq if r.get("retest_with") != "no EMA"]))
        sets.append(("Gap retest, all", "buypoint", gq))
    d = data("probe_gapbase")
    if d and d.get("trades"):
        sets.append(("Gap out of base", "gapbase", tr.with_risk_adr(d["trades"])))
    alld = sorted(r["date"] for _, _, rs in sets for r in rs)
    mid = alld[len(alld) // 2] if alld else "2026-03-01"
    res, best = [], []
    for name, kind, rs in sets:
        rows = prep(rs, kind)
        found = scan(rows, kind, name, mid)
        res += found
        for f in found:
            f["robust"] = bool(robust(f))
    # the strongest robust combinations, by the net R per trade x how far it is from luck
    keep = [f for f in res if f["robust"] and f["realism"] == "fair" and f["t"] >= 2]
    keep.sort(key=lambda f: (-(f["avgR"] * min(f["t"], 4)), -f["n"]))
    seen = set()
    for f in keep:
        key = (f["strategy"], f["filters"])
        if key in seen:
            continue
        seen.add(key)
        best.append(f)
    # the capital each of the best needs: positions open at once
    allrows = {name: prep(rs, kind) for name, kind, rs in sets}
    for f in best[:40]:
        sel = [r for r in allrows[f["strategy"]] if r.get("entry tactic") == f["tactic"] and r.get("runners") == f["runners"]
               and all(str(r.get(c.split(" = ")[0])) == c.split(" = ")[1] for c in f["filters"].split(" & ") if " = " in c)]
        f["max_open"], f["avg_open"] = concurrency(sel)
    base = [f for f in res if f["filters"] == "(none)"]
    out = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), middle_date=mid, cost_pct=COST,
               risk_floor_pct=FLOOR, min_trades=MIN_N, baseline=base, best=best[:60], all=res)
    json.dump({k: v for k, v in out.items() if k != "all"}, open(os.path.join(ROOT, "tools", "analysis.json"), "w"), indent=1)
    print("middle date", mid)
    print("\nBASELINES (no filter), net R per trade:")
    for f in sorted(base, key=lambda f: (f["realism"] != "fair", -f["avgR"])):
        print(f"  {f['realism'][:11]:11} | {f['strategy'][:34]:34} | {f['tactic'][:46]:46} | {f['runners']:12} | n {f['n']:5} win {f['win']:3}% avg {f['avg_pct']:+.2f}% "
              f"avgR {f['avgR']:+.3f} t {f['t']:+.1f} halves {f['half1'][1]} / {f['half2'][1]} no-top5% {f['avgR_without_top5pct']}")
    print("\nBEST ROBUST COMBINATIONS (fair only, positive in both halves, t 2+):")
    for f in best[:30]:
        print(f"  {f['strategy'][:30]:30} | {f['tactic'][:40]:40} | {f['runners']:12} | {f['filters'][:60]:60} | n {f['n']:4} "
              f"win {f['win']:3}% avgR {f['avgR']:+.3f} t {f['t']:+.1f} h {f['half1'][1]}/{f['half2'][1]} no-top {f['avgR_without_top5pct']} "
              f"/mo {f['per_month']} open {f.get('max_open')}/{f.get('avg_open')}")


if __name__ == "__main__":
    main()
