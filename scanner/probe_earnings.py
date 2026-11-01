#!/usr/bin/env python3
"""The user's earnings-day high breakout test (Nov 1 2026).

  python3 scanner/probe_earnings.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json
  (needs ALPACA_KEY_ID / ALPACA_SECRET: the news for the earnings days, the 5-minute bars)

  earnings day  the company's own earnings news (Alpaca / Benzinga headlines about results, guidance, the quarter) from the
                day before's 3 PM to 9:30 that morning; the day closes over its 1-month high (the highest high of the 20
                sessions before it, wicks and bodies), over the 200 SMA, 30%+ over the 52-week low; liquid: $10+, a 20-day
                average of $30M+ and 700K+ shares a day, market cap $700M+ (today's), ADR 4%+; volume 1.5x+ (an earnings
                day's volume: keeps the news lookups to the real reactions)
  entry         the first day within 10 sessions whose high gets over the earnings-day high: bought at the first 5-minute
                bar after the opening range trading over both the 5-minute opening range high and the earnings-day high
                (at the higher of the two, or the bar's open over them); the risk = the 5-minute opening range low.
                Only the first such day (no second try)
  managed       your rules (scanner/probe_pb1h.py trade): +2R breakeven, 1/3 at +3R, 1/3 at +5R, the runners out on a daily
                close under the 21 EMA or at breakeven (that close takes whatever is open)
"""
import argparse, collections, datetime, json, os, sys, time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402
import probe_catalyst as pc  # noqa: E402
import probe_pb1h as pb  # noqa: E402


def earnings_news(by_day):
    """{(symbol, date)} with the company's earnings news before that session's open"""
    out = set()
    for d, syms in sorted(by_day.items()):
        p = by_day_prev[d]
        t0 = datetime.datetime.fromisoformat(p + "T15:00").replace(tzinfo=pc.NY)
        t1 = datetime.datetime.fromisoformat(d + "T09:30").replace(tzinfo=pc.NY)
        syms = sorted(syms)
        for c0 in range(0, len(syms), 40):
            q = {"symbols": ",".join(pc.alp(s) for s in syms[c0:c0 + 40]), "start": pc.iso(t0), "end": pc.iso(t1), "limit": 50, "sort": "asc"}
            while True:
                res = pc.get("https://data.alpaca.markets/v1beta1/news", q)
                for n in res.get("news", []):
                    if len(n.get("symbols", [])) > 3 or pc.GENERIC.search(n.get("headline", "")) or not pc.EARN.search(n.get("headline", "")):
                        continue
                    for s in n.get("symbols", []):
                        s = s.replace(".", "-")
                        if s in syms:
                            out.add((s, d))
                if not res.get("next_page_token"):
                    break
                q["page_token"] = res["next_page_token"]
            time.sleep(0.3)
    return out


by_day_prev = {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    first = 200
    cand = collections.defaultdict(set)
    for s, a in A.items():
        st = a.st
        c, v = st.c, st.v
        av20, dv20 = launch.roll_mean(v, 20), launch.roll_mean(c * v, 20) / 1e6
        for i in range(max(a.start, first), c.size - 1):
            j = i - 1
            if not (c[j] >= 10 and av20[j] >= 700000 and dv20[j] >= 30 and st.adr[j] >= 4):
                continue
            if c[i] > a.hi20[i] and c[i] > a.s200[i] and c[i] >= st.low52[i] * 1.3 and a.rv[i] >= 1.5:
                cand[st.dates[i]].add(s)
                by_day_prev[st.dates[i]] = st.dates[i - 1]
    print(sum(len(x) for x in cand.values()), "possible earnings days")
    earn = earnings_news(cand)
    print(len(earn), "earnings days")
    # the entry day: the first of the next 10 sessions over the earnings-day high
    ent = collections.defaultdict(list)
    for s, d in earn:
        a = A[s]
        st = a.st
        i = st.dates.index(d)
        k = next((x for x in range(i + 1, min(st.c.size, i + 11)) if st.h[x] > st.h[i]), None)
        if k is not None:
            ent[st.dates[k]].append((s, i, k))
    ts = []
    for d, ks in sorted(ent.items()):
        t0 = datetime.datetime.fromisoformat(d + "T09:30").replace(tzinfo=pc.NY)
        b5 = pb.bars(sorted({s for s, i, k in ks}), t0, t0 + datetime.timedelta(minutes=390), "5Min")
        for s, i, k in ks:
            b = b5.get(pc.alp(s))
            if not b or not b[0]["t"].startswith(pc.iso(t0)[:16]):
                continue
            a = A[s]
            st = a.st
            lvl = max(b[0]["h"], float(st.h[i]))
            m = next((x for x in range(1, len(b)) if b[x]["h"] > lvl), None)
            if m is None:
                continue                                    # over the earnings-day high only in the first 5 minutes
            buy = max(lvl, b[m]["o"])
            t = pb.trade(a, k, b, -1e9, {}, entry=(m, buy))
            if t is None or not t.get("broke"):
                continue
            t.update(sym=s, earnings=st.dates[i], date=d, after=k - i, e_gap=float(a.gap[i]), e_chg=float(a.chg[i]),
                     e_top=bool(a.clpos[i] >= 0.5), cleared=a.cleared(i), entry_gap=float(a.gap[k]))
            ts.append(t)
    summ = pb.summ
    cut = lambda f: summ([t for t in ts if f(t)])
    out = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), first=cal[first], last=cal[-1],
               possible_earnings_days=sum(len(x) for x in cand.values()), earnings_days=len(earn),
               broke_the_earnings_high_within_10_days=sum(len(x) for x in ent.values()),
               all=summ(ts),
               by_days_after={"next day": cut(lambda t: t["after"] == 1), "2-3 days after": cut(lambda t: 2 <= t["after"] <= 3),
                              "4-10 days after": cut(lambda t: t["after"] >= 4)},
               by_earnings_gap={"gapped down": cut(lambda t: t["e_gap"] < 0), "gap 0-5%": cut(lambda t: 0 <= t["e_gap"] < 5),
                                "gap 5-10%": cut(lambda t: 5 <= t["e_gap"] < 10), "gap 10%+": cut(lambda t: t["e_gap"] >= 10)},
               by_earnings_close={"closed in the top half": cut(lambda t: t["e_top"]), "closed in the lower half": cut(lambda t: not t["e_top"])},
               by_base_cleared={"1-month": cut(lambda t: t["cleared"] <= 21), "3-month": cut(lambda t: t["cleared"] == 63),
                                "6-month": cut(lambda t: t["cleared"] == 120)},
               by_entry_gap={"entry day gapped up": cut(lambda t: t["entry_gap"] > 0), "entry day opened flat / down": cut(lambda t: t["entry_gap"] <= 0)},
               examples=[{k: (round(v, 2) if isinstance(v, float) else v) for k, v in t.items() if k in ("sym", "earnings", "date", "after", "R", "how", "e_gap", "e_chg")}
                         for t in ts[-40:]])
    json.dump(out, open(a_.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "examples"}, indent=1))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        json.dump(dict(error=traceback.format_exc()[-3000:]), open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
        raise
