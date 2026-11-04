#!/usr/bin/env python3
"""Backtest of the code grader (radar/codegrade.py) on every past gap-up of 5%+ (test/codegrade, Nov 4 2026).

  python3 scanner/probe_codegrade.py --bars BARS.json.gz --stocks stocks.json --out OUT.json [--minutes 42]

Each gap-up of the last ~14 months (2 years of bars; the first 200 sessions build the averages) in the launch universe
(price $10+, 20-day $20M+ and 700K+ shares, market cap $700M+ then, under $2T) is judged as of that morning, the open
standing in for the pre-market price, with the grader's own functions:
  stage     at the last close (codegrade.stage)
  eligible  at the open (codegrade.eligible: the 21-day high = the highest close; at most 100% over the 200; a laggard at
            most 20% under it); variants: no cap over the 200, the launch list's 28% (50% on 8%+ gaps), laggards 30%
            under, the 21-day high by the wicks, no 21-day high in stage 2 / 3
  news      SEC filings accepted from the last close (4 PM) to 9:30 AM (codegrade.classify); an earnings release gets its
            revenue growth and last quarter's from the SEC's XBRL facts and the guidance words from the release (no
            estimates exist this far back, so no beat / miss). Only gaps that can get a grade in some variant are
            looked up (the SEC's 10-a-second limit); the rest are "—" whatever the news, and are scored without it.
Then what happened: held = closed at or over the open; ran 20%+ = a high 20%+ over the open within 20 sessions; broke
the low = under the gap day's low within 5 sessions; r20 = the close 20 sessions on vs the gap-day close; trade = bought
at the open, out under the day's low or on the first close under the 21 EMA (the launch backtest's rule). W laggards:
crossed the 200 within 60 sessions, and how they did from that close.
"""
import argparse, datetime, json, os, sys, time, zoneinfo
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "radar"))
import launch  # noqa: E402
import codegrade as G  # noqa: E402
from earnings import guidance  # noqa: E402

NY = zoneinfo.ZoneInfo("America/New_York")
CONCEPTS = ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet",
            "RevenueFromContractWithCustomerIncludingAssessedTax", "RevenuesNetOfInterestExpense")
GR = ("A+", "A", "B", "W", "C", "F", "—")
_xq = {}


def xbrl_quarters(sym):
    """{quarter end: revenue} from the SEC's XBRL facts; Q4 = the year minus its three quarters"""
    c = G.cik_of(sym)
    if not c:
        return {}
    if c in _xq:
        return _xq[c]
    best = {}
    for con in CONCEPTS:
        try:
            j = G.sec_get(f"https://data.sec.gov/api/xbrl/companyconcept/CIK{c:010d}/us-gaap/{con}.json")
        except Exception:
            continue
        q, fy = {}, {}
        for f in (j.get("units") or {}).get("USD", []):
            if not f.get("start") or not f.get("end"):
                continue
            s, e = datetime.date.fromisoformat(f["start"]), datetime.date.fromisoformat(f["end"])
            days = (e - s).days
            if 80 <= days <= 100:
                q[e] = f["val"]
            elif 350 <= days <= 380:
                fy[(s, e)] = f["val"]
        for (s, e), v in fy.items():
            if e not in q:
                inside = [x for x in q if s < x < e]
                if len(inside) == 3:
                    q[e] = v - sum(q[x] for x in inside)
        if q and (not best or max(q) > max(best)):
            best = q
        if best and max(best) >= datetime.date(2026, 3, 1):
            break
    _xq[c] = best
    return best


def near(q, d, tol=12):
    k = min(q, key=lambda x: abs((x - d).days), default=None)
    return q[k] if k is not None and abs((k - d).days) <= tol else None


