#!/usr/bin/env python3
"""The evening list of parabolic shorts (the user, Nov 28 2026; the rule and its study: radar/para.py).

  python3 scanner/parabolic.py --out setups/parabolic.json [--alerts <radar-data alerts.json>] [--asof YYYY-MM-DD]

Its own data: the scanner's bars hold only the stocks over $700M, and most of these runs are smaller (BYND Oct 2025), so
this reads every common stock on NASDAQ / NYSE / AMEX from Alpaca (the asset list, then ~3 months of daily bars, SIP,
split-adjusted; about 40 requests). Run by scanner.yml after the Watchlist and Launches steps, as a step that may fail
without touching them (continue-on-error): on any error the file is left as it was.

Writes setups/parabolic.json:
  date     the session the list was made on (the last close)
  rules    radar/para.py RULES
  rows     {SYM: {tv, name, close, gain3 (% the last 3 sessions added), up_days, dvol_m ($M traded), run20 (% over the
           20-session low close), lo20, need_open (the open it needs: 3%+ over the close, 130%+ over lo20, $5+), gap_need %}}
           the stocks that closed up 3+ sessions in a row, +50% in 3, on $20M+; on the list for the next session only
  shorts   the SHORT alerts (radar/alerts.py find_para, from radar-data alerts.json --alerts), followed to the cover:
           {symbol, tv, date, time, kind "opening low" | "re-entry", entry, stop, status, exit, exit_date, pct, r}
           status: "open" (cover at the next close) -> "covered" (the next session's close) / "stopped next day" (its high
           reached the stop: out at the stop, at the open when it opened over it); "stopped" = the same day. A closed one
           stays 10 sessions."""
import collections, datetime, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request, zoneinfo

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "radar"))
import para  # noqa: E402

NY = zoneinfo.ZoneInfo("America/New_York")
# not a common stock: funds, notes, warrants, units, rights, preferreds, leveraged products
BAD = re.compile(r"\b(ETF|ETN|FUND|TRUST|WARRANT|WARRANTS|UNIT|UNITS|RIGHT|RIGHTS|PREFERRED|NOTES|DEPOSITARY SHARES? EACH|%|BULL|BEAR|2X|3X|PROSHARES|DIREXION)\b", re.I)
KEEP_SESSIONS = 10


def hdr():
    return {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}


def get(url):
    err = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=hdr()), timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            err = e
            if e.code == 429 or e.code >= 500:
                time.sleep(5 * (attempt + 1))
                continue
            raise
        except Exception as e:
            err = e
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"alpaca kept failing ({err!r}): {url[:100]}")


def assets():
    """{symbol: {name, exchange}}: the active common stocks on NASDAQ / NYSE / AMEX (the keys answer on one of the two hosts)"""
    out, errs = {}, []
    for host in ("https://paper-api.alpaca.markets", "https://api.alpaca.markets"):
        try:
            rows = get(f"{host}/v2/assets?asset_class=us_equity&status=active")
        except Exception as e:
            errs.append(f"{host}: {e!r}")
            continue
        for a in rows:
            s = a.get("symbol") or ""
            if a.get("exchange") in ("NASDAQ", "NYSE", "AMEX") and re.fullmatch(r"[A-Z]{1,5}", s) and not BAD.search(a.get("name") or ""):
                out[s] = {"name": (a.get("name") or "")[:60], "exchange": a["exchange"]}
        if out:
            return out
    raise RuntimeError("no asset list: " + "; ".join(errs))


