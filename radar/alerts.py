#!/usr/bin/env python3
"""Phone alerts (ntfy) from the 5-minute live prices: launches and breakouts as they happen.

  python3 radar/alerts.py <live.json> <launch.json> <alerts.json> [--fast]   (NTFY_TOPIC set: sends; unset: only logs)

Every 5 minutes with the live prices; every minute in between (--fast, radar/fast.py: 9:31-12:00 and 3:00-4:00) for
the big gap-ups on volume (catalyst gaps and their 2nd trigger, power days, A+/A launches) and the followed launches'
breakouts. 9:31-9:34 (the 1-minute check only): the early heads-up (find_early), the shape of such a gap before its
volume can be read.

Alerts, each stock and kind once a day (alerts.json keeps what was sent, on the radar-data branch):
  power day   volume pace 4x+ for the time of day, a 10%+ gap, up 15%+, above the 200 SMA, at most 50% over it
  catalyst    an episodic pivot, the moment it happens: a neglected stock (closed under its 50 EMA or 200 SMA the
              day before) gaps up 5%+ on earnings or news with volume pace 3x+ and trades above both the 50 EMA and
              the 200 SMA. No base breakout needed, and no clean base either (HRI on Oct 27 2026: earnings, gapped 9.3%
              from under both out of a choppy chart; the launch alert waited for its 20-day high). It says whether
              the base high is cleared yet; if not, a 2nd trigger follows when it is (volume 1x+). Such a stock
              gets these two instead of a launch alert. Earnings = reported after the last close; without
              earnings it says to check the news
  launch      A+ or A off the watch list (setups/launch.json, from the last close), graded like the portal's
              Launching today: volume pace 3x+ and above its base high (the previous 20 days' high), with a 3%+
              gap or a 10%+ day; A+ = a 6%+ gap jumping from under the 200 SMA. Also needs: up 5%+, opened up,
              above the 200 SMA, and the day before at most 28% over it. A faded high-volume gap that held its
              base (a delayed launch) gets that day's volume and gap.
  breakout    a launch being followed clears its buy point (the nearest of: your MSF pattern's pivot, the flag
              trendline, the smaller or the larger base's top), whatever the volume: the alert shows the volume pace
              for the time of day and says when it is light (ATRC Aug 7 2026 over 41.29 on 0.6x, Oct 29 over 61.70),
              after closing under it the day before; graded from 2 years of data (grade_breakout): A = an early
              breakout (1st / 2nd, within 50 sessions of the launch) in a leading theme with volume building before,
              B = early plus one of those, C = the rest
  touch       a launch being followed traded over its buy point (today's high) but is back under it at the check: not a
              breakout, a heads-up (LION Oct 29 2026 touched $12.98 at 1:26 PM and fell back between two 5-minute updates)
  confirm     in the 3 sessions after a base breakout, it opens and trades above the base top on 2x+ volume
  pop         the entry inside a base: after its resting time (the volume dried up, surfing the 10 & 21 EMA) and a
              tight candle, it opens above that candle's open and close and above the rising 10 & 21 EMA (ANF Oct 5 2026)
  zone        a heads-up: a launch being followed pulls back into the retest zone of its last breakout (from 1.5 ADRs
              under the top of the broken base's bodies to a quarter ADR over its wick top), after a real pullback (1.5
              ADRs off the high since) and having closed 1.25 ADRs away first; with the 10 / 21 / 50 EMA there if they are
              (GMAB Oct 2 2026: down to 33.72 under its 34.63 level, the 21 EMA 34.39 there)
  retest      from 3:45 PM: today's low came into that zone as the pullback's new low and it trades back over the
              bodies' top and the 21 EMA: the retest holding into the close (the buy: at the close, if it holds); high
              priority with an EMA there too. The scan after the close confirms it (radar/eod_alerts.py). One per breakout
              (GMAB Oct 2 2026: down to 33.72 under 34.63, back to 34.75 over it and the 21 EMA; ANF Aug 17-18 closed
              under the 21 EMA: no retest)
  push        within 5 sessions of the retest's first touch, the day before still at the EMAs: it opens over that
              day's open and close and its 10 & 21 EMA, pushing out of the 21 EMA with a gap (ANF Aug 21 2026)
Nothing but the early heads-ups is sent before 9:35 ET (the volume pace is rough in the first minutes). ntfy is a free phone app:
subscribe to the topic in the NTFY_TOPIC secret.
"""
import datetime, json, os, sys, urllib.request, zoneinfo

