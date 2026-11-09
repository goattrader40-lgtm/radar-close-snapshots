#!/usr/bin/env python3
"""Replay the morning breakout alert (radar/alerts.py, the user Nov 9 2026) on a day's 1-minute charts.

  python3 radar/probe_morning.py <stocks.json> <volprofile.json> <earnings.json> <out.json> [--settings=FILE] [--day=YYYY-MM-DD] [key=value ...] [SYM ...]

key=value: a setting changed for this replay only (above200=0 e10_e21=0 min_chg=4 ...; 0 / 1 for the tick boxes, "off" for a box left empty).

stocks.json must be the base the live job used that morning (the last close before the day): run it on the day, before
the 4:06 PM refresh. Every stock that can pass the settings' liquidity / ADR (with 30% room for the day's move on the
price rules) gets its 1-minute chart of the last 2 sessions from Yahoo; then each minute from the start to the end of the
window the alert's own tests run on what was known at that minute (the price = the last finished bar's close, the volume
so far with the job's Rel vol curve, yesterday's high, the 5-minute opening range, today's low so far). The first minute
a stock passes is when it would have alerted (the live check runs every minute; its quotes are Yahoo's, these are the
1-minute bars' closes, so a few cents and a minute can differ). The SYMs given (the user's examples) also get the reason
they didn't alert, minute by minute. The fired stocks and the SYMs get the alert's news (today's, else the last 2
sessions' fundamental news). Writes {settings, fired: [...], per_minute: {...}, watch: {...}} (-> radar-data probe_morning.json).
"""
import concurrent.futures, datetime, json, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from alerts import NY, MORNING_DEF, load_morning, morning_static, morning_why_not, morning_alert, hhmm  # noqa: E402
from live import rvol_at  # noqa: E402


