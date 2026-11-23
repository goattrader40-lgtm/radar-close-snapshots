#!/usr/bin/env python3
"""Check of the EP pullback alerts on today's exact minute bars (a check tool, not part of the live jobs).

  python3 radar/probe_epp.py <setups/ep_pullback.json> <out.json>   (needs ALPACA_KEY_ID / ALPACA_SECRET; run after 4:16 PM ET
                                                                     for the whole session: the last 16 minutes aren't out)

For every stock of the plan (the evening file the live job read today) it fetches today's 1-minute SIP bars and replays
radar/epp.py minute by minute, exactly as radar/alerts.py find_epp calls it: when READY, BUY or off first show, for each
play that was waiting; and, for the plays that were not waiting, whether the EMA level was touched at all. It also reads
the daily bars (split-adjusted) to recompute the 10 / 21 EMA at the last close and the EP day's close / low, so the plan's
own numbers can be compared with a second source. Nothing is alerted, nothing on main is read or written."""
import datetime, json, os, sys, urllib.parse, urllib.request, zoneinfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epp

NY = zoneinfo.ZoneInfo("America/New_York")
UTC = datetime.timezone.utc
HDR = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
z = lambda t: t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
FETCH_PCT = 5.0      # radar/alerts.py EPP_FETCH_PCT


def alpaca(q):
    bars = {}
    q = dict(q)
    while True:
        req = urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q), headers=HDR)
        with urllib.request.urlopen(req, timeout=60) as r:
            res = json.load(r)
        for s, rows in (res.get("bars") or {}).items():
            bars.setdefault(s, []).extend(rows)
        if not res.get("next_page_token"):
            return bars
        q["page_token"] = res["next_page_token"]


def ema(vals, n):
    k, e, out = 2 / (n + 1), None, []
    for v in vals:
        e = v if e is None else e + k * (v - e)
        out.append(e)
    return out