NY = zoneinfo.ZoneInfo("America/New_York")
MAX_PER_RUN = 8


def grade(rv, bo, gap, chg, R, under):
    vol3, gap3, big = rv >= R["rv_big"], gap is not None and gap >= R["gap_big"], chg >= R["chg_big"]
    if vol3 and bo and under and gap is not None and gap >= R["aplus_gap"]:
        return "A+"
    if vol3 and bo and (gap3 or big):
        return "A"
    return "B" if int(vol3) + int(bo) + int(gap3) + int(big) >= 2 else "C"


def grade_breakout(r):
    """the breakout grade, from what separated the ones that worked (2 years, 906 base breakouts after launches):
    early = the 1st or 2nd breakout since the launch, within 50 sessions of it; the theme Leading; the volume building
    the 5 days before (1.1x+ the 50 before). A = all three (62% ran 10%+ in 20 days, 35% ran 20%+); B = early plus
    one of the others (51% / 24%); C = the rest (40% / 15%). The day's volume and 'turning up' themes didn't help."""
    early = (r.get("breakouts") or 0) < 2 and (r.get("sessions") or 0) + 1 < 50
    lead = r.get("group_status_now") == "Leading"
    build = (r.get("vol_build") or 0) >= 1.1
    g = "A" if early and lead and build else "B" if early and (lead or build) else "C"
    why = [("1st" if not r.get("breakouts") else "2nd") + " breakout since the launch" if early else "late (3rd+ breakout or 50+ sessions on)",
           "theme leading" if lead else f"theme {(r.get('group_status_now') or 'none').lower()}"] + (["volume building"] if build else [])
    return g, ", ".join(why)


def find_early(live, doc, now=None):
    """the early heads-up, 9:31-9:34 (every minute): the shape of a big gap-up from the first minutes' prices, before
    the volume pace means anything (the opening auction is most of the first minutes' volume). The full alert follows
    from 9:35 if the volume confirms. Big gaps only, 5%+ (smaller ones are noise this early), with the shapes the
    9:35 alerts judge, minus the volume: a power-day gap (10%+), a catalyst gap (from under the 50 EMA or 200 SMA to
    over both), a launch gap (through the base high, up 5%+); above the 200 SMA, and the day before at most 28% over
    it (50% for a power-day gap)."""
    R, rows, out = doc["rules"], live["rows"], []
    now = now or datetime.datetime.now(NY)
    d0 = datetime.date.fromisoformat(doc["date"])
    after_close = datetime.datetime(d0.year, d0.month, d0.day, 15, 30, tzinfo=NY).timestamp()
    for sym, w in doc.get("watch", {}).items():
        q = rows.get(sym)
        if not q or len(q) < 6 or not q[5]:
            continue                                                # not open yet (NYSE often takes a minute or more)
        price, chg, rv, op = q[0], q[1], q[4], q[5]
        prev = price / (1 + chg / 100)
        gap = (op / prev - 1) * 100
        close0, pivot, s200, s50 = w[0], w[1], w[2], w[4]
        if not s200 or price <= s200 or gap < R.get("ep_gap", 5):
            continue
        ext = (close0 / s200 - 1) * 100
        power = gap >= R.get("power_gap", 10)
        if ext > R.get("power_ext200", 50) or (ext > R["max_ext200"] and not power):
            continue
        under = [n for n, m in (("50 EMA", s50), ("200 SMA", s200)) if m and close0 < m]
        catalyst = bool(under) and bool(s50) and price > s50
        launch = price > pivot and chg >= R["min_chg"]
        if not (power or catalyst or launch):
            continue
        ern = q[6] if len(q) > 6 else None
        earn = bool(ern and after_close <= ern <= now.timestamp() + 3600)
        group, gstat = w[8], w[9]
        theme = f"{group} ({['not trending', 'turning up', 'leading'][gstat] if gstat in (0, 1, 2) else 'no group'})" if group else "no group"
        what, need = ("power-day gap", "4x+ and up 15%+") if power else ("catalyst gap", "3x+") if catalyst else ("launch gap", "3x+")
        out.append((f"{sym}:early", f"{sym} EARLY: {what} " + ("on earnings" if earn else "(news? no earnings)"),
                    f"gap {gap:+.1f}% · ${price:.2f} ({chg:+.1f}%)"
                    + (f" · was under its {' & '.join(under)}, now above the 50 EMA & 200 SMA" if under and price > s50 else "")
                    + f" · base high ${pivot:.2f} " + ("cleared" if price > pivot else "not cleared")
                    + (f" · vol {rv:.1f}x so far (rough: the opening auction)" if rv else "")
                    + f" · the full alert from 9:35 if the volume confirms ({need}) · theme {theme}", "default", w[10]))
    return out


