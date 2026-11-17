#!/usr/bin/env python3
"""A history check, nothing live reads it (the user, Nov 16-17 2026): the days when 3+ stocks of one theme or industry
group opened 2-5% up or down together. Is there an edge worth a pre-market group check?

  python3 scanner/probe_groupopen.py --bars BARS.json.gz --out OUT.json.gz [--days 63]     (ALPACA_KEY_ID / ALPACA_SECRET)

Pre-market prices are not stored: the open against the close before, from the daily bars. This job only collects; the
grouping and the tables are made from its file afterwards (so the definitions can be changed without a new run):

  rows[day]  = every liquid stock that day ($10+, $20M+ a day over the 20 sessions before):
               [sym, gap %, open -> close %, close vs the close before %, open -> the close 1 / 3 / 5 / 10 sessions later %,
                the highest high of the next 5 sessions vs the open %, the day's high vs the open %, the low vs the open %]
  orh[day]   = the stocks that gapped 2%+ either way, on Alpaca's 5-minute bars: the user's trade (in over the first 5
               minutes' high, stop under the day's low so far): [sym, the range high, its low, the entry time or null,
               the risk %, the result at the close in R, stopped 0/1, the best R after the entry]
  news[day]  = Alpaca's headlines tagged with those stocks between the close before and 9:30: [time ET, headline, tickers]
"""
import argparse, datetime, gzip, json, os, sys, time, urllib.parse, urllib.request, zoneinfo

NY = zoneinfo.ZoneInfo("America/New_York")
UTC = datetime.timezone.utc
GAP = 2.0


def alpaca(url, q, hdr, key):
    """every page of an Alpaca call -> the merged `key` (bars: {sym: [...]}; news: [...])"""
    out, tok = ({} if key == "bars" else []), None
    for _ in range(60):
        qq = dict(q, **({"page_token": tok} if tok else {}))
        for attempt in range(5):
            try:
                with urllib.request.urlopen(urllib.request.Request(url + "?" + urllib.parse.urlencode(qq), headers=hdr), timeout=60) as r:
                    d = json.load(r)
                break
            except Exception as e:
                if attempt == 4:
                    raise
                time.sleep(3 * (attempt + 1))
        if key == "bars":
            for s, v in (d.get("bars") or {}).items():
                out.setdefault(s, []).extend(v)
        else:
            out += d.get("news") or []
        tok = d.get("next_page_token")
        time.sleep(0.32)
        if not tok:
            break
    return out