def bars_2d(sym):
    """[(datetime, open, high, low, close, volume)] regular hours of the last 2 sessions, 1-minute"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym.replace('/', '-').replace('.', '-'))}?range=2d&interval=1m"
    for _ in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"})
            with urllib.request.urlopen(req, timeout=20) as r:
                res = json.load(r)["chart"]["result"][0]
            qd = res["indicators"]["quote"][0]
            out = []
            for t, o, h, l, c, v in zip(res.get("timestamp") or [], qd["open"], qd["high"], qd["low"], qd["close"], qd["volume"]):
                d = datetime.datetime.fromtimestamp(t, NY)
                if h and l and c and (9, 30) <= (d.hour, d.minute) < (16, 0):
                    out.append((d, o, h, l, c, v or 0))
            return out
        except Exception:
            pass
    return None


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--") and "=" not in x]
    stocks_p, prof_p, earn_p, out_p, watch = a[0], a[1], a[2], a[3], [s.upper() for s in a[4:]]
    opt = {x.split("=", 1)[0]: x.split("=", 1)[1] for x in sys.argv[1:] if x.startswith("--") and "=" in x}
    M = load_morning(opt.get("--settings"))
    for x in sys.argv[1:]:
        if "=" in x and not x.startswith("--"):
            k, v = x.split("=", 1)
            if k in M:
                M[k] = (v == "1") if isinstance(MORNING_DEF.get(k), bool) else (None if v == "off" else v if k in ("start", "end") else float(v))
    day = datetime.date.fromisoformat(opt["--day"]) if "--day" in opt else datetime.datetime.now(NY).date()
    SL = json.load(open(stocks_p))
    S = {s["symbol"]: s for s in SL}
    try:
        prof = json.load(open(prof_p))["rows"]
    except Exception:
        prof = {}
    try:
        E = {r["sym"]: r for r in json.load(open(earn_p)).get("rows", []) if r.get("reported")}
    except Exception:
        E = {}
    cands = sorted({s["symbol"] for s in SL if morning_static(s, M, slack=0.3)} | {w for w in watch if w in S})
    print(f"{len(cands)} stocks to read ({len(watch)} named)")
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        B = dict(zip(cands, ex.map(bars_2d, cands)))
    got = {s: b for s, b in B.items() if b}
    print(f"charts: {len(got)} of {len(cands)}")
    s0, e0 = hhmm(M["start"], (9, 35)), hhmm(M["end"], (10, 30))
    minutes = []
    t = datetime.datetime(day.year, day.month, day.day, s0[0], s0[1], tzinfo=NY)
    while (t.hour, t.minute) <= e0:
        minutes.append(t)
        t += datetime.timedelta(minutes=1)
    fired, per_min, why = {}, {}, {w: [] for w in watch}
    for sym, b in got.items():
        st = S[sym]
        prev = [x for x in b if x[0].date() < day]
        tod = [x for x in b if x[0].date() == day]
        if not prev or not tod or (tod[0][0].hour, tod[0][0].minute) != (9, 30):
            if sym in why:
                why[sym].append(["—", "no 1-minute chart for the day (or no 9:30 bar)"])
            continue
        pd = max(x[0].date() for x in prev)
        pdh = max(x[2] for x in prev if x[0].date() == pd)
        rng = [x for x in tod if x[0] < tod[0][0] + datetime.timedelta(minutes=5)]
        orh, orl = max(x[2] for x in rng), min(x[3] for x in rng)
        prev_c = st.get("price")
        op = tod[0][1]
        last_reason = None
        for m in minutes:
            known = [x for x in tod if x[0] < m]
            if not known or not prev_c:
                continue
            price = known[-1][4]
            vol = sum(x[5] for x in known)
            rv = rvol_at(vol, m.timestamp(), prof.get(sym), st.get("avg_vol_20"))
            q = [price, round(100 * (price / prev_c - 1), 2), vol, m.timestamp(), rv, op]
            r = morning_why_not(st, q, M)
            lv = {"pdh": pdh, "orh": orh, "orl": orl, "low": min(x[3] for x in known), "pd": pd.isoformat()}
            if not r:
                al = morning_alert(sym, st, q, lv, M)
                if al:
                    fired[sym] = {"time": f"{m:%H:%M}", "price": round(price, 2), "chg": q[1], "rv": rv, "pdh": round(pdh, 2), "orh": round(orh, 2),
                                  "low": round(lv["low"], 2), "title": al[0], "msg": al[1]}
                    per_min.setdefault(f"{m:%H:%M}", []).append(sym)
                    if sym in why:
                        why[sym].append([f"{m:%H:%M}", "ALERT"])
                    break
                r = f"not over yesterday's high ${pdh:.2f}" if M.get("over_pdh") and price <= pdh else f"not over the 5-min opening range high ${orh:.2f}"
            if sym in why and r != last_reason:
                why[sym].append([f"{m:%H:%M}", f"${price:.2f} ({q[1]:+.1f}%, vol {rv if rv is not None else '—'}x): {r}"])
            last_reason = r
    news = {}
    syms = [s for s, _ in sorted(fired.items(), key=lambda kv: kv[1]["time"])][:25]
    syms += [w for w in watch if w in S and w not in syms]
    if syms:
        try:
            import codegrade
            at = datetime.datetime(day.year, day.month, day.day, e0[0], e0[1], tzinfo=NY)
            news = codegrade.stock_news(syms, S, E, at, budget=240)
        except Exception as ex:
            print("news:", repr(ex)[:200])
    for s, x in news.items():
        if s in fired:
            fired[s]["news"] = x
    out = {"day": day.isoformat(), "settings": M, "read": len(got), "fired_n": len(fired),
           "fired": sorted(({"symbol": s, **v} for s, v in fired.items()), key=lambda x: (x["time"], -x["chg"])),
           "per_minute": {k: per_min[k] for k in sorted(per_min)}, "watch": {w: {"steps": why.get(w, []), "news": news.get(w)} for w in watch}}
    json.dump(out, open(out_p, "w"), indent=1, default=str)
    print(f"{len(fired)} would have alerted; by minute: " + ", ".join(f"{k} {len(v)}" for k, v in out["per_minute"].items()))


if __name__ == "__main__":
    main()