def find(live, doc, now=None):
    """[(key, title, message, priority, tv symbol)] for everything that fires right now"""
    R, rows, out = doc["rules"], live["rows"], []
    now = now or datetime.datetime.now(NY)
    d0 = datetime.date.fromisoformat(doc["date"])                 # the last close the watch list was built from
    after_close = datetime.datetime(d0.year, d0.month, d0.day, 15, 30, tzinfo=NY).timestamp()
    for sym, w in doc.get("watch", {}).items():
        q = rows.get(sym)
        if not q or len(q) < 5 or q[4] is None:
            continue
        price, chg, rv = q[0], q[1], q[4]
        op = q[5] if len(q) > 5 else None
        prev = price / (1 + chg / 100)
        gap = (op / prev - 1) * 100 if op else None
        close0, pivot, s200 = w[0], w[1], w[2]
        group, gstat, tvs = w[8], w[9], w[10]
        mem = w[11] if len(w) > 11 else None
        s50 = w[4]                                                 # the 50 EMA
        ern = q[6] if len(q) > 6 else None
        earn = bool(ern and after_close <= ern <= now.timestamp() + 3600)  # reported after the last close (or this morning)
        if not s200 or price <= s200:
            continue
        ext = (close0 / s200 - 1) * 100
        power = rv >= R.get("power_rv", 4) and gap is not None and gap >= R.get("power_gap", 10) and chg >= R.get("power_chg", 15)
        if ext > R.get("power_ext200", 50) or (ext > R["max_ext200"] and not power):
            continue
        theme = f"{group} ({['not trending', 'turning up', 'leading'][gstat] if gstat in (0, 1, 2) else 'no group'})" if group else "no group"
        facts = f"{chg:+.1f}% · gap {gap:+.1f}% · vol {rv:.1f}x for the time of day" if gap is not None else f"{chg:+.1f}% · vol {rv:.1f}x"
        under = [n for n, m in (("50 EMA", s50), ("200 SMA", s200)) if m and close0 < m]
        over = bool(s50) and price > s50 and price > s200
        crossed = f" · was under its {' & '.join(under)}, now above the 50 EMA & 200 SMA" if under and over else ""
        # how far under its 52-week high it trades now, and the correction it is coming out of (AXGN Oct 28 2026: 14% under
        # its 52-week high at $45.48, after a 36% correction; not "36% off its high", which was yesterday's depth)
        neglect = (f" · {100 * (1 - price / w[5]):.0f}% under its 52-week high (${w[5]:.2f})" if w[5] and price < w[5] else " · at a 52-week high" if w[5] else "") \
            + (f", after a {w[7]:.0f}% correction" if w[7] and w[7] >= 15 else "")
        cat = " · EARNINGS" if earn else ""
        bo = price > pivot or bool(mem and price > mem[1])
        g = grade(max(rv, R["rv_big"]), bo, max(gap or 0, R["gap_big"]), chg, R, False) if mem else grade(rv, bo, gap, chg, R, close0 < s200)
        shape = bool(under) and over and gap is not None and gap >= R.get("ep_gap", 5)    # a catalyst gap, whatever the volume
        if shape and price > pivot and rv >= 1:
            # the 2nd trigger: sent only after a catalyst alert that hadn't cleared the base yet (see main)
            out.append((f"{sym}:basebreak", f"{sym} 2nd trigger: base high ${pivot:.2f} cleared",
                        f"${price:.2f} · {chg:+.1f}% · vol {rv:.1f}x for the time of day · grade so far {g}{cat}"
                        f" · after its catalyst gap over the 50 EMA & 200 SMA · theme {theme}", "high", tvs))
        if power:
            out.append((f"{sym}:power", f"{sym} POWER DAY" + (" on earnings" if earn else ""),
                        f"{facts} · ${price:.2f}{crossed}{neglect} · theme {theme}", "high", tvs))
            continue
        if shape and rv >= R["rv_big"]:
            out.append((f"{sym}:catalyst", f"{sym} CATALYST GAP: " + ("earnings" if earn else "news? (no earnings)")
                        + ", over its 50 EMA & 200 SMA", f"{facts} · ${price:.2f}{crossed}{neglect} · base high ${pivot:.2f} "
                        + (f"cleared (grade so far {g})" if price > pivot else "not cleared yet: 2nd alert when it is") + f" · theme {theme}", "high", tvs))
        if chg < R["min_chg"] or rv < R["min_rv"] or (gap is not None and gap <= 0):
            continue
        if g in ("A+", "A"):
            out.append((f"{sym}:launch", f"{sym} {g} launch", f"{facts}{cat} · ${price:.2f} through its base high ${pivot:.2f}"
                        + (" (delayed: faded gap " + mem[0] + ")" if mem else "") + f"{crossed} · theme {theme}", "high" if g == "A+" else "default", tvs))
    for r in doc.get("launches", []):
        q = rows.get(r["symbol"])
        if not q or len(q) < 5 or q[4] is None:
            continue
        price, chg, rv = q[0], q[1], q[4]
        op = q[5] if len(q) > 5 else None
        sym, tvs = r["symbol"], r.get("tv") or r["symbol"]
        late = bool(r.get("late"))
        ago = r.get("last_breakout_days_ago")
        # a breakout a few sessions after the last one is the same push (RPD Oct 22 / Oct 23): the same leg
        nxt = (r.get("leg") or 0) + (0 if ago is not None and ago < doc["rules"].get("leg_pause", 5) else 1)
        # the pop out of a consolidation is an entry inside the base, not a new leg (ANF Oct 5 2026)
        inside = (r.get("pattern") or "").startswith("Pop out of the consolidation")
        if inside:
            nxt = r.get("leg") or 0
        # confirmation: in the 3 sessions after a base breakout, it opens and trades above the base top on 2x+ volume
        # (RPD Oct 26 2026, after breaking its Aug high on Oct 23)
        top = r.get("last_breakout_top")
        confirm = (f"{sym}:confirm", f"{sym} breakout confirmed",
                   f"opened ${op:.2f} and trades ${price:.2f} above the base top ${top:.2f} (broken {r['last_breakout_date']})"
                   f" · {chg:+.1f}% · vol {rv:.1f}x for the time of day", "high", tvs) \
            if top and ago is not None and ago <= 2 and op and op > top and price > top and rv >= 2 else None
        # the retest of the last breakout: the zone for today was set at the last close (scanner/launch.py follow)
        z, lvb = r.get("retest_zone"), r.get("retest_level")
        if z and lvb and r.get("retest_away") and (now.hour, now.minute) >= (9, 35):
            lvw, adr = r.get("retest_level_wick") or lvb, r.get("adr_pct") or 5.0
            lv = f"${lvb:.2f}" + (f"-${lvw:.2f} (bodies-wicks)" if lvw > lvb * 1.001 else "")
            emas = [(n, e) for n, e in (("10 EMA", r.get("ema10")), ("21 EMA", r.get("ema21")), ("50 EMA", r.get("ema50")))
                    if e and lvb * (1 - adr / 100) <= e <= lvw * (1 + adr / 100)]
            conf = (" · at the " + " & ".join(f"{n} (${e:.2f} at the last close)" for n, e in emas)) if emas else ""
            tail = f" · {chg:+.1f}% · vol {rv:.1f}x · leg {r.get('leg')}" + since(r)
            if z[0] <= price <= min(z[1], r.get("retest_need_low") or z[1]):
                out.append((f"{sym}:zone", f"{sym} pulling back to its breakout level" + (" + " + " & ".join(n for n, e in emas) if emas else ""),
                            f"${price:.2f} in the retest zone ${z[0]:.2f}-${z[1]:.2f} · level {lv} (broken {r['retest_from']}){conf}"
                            f" · a heads-up: the buy is the close holding over ${lvb:.2f}" + tail, "default", tvs))
            if (now.hour, now.minute) >= (15, 45) and lvb < price <= lvb * (1 + 1.5 * adr / 100) and price > (r.get("ema21") or 0):
                # the low is checked on today's 1-minute chart before it goes out (main); an EMA counts when it trades over it
                held = [(n, e) for n, e in emas if price > e]
                conf = (" · over the " + " & ".join(f"{n} (${e:.2f} at the last close)" for n, e in held)) if held else ""
                out.append((f"{sym}:retest", f"{sym} RETEST HOLDING into the close" + (" + " + " & ".join(n for n, e in held) if held else ""),
                            f"came back to its breakout level {lv} (broken {r['retest_from']}) and trades ${price:.2f} over it{conf}"
                            f" · the buy: at the close, if it holds over ${lvb:.2f}" + tail, "high" if held else "default", tvs))
        # the push out of the 21 EMA with a gap after the retest's touch (push_level = what the open has to clear)
        pl = r.get("push_level")
        if pl and op and r.get("day_open") and op > max(r["day_open"], r["price"]) and price > pl and rv >= 1:
            gap_ = (op / (price / (1 + chg / 100)) - 1) * 100
            out.append((f"{sym}:push", f"{sym} entry: push out of the 10 / 21 EMA with a gap",
                        f"opened ${op:.2f} ({gap_:+.1f}%) over yesterday's candle, now ${price:.2f} over the trigger ${pl:.2f}"
                        f" (yesterday's candle, its 10 & 21 EMA and the breakout level, all reclaimed)"
                        f" · after the retest of its breakout level ${r.get('retest_level'):.2f} (touched {r.get('retest_tried')})"
                        f" · {chg:+.1f}% · vol {rv:.1f}x · leg {r.get('leg')}" + since(r), "high", tvs))
        bp = r.get("buy_point")
        if bp and inside and (r.get("price") or 0) < bp:
            # the pop out of a consolidation: after a tight candle, it opens above that candle's open and close and above
            # the rising 10 and 21 EMA (bp = the level the open has to clear), still holding it; no volume needed (ANF Oct 5 2026)
            if op and op > bp and price >= bp:
                gap_ = (op / (price / (1 + chg / 100)) - 1) * 100
                out.append((f"{sym}:pop", f"{sym} entry in base: the pop out of the consolidation",
                            f"opened ${op:.2f} ({gap_:+.1f}%) above yesterday's tight candle and the rising 10 & 21 EMA, now ${price:.2f}"
                            f" · {chg:+.1f}% · vol {rv:.1f}x · after its resting time (volume dried up, surfing the 10 & 21 EMA) · an entry inside"
                            f" the base (still leg {nxt}) · theme {r.get('group_now') or '-'} ({(r.get('group_status_now') or '').lower()})"
                            + since(r), "default", tvs))
            elif confirm:
                out.append(confirm)
            continue
        # from 9:45 only: until a stock's first trades show, Yahoo's day high is yesterday's (ENTG Oct 30 2026: $170.01,
        # yesterday's high, at 9:30; its real high was $159.00); and only a high at or above the open and the price
        hi = q[7] if len(q) > 7 else None
        if (now.hour, now.minute) >= (9, 45) and bp and (r.get("price") or 0) <= bp and hi and hi > bp and price <= bp \
                and hi >= price and (not op or hi >= op):
            out.append((f"{sym}:touch", f"{sym} touched its buy point, back under",
                        f"traded up to ${hi:.2f} today, over the buy point ${bp:.2f}, now ${price:.2f} ({100 * (price / bp - 1):+.1f}%)"
                        f" · not a breakout yet: that alert comes when it trades over ${bp:.2f} at a check · {chg:+.1f}% · vol {rv:.1f}x"
                        + since(r), "default", tvs))
        if not bp or (r.get("price") or 0) > bp or not price > bp:
            if confirm:
                out.append(confirm)                   # a new breakout the same day says more than the confirmation
            continue
        if True:
            g, why = grade_breakout(r)
            pat = r.get("pattern") or ""
            pat = "base" if not pat or pat.startswith("Base forming") else pat
            what = (f"base top ${bp:.2f} (set {r['buy_point_top_date']}; nothing traded above it for {int(r['base_days'])} sessions)"
                    if pat == "Base top" and r.get("buy_point_top_date") else f"buy point ${bp:.2f}")
            # the breakout that also pushed out of the 10 & 21 EMA with a gap: opened over yesterday's candle (its open and
            # close) and both EMAs, a double confluence (GMAB Oct 5 2026)
            push = bool(op and r.get("day_open") and r.get("ema10") and r.get("ema21")
                        and op > max(r["day_open"], r["price"], r["ema10"], r["ema21"]))
            why += " · also pushed out of the 10 & 21 EMA with a gap (opened over yesterday's candle)" if push else ""
            out.append((f"{sym}:breakout", f"{sym} {g} breakout: {pat}",
                        f"${price:.2f} over the {what} · {why} · {chg:+.1f}% · vol {rv:.1f}x for the time of day"
                        + (" (light)" if rv < 1 else "") + " · "
                        + f"would be leg {nxt}" + (" (late)" if nxt >= 4 else "") + f" · theme {r.get('group_now') or '-'} ({(r.get('group_status_now') or '').lower()})"
                        + since(r), "high" if g == "A" else "default", tvs))
    return out