def hist_earnings(sym, day, text):
    q = xbrl_quarters(sym)
    e = {"guide": guidance(text, None, None) if text else {"dir": "none"}}
    if not q:
        return e
    d = datetime.date.fromisoformat(day)
    ends = [x for x in q if datetime.timedelta(days=10) <= d - x <= datetime.timedelta(days=120)]
    if not ends:
        return e
    qe = max(ends)
    yr = lambda x: x - datetime.timedelta(days=364)
    pq = qe - datetime.timedelta(days=91)
    v, vy, vp, vpy = q.get(qe), near(q, yr(qe)), near(q, pq), near(q, yr(pq))
    pct = lambda a, b: round((a / b - 1) * 100, 1) if a and b and b > 0 else None
    e.update(rev_growth=pct(v, vy), rev_prev_growth=pct(vp, vpy))
    return e


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(float(np.mean(xs)), 1) if xs else None


def pc(xs):
    xs = [bool(x) for x in xs if x is not None]
    return round(100 * sum(xs) / len(xs)) if xs else None


def stats(rs):
    if not rs:
        return {"n": 0}
    r20 = [r["r20"] for r in rs if r.get("r20") is not None]
    return {"n": len(rs), "held%": pc([r["held"] for r in rs]), "ran20%": pc([r.get("ran20") for r in rs]),
            "broke_low5%": pc([r["broke5"] for r in rs]), "r20_avg": mean(r20), "r20_med": round(float(np.median(r20)), 1) if r20 else None,
            "trade_avg": mean([r.get("trade") for r in rs]), "trade_win%": pc([(r["trade"] > 0) if r.get("trade") is not None else None for r in rs])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--minutes", type=float, default=42)
    a = ap.parse_args()
    t_end = time.time() + 60 * a.minutes
    A, groups, GS, cal, S = launch.load(a.bars, a.stocks)
    mcap = {s["symbol"]: s.get("mcap_b") or 0 for s in json.load(open(a.stocks))}
    pos = {d: k for k, d in enumerate(cal)}
    gstat = {}
    for g, (ms, stt, _, _) in GS.items():
        for s in ms:
            gstat.setdefault(s, []).append(stt)
    # 1. every liquid gap-up of 5%+, its levels at the last close, and what happened after
    ev = []
    for s, ar in A.items():
        st = ar.st
        c, o, h, l = st.c, st.o, st.h, st.l
        n, last = c.size, c[-1]
        for i in range(max(ar.start, 31), n):
            gp = ar.gap[i]
            if not (gp >= 5) or not ar.liq_noadr[i] or not (0.7 <= mcap.get(s, 0) * c[i] / last < 2000):
                continue
            p = i - 1
            px, pcl = float(o[i]), float(c[p])
            lv = dict(px=px, pc=pcl, e21=float(ar.e21[p]), e50=float(ar.e50[p]), s200=float(ar.s200[p]),
                      e21_5=float(ar.e21[p - 5]), e50_5=float(ar.e50[p - 5]), e21_1=float(ar.e21[p - 1]), e50_1=float(ar.e50[p - 1]),
                      hi21=float(c[i - 21:i].max()), hi21w=float(h[i - 21:i].max()), adr=float(st.adr[p]), gap=round(float(gp), 1),
                      lo52=float(l[max(0, i - 252):i].min()))
            if not all(x == x for x in lv.values()):
                continue
            ol = 100 * (px / lv["lo52"] - 1) if lv["lo52"] > 0 else None
            k = pos.get(st.dates[p])
            grp = max((int(x[k]) for x in gstat.get(s, []) if k is not None and k < len(x)), default=0)
            r = dict(sym=s, date=st.dates[i], lv=lv, over_low52=ol, group=grp, mcap=mcap.get(s, 0) * c[i] / last)
            r["held"] = bool(c[i] >= o[i])
            r["ran20"] = bool(h[i:i + 21].max() >= 1.2 * o[i]) if i + 20 < n else None
            r["broke5"] = bool(any(l[j] < l[i] for j in range(i + 1, min(i + 6, n))))
            r["r20"] = round(100 * (c[i + 20] / c[i] - 1), 1) if i + 20 < n else None
            for j in range(i + 1, n):
                if l[j] <= l[i] or c[j] < ar.e21[j]:
                    r["trade"] = round(100 * ((min(l[i], o[j]) if l[j] <= l[i] else c[j]) / o[i] - 1), 1)
                    break
            if px < lv["s200"]:
                j = next((j for j in range(i + 1, min(i + 61, n)) if c[j] > ar.s200[j]), None)
                r["crossed200"] = (j is not None) if (i + 60 < n or j is not None) else None
                if j is not None:
                    r["after_cross"] = dict(r20=round(100 * (c[j + 20] / c[j] - 1), 1) if j + 20 < n else None,
                                            ran20=bool(h[j + 1:j + 21].max() >= 1.2 * c[j]) if j + 20 < n else None,
                                            held5=bool(all(c[m] > ar.s200[m] for m in range(j, min(j + 5, n)))))
            ev.append(r)
    print(len(ev), "gap-ups")
    # 2. the stage and the eligibility, by variant
    V = {"rules": dict(ext=G.MAX_EXT200, under=G.MAX_UNDER200, hi="hi21", hi_in_trend=True),
         "no_cap_over_200": dict(ext=None, under=G.MAX_UNDER200, hi="hi21", hi_in_trend=True),
         "launch_cap_28_50": dict(ext="launch", under=G.MAX_UNDER200, hi="hi21", hi_in_trend=True),
         "laggard_30_under": dict(ext=G.MAX_EXT200, under=30, hi="hi21", hi_in_trend=True),
         "21day_high_by_wicks": dict(ext=G.MAX_EXT200, under=G.MAX_UNDER200, hi="hi21w", hi_in_trend=True),
         "no_high_in_stage2_3": dict(ext=G.MAX_EXT200, under=G.MAX_UNDER200, hi="hi21", hi_in_trend=False)}
    for r in ev:
        L = r["lv"]
        r["v"] = {}
        stg = G.stage(L["pc"], L["e21"], L["e50"], L["s200"], L["e21_5"], L["e50_5"])
        for name, v in V.items():
            hi = L[v["hi"]] if (v["hi_in_trend"] or stg not in (2, 3)) else None
            ext = (50 if L["gap"] >= 8 else 28) if v["ext"] == "launch" else v["ext"]
            ok, why = G.eligible(L["px"], L["pc"], L["e50"], L["s200"], hi, L["adr"], L["gap"], r["over_low52"], ext, v["under"])
            cat = ("" if ok else "too far over the 200" if "over the 200" in why else "too far under the 200" if "under the 200" in why
                   else "ADR under 3.5%" if why.startswith("ADR") else "under 30% over the 52-week low" if "52-week" in why
                   else "under the 50 EMA" if "50 EMA" in why else "under the 21-day high" if "high" in why else why)
            r["v"][name] = dict(stage=stg, ok=ok, why=cat, ev=G.event(stg, L["px"], L["s200"]))
    need = [r for r in ev if any(x["ok"] for x in r["v"].values())]
    need.sort(key=lambda r: r["date"], reverse=True)              # newest first, if the time runs out
    G.FILINGS_SINCE = min((r["date"] for r in need), default="9999")
    print(len(need), "can get a grade in some variant: looking up their news")
    # 3. the news at the SEC, as of 9:30 that morning
    done = 0
    for r in need:
        if time.time() > t_end:
            break
        d = datetime.date.fromisoformat(r["date"])
        p = datetime.date.fromisoformat(cal[pos[r["date"]] - 1]) if pos.get(r["date"], 0) > 0 else d - datetime.timedelta(days=1)
        try:
            fs = G.filings(r["sym"], datetime.datetime(p.year, p.month, p.day, 16, 0, tzinfo=NY), datetime.datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY))
        except Exception as ex:
            r["err"] = repr(ex)[:80]
            continue
        texts = {f["acc"]: G.release_text(f) for f in [f for f in (fs or []) if G.worth_reading(f)][:4]}
        er = [f for f in (fs or []) if f["form"] == "8-K" and "2.02" in (f.get("items") or "")]
        e = hist_earnings(r["sym"], r["date"], texts.get(er[0]["acc"], ("", ""))[1]) if er else None
        nw = G.classify(fs, texts, "up", r["mcap"], e)
        r.update(news=nw["news"], catalyst=nw["catalyst"], why=nw["reason"][:120], earn=bool(er))
        done += 1
    print(done, "looked up")
    # 4. the grades and the tables
    for r in ev:
        for name, x in r["v"].items():
            x["grade"] = "—" if not x["ok"] else (G.combine(r["news"], x["ev"], "up", True, r.get("earn", False)) if r.get("news") else None)
    out = {"made_at": datetime.datetime.now(NY).isoformat(timespec="seconds"), "gap_ups": len(ev), "needed_news": len(need),
           "news_looked_up": done, "first": min((r["date"] for r in ev), default=None), "last": max((r["date"] for r in ev), default=None)}
    ok_rows = [r for r in ev if all(x.get("grade") is not None for x in r["v"].values())]
    out["scored"] = len(ok_rows)
    out["all_gap_ups"] = stats(ok_rows)
    for name in V:
        T = out[name] = {}
        T["by_grade"] = {g: stats([r for r in ok_rows if r["v"][name]["grade"] == g]) for g in GR}
        T["eligible_by_stage"] = {f"stage {k}": stats([r for r in ok_rows if r["v"][name]["ok"] and r["v"][name]["stage"] == k]) for k in (2, 3, 1, 4)}
        T["eligible_all"] = stats([r for r in ok_rows if r["v"][name]["ok"]])
        T["not_eligible_by_reason"] = {w: stats([r for r in ok_rows if not r["v"][name]["ok"] and r["v"][name]["why"] == w])
                                       for w in sorted({r["v"][name]["why"] for r in ok_rows if not r["v"][name]["ok"]})}
    R = out["rules"]
    R["turnup_by_group"] = {f"group {k}": stats([r for r in ok_rows if r["v"]["rules"]["grade"] in ("A+", "A") and r["v"]["rules"]["ev"] == "turnup" and r["group"] == k]) for k in (2, 1, 0)}
    R["AB_news_eligible_by_group"] = {f"group {k}": stats([r for r in ok_rows if r["v"]["rules"]["ok"] and r.get("news") in ("A", "B") and r["group"] == k]) for k in (2, 1, 0)}
    R["eligible_by_news"] = {g: stats([r for r in ok_rows if r["v"]["rules"]["ok"] and r.get("news") == g]) for g in "ABCF"}
    R["eligible_by_catalyst"] = {k: stats([r for r in ok_rows if r["v"]["rules"]["ok"] and r.get("catalyst") == k])
                                 for k in sorted({r.get("catalyst") for r in ok_rows if r["v"]["rules"]["ok"] and r.get("catalyst")})}
    ws = [r for r in ok_rows if r["v"]["rules"]["grade"] == "W"]
    cr = [r for r in ws if r.get("crossed200")]
    R["W_laggards"] = {"n": len(ws), "crossed_200_within_60%": pc([r.get("crossed200") for r in ws]),
                       "median_days_to_cross": None, "after_cross_held_5d%": pc([r["after_cross"]["held5"] for r in cr]),
                       "after_cross_ran20%": pc([r["after_cross"]["ran20"] for r in cr]), "after_cross_r20_avg": mean([r["after_cross"]["r20"] for r in cr])}
    R["examples"] = {g: [(r["sym"], r["date"], r["lv"]["gap"], r["v"]["rules"]["stage"], r.get("news"), r.get("catalyst"), (r.get("why") or "")[:80], r.get("r20"))
                         for r in ok_rows if r["v"]["rules"]["grade"] == g][:10] for g in ("A+", "A", "B", "W")}
    K = ("sym", "date", "over_low52", "group", "held", "ran20", "broke5", "r20", "trade", "crossed200", "news", "catalyst", "earn")
    out["rows_keys"] = list(K) + ["lv", "v"]
    out["rows"] = [[r.get(k) for k in K] + [{k2: round(v2, 3) if isinstance(v2, float) else v2 for k2, v2 in r["lv"].items()},
                                             {n2: {k3: x[k3] for k3 in ("stage", "ok", "grade")} for n2, x in r["v"].items()}] for r in ev]
    json.dump(out, open(a.out, "w"), separators=(",", ":"), default=str)
    print(json.dumps(out["rules"]["by_grade"], indent=0)[:1500])


if __name__ == "__main__":
    main()
