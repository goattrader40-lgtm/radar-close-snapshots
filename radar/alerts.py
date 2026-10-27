#!/usr/bin/env python3
"""Phone alerts (ntfy) from the 5-minute live prices: launches and breakouts as they happen.

  python3 radar/alerts.py <live.json> <launch.json> <alerts.json>      (NTFY_TOPIC set: sends; unset: only logs)

Alerts, each stock and kind once a day (alerts.json keeps what was sent, on the radar-data branch):
  power day   volume pace 4x+ for the time of day, a 10%+ gap, up 15%+, above the 200 SMA, at most 50% over it
  catalyst    an episodic pivot, the moment it happens: a neglected stock (closed under its 50 or 200 SMA the day
              before) gaps up 5%+ on earnings or news with volume pace 3x+ and trades above both the 50 and the
              200 SMA. No base breakout needed yet (HRI on Oct 27 2026: earnings, gapped 9.3% from under both;
              the launch alert waited for its 20-day high). Earnings = reported after the last close; without
              earnings it says to check the news
  launch      A+ or A off the watch list (setups/launch.json, from the last close), graded like the portal's
              Launching today: volume pace 3x+ and above its base high (the previous 20 days' high), with a 3%+
              gap or a 10%+ day; A+ = a 6%+ gap jumping from under the 200 SMA. Also needs: up 5%+, opened up,
              above the 200 SMA, and the day before at most 28% over it. A faded high-volume gap that held its
              base (a delayed launch) gets that day's volume and gap.
  breakout    a launch being followed clears its buy point (the nearest of: your MSF pattern's pivot, the flag
              trendline, the smaller or the larger base's top) with volume running at 1x+ normal for the time of day,
              after closing under it the day before; graded A (volume 2x+, trending theme, not a late leg), B
              (1.5x+), C (the rest)
  confirm     in the 3 sessions after a base breakout, it opens and trades above the base top on 2x+ volume
Nothing is sent before 9:35 ET (the volume pace is rough in the first minutes). ntfy is a free phone app:
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


def find(live, doc, now=None):
    """[(key, title, message, priority, tv symbol)] for everything that fires right now"""
    R, rows, out = doc["rules"], live["rows"], []
    now = now or datetime.datetime.now(NY)
    d0 = datetime.date.fromisoformat(doc["date"])                 # the last close the watch list was built from
    since = datetime.datetime(d0.year, d0.month, d0.day, 15, 30, tzinfo=NY).timestamp()
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
        s50 = (w[13] if len(w) > 13 else None) or w[4]             # the 50 SMA (lists made before Oct 27: the 50 EMA)
        ern = q[6] if len(q) > 6 else None
        earn = bool(ern and since <= ern <= now.timestamp() + 3600)  # reported after the last close (or this morning)
        if not s200 or price <= s200:
            continue
        ext = (close0 / s200 - 1) * 100
        power = rv >= R.get("power_rv", 4) and gap is not None and gap >= R.get("power_gap", 10) and chg >= R.get("power_chg", 15)
        if ext > R.get("power_ext200", 50) or (ext > R["max_ext200"] and not power):
            continue
        theme = f"{group} ({['not trending', 'turning up', 'leading'][gstat] if gstat in (0, 1, 2) else 'no group'})" if group else "no group"
        facts = f"{chg:+.1f}% · gap {gap:+.1f}% · vol {rv:.1f}x for the time of day" if gap is not None else f"{chg:+.1f}% · vol {rv:.1f}x"
        under = [n for n, m in (("50", s50), ("200", s200)) if m and close0 < m]
        over = bool(s50) and price > s50 and price > s200
        crossed = f" · was under its {' & '.join(under)} SMA, now above the 50 & 200" if under and over else ""
        neglect = f" · {w[7]:.0f}% off its high of {w[6]} sessions ago" if w[7] and w[6] is not None and w[7] >= 15 else ""
        cat = " · EARNINGS" if earn else ""
        if power:
            out.append((f"{sym}:power", f"{sym} POWER DAY" + (" on earnings" if earn else ""),
                        f"{facts} · ${price:.2f}{crossed}{neglect} · theme {theme}", "high", tvs))
            continue
        bo = price > pivot or bool(mem and price > mem[1])
        g = grade(max(rv, R["rv_big"]), bo, max(gap or 0, R["gap_big"]), chg, R, False) if mem else grade(rv, bo, gap, chg, R, close0 < s200)
        if under and over and gap is not None and gap >= R.get("ep_gap", 5) and rv >= R["rv_big"]:
            out.append((f"{sym}:catalyst", f"{sym} CATALYST GAP: " + ("earnings" if earn else "news? (no earnings)")
                        + ", over its 50 & 200 SMA", f"{facts} · ${price:.2f}{crossed}{neglect} · base high ${pivot:.2f} "
                        + (f"cleared (grade so far {g})" if price > pivot else "next") + f" · theme {theme}", "high", tvs))
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
        trending = r.get("group_status_now") in ("Leading", "Turning up")
        late = bool(r.get("late"))
        ago = r.get("last_breakout_days_ago")
        # a breakout a few sessions after the last one is the same push (RPD Oct 22 / Oct 23): the same leg
        nxt = (r.get("leg") or 0) + (0 if ago is not None and ago < doc["rules"].get("leg_pause", 5) else 1)
        # confirmation: in the 3 sessions after a base breakout, it opens and trades above the base top on 2x+ volume
        # (RPD Oct 26 2026, after breaking its Aug high on Oct 23)
        top = r.get("last_breakout_top")
        confirm = (f"{sym}:confirm", f"{sym} breakout confirmed",
                   f"opened ${op:.2f} and trades ${price:.2f} above the base top ${top:.2f} (broken {r['last_breakout_date']})"
                   f" · {chg:+.1f}% · vol {rv:.1f}x for the time of day", "high", tvs) \
            if top and ago is not None and ago <= 2 and op and op > top and price > top and rv >= 2 else None
        bp = r.get("buy_point")
        if not bp or (r.get("price") or 0) > bp or not (price > bp and rv >= 1):
            if confirm:
                out.append(confirm)                   # a new breakout the same day says more than the confirmation
            continue
        if True:
            # graded to help decide: A = volume pace 2x+ in a trending theme, not a late leg; B = 1.5x+; C = the rest
            g = "A" if rv >= 2 and trending and nxt < 4 else "B" if rv >= 1.5 and nxt < 4 else "C"
            pat = r.get("pattern") or ""
            pat = "base" if not pat or pat.startswith("Base forming") else pat
            what = (f"base top ${bp:.2f} (set {r['buy_point_top_date']}; nothing traded above it for {int(r['base_days'])} sessions)"
                    if pat == "Base top" and r.get("buy_point_top_date") else f"buy point ${bp:.2f}")
            out.append((f"{sym}:breakout", f"{sym} {g} breakout: {pat}",
                        f"${price:.2f} over the {what} · {chg:+.1f}% · vol {rv:.1f}x · would be leg {nxt}"
                        + (" (late)" if nxt >= 4 else "") + f" · theme {r.get('group_now') or '-'} ({(r.get('group_status_now') or '').lower()})"
                        + f" · launched {r['date']} ({r['grade']})", "high" if g == "A" else "default", tvs))
    return out


def send(topic, title, msg, prio, tvs):
    req = urllib.request.Request(f"https://ntfy.sh/{topic}", data=msg.encode(), method="POST", headers={
        "Title": title.encode("ascii", "replace").decode(), "Priority": prio, "Tags": "chart_with_upwards_trend",
        "Click": "https://www.tradingview.com/chart/?symbol=" + urllib.request.quote(tvs)})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status


def main():
    live_p, launch_p, state_p = sys.argv[1:4]
    now = datetime.datetime.now(NY)
    live, doc = json.load(open(live_p)), json.load(open(launch_p))
    today = now.date().isoformat()
    try:
        state = json.load(open(state_p))
    except Exception:
        state = {}
    if state.get("date") != today:
        state = {"date": today, "sent": []}
    if live.get("session") != today or (now.hour, now.minute) < (9, 35):
        print("alerts: not in today's session yet")
        return
    sent = set(state["sent"])
    new = [a for a in find(live, doc, now) if a[0] not in sent and not (a[0].endswith(":launch") and a[0].split(":")[0] + ":power" in sent)]
    cat_now = {a[0].split(":")[0] for a in new if a[0].endswith(":catalyst")}
    # a catalyst gap already through its base high says it all: no second push for the launch in the same run
    quiet = [(a[0], None, None, None, None) for a in new if a[0].endswith(":launch") and a[0].split(":")[0] in cat_now]
    new = [a for a in new if not (a[0].endswith(":launch") and a[0].split(":")[0] in cat_now)]
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    if len(new) > MAX_PER_RUN:          # a flood (a market-wide gap): one summary instead of a stack of pushes
        new = new[:MAX_PER_RUN - 1] + [(f"summary:{now:%H%M}", f"{len(new) - MAX_PER_RUN + 1} more alerts",
                                        ", ".join(a[0].split(":")[0] for a in new[MAX_PER_RUN - 1:]), "default", "SPY")] \
            + [(a[0], None, None, None, None) for a in new[MAX_PER_RUN - 1:]]
    new += quiet
    for key, title, msg, prio, tvs in new:
        if title is not None:
            line = f"{now:%H:%M} {title}: {msg}"
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
