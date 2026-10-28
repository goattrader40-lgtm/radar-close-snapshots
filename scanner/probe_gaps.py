#!/usr/bin/env python3
"""Two checks on the big gap-up alerts, before changing them.

  python3 scanner/probe_gaps.py --bars BARS.json.gz --stocks radar-data/stocks.json --volprofile volprofile.json
                                --out OUT.json [--days 60]      (part 2 needs ALPACA_KEY_ID / ALPACA_SECRET)

1. Power days and big gap-ups the live alerts don't see (2 years of daily bars, the launch list's minimums:
   price $10+, $20M+ a day, 600K+ shares a day over 20 days, ADR 3.5%+, market cap $700M+ today). Each one by where
   it stood at the last close: in the watch list's range (alerted today), 28-50% over the 200 SMA (power days only),
   50%+ over it (a trend already running), or launched in the last 20 sessions without a close under the 21 EMA
   (on the Launches table: breakout alerts only). Scored like the launch backtest: bought at the open, stop under
   the day's low from the next day, else out on the first close under the 21 EMA; and from the close.
   power day = volume 4x+, a 10%+ gap, a 15%+ day; big gap = a 5%+ gap on 3x+ volume (no earnings dates this far
   back, so earnings and news alike).
2. The 9:31 early heads-up (radar/alerts.py find_early) on the last N sessions: each day's watch list rebuilt
   from the bars as the evening scan makes it, the first 30 minutes replayed from Alpaca's SIP minute bars, the
   heads-ups 9:31-9:34 and the full alerts 9:35-10:00 every minute, as the job runs them. Rel vol: the stock's
   volume curve today (volprofile.json) scaled by its 20-day volume then. How many heads-ups a day, how many the
   volume confirmed by 9:35 / by 10:00, and how the rest did.
"""
import argparse, collections, datetime, json, os, sys, time, urllib.parse, urllib.request
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "radar"))
import launch  # noqa: E402
import run  # noqa: E402
import alerts  # noqa: E402
from live import rvol_at  # noqa: E402

L = launch.L
NY = alerts.NY
UTC = datetime.timezone.utc


def score(a, i):
    """the launch backtest's two ways: (from the open: stop under the day's low, else the first close under the 21 EMA),
    (from the close: out on the first close under the 21 EMA); each (return %, max gain %, 20-day %, broke the low in 5)"""
    c, o, h, lo = a.st.c, a.st.o, a.st.h, a.st.l
    n = c.size
    out = []
    for buy in (o[i], c[i]):
        k, px = None, None
        for j in range(i + 1, n):
            if buy == o[i] and lo[j] <= lo[i]:
                k, px = j, min(lo[i], o[j])
                break
            if c[j] < a.e21[j]:
                k, px = j, c[j]
                break
        if k is None:
            return None
        out.append(dict(ret=100 * (px / buy - 1), maxg=100 * (h[i:k + 1].max() / buy - 1), days=k - i,
                        r20=100 * (c[i + 20] / buy - 1) if i + 20 < n else None))
    broke = bool(any(lo[j] < lo[i] for j in range(i + 1, min(i + 6, n))))
    return out[0], out[1], broke


def summ(rs, which):
    if not rs:
        return None
    x = [r[which] for r in rs]
    ret, mg = np.array([e["ret"] for e in x]), np.array([e["maxg"] for e in x])
    r20 = np.array([e["r20"] for e in x if e["r20"] is not None])
    return dict(n=len(rs), win=round(100 * float(np.mean(ret > 0))), avg=round(float(ret.mean()), 1), med=round(float(np.median(ret)), 1),
                ran20=round(100 * float(np.mean(mg >= 20))), ran50=round(100 * float(np.mean(mg >= 50))),
                avg20d=round(float(r20.mean()), 1) if r20.size else None, days=round(float(np.mean([e["days"] for e in x])), 1),
                broke_low_5d=round(100 * float(np.mean([r["broke"] for r in rs]))))


