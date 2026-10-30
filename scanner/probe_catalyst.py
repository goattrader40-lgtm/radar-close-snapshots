#!/usr/bin/env python3
"""The catalyst launch (earnings or meaningful news; a 5%+ gap that closes net positive, still in the gap and over at
least its 1-month base by the candle bodies, though up less than 5%) against the current launch rules, on the last
2 years. A launch is what you follow, not the trade: the trades are the buy points after it, and on the day itself
only a break of the 5-minute opening range high.

  python3 scanner/probe_catalyst.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json
  (needs ALPACA_KEY_ID / ALPACA_SECRET: the news headlines and the launch days' 5-minute bars)

  news        Alpaca's news (Benzinga) from the prior session's close to 9:30 that morning, about the company
              itself (3 symbols or fewer, not a movers list or a "why it's moving" story); "earnings" when the
              headline is about results / guidance. The live scanner uses your earnings and news tags instead (2
              years of those don't exist)
  launch day  the opening range high (the first 5 minutes): bought when it breaks, at that high (or the bar's open
              over it); stopped under the day's low from the next day, else sold on the first close under the 21 EMA
  buy points  the follow day by day for 60 sessions (until the 50 EMA is lost): breakouts, flag breakouts, pops,
              retests; each bought at that day's close: ran 10% / 20% in 20 sessions, failed in 5 (a close under
              the day's low), the close 20 sessions on
"""
import argparse, collections, datetime, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request, zoneinfo
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402

L = launch.L
NY = zoneinfo.ZoneInfo("America/New_York")
HDR = {"APCA-API-KEY-ID": os.environ.get("ALPACA_KEY_ID", ""), "APCA-API-SECRET-KEY": os.environ.get("ALPACA_SECRET", "")}
GENERIC = re.compile(r"stocks? (moving|to watch|making|that|hitting|trading)|movers|gainers|losers|mid-?day|pre-?market session|"
                     r"market (update|open|close|wrap)|trading (higher|lower)|shares are|what's going on|why .* (shares|stock)|"
                     r"52-week|unusual options|options activity|short interest", re.I)
EARN = re.compile(r"earnings|results|\bF?Q[1-4]\b|\bEPS\b|revenue|sales|guidance|guides|outlook|quarter|beats|misses", re.I)
iso = lambda t: t.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
alp = lambda s: s.replace("-", ".")


def get(url, q):
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url + "?" + urllib.parse.urlencode(q), headers=HDR), timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise
            time.sleep(10 if e.code == 429 else 3)
        except Exception:
            time.sleep(3)
    return {}


def news_on(s, d, p):
    """(what, headline) for the company's own news from session p's close to 9:30 on d, or None"""
    t0 = datetime.datetime.fromisoformat(p + "T16:00").replace(tzinfo=NY)
    t1 = datetime.datetime.fromisoformat(d + "T09:30").replace(tzinfo=NY)
    res = get("https://data.alpaca.markets/v1beta1/news", {"symbols": alp(s), "start": iso(t0), "end": iso(t1), "limit": 50, "sort": "asc"})
    own = [n for n in res.get("news", []) if len(n.get("symbols", [])) <= 3 and not GENERIC.search(n.get("headline", ""))]
    if not own:
        return None
    e = next((n for n in own if EARN.search(n["headline"])), None)
    return ("earnings" if e else "news", (e or own[0])["headline"][:140])


