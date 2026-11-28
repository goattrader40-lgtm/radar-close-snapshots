#!/usr/bin/env python3
"""1-minute quotes for the stocks that can alert, between the 5-minute live updates.

  python3 radar/fast.py <launch.json> <stocks.json> <volprofile.json> <sipcal.json> <out.json> [--morning <settings.json>] [--earnings <earnings.json>]

The launch watch list (setups/launch.json, a few hundred stocks), so a big gap-up on volume (a catalyst gap, a power
day, an A+/A launch) alerts within a minute (and the names only the EP / power day alert reads: launch.json ep_watch) instead of up to five (HRI crossed its 200 SMA between the 9:35 and the
9:40 update on Oct 27, 2026), plus the launches being followed, for their breakouts (LION crossed its buy point at
3:08 PM on Oct 29, 2026 and the 5-minute update saw it at 3:11). Writes live.json-shaped rows for those stocks only, Rel vol as radar/live.py works it out,
with the volume correction the last live update measured (radar/sipcal.py). radar/alerts.py reads it like live.json.
In the morning breakout window (radar/alerts.py, the user's settings: 9:35-10:30 by default) also every stock that can
pass those settings (the liquidity and the ADR, the price rules on the last close with 30% room), so a morning breakout of
any stock alerts within a minute (the user, Nov 9 2026: "usually they alert at 9:36-9:45"). And the stocks reacting to
earnings today (the Earnings tab's rows), for the earnings breakdown, the short side (the user, Nov 28 2026).
"""
import datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sipcal  # noqa: E402
from live import NY, Yahoo, fill_opens, rvol_at, yahoo_sym  # noqa: E402
from alerts import load_morning, load_morning2, in_morning, morning_static, res_setup, EBD_LIQ, EBD_TO, ebd_reacts, ebd_rows, find_ebd  # noqa: E402


def main():
    launch_p, stocks_p, prof_p, cal_p, out_p = sys.argv[1:6]
    now = datetime.datetime.now(NY)
    doc = json.load(open(launch_p))
    syms = sorted(set(doc.get("watch", {})) | set(doc.get("ep_watch") or {}) | {r["symbol"] for r in doc.get("launches", []) + doc.get("ema50_undercut", []) + doc.get("laggards", [])})   # + the 50 EMA undercut tab: its reclaim within a minute
    syms = sorted(set(syms) | {r["symbol"] for r in doc.get("setups3") or [] if r.get("buy_point") or r.get("live")})   # + 3-SETUPS: every entry (Nov 3 2026)
    # + the names the user follows, for the 9:31-9:34 gap heads-up (alerts.py find_early_lists): Start days, every 3-SETUPS
    # name and the Watchlist's lists (setups/latest.json, --lists)
    syms = sorted(set(syms) | {r["symbol"] for r in (doc.get("start_days") or []) + (doc.get("setups3") or []) if r.get("symbol")})
    if "--lists" in sys.argv:
        try:
            for rows_ in (json.load(open(sys.argv[sys.argv.index("--lists") + 1])).get("lists") or {}).values():
                syms = sorted(set(syms) | {r["symbol"] for r in rows_ or [] if isinstance(r, dict) and r.get("symbol")})
        except Exception as e:
            print(f"fast: the Watchlist's lists not read: {e!r}", file=sys.stderr)
    try:
        prof = json.load(open(prof_p))["rows"]
    except Exception:
        prof = {}
    SL = json.load(open(stocks_p))
    avg20 = {r["symbol"]: r.get("avg_vol_20") for r in SL}
    if "--morning" in sys.argv:                         # the morning breakout window: every stock that can pass the settings
        res_setup(doc)                                  # (the resistance levels a ticked box needs, the followed names)
        M = load_morning(sys.argv[sys.argv.index("--morning") + 1])
        # + the second box (the stocks not in trend; its own settings, or the first box's with the trend boxes off)
        M2 = load_morning2(sys.argv[sys.argv.index("--morning2") + 1] if "--morning2" in sys.argv else None, M)
        for M_ in (M, M2):
            if in_morning(M_, now) or in_morning(M_, now + datetime.timedelta(minutes=1)):
                syms = sorted(set(syms) | {r["symbol"] for r in SL if morning_static(r, M_, slack=0.3)})
    # + today's earnings gap-downs, for the earnings breakdown, the short side (alerts.py find_ebd; the user, Nov 28 2026): the
    # Earnings tab's rows reacting today (--earnings) and the ones the last full update saw gapping down 8%+ on earnings
    # (a stock the tab doesn't list), so the break of the first 3-minute candle's low alerts within a minute
    if (now.hour, now.minute) < EBD_TO:
        try:
            S_, today = {r["symbol"]: r for r in SL}, now.date().isoformat()
            E_ = ebd_rows(sys.argv[sys.argv.index("--earnings") + 1]) if "--earnings" in sys.argv else {}
            rep = {s_ for s_, r in E_.items() if ebd_reacts(r, today, doc.get("date"))}
            lp = os.path.join(os.path.dirname(os.path.abspath(out_p)), "live.json")
            if os.path.exists(lp):
                rep |= set(find_ebd(json.load(open(lp)), S_, E_, doc, now))
            syms = sorted(set(syms) | {s_ for s_ in rep if s_ in S_ and morning_static(S_[s_], EBD_LIQ)})
        except Exception as e:
            print(f"fast: today's earnings gap-downs not read: {e!r}", file=sys.stderr)
    off = sipcal.saved(cal_p, now.date())
    ymap = {yahoo_sym(s): s for s in syms}
    y = Yahoo()
    if not y.login():
        sys.exit("fast: no Yahoo crumb")
    rows = {}
    got = y.quotes(list(ymap))
    opened = fill_opens(y, got, now)                    # the movers' opens from the chart in the first 20 minutes (NYSE)
    for k, v in got.items():
        s = ymap.get(k)
        if not s:
            continue
        price, chg, vol, qt, op, ern, hi = v
        fv = sipcal.corrected(vol, qt, off.get(s))
        vol = vol if fv is None else fv
        rows[s] = [price, chg, vol, qt, rvol_at(vol, qt, prof.get(s), avg20.get(s)), op, ern, hi]
    if len(rows) < 0.5 * len(syms):
        sys.exit(f"fast: only {len(rows)} of {len(syms)} quotes")
    times = sorted(v[3] for v in rows.values() if v[3])
    session = datetime.datetime.fromtimestamp(times[len(times) // 2], NY).date().isoformat() if times else now.date().isoformat()
    json.dump({"saved_at": now.isoformat(timespec="seconds"), "date": now.date().isoformat(), "session": session,
               "n": len(rows), "source": "yahoo quote (1-minute watch list)", "rows": rows}, open(out_p, "w"), separators=(",", ":"))
    print(f"fast: {len(rows)} quotes, {sum(1 for s in rows if s in off)} volume-corrected, open from the chart: {' '.join(f'{ymap.get(k, k)} {o}' + (f' (quote {q})' if q != o else '') for k, q, o in opened) or '-'}")


if __name__ == "__main__":
    main()
