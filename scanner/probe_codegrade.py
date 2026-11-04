#!/usr/bin/env python3
"""Backtest of the code grader (radar/codegrade.py) on every past gap of 5%+ (test/codegrade, Nov 4 2026).

  python3 scanner/probe_codegrade.py --bars BARS.json.gz --stocks stocks.json --out OUT.json [--minutes 40]

Each gap day of the last ~14 months (2 years of bars, the first 200 sessions for the averages) in the pre-market
list's universe (market cap $700M+ then, price $10+, 20-day $20M+ and 600K+ shares, ADR 3%+) is graded as of that
morning, with no hindsight:
  news   the SEC filings accepted from the last close (4 PM ET) to 9:30 AM that day, classified by codegrade.classify;
         an earnings release gets its revenue growth and last quarter's growth from the SEC's XBRL data (the numbers
         the release reported) and the guidance words from the release (radar/earnings.py guidance); no estimates
         exist this far back, so no beat / miss
  chart  the open stands in for the pre-market price, against the last close's 21 EMA, 50 EMA, 200 SMA and the
         21-day high (variants: the 30-day high, the 50-day SMA)
  group  the stock's best group status at the last close (launch.group_status: 2 leading, 1 turning up, 0 not)
Then what happened (gap-ups): held = closed at or over the open (the pre-market price proxy), ran 20%+ = a high 20%+
over the open within 20 sessions, broke the low = under the gap day's low within 5 sessions, r20 = the close 20
sessions on vs the gap-day close, trade = bought at the open, out under the day's low or the first close under the
21 EMA (the launch backtest's rule). Gap-downs: held = closed at or under the open, r20 the same.
"""
import argparse, collections, datetime, json, os, sys, time, zoneinfo
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


_xq = {}


def xbrl_quarters(sym):
    """{quarter end (date): revenue} from the SEC's XBRL facts; Q4 = the year minus its three quarters"""
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
    _xq[c] = best
    return best


def near(q, d, tol=12):
    k = min(q, key=lambda x: abs((x - d).days), default=None)
    return q[k] if k is not None and abs((k - d).days) <= tol else None


def hist_earnings(sym, day, text):
    """the Earnings fields for a past release: revenue growth y/y, last quarter's, the guidance words"""
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
    e.update(rev_growth=pct(v, vy), rev_prev_growth=pct(vp, vpy), q_end=qe.isoformat())
    return e