def since(r):
    """how the stock came to be followed: its launch, or your Follow button"""
    return f" · your pick since {r['pick'][:10]}" if r.get("grade") == "You" else f" · launched {r['date']} ({r['grade']})"


def opening_range_high(sym):
    """the high of the first 5 minutes (9:30-9:35), from Yahoo's 5-minute chart (its prices are fine), or None"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym.replace('/', '-').replace('.', '-'))}?range=1d&interval=5m"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.load(r)["chart"]["result"][0]
        t0 = datetime.datetime.fromtimestamp(res["timestamp"][0], NY)
        hi = res["indicators"]["quote"][0]["high"][0]
        return round(hi, 2) if hi and (t0.hour, t0.minute) == (9, 30) else None
    except Exception:
        return None


def chart_high_today(sym):
    """today's high from 9:30 on, from Yahoo's 1-minute chart (its prices are today's, unlike the quote's day high in
    the first minutes), or None"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym.replace('/', '-').replace('.', '-'))}?range=1d&interval=1m"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.load(r)["chart"]["result"][0]
        today = datetime.datetime.now(NY).date()
        his = [h for t, h in zip(res.get("timestamp") or [], res["indicators"]["quote"][0].get("high") or [])
               if h and datetime.datetime.fromtimestamp(t, NY).date() == today and datetime.datetime.fromtimestamp(t, NY).hour * 60
               + datetime.datetime.fromtimestamp(t, NY).minute >= 570]
        return round(max(his), 4) if his else None
    except Exception:
        return None