def orh_entries(A, keys):
    """{(symbol, i): the buy price when the launch day broke its 5-minute opening range high, else None}"""
    by_day = collections.defaultdict(list)
    for s, i in keys:
        by_day[A[s].st.dates[i]].append((s, i))
    out = {}
    for d, ks in sorted(by_day.items()):
        t0 = datetime.datetime.fromisoformat(d + "T09:30").replace(tzinfo=NY)
        syms = sorted({s for s, i in ks})
        bars = collections.defaultdict(list)
        for c0 in range(0, len(syms), 100):
            q = {"symbols": ",".join(alp(s) for s in syms[c0:c0 + 100]), "timeframe": "5Min", "feed": "sip", "adjustment": "split",
                 "limit": 10000, "start": iso(t0), "end": iso(t0 + datetime.timedelta(minutes=390))}
            while True:
                res = get("https://data.alpaca.markets/v2/stocks/bars", q)
                for s, rows in (res.get("bars") or {}).items():
                    bars[s].extend(rows)
                if not res.get("next_page_token"):
                    break
                q["page_token"] = res["next_page_token"]
            time.sleep(0.3)
        for s, i in ks:
            b = bars.get(alp(s))
            if not b or not b[0]["t"].startswith(iso(t0)[:16]):
                continue                                   # no bar for 9:30 (a halt or no data): left out
            orh = b[0]["h"]
            hit = next((x for x in b[1:] if x["h"] > orh), None)
            out[(s, i)] = max(orh, hit["o"]) if hit else None
    return out


def trade(a, i, buy):
    st, c, o, lo = a.st, a.st.c, a.st.o, a.st.l
    stop = lo[i]
    for j in range(i + 1, c.size):
        if lo[j] <= stop:
            return 100 * (min(stop, o[j]) / buy - 1), 100 * (st.h[i:j + 1].max() / buy - 1)
        if c[j] < a.e21[j]:
            return 100 * (c[j] / buy - 1), 100 * (st.h[i:j + 1].max() / buy - 1)
    return None


def summ(rs, n_all=None):
    rs = [r for r in rs if r]
    if not rs:
        return None
    ret, mg = np.array([r[0] for r in rs]), np.array([r[1] for r in rs])
    out = dict(n=len(rs), win=round(100 * float(np.mean(ret > 0))), avg=round(float(ret.mean()), 1), med=round(float(np.median(ret)), 1),
               ran20=round(100 * float(np.mean(mg >= 20))), ran50=round(100 * float(np.mean(mg >= 50))))
    if n_all:
        out["broke_orh_pct"] = round(100 * len(rs) / n_all)
    return out


def launch_day(A, keys, orh):
    have = [k for k in keys if k in orh]
    return summ([trade(A[s], i, orh[(s, i)]) for s, i in have if orh[(s, i)]], len(have))