def stats(rs, up=True):
    n = len(rs)
    if not n:
        return {"n": 0}
    f = lambda k: [r[k] for r in rs if r.get(k) is not None]
    held, ran, broke, r20, tr = f("held"), f("ran20"), f("broke5"), f("r20"), f("trade")
    pc = lambda xs: round(100 * sum(xs) / len(xs)) if xs else None
    return {"n": n, "held%": pc(held), "ran20%": pc(ran), "broke_low5%": pc(broke),
            "r20_avg": round(float(np.mean(r20)), 1) if r20 else None, "r20_med": round(float(np.median(r20)), 1) if r20 else None,
            "trade_avg": round(float(np.mean(tr)), 1) if tr else None, "trade_win%": pc([x > 0 for x in tr])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--minutes", type=float, default=40)
    a = ap.parse_args()
    t_end = time.time() + 60 * a.minutes
    A, groups, GS, cal, S = launch.load(a.bars, a.stocks)
    mcap = {s["symbol"]: s.get("mcap_b") or 0 for s in json.load(open(a.stocks))}
    pos = {d: k for k, d in enumerate(cal)}
    best_g = {}
    for g, (ms, stt, _, _) in GS.items():
        for s in ms:
            best_g.setdefault(s, []).append(stt)
    # 1. the events
    ev, skipped52 = [], 0
    for s, ar in A.items():
        st = ar.st
        c, o, h, l = st.c, st.o, st.h, st.l
        n, last = c.size, c[-1]
        for i in range(max(ar.start, 31), n):
            gp = ar.gap[i]
            if not (abs(gp) >= 5) or not ar.liq_noadr[i] or st.adr[i] < 3 or mcap.get(s, 0) * c[i] / last < 0.7:
                continue
            up = gp > 0
            px = o[i]
            hi21, hi30 = float(h[i - 21:i].max()), float(h[i - 30:i].max())
            s50 = float(c[i - 50:i].mean()) if i >= 50 else float("nan")
            e21, e50, s200, pc = float(ar.e21[i - 1]), float(ar.e50[i - 1]), float(ar.s200[i - 1]), float(c[i - 1])
            k = pos.get(st.dates[i - 1])
            grp = max((int(x[k]) for x in best_g.get(s, []) if k is not None and k < len(x)), default=0)
            lo52 = float(l[max(0, i - 252):i].min())
            lv = dict(px=round(float(px), 4), pc=round(float(c[i - 1]), 4), e21=round(float(ar.e21[i - 1]), 4), e50=round(float(ar.e50[i - 1]), 4),
                      s200=round(float(ar.s200[i - 1]), 4), hi21=round(float(h[i - 21:i].max()), 4), hi30=round(float(h[i - 30:i].max()), 4),
                      s50=round(float(c[i - 50:i].mean()), 4) if i >= 50 else None)
            r = dict(sym=s, date=st.dates[i], up=up, gap=round(float(gp), 1), mcap=mcap.get(s, 0) * c[i] / last,
                     over_low52=round(100 * (px / lo52 - 1), 1) if lo52 > 0 else None, lv=lv,
                     chart=G.chart_state(px, pc, e21, e50, s200, hi21), chart30=G.chart_state(px, pc, e21, e50, s200, hi30),
                     chartS50=G.chart_state(px, pc, e21, s50, s200, hi21) if s50 == s50 else "unknown", group=grp,
                     broke_trend=bool(not up and e21 > e50 > s200 and px < e50 and px < s200))
            if up:
                r["held"] = bool(c[i] >= o[i])
                r["ran20"] = bool(h[i:i + 21].max() >= 1.2 * o[i]) if i + 20 < n else None
                r["broke5"] = bool(any(l[j] < l[i] for j in range(i + 1, min(i + 6, n))))
                k2 = None
                for j in range(i + 1, n):
                    if l[j] <= l[i] or c[j] < ar.e21[j]:
                        k2 = j
                        break
                if k2 is not None:
                    exit_px = min(l[i], o[k2]) if l[k2] <= l[i] else c[k2]
                    r["trade"] = round(100 * (exit_px / o[i] - 1), 1)
            else:
                r["held"] = bool(c[i] <= o[i])
                r["broke5"] = None
            r["r20"] = round(100 * (c[i + 20] / c[i] - 1), 1) if i + 20 < n else None
            if up and px < s200:                        # still under the 200: did it cross later, and how did it do from there?
                r["under50"] = bool(px < e50)
                j = next((j for j in range(i + 1, min(i + 61, n)) if c[j] > ar.s200[j]), None)
                r["crossed200"] = j is not None if i + 60 < n else (True if j is not None else None)
                if j is not None:
                    r["days_to_200"] = j - i
                    r["after_cross_r20"] = round(100 * (c[j + 20] / c[j] - 1), 1) if j + 20 < n else None
                    r["after_cross_ran20"] = bool(h[j + 1:j + 21].max() >= 1.2 * c[j]) if j + 20 < n else None
                    r["after_cross_held5"] = bool(all(c[k] > ar.s200[k] for k in range(j, min(j + 5, n))))
            if r["over_low52"] is not None and r["over_low52"] < G.LOW52_MIN:
                skipped52 += 1                          # qualifies for nothing (the user, Nov 4 2026)
                continue
            ev.append(r)
    ev.sort(key=lambda r: r["date"], reverse=True)          # newest first: if time runs out, the recent months are in
    print(len(ev), "gap events")
    # 2. the news at the SEC, as of 9:30 that morning
    done = 0
    for r in ev:
        if time.time() > t_end:
            break
        d = datetime.date.fromisoformat(r["date"])
        p = datetime.date.fromisoformat(cal[pos[r["date"]] - 1]) if r["date"] in pos and pos[r["date"]] > 0 else d - datetime.timedelta(days=1)
        t_from = datetime.datetime(p.year, p.month, p.day, 16, 0, tzinfo=NY)
        t_to = datetime.datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY)
        try:
            fs = G.filings(r["sym"], t_from, t_to)
        except Exception as ex:
            r["news"] = None; r["err"] = repr(ex)[:80]
            continue
        texts = {}
        for f in (fs or [])[:6]:
            if f["form"] in ("8-K", "6-K"):
                texts[f["acc"]] = G.release_text(f)
        e = None
        er = [f for f in (fs or []) if f["form"] == "8-K" and "2.02" in (f.get("items") or "")]
        if er:
            e = hist_earnings(r["sym"], r["date"], texts.get(er[0]["acc"], ("", ""))[1])
        nw = G.classify(fs, texts, "up" if r["up"] else "down", r["mcap"], e)
        dn = "up" if r["up"] else "down"
        r.update(news=nw["news"], catalyst=nw["catalyst"], why=nw["reason"][:140], earn=bool(er),
                 grade=G.combine(nw["news"], r["chart"], dn, r["broke_trend"], r["over_low52"], bool(er)),
                 grade30=G.combine(nw["news"], r["chart30"], dn, r["broke_trend"], r["over_low52"], bool(er)),
                 gradeS50=G.combine(nw["news"], r["chartS50"], dn, r["broke_trend"], r["over_low52"], bool(er)))
        done += 1
    graded = [r for r in ev if r.get("news")]
    print(done, "graded")
    # 3. the tables
    out = {"made_at": datetime.datetime.now(NY).isoformat(timespec="seconds"), "events": len(ev), "graded": len(graded),
           "left_out_under_30pct_over_52w_low": skipped52,
           "first": min((r["date"] for r in graded), default=None), "last": max((r["date"] for r in graded), default=None)}
    for side, flag in (("up", True), ("down", False)):
        rs = [r for r in graded if r["up"] == flag]
        T = out[side] = {}
        T["all"] = stats(rs)
        T["by_news"] = {g: stats([r for r in rs if r["news"] == g]) for g in "ABCF"}
        T["by_chart"] = {c: stats([r for r in rs if r["chart"] == c]) for c in ("turnup", "trending", "mixed", "laggard", "downtrend", "under50")}
        T["news_x_chart"] = {f"{g} / {c}": stats([r for r in rs if r["news"] == g and r["chart"] == c])
                             for g in "ABCF" for c in ("turnup", "trending", "mixed", "laggard", "downtrend", "under50")}
        GR = ("A+", "A", "B", "W", "C", "F", "—")
        T["by_grade"] = {g: stats([r for r in rs if r["grade"] == g]) for g in GR}
        T["by_grade_30day_high"] = {g: stats([r for r in rs if r["grade30"] == g]) for g in GR}
        T["by_grade_50sma"] = {g: stats([r for r in rs if r["gradeS50"] == g]) for g in GR}
        ws = [r for r in rs if r["grade"] == "W"]
        cr = [r for r in ws if r.get("crossed200")]
        T["W_laggard_watch"] = {"n": len(ws), "crossed_200_within_60%": round(100 * len(cr) / len([r for r in ws if r.get("crossed200") is not None])) if ws else None,
                                "median_days_to_cross": float(np.median([r["days_to_200"] for r in cr])) if cr else None,
                                "after_cross": {"held_over_200_5d%": round(100 * np.mean([r["after_cross_held5"] for r in cr])) if cr else None,
                                                "ran20%": round(100 * np.mean([r["after_cross_ran20"] for r in cr if r.get("after_cross_ran20") is not None])) if cr else None,
                                                "r20_avg": round(float(np.mean([r["after_cross_r20"] for r in cr if r.get("after_cross_r20") is not None])), 1) if cr else None},
                                "C_laggard_for_comparison": {"n": len([r for r in rs if r["news"] == "C" and r["chart"] == "laggard"]),
                                                              "crossed_200_within_60%": round(100 * np.mean([bool(r.get("crossed200")) for r in rs if r["news"] == "C" and r["chart"] == "laggard" and r.get("crossed200") is not None])) if any(r["news"] == "C" and r["chart"] == "laggard" for r in rs) else None},
                                "AB_under200_under21d_high": stats([r for r in rs if r["news"] in ("A", "B") and r["chart"] == "downtrend"])}
        T["turnup_by_group"] = {f"group {k}": stats([r for r in rs if r["chart"] == "turnup" and r["group"] == k]) for k in (2, 1, 0)}
        T["AB_news_by_group"] = {f"group {k}": stats([r for r in rs if r["news"] in ("A", "B") and r["group"] == k]) for k in (2, 1, 0)}
        T["by_catalyst"] = {k: stats([r for r in rs if r["catalyst"] == k]) for k in sorted({r["catalyst"] for r in rs})}
        T["earnings_only_by_news"] = {g: stats([r for r in rs if r["earn"] and r["news"] == g]) for g in "ABC"}
        T["examples"] = {g: [(r["sym"], r["date"], r["gap"], r["news"], r["chart"], r["catalyst"], r["why"][:90], r.get("r20"))
                             for r in rs if r["grade"] == g][:12] for g in ("A+", "A", "B", "W", "F")}
    # every graded event, compact, so a rule change can be re-scored without re-running the SEC part
    K = ("sym", "date", "up", "gap", "over_low52", "news", "catalyst", "chart", "chart30", "chartS50", "group", "held", "ran20",
         "broke5", "r20", "trade", "crossed200", "days_to_200", "after_cross_r20", "after_cross_ran20", "after_cross_held5", "earn", "lv",
         "broke_trend")
    out["rows_keys"] = K
    out["rows"] = [[r.get(k) for k in K] for r in graded]
    json.dump(out, open(a.out, "w"), separators=(",", ":"), default=str)
    print(json.dumps(out["up"]["by_grade"], indent=1))


if __name__ == "__main__":
    main()