def main():
    plan_p, out_p = sys.argv[1:3]
    plan = json.load(open(plan_p))
    rows = plan.get("rows") or {}
    syms = sorted(rows)
    now = datetime.datetime.now(NY)
    day = now.date() if len(sys.argv) < 4 else datetime.date.fromisoformat(sys.argv[3])
    t0 = datetime.datetime(day.year, day.month, day.day, 9, 30, tzinfo=NY)
    end = min(now - datetime.timedelta(minutes=16), t0 + datetime.timedelta(minutes=390))
    out = {"day": str(day), "plan_date": plan.get("date"), "made_at": now.isoformat(timespec="seconds"),
           "bars_to": end.strftime("%H:%M"), "rows": {}, "errors": []}
    try:
        mins = alpaca({"symbols": ",".join(syms), "timeframe": "1Min", "feed": "sip", "adjustment": "raw", "limit": 10000,
                       "start": z(t0), "end": z(end)})
    except Exception as e:
        out["errors"].append(f"minute bars: {e!r}")
        mins = {}
    try:
        d0 = datetime.datetime(day.year, day.month, day.day, tzinfo=NY) - datetime.timedelta(days=560)
        days = alpaca({"symbols": ",".join(syms), "timeframe": "1Day", "feed": "sip", "adjustment": "split", "limit": 10000,
                       "start": z(d0), "end": z(end)})
    except Exception as e:
        out["errors"].append(f"daily bars: {e!r}")
        days = {}
    for s in syms:
        r = rows[s]
        bars = []
        for b in mins.get(s) or []:
            d = datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(NY)
            m = d.hour * 60 + d.minute - 570
            if d.date() == day and 0 <= m < 390:
                bars.append((m, b["o"], b["h"], b["l"], b["c"], b["v"]))
        bars.sort()
        o = {"plan": r, "n_bars": len(bars)}
        if bars:
            lo = min(b[3] for b in bars)
            hi = max(b[2] for b in bars)
            o.update(open=bars[0][1], high=hi, low=lo, last=bars[-1][4],
                     low_at=epp.hhmm(next(b[0] for b in bars if b[3] == lo)), high_at=epp.hhmm(next(b[0] for b in bars if b[2] == hi)))
            vw, lows = epp.vwap_lows(bars)
            # the 15-minute candles: [start, open, high, low, close, VWAP at its end, the day's low at its end]
            c15 = {}
            for j, b in enumerate(bars):
                w = b[0] // 15
                c = c15.setdefault(w, [epp.hhmm(w * 15), b[1], b[2], b[3], b[4], None, None])
                c[2], c[3], c[4], c[5], c[6] = max(c[2], b[2]), min(c[3], b[3]), b[4], round(vw[j], 4), lows[j]
            o["c15"] = [c15[w] for w in sorted(c15)]
            o["bars"] = [[b[0], b[1], b[2], b[3], b[4], b[5]] for b in bars]
            last_m = bars[-1][0] + 1
            for play in ("10", "21"):
                p = r.get("p" + play) or {}
                lv = p.get("level")
                if lv is None:
                    continue
                jt = next((b for b in bars if b[3] <= lv), None)
                res = {"status": p.get("status"), "level": lv, "touch_at": epp.hhmm(jt[0]) if jt else None}
                if play == "10":
                    jd = next((b for b in bars if b[3] < r["c0"]), None)
                    res["under_ep_close_at"] = epp.hhmm(jd[0]) if jd else None
                else:
                    jl = next((b for b in bars if b[3] < r["l0"]), None)
                    res["under_ep_low_at"] = epp.hhmm(jl[0]) if jl else None
                # minute by minute, as find_epp sees it (now_min = the minutes since 9:30 at the run; only finished minutes)
                first = {}
                ready_gate = None
                for nowm in range(1, last_m + 1):
                    c = epp.check(bars, play, lv, r["c0"], r["l0"], floor=p.get("floor") if play == "10" else None, now_min=nowm)
                    for k in ("ready", "buy", "off"):
                        if c[k] and k not in first:
                            first[k] = {"seen_at": epp.hhmm(nowm), "value": c[k]}
                    # the 5-minute run reads the chart only when the price is within 5% over the level (or once READY)
                    if ready_gate is None and nowm % 5 == 0 and c["ready"] and not c["buy"] and not c["off"]:
                        px = next((b[4] for b in reversed(bars) if b[0] < nowm), None)
                        if px is not None and px <= lv * (1 + FETCH_PCT / 100):
                            ready_gate = epp.hhmm(nowm)
                    if c["buy"] or c["off"]:
                        break
                res["first"] = first
                res["ready_at_5min_run"] = ready_gate
                whole = epp.check(bars, play, lv, r["c0"], r["l0"], floor=p.get("floor") if play == "10" else None,
                                  now_min=None if last_m >= 390 else last_m)
                res["end"] = {k: whole[k] for k in ("ready", "buy", "off", "low", "vwap")}
                o["p" + play] = res
        db = [b for b in (days.get(s) or [])]
        dd = [(datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(NY).date().isoformat(), b) for b in db]
        dd = [x for x in dd if x[0] < str(day)]
        if len(dd) > 60:
            cl = [b["c"] for _, b in dd]
            e10, e21 = ema(cl, 10), ema(cl, 21)
            o["daily"] = {"n": len(dd), "last": dd[-1][0], "close": cl[-1], "e10": round(e10[-1], 4), "e10_prev": round(e10[-2], 4),
                          "e21": round(e21[-1], 4), "e21_prev": round(e21[-2], 4)}
            pos = {d: i for i, (d, _) in enumerate(dd)}
            j = pos.get(r.get("ep"))
            if j:
                b = dd[j][1]
                o["daily"]["ep"] = {"date": dd[j][0], "open": b["o"], "high": b["h"], "low": b["l"], "close": b["c"], "prev_close": dd[j - 1][1]["c"],
                                    "gap_pct": round(100 * (b["o"] / dd[j - 1][1]["c"] - 1), 2), "sessions_to_today": len(dd) - j,
                                    "min_close_since": min([x[1]["c"] for x in dd[j + 1:]] or [None], default=None) if len(dd) > j + 1 else None,
                                    "min_low_since": min([x[1]["l"] for x in dd[j + 1:]] or [None], default=None) if len(dd) > j + 1 else None}
                # the first earlier touch of each EMA after the EP day (a low at or under the EMA of the day before)
                for name, em in (("t10", e10), ("t21", e21)):
                    t = next((q for q in range(j + 1, len(dd)) if dd[q][1]["l"] <= em[q - 1]), None)
                    o["daily"][name] = dd[t][0] if t is not None else None
            o["daily"]["tail"] = [[d, b["o"], b["h"], b["l"], b["c"], b["v"]] for d, b in dd[-25:]]
        out["rows"][s] = o
    # the plan's completeness: every name on the 1-EP/GAP list that is NOT in the plan gets its plays' status worked out here
    # from the daily bars (the same rules as scanner/launch.py write_ep_pullback, written again on purpose), so a name the
    # plan should carry but doesn't would show
    try:
        lst = (json.load(open(os.path.join(os.path.dirname(os.path.abspath(plan_p)), "latest.json"))).get("lists") or {}).get("1-EP/GAP") or []
        extra = {r["symbol"]: r for r in lst if r.get("symbol") and r["symbol"] not in rows}
        P = plan.get("rules") or {}
        n10, n21, fl = int(P.get("e10_max_sessions", 10)), int(P.get("e21_max_sessions", 30)), float(P.get("e10_floor_pct", 5))
        xd = alpaca({"symbols": ",".join(sorted(extra)), "timeframe": "1Day", "feed": "sip", "adjustment": "split", "limit": 10000,
                     "start": z(d0), "end": z(end)}) if extra else {}
        audit = {}
        for s, r in extra.items():
            dd = [(datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(NY).date().isoformat(), b) for b in xd.get(s) or []]
            dd = [x for x in dd if x[0] <= str(plan.get("date"))]
            a = {"added": r.get("added"), "why": r.get("why"), "n": len(dd)}
            pos = {d: i for i, (d, _) in enumerate(dd)}
            j = pos.get(r.get("added"))
            if j is None or j < 1 or len(dd) < 60:
                a["note"] = "no bars for its EP day"
                audit[s] = a
                continue
            cl = [b["c"] for _, b in dd]
            lo = [b["l"] for _, b in dd]
            e10, e21 = ema(cl, 10), ema(cl, 21)
            i = len(dd) - 1
            c0, l0, days = cl[j], lo[j], i + 1 - j
            a.update(ep=dd[j][0], c0=c0, l0=l0, gap=round(100 * (dd[j][1]["o"] / cl[j - 1] - 1), 2), days=days, close=cl[i])
            for name, em, lim in (("p10", e10, n10), ("p21", e21, n21)):
                t = next((q for q in range(j + 1, i + 1) if lo[q] <= em[q - 1]), None)
                up = em[i] > em[i - 1]
                if t is not None:
                    stt = "used " + dd[t][0]
                elif days > lim:
                    stt = "late"
                elif name == "p10" and i > j and min(cl[j + 1:i + 1]) < c0 * (1 - fl / 100):
                    stt = "out"
                elif name == "p21" and i > j and min(lo[j + 1:i + 1]) < l0:
                    stt = "out"
                else:
                    stt = "wait" if up else "flat"
                a[name] = {"level": round(em[i], 4), "up": up, "status": stt}
            audit[s] = a
        out["list_audit"] = audit
    except Exception as e:
        out["errors"].append(f"list audit: {e!r}")
    with open(out_p, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print("epp check:", len(out["rows"]), "stocks,", sum(1 for o in out["rows"].values() if o.get("n_bars")), "with minute bars; errors:", out["errors"])


if __name__ == "__main__":
    try:
        main()
    except Exception as e:                       # the job's log can't be read from a session: the error goes into the file
        import traceback
        with open(sys.argv[2], "w") as f:
            json.dump({"errors": [repr(e), traceback.format_exc()[-1500:]]}, f)
        print("epp check failed:", repr(e))