def recent_launches(A, groups, GS, cal):
    """{sym: bool array}: launched in the last 20 sessions without a close under the 21 EMA since (the watch list leaves these out)"""
    rec = {s: np.zeros(a.st.c.size, bool) for s, a in A.items()}
    for s, i, k, gs, gn in launch.detect(A, groups, GS, cal, None):
        a = A[s]
        for j in range(i, min(i + L["dedupe_days"], a.st.c.size)):
            if j > i and a.st.c[j] < a.e21[j]:
                break
            rec[s][j] = True
    return rec


def part1(A, rec, mcap, cal):
    ev = collections.defaultdict(list)
    for s, a in A.items():
        c, n = a.st.c, a.st.c.size
        last = c[-1]
        for i in range(max(a.start, 1), n):
            if not a.liquid[i] or not (c[i] > a.s200[i]) or mcap.get(s, 0) * c[i] / last < 700e6:
                continue
            pw = a.power(i)
            big = a.gap[i] >= L["ep_gap"] and a.rv[i] >= L["rv_big"]
            if not (pw or big):
                continue
            ext = a.ext200_prev[i]
            if np.isnan(ext) or ext < -L["watch_under200"]:
                continue
            launched = bool(rec[s][i - 1])
            where = ("launched" if launched else "over50" if ext > L["power_ext200"] else
                     "28to50" if ext > L["max_ext200"] else "watch")
            if where == "28to50" and pw:
                where = "watch"                            # the watch list keeps 28-50% over for power days
            sc = score(a, i)
            if sc is None:
                continue
            r = dict(sym=s, date=a.st.dates[i], ext=round(float(ext)), gap=round(float(a.gap[i]), 1), chg=round(float(a.chg[i]), 1),
                     rv=round(float(a.rv[i]), 1), open=sc[0], close=sc[1], broke=sc[2])
            ev[("power" if pw else "gap", where)].append(r)
    out = {}
    months = len(cal[200:]) / 21
    for (kind, where), rs in sorted(ev.items()):
        out[f"{kind} / {where}"] = dict(per_month=round(len(rs) / months, 1), from_open=summ(rs, "open"), from_close=summ(rs, "close"),
                                         best=sorted(((round(r["open"]["maxg"]), r["sym"], r["date"], r["ext"]) for r in rs), reverse=True)[:8],
                                         recent=[(r["sym"], r["date"], r["ext"], r["gap"], r["chg"], r["rv"], round(r["open"]["ret"], 1)) for r in sorted(rs, key=lambda r: r["date"])[-8:]])
    # the running leaders by how far over the 200 SMA
    for kind in ("power", "gap"):
        rs = ev.get((kind, "over50"), [])
        for lo_, hi_ in ((50, 80), (80, 150), (150, 10 ** 6)):
            sub = [r for r in rs if lo_ < r["ext"] <= hi_]
            out[f"{kind} / over50 {lo_}-{hi_ if hi_ < 10 ** 6 else ''}"] = dict(from_open=summ(sub, "open"), from_close=summ(sub, "close"))
    return out


def watch_rows(A, groups, GS, cal, rec, k, pos):
    """the watch list the evening scan would have made after calendar day k (launch.daily's rules)"""
    W = {}
    for s, a in A.items():
        i = pos[s].get(cal[k])
        st = a.st
        if i is None or i < a.start or i < 60 or not a.liquid[i] or rec[s][i]:
            continue
        ext = 100 * (st.c[i] / a.s200[i] - 1)
        if not (-L["watch_under200"] <= ext <= L["power_ext200"]):
            continue
        gs, gn = launch.best_group(s, k, groups, GS)
        g = int(a.mem[i + 1]) if i + 1 < st.c.size else -1
        W[s] = [float(st.c[i]), float(st.h[i - L["base_days"] + 1:i + 1].max()), float(a.s200[i]), float(a.e21[i]), float(a.e50[i]),
                float(st.high52[i]), 0, 0, gn, gs, run.tv_symbol(s, st.exchange), [st.dates[g], float(a.hi20[g])] if g >= 0 else None, None]
    return W