def daily(syms, start, end):
    """{symbol: [(date, o, h, l, c, v)]} since start, up to end (a time 16+ minutes ago: the free plan's limit on recent SIP data)"""
    out = collections.defaultdict(list)
    for k in range(0, len(syms), 200):
        token = None
        while True:
            q = {"symbols": ",".join(syms[k:k + 200]), "timeframe": "1Day", "feed": "sip", "adjustment": "split", "limit": 10000,
                 "start": start, "end": end}
            if token:
                q["page_token"] = token
            res = get("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q))
            for s, bs in (res.get("bars") or {}).items():
                out[s].extend((b["t"][:10], b["o"], b["h"], b["l"], b["c"], b["v"]) for b in bs)
            token = res.get("next_page_token")
            time.sleep(0.32)                 # the free plan's 200 requests a minute
            if not token:
                break
    return {s: sorted(set(b)) for s, b in out.items()}


def build(bars, meta, asof, prev=None, alerts=None):
    """the file's content from the daily bars ({sym: bars}, already cut at asof), the asset names, the last file and today's alert state"""
    rows = {}
    for s, b in bars.items():
        if not b or b[-1][0] != asof:
            continue
        r = para.list_row(b[-25:])
        if r:
            m = meta.get(s) or {}
            r.pop("high", None)
            rows[s] = {"tv": f"{m.get('exchange', 'NASDAQ')}:{s}", "name": m.get("name", ""), **r}
    shorts = [dict(x) for x in ((prev or {}).get("shorts") or [])]
    # the open shorts of an earlier session: the next session's bar decides (the stop first, else its close)
    for x in shorts:
        if x.get("status") != "open" or x.get("date", "9") >= asof:
            continue
        nxt = next((b for b in bars.get(x["symbol"], []) if b[0] > x["date"]), None)
        if not nxt:
            continue
        if nxt[2] >= x["stop"]:
            x["status"], x["exit"] = "stopped next day", round(max(x["stop"], nxt[1]), 4)
        else:
            x["status"], x["exit"] = "covered", nxt[4]
        x["exit_date"] = nxt[0]
        x["pct"] = round((x["entry"] - x["exit"]) / x["entry"] * 100, 1)
        x["r"] = round((x["entry"] - x["exit"]) / (x["stop"] - x["entry"]), 2)
    # today's SHORT alerts (alerts.json: state["para"], radar/alerts.py find_para)
    if alerts and alerts.get("date") == asof:
        have = {(x["symbol"], x["date"], x["kind"]) for x in shorts}
        tv_of = {s: r.get("tv") for s, r in ((prev or {}).get("rows") or {}).items()}
        for s, m in (alerts.get("para") or {}).items():
            close = (bars.get(s) or [(None,) * 5])[-1][4] if bars.get(s) and bars[s][-1][0] == asof else None
            for kind, e, stopped in (("opening low", m.get("short"), m.get("stopped")), ("re-entry", m.get("re"), m.get("stopped2"))):
                if not e or (s, asof, kind) in have:
                    continue
                x = {"symbol": s, "tv": tv_of.get(s) or (f"{meta[s]['exchange']}:{s}" if s in meta else s), "date": asof, "time": e.get("time"),
                     "kind": kind, "entry": e["px"], "stop": e["stop"]}
                if stopped:
                    x.update(status="stopped", exit=e["stop"], exit_date=asof, pct=round((e["px"] - e["stop"]) / e["px"] * 100, 1), r=-1.0)
                else:
                    x.update(status="open", close=close, pct_now=round((e["px"] - close) / e["px"] * 100, 1) if close else None)
                shorts.append(x)
    # a closed one stays KEEP_SESSIONS sessions (by the sessions any stock traded since)
    days = sorted({b[0] for bs in list(bars.values())[:400] for b in bs})
    keep_from = days[-KEEP_SESSIONS] if len(days) >= KEEP_SESSIONS else "0"
    shorts = [x for x in shorts if x.get("status") == "open" or (x.get("exit_date") or x["date"]) >= keep_from]
    shorts.sort(key=lambda x: (x["date"], x.get("time") or ""), reverse=True)
    return {"date": asof, "made_at": datetime.datetime.now(NY).isoformat(timespec="seconds"), "rules": dict(para.RULES),
            "rows": dict(sorted(rows.items(), key=lambda kv: -kv[1]["run20"])), "shorts": shorts}


def main():
    arg = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None
    out_p, asof_arg = arg("--out"), arg("--asof")
    now = datetime.datetime.now(datetime.timezone.utc)
    A = assets()
    start = (now - datetime.timedelta(days=95)).strftime("%Y-%m-%dT00:00:00Z")
    end = (now - datetime.timedelta(minutes=16)).strftime("%Y-%m-%dT%H:%M:%SZ")
    bars = daily(sorted(A), start, end)
    if asof_arg:
        bars = {s: [x for x in b if x[0] <= asof_arg] for s, b in bars.items()}
    last = collections.Counter(b[-1][0] for b in bars.values() if b)
    if not last:
        sys.exit("parabolic: no daily bars")
    asof = last.most_common(1)[0][0]
    # a session still open (a run before the close): its bar is not a close: the last finished session
    ny = datetime.datetime.now(NY)
    if not asof_arg and asof == ny.date().isoformat() and (ny.hour, ny.minute) < (16, 16):
        bars = {s: [x for x in b if x[0] < asof] for s, b in bars.items()}
        asof = collections.Counter(b[-1][0] for b in bars.values() if b).most_common(1)[0][0]
    prev = None
    if out_p and os.path.exists(out_p):
        try:
            prev = json.load(open(out_p))
        except Exception:
            prev = None
    alerts = None
    if arg("--alerts"):
        try:
            alerts = json.load(open(arg("--alerts")))
        except Exception as e:
            print(f"parabolic: no alert state ({e!r})", file=sys.stderr)
    doc = build(bars, A, asof, prev, alerts)
    doc["stocks"] = sum(1 for b in bars.values() if b and b[-1][0] == asof)
    json.dump(doc, open(out_p, "w"), indent=1)
    print(f"parabolic: {asof}, {doc['stocks']} stocks read, {len(doc['rows'])} on the list ({', '.join(list(doc['rows'])[:12])}), {len(doc['shorts'])} shorts followed")


if __name__ == "__main__":
    main()