def orh_trade(bs):
    """5-minute bars of one session (9:30 on) -> [range high, range low, entry time, risk %, R at the close, stopped, best R]"""
    if len(bs) < 3 or bs[0]["hm"] != "09:30":
        return None
    oh, ol = bs[0]["h"], bs[0]["l"]
    low = ol
    for i, b in enumerate(bs[1:], 1):
        if b["h"] > oh:
            entry = max(oh, b["o"])
            stop = low                                  # the day's low before this bar (inside the bar: not knowable)
            if entry <= stop:
                return [oh, ol, None, None, None, None, None]
            risk = entry - stop
            best, r, stopped = 0.0, None, 0
            if b["c"] < stop:                           # the entry bar itself closed under the day's low: stopped
                return [oh, ol, b["hm"], round(100 * risk / entry, 2), -1.0, 1, 0.0]
            best = max(best, (b["h"] - entry) / risk)
            for c in bs[i + 1:]:
                if c["l"] < stop:
                    r, stopped = -1.0, 1
                    break
                best = max(best, (c["h"] - entry) / risk)
            if r is None:
                r = (bs[-1]["c"] - entry) / risk
            return [oh, ol, b["hm"], round(100 * risk / entry, 2), round(r, 2), stopped, round(best, 2)]
        low = min(low, b["l"])
    return [oh, ol, None, None, None, None, None]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--days", type=int, default=63)
    a = ap.parse_args()
    B = json.load(gzip.open(a.bars, "rt"))["bars"]
    days = [b[0] for b in B["SPY"]][-a.days:]
    first = days[0]
    pc = lambda x, y: round(100 * (x / y - 1), 2) if x and y else None
    rows, spy = {d: [] for d in days}, {}
    for sym, bs in B.items():
        idx = {b[0]: i for i, b in enumerate(bs)}
        for d in days:
            i = idx.get(d)
            if i is None or i < 21:
                continue
            _, o, h, l, c, v = bs[i]
            p = bs[i - 1][4]
            if sym == "SPY":
                spy[d] = [pc(o, p), pc(c, o)]
                continue
            dv = sum(x[4] * x[5] for x in bs[i - 20:i]) / 20
            if p < 10 or dv < 20e6 or not o:
                continue
            f = lambda n: pc(bs[i + n][4], o) if i + n < len(bs) else None
            hi5 = pc(max(x[2] for x in bs[i + 1:i + 6]), o) if i + 5 < len(bs) else None
            rows[d].append([sym, pc(o, p), pc(c, o), pc(c, p), f(1), f(3), f(5), f(10), hi5, pc(h, o), pc(l, o)])
    print("rows:", sum(len(v) for v in rows.values()), "over", len(days), "sessions from", first)
    res = {"days": days, "spy": spy, "rows": rows, "orh": {}, "news": {}, "errors": [],
           "fields": {"rows": ["sym", "gap", "o2c", "c2pc", "f1", "f3", "f5", "f10", "hi5", "h2o", "l2o"],
                      "orh": ["sym", "orh", "orl", "entry", "risk_pct", "r_close", "stopped", "best_r"],
                      "news": ["time ET", "headline", "tickers"]}}
    key, sec = os.environ.get("ALPACA_KEY_ID"), os.environ.get("ALPACA_SECRET")
    if key and sec:
        hdr = {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": sec}
        z = lambda t: t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        spy_days = [b[0] for b in B["SPY"]]
        for d in days:
            syms = sorted(r[0] for r in rows[d] if r[1] is not None and abs(r[1]) >= GAP)
            if not syms:
                continue
            dd = datetime.date.fromisoformat(d)
            t0 = datetime.datetime(dd.year, dd.month, dd.day, 9, 30, tzinfo=NY)
            t1 = datetime.datetime(dd.year, dd.month, dd.day, 16, 0, tzinfo=NY)
            pd_ = datetime.date.fromisoformat(spy_days[spy_days.index(d) - 1])
            tp = datetime.datetime(pd_.year, pd_.month, pd_.day, 16, 0, tzinfo=NY)
            out, got = [], set(syms)
            try:
                for i in range(0, len(syms), 150):
                    ch = syms[i:i + 150]
                    bars = alpaca("https://data.alpaca.markets/v2/stocks/bars",
                                  {"symbols": ",".join(x.replace("/", ".").replace("-", ".") for x in ch), "timeframe": "5Min", "feed": "sip",
                                   "adjustment": "raw", "limit": 10000, "start": z(t0), "end": z(t1 - datetime.timedelta(minutes=1))}, hdr, "bars")
                    for s in ch:
                        bs = [dict(b, hm=datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(NY).strftime("%H:%M"))
                              for b in bars.get(s.replace("/", ".").replace("-", "."), [])]
                        t = orh_trade(bs)
                        if t:
                            out.append([s] + t)
                res["orh"][d] = out
            except Exception as e:
                res["errors"].append(f"bars {d}: {e!r}"[:200])
            try:
                seen, arts = set(), []
                for i in range(0, len(syms), 100):
                    for n in alpaca("https://data.alpaca.markets/v1beta1/news",
                                    {"symbols": ",".join(syms[i:i + 100]), "start": z(tp), "end": z(t0), "limit": 50, "sort": "asc"}, hdr, "news"):
                        if n.get("id") in seen:
                            continue
                        seen.add(n.get("id"))
                        at = datetime.datetime.fromisoformat((n.get("created_at") or "").replace("Z", "+00:00")).astimezone(NY)
                        arts.append([at.strftime("%m-%d %H:%M"), (n.get("headline") or "")[:150], sorted(set(n.get("symbols") or []) & got)[:12],
                                     len(n.get("symbols") or [])])
                res["news"][d] = arts
            except Exception as e:
                res["errors"].append(f"news {d}: {e!r}"[:200])
            print(d, len(syms), "gappers", len(res["orh"].get(d, [])), "with 5-minute bars", len(res["news"].get(d, [])), "headlines", flush=True)
    else:
        res["errors"].append("no Alpaca keys: daily rows only")
    with gzip.open(a.out, "wt") as f:
        json.dump(res, f, separators=(",", ":"))
    print("saved", a.out, os.path.getsize(a.out), "bytes", res["errors"][:5])


if __name__ == "__main__":
    main()