def alpaca_bars(syms, day, hdr):
    t0 = datetime.datetime(day.year, day.month, day.day, 9, 30, tzinfo=NY)
    z = lambda t: t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    q = {"symbols": ",".join(x.replace("/", ".") for x in syms), "timeframe": "1Min", "feed": "sip", "adjustment": "raw", "limit": 10000,
         "start": z(t0), "end": z(t0 + datetime.timedelta(minutes=31))}
    bars = {}
    while True:
        for attempt in range(4):
            try:
                with urllib.request.urlopen(urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q),
                                                                   headers=hdr), timeout=60) as r:
                    res = json.load(r)
                break
            except Exception:
                time.sleep(3 * (attempt + 1))
        else:
            return {}
        for s, rows in (res.get("bars") or {}).items():
            bars.setdefault(s.replace(".", "/"), []).extend(rows)
        if not res.get("next_page_token"):
            break
        q["page_token"] = res["next_page_token"]
    for rows in bars.values():
        for b in rows:
            b["ts"] = datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).timestamp()
    return bars


def part2(A, groups, GS, cal, rec, prof, days):
    hdr = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
    rules = dict(L)
    res, perday = [], []
    pos = {s: {d: i for i, d in enumerate(a.st.dates)} for s, a in A.items()}
    for k in range(len(cal) - days, len(cal)):
        day = datetime.date.fromisoformat(cal[k])
        W = watch_rows(A, groups, GS, cal, rec, k - 1, pos)
        doc = {"date": cal[k - 1], "rules": rules, "watch": W, "launches": []}
        cand = []
        for s in W:
            a = A[s]
            i = pos[s].get(cal[k])
            if i is None:
                continue
            if a.gap[i] >= 3 or 100 * (a.st.h[i] / a.st.c[i - 1] - 1) >= 5:
                cand.append(s)
        bars = {}
        for j in range(0, len(cand), 150):
            bars.update(alpaca_bars(cand[j:j + 150], day, hdr))
        t0 = datetime.datetime(day.year, day.month, day.day, 9, 30, tzinfo=NY)
        first_early, first_full = {}, {}
        for m in range(1, 31):
            t = t0 + datetime.timedelta(minutes=m, seconds=20)
            rows = {}
            for s in cand:
                done = [b for b in bars.get(s, []) if b["ts"] + 60 <= t.timestamp()]
                if not done:
                    continue
                a = A[s]
                i = pos[s][cal[k]]
                prev = float(a.st.c[i - 1])
                price, vol, qt = done[-1]["c"], sum(b["v"] for b in done), done[-1]["ts"] + 60 - 1e-3
                curve = prof.get(s)
                if curve:
                    v20 = a.st.v[max(0, i - 20):i].mean()
                    v20_now = a.st.v[-20:].mean()
                    curve = [x * v20 / v20_now for x in curve] if v20_now > 0 else None
                rows[s] = [price, 100 * (price / prev - 1), vol, qt, rvol_at(vol, qt, curve), bars[s][0]["o"], None]
            live = {"rows": rows}
            found = alerts.find_early(live, doc, t) if m < 5 else alerts.find(live, doc, t, gaps_only=True)
            for key, title, msg, prio, tv in found:
                s = key.split(":")[0]
                if m < 5:
                    if s not in first_early:
                        first_early[s] = (t.strftime("%H:%M"), title.split("EARLY: ")[1].split(" (")[0].split(" on ")[0], rows[s][0], rows[s][4])
                elif s not in first_full and not key.endswith(":basebreak"):
                    first_full[s] = (t.strftime("%H:%M"), key.split(":")[1], rows[s][0])
        for s in set(first_early) | set(first_full):
            a = A[s]
            i = pos[s][cal[k]]
            e, f = first_early.get(s), first_full.get(s)
            ref = e[2] if e else f[2]
            res.append(dict(day=cal[k], sym=s, early=e, full=f, close=float(a.st.c[i]), day_low=float(a.st.l[i]),
                            close_vs=round(100 * (a.st.c[i] / ref - 1), 1), rv_early=e[3] if e else None))
        perday.append((cal[k], len(first_early), len(first_full), len(cand)))
        print(cal[k], "heads-ups", len(first_early), "full alerts", len(first_full), "candidates", len(cand), file=sys.stderr)
    ups = [r for r in res if r["early"]]
    conf935 = [r for r in ups if r["full"] and r["full"][0] == "09:35"]
    conf10 = [r for r in ups if r["full"]]
    noconf = [r for r in ups if not r["full"]]
    fulls = [r for r in res if r["full"]]
    rv_c = sorted(r["rv_early"] for r in conf10 if r["rv_early"] is not None)
    rv_n = sorted(r["rv_early"] for r in noconf if r["rv_early"] is not None)
    q = lambda xs: [xs[int(p * (len(xs) - 1))] for p in (0.1, 0.25, 0.5, 0.75)] if xs else None
    by_rv = {}
    for lo_ in (0, 1, 2, 3, 5):
        sub = [r for r in ups if r["rv_early"] is not None and r["rv_early"] >= lo_]
        by_rv[f"rv {lo_}+ at the heads-up"] = dict(n=len(sub), confirmed_by_10=round(100 * sum(1 for r in sub if r["full"]) / len(sub)) if sub else None)
    by_kind = {}
    for kind in ("power-day gap", "catalyst gap", "launch gap"):
        sub = [r for r in ups if r["early"][1] == kind]
        by_kind[kind] = dict(n=len(sub), confirmed_935=sum(1 for r in sub if r["full"] and r["full"][0] == "09:35"),
                             confirmed_by_10=sum(1 for r in sub if r["full"]),
                             unconfirmed_closed_above=sum(1 for r in sub if not r["full"] and r["close_vs"] > 0))
    return dict(days=len(perday), per_day=perday, headsups=len(ups), per_day_avg=round(len(ups) / max(1, len(perday)), 1),
                max_day=max((p[1] for p in perday), default=0), confirmed_at_935=len(conf935), confirmed_by_10=len(conf10),
                unconfirmed=len(noconf), unconfirmed_closed_above_headsup=sum(1 for r in noconf if r["close_vs"] > 0),
                unconfirmed_avg_close_vs=round(float(np.mean([r["close_vs"] for r in noconf])), 1) if noconf else None,
                full_alerts=len(fulls), full_with_headsup=sum(1 for r in fulls if r["early"]),
                rv_at_headsup_confirmed_q10_25_50_75=q(rv_c), rv_at_headsup_unconfirmed_q10_25_50_75=q(rv_n), by_rv=by_rv, by_kind=by_kind,
                full_without_headsup=[(r["day"], r["sym"], r["full"]) for r in fulls if not r["early"]][:40],
                rows=sorted(res, key=lambda r: (r["day"], r["sym"])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--volprofile", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--days", type=int, default=60)
    a = ap.parse_args()
    A, groups, GS, cal, S = launch.load(a.bars, a.stocks)
    D = run.load_bars(a.bars)
    mcap = D.get("market_cap", {})
    rec = recent_launches(A, groups, GS, cal)
    out = {"made_at": datetime.datetime.now(UTC).isoformat(timespec="seconds"), "first": cal[200], "last": cal[-1]}
    out["part1"] = part1(A, rec, mcap, cal)
    print(json.dumps({k: (v["per_month"] if "per_month" in v else None, v["from_open"], v["from_close"]) for k, v in out["part1"].items()}, indent=0)[:6000])
    json.dump(out, open(a.out, "w"), indent=1)
    if os.environ.get("ALPACA_KEY_ID"):
        prof = json.load(open(a.volprofile))["rows"]
        out["part2"] = part2(A, groups, GS, cal, rec, prof, a.days)
        print(json.dumps({k: v for k, v in out["part2"].items() if k not in ("rows", "per_day")}, indent=1)[:6000])
    json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