def buy_points(A, keys):
    """the buy points in each launch's first 60 sessions: {kind: [outcome]}, plus the count per launch"""
    out, per = collections.defaultdict(list), []
    for s, i0 in keys:
        a = A[s]
        c, lo, h = a.st.c, a.st.l, a.st.h
        n, m = c.size, 0
        for j in range(i0 + 1, min(n - 6, i0 + 61)):
            f = launch.follow(a, i0, j)
            if f["lost_50ema"]:
                break
            st = f["stage"]
            kind = next((k for k, w in (("breakout", "Base breakout"), ("flag", "Flag breakout"), ("pop", "Pop out"), ("retest", "Retest"))
                         if st.startswith(w)), None)
            if not kind:
                continue
            e = c[j]
            r = dict(ran10=h[j + 1:j + 21].max() >= e * 1.1, ran20=h[j + 1:j + 21].max() >= e * 1.2, fail5=bool((c[j + 1:j + 6] < lo[j]).any()),
                     r20=100 * (c[j + 20] / e - 1) if j + 20 < n else None)
            out[kind].append(r)
            out["all"].append(r)
            m += 1
        per.append(m)
    res = {}
    for k, rs in out.items():
        r20 = [r["r20"] for r in rs if r["r20"] is not None]
        res[k] = dict(n=len(rs), ran10=round(100 * np.mean([r["ran10"] for r in rs])), ran20=round(100 * np.mean([r["ran20"] for r in rs])),
                      fail5=round(100 * np.mean([r["fail5"] for r in rs])), med20=round(float(np.median(r20)), 1) if r20 else None)
    res["per_launch"] = round(float(np.mean(per)), 2) if per else None
    res["launches_with_one"] = round(100 * float(np.mean([m > 0 for m in per]))) if per else None
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    # the days that would be catalyst launches with news, and their news
    every = {}
    for s, a in A.items():
        for i in range(max(a.start, 200), a.st.c.size):
            if a.gap[i] >= L["ep_gap"] and a.chg[i] > 0 and not (a.chg[i] >= L["min_chg"] and a.held(i)):
                every[(s, a.st.dates[i])] = "?"
    launch.CATALYST_DAYS.clear()
    launch.CATALYST_DAYS.update(every)
    L["catalyst_launch"] = 1
    maybe = [(s, i) for s, a in A.items() for i in range(max(a.start, 200), a.st.c.size) if a.catalyst(i) and a.candidate(i)]
    news = {}
    for s, i in maybe:
        r = news_on(s, A[s].st.dates[i], A[s].st.dates[i - 1])
        if r:
            news[(s, A[s].st.dates[i])] = r
        time.sleep(0.3)
    check = {"GMAB 2026-08-07": news_on("GMAB", "2026-08-07", "2026-08-06")}
    sets = {}
    for name, flag, days in (("current", 0, {}), ("with_news", 1, {k: v[0] for k, v in news.items()}), ("no_news_needed", 1, every)):
        L["catalyst_launch"] = flag
        launch.CATALYST_DAYS.clear()
        launch.CATALYST_DAYS.update(days)
        sets[name] = {(s, i) for s, i, k, gs, gn in launch.detect(A, groups, GS, cal, S)}
    cur = sets["current"]
    cat = sorted(k for k in sets["with_news"] - cur if (k[0], A[k[0]].st.dates[k[1]]) in news)
    nonews = sorted(k for k in sets["no_news_needed"] - cur if (k[0], A[k[0]].st.dates[k[1]]) not in news)
    gone = sorted(cur - sets["with_news"])
    orh = orh_entries(A, sorted(cur | set(cat) | set(nonews)))
    out = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), first=cal[200], last=cal[-1],
               candidate_days=len(maybe), with_news=len(news), earnings=sum(1 for v in news.values() if v[0] == "earnings"),
               launches=dict(current=len(cur), catalyst_with_news=len(cat), catalyst_without_news=len(nonews), current_absorbed=len(gone)),
               launch_day_orh=dict(current=launch_day(A, cur, orh), catalyst_with_news=launch_day(A, cat, orh),
                                   catalyst_without_news=launch_day(A, nonews, orh), absorbed=launch_day(A, gone, orh)),
               buy_points=dict(current=buy_points(A, sorted(cur)), catalyst_with_news=buy_points(A, cat), catalyst_without_news=buy_points(A, nonews)),
               by_base={f"{n} sessions": dict(n=sum(1 for s, i in cat if A[s].cleared(i) == n),
                                              orh=launch_day(A, [(s, i) for s, i in cat if A[s].cleared(i) == n], orh),
                                              buy_points=buy_points(A, [(s, i) for s, i in cat if A[s].cleared(i) == n]).get("all"))
                        for n in launch.BASES},
               check=check,
               examples=[[A[s].st.dates[i], s, round(float(A[s].gap[i]), 1), round(float(A[s].chg[i]), 1), A[s].cleared(i)] + list(news[(s, A[s].st.dates[i])])
                         for s, i in sorted(cat, key=lambda k: A[k[0]].st.dates[k[1]])[-40:]])
    json.dump(out, open(a_.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "examples"}, indent=1))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:                       # the run's log isn't readable from the session: the error goes out instead
        import traceback
        body = getattr(e, "read", lambda: b"")()[:500].decode("utf-8", "replace")
        json.dump(dict(error=traceback.format_exc()[-3000:], body=body), open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
        raise