def chart_low_today(sym):
    """today's low from 9:30 on, from Yahoo's 1-minute chart, or None"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym.replace('/', '-').replace('.', '-'))}?range=1d&interval=1m"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.load(r)["chart"]["result"][0]
        today = datetime.datetime.now(NY).date()
        los = [x for t, x in zip(res.get("timestamp") or [], res["indicators"]["quote"][0].get("low") or [])
               if x and datetime.datetime.fromtimestamp(t, NY).date() == today and datetime.datetime.fromtimestamp(t, NY).hour * 60
               + datetime.datetime.fromtimestamp(t, NY).minute >= 570]
        return round(min(los), 4) if los else None
    except Exception:
        return None


def send(topic, title, msg, prio, tvs):
    req = urllib.request.Request(f"https://ntfy.sh/{topic}", data=msg.encode(), method="POST", headers={
        "Title": title.encode("ascii", "replace").decode(), "Priority": prio, "Tags": "chart_with_upwards_trend",
        "Click": "https://www.tradingview.com/chart/?symbol=" + urllib.request.quote(tvs)})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status


def main():
    live_p, launch_p, state_p = sys.argv[1:4]
    fast = "--fast" in sys.argv                          # the 1-minute check (radar/fast.py)
    now = datetime.datetime.now(NY)
    live, doc = json.load(open(live_p)), json.load(open(launch_p))
    today = now.date().isoformat()
    try:
        state = json.load(open(state_p))
    except Exception:
        state = {}
    if state.get("date") != today:
        state = {"date": today, "sent": []}
    early = (now.hour, now.minute) < (9, 35)            # 9:31-9:34: the early heads-ups only (the 1-minute check)
    if live.get("session") != today or (now.hour, now.minute) < (9, 31) or (early and not fast):
        print("alerts: not in today's session yet")
        return
    sent = set(state["sent"])
    found = find_early(live, doc, now) if early else find(live, doc, now)
    cat_before = {k.split(":")[0] for k in sent if k.endswith(":catalyst")}
    cat_now = {a[0].split(":")[0] for a in found if a[0].endswith(":catalyst") and a[0] not in sent}
    new, quiet = [], []
    for a in found:
        key, sym = a[0], a[0].split(":")[0]
        if key in sent or (key.endswith(":launch") and sym + ":power" in sent):
            continue
        # a catalyst stock gets two triggers: the catalyst gap, then (if its base wasn't cleared yet) the base breakout;
        # its launch alert would only repeat them
        if key.endswith(":basebreak") and sym not in cat_before:
            if sym in cat_now:                      # this run's catalyst alert already says "cleared"
                quiet.append((key, None, None, None, None))
            continue
        if key.endswith(":launch") and (sym in cat_before or sym in cat_now):
            quiet.append((key, None, None, None, None))
            continue
        new.append(a)
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    if len(new) > MAX_PER_RUN:          # a flood (a market-wide gap): one summary instead of a stack of pushes
        new = new[:MAX_PER_RUN - 1] + [(f"summary:{now:%H%M}", f"{len(new) - MAX_PER_RUN + 1} more alerts",
                                        ", ".join(a[0].split(":")[0] for a in new[MAX_PER_RUN - 1:]), "default", "SPY")] \
            + [(a[0], None, None, None, None) for a in new[MAX_PER_RUN - 1:]]
    new += quiet
    for key, title, msg, prio, tvs in new:
        if title is not None and key.endswith(":retest"):
            # today's low (1-minute chart) came into the zone, after a real pullback; with the EMA, the low at it
            sym_ = key.split(":")[0]
            r_ = next((x for x in doc.get("launches", []) if x["symbol"] == sym_), {})
            lo_ = chart_low_today(sym_)
            # the pullback's new low (undercut and reclaim), or any low in the zone while it tests the level with every close
            # since the first touch over the 21 EMA (ACN Oct 7 2026)
            z_ = r_.get("retest_zone") or [0, 0]
            need_ = min(r_.get("retest_need_low") or 0, 1e9 if r_.get("retest_testing") else (r_.get("retest_low") or 1e9))
            if not (lo_ and z_[0] <= lo_ <= min(z_[1], need_)):       # in the zone, the pullback's new low (undercut and reclaim)
                print(f"{key}: today's low {lo_} not in the zone {z_} as a new pullback low (under {need_}), not sent")
                continue
            msg += f" · today's low ${lo_:.2f}"
        if title is not None and key.endswith(":touch"):
            # only when today's 1-minute chart shows the trade over the buy point (the quote's day high can be yesterday's)
            r_ = next((x for x in doc.get("launches", []) if x["symbol"] == key.split(":")[0]), {})
            ch = chart_high_today(key.split(":")[0])
            if not (ch and r_.get("buy_point") and ch > r_["buy_point"]):
                print(f"{key}: not confirmed by today's chart (high {ch}), not sent")
                continue
        if title is not None and key.endswith((":catalyst", ":basebreak", ":pop", ":push")):
            # your entry: over the first 5 minutes' high, or a retest of it
            orh, q = opening_range_high(key.split(":")[0]), live["rows"].get(key.split(":")[0])
            if orh and q:
                msg += f" · 5-min opening range high ${orh:.2f}: " + (f"{100 * (q[0] / orh - 1):.1f}% above it" if q[0] > orh else "not cleared yet")
        if title is not None:
            line = f"{now:%H:%M} {title}: {msg}"
            state.setdefault("items", []).append({"key": key, "time": f"{now:%H:%M}", "title": title, "msg": msg, "tv": tvs})
            if topic:
                try:
                    send(topic, title, msg, prio, tvs)
                except Exception as e:
                    print("alert not sent:", e, file=sys.stderr)
                    continue
            print(line)
            state.setdefault("log", []).append(line)
        state["sent"].append(key)
    state["sent"] = sorted(set(state["sent"]))
    json.dump(state, open(state_p, "w"), indent=1)
    print(f"alerts: {sum(1 for a in new if a[1])} new, {len(state['sent'])} today" + ("" if topic else " (no NTFY_TOPIC: logged, not sent)"))


if __name__ == "__main__":
    main()
