#!/usr/bin/env python3
"""Phone alerts (ntfy) from the 5-minute live prices: launches and breakouts as they happen.

  python3 radar/alerts.py <live.json> <launch.json> <alerts.json> [--fast]   (NTFY_TOPIC set: sends; unset: only logs)

Every 5 minutes with the live prices; every minute in between (--fast, radar/fast.py: 9:31-12:00 and 3:00-4:00) for
the big gap-ups on volume (catalyst gaps and their 2nd trigger, power days, A+/A launches) and the followed launches'
breakouts. 9:31-9:34 (the 1-minute check only): the early heads-up (find_early), the shape of such a gap before its
volume can be read.

Alerts, each stock and kind once a day (alerts.json keeps what was sent, on the radar-data branch):
  power day   volume pace 4x+ for the time of day, an 8%+ gap, up 10%+, above the 200 SMA, at most 50% over it
  catalyst    an episodic pivot, the moment it happens: a neglected stock (closed under its 50 EMA or 200 SMA the
              day before) gaps up 5%+ on earnings or news with volume pace 3x+ and trades above both the 50 EMA and
              the 200 SMA. No base breakout needed, and no clean base either (HRI on Oct 27 2026: earnings, gapped 9.3%
              from under both out of a choppy chart; the launch alert waited for its 20-day high). It says whether
              the base high is cleared yet; if not, a 2nd trigger follows when it is (volume 1x+). Such a stock
              gets these two instead of a launch alert. Earnings = reported after the last close; without
              earnings it says to check the news
  reversal    a reversal launch as it happens: opened under yesterday's close, now up 8%+ on a volume pace of 2x+, over
              its 1-month high (the previous 20 sessions' highest high), in the top half of today's range (1-minute chart),
              above the 200 SMA (at most 28% over it the day before) and 30%+ over its 52-week low (GDDY Oct 30 2026)
  3-SETUPS    no phone alert during the day: the Ready list comes once after the close as a text file
              (radar/eod_alerts.py); its triggers during the day are desktop notifications on the portal
  launch      A+ or A off the watch list (setups/launch.json, from the last close), graded like the portal's
              Launching today: volume pace 3x+ and above its base high (the previous 20 days' high), with a 3%+
              gap or a 10%+ day; A+ = a 6%+ gap jumping from under the 200 SMA. Also needs: up 5%+, opened up,
              above the 200 SMA, and the day before at most 28% over it. A faded high-volume gap that held its
              base (a delayed launch) gets that day's volume and gap.
  breakout    a launch being followed clears its buy point (the nearest of: your MSF pattern's pivot, the flag
              trendline, the smaller or the larger base's top), whatever the volume (a base top: the close has to hold
              more than 0.5% over it to be decisive, within 0.5% is a breakout with caution): the alert shows the volume pace
              for the time of day and says when it is light (ATRC Aug 7 2026 over 41.29 on 0.6x, Oct 29 over 61.70),
              after closing under it the day before; graded from the data (grade_breakout): A = an early
              breakout (1st / 2nd, within 50 sessions of the launch) in a Top or Strong group (the group rank, top 10%)
              with volume building before, B = early plus one of those, C = the rest
  gap out of base  a launch being followed closed at or under its base high (the base top or your MSF pattern's pivot;
              not a flag line, not a pop) and opens above it today (your rule, Nov 1 2026; Zanger / Qullamaggie). Only
              stocks with an ADR of 4%+, 600K+ shares and $30M+ a day (20-day averages) and a $700M+ market cap. Four
              alerts: the gap (volume pace 1x+), the 1-minute opening range high broken and the 5-minute one (each with
              its stop, the range's low, and the risk in ADRs), and at 9:50 the volume check: under 2x = out, whatever
              the trade. A trigger after 9:50 needs 2x+. The stock's other alerts (breakout, touch) stay quiet that day
  reclaimbo   the breakout undercut & reclaim: a launch that closed under its breakout level 2+ days (holding over the 50
              EMA) trades back over it (heads-up), from 3:45 PM holding into the close (CAI Oct 9 2026)
  ema50back   the 50 EMA undercut tab (your rule, Nov 1 2026): a launch that closed under its 50 EMA 2 days in a row has to
              close back over it today (a 3rd close under takes it off the list): the heads-up when it trades back over it
  ema50       from 3:45 PM: today's low went under the 50 EMA and under the open, and it trades back over it in the upper
              half of the day: the 50 EMA undercut & reclaim holding into the close (AEHR Mar 31 2026). The buy is the close
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
              day's candle and trades over its 10 & 21 EMA and the breakout level, pushing out of the 21 EMA with a gap,
              whatever the volume (shown) (ANF Aug 21 2026; CAI Oct 9 on 0.98x). None while still under a flag's
              falling line (ARM Apr 8 2026)
  ema21zone   a heads-up: a stock set up for a 21 EMA entry in its base (scanner/launch.py ema21_watch) trades down to its
              21 EMA (a quarter ADR over it or under it)
  ema21       from 3:45 PM: today's low went under the 21 EMA and under the open, and it trades back over it in the upper
              half of the day: the 21 EMA retest holding into the close (after a controlled pullback, the closes held
              over it: TTAN Oct 29 2026, ARM May 18) or the undercut & reclaim (after 2 closes under it, strong: SMCI Jun
              27 2023). The buy is the close; the scan after the close confirms it
              The retest alone is a heads-up; holding over the breakout level too (today's low within 1 ADR over
              it) it is a trigger, "RETEST + BREAKOUT LEVEL" (the user's RPD Nov 3 2026: 2 confluences)
  theme up    THEME MOVING UP / GROUP MOVING UP (the user, Nov 18 2026: Cybersecurity, PANW 9:53, CRWD 10:07, S 10:10, with
              no alert of its own): 3+ tight members (fit 0.7+) of a theme, or of a tight industry group, with a morning
              breakout today, from either morning box (theme_breakouts). Once a day per theme; on the phone too
  EP pullback the first touch of the rising 10 / 21 EMA after an EP day (setups/ep_pullback.json, the evening scan; the
              rule in radar/epp.py, the user's Nov 23 2026: "it has to say in alert message ep pullback buy 10 ema"):
              READY (heads-up) when it touched the EMA (the 10 EMA: and traded under the EP day's close; the 21 EMA:
              still over the EP day's low), BUY (trigger) when a 15-minute candle closes back over the EMA and VWAP
              (the 10 EMA: not more than 5% under the EP close), with its stop (today's low) and first sale (+10%).
              Read from today's 1-minute chart for the names within 5% of their level; a BUY holds in its box while
              the price stays over its stop. In the portal's ⚡ Episodic pivots box (the user: "same box")
  ebd         EARNINGS BREAKDOWN, the short side (the user, Nov 28 2026; the gap-down study, tools/gapdown): a stock that
              reported since the last close and gaps down 8%+ trades under the low of its first 3-minute candle; stop =
              that candle's high, out at the close; the alert says the Earnings tab's grade, the candle's size in ADRs
              (TIGHT STOP under 0.8 ADR) and whether the stock was strong yesterday. Any liquid stock, from 9:33, each
              once a day, on the phone too; in the portal's 🔻 box while under that low (the EBD_ section below).
              Before it, at 9:33, a READY heads-up with the two prices (ebdr), in 👀 until the alert fires
  parabolic   PARABOLIC SHORTS (the user, Nov 28 2026: CAR Apr 22 2026, BYND Oct 22 2025; the rule and its study in
              radar/para.py): the stocks of last night's setups/parabolic.json (3+ up closes adding 50%+; every US stock,
              scanner/parabolic.py), read on today's 1-minute chart, not on the live quotes (most are not in the radar's
              stocks). GAP UP (heads-up, from 9:31) when it opens 3%+ up, 130%+ over its 20-session low close, at $5+;
              SHORT (trigger) at the first trade under the opening 5-minute candle's low, with its stop (the day's high);
              STOPPED (heads-up); one RE-ENTRY (trigger) on the next 5-minute close under VWAP after one over it; the next
              session COVER at the close (trigger, from 3:45 PM) or STOPPED when its high reaches the stop. A SHORT holds
              in its box while its stop is not traded. In the portal's own box, 📉 Parabolic shorts
Triggers (the buys, TRIGGERS) always get their own push, up to MAX_TRIGGERS a run, after today's 1-minute chart checks;
heads-ups fill the rest of MAX_PER_RUN and the others are grouped into one push naming each. Every alert's full text
is saved in alerts.json items (kind trigger / heads-up / summary, grouped) for the portal's log.
Nothing but the early heads-ups, the two morning breakout boxes (from their own From time, 9:31 at the earliest) and the
earnings breakdowns (from 9:33, the price under a candle's low: no volume pace in it) is sent
before 9:35 ET (the volume pace is rough in the first minutes). ntfy is a free phone app:
subscribe to the topic in the NTFY_TOPIC secret.
"""
import datetime, json, os, re, sys, urllib.request, zoneinfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epp  # noqa: E402  (the EP pullback rule, shared with the tests)
import para  # noqa: E402  (the parabolic short rule, shared with the evening list and the tests)

NY = zoneinfo.ZoneInfo("America/New_York")
MAX_PER_RUN = 8               # pushes a run: the triggers first, then heads-ups; the rest grouped into one
MAX_TRIGGERS = 15             # triggers a run that always get their own push (a market-wide gap day: the rest grouped)
# the buys (the user, Nov 3 2026: "so it gets my attention"); everything else is a heads-up. The 21 EMA retest alone is a
# heads-up (the user: "21 ema retest is not a strong sign by itself"); with the breakout level under it (ema21bl) a trigger
TRIGGERS = {"power", "catalyst", "basebreak", "launch", "reversal", "laggard", "breakout", "retest", "reclaimbo2",
            "ema50", "push", "pop", "gapbase", "gob1", "gob5", "confirm", "s3", "ema21bl", "ep", "mbo", "mbo2", "epb10", "epb21",
            "ebd",                # ebd: the earnings breakdown, the short side (the user, Nov 28 2026)
            "paras", "parar", "parac"}      # parabolic shorts: the short, its re-entry, the cover at the next close


# a trigger back in its box after it stopped holding (the user, Nov 18 2026: "i need sounds for episodic pivots as well for
# back on.... and pattern breakouts with 1.5 volume"): one BACK ON alert, on the portal only, at most one every 15 minutes
# a stock; ⚡ power days and EPs always, 🎯 pattern breakouts only with a volume pace of 1.5x+ for the time of day (under
# it they come back silently, as before). 🚀 launches and ↩️ pullback entries still come back silently
BACK_EP = ("power", "ep")
BACK_PATTERN = ("breakout", "confirm", "gapbase", "gob1", "gob5", "basebreak", "pop", "s3")
BACK_PATTERN_RV = 1.5
BACK_EVERY = 15
BACK_RE = re.compile(r"^(" + "|".join(BACK_EP + BACK_PATTERN) + r")back\d{4}$")


def is_trigger(key, title=""):
    if BACK_RE.match(key.split(":", 1)[1] if ":" in key else "") or re.match(r"^ebdback\d{4}$", key.split(":", 1)[1] if ":" in key else ""):
        return True
    if key.startswith(("grp:", "thm:")):                # a group move (2+ stocks of a theme / group alerting today); a theme moving up
        return True
    kind = key.split(":", 1)[1] if ":" in key else ""
    if kind == "ema21":                                  # the 21 EMA undercut & reclaim (2 closes under: strong) is one
        return "UNDERCUT" in (title or "")
    return kind in TRIGGERS


def short(a):
    """a grouped alert in a few words: the ticker, its kind and the price (RPD at its 21 EMA $14.60)"""
    key, title, msg = a[0], a[1] or "", a[2] or ""
    sym = key.split(":")[0]
    import re
    m = re.search(r"\$(\d[\d,]*\.\d+)", msg)
    what = title[len(sym):].strip() if title.startswith(sym) else title
    what = re.split(r" \+ | \(|: ", what)[0]
    return f"{sym} {what}" + (f" ${m.group(1)}" if m else "")


# a few words for each kind, for the group-move lines (RPD 21 EMA + breakout level 3:46)
KIND_WORDS = {"ebd": "earnings breakdown (short)", "ebdr": "earnings breakdown ready (short)", "ebdr2": "earnings breakdown ready (short)", "epr10": "EP pullback ready (10 EMA)", "epb10": "EP pullback buy (10 EMA)", "epr21": "EP pullback ready (21 EMA)",
              "epb21": "EP pullback buy (21 EMA)", "retest": "retest holding", "zone": "in the retest zone", "ema21": "21 EMA retest", "ema21bl": "21 EMA + breakout level",
              "ema21zone": "at the 21 EMA", "breakout": "breakout", "touch": "touched the buy point", "confirm": "breakout confirmed",
              "power": "power day", "catalyst": "catalyst gap", "basebreak": "base high cleared", "launch": "launch",
              "reversal": "reversal launch", "laggard": "laggard launch", "reclaimbo": "back over its breakout level",
              "reclaimbo2": "breakout undercut & reclaim", "ema50back": "back over the 50 EMA", "ema50": "50 EMA undercut & reclaim",
              "push": "push", "pop": "pop", "gapbase": "gap out of base", "gob1": "gap out of base", "gob5": "gap out of base",
              "s3": "3-SETUPS trigger", "early": "early gap", "near": "gapping to the buy point", "ep": "episodic pivot",
              "mbo": "morning breakout", "mbo2": "breakout, not in trend",
              "parag": "parabolic gap up (short watch)", "paras": "parabolic short", "parax": "parabolic short stopped",
              "parar": "parabolic short re-entry", "parax2": "parabolic re-entry stopped", "parac": "parabolic short: cover",
              "parax1": "parabolic short stopped (day 2)"}


def kind_words(key, title=""):
    kind = key.split(":", 1)[1] if ":" in key else ""
    if kind == "ema21" and "UNDERCUT" in (title or ""):
        return "21 EMA undercut & reclaim"
    return KIND_WORDS.get(kind, kind)


GROUP_MIN_ADR = 4.0           # a stock counts for a group move with an ADR of 4%+ (the user, Nov 18 2026: "lets do b with 4 adr")
GROUP_FROM = "09:40"          # the GROUP MOVE alert is sent from this time (the user, Nov 18 2026: "we are only changing alert time")


def group_moves(doc, state, alerts_now, now):
    """the user (Nov 3 2026, RPD and QLYS both in Cybersecurity at 3:46 PM): 2+ stocks of the same theme or tight
    industry group alerting the same day is a group move. Returns {group: [(sym, words, time), ...]} for the groups with
    2+ stocks, from today's alerts so far plus this run's; the loose "· other" industries don't count. Every alert of the
    day counts, the 9:35 ones too; only the GROUP MOVE alert itself waits until 9:40 (GROUP_FROM, in main; the user, Nov 18
    2026: "if something happened between 930-940 it has to show"). Only stocks with an ADR of 4%+ count (GROUP_MIN_ADR)"""
    loose = {r["group"] for r in (doc.get("group_rank") or {}).get("rows", []) if r.get("loose")}
    seen = {}
    past = [(it["key"], it.get("title"), it.get("time")) for it in state.get("items", [])
            if ":" in it.get("key", "") and not it["key"].startswith(("summary:", "grp:", "thm:")) and not it["key"].endswith((":mbo", ":mbo2", ":ebd", ":ebdr", ":ebdr2")) and ":mbo2back" not in it["key"] and ":ebdback" not in it["key"]]       # (a short is no group move)
    for key, title, t in past + [(a[0], a[1], f"{now:%H:%M}") for a in alerts_now]:
        sym = key.split(":")[0]
        if key.split(":", 1)[-1].startswith("para"):      # a parabolic short is no stock moving up with its group
            continue
        if (_ADR.get(sym) or 0) < GROUP_MIN_ADR:          # MD 3.73%, WAT 3.42%, BSY 3.20% on Nov 18 2026: not counted
            continue
        for g in _GROUPS.get(sym, []):
            if g in loose or "· other" in g:
                continue
            lst = seen.setdefault(g, [])
            if not any(x[0] == sym for x in lst):
                lst.append((sym, kind_words(key, title), t))
    pct = {r["group"]: r.get("pct") or 0 for r in (doc.get("group_rank") or {}).get("rows", [])}
    best = {}
    # a theme and an industry group with the same stocks alerting (Cybersecurity / Software: Cybersecurity) are one
    # move: the better-ranked one names it
    for g, v in seen.items():
        if len(v) < 2:
            continue
        ss = frozenset(x[0] for x in v)
        if ss not in best or pct.get(g, 0) > pct.get(best[ss], 0):
            best[ss] = g
    return {g: seen[g] for g in best.values()}


def group_label(doc, g):
    r = next((x for x in (doc.get("group_rank") or {}).get("rows", []) if x["group"] == g), None)
    if not r:
        return g
    tier = ("★ Top " if r.get("tier") == "Top" else "Strong " if r.get("tier") == "Strong" else "")
    return f"{g} ({tier}#{r['rank']}/{r['of']}, {r.get('members')} stocks)"


# a theme moving up (the user, Nov 18 2026): 3+ stocks of one theme with a morning breakout today (over yesterday's high and
# the opening range high, on volume: either morning box). The GROUP MOVE alert above counts stocks that alerted on the
# followed lists: Cybersecurity's was spent at 9:35 on three pullback heads-ups, and PANW, CRWD, S, TENB, under their 50
# EMA and on no list, could not alert at all. A first version counted the members up 3%+: about 30 alerts a day on the
# last 22 sessions (the user: "i m looking for real alerts")
THEME_MIN = 3                 # morning breakouts of one theme that make the alert
THEME_FIT = 0.7               # a tight member


def theme_members(themes, stocks, fit=0.7):
    """{("theme" | "group", name): [tight members]}: a theme's members with a fit of 0.7+ (themes.json scores), a tight
    industry group's with a group score of 0.7+ (stocks.json group / group_score; the loose "· other" ones have no group)"""
    out = {}
    for t in themes or []:
        syms = []
        for x in str(t.get("scores") or "").split():
            sym, _, sc = x.partition(":")
            try:
                if float(sc) >= fit:
                    syms.append(sym)
            except ValueError:
                pass
        if t.get("theme") and syms:
            out[("theme", t["theme"])] = syms
    for s in stocks or []:
        if s.get("group") and "· other" not in s["group"] and (s.get("group_score") or 0) >= fit:
            out.setdefault(("group", s["group"]), []).append(s["symbol"])
    return out


def theme_breakouts(state, new, members, live, now, doc=None):
    """the THEME MOVING UP alerts of this check: [(key, title, msg, prio, tvs)]. `new` = this check's morning breakouts
    [(key, title, msg, ...)] of both boxes; the earlier ones are in state items. A theme and an industry group with the
    same stocks are one alert (the theme names it); a name whose stocks all are in an alert already sent counts as sent"""
    rows, sent, t = live.get("rows") or {}, set(state.get("sent") or []), f"{now:%H:%M}"
    when = {}
    for key, tm in [(it.get("key", ""), it.get("time", "")) for it in state.get("items", [])] + [(a[0], t) for a in new]:
        if key.endswith((":mbo", ":mbo2")) and not key.startswith("mbatch"):
            when.setdefault(key.split(":")[0], tm)
    if len(when) < THEME_MIN:
        return []
    hit = {k: sorted((s for s in syms if s in when), key=lambda s: when[s]) for k, syms in members.items()}
    hit = {k: v for k, v in hit.items() if len(v) >= THEME_MIN}
    seen = [frozenset(v) for (_, name), v in hit.items() if f"thm:{name}" in sent]
    rank = {r.get("group"): r for r in ((doc or {}).get("group_rank") or {}).get("rows", [])}
    out = []
    for (kind, name), v in sorted(hit.items(), key=lambda x: (x[0][0] != "theme", -len(x[1]) / len(members[x[0]]), x[0][1])):
        key = f"thm:{name}"
        if key in sent:
            continue
        if any(frozenset(v) <= x for x in seen):
            state.setdefault("sent", []).append(key)        # the same move under its other name
            continue
        seen.append(frozenset(v))
        r = rank.get(name)
        tier = "" if not r else (" (" + ("★ Top " if r.get("tier") == "Top" else "Strong " if r.get("tier") == "Strong" else "") + f"#{r['rank']}/{r['of']})")
        title = f"{'THEME' if kind == 'theme' else 'GROUP'} MOVING UP: {name}{tier}: {len(v)} morning breakouts: " + ", ".join(v)
        msg = " · ".join(f"{s} {when[s]}" + (f" {rows[s][1]:+.1f}%" if rows.get(s) and rows[s][1] is not None else "")
                         + (f" vol {rows[s][4]:.1f}x" if rows.get(s) and len(rows[s]) > 4 and rows[s][4] else "") for s in v)
        msg += f" · {len(v)} of the {len(members[(kind, name)])} stocks of {name} broke out this morning (over yesterday's high and the opening range high)"
        out.append((key, title, msg, "high", ""))
    return out


# the context of a group / theme move (the user, Nov 20 2026: IT services up 2-5% together the morning after Globant's
# report, the AI chip themes down 2-5%; "we were supposed to have reason for that today we didnt get it"). Two facts the
# job can state by code, worded as context, never as the cause: a stock of that group that reported with today as its
# reaction session and gapped MOVE_GAP%+ ("also reported"), and the themes whose tight members move OTHER_WAY%+ the other
# way on average right now (a rotation). The bellwether "why" (radar/event.py) is separate and has its own switch
MOVE_GAP = 5.0                # a reporter's gap at the open, either way, that is named
OTHER_WAY = 2.0               # a theme's average move the other way that is named
OTHER_OWN = 1.0               # the moving group's own average move before the other side is looked at
OTHER_MAX = 3


def gap_of(q):
    """the gap at the open % from a live row [price, chg, volume, time, rel vol, open, ...], or None"""
    try:
        prev = q[0] / (1 + q[1] / 100)
        return 100 * (q[5] / prev - 1) if q[5] and prev else None
    except Exception:
        return None


def move_context(name, syms, live, E, tmem, today, up_only=False):
    """the words added to a GROUP MOVE / THEME MOVING UP alert of `name` (its alerting stocks `syms`), or ''; up_only (a
    THEME MOVING UP alert): the other side only when the theme itself is up on average"""
    rows = (live or {}).get("rows") or {}
    out = []
    rep = []
    for sym, r in sorted((E or {}).items()):
        if r.get("react_day") != today or name not in _GROUPS.get(sym, []):
            continue
        q = rows.get(sym)
        g = gap_of(q) if q else None
        if g is None or abs(g) < MOVE_GAP:
            continue
        why = ", ".join(x for x in str(r.get("why") or "").split(", ") if "after hours" not in x and "pre-market" not in x)
        rep.append(f"{sym} ({r.get('read') or 'no reading'}" + (f": {why}" if why else "") + f"; gap {g:+.1f}%, now {q[1]:+.1f}%)")
    if rep:
        out.append("also reported: " + "; ".join(rep[:3]) + " (context, not by itself the cause)")
    avg = {}
    for (kind, nm), mem in (tmem or {}).items():
        v = [rows[x][1] for x in mem if rows.get(x) and rows[x][1] is not None]
        if len(v) >= 3:
            avg[(kind, nm)] = sum(v) / len(v)
    own = avg.get(("theme", name), avg.get(("group", name)))
    if own is None:
        v = [rows[x][1] for x in syms if rows.get(x) and rows[x][1] is not None]
        own = sum(v) / len(v) if v else None
    if own is not None and abs(own) >= OTHER_OWN and (own > 0 or not up_only):
        opp = sorted(((a, nm) for (kind, nm), a in avg.items() if kind == "theme" and nm != name and a * own < 0 and abs(a) >= OTHER_WAY),
                     key=lambda x: -abs(x[0]))[:OTHER_MAX]
        if opp:
            out.append(f"{name} {own:+.1f}% on average; moving the other way: " + ", ".join(f"{nm} {a:+.1f}%" for a, nm in opp))
    return "".join(" · " + x for x in out)


def move_context_data(launch_p, S_all, E_all):
    """(earnings rows by stock, {(kind, name): tight members}) for move_context, read here when the morning boxes did not"""
    d_ = os.path.dirname(os.path.abspath(launch_p))
    if not S_all:
        for n in ("base_stocks.json", "stocks.json"):
            if os.path.exists(os.path.join(d_, n)):
                S_all = {x["symbol"]: x for x in json.load(open(os.path.join(d_, n)))}
                break
    if not E_all and "--earnings" in sys.argv:
        E_all = {r["sym"]: r for r in json.load(open(sys.argv[sys.argv.index("--earnings") + 1])).get("rows", []) if r.get("reported")}
    tp_ = next((os.path.join(d_, n) for n in ("base_themes.json", "themes.json") if os.path.exists(os.path.join(d_, n))), None)
    th_ = json.load(open(tp_)) if tp_ else []
    return E_all, theme_members(th_.get("themes", []) if isinstance(th_, dict) else th_, list(S_all.values()), THEME_FIT)


def confluence_level(r, price, low):
    """the breakout level under a 21 EMA retest: the price over it and today's low within 1 ADR over it (or under it)"""
    lv = r.get("retest_level") or r.get("last_breakout_top")
    adr = (r.get("adr_pct") or 5.0) / 100
    if not (lv and price and low and price > lv and low <= lv * (1 + adr)):
        return None
    return lv


def grade(rv, bo, gap, chg, R, under):
    vol3, gap3, big = rv >= R["rv_big"], gap is not None and gap >= R["gap_big"], chg >= R["chg_big"]
    if vol3 and bo and under and gap is not None and gap >= R["aplus_gap"]:
        return "A+"
    if vol3 and bo and (gap3 or big):
        return "A"
    return "B" if int(vol3) + int(bo) + int(gap3) + int(big) >= 2 else "C"


def grade_breakout(r):
    """the breakout grade, from what separated the ones that worked: early = the 1st or 2nd breakout since the launch,
    within 50 sessions of it; its group Top or Strong in the group rank (top 10% of themes or industries after the last
    close; the user, Nov 3 2026: it replaces the old "theme Leading"); the volume building the 5 days before (1.1x+ the
    50 before). Base breakouts after launches, Aug 2025 - Nov 2026 (2,743 crosses of the top), ran 10% / 20%+ within
    20 sessions: A = all three 63% / 37% (379; the old Leading theme: 59% / 31%), B = early plus one of the others
    52% / 22%, C = the rest 45% / 17%; the ones that closed as a breakout: A 73% / 43% (157). The day's volume didn't help.
    A launch.json without the rank (group_tier_now missing) falls back to the old Leading theme."""
    early = (r.get("breakouts") or 0) < 2 and (r.get("sessions") or 0) + 1 < 50
    if "group_tier_now" in r:
        tier = r.get("group_tier_now") or ""
        lead = tier in ("Top", "Strong")
        gtxt = ("group " + ("★ Top " if tier == "Top" else "Strong " if tier == "Strong" else "not top 10% ")
                + (r.get("group_rank_now") or "unranked")).strip()
    else:
        lead = r.get("group_status_now") == "Leading"
        gtxt = "theme leading" if lead else f"theme {(r.get('group_status_now') or 'none').lower()}"
    build = (r.get("vol_build") or 0) >= 1.1
    g = "A" if early and lead and build else "B" if early and (lead or build) else "C"
    why = [("1st" if not r.get("breakouts") else "2nd") + " breakout since the launch" if early else "late (3rd+ breakout or 50+ sessions on)",
           gtxt] + (["volume building"] if build else [])
    return g, ", ".join(why)


# ───────── the episodic pivot / power day alert (the user, Nov 21 2026) ─────────
# "fix to ep alert so we dont miss it": of the 40 names on 1-EP/GAP on Nov 20 2026 only 28 met the alert's rules at the
# close of their gap day (APP, WING, TMDX under the 200 SMA; HAWK, LFTO without one; KD opened 14.91 under its 21-day
# closing high 15.20; AZTA, UPBD, PCOR, KVYO, CHYM under 3x; CGON already on Launches). Now, on the live price:
#   a 5%+ gap (was 6%), a volume pace of 2.2x+ (was 3x), over the 50 EMA (new), $10+ now (was last night's close),
#   30%+ over the 52-week low (main() checks it for every alert), NO 200 SMA rule, NO 1-month-high rule ("its same thing"
#   as the 21-day level), and over the highest close of the last 21 sessions:
#     - it opened over that level: it rings as before (and holds while the price is over the level);
#     - it opened under it ("its for laggards starts"): it rings when the price is over the 3-minute opening range high
#       AND over that level ("alert would just ring and sound when it passes 2 true states: above orh, plus above the
#       level"); KD Nov 4 2026.
# A power day keeps its own bar (gap 8%+, up 10%+, a volume pace of 3x+) on the same rules. Read for the watch list AND
# launch.json ep_watch (a stock launched in the last 20 sessions, a liquid stock closing $7-10). A stock under its 200 SMA
# rings as an EP when it meets them; the laggard-launch alert stays for the ones that don't.
EP_GAP, EP_RV, EP_MIN_PRICE, EP_ORH_MIN = 5.0, 2.2, 10.0, 3
_EP_NEED_ORH = {}        # symbol -> its 21-day closing high, for an EP / power day found this run that opened under it
_EP_ORH = {}             # symbol -> today's 3-minute opening range high (kept in the state file: read once a stock a day)


def ep_orh(sym):
    """today's 3-minute opening range high (9:30-9:33) of a stock that opened under its 21-day closing high, or None"""
    if not _EP_ORH.get(sym):
        lv = morning_levels(sym, n=EP_ORH_MIN)
        if lv and lv.get("orh"):
            _EP_ORH[sym] = lv["orh"]
    return _EP_ORH.get(sym)


def ep_orh_ok(sym, price):
    """(True / False, the 3-minute high): an EP / power day that opened under its 21-day closing high also needs the price
    over its 3-minute opening range high; one that opened over the level needs nothing more (True, None)"""
    if sym not in _EP_NEED_ORH:
        return True, None
    orh = ep_orh(sym)
    return bool(orh and price and price > orh), orh


def ep_names(doc):
    """[(symbol, watch row, only_ep)]: the watch list, then the names only the EP / power day alert reads (ep_watch)"""
    w = doc.get("watch", {})
    return [(s_, r_, False) for s_, r_ in w.items()] + [(s_, r_, True) for s_, r_ in (doc.get("ep_watch") or {}).items() if s_ not in w]


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
    hc = doc.get("watch_close_high_21d") or {}
    for sym, w, only_ep in ep_names(doc):
        q = rows.get(sym)
        if not q or len(q) < 6 or not q[5]:
            continue                                                # not open yet (NYSE often takes a minute or more)
        price, chg, rv, op = q[0], q[1], q[4], q[5]
        prev = price / (1 + chg / 100)
        gap = (op / prev - 1) * 100
        close0, pivot, s200, s50 = w[0], w[1], w[2], w[4]
        if gap < R.get("ep_gap", 5):
            continue
        # the EP / power-day gap follows the EP alert's rules (the user, Nov 21 2026): over the 50 EMA, $10+ now, no 200 SMA rule
        hc21 = hc.get(sym)
        epgap = (not s50 or price > s50) and price >= EP_MIN_PRICE
        over200 = bool(s200 and price > s200)
        power = epgap and gap >= R.get("power_gap", 8)
        under = [n for n, m in (("50 EMA", s50), ("200 SMA", s200)) if m and close0 < m]
        catalyst = not only_ep and over200 and bool(under) and bool(s50) and price > s50
        launch = not only_ep and over200 and price > pivot and chg >= R["min_chg"]
        if not (epgap or catalyst or launch):
            continue
        ern = q[6] if len(q) > 6 else None
        earn = bool(ern and after_close <= ern <= now.timestamp() + 3600)
        group, gstat = w[8], w[9]
        theme = gtext(w)
        what, need = (("power-day gap", f"{R.get('power_rv', 3):g}x+ and up {R.get('power_chg', 10):g}%+") if power else ("catalyst gap", "3x+") if catalyst
                      else ("launch gap", "3x+") if launch else ("EP gap", f"{EP_RV:g}x+"))
        lvl = "" if not hc21 or not (power or not (catalyst or launch)) else (
            f" · opened over its 21-day closing high ${hc21:.2f}" if op > hc21
            else f" · opened {100 * (1 - op / hc21):.1f}% under its 21-day closing high ${hc21:.2f}: the alert needs the {EP_ORH_MIN}-minute opening range high and that level")
        out.append((f"{sym}:early", f"{sym} EARLY: {what} " + ("on earnings" if earn else "(news? no earnings)"),
                    f"gap {gap:+.1f}% · ${price:.2f} ({chg:+.1f}%)"
                    + (f" · was under its {' & '.join(under)}, now above the 50 EMA & 200 SMA" if under and price > s50 and over200 else "")
                    + (f" · under its 200 SMA ${s200:.2f}" if s200 and not over200 else "") + lvl
                    + f" · base high ${pivot:.2f} " + ("cleared" if price > pivot else "not cleared")
                    + (f" · vol {rv:.1f}x so far (rough: the opening auction)" if rv else "")
                    + f" · the full alert from 9:35 if the volume confirms ({need}) · theme {theme}", "default", w[10]))
    return out


EARLY_LIST_GAP = 5.0          # the gap a followed name needs for its early heads-up


def list_names(doc, lists_doc=None):
    """{symbol: [the lists it is on]}: Launches (with the 50 EMA undercut tab and the laggards), 3-SETUPS, Start days
    (launch.json) and the Watchlist's lists (setups/latest.json: 1-EP/GAP, 1-UPDAY, 2-POOL, the TREND names' sources)"""
    out = {}
    for name, rows in (("Launches", (doc.get("launches") or []) + (doc.get("ema50_undercut") or []) + (doc.get("laggards") or [])),
                       ("3-SETUPS", doc.get("setups3") or []), ("Start days", doc.get("start_days") or [])):
        for r in rows:
            if r.get("symbol") and name not in out.setdefault(r["symbol"], []):
                out[r["symbol"]].append(name)
    for name, rows in ((lists_doc or {}).get("lists") or {}).items():
        if name == "3-SETUPS":
            continue
        for r in rows or []:
            if isinstance(r, dict) and r.get("symbol") and name not in out.setdefault(r["symbol"], []):
                out[r["symbol"]].append(name)
    return out


def find_early_lists(live, doc, lists_doc, skip=()):
    """the early heads-up, 9:31-9:34, for the names the user follows that find_early leaves out (the user, Nov 18 2026: "gap
    heads up can you include my wl (ep + trend + start + setups) too"). find_early reads launch.json watch, which drops a
    stock that launched in the last 20 sessions: 34 of the 49 1-EP/GAP names, 38 of the 94 3-SETUPS names and 13 of the 44
    Start days that day, all on Launches. For them: gapping up 5%+ and still over the open; no shape, no volume. One
    heads-up a stock (the same key as find_early's)"""
    rows, out = live.get("rows") or {}, []
    for sym, names in sorted(list_names(doc, lists_doc).items()):
        q = rows.get(sym)
        if sym in skip or sym in (doc.get("watch") or {}) or not q or len(q) < 6 or not q[5] or not q[0] or q[1] is None:
            continue
        price, chg, rv, op = q[0], q[1], q[4], q[5]
        gap = (op / (price / (1 + chg / 100)) - 1) * 100
        if gap < EARLY_LIST_GAP or price <= op:
            continue
        r = row_of(doc, sym) or {}
        out.append((f"{sym}:early", f"{sym} EARLY: gapping {gap:+.1f}% (on {', '.join(names)})",
                    f"gap {gap:+.1f}% · ${price:.2f} ({chg:+.1f}%), over its open ${op:.2f}"
                    + (f" · buy point ${r['buy_point']:.2f} " + ("cleared" if price > r["buy_point"] else "not cleared") if r.get("buy_point") else "")
                    + (f" · vol {rv:.1f}x so far (rough: the opening auction)" if rv else "")
                    + " · its own alerts follow from 9:35", "default", r.get("tv") or r.get("tv_symbol") or sym))
    return out


def gtext(w):
    """the group line in a launch alert: the group rank and RS (watch fields 15-16, Nov 3 2026), else the old status"""
    if len(w) > 16 and (w[15] or w[16] is not None):
        return (w[15] or "no ranked group") + (f" · RS {w[16]}" + (" ★" if w[16] >= 97 else "") if w[16] is not None else "")
    group, gstat = w[8], w[9]
    return f"{group} ({['not trending', 'turning up', 'leading'][gstat] if gstat in (0, 1, 2) else 'no group'})" if group else "no group"


def find(live, doc, now=None):
    """[(key, title, message, priority, tv symbol)] for everything that fires right now"""
    R, rows, out = doc["rules"], live["rows"], []
    now = now or datetime.datetime.now(NY)
    d0 = datetime.date.fromisoformat(doc["date"])                 # the last close the watch list was built from
    after_close = datetime.datetime(d0.year, d0.month, d0.day, 15, 30, tzinfo=NY).timestamp()
    _EP_NEED_ORH.clear()
    for sym, w, only_ep in ep_names(doc):
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
        # the episodic pivot and the power day (the rules above find_early; the user, Nov 21 2026): over the 50 EMA, $10+
        # now, over the highest close of the last 21 sessions (no number = not checked), no 200 SMA and no 1-month-high rule
        hc21 = (doc.get("watch_close_high_21d") or {}).get(sym)
        ep_base = (gap is not None and (not s50 or price > s50) and price >= EP_MIN_PRICE and (not hc21 or price > hc21))
        power = ep_base and rv >= R.get("power_rv", 4) and gap >= R.get("power_gap", 8) and chg >= R.get("power_chg", 10)
        ep = ep_base and rv >= EP_RV and gap >= EP_GAP
        opened_under = bool(hc21 and op and op <= hc21)
        if (power or ep) and opened_under:
            _EP_NEED_ORH[sym] = hc21                               # main(): only over its 3-minute opening range high too
        if only_ep and not (power or ep):
            continue
        if s200 and price <= s200 and not (power or ep):
            # a laggard launch (the Launch Laggards tab): under the 200 SMA, on earnings or this morning's A/B-graded news,
            # up 5%+ from an up open on 2x+ volume
            news, lo52 = doc.get("_news_today", {}).get(sym), (w[14] if len(w) > 14 else None)
            if ((earn or news) and gap is not None and gap > 0 and chg >= R["min_chg"] and rv >= R.get("lag_rv", 2) and price > pivot
                    and (not s50 or price > s50)                         # over the 50 EMA (the user, Nov 4 2026)
                    and (not lo52 or price >= lo52 * (1 + R["min_above_low52"] / 100))):
                g = grade(rv, price > pivot, gap, chg, R, False)
                out.append((f"{sym}:laggard", f"{sym} {g} LAGGARD launch on " + ("earnings" if earn else "news (" + news + ")"),
                            f"{chg:+.1f}% · gap {gap:+.1f}% · vol {rv:.1f}x for the time of day · ${price:.2f}, "
                            f"{100 * (price / s200 - 1):+.1f}% vs the 200 SMA ${s200:.2f} · base high ${pivot:.2f} "
                            + ("cleared" if price > pivot else "not cleared") + " · moves to Launches after 5 closes over the 200 SMA",
                            "default", tvs))
        if (not s200 or price <= s200) and not (power or ep):
            continue
        ext = (close0 / s200 - 1) * 100 if s200 else 0.0
        # an episodic pivot (the user, Nov 4 2026; in this job Nov 5, so every device has it): a volume pace of 3x+ (was 4x), a 6%+
        # gap, over the 1-month high and the 200 SMA; a power day (8%+ gap, +10%) is one and alerts as the power day
        # (CHYM Nov 5: gap +6.4%, up 4.7%, 5x: an EP, not a power day)
        # a volume pace of 3x+ (the user, Nov 5 2026 evening: "change the rule for the episodic pivot: 3 rvol at least,
        # everything else stays the same"; was 4x, the power day's)
        # (until Nov 21 2026: 3x, a 6%+ gap, over the 1-month high and the 200 SMA, and it had to OPEN over the highest close of
        # the last 21 sessions: the user, Nov 5 2026, "the whole point is to gap up above it"; WRBY Nov 5 opened 25.93 under
        # its 26.52 and fired a power day at 12:35 on a 1-cent pass of its 27.00 high, then closed 26.10. Now a stock that
        # opened under that level needs the price over it AND over its 3-minute opening range high: main() checks it)
        if ext > R.get("power_ext200", 50) or (ext > R["max_ext200"] and not (power or ep)):
            continue
        theme = gtext(w)
        facts = f"{chg:+.1f}% · gap {gap:+.1f}% · vol {rv:.1f}x for the time of day" if gap is not None else f"{chg:+.1f}% · vol {rv:.1f}x"
        under = [n for n, m in (("50 EMA", s50), ("200 SMA", s200)) if m and close0 < m]
        over = bool(s50) and price > s50 and bool(s200) and price > s200
        crossed = f" · was under its {' & '.join(under)}, now above the 50 EMA & 200 SMA" if under and over else ""
        # how far under its 52-week high it trades now, and the correction it is coming out of (AXGN Oct 28 2026: 14% under
        # its 52-week high at $45.48, after a 36% correction; not "36% off its high", which was yesterday's depth)
        neglect = (f" · {100 * (1 - price / w[5]):.0f}% under its 52-week high (${w[5]:.2f})" if w[5] and price < w[5] else " · at a 52-week high" if w[5] else "") \
            + (f", after a {w[7]:.0f}% correction" if w[7] and w[7] >= 15 else "")
        cat = " · EARNINGS" if earn else ""
        bo = price > pivot or bool(mem and price > mem[1])
        g = grade(max(rv, R["rv_big"]), bo, max(gap or 0, R["gap_big"]), chg, R, False) if mem else grade(rv, bo, gap, chg, R, bool(s200) and close0 < s200)
        # what the EP / power-day alert says about its levels: the 21-day closing high it is over (and how it opened), the
        # 200 SMA when it is under it or has none yet
        lv21 = ("" if not hc21 else f" over its 21-day closing high ${hc21:.2f}"
                + (f" (opened {100 * (1 - op / hc21):.1f}% under it)" if opened_under else ""))
        s2txt = (" · no 200 SMA yet" if not s200 else f" · under its 200 SMA ${s200:.2f}" if price <= s200 else "")
        shape = bool(under) and over and gap is not None and gap >= R.get("ep_gap", 5)    # a catalyst gap, whatever the volume
        if shape and price > pivot and rv >= 1 and not only_ep:      # (an ep_watch name gets the EP / power day alert only)
            # the 2nd trigger: sent only after a catalyst alert that hadn't cleared the base yet (see main)
            out.append((f"{sym}:basebreak", f"{sym} 2nd trigger: base high ${pivot:.2f} cleared",
                        f"${price:.2f} · {chg:+.1f}% · vol {rv:.1f}x for the time of day · grade so far {g}{cat}"
                        f" · after its catalyst gap over the 50 EMA & 200 SMA · theme {theme}", "high", tvs))
        if power:
            out.append((f"{sym}:power", f"{sym} POWER DAY" + (" on earnings" if earn else ""),
                        f"{facts} · ${price:.2f}{lv21}{s2txt}{crossed}{neglect} · theme {theme}", "high", tvs))
            continue
        if ep:                                                     # stands for this stock's catalyst gap, A launch and laggard launch
            out.append((f"{sym}:ep", f"{sym} EPISODIC PIVOT" + (" on earnings" if earn else ""),
                        f"{facts} · ${price:.2f}{lv21}{s2txt}{crossed}{neglect} · grade so far {g} · theme {theme}",
                        "high", tvs))
            continue
        if shape and rv >= R["rv_big"]:
            out.append((f"{sym}:catalyst", f"{sym} CATALYST GAP: " + ("earnings" if earn else "news? (no earnings)")
                        + ", over its 50 EMA & 200 SMA", f"{facts} · ${price:.2f}{crossed}{neglect} · base high ${pivot:.2f} "
                        + (f"cleared (grade so far {g})" if price > pivot else "not cleared yet: 2nd alert when it is") + f" · theme {theme}", "high", tvs))
        # a reversal launch (your rule, Nov 1 2026; GDDY Oct 30): it opened under yesterday's close and now trades up 8%+ on
        # a volume pace of 2x+, over its 1-month high (the previous 20 sessions' highest high, wicks and bodies) and 30%+
        # over its 52-week low; the top half of today's range is checked on today's 1-minute chart before it goes out (main)
        low52 = w[14] if len(w) > 14 else None
        if (R.get("reversal_launch") and gap is not None and gap < 0 and chg >= R.get("rev_chg", 8) and rv >= R.get("rev_rv", 2)
                and price > pivot and (not low52 or price >= low52 * (1 + R["min_above_low52"] / 100))):
            out.append((f"{sym}:reversal", f"{sym} REVERSAL launch" + (" on earnings" if earn else ""),
                        f"opened {gap:+.1f}%, now {chg:+.1f}% · vol {rv:.1f}x for the time of day · ${price:.2f} over its 1-month high"
                        f" ${pivot:.2f}{crossed}{neglect} · the close confirms it (up 8%+, top half of the day) · theme {theme}", "high", tvs))
            continue
        if chg < R["min_chg"] or rv < R["min_rv"] or (gap is not None and gap <= 0):
            continue
        if g in ("A+", "A"):
            out.append((f"{sym}:launch", f"{sym} {g} launch", f"{facts}{cat} · ${price:.2f} through its base high ${pivot:.2f}"
                        + (" (delayed: faded gap " + mem[0] + ")" if mem else "") + f"{crossed} · theme {theme}", "high" if g == "A+" else "default", tvs))
    for r in doc.get("launches", []) + doc.get("laggards", []) + s3_rows(doc):
        try:
            q = rows.get(r["symbol"])
            if not q or len(q) < 5 or q[4] is None:
                continue
            if (r.get("cycle_warn") or "").startswith("END OF CYCLE"):
                continue                    # stalled at its highs: no buy alerts until a close over the stalled high (the user, Nov 13 2026)
            if gob_of(r, q):
                continue                    # gapping out of its base: the gap-out-of-base alerts (find_gob) have it today
            price, chg, rv = q[0], q[1], q[4]
            op = q[5] if len(q) > 5 else None
            sym, tvs = r["symbol"], r.get("tv") or r["symbol"]
            # the 21 EMA reclaim on a strong day (the user, Nov 13 2026: AMD Jun 11 2026 "21 ema undercut and reclaim"): a followed
            # launch that closed under its 21 EMA, over the 50 EMA, trades back over the 21 EMA on a 2%+ gap that opened over it or
            # up 1 ADR+, from 9:36
            e21_, e50_, adr_ = r.get("ema21"), r.get("ema50"), r.get("adr_pct")
            if (e21_ and e50_ and adr_ and not r.get("off_now") and (r.get("price") or 0) < e21_ and (r.get("price") or 0) > e50_ and price > e21_
                    and (now.hour, now.minute) >= (9, 36) and op
                    and ((op > e21_ and 100 * (op / (price / (1 + chg / 100)) - 1) >= doc["rules"].get("pop21_gap", 2) and chg > 0) or chg >= adr_)):
                out.append((f"{sym}:ema21strong", f"{sym} entry: back over its 21 EMA on a strong day",
                            f"closed under the 21 EMA ${e21_:.2f} (over the 50 EMA ${e50_:.2f}), now ${price:.2f} back over it · {chg:+.1f}% "
                            f"({chg / adr_:.1f} ADR) · vol {rv:.1f}x for the time of day · the 21 EMA undercut & reclaim on a strong day, "
                            f"a short swing entry; the close confirms it" + since(r), "default", tvs))
            late = bool(r.get("late"))
            ago = r.get("last_breakout_days_ago")
            # a breakout a few sessions after the last one is the same push (RPD Oct 22 / Oct 23): the same leg
            nxt = (r.get("leg") or 0) + (0 if ago is not None and ago < doc["rules"].get("leg_pause", 5) else 1)
            # the pop out of a consolidation is an entry inside the base, not a new leg (ANF Oct 5 2026); so is the break of
            # a bull flag's falling line: the leg comes with the close over the base top (TTAN Oct 30 2026)
            inside = (r.get("pattern") or "").startswith("Pop out of the consolidation")
            flag = (r.get("pattern") or "").startswith(("Flag", "Bull flag", "Bull pennant", "Pennant"))
            if inside or flag:
                nxt = r.get("leg") or 0
            # confirmation: in the 3 sessions after a base breakout, it opens and trades above the base top on 2x+ volume
            # (RPD Oct 26 2026, after breaking its Aug high on Oct 23)
            top = r.get("last_breakout_top")
            confirm = (f"{sym}:confirm", f"{sym} breakout confirmed",
                       f"opened ${op:.2f} and trades ${price:.2f} above the base top ${top:.2f} (broken {r['last_breakout_date']})"
                       f" · {chg:+.1f}% · vol {rv:.1f}x for the time of day", "high", tvs) \
                if top and ago is not None and ago <= 2 and op and op > top and price > top and rv >= 2 else None
            # the 21 EMA entries in the base, set up at the last close (scanner/launch.py follow, ema21_watch)
            w21, e21, adr21 = r.get("ema21_watch"), r.get("ema21"), r.get("adr_pct") or 5.0
            if w21 and e21 and (now.hour, now.minute) >= (9, 35):
                kind = ("undercut & reclaim (2 closes under it: strong)" if w21 == "undercut" else "retest (a controlled pullback into it)")
                tail21 = f" · {chg:+.1f}% · vol {rv:.1f}x · leg {r.get('leg')}" + since(r)
                if price <= e21 * (1 + adr21 / 400) and price > (r.get("ema50") or 0):
                    out.append((f"{sym}:ema21zone", f"{sym} at its 21 EMA in the base",
                                f"${price:.2f} at the 21 EMA ${e21:.2f} (the last close's) · a 21 EMA {kind} setup: the buy is the close back"
                                f" over it, in the upper half of the day" + tail21, "default", tvs))
                if (now.hour, now.minute) >= (15, 45) and e21 < price <= e21 * (1 + 1.5 * adr21 / 100):
                    # today's low under the 21 EMA and the open, the price in the upper half of the day: checked on today's
                    # 1-minute chart before it goes out (main)
                    out.append((f"{sym}:ema21", f"{sym} 21 EMA {'UNDERCUT & RECLAIM' if w21 == 'undercut' else 'RETEST'} holding into the close",
                                f"back over the 21 EMA ${e21:.2f} (the last close's) at ${price:.2f}"
                                f" · the buy: at the close, if it holds over it" + tail21, "high" if w21 == "undercut" else "default", tvs))
            # the breakout undercut & reclaim (the user's CAI Oct 9 2026): 2+ closes back under the breakout level, holding over the
            # 50 EMA; today back over it: a heads-up as it crosses, from 3:45 PM holding into the close (the buy: the close)
            rl = r.get("reclaim_level")
            if rl and (now.hour, now.minute) >= (9, 35) and price > rl:
                tail_ = f" · {chg:+.1f}% · vol {rv:.1f}x · leg {r.get('leg')}" + since(r)
                out.append((f"{sym}:reclaimbo", f"{sym} back over its breakout level", f"${price:.2f} over the breakout level ${rl:.2f} after closing under it"
                            f" · the buy: the close back over it (the breakout undercut & reclaim)" + tail_, "default", tvs))
                if (now.hour, now.minute) >= (15, 45):
                    out.append((f"{sym}:reclaimbo2", f"{sym} BREAKOUT UNDERCUT & RECLAIM holding into the close", f"${price:.2f} back over the breakout"
                                f" level ${rl:.2f} after closing under it, holding over the 50 EMA · the buy: at the close, if it holds" + tail_, "high", tvs))
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
            if pl and op and r.get("day_open") and op > max(r["day_open"], r["price"]) and price > pl:     # whatever the volume
                gap_ = (op / (price / (1 + chg / 100)) - 1) * 100
                out.append((f"{sym}:push", f"{sym} entry: push out of the 10 / 21 EMA with a gap",
                            f"opened ${op:.2f} ({gap_:+.1f}%) over yesterday's candle, now ${price:.2f} over the trigger ${pl:.2f}"
                            f" (yesterday's candle, its 10 & 21 EMA and the breakout level, all reclaimed)"
                            f" · after the retest of its breakout level ${r.get('retest_level'):.2f} (touched {r.get('retest_tried')})"
                            f" · {chg:+.1f}% · vol {rv:.1f}x for the time of day" + (" (light)" if rv < 1 else "") + f" · leg {r.get('leg')}" + since(r), "high", tvs))
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
                # 3-SETUPS rows carry no base_days (Nov 4 2026: int(r['base_days']) raised on AMLX / XMTR ... and every check from
                # 9:35 crashed: no alert all day after the 9:31-9:34 heads-ups)
                bd = r.get("base_days")
                what = (f"base top ${bp:.2f} (set {r['buy_point_top_date']}" + (f"; nothing traded above it for {int(bd)} sessions" if bd else "")
                        + f"; decisive with a close more than 0.5% over it, ${bp * 1.005:.2f}: within 0.5% a breakout with caution)"
                        if pat == "Base top" and r.get("buy_point_top_date") else f"buy point ${bp:.2f}")
                # the breakout that also pushed out of the 10 & 21 EMA with a gap: opened over yesterday's candle (its open and
                # close) and both EMAs, a double confluence (GMAB Oct 5 2026)
                push = bool(op and r.get("day_open") and r.get("ema10") and r.get("ema21")
                            and op > max(r["day_open"], r["price"], r["ema10"], r["ema21"]))
                why += " · also pushed out of the 10 & 21 EMA with a gap (opened over yesterday's candle)" if push else ""
                # the base's length (the user, Nov 6 2026: "add base days"; the portal's voice reads it out): the Base length
                # column, sessions since the base's top at the last close (the top's day = day 1); not Base day, which counts
                # from the leg's breakout when the stock isn't in a base (FLS Nov 9 2026: Base day 52, its base 5 days)
                blen = int(round(r.get("trig_base_len") or 0))
                out.append((f"{sym}:breakout", f"{sym} {g} breakout: {pat}",
                            f"${price:.2f} over the {what} · {why} · {chg:+.1f}% · vol {rv:.1f}x for the time of day"
                            + (" (light)" if rv < 1 else "") + (f" · base {blen} day{'' if blen == 1 else 's'}" if blen >= 1 else "") + " · "
                            + (f"an entry in the base (still leg {nxt}), the base top is next" if flag else f"would be leg {nxt}" + (" (late)" if nxt >= 4 else ""))
                            + ("" if "group_tier_now" in r else f" · theme {r.get('group_now') or '-'} ({(r.get('group_status_now') or '').lower()})")
                            + since(r), "high" if g == "A" else "default", tvs))
        except Exception as ex:                     # one bad row skips that stock, not every alert (Nov 4 2026)
            print(f"alerts: {r.get('symbol')} skipped: {ex!r}", file=sys.stderr)
    # the 50 EMA undercut tab: 2 closes in a row under the 50 EMA at the last close; today it has to close back over it
    for r in doc.get("ema50_undercut", []):
        q = rows.get(r["symbol"])
        if not q or len(q) < 5 or q[4] is None or (now.hour, now.minute) < (9, 35):
            continue
        sym, tvs = r["symbol"], r.get("tv") or r["symbol"]
        price, chg, rv = q[0], q[1], q[4]
        e50, adr50 = r.get("ema50"), r.get("adr_pct") or 5.0
        if not e50 or price <= e50:
            continue
        dates = " & ".join(r.get("ema50_under_dates") or [])
        tail50 = f" · {chg:+.1f}% · vol {rv:.1f}x" + since(r)
        out.append((f"{sym}:ema50back", f"{sym} back over its 50 EMA",
                    f"${price:.2f} over the 50 EMA ${e50:.2f} (the last close's) after 2 closes under it ({dates}) · the buy: the close back"
                    f" over it, in the upper half of the day (the 50 EMA undercut & reclaim); a 3rd close under takes it off the list" + tail50,
                    "default", tvs))
        if (now.hour, now.minute) >= (15, 45) and price <= e50 * (1 + 1.5 * adr50 / 100):
            # today's low under the 50 EMA and the open, the price in the upper half of the day: checked on today's
            # 1-minute chart before it goes out (main)
            out.append((f"{sym}:ema50", f"{sym} 50 EMA UNDERCUT & RECLAIM holding into the close",
                        f"back over the 50 EMA ${e50:.2f} (the last close's) at ${price:.2f} after 2 closes under it ({dates})"
                        f" · the buy: at the close, if it holds over it" + tail50, "high", tvs))
    # 3-SETUPS (Watchlist tab) on the phone too (the user, Nov 3 2026; the desktop had them): a name trading over its
    # trigger, any section, once a day; a name also on Launches / Launch laggards alerts from there
    followed = {r["symbol"] for r in doc.get("launches", []) + doc.get("laggards", [])}
    for r in doc.get("setups3") or []:
        sym, bp = r.get("symbol"), r.get("buy_point")
        if not sym or not bp or sym in followed or r.get("live") or (r.get("away_adr") is not None and r["away_adr"] < 0):
            continue                                    # no trigger, or the close was already over it
        q = rows.get(sym)
        if not q or len(q) < 5 or q[4] is None or not q[0] > bp:
            continue
        price, chg, rv = q[0], q[1], q[4]
        out.append((f"{sym}:s3", f"{sym} 3-SETUPS {r.get('section', '')}: {r.get('setup', '')} trigger",
                    f"${price:.2f} over ${bp:.2f} · {chg:+.1f}% · vol {rv:.1f}x for the time of day" + (" (light)" if rv < 1 else "")
                    + (f" · {r['why']}" if r.get("why") else ""), "default", r.get("tv") or sym))
    return out


def find_start(live, doc, now, sent=()):
    """the START DAY as it happens (the user, Nov 13 2026: "do alerts go live"; RKLB Nov 9 2026: "clear downtrending stock, november
    9th was a start point upward"): a stock that closed under its 21 or 50 EMA after a downtrend (launch.json start_watch, from the
    last close) trades over its 21 EMA, up 1 ADR+ (or 4%+ with 0.8 ADR+) on a volume pace of 1x+, over the high of any violent red candle of the last 5
    sessions, in the top half of today's range and over its 5-minute opening range high (the user's entry; the stop: today's low).
    Any liquid stock, on the list or not. From 9:35. Tags: launch size under the 200 SMA; after a reset (AMD Sep 8 2026)"""
    out = []
    if (now.hour, now.minute) < (9, 36):
        return out
    R = doc.get("rules", {})
    for sym, w in (doc.get("start_watch") or {}).items():
        q = live["rows"].get(sym)
        if f"{sym}:start" in sent or not q or len(q) < 8 or q[4] is None or q[0] is None or q[1] is None:
            continue
        price, chg, rv, op, hi = q[0], q[1], q[4], q[5], q[7]
        e21, e50, adr, red, u200, rs_n, rs_lv, first, tvs = w[:9]
        # up 1 ADR+, or up 4%+ with 0.8 ADR+ (the user, Nov 15 2026: ZETA Nov 9, TTEK Oct 15; the rules come with launch.json)
        move = chg >= R.get("start_adr", 1) * adr or ("start_pct" in R and chg >= max(R["start_pct"], R.get("start_pct_adr", 0.8) * adr))
        if not (price > e21 and move and rv >= R.get("start_rv", 1) and price > (red or 0)):
            continue
        orh, low = opening_range_high(sym), chart_low_today(sym)
        if not orh or not low or not price > orh or (hi and price < (hi + low) / 2):
            continue
        tag = ""
        if not first and not (rs_n and rs_lv and price > rs_lv and price > e50):
            continue                    # a start came before: only the reset start (over both EMAs and the last lower high) alerts
        if rs_n and rs_lv and price > rs_lv and price > e50:
            tag = f" · NEW TREND after a reset: {rs_n} lower highs, now over the last one ${rs_lv:.2f}"
        elif u200 and price > e50 and chg >= R.get("min_chg", 5) and rv >= R.get("first_rv", 1.3):
            tag = " · launch size, from under the 200 SMA"
        conf = (f"over the 50 EMA ${e50:.2f} too" if price > e50 else f"still under the 50 EMA ${e50:.2f}: the close over it is the confirmation")
        out.append((f"{sym}:start", f"{sym} START DAY: over its 21 EMA after a downtrend",
                    f"{chg:+.1f}% ({chg / adr:.1f} ADR) · vol {rv:.1f}x for the time of day · ${price:.2f} over the 21 EMA ${e21:.2f} (the last close's), "
                    f"{conf} · over the 5-min opening range high ${orh:.2f} · stop: today's low ${low:.2f} ({100 * (price / low - 1) / adr:.1f} ADR)"
                    + (f" · over the red candle's high ${red:.2f}" if red else "") + tag, "high", tvs))   # always high on the phone (the user, Nov 17 2026: "its important one"; was high only with a tag)
    return out


def find_range(live, doc, now, sent=()):
    """the BREAKOUT OF A FALLING RANGE as it happens (the user, Nov 13 2026: "breakout of falling range its good alert"; INTC Apr 1
    2026): a list stock (on the list, or off it waiting for its way back; launch.json range_watch, from the last close) trades
    over its falling line (the line through the lower highs from the range's top) and over the 21 and 50 EMA, up on the day on a
    volume pace of 1x+ or a 1 ADR+ day, with a 1 ADR+ day or a 2%+ gap, in the top half of today's range and over its 5-minute
    opening range high. From 9:36"""
    out = []
    if (now.hour, now.minute) < (9, 36):
        return out
    R = doc.get("rules", {})
    for sym, w in (doc.get("range_watch") or {}).items():
        q = live["rows"].get(sym)
        if f"{sym}:rangebo" in sent or not q or len(q) < 8 or q[4] is None or q[0] is None or q[1] is None:
            continue
        price, chg, rv, op, hi = q[0], q[1], q[4], q[5], q[7]
        line, e21, e50, adr, top_d, top, tvs = w[:7]
        gap = 100 * (op / (price / (1 + chg / 100)) - 1) if op else 0
        if not (price > line and price > e21 and price > e50 and chg > 0 and (rv >= 1 or chg >= adr)
                and (chg >= R.get("range_day_adr", 1) * adr or gap >= R.get("range_gap", 2))):
            continue
        orh, low = opening_range_high(sym), chart_low_today(sym)
        if not orh or not low or not price > orh or (hi and price < (hi + low) / 2):
            continue
        out.append((f"{sym}:rangebo", f"{sym} BREAKOUT of its falling range",
                    f"${price:.2f} over the falling line ${line:.2f} (from the {top_d} high ${top:.2f}) and over the 21 & 50 EMA "
                    f"${e21:.2f} / ${e50:.2f} · {chg:+.1f}% ({chg / adr:.1f} ADR)" + (f", a {gap:.1f}% gap" if gap >= 2 else "")
                    + f" · vol {rv:.1f}x for the time of day · over the 5-min opening range high ${orh:.2f} · stop: today's low ${low:.2f} "
                    f"({100 * (price / low - 1) / adr:.1f} ADR) · the close over the line confirms it", "high", tvs))
    return out


def gob_of(r, q):
    """a followed launch gapping out of its base today (your rule, Nov 1 2026): (base high, open) or None. The base high
    is last night's (scanner/launch.py gap_base_level: the base top or a pattern's pivot, not a flag line or a pop), the
    stock qualified at that close (gap_base_ok: ADR 4%+, 600K+ shares and $30M+ a day, market cap $700M+) and closed at
    or under it"""
    gl = r.get("gap_base_level")
    op = q[5] if q and len(q) > 5 else None
    if not (gl and r.get("gap_base_ok") and op and (r.get("price") or 0) <= gl < op):
        return None
    return gl, op


def find_gob(live, doc, now=None):
    """the gap-out-of-base candidates right now; main() reads today's 1-minute chart for the opening ranges before
    they go out (gob_bars)"""
    R, rows, out = doc["rules"], live["rows"], []
    now = now or datetime.datetime.now(NY)
    m = now.hour * 60 + now.minute - 570                # minutes since 9:30
    if m < 1:
        return out
    for r in doc.get("launches", []) + s3_rows(doc):
        sym, tvs = r["symbol"], r.get("tv") or r["symbol"]
        q = rows.get(sym)
        if not q or len(q) < 6 or q[4] is None:
            continue
        g = gob_of(r, q)
        if not g:
            continue
        gl, op = g
        price, chg, rv = q[0], q[1], q[4]
        pat = r.get("gap_base_pattern") or "Base top"
        base = f"opened ${op:.2f}, {100 * (op / gl - 1):+.1f}% over its base high ${gl:.2f} ({pat})"
        tail = f" · vol {rv:.1f}x for the time of day" + since(r)
        # the volume pace your rule needs (the user, Nov 16 2026: "I want to drop 2x to 1x, and when it gets to 2x it can
        # alert me"; KVYO that day: 1.1x at 9:50, over its opening range high $22.72 later in the morning, and the 1- / 5-min
        # alerts only came at 12:30 with the volume at 2.0x and the price at $23.76): 1x+ all day (gob_rv), at the 9:50
        # check too; 2x+ (gob_rv20) is a notice of its own from 9:50
        need, big = R.get("gob_rv", 1), R.get("gob_rv20", 2)
        if 20 <= m <= 60:                               # 9:50-10:30: the volume check (sent only after a gap alert)
            ok = rv >= need
            out.append((f"{sym}:gob950", f"{sym} gap out of base: " + (f"keep it, vol {rv:.1f}x at 9:50" if ok else f"OUT, vol {rv:.1f}x under {need:g}x at 9:50"),
                        f"your rule: a volume pace of {need:g}x+ by 20 minutes after the open, else out whatever the trade ({big:g}x+ gets its own alert) · ${price:.2f} ({chg:+.1f}%) · {base}"
                        + since(r), "default" if ok else "high", tvs))
        if price <= gl:
            continue                                    # back under its base high: the gap failed, no buy
        if rv < need:
            continue                                    # the volume pace your rule needs at the buy: 1x+
        out.append((f"{sym}:gapbase", f"{sym} GAP OUT OF BASE", f"{base} · now ${price:.2f} ({chg:+.1f}%)" + tail
                    + f" · the entry: over the 1-minute or the 5-minute opening range high, the stop its low; out at 9:50 if the volume pace isn't {need:g}x",
                    "default", tvs))
        out.append((f"{sym}:gob1", f"{sym} gap out of base: 1-min high broke", base + tail, "high", tvs))
        if m >= 5:
            out.append((f"{sym}:gob5", f"{sym} gap out of base: 5-min high broke", base + tail, "high", tvs))
        if m >= 20 and rv >= big:                       # after a gap alert only (main())
            out.append((f"{sym}:gob2x", f"{sym} gap out of base: volume now {rv:.1f}x", f"the volume pace reached {big:g}x+ · ${price:.2f} ({chg:+.1f}%) · {base}"
                        + since(r), "default", tvs))
    return out


def gob_bars(sym):
    """today's 1-minute bars from 9:30 on, from Yahoo's chart: [(minutes since 9:30, high, low)], or None"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym.replace('/', '-').replace('.', '-'))}?range=1d&interval=1m"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.load(r)["chart"]["result"][0]
        today = datetime.datetime.now(NY).date()
        qd = res["indicators"]["quote"][0]
        out = []
        for t, hi, lo in zip(res.get("timestamp") or [], qd.get("high") or [], qd.get("low") or []):
            d = datetime.datetime.fromtimestamp(t, NY)
            mm = d.hour * 60 + d.minute - 570
            if hi and lo and d.date() == today and mm >= 0:
                out.append((mm, hi, lo))
        return out or None
    except Exception:
        return None


def gob_range(bars, n):
    """the opening range of the first n minutes (1 or 5) and whether a later bar traded over its high: (high, low, broke)"""
    if not bars or bars[0][0] > 5:
        return None
    t0 = bars[0][0]                                     # the first minute of trading (a late NYSE open counts from it)
    rng = [b for b in bars if b[0] < t0 + n]
    after = [b for b in bars if b[0] >= t0 + n]
    if not rng:
        return None
    hi, lo = max(b[1] for b in rng), min(b[2] for b in rng)
    return hi, lo, any(b[1] > hi for b in after)


def s3_rows(doc):
    """3-SETUPS names not on Launches / Launch laggards, as launch-like rows for their live entries (setups3 "live",
    scanner/launch.py S3_LIVE): every buy point, as on Launches (the user, Nov 3 2026: AMPL's retest of its breakout
    level with the 21 EMA had no alert; Nov 1: desktop alerts for every 3-SETUPS trigger). The best group's tier from
    the group rank (the stock's themes and tight group)"""
    if "_s3rows" in doc:
        return doc["_s3rows"]
    followed = {r["symbol"] for r in doc.get("launches", []) + doc.get("laggards", [])}
    ranks = {r["group"]: r for r in (doc.get("group_rank") or {}).get("rows", []) if not r.get("loose")}
    out = []
    for r in doc.get("setups3") or []:
        if not r.get("live") or r.get("symbol") in followed:
            continue
        x = dict(r["live"], symbol=r["symbol"], tv=r.get("tv") or r["symbol"], s3=True, section=r.get("section"),
                 source=r.get("source"), added=r.get("added"))
        best = max((ranks[g] for g in _GROUPS.get(r["symbol"], []) if g in ranks), key=lambda g: g.get("pct") or 0, default=None)
        x["group_tier_now"] = (best or {}).get("tier") or ""
        x["group_rank_now"] = f"{best['group']} #{best['rank']}/{best['of']}" if best else None
        out.append(x)
    doc["_s3rows"] = out
    return out


def row_of(doc, sym):
    """a followed stock's row: Launches, Launch laggards, then 3-SETUPS"""
    return next((x for x in doc.get("launches", []) + doc.get("laggards", []) + s3_rows(doc) if x["symbol"] == sym), {})


def since(r):
    """how the stock came to be followed: its launch, your Follow button, or the 3-SETUPS list"""
    if r.get("s3"):
        return f" · 3-SETUPS {r.get('section') or ''} (from {r.get('source') or 'the watchlist'} {r.get('added') or ''})"
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


MIN_OVER_LOW52 = 30          # % over the 52-week low every alert needs (scanner/settings.json standard)
_LOW52 = None
_SMA200 = {}
_ADR = {}                    # symbol -> its 20-day ADR % (stocks.json adr_20)
_GROUPS = {}                 # symbol -> its themes and its tight industry group (stocks.json themes " | ", group)


def over_sma200(sym, live):
    """True when the live price is over the 200 SMA (the last close's); no SMA yet = not held back"""
    sma, q = _SMA200.get(sym), (live.get("rows") or {}).get(sym)
    return not sma or not q or not q[0] or q[0] > sma


def low52_of(launch_p):
    """{symbol: 52-week low} from the stocks file the live job keeps next to launch.json (base_stocks.json)"""
    global _LOW52
    if _LOW52 is None:
        _LOW52 = {}
        d = os.path.dirname(os.path.abspath(launch_p))
        for name in ("base_stocks.json", "stocks.json"):
            p = os.path.join(d, name)
            if os.path.exists(p):
                try:
                    st = json.load(open(p))
                    _LOW52 = {s["symbol"]: s.get("low_52w") for s in st}
                    _SMA200.update({s["symbol"]: s.get("sma200") for s in st})
                    _ADR.update({s["symbol"]: s.get("adr_20") for s in st})
                    _GROUPS.update({s["symbol"]: [t for t in str(s.get("themes") or "").split(" | ") if t]
                                    + ([s["group"]] if s.get("group") else []) for s in st})
                    break
                except Exception:
                    pass
    return _LOW52


def over_low52(sym, live, low):
    """True when the stock trades 30%+ over its 52-week low (or there is no low to check: a new listing, a summary)"""
    lo, q = low.get(sym), (live.get("rows") or {}).get(sym)
    if not lo or not q or not q[0]:
        return True
    return q[0] >= lo * (1 + MIN_OVER_LOW52 / 100)


def still_holds(key, title, found_keys, live, doc, memo):
    """a trigger sent today still meets its own rule at this check (the user, Nov 5 2026: "whatever doesn't hold, it has
    to be taken from that box"; "whatever the rule is, it's the rule"): find() finds it again on the latest prices (the
    price, the levels and the volume pace it needs), then the same 1-minute chart tests main() runs before sending it"""
    sym, kind = key.split(":", 1)
    if (sym + ":ema21" if kind == "ema21bl" else key) not in found_keys:
        return False
    if kind.startswith("para"):              # a parabolic short: find_para finds it again while its stop is not traded
        return True
    q = (live.get("rows") or {}).get(sym)
    if not q or not q[0]:
        return False
    price, op = q[0], (q[5] if len(q) > 5 else None)

    def got(name, fn):
        if (name, sym) not in memo:
            memo[(name, sym)] = fn(sym)
        return memo[(name, sym)]
    if kind == "retest":                     # the low in the zone as the pullback's low; over the 10 EMA unless it tested the 21
        r_, lo_ = row_of(doc, sym), got("lo", chart_low_today)
        z_ = r_.get("retest_zone") or [0, 0]
        need_ = min(r_.get("retest_need_low") or 0, 1e9 if r_.get("retest_testing") else (r_.get("retest_low") or 1e9))
        if not (lo_ and z_[0] <= lo_ <= min(z_[1], need_)):
            return False
        e10_, e21_, adr_ = r_.get("ema10") or 0, r_.get("ema21") or 0, r_.get("adr_pct") or 5.0
        return price > e10_ or lo_ <= e21_ * (1 + adr_ / 400)
    if kind in ("ema21", "ema21bl", "ema50"):  # the low under the EMA and the open, the price in the upper half of the day
        r_ = (next((x for x in doc.get("ema50_undercut", []) if x["symbol"] == sym), {}) if kind == "ema50" else row_of(doc, sym))
        e_ = r_.get("ema50" if kind == "ema50" else "ema21") or 0
        lo_, hi_ = got("lo", chart_low_today), got("hi", chart_high_today)
        if not (lo_ and hi_ and op and lo_ < e_ and lo_ < op and price - lo_ >= 0.5 * (hi_ - lo_)):
            return False
        return kind != "ema21bl" or bool(confluence_level(r_, price, lo_))
    if kind == "reversal":                   # in the top half of today's range
        lo_, hi_ = got("lo", chart_low_today), got("hi", chart_high_today)
        return bool(lo_ and hi_ and price - lo_ >= 0.5 * (hi_ - lo_))
    if kind in ("gob1", "gob5"):             # the opening range's high broken, the price over its low (the stop)
        rg = gob_range(got("bars", gob_bars), 1 if kind == "gob1" else 5)
        return bool(rg and rg[2] and price > rg[1])
    if kind in ("ep", "power"):              # it opened under its 21-day closing high: over the 3-minute range too
        return ep_orh_ok(sym, price)[0]
    return True


def update_holding(state, found, live, doc, now):
    """each run: today's triggers that still hold (state hold: the keys, at this time), the ones that stopped (lost: when
    and the price) and the ones holding again after that (back); the portal's boxes show only what holds. Returns the
    BACK ON alerts [(key, title, msg)] of the ⚡ power days / EPs and, with a volume pace of 1.5x+, the 🎯 pattern breakouts"""
    found_keys, t, memo = {a[0] for a in found}, f"{now:%H:%M}", {}
    lost, back, held, seen = state.setdefault("lost", {}), state.setdefault("back", {}), [], set()
    last, out = state.setdefault("trig_back", {}), []
    mins = lambda x: int(x[:2]) * 60 + int(x[3:5])
    for it in state.get("items", []):
        key = it.get("key", "")
        if it.get("kind") != "trigger" or key in seen or key.startswith(("grp:", "thm:", "summary:")) or key.endswith((":mbo", ":mbo2", ":ebd")) \
                or BACK_RE.match(key.split(":", 1)[-1]) or re.match(r"^ebdback\d{4}$", key.split(":", 1)[-1]):
            continue                                    # (the morning breakouts: morning_holding, on the user's settings; the
                                                        # earnings breakdowns: ebd_holding)
        seen.add(key)
        q = (live.get("rows") or {}).get(key.split(":")[0])
        px = round(q[0], 2) if q and q[0] else None
        if still_holds(key, it.get("title", ""), found_keys, live, doc, memo):
            held.append(key)
            if key in lost:
                back[key] = {"at": t, "price": px}
                del lost[key]
                sym, kind = key.split(":", 1)
                rv = q[4] if q and len(q) > 4 else None
                if (kind in BACK_EP or (kind in BACK_PATTERN and rv is not None and rv >= BACK_PATTERN_RV)) \
                        and (sym not in last or mins(t) - mins(last[sym]) >= BACK_EVERY):
                    last[sym] = t
                    what = "POWER DAY" if kind == "power" else "EPISODIC PIVOT" if kind == "ep" else "PATTERN BREAKOUT"
                    out.append((f"{sym}:{kind}back{now:%H%M}", f"{sym} {what} BACK ON" + (f" {q[1]:+.1f}%" if q[1] is not None else ""),
                                (f"{kind_words(key, it.get('title', ''))}: " if kind in BACK_PATTERN else "") + f"meets its rules again (first alert {it.get('time', '')})"
                                + f" · ${q[0]:.2f}" + (f" · {q[1]:+.1f}%" if q[1] is not None else "") + (f" · vol {rv:.1f}x for the time of day" if rv is not None else ""), it.get("tv") or sym))
        elif key not in lost:
            lost[key] = {"at": t, "price": px}
    # and every trigger its rules find right now, sent or not: a power day / EP that stops holding steps down to a launch
    # when the stock still meets a launch's rules (EPAM Nov 5: volume pace 3.6x at the close, under 4x; still an A launch)
    now_ = sorted({a[0] for a in found if is_trigger(a[0], a[1]) and not a[0].startswith(("grp:", "thm:", "summary:"))})
    state["hold"] = {"at": t, "keys": held, "now": now_}
    return out


# ───────── morning breakouts (the user, Nov 9 2026) ─────────
# "a trigger for my alerts: any stock that has broken the PDH and the opening range 5-min high, +5% for the day, at
# Rvol over 1"; "mainly for the morning session: I don't need it after 10:30 AM"; usually 9:36-9:45; every number
# adjustable, each extra criterion on or off (52-week low, 200 SMA, 50, the trend 10 over 21, 21 over 50 ...), the base
# criteria for volatility and liquidity from the Gainers tab with ADR 4%+; one alert when one fires, one batch when several
# fire at once. Any stock (not only the followed lists), checked every minute from start to end. On the portal only, no
# phone yet (the user: "I don't do the phone thing yet"). The settings: alerts/morning.json on main, saved by the portal's
# Save button (like the Graded gappers rules); none saved = these defaults. Each stock once a day.
MORNING_DEF = {"on": True, "start": "09:35", "end": "10:30", "min_chg": 5.0, "min_rv": 1.0, "over_pdh": True, "over_orh": True,
               "orh_min": 5, "price": 5.0, "mcap_b": 0.7, "avgvol_k": 700.0, "dvol_m": 30.0, "adr": 4.0, "low52": 30.0,
               "above200": True, "above50": True, "e10_e21": True, "e21_e50": True, "e50_s200": False,
               "res_1m": False, "res_3m": False, "res_6m": False, "res_9m": False, "res_52w": False, "res_ath": False, "res_bs": False,
               "lists_only": False}
MORNING_NUM = {"min_chg": (0, 100), "min_rv": (0, 50), "price": (0, 10000), "mcap_b": (0, 5000), "avgvol_k": (0, 100000),
               "dvol_m": (0, 100000), "adr": (0, 50), "low52": (0, 1000)}     # an empty box (null) = that filter off
MORNING_BOOL = ("on", "over_pdh", "over_orh", "above200", "above50", "e10_e21", "e21_e50", "e50_s200",
                "res_1m", "res_3m", "res_6m", "res_9m", "res_52w", "res_ath", "res_bs", "lists_only")
# The resistance levels as one more filter of the two morning boxes (the user, Nov 21 2026: "you are just adding new filter
# above 1m high / 3month / 6 / 9 / 52w / ath, and i choose which one, when other filters aligns with it it fires"; "stock can
# open up above 1month high, it would have to wait to breakout of orh to trigger.. at orh both states has to be true above
# the level and orh"). Ticked: the price must be over the TOP of a ticked range (its highest high) that was overhead at the
# last close (setups/resistance.json, the evening scan: scanner/launch.py alert_levels), at the same moment as every other
# setting; a joined range ("1m/3m") counts when any of its labels is ticked. Nothing ticked = the box as before. The alert
# names the ticked level(s) it is over ("ABOVE 3M"), the other levels it cleared and the next one overhead, and the trend tag.
# "Only my lists": Launches (with the 50 EMA undercut tab and the laggards), 3-SETUPS, Start days, the Watchlist's lists
RES_KEYS = {"res_1m": "1m", "res_3m": "3m", "res_6m": "6m", "res_9m": "9m", "res_52w": "52w", "res_ath": "ath", "res_bs": "bs"}
_RES = {"lv": None, "lists": None}       # main() / fast.py fill them: {sym: levels} (None = not read), {sym: [lists]}
# the opening range the alert tests (the user, Nov 17 2026: "when i put it does 1min, if i put 2min it does 2 mins, if i put
# 5min it does 5min"; alerts/morning.json "orh_min", 5 when not saved) and the first minute it is complete
ORH_START = {1: (9, 31), 2: (9, 32), 3: (9, 33), 5: (9, 35)}     # 3: the user, Nov 18 2026
PAGE_ONLY = ("mbo", "ebdback")  # kinds shown on the portal only (no phone push): mbo, and mboback... / ebdback... (back in its box)
MORNING_FETCH = 80              # new stocks' levels (yesterday's high, the opening range) read a run, the biggest movers first
MORNING_NEWS_BUDGET = 35        # seconds a run for the alerts' news
# + Filter (the user, Nov 9 2026: "add filter to that part so I can add other filters as well, let's say above the 21-day
# high, so I can add / delete filters as I have in other parts of the portal"): extra criteria on top of the boxes, added
# and deleted on the portal, saved with the boxes in alerts/morning.json ("x": [{id, op, v}]); a stock without a value
# for one that is set is left out (as the portal's other + Filters). The 21-day high = the highest CLOSE of the last 21
# sessions (the user: "highest close", like the EP rule). Only what this job can see for any stock.
MORNING_X = {
    "hc21": ("Over the 21-day closing high", "cat", ["Over it", "Under it"]),
    "gap": ("Gap at the open %", "num", None), "chg_1w": ("1W %", "num", None), "chg_1m": ("1M %", "num", None),
    "chg_3m": ("3M %", "num", None), "off_hi52": ("% under the 52-week high", "num", None),
    "vs200": ("% vs the 200 SMA", "num", None), "vs50e": ("% vs the 50 EMA", "num", None),
    "trend": ("Trend", "cat", ["Up", "Turn up", "Reclaim", "Resting", "Negative", "—"]),
    "grank": ("Group rank", "cat", ["★ Top", "Strong", "★ Top or Strong", "Not in the top 10%"]),
    "rs": ("RS", "num", None), "themes": ("Themes", "text", None), "industry": ("Industry", "text", None),
    "sector": ("Sector", "text", None),
}
_MCTX = {"rs": {}, "gr": {}}     # RS and the group rank from tonight's launch.json (main() fills it)


def morning_x(doc):
    """the saved + Filter list, checked: unknown ids, bad operators or values are left out"""
    out = []
    for f in doc.get("x") or []:
        if not isinstance(f, dict) or f.get("id") not in MORNING_X:
            continue
        kind, opts, v, op = MORNING_X[f["id"]][1], MORNING_X[f["id"]][2], f.get("v"), f.get("op")
        if kind == "num" and op in (">=", "<=") and isinstance(v, (int, float)) and not isinstance(v, bool):
            out.append({"id": f["id"], "op": op, "v": float(v)})
        elif kind == "cat" and v in opts:
            out.append({"id": f["id"], "op": "is", "v": v})
        elif kind == "text" and op in ("has", "is", "not") and isinstance(v, str) and 0 < len(v.strip()) <= 60:
            out.append({"id": f["id"], "op": op, "v": v.strip()})
    return out[:20]


def hhmm(s, d):
    m = re.match(r"^(\d{1,2}):(\d\d)$", str(s or ""))
    return (int(m.group(1)), int(m.group(2))) if m and 0 <= int(m.group(1)) < 24 and 0 <= int(m.group(2)) < 60 else d


def load_morning(path):
    """the saved settings, checked (out of range or unreadable = the default), or the defaults"""
    try:
        doc = json.load(open(path)) if path and os.path.exists(path) else {}
    except Exception:
        doc = {}
    M = dict(MORNING_DEF)
    for k, (lo, hi) in MORNING_NUM.items():
        if k in doc:
            v = doc[k]
            if v is None:
                M[k] = None
            elif isinstance(v, (int, float)) and lo <= v <= hi:
                M[k] = float(v)
    for k in MORNING_BOOL:
        if isinstance(doc.get(k), bool):
            M[k] = doc[k]
    M["orh_min"] = doc.get("orh_min") if doc.get("orh_min") in ORH_START and not isinstance(doc.get("orh_min"), bool) else 5
    s, e = hhmm(doc.get("start"), (9, 35)), hhmm(doc.get("end"), (10, 30))
    s = max(s, ORH_START[M["orh_min"]] if M["over_orh"] else (9, 31))     # the 1- / 2- / 5-minute opening range is complete at 9:31 / 9:32 / 9:35
    e = min(max(e, s), (16, 0))
    M["start"], M["end"] = f"{s[0]:02d}:{s[1]:02d}", f"{e[0]:02d}:{e[1]:02d}"
    M["x"] = morning_x(doc)
    M["saved_at"] = doc.get("saved_at", "")
    return M


# the second morning box (the user, Nov 18 2026): the same breakout for the stocks NOT in trend ("another tab alerts for stocks
# not in trend, basically not eligible for setups i have in morning breakout alerts": PANW, CRWD, QLYS, TENB, S under their 50
# EMA that day). Its own settings, alerts/morning2.json, saved by the portal's second box; none saved = a copy of the first
# box's with the trend boxes off. A stock that passes the first box's trend boxes at the live price belongs to the first
# box and is left out here; one that already fired there does not fire here
MORNING_TREND = ("above200", "above50", "e10_e21", "e21_e50", "e50_s200")
MORNING_NAME = {"mbo": "MORNING BREAKOUT", "mbo2": "BREAKOUT, NOT IN TREND"}


def load_morning2(path, M1):
    try:
        ok = bool(path) and os.path.exists(path) and isinstance(json.load(open(path)), dict) and bool(json.load(open(path)))
    except Exception:
        ok = False
    if ok:
        return load_morning(path)
    M = dict(M1 or load_morning(None), x=list((M1 or {}).get("x") or []), saved_at="")
    for k in MORNING_TREND:
        M[k] = False
    return M


def morning_trend_ok(st, price, M):
    """True when the first box has a trend box ticked and the stock passes every ticked one at this price (a stock in
    trend: the first box's)"""
    if not any(M.get(k) for k in MORNING_TREND) or not price:
        return False
    sma = st.get("sma200")
    if M.get("above200") and sma and price <= sma:
        return False
    if M.get("above50") or M.get("e10_e21") or M.get("e21_e50") or M.get("e50_s200"):
        e = live_emas(st, price)
        if not e:
            return False
        if (M.get("above50") and price <= e[2]) or (M.get("e10_e21") and e[0] <= e[1]) or (M.get("e21_e50") and e[1] <= e[2]) \
                or (M.get("e50_s200") and sma and e[2] <= sma):
            return False
    return True


def in_morning(M, now):
    t = (now.hour, now.minute)
    return bool(M and M.get("on")) and hhmm(M["start"], (9, 35)) <= t <= hhmm(M["end"], (10, 30))


def live_emas(st, price):
    """the 10 / 21 / 50 EMA at the live price (the portal's Trend column: the last close's EMAs moved one step), or None"""
    t = st.get("tr")
    if not t or len(t) < 4 or any(x is None for x in t[:4]) or not price:
        return None
    mv = lambda e, n: e + (2 / (n + 1)) * (price - e)
    return mv(t[1], 10), mv(t[2], 21), mv(t[3], 50)


def live_trend(st, p):
    """the Trend column's label at the live price (docs/index.html trendOf, your rule Nov 3 2026), else the last close's"""
    t = st.get("tr")
    if not t or len(t) < 6 or any(x is None for x in t) or not p:
        return st.get("trend") or "—"
    e5, e10, e21, e50, _, c = t
    mv = lambda e, n: e + (2 / (n + 1)) * (p - e)
    E5, E10, E21, E50 = mv(e5, 5), mv(e10, 10), mv(e21, 21), mv(e50, 50)
    base, stack = E10 > E21 > E50 and E50 > e50, E10 > E21 > E50     # the 50 up on the day: vs the last close's (Nov 12 2026)
    lab = ("Negative" if p < E21 else "" if not base else "Reclaim" if c < e21 else "Turn up" if E5 > E10 and e5 <= e10
           else "Up" if stack and p > E50 and E10 > e10 and E21 > e21 else "Resting" if stack else "")
    return lab or "—"


def best_tier(st):
    """the best-ranked of the stock's themes and its industry group, as the portal's Group rank: Top / Strong / ''"""
    gr = _MCTX["gr"]
    c = [gr.get(("theme", t)) for t in str(st.get("themes") or "").split(" | ") if t] + [gr.get(("ind", st.get("group") or st.get("industry")))]
    c = [g for g in c if g]
    if not c:
        return ""
    b = sorted(c, key=lambda g: (-(min(g.get("pct") or 0, 89.9) if g.get("loose") else (g.get("pct") or 0)), g.get("rank") or 999))[0]
    return b.get("tier") or ""


def x_value(fid, st, q, lv=None):
    """one + Filter criterion's value for a stock at the live quote (None = no value)"""
    price, chg = q[0], q[1]
    n = lambda k: st.get(k) if isinstance(st.get(k), (int, float)) else None
    if fid == "hc21":
        return (lv or {}).get("hc21")
    if fid == "gap":
        op = q[5] if len(q) > 5 else None
        prev = price / (1 + chg / 100) if chg is not None and chg > -100 else None
        return 100 * (op / prev - 1) if op and prev else None
    if fid in ("chg_1w", "chg_1m", "chg_3m"):
        return n(fid)
    if fid == "off_hi52":
        return 100 * (1 - price / n("high_52w")) if n("high_52w") else None
    if fid == "vs200":
        return 100 * (price / n("sma200") - 1) if n("sma200") else None
    if fid == "vs50e":
        return 100 * (price / n("ema50") - 1) if n("ema50") else None
    if fid == "rs":
        return _MCTX["rs"].get(st.get("symbol"))
    if fid == "trend":
        return live_trend(st, price)
    if fid == "grank":
        return best_tier(st)
    return str(st.get(fid) or "")


def x_fails(f, st, q, lv=None):
    """'' when the stock passes this + Filter, else why not"""
    name, kind, _ = MORNING_X[f["id"]]
    v = x_value(f["id"], st, q, lv)
    if kind == "num":
        if v is None:
            return f"no {name} value"
        ok = v >= f["v"] if f["op"] == ">=" else v <= f["v"]
        return "" if ok else f"{name} {v:.1f}, not {'≥' if f['op'] == '>=' else '≤'} {f['v']:g}"
    if kind == "text":
        a, b = str(v).lower(), f["v"].lower()
        ok = a == b if f["op"] == "is" else b not in a if f["op"] == "not" else b in a
        return "" if ok else f"{name} \"{v}\" ({f['op']} \"{f['v']}\")"
    if f["id"] == "hc21":
        if v is None:
            return "no 21-day closing high"
        over = q[0] > v
        return "" if over == (f["v"] == "Over it") else f"{'under' if not over else 'over'} the 21-day closing high ${v:.2f}"
    if f["id"] == "grank":
        ok = {"★ Top": v == "Top", "Strong": v == "Strong", "★ Top or Strong": v in ("Top", "Strong")}.get(f["v"], v not in ("Top", "Strong"))
        return "" if ok else f"group rank {v or 'not in the top 10%'}"
    return "" if v == f["v"] else f"{name} {v}"


def morning_static(st, M, slack=None):
    """the criteria that don't need today's price (the liquidity and the ADR); with a slack (the fast check's candidates)
    also the price rules on the last close, with that much room for today's move"""
    n = lambda k: st.get(k) if isinstance(st.get(k), (int, float)) else None
    if M.get("mcap_b") is not None and (n("mcap_b") or -1) < M["mcap_b"]:
        return False
    if M.get("avgvol_k") is not None and (n("avg_vol_20") or n("avg_vol_30d") or -1) < M["avgvol_k"] * 1000:
        return False
    if M.get("dvol_m") is not None and n("dvol_20_m") is not None and n("dvol_20_m") < M["dvol_m"]:
        return False
    if M.get("adr") is not None and n("adr_20") is not None and n("adr_20") < M["adr"]:
        return False
    if M.get("lists_only") and _RES["lists"] is not None and st.get("symbol") not in _RES["lists"]:
        return False
    if res_ticked(M) and _RES["lv"] is not None and not ticked_levels(st.get("symbol"), M):
        return False                                        # no ticked level overhead at the last close: can't fire today
    if slack is None:
        return True
    px = n("price")                                         # the last close, with some room for today's move
    if px and res_ticked(M) and _RES["lv"] is not None and not any(x[1] <= px * (1 + slack) for x in ticked_levels(st.get("symbol"), M)):
        return False
    if px and M.get("price") is not None and px * (1 + slack) < M["price"]:
        return False
    if px and M.get("above200") and n("sma200") and px * (1 + slack) < n("sma200"):
        return False
    if px and M.get("low52") is not None and n("low_52w") and px * (1 + slack) < n("low_52w") * (1 + M["low52"] / 100):
        return False
    return True


def res_ticked(M):
    """the level labels ticked in a box"""
    return {v for k, v in RES_KEYS.items() if M and M.get(k)}


def ticked_levels(sym, M):
    """the stock's levels overhead at the last close that the box has ticked"""
    t = res_ticked(M)
    return [x for x in (_RES["lv"] or {}).get(sym) or [] if t & set(x[0].split("/"))]


def res_name(lab):
    """a level's name: "1m/3m" -> "1M/3M", "bs" -> "broken support"""
    return "broken support" if lab == "bs" else lab.upper()


def res_span(x):
    """a range's prices: one price when both ends are within 0.5%"""
    return f"${x[1]:.2f}" if abs(x[1] / x[2] - 1) < 0.005 else f"${x[2]:.2f}-{x[1]:.2f}"


def res_setup(doc):
    """_RES from the command line: --resistance <setups/resistance.json> (the levels) and the followed names (launch.json and
    --lists <setups/latest.json>) for "Only my lists"; read once a run"""
    if "--resistance" in sys.argv:
        load_res(sys.argv[sys.argv.index("--resistance") + 1])
    try:
        lists_doc = json.load(open(sys.argv[sys.argv.index("--lists") + 1])) if "--lists" in sys.argv else None
    except Exception:
        lists_doc = None
    _RES["lists"] = list_names(doc, lists_doc) if (doc.get("launches") or lists_doc) else None


def load_res(path):
    """setups/resistance.json's levels into _RES (None when it can't be read: then a ticked level can't fire)"""
    try:
        _RES["lv"] = json.load(open(path)).get("levels") or {}
    except Exception as e:
        _RES["lv"] = None
        print(f"no resistance levels: {e!r}", file=sys.stderr)


def live_trend_tag(st, price):
    """the Watchlist's trend tag at the live price (docs/index.html trendTag): FULL TREND / NEW TREND / CAUTION / NO TREND"""
    t, e = st.get("tr"), live_emas(st, price)
    if not e or not t or len(t) < 4 or t[3] is None:
        return ""
    E10, E21, E50 = e
    s200 = st.get("sma200")
    stack = E10 > E21 > E50
    full = stack and s200 and E50 > s200 and E50 > t[3]
    return "FULL TREND" if full and price > E21 else "NEW TREND" if price > E21 and price > E50 else "CAUTION" if stack else "NO TREND"


def morning_why_not(st, q, M):
    """'' when the live quote passes every criterion but the levels (yesterday's high, the opening range), else the first
    one it fails (the replay names it)"""
    if not q or len(q) < 5 or not q[0] or q[1] is None:
        return "no live price"
    price, chg, rv = q[0], q[1], q[4]
    if M.get("min_chg") is not None and chg < M["min_chg"]:
        return f"up {chg:.1f}%, under {M['min_chg']:g}%"
    if M.get("min_rv") is not None and (rv is None or rv < M["min_rv"]):
        return f"Rel vol {rv if rv is not None else '—'}x, under {M['min_rv']:g}x"
    if M.get("price") is not None and price < M["price"]:
        return f"price ${price:.2f}, under ${M['price']:g}"
    if not morning_static(st, M):
        return "liquidity / ADR"
    sma, lo = st.get("sma200"), st.get("low_52w")
    if M.get("low52") is not None and lo and price < lo * (1 + M["low52"] / 100):
        return f"under {M['low52']:g}% over its 52-week low"
    if M.get("above200") and sma and price <= sma:
        return f"under the 200 SMA ${sma:.2f}"
    if M.get("above50") or M.get("e10_e21") or M.get("e21_e50") or M.get("e50_s200"):
        e = live_emas(st, price)
        if not e:
            return "no trend data (a new listing)"
        e10, e21, e50 = e
        if M.get("above50") and price <= e50:
            return f"under the 50 EMA ${e50:.2f}"
        if M.get("e10_e21") and e10 <= e21:
            return "10 EMA not over the 21"
        if M.get("e21_e50") and e21 <= e50:
            return "21 EMA not over the 50"
        if M.get("e50_s200") and sma and e50 <= sma:
            return "50 EMA not over the 200 SMA"
    for f in M.get("x") or []:                             # your + Filters (the 21-day high: with the levels)
        if f["id"] != "hc21":
            why = x_fails(f, st, q)
            if why:
                return why
    return ""


def morning_levels(sym, today=None, n=5):
    """yesterday's regular-session high and today's n-minute opening range (5: 9:30-9:35, from Yahoo's 5-minute chart as
    before; 1, 2 or 3: the first 1, 2 or 3 minutes, from its 1-minute chart) and day's low so far, of the last 2 sessions:
    {pdh, orh, orl, low, pd, n} or None"""
    n = n if n in (1, 2, 3) else 5
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym.replace('/', '-').replace('.', '-'))}?range=2d&interval={'5m' if n == 5 else '1m'}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.load(r)["chart"]["result"][0]
        today = today or datetime.datetime.now(NY).date()
        qd = res["indicators"]["quote"][0]
        prev, tod = {}, []
        for t, hi, lo in zip(res.get("timestamp") or [], qd.get("high") or [], qd.get("low") or []):
            d = datetime.datetime.fromtimestamp(t, NY)
            if not hi or not lo or not ((9, 30) <= (d.hour, d.minute) < (16, 0)):
                continue
            if d.date() == today:
                tod.append((d, hi, lo))
            elif d.date() < today:
                prev.setdefault(d.date(), []).append(hi)
        if not prev or not tod or (tod[0][0].hour, tod[0][0].minute) != (9, 30):
            return None
        pd = max(prev)
        rng = tod[:1] if n == 5 else [x for x in tod if (x[0].hour, x[0].minute) < (9, 30 + n)]
        return {"pdh": round(max(prev[pd]), 4), "orh": round(max(x[1] for x in rng), 4), "orl": round(min(x[2] for x in rng), 4),
                "low": round(min(x[2] for x in tod), 4), "pd": pd.isoformat(), "n": n}
    except Exception:
        return None


def close_high_21(sym, today=None):
    """the highest close of the last 21 sessions before today, from Yahoo's daily chart, or None"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym.replace('/', '-').replace('.', '-'))}?range=3mo&interval=1d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.load(r)["chart"]["result"][0]
        today = today or datetime.datetime.now(NY).date()
        cl = [c for t, c in zip(res.get("timestamp") or [], res["indicators"]["quote"][0].get("close") or [])
              if c and datetime.datetime.fromtimestamp(t, NY).date() < today]
        return round(max(cl[-21:]), 4) if len(cl) >= 5 else None
    except Exception:
        return None


def find_morning(live, S, M, now):
    """[(key, title, msg, prio, tv, sym, q)] the stocks whose live quote passes the criteria now (the levels come next)"""
    if not in_morning(M, now):
        return []
    out = []
    for sym, q in (live.get("rows") or {}).items():
        st = S.get(sym)
        if not st or morning_why_not(st, q, M):
            continue
        out.append(sym)
    return sorted(out, key=lambda s: -(live["rows"][s][1] or 0))


def morning_alert(sym, st, q, lv, M, kind="mbo"):
    """(title, msg) of one morning breakout, or None when the levels aren't broken"""
    price, chg, rv = q[0], q[1], q[4]
    if M.get("over_pdh") and not (lv and lv.get("pdh") and price > lv["pdh"]):
        return None
    if M.get("over_orh") and not (lv and lv.get("orh") and price > lv["orh"]):
        return None
    if any(f["id"] == "hc21" and x_fails(f, st, q, lv) for f in M.get("x") or []):
        return None
    all_lv = (_RES["lv"] or {}).get(sym) or []
    hits = [x for x in ticked_levels(sym, M) if price > x[1]]
    if res_ticked(M) and not hits:                      # a level ticked: over the top of one of them, now, or no alert
        return None
    adr = st.get("adr_20") or 0
    over = [f"yesterday's high ${lv['pdh']:.2f}"] if M.get("over_pdh") and lv else []
    over += [f"the {M.get('orh_min') or 5}-min opening range high ${lv['orh']:.2f}"] if M.get("over_orh") and lv else []
    msg = f"${price:.2f} · {chg:+.1f}% · vol {rv:.1f}x for the time of day" + (f" · over {' and '.join(over)}" if over else "")
    if lv and lv.get("low"):
        risk = 100 * (price / lv["low"] - 1)
        msg += f" · stop under the day's low ${lv['low']:.2f}: risk {risk:.1f}%" + (f" = {risk / adr:.1f} ADR" if adr else "")
    sma = st.get("sma200")
    msg += (f" · ADR {adr:.1f}%" if adr else "") + (f" · {100 * (price / sma - 1):+.0f}% vs the 200 SMA" if sma else "")
    e = live_emas(st, price)
    if e:
        stack = "10 > 21 > 50 EMA" if e[0] > e[1] > e[2] else "10 / 21 / 50 EMA not stacked"
        msg += f" · {stack}"
    th = [t for t in str(st.get("themes") or "").split(" | ") if t]
    if th or st.get("group"):
        msg += " · theme " + (th[0] if th else st.get("group"))
    tag = live_trend_tag(st, price)
    lv_msg = ""
    if hits:
        lv_msg += " · above its " + " and ".join(f"{res_name(x[0])} {res_span(x)}" for x in hits)
    other = [x for x in all_lv if price > x[1] and x not in hits]
    if other:
        lv_msg += " · also cleared " + ", ".join(f"{res_name(x[0])} {res_span(x)}" for x in other)
    nxt = [x for x in all_lv if price <= x[1]]
    if nxt:
        x = min(nxt, key=lambda y: y[2])
        lv_msg += f" · next: {res_name(x[0])} {res_span(x)}, " + (f"+{100 * (x[2] / price - 1):.1f}%" if price < x[2] else "in it now")
    parts = msg.split(" · ")                            # the price, the % and the volume first, then the levels and the tag
    msg = " · ".join(parts[:3]) + lv_msg + (f" · {tag}" if tag else "") + "".join(" · " + p_ for p_ in parts[3:])
    above = " · ABOVE " + " + ".join(res_name(x[0]).upper() for x in hits) if hits else ""
    return f"{sym} {MORNING_NAME[kind]} {chg:+.1f}%{above}", msg


def morning_holding(state, M, live, S, now, kind="mbo"):
    """today's morning breakouts that still meet the user's settings (the user, Nov 17 2026: the box "was supposed to be in
    true state, meaning when it gets out it takes out of box, when it gets back in it just alerts that its back in"; TSCO
    that day: alerted 9:45 at $38.72 over $38.58 and $38.38, at 11:20 $38.29 and still in the box). Holding = every
    criterion of the box the user chose ("whatever i choose in that filters"): % up, Rel vol, the levels, the price and
    trend rules, the + Filters; not the time window. state lost / back, as update_holding keeps them for the other boxes
    (the portal moves a lost one to Heads-ups and back). A stock back on gets one alert (key SYM:mbobackHHMM, portal
    only), at most one a stock a day and only inside the box's time window (Nov 23 2026). A stock without a live row, a stocks row or its kept levels in
    this run stays as it was. Returns the back-on alerts [(key, title, msg, 'high', tv)]"""
    lost, back, lvs = state.setdefault("lost", {}), state.setdefault("back", {}), state.get(f"{kind}_lv") or {}
    last, t, out, seen = state.setdefault(f"{kind}_back", {}), f"{now:%H:%M}", [], set()
    for it in state.get("items", []):
        key = it.get("key", "")
        if not key.endswith(f":{kind}") or key.startswith("mbatch") or key in seen:
            continue
        seen.add(key)
        sym = key.split(":")[0]
        q, st, lv = (live.get("rows") or {}).get(sym), S.get(sym), lvs.get(sym)
        if not q or not q[0] or q[1] is None or not st or not lv:
            continue
        a = None if morning_why_not(st, q, M) else morning_alert(sym, st, q, lv, M, kind)
        px = round(q[0], 2)
        if a and key in lost:
            back[key] = {"at": t, "price": px}
            del lost[key]
            # one BACK ON a stock a day, and only inside the box's own time window (the user, Nov 23 2026, after 286 BACK ON
            # repeats that day, TTAN 9 times, THC at 4:05 PM: "stop the morning's boxes back on after the boxes end time
            # ... at most one back on per stock per day in their time frame"); out of the window it still moves in and out
            # of the box silently
            if sym not in last and in_morning(M, now):
                last[sym] = t
                out.append((f"{sym}:{kind}back{now:%H%M}", f"{sym} {MORNING_NAME[kind]}{',' if kind == 'mbo2' else ''} BACK ON {q[1]:+.1f}%",
                            f"meets your {'morning breakout' if kind == 'mbo' else 'not-in-trend breakout'} settings again (first alert {it.get('time', '')}) · " + a[1],
                            "high", st.get("tv_symbol") or sym))
        elif not a and key not in lost:
            lost[key] = {"at": t, "price": px}
    return out


def news_words(x):
    """the alert's news line from codegrade.stock_news"""
    if not x:
        return ""
    if not x.get("checked"):
        return " · news: not checked in time (the Pre-market tab's News column has the 5%+ gappers)"
    if x.get("weak"):
        return " · news: nothing of its own today or the last 2 sessions (" + str(x.get("catalyst") or "") + ")"
    return " · news: " + str(x.get("catalyst") or "") + ": " + str(x.get("reason") or "")[:260] + (f" · 📰 {x['url']}" if x.get("url") else "")


def check_morning(cands, state, M, live, S, E, now, sent, kind="mbo"):
    """the candidates whose levels are broken: [(key, title, msg, 'high', tv)], each stock once a day; the levels are
    read once a day per stock (a minute after the opening range closes it is final: 9:36 for the 5-minute one, 9:32 / 9:33
    for the 1- / 2-minute ones) and kept in alerts.json (mbo_lv); levels kept for another range (the setting changed
    during the morning) are read again; a stock that fires gets its day's low read again (the stop)"""
    import concurrent.futures
    n = M.get("orh_min") or 5
    state[f"{kind}_lv"] = lvs = {k: v for k, v in (state.get(f"{kind}_lv") or {}).items() if (v.get("n") or 5) == n}
    todo = [s for s in cands if f"{s}:{kind}" not in sent]
    before = set(lvs)                                       # levels read at an earlier check (their day's low is old)
    hc = any(f["id"] == "hc21" for f in M.get("x") or [])     # the 21-day closing high only when a + Filter needs it
    need = [s for s in todo if s not in lvs or (hc and "hc21" not in lvs[s])][:MORNING_FETCH]

    def lev(s_):
        lv_ = dict(lvs[s_]) if s_ in lvs else morning_levels(s_, now.date(), n)
        if lv_ and hc and "hc21" not in lv_:
            lv_["hc21"] = close_high_21(s_, now.date())
        return lv_
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        got = dict(zip(need, ex.map(lev, need)))
    final = (now.hour, now.minute) >= (9, 31 + n)
    fired, recheck = [], []
    for sym in todo:
        lv = got.get(sym) or lvs.get(sym)
        if got.get(sym) and final:
            lvs[sym] = got[sym]
        q = live["rows"][sym]
        a = morning_alert(sym, S[sym], q, lv, M, kind)
        if a:
            (recheck if sym in before else fired).append((sym, a, lv))
        elif lv:
            print(f"{sym}:{kind}: ${q[0]:.2f} not over yesterday's high {lv.get('pdh')} / the opening range high {lv.get('orh')}"
                  + (f" / a ticked level {[x[1] for x in ticked_levels(sym, M)]}" if res_ticked(M) else "") + " yet")
    if recheck:                                         # levels from an earlier check: the day's low now
        with concurrent.futures.ThreadPoolExecutor(8) as ex:
            fresh = dict(zip([r[0] for r in recheck], ex.map(lambda s_: morning_levels(s_, now.date(), n), [r[0] for r in recheck])))
        for sym, a, lv in recheck:
            if fresh.get(sym):
                lv = dict(lv, low=fresh[sym]["low"])     # (the 21-day closing high and the levels as they were)
                a = morning_alert(sym, S[sym], live["rows"][sym], lv, M, kind) or a
            fired.append((sym, a, lv))
    for sym, _, lv in fired:                            # the levels at the alert stay with it (the box's true state reads them:
        if lv and sym not in lvs:                       # a stock that fired in the range's first minute had none kept)
            lvs[sym] = lv
    if not fired:
        return []
    try:
        import codegrade
        NWS = codegrade.stock_news([f[0] for f in fired], S, E, now, budget=MORNING_NEWS_BUDGET)
    except Exception as ex:
        print("morning news:", repr(ex)[:160], file=sys.stderr)
        NWS = {}
    out = []
    for sym, (title, msg), lv in fired:
        out.append((f"{sym}:{kind}", title, msg + news_words(NWS.get(sym)), "high", S[sym].get("tv_symbol") or sym))
    return out


def event_reasons(path, today):
    """({sym: reason}, {theme: reason}) of the bellwether events whose reaction session is today (radar-data events.json)"""
    try:
        doc_ = json.load(open(path))
        if not doc_.get("alert_reasons"):          # the switch (radar/bellwethers.json "alert_reasons"): off = the Event card only
            return {}, {}
        evs = doc_.get("events") or []
    except Exception as e:
        print(f"no events file: {e}", file=sys.stderr)
        return {}, {}
    by_sym, by_theme = {}, {}
    for e in evs:
        if e.get("status") == "out" and e.get("react_day") == today:
            # a stock tied to two bellwethers that report the same evening (CoreWeave: Microsoft and Meta) gets both reasons
            for k, v in (e.get("alerts") or {}).items():
                by_sym[k] = (by_sym[k] + " | also: " + v[:700]) if k in by_sym else v
            for k, v in (e.get("themes") or {}).items():
                by_theme[k] = (by_theme[k] + " | also: " + v[:700]) if k in by_theme else v
    return by_sym, by_theme


# ───────── EP pullbacks (the user, Nov 23 2026) ─────────
EPP = {"rows": {}, "rules": {}}    # setups/ep_pullback.json (the evening scan); main() fills it (--epp)
EPP_FETCH_PCT = 5.0                # a name's 1-minute chart is read when its price is within this % over its EMA level, or once READY
EPP_MAX_FETCH = 40                 # charts read a run


def chart_bars_today(sym):
    """today's 1-minute bars from 9:30 on, from Yahoo's chart: [(minute after 9:30, open, high, low, close, volume)], or []"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym.replace('/', '-').replace('.', '-'))}?range=1d&interval=1m"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.load(r)["chart"]["result"][0]
        q = res["indicators"]["quote"][0]
        today, out = datetime.datetime.now(NY).date(), []
        for t, o, h, l, c, v in zip(res.get("timestamp") or [], q.get("open") or [], q.get("high") or [], q.get("low") or [],
                                    q.get("close") or [], q.get("volume") or []):
            if None in (o, h, l, c):
                continue
            d = datetime.datetime.fromtimestamp(t, NY)
            m = d.hour * 60 + d.minute - 570
            if d.date() == today and 0 <= m < 390:
                out.append((m, o, h, l, c, v or 0))
        return out
    except Exception:
        return []


def find_epp(live, now, sent, state, bars_of=None, fast=False):
    """EP PULLBACK READY / BUY (radar/epp.py has the rule): the names of tonight's setups/ep_pullback.json with a play waiting
    (status "wait"), read on today's 1-minute chart once the price is within EPP_FETCH_PCT % over the EMA level. A BUY is
    found again every run while the price holds over its stop, so it stays in its box (update_holding). The 1-minute check
    (fast) only reads the names already READY: a new READY comes from the 5-minute run"""
    out, rows = [], EPP.get("rows") or {}
    bars_of = bars_of or chart_bars_today
    nowm = now.hour * 60 + now.minute - 570
    if not rows or nowm < 1:
        return out
    first = (EPP.get("rules") or {}).get("first_sale_pct", 10)
    memo = state.setdefault("epp", {})
    charts, fetched = {}, 0
    for sym, r in rows.items():
        q = live["rows"].get(sym)
        if not q or not q[0]:
            continue
        price, tvs = q[0], r.get("tv") or sym
        for play in ("10", "21"):
            p = r.get("p" + play) or {}
            if p.get("status") != "wait":
                continue
            kr, kb = f"{sym}:epr{play}", f"{sym}:epb{play}"
            if kb in sent:                                  # bought today: in its box while over its stop
                b = memo.get(kb)
                if b and price > b["stop"]:
                    out.append((kb, b["title"], b["msg"], "high", tvs))
                continue
            if memo.get(f"{sym}:off{play}") or (kr not in sent and (fast or price > p["level"] * (1 + EPP_FETCH_PCT / 100))):
                continue
            if sym not in charts:
                if fetched >= EPP_MAX_FETCH:
                    continue
                charts[sym], fetched = bars_of(sym), fetched + 1
            if not charts[sym]:
                continue
            lv, c0, l0 = p["level"], r["c0"], r["l0"]
            res = epp.check(charts[sym], play, lv, c0, l0, floor=p.get("floor") if play == "10" else None, now_min=nowm)
            if res["off"]:
                memo[f"{sym}:off{play}"] = True
                print(f"{sym}: EP pullback {play} EMA off (under the EP day's low {l0})")
                continue
            if res["buy"]:
                end, px, stop, vw, start = res["buy"]
                risk = 100 * (px / stop - 1)
                adr = _ADR.get(sym) or r.get("adr")
                title = f"{sym} EP PULLBACK BUY - {play} EMA ${px:.2f}"
                msg = (f"the {epp.hhmm(start)}-{epp.hhmm(end)} candle closed ${px:.2f} over the {play} EMA ${lv:.2f} and VWAP ${vw:.2f}"
                       f" · stop ${stop:.2f}, today's low: risk {risk:.1f}%" + (f" = {risk / adr:.1f} ADR" if adr else "")
                       + f" · first sale ${px * (1 + first / 100):.2f} (+{first:g}%), then breakeven, the rest on a daily close under the 21 EMA"
                       + f" · EP {r['ep']} (close ${c0:.2f}, low ${l0:.2f}), {r.get('days')} sessions ago · ready at {epp.hhmm(res['ready'][0])}")
                memo[kb] = {"stop": stop, "entry": px, "title": title, "msg": msg}
                out.append((kb, title, msg, "high", tvs))
            elif res["ready"] and kr not in sent:
                t0, low0 = res["ready"]
                how = (f"traded under the EP day's close ${c0:.2f}" if play == "10" else f"still over the EP day's low ${l0:.2f}")
                need = (f"not under ${p['floor']:.2f}" if play == "10" else f"while today's low stays over ${l0:.2f}")
                out.append((kr, f"{sym} EP PULLBACK READY - {play} EMA",
                            f"touched the {play} EMA ${lv:.2f} by {epp.hhmm(t0)} and {how} (EP {r['ep']}, {r.get('days')} sessions ago)"
                            f" · now ${price:.2f}, VWAP ${res['vwap']:.2f} · the buy: a 15-minute candle closing over ${lv:.2f} and VWAP, {need}"
                            f" · stop: today's low, now ${res['low']:.2f}", "default", tvs))
    return out


# ───────── parabolic shorts (the user, Nov 28 2026) ─────────
PARA = {"date": None, "rows": {}, "shorts": [], "rules": {}}    # setups/parabolic.json (scanner/parabolic.py); main() fills it (--para)
PARA_MAX_FETCH = 30                # charts read a run (the list is a few names a night)


def find_para(now, sent, state, bars_of=None, early=False):
    """PARABOLIC GAP UP / SHORT / STOPPED / RE-ENTRY / COVER (radar/para.py has the rule and the study's numbers): each
    stock of last night's list is read on today's 1-minute chart every run until it is decided: no gap (off, silently), or
    armed -> the short at the break of the opening 5-minute low -> stopped -> one re-entry on a 5-minute close under VWAP.
    A SHORT / RE-ENTRY is found again every run while its stop is not traded, so it holds in its box (update_holding).
    Before 9:35 (early) only the GAP UP heads-up. state["para"][SYM] keeps what happened (the portal's Now column, and the
    evening file's shorts). The open shorts of the last session: COVER at the close from 3:45 PM, or STOPPED once today's
    high reaches the stop"""
    out, rows = [], PARA.get("rows") or {}
    bars_of = bars_of or chart_bars_today
    nowm = now.hour * 60 + now.minute - 570
    today = now.date().isoformat()
    if nowm < 1 or not PARA.get("date") or PARA["date"] >= today:      # the list has to be of an earlier close
        return out
    R = {**para.RULES, **(PARA.get("rules") or {})}
    memo = state.setdefault("para", {})
    fetched = 0
    for sym, r in rows.items():
        m = memo.setdefault(sym, {})
        if m.get("off") or m.get("done") or fetched >= PARA_MAX_FETCH:
            continue
        tvs = r.get("tv") or sym
        bars, fetched = bars_of(sym), fetched + 1
        if not bars:
            continue
        res = para.check(bars, r["close"], r.get("lo20"), now_min=nowm, rules=R)
        if res["open"] is None:
            continue
        m.update(open=round(res["open"], 4), gap=round(res["gap"], 1), run20=round(res["run20"], 0) if res["run20"] is not None else None)
        if not res["armed"]:
            if min(b[0] for b in bars) <= 1 or nowm >= 5:     # the open is known: no gap day, out for today
                m.update(off=True, why=res["why"])
                print(f"{sym}: parabolic short off today ({res['why']})")
            continue
        m["armed"] = True
        ctx = (f"+{r['gain3']:.0f}% in the last 3 sessions ({r['up_days']} up closes in a row), now +{res['run20']:.0f}% over its 20-session low close"
               f" · last close ${r['close']:.2f}, opened ${res['open']:.2f}")
        s = res["short"]
        kg = f"{sym}:parag"
        if kg not in sent and not s:
            out.append((kg, f"{sym} PARABOLIC GAP UP {res['gap']:+.1f}% - short watch",
                        f"gapped up {res['gap']:+.1f}% after {ctx} · the short: the first trade under the opening {R['range_min']}-minute candle's low"
                        + (f" ${res['orl']:.2f}" if res["orl"] else " (known at 9:35)") + ", stop the day's high"
                        + (f" (now ${res['hod']:.2f})" if res["hod"] else "") + " · cover at the next session's close · check the borrow first", "default", tvs))
        if early:
            continue
        if not s:
            if nowm >= R["last_entry_min"]:
                m["done"] = True                              # no short today
            continue
        ks, kx, kr, kx2 = f"{sym}:paras", f"{sym}:parax", f"{sym}:parar", f"{sym}:parax2"
        if "short" not in m:
            risk = 100 * (s["stop"] / s["px"] - 1)
            m["short"] = {"time": para.hhmm(s["min"]), "px": round(s["px"], 4), "stop": round(s["stop"], 4), "orl": round(s["orl"], 4),
                          "title": f"{sym} PARABOLIC SHORT - opening low broken ${s['px']:.2f}",
                          "msg": f"traded under the opening {R['range_min']}-minute low ${s['orl']:.2f} at {para.hhmm(s['min'])}: short ${s['px']:.2f}"
                                 f" · stop ${s['stop']:.2f}, the day's high: risk {risk:.1f}% · cover at the next session's close"
                                 f" (one re-entry if stopped: a 5-minute close back under VWAP) · gap {res['gap']:+.1f}% after {ctx}"}
        if res["stopped"] is None:
            out.append((ks, m["short"]["title"], m["short"]["msg"], "high", tvs))
            continue
        m["stopped"] = para.hhmm(res["stopped"])
        e = res["re"]
        if kx not in sent and not e:
            out.append((kx, f"{sym} PARABOLIC SHORT STOPPED ${s['stop']:.2f}",
                        f"the {m['short']['time']} short ${s['px']:.2f} was stopped at {m['stopped']}: the day's high ${s['stop']:.2f} was traded"
                        + (" (it came and went between two checks: no SHORT alert was sent)" if ks not in sent else "")
                        + (f" · one re-entry: the next 5-minute candle closing under VWAP (now ${res['vwap']:.2f}) after one closed over it, stop the day's new high"
                           if R.get("reentry") and nowm < R["last_entry_min"] else ""), "default", tvs))
        if not e:
            if nowm >= R["last_entry_min"] or not R.get("reentry"):
                m["done"] = True
            continue
        if "re" not in m:
            risk = 100 * (e["stop"] / e["px"] - 1)
            m["re"] = {"time": para.hhmm(e["min"]), "px": round(e["px"], 4), "stop": round(e["stop"], 4),
                       "title": f"{sym} PARABOLIC SHORT RE-ENTRY - lost VWAP ${e['px']:.2f}",
                       "msg": f"the 5-minute candle to {para.hhmm(e['min'])} closed ${e['px']:.2f} under VWAP ${e['vwap']:.2f} after one over it: short again"
                              f" · stop ${e['stop']:.2f}, the day's high: risk {risk:.1f}% · cover at the next session's close"
                              f" · the first short ({m['short']['time']}, ${s['px']:.2f}) was stopped at {m['stopped']} · gap {res['gap']:+.1f}% after {ctx}"}
        if res["stopped2"] is None:
            out.append((kr, m["re"]["title"], m["re"]["msg"], "high", tvs))
            continue
        m["stopped2"], m["done"] = para.hhmm(res["stopped2"]), True
        if kx2 not in sent:
            out.append((kx2, f"{sym} PARABOLIC RE-ENTRY STOPPED ${e['stop']:.2f}",
                        f"the {m['re']['time']} re-entry ${e['px']:.2f} was stopped at {m['stopped2']} (the day's high ${e['stop']:.2f})"
                        + (" (it came and went between two checks: no RE-ENTRY alert was sent)" if kr not in sent else "") + " · no more shorts in it today", "default", tvs))
    # the open shorts of the last session (the evening file followed them): cover at the close, or stopped today
    for x in PARA.get("shorts") or []:
        if x.get("status") != "open" or x.get("date") != PARA.get("date") or fetched >= PARA_MAX_FETCH:
            continue
        sym, tvs = x["symbol"], x.get("tv") or x["symbol"]
        tag = "re" if x.get("kind") == "re-entry" else "s"
        mk, kc, k1 = f"{sym}:open:{tag}", f"{sym}:parac" + ("" if tag == "s" else "2"), f"{sym}:parax1" + ("" if tag == "s" else "r")
        m = memo.setdefault(mk, {})
        if m.get("stopped"):
            continue
        if nowm < 375 and now.minute % 5:                    # every 5 minutes is enough until 3:45 PM
            continue
        bars, fetched = bars_of(sym), fetched + 1
        done = [b for b in bars if b[0] < nowm]
        if not done:
            continue
        hi, last = max(b[2] for b in done), done[-1][4]
        what = f"the {x['date']} {x.get('time') or ''} short ${x['entry']:.2f} ({x.get('kind')})"
        if hi >= x["stop"]:
            m["stopped"] = para.hhmm(next(b[0] for b in done if b[2] >= x["stop"]))
            out.append((k1, f"{sym} PARABOLIC SHORT STOPPED ${x['stop']:.2f} (day 2)",
                        f"{what}: its stop ${x['stop']:.2f} was traded at {m['stopped']} today · out", "default", tvs))
        elif nowm >= 375:
            pct = 100 * (x["entry"] - last) / x["entry"]
            out.append((kc, f"{sym} PARABOLIC SHORT - COVER at the close ${last:.2f}",
                        f"{what}: the cover is today's close · now ${last:.2f}, {pct:+.1f}% on the short · stop ${x['stop']:.2f} not traded (today's high ${hi:.2f})", "high", tvs))
    return out


# ───────── the earnings breakdown: the short side (the user, Nov 28 2026) ─────────
# The gap-down study (tools/gapdown: every 5%+ gap-down of the liquid universe, Jan 2023 - Nov 2026, 1-minute bars) and the
# user's choices from it: "what strategy you see has best edge for earnings gap down... 1# break of opening range low";
# "u mean in alers tab short box? and same logic of other boxes?"; the stop "to their adr, dont you thinks its better
# judgmeent?"; "I go with your option b" = every setup alerts and the alert says the risk in ADRs.
#   the day     the stock reported since the last close (the Earnings tab's row reacting today, with its grade and reason
#               in the alert; else Yahoo's earnings time)
#               and gaps down 8%+ at the open; open $10+, market cap $700M+, 700K+ shares and $20M+ a day (the study's
#               universe). Not an earnings day, or a gap under 8%: no alert (they lost outside the market-wide days).
#   the short   the price under the low of the first 3-minute candle (9:30-9:33; a late open: the candle it opened in),
#               also when it went over that candle's high first. 970 trades: 46.7% won, +0.19R a trade, each year up.
#   the stop    the first candle's high. The alert says the candle's size (its low to its high: the study's stop distance)
#               in % and in ADRs: under 0.8 ADR is "tight" (+0.46R a trade, 284 trades), 0.8 ADR or more made about
#               nothing (+0.05R, 639 trades); and how far the stop is from the price now.
#   replayed    minute by minute as this job sees it (tools/gapdown/sim_ebd.py, the 7,197 stock-days of the study): 871
#               alerts on 369 days, none on a non-earnings day; 2 of 3 at the first check after the break, the price by
#               then a median 0.4% under the candle's low. Shorting at the ALERT's price: 49.3% won, +0.11R a trade
#               (tight 272 alerts +0.32R, wide 599 +0.01R); the study's +0.19R is a short AT the candle's low. No alert
#               for the 64 breaks that never held under the low at a check (-53R in the study) nor for the 31 already
#               back at the candle's high (-31R). tools/gapdown/test_ebd.py keeps 8 of those days as the test.
#   READY       (the user, Nov 28 2026: "yes ready"; live that evening) a heads-up as soon as that candle is complete (9:33) and
#               its low not broken yet: "SHORT UNDER $45.36", the stop, tight or wide; on the phone too, so the order can
#               wait at the candle's low (the study's entry). 1,469 READY lines in the replay (every earnings gap-down of
#               8%+; the low then breaks on 2 of 3). 326 of the 970 study trades break in the 9:33 minute itself, before a
#               READY line can help; the breaks from 9:35 on: 551 trades +0.11R at the candle's low (tight 152: +0.39R).
#               A heads-up, in 👀 (🔻 holds only the triggered shorts, the user: "in its own box meaning its triggered");
#               it leaves when the SHORT alert fires, when the break was skipped, or at 3:00 PM.
#   strong      yesterday's close over the 50 EMA and the 200 SMA: said in the alert (+0.31R vs +0.10R).
#   the box     🔻 on the Alerts tab, one alert a stock a day; in the box while the price is under that low; back over the
#               low = out (BACK ON once when under it again); the stop hit = out for the day. Out at the close.
# Any stock (stocks.json), checked every minute in the morning (radar/fast.py reads today's reporters) and every 5 minutes.
EBD_GAP = 8.0                 # the gap down at the open, %
EBD_PRICE = 10.0              # the open, $
EBD_LIQ = {"mcap_b": 0.7, "avgvol_k": 700, "dvol_m": 20.0}
EBD_MIN = 3                   # the first 3-minute candle
EBD_TIGHT = 0.8               # the stop under 0.8 ADR away = tight
EBD_SSR = 10.0                # down 10%+ on the day: the uptick rule (a short only fills on an uptick)
EBD_FROM, EBD_TO = (9, 33), (15, 0)       # no first alert from 3:00 PM (the box still follows the ones it holds)
EBD_FETCH = 40                # 1-minute charts read a run
EBD_RECHECK = 5               # a READY stock at its candle's high: its chart is read again at most every 5 minutes
EBD_NAME = "EARNINGS BREAKDOWN"


def ebd_reacts(r, today, last_day):
    """is today the session that reacts to this Earnings-tab row's report? Its reaction day when the tab set one (a report
    after the close: the next session); else a report before today's open, or after the last session's close"""
    if r.get("react_day"):
        return r["react_day"] == today
    return (r.get("when") == "bmo" and r.get("date") == today) or (r.get("when") == "amc" and r.get("date") == last_day)


def ebd_rows(path):
    """{symbol: row} of the Earnings tab (earnings.json), every row: a morning report can be minutes old, not graded yet"""
    try:
        return {r["sym"]: r for r in json.load(open(path)).get("rows", []) if r.get("sym")}
    except Exception:
        return {}


def ebd_earnings(sym, q, E, today, last_day, after_close, now_ts):
    """the words of today's earnings reaction, or None: the Earnings tab's grade and reason when its row reacts today
    ("Bearish: revenue miss -3.8%, EPS miss -11.0%"; not graded yet: "reports today"), else Yahoo's earnings time between
    the last close and now (the EP alert's test: a stock the Earnings tab doesn't list, ADR under 3% or $20-30M a day)"""
    r = (E or {}).get(sym)
    if r and ebd_reacts(r, today, last_day):
        if not r.get("read"):
            return "reports today, not graded yet"
        why = ", ".join(x for x in str(r.get("why") or "").split(", ") if "after hours" not in x and "pre-market" not in x)
        return (str(r["read"]) + (f": {why}" if why else ""))[:140]
    ern = q[6] if len(q) > 6 else None
    return "reported since the last close" if ern and after_close <= ern <= now_ts + 3600 else None


def ebd_strong(st):
    """yesterday's close over the 50 EMA and the 200 SMA (the study's "strong yesterday"): True / False, None without them"""
    c, e50, s200 = st.get("price"), st.get("ema50"), st.get("sma200")
    if not all(isinstance(x, (int, float)) and x for x in (c, e50, s200)):
        return None
    return c > e50 and c > s200


def find_ebd(live, S, E, doc, now):
    """{symbol: the earnings words} of today's earnings gap-downs of 8%+ in the liquid universe (the levels come next)"""
    if not (EBD_FROM <= (now.hour, now.minute) < EBD_TO):
        return {}
    d0 = datetime.date.fromisoformat(doc["date"])
    after_close = datetime.datetime(d0.year, d0.month, d0.day, 15, 30, tzinfo=NY).timestamp()
    today, out = now.date().isoformat(), {}
    for sym, q in (live.get("rows") or {}).items():
        st = S.get(sym)
        if not st or len(q) < 6 or not q[0] or q[1] is None or not q[5] or q[5] < EBD_PRICE:
            continue
        g = gap_of(q)
        if g is None or g > -EBD_GAP or not morning_static(st, EBD_LIQ):
            continue
        why = ebd_earnings(sym, q, E, today, doc["date"], after_close, now.timestamp())
        if why:
            out[sym] = why
    return out


def ebd_levels(sym, now, bars_of=None):
    """the first 3-minute candle that traded today and what happened since, from the 1-minute chart: {orh, orl, start (its
    first minute after 9:30), broke (the minute the price first went under its low, or None), stopped (the minute it went
    back to its high after that, or None), hi (the day's high so far), final (read a minute or more after the candle
    closed: Yahoo's last minute can still be filling), full (the chart holds the candle's last minute or a later one)};
    None before the candle is complete or without a chart"""
    bars = sorted((bars_of or chart_bars_today)(sym))
    if not bars:
        return None
    start = bars[0][0] // EBD_MIN * EBD_MIN
    nowm = (now.hour * 60 + now.minute) - 570
    if nowm < start + EBD_MIN:
        return None
    rng = [b for b in bars if b[0] < start + EBD_MIN]
    orh, orl = max(b[2] for b in rng), min(b[3] for b in rng)
    if not orl or orh <= orl:
        return None
    broke = stopped = None
    for b in bars:
        if b[0] < start + EBD_MIN:
            continue
        if broke is None:
            if b[3] < orl:
                broke = b[0]
        elif b[2] >= orh:
            stopped = b[0]
            break
    return {"orh": round(orh, 4), "orl": round(orl, 4), "start": start, "broke": broke, "stopped": stopped,
            "hi": round(max(b[2] for b in bars), 4), "final": nowm >= start + EBD_MIN + 1,
            "full": bars[-1][0] >= start + EBD_MIN - 1}


def ebd_words(st, lv):
    """(tight, the candle's size in words, the strong-yesterday words, the candle's name): shared by the READY line and
    the alert. Tight / wide is the candle's own size (its low to its high, the study's stop distance) in ADRs"""
    adr = st.get("adr_20") or 0
    size = 100 * (lv["orh"] / lv["orl"] - 1)
    sadr = size / adr if adr else None
    tight = sadr is not None and sadr < EBD_TIGHT
    cw = (f"the candle is {size:.1f}% = {sadr:.1f} ADR: " + (f"TIGHT (under {EBD_TIGHT:g} ADR: where the short paid)" if tight
                                                           else f"wide ({EBD_TIGHT:g} ADR or more made about nothing)")) if sadr is not None \
        else f"the candle is {size:.1f}%"
    strong = ebd_strong(st)
    sw = (" · strong yesterday (over its 50 EMA and 200 SMA): the better ones" if strong
          else " · not strong yesterday (under its 50 EMA or 200 SMA)" if strong is False else "")
    t0 = 570 + lv.get("start", 0)
    candle = f"{EBD_MIN}-minute candle" if not lv.get("start") else f"{EBD_MIN}-minute candle ({t0 // 60}:{t0 % 60:02d}, a late open)"
    return tight, cw, sw, candle


def ebd_ready(sym, st, q, lv, why, fixed=False):
    """(title, msg) of the READY line, a heads-up before the break (the user, Nov 28 2026: "yes ready"): the first
    3-minute candle is complete and its low not broken yet, so the order can wait at that low (the study's entry).
    fixed: the same line again when the candle read a minute later differs (Yahoo's last minute was still filling)"""
    price, chg = q[0], q[1]
    adr, gap = st.get("adr_20") or 0, gap_of(q)
    tight, cw, sw, candle = ebd_words(st, lv)
    prev = price / (1 + chg / 100) if chg is not None and chg > -100 else None
    at_low = 100 * (lv["orl"] / prev - 1) if prev else None
    msg = (f"${price:.2f} · {chg:+.1f}% · gap {gap:+.1f}% on earnings ({why}) · its first {candle}: ${lv['orl']:.2f} to ${lv['orh']:.2f}"
           + f" · SHORT UNDER ${lv['orl']:.2f} · stop ${lv['orh']:.2f} (that candle's high) · " + cw + sw
           + (f" · ADR {adr:.1f}%" if adr else "")
           + (f" · at that low it is down {-at_low:.1f}%: the uptick rule will be on, a short only fills on an uptick"
              if at_low is not None and at_low <= -EBD_SSR else "")
           + " · the SHORT alert comes when the low breaks · out at the close")
    return (f"{sym} {EBD_NAME} READY" + (" (levels corrected)" if fixed else "") + f" {chg:+.1f}% · SHORT UNDER ${lv['orl']:.2f}"
            + (" · TIGHT STOP" if tight else "")), msg


def ebd_alert(sym, st, q, lv, why):
    """(title, msg) of one earnings breakdown, or None while the price is not under the first candle's low. Tight / wide
    is the candle's own size, the same all day; the stop's distance from the price now is said next to it (an alert a
    minute after the break is already further from the stop)"""
    price, chg, rv = q[0], q[1], q[4] if len(q) > 4 else None
    if not (lv and lv.get("orl") and lv.get("orh") and price < lv["orl"]):
        return None
    adr, gap = st.get("adr_20") or 0, gap_of(q)
    risk = 100 * (lv["orh"] / price - 1)
    tight, cw, sw, candle = ebd_words(st, lv)
    msg = (f"${price:.2f} · {chg:+.1f}% · gap {gap:+.1f}% on earnings ({why}) · short under the low of its first {candle} ${lv['orl']:.2f}"
           + f" · stop: that candle's high ${lv['orh']:.2f} · " + cw
           + f" · from the price now the stop is {risk:.1f}% away" + (f" ({risk / adr:.1f} ADR)" if adr else "") + sw
           + (f" · vol {rv:.1f}x for the time of day" if rv is not None else "")
           + (f" · ADR {adr:.1f}%" if adr else "")
           + (f" · down {EBD_SSR:g}%+: the uptick rule is on, a short only fills on an uptick" if chg <= -EBD_SSR else "")
           + " · out at the close")
    return f"{sym} {EBD_NAME} {chg:+.1f}% · SHORT" + (" · TIGHT STOP" if tight else ""), msg


def check_ebd(cands, state, live, S, now, sent, bars_of=None):
    """today's earnings gap-downs: the READY line when the first 3-minute candle is complete and its low not broken yet,
    then the alert when the price is under that low: [(key, title, msg, prio, tv)], each once a stock a day (SYM:ebdr,
    SYM:ebd). The candle is read once a stock, a minute after it closed (kept in alerts.json ebd_lv; a read in its
    closing minute is used, for the READY line too, and read again: READY (levels corrected), SYM:ebdr2, when it
    differs); a stock about to fire has its chart read again: one that already went back to the candle's high after
    breaking the low (between two checks) is not alerted (the study's trade was stopped; ebd_skip says so).
    A READY line leaves its box (alerts.json lost, with why) when the alert fires, when the break was skipped (also seen
    on the chart when the price is at the candle's high: read at most every EBD_RECHECK minutes), or when corrected"""
    import concurrent.futures
    lvs, skip = state.setdefault("ebd_lv", {}), state.setdefault("ebd_skip", {})
    ready, lost = state.setdefault("ebd_ready", {}), state.setdefault("lost", {})
    t, nowm = f"{now:%H:%M}", now.hour * 60 + now.minute - 570
    todo = [s for s in cands if f"{s}:ebd" not in sent and s not in skip]
    need = [s for s in todo if not (lvs.get(s) or {}).get("final")][:EBD_FETCH]
    if need:
        with concurrent.futures.ThreadPoolExecutor(8) as ex:
            for s_, lv_ in zip(need, ex.map(lambda x: ebd_levels(x, now, bars_of), need)):
                if lv_:
                    lvs[s_] = lv_

    def close_ready(sym, why_, px):
        for k in (f"{sym}:ebdr", f"{sym}:ebdr2"):
            if k in sent and k not in lost:
                lost[k] = {"at": t, "price": px, "why": why_}

    def skipped(sym, lv, px):
        t_ = 570 + lv["stopped"]
        skip[sym] = f"broke its first candle's low and went back to its high by {t_ // 60}:{t_ % 60:02d}, before a check saw it"
        print(f"{sym}:ebd: {skip[sym]}, not sent")
        close_ready(sym, "skip", px)
    out = []
    for sym in todo:
        lv, q = lvs.get(sym), live["rows"][sym]
        if not lv:
            continue
        px, tv = round(q[0], 2), S[sym].get("tv_symbol") or sym
        if q[0] < lv["orl"]:
            fresh = ebd_levels(sym, now, bars_of)             # the chart now: was the stop already hit after the break?
            if fresh:
                lvs[sym] = lv = fresh
            if lv.get("stopped") is not None:
                skipped(sym, lv, px)
                continue
            a = ebd_alert(sym, S[sym], q, lv, cands[sym])
            if a:
                state.setdefault("ebd_why", {})[sym] = cands[sym]        # the earnings words, for its BACK ON alert
                close_ready(sym, "fired", px)
                out.append((f"{sym}:ebd", a[0], a[1], "high", tv))
            continue
        rd = ready.get(sym)
        if rd is None:
            if lv.get("broke") is None and lv.get("full"):   # the candle is complete, its low not broken yet: READY
                title, msg = ebd_ready(sym, S[sym], q, lv, cands[sym])
                ready[sym] = {"orl": lv["orl"], "orh": lv["orh"], "at": t}
                out.append((f"{sym}:ebdr", title, msg, "default", tv))
        elif lv.get("final") and "fixed" not in rd and (abs(lv["orl"] / rd["orl"] - 1) > 0.0005 or abs(lv["orh"] / rd["orh"] - 1) > 0.0005):
            rd.update(orl=lv["orl"], orh=lv["orh"], fixed=t)  # the READY line's candle was read while still filling
            if lv.get("broke") is None:
                title, msg = ebd_ready(sym, S[sym], q, lv, cands[sym], fixed=True)
                lost[f"{sym}:ebdr"] = {"at": t, "price": px, "why": "corrected"}
                out.append((f"{sym}:ebdr2", title, msg, "default", tv))
        elif q[0] >= lv["orh"] and nowm - rd.get("chk", -99) >= EBD_RECHECK:
            rd["chk"] = nowm                                  # at the candle's high: did it break the low first, unseen?
            fresh = ebd_levels(sym, now, bars_of)
            if fresh and fresh.get("stopped") is not None:
                lvs[sym] = fresh
                skipped(sym, fresh, px)
    return out


def ebd_holding(state, live, S, now, bars_of=None):
    """today's earnings breakdowns in their box: under the first candle's low = holding; back over it = lost (out of the
    box) and back when under it again (one BACK ON a stock a day, the portal only); at the candle's high = the stop, out
    for the day (lost with why "stop", kept in ebd_stopped). The stop is the price at a check, and the 1-minute chart
    when a touch between two checks is possible: before a stock comes back into the box, and when the quote's day high
    (from 9:45; Yahoo's is yesterday's in the first minutes) is a new one at or over the stop. A stock without a live
    row in this run stays as it was. Returns the back-on alerts [(key, title, msg, 'high', tv)]"""
    lost, back, lvs = state.setdefault("lost", {}), state.setdefault("back", {}), state.get("ebd_lv") or {}
    stopped, last = state.setdefault("ebd_stopped", {}), state.setdefault("ebd_back", {})
    t, out, seen = f"{now:%H:%M}", [], set()
    for it in state.get("items", []):
        key = it.get("key", "")
        if not key.endswith(":ebd") or key in seen:
            continue
        seen.add(key)
        sym = key.split(":")[0]
        q, lv, st = (live.get("rows") or {}).get(sym), lvs.get(sym), S.get(sym) or {}
        if not q or not q[0] or not lv or key in stopped:
            continue
        px, hi = round(q[0], 2), q[7] if len(q) > 7 else None
        under, stop = q[0] < lv["orl"], {"at": t, "price": px} if q[0] >= lv["orh"] else None
        new_high = hi and (now.hour, now.minute) >= (9, 45) and hi >= lv["orh"] and hi > (lv.get("hi") or 0)
        if not stop and ((under and key in lost) or new_high):
            fresh = ebd_levels(sym, now, bars_of)
            if fresh:
                lv["hi"] = max(fresh["hi"], hi or 0, lv.get("hi") or 0)
                if fresh.get("stopped") is not None:
                    t_ = 570 + fresh["stopped"]
                    stop = {"at": f"{t_ // 60:02d}:{t_ % 60:02d}", "price": round(lv["orh"], 2)}
        if stop:
            stopped[key] = stop
            lost[key] = dict(stop, why="stop")
            back.pop(key, None)
        elif not under:
            if key not in lost:
                lost[key] = {"at": t, "price": px, "why": "low"}
        elif key in lost:
            back[key] = {"at": t, "price": px}
            del lost[key]
            if sym not in last:
                last[sym] = t
                a = ebd_alert(sym, st, q, lv, (state.get("ebd_why") or {}).get(sym) or "reported") if st else None
                if a:
                    out.append((f"{sym}:ebdback{now:%H%M}", f"{sym} {EBD_NAME} BACK ON" + (f" {q[1]:+.1f}%" if q[1] is not None else ""),
                                f"under its first {EBD_MIN}-minute candle's low again (first alert {it.get('time', '')}) · " + a[1],
                                "high", st.get("tv_symbol") or sym))
    return out


def ebd_run(live, launch_p, doc, state, now, sent, S_all, E_all, bars_of=None):
    """the earnings breakdowns of one check: (the new alerts, the back-on alerts). The stocks file is the morning boxes'
    when they read it this run, else read here; the Earnings tab's rows are read here, the not yet graded ones too
    (--earnings; without it E_all, a test's rows)"""
    if (now.hour, now.minute) < EBD_FROM:
        return [], []
    if (now.hour, now.minute) >= EBD_TO:                 # no first alert from 3:00 PM: the READY lines still open leave the box
        lost_ = state.setdefault("lost", {})
        for sym in state.get("ebd_ready") or {}:
            for k in (f"{sym}:ebdr", f"{sym}:ebdr2"):
                if k in sent and k not in lost_:
                    lost_[k] = {"at": f"{now:%H:%M}", "price": None, "why": "late"}
    S = S_all
    if not S:
        for name in ("base_stocks.json", "stocks.json"):
            p = os.path.join(os.path.dirname(os.path.abspath(launch_p)), name)
            if os.path.exists(p):
                S = {s["symbol"]: s for s in json.load(open(p))}
                break
    E = ebd_rows(sys.argv[sys.argv.index("--earnings") + 1]) if "--earnings" in sys.argv else (E_all or {})
    if not S:
        return [], []
    new = check_ebd(find_ebd(live, S, E, doc, now), state, live, S, now, sent, bars_of)
    return new, ebd_holding(state, live, S, now, bars_of)


def send(topic, title, msg, prio, tvs, tags="chart_with_upwards_trend"):
    req = urllib.request.Request(f"https://ntfy.sh/{topic}", data=msg.encode(), method="POST", headers={
        "Title": title.encode("ascii", "replace").decode(), "Priority": prio, "Tags": tags,
        "Click": "https://www.tradingview.com/chart/?symbol=" + urllib.request.quote(tvs)})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status


def main():
    live_p, launch_p, state_p = sys.argv[1:4]
    fast = "--fast" in sys.argv                          # the 1-minute check (radar/fast.py)
    now = datetime.datetime.now(NY)
    live, doc = json.load(open(live_p)), json.load(open(launch_p))
    # this morning's A/B-graded gap-ups (the pre-market grading): company news a laggard launch can come on
    if "--premarket" in sys.argv:
        try:
            pm = json.load(open(sys.argv[sys.argv.index("--premarket") + 1]))
            doc["_news_today"] = {r["symbol"]: r["grade"] + ": " + (r.get("catalyst") or "") for r in pm
                                  if r.get("scan_date") == now.date().isoformat() and r.get("grade") in ("A", "B") and r.get("direction") == "up"}
        except Exception as e:
            print(f"no pre-market grades: {e}", file=sys.stderr)
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
    if "--epp" in sys.argv:                              # tonight's EP pullbacks (setups/ep_pullback.json)
        try:
            d_ = json.load(open(sys.argv[sys.argv.index("--epp") + 1]))
            EPP.update(rows=d_.get("rows") or {}, rules=d_.get("rules") or {})
        except Exception as e:
            print(f"no EP pullbacks: {e!r}", file=sys.stderr)
    if "--para" in sys.argv:                             # last night's parabolic shorts list (setups/parabolic.json)
        try:
            d_ = json.load(open(sys.argv[sys.argv.index("--para") + 1]))
            PARA.update(date=d_.get("date"), rows=d_.get("rows") or {}, shorts=d_.get("shorts") or [], rules=d_.get("rules") or {})
        except Exception as e:
            print(f"no parabolic shorts list: {e!r}", file=sys.stderr)
    _EP_ORH.clear()
    _EP_ORH.update(state.get("ep_orh") or {})      # today's 3-minute opening range highs read so far (EP / power day)
    low52_of(launch_p)                  # the stocks file: 52-week lows, 200 SMAs and each stock's groups (3-SETUPS tiers)
    # the morning breakouts (any stock; the user's settings, alerts/morning.json): the stocks whose live quote passes now
    M = load_morning(sys.argv[sys.argv.index("--morning") + 1]) if "--morning" in sys.argv else None
    M2 = load_morning2(sys.argv[sys.argv.index("--morning2") + 1] if "--morning2" in sys.argv else None, M) if M else None
    res_setup(doc)                                       # the levels (setups/resistance.json) and the followed names, for the boxes
    mb_cands, mb2_cands, S_all, E_all = [], [], {}, {}
    # (from each box's own From time, 9:31 at the earliest, in the 1-minute check: the 9:35 rule below is for the other alerts.
    # The user, Nov 18 2026: "if i choose 932 or 933 meaning 3 orh breakout it should sound around 934 or 935... its every
    # 1min"; until then the box took a 9:31-9:33 start and the job still held the morning breakouts to 9:35)
    if M and ((M.get("on") and in_morning(M, now)) or (M2.get("on") and in_morning(M2, now))
                            or any(k.endswith((":mbo", ":mbo2")) for k in sent)):
        for name in ("base_stocks.json", "stocks.json"):
            p = os.path.join(os.path.dirname(os.path.abspath(launch_p)), name)
            if os.path.exists(p):
                S_all = {s["symbol"]: s for s in json.load(open(p))}
                break
        if "--earnings" in sys.argv:
            try:
                E_all = {r["sym"]: r for r in json.load(open(sys.argv[sys.argv.index("--earnings") + 1])).get("rows", []) if r.get("reported")}
            except Exception:
                E_all = {}
        gr_ = (doc.get("group_rank") or {})
        _MCTX["rs"] = gr_.get("rs") or {}
        _MCTX["gr"] = {(g.get("kind"), g.get("group")): g for g in gr_.get("rows") or []}
        mb_cands = find_morning(live, S_all, M, now) if M.get("on") else []
        # the second box: the stocks not in trend (they fail a trend box the first box has ticked) that didn't fire there
        mb2_cands = [s_ for s_ in (find_morning(live, S_all, M2, now) if M2.get("on") else [])
                     if f"{s_}:mbo" not in sent and not morning_trend_ok(S_all[s_], live["rows"][s_][0], M)]
    found = (find_early(live, doc, now) if early else find(live, doc, now)) + find_gob(live, doc, now)
    if early:                                           # + the followed names the watch list leaves out (Launches, the Watchlist's lists)
        try:
            lists_doc = json.load(open(sys.argv[sys.argv.index("--lists") + 1])) if "--lists" in sys.argv else None
            found += find_early_lists(live, doc, lists_doc, {a[0].split(":")[0] for a in found})
        except Exception as e:
            print(f"early heads-ups of the lists: {e!r}", file=sys.stderr)
    if not early:
        try:
            found += find_start(live, doc, now, sent)
            found += find_range(live, doc, now, sent)
        except Exception as e:
            print(f"start-day alerts: {e}", file=sys.stderr)
        try:
            found += find_epp(live, now, sent, state, fast=fast)
        except Exception as e:                          # never at the cost of the other alerts
            print(f"EP pullback alerts: {e!r}", file=sys.stderr)
    try:                                                # parabolic shorts: the GAP UP heads-up from 9:31, the rest from 9:35
        found += find_para(now, sent, state, early=early)
    except Exception as e:                              # never at the cost of the other alerts
        print(f"parabolic short alerts: {e!r}", file=sys.stderr)
    # your rule for every alert (Nov 3 2026): the price at least 30% over the 52-week low, checked when it fires
    found = [a for a in found if over_low52(a[0].split(":")[0], live, low52_of(launch_p))]
    # 3-SETUPS triggers only over the 200 SMA (the user, Nov 3 2026: ECHO's base top 100.90 under its 200 SMA 106.63)
    low52_of(launch_p)
    s3syms = {x["symbol"] for x in s3_rows(doc)}
    found = [a for a in found if not (a[0].endswith(":s3") or a[0].split(":")[0] in s3syms) or over_sma200(a[0].split(":")[0], live)
             or a[0].split(":")[-1][:3] in ("epr", "epb") or a[0].split(":")[-1].startswith("para")]     # an EP pullback / a parabolic short keeps its own rules
    gbars = {}
    cat_before = {k.split(":")[0] for k in sent if k.endswith(":catalyst")}
    cat_now = {a[0].split(":")[0] for a in found if a[0].endswith(":catalyst") and a[0] not in sent}
    new, quiet = [], []
    for a in found:
        key, sym = a[0], a[0].split(":")[0]
        if key in sent or (key.endswith(":launch") and sym + ":power" in sent):
            continue
        # one alert per move: an EP covers the stock's later catalyst gap / A launch; a power day covers its EP
        if ((key.endswith(":launch") or key.endswith(":catalyst") or key.endswith(":laggard")) and (sym + ":ep" in sent or sym + ":power" in sent)) \
                or (key.endswith(":ep") and sym + ":power" in sent):
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
    # the cap on pushes comes AFTER today's 1-minute chart checks (below), so only alerts that passed them take a slot
    # (Nov 3 2026: 28 alerts at 3:46 PM, 6 of the first 8 failed their check and RPD's 21 EMA retest was folded unchecked)
    new += quiet
    # one heads-up for one pullback (the user, Nov 6 2026: MANE at 9:35 got "at its 21 EMA in the base" and "pulling back to
    # its breakout level" as two messages; "if it happens at the same time, one message"): when both come for a stock in
    # the same run, one message names both levels; the 21 EMA one counts as sent (a later run doesn't send it alone)
    zone_syms = {a_[0].split(":")[0] for a_ in new if a_[0].endswith(":zone") and a_[1] is not None}
    for a_ in [a_ for a_ in new if a_[0].endswith(":ema21zone") and a_[1] is not None and a_[0].split(":")[0] in zone_syms]:
        sym_ = a_[0].split(":")[0]
        k_ = next(i_ for i_, b_ in enumerate(new) if b_[0] == f"{sym_}:zone")
        key_, title_, msg_, prio_, tvs_ = new[k_]
        lv_ = re.search(r"level (\$[\d,.]+(?:-\$[\d,.]+)?)", msg_)
        e21_ = re.search(r"at the 21 EMA (\$[\d,.]+)", a_[2])
        new[k_] = (key_, f"{sym_} retesting its breakout level {lv_.group(1) if lv_ else ''} and its 21 EMA {e21_.group(1) if e21_ else ''}".replace("  ", " "),
                   msg_ + (f" · also at its 21 EMA {e21_.group(1)} (the last close's): the 21 EMA retest setup, its buy the close back over it,"
                           " in the upper half of the day" if e21_ else ""), prio_, tvs_)
        new.remove(a_)
        state["sent"].append(a_[0])
    passed = []
    for key, title, msg, prio, tvs in new:
        if title is not None and key.endswith((":gapbase", ":gob1", ":gob5", ":gob950", ":gob2x")):
            # gap out of base: the opening ranges from today's 1-minute chart; the 9:50 check only after a gap alert
            sym_ = key.split(":")[0]
            if key.endswith(":gob950"):
                # only for a gap alerted before 9:50
                if not any(it.get("key") == f"{sym_}:{k_}" and it.get("time", "99:99") < "09:50"
                           for it in state.get("items", []) for k_ in ("gapbase", "gob1", "gob5")):
                    continue
            elif key.endswith(":gob2x"):
                # the volume reached 2x: only for a gap already alerted today, at an earlier check
                gi_ = [it for it in state.get("items", []) for k_ in ("gapbase", "gob1", "gob5") if it.get("key") == f"{sym_}:{k_}"]
                if not gi_ or any(float(v_) >= 2 for it in gi_ for v_ in re.findall(r"vol (\d+(?:\.\d+)?)x", it.get("msg", ""))):
                    continue                            # no gap alert yet, or one that already said 2x+
            else:
                if sym_ not in gbars:
                    gbars[sym_] = gob_bars(sym_)
                r_ = row_of(doc, sym_)
                adr_ = r_.get("adr_pct") or 5.0
                q_ = live["rows"].get(sym_)
                if key.endswith(":gapbase"):
                    one = gob_range(gbars[sym_], 1)
                    if one:
                        msg += f" · the 1-min range ${one[1]:.2f}-${one[0]:.2f}"
                else:
                    n_ = 1 if key.endswith(":gob1") else 5
                    rg = gob_range(gbars[sym_], n_)
                    if not (rg and rg[2] and q_ and q_[0] > rg[1]):
                        print(f"{key}: the {n_}-min high not broken yet ({rg}), not sent")
                        continue
                    risk = 100 * (rg[0] / rg[1] - 1)
                    msg = (f"${q_[0]:.2f} over the {n_}-minute opening range high ${rg[0]:.2f} · stop ${rg[1]:.2f}, its low: risk {risk:.1f}%"
                           f" = {risk / adr_:.1f} ADR" + (" (over your 0.7 ADR)" if risk / adr_ > 0.7 else "") + " · " + msg
                           + (" · out at 9:50 if the volume pace isn't 1x" if (now.hour, now.minute) < (9, 50) else ""))
        if title is not None and key.endswith(":retest"):
            # today's low (1-minute chart) came into the zone, after a real pullback; with the EMA, the low at it
            sym_ = key.split(":")[0]
            r_ = row_of(doc, sym_)
            lo_ = chart_low_today(sym_)
            # the pullback's new low (undercut and reclaim), or any low in the zone while it tests the level with every close
            # since the first touch over the 21 EMA (ACN Oct 7 2026)
            z_ = r_.get("retest_zone") or [0, 0]
            need_ = min(r_.get("retest_need_low") or 0, 1e9 if r_.get("retest_testing") else (r_.get("retest_low") or 1e9))
            if not (lo_ and z_[0] <= lo_ <= min(z_[1], need_)):       # in the zone, the pullback's new low (undercut and reclaim)
                print(f"{key}: today's low {lo_} not in the zone {z_} as a new pullback low (under {need_}), not sent")
                continue
            msg += f" · today's low ${lo_:.2f}"
        if title is not None and key.endswith(":retest"):
            # and over the 10 EMA, unless today's low tested the 21 EMA (ARM Mar 30 2026 closed under its 10 EMA with the
            # 21 EMA far under: no retest; Apr 7 down under the 21 EMA and back: the retest + 21 EMA)
            r_ = row_of(doc, key.split(":")[0])
            q_, lo_ = live["rows"].get(key.split(":")[0]), chart_low_today(key.split(":")[0])
            e10_, e21_, adr_ = r_.get("ema10") or 0, r_.get("ema21") or 0, r_.get("adr_pct") or 5.0
            if not (q_ and (q_[0] > e10_ or (lo_ and lo_ <= e21_ * (1 + adr_ / 400)))):
                print(f"{key}: under the 10 EMA {e10_} without a 21 EMA test (low {lo_}), not sent")
                continue
        if title is not None and key.endswith(":ema21"):
            # today's low under the 21 EMA and under the open, the price in the upper half of today's range
            r_ = row_of(doc, key.split(":")[0])
            q_, lo_, hi_ = live["rows"].get(key.split(":")[0]), chart_low_today(key.split(":")[0]), chart_high_today(key.split(":")[0])
            e21_ = r_.get("ema21") or 0
            op_ = q_[5] if q_ and len(q_) > 5 else None
            if not (q_ and lo_ and hi_ and op_ and lo_ < e21_ and lo_ < op_ and q_[0] - lo_ >= 0.5 * (hi_ - lo_)):
                print(f"{key}: today's low {lo_} / high {hi_} / open {op_}: no undercut and reclaim of the 21 EMA {e21_} yet, not sent")
                continue
            msg += f" · today's low ${lo_:.2f} under it"
        if title is not None and key.endswith(":ema50"):
            # today's low under the 50 EMA and under the open, the price in the upper half of today's range
            r_ = next((x for x in doc.get("ema50_undercut", []) if x["symbol"] == key.split(":")[0]), {})
            q_, lo_, hi_ = live["rows"].get(key.split(":")[0]), chart_low_today(key.split(":")[0]), chart_high_today(key.split(":")[0])
            e50_ = r_.get("ema50") or 0
            op_ = q_[5] if q_ and len(q_) > 5 else None
            if not (q_ and lo_ and hi_ and op_ and lo_ < e50_ and lo_ < op_ and q_[0] - lo_ >= 0.5 * (hi_ - lo_)):
                print(f"{key}: today's low {lo_} / high {hi_} / open {op_}: no undercut and reclaim of the 50 EMA {e50_} yet, not sent")
                continue
            msg += f" · today's low ${lo_:.2f} under it"
        if title is not None and key.endswith(":reversal"):
            # in the top half of today's range (today's 1-minute chart: the quote's day low can be missing or yesterday's)
            q_, lo_, hi_ = live["rows"].get(key.split(":")[0]), chart_low_today(key.split(":")[0]), chart_high_today(key.split(":")[0])
            if not (q_ and lo_ and hi_ and q_[0] - lo_ >= 0.5 * (hi_ - lo_)):
                print(f"{key}: today's low {lo_} / high {hi_}: not in the top half of the day yet, not sent")
                continue
            msg += f" · today's range ${lo_:.2f}-${hi_:.2f}"
        if title is not None and key.endswith(":touch"):
            # only when today's 1-minute chart shows the trade over the buy point (the quote's day high can be yesterday's)
            r_ = row_of(doc, key.split(":")[0])
            ch = chart_high_today(key.split(":")[0])
            if not (ch and r_.get("buy_point") and ch > r_["buy_point"]):
                print(f"{key}: not confirmed by today's chart (high {ch}), not sent")
                continue
        if title is not None and key.endswith((":ep", ":power")) and key.split(":")[0] in _EP_NEED_ORH:
            # it opened under its 21-day closing high (the user, Nov 21 2026, KD Nov 4 2026: opened 14.91 under 15.20): the
            # alert goes out when the price is over the 3-minute opening range high as well as over that level
            sym_ = key.split(":")[0]
            q_ = live["rows"].get(sym_)
            ok_, orh_ = ep_orh_ok(sym_, q_[0] if q_ else None)
            if not ok_:
                print(f"{key}: opened under its 21-day closing high {_EP_NEED_ORH[sym_]}, the {EP_ORH_MIN}-minute opening range high {orh_} not broken yet, not sent")
                continue
            msg += f" · and over its {EP_ORH_MIN}-minute opening range high ${orh_:.2f}"
        if title is not None and key.endswith((":catalyst", ":basebreak", ":pop", ":push")):
            # your entry: over the first 5 minutes' high, or a retest of it
            orh, q = opening_range_high(key.split(":")[0]), live["rows"].get(key.split(":")[0])
            if orh and q:
                msg += f" · 5-min opening range high ${orh:.2f}: " + (f"{100 * (q[0] / orh - 1):.1f}% above it" if q[0] > orh else "not cleared yet")
        if title is not None and key.endswith(":ema21") and "RETEST" in title:
            # your read (RPD Nov 3 2026): the 21 EMA retest alone is no strong buy; holding over the breakout level too, with
            # today's low within 1 ADR over it, is two confluences: it says so and counts as a trigger
            r_ = row_of(doc, key.split(":")[0])
            q_, lo_ = live["rows"].get(key.split(":")[0]), chart_low_today(key.split(":")[0])
            if confluence_level(r_, q_[0] if q_ else None, lo_):
                lvl_ = confluence_level(r_, q_[0], lo_)
                title = title.replace("RETEST holding", f"RETEST + BREAKOUT LEVEL ${lvl_:.2f} holding")
                msg += f" · also holding over its breakout level ${lvl_:.2f} (broken {r_.get('last_breakout_date')}): 2 confluences"
                key = key + "bl"
        if title is None:
            state["sent"].append(key)
            continue
        passed.append((key, title, msg, prio, tvs))
    # the morning breakouts: the levels (yesterday's high, the 1- / 2- / 5-minute opening range) and the news, then their own
    # alerts, apart from the caps and the group moves below (they don't take the other alerts' places)
    mb = []
    if mb_cands:
        try:
            mb = check_morning(mb_cands, state, M, live, S_all, E_all, now, sent)
        except Exception as e:                      # never at the cost of the other alerts
            print(f"morning breakouts: {e!r}", file=sys.stderr)
    mb2 = []
    if mb2_cands:
        try:
            mb2 = check_morning([s_ for s_ in mb2_cands if s_ not in {a[0].split(":")[0] for a in mb}], state, M2, live, S_all, E_all, now, sent, "mbo2")
        except Exception as e:
            print(f"breakouts not in trend: {e!r}", file=sys.stderr)
    # which of today's morning breakouts still meet the settings (the portal's box holds only those), and the ones back on
    mbk = []
    for M_, kind_ in ((M, "mbo"), (M2, "mbo2")):
        if M_ and M_.get("on") and S_all:
            try:
                mbk += morning_holding(state, M_, live, S_all, now, kind_)
            except Exception as e:
                print(f"morning breakouts holding ({kind_}): {e!r}", file=sys.stderr)
    # the earnings breakdowns, the short side (the user, Nov 28 2026): their own alerts, apart from the caps and the group moves
    ebd, ebk = [], []
    try:
        ebd, ebk = ebd_run(live, launch_p, doc, state, now, sent, S_all, E_all)
    except Exception as e:                          # never at the cost of the other alerts
        print(f"earnings breakdowns: {e!r}", file=sys.stderr)
    # triggers (the buys) always get their own alert, up to MAX_TRIGGERS a run; the heads-ups fill what is left of
    # MAX_PER_RUN and the rest are grouped into one alert that still names each one, its kind and price. Every alert's
    # full text is saved in alerts.json either way, so the portal's log shows each one (grouped ones without a pop-up)
    # one alert per move: a stock whose breakout-level retest holds doesn't also get its 21 EMA retest
    rt = {a[0].split(":")[0] for a in passed if a[0].endswith(":retest")}
    for a in [a for a in passed if a[0].split(":")[0] in rt and a[0].endswith((":ema21", ":ema21bl"))]:
        passed.remove(a)
        state["sent"] += [a[0]] + ([a[0][:-2]] if a[0].endswith("bl") else [])
    trig = [a for a in passed if is_trigger(a[0], a[1])]
    heads = [a for a in passed if not is_trigger(a[0], a[1])]
    solo = trig[:MAX_TRIGGERS] + heads[:max(0, MAX_PER_RUN - len(trig[:MAX_TRIGGERS]))]
    grouped = trig[MAX_TRIGGERS:] + heads[max(0, MAX_PER_RUN - len(trig[:MAX_TRIGGERS])):]
    if len(grouped) == 1:
        solo, grouped = solo + grouped, []
    out_ = [(a, False) for a in solo] + [(a, True) for a in grouped]
    # group moves: each alert of a stock whose theme / group has 2+ stocks alerting today says so, and the group gets its
    # own alert once a day (a trigger: own push, a loud pop-up on the desktop)
    low52_of(launch_p)
    gm = group_moves(doc, state, solo + grouped, now)
    if gm:
        tagged = []
        for (key, title, msg, prio, tvs), g_ in out_:
            sym = key.split(":")[0]
            mine = [g for g in gm if any(x[0] == sym for x in gm[g])]
            for g in mine:
                others = ", ".join(f"{x[0]} {x[1]} {x[2]}" for x in gm[g] if x[0] != sym)
                msg += f" · {g.upper()} MOVE: also {others}"
            tagged.append(((key, title, msg, prio, tvs), g_))
        out_ = tagged
        for g, lst in gm.items():
            gk = f"grp:{g}"
            if gk in state["sent"] or f"{now:%H:%M}" < GROUP_FROM:      # sent from 9:40: a group made at 9:35 alerts at 9:40
                continue
            out_.append(((gk, f"GROUP MOVE: {group_label(doc, g)}: " + ", ".join(x[0] for x in lst),
                          " · ".join(f"{x[0]} {x[1]} {x[2]}" for x in lst) + f" · {len(lst)} stocks of {g} alerting today",
                          "high", ""), False))
    # a theme moving up (the user, Nov 18 2026): 3+ stocks of one theme with a morning breakout today, from either box
    if (mb or mb2) and S_all:
        try:
            d_ = os.path.dirname(os.path.abspath(launch_p))
            tp_ = next((os.path.join(d_, n) for n in ("base_themes.json", "themes.json") if os.path.exists(os.path.join(d_, n))), None)
            mem_ = theme_members(json.load(open(tp_)) if tp_ else [], list(S_all.values()), THEME_FIT)
            out_ += [(a, False) for a in theme_breakouts(state, mb + mb2, mem_, live, now, doc)]
        except Exception as e:                      # never at the cost of the other alerts
            print(f"theme moving up: {e!r}", file=sys.stderr)
    if grouped:
        names = " · ".join(short(a) for a in grouped)
        out_.append(((f"summary:{now:%H%M}", f"{len(grouped)} more heads-ups (in the portal's alert log)", names, "default", ""), False))
    # one alert when one fires, one batch when several fire in the same check (the user, Nov 9 2026): each stock still has
    # its own line in the log (grouped: no pop-up of its own); the batch names them all
    if len(mb) == 1:
        out_.append((mb[0], False))
    elif mb:
        out_ += [(a, True) for a in mb]
        out_.append(((f"mbatch{now:%H%M}:mbo", f"MORNING BREAKOUTS ({len(mb)}): " + ", ".join(a[0].split(":")[0] for a in mb),
                      " · ".join(a[1].replace(" MORNING BREAKOUT", "") + " " + a[2].split(" · ")[0] for a in mb), "high", ""), False))
    if len(mb2) == 1:
        out_.append((mb2[0], False))
    elif mb2:
        out_ += [(a, True) for a in mb2]
        out_.append(((f"mbatch2{now:%H%M}:mbo2", f"BREAKOUTS, NOT IN TREND ({len(mb2)}): " + ", ".join(a[0].split(":")[0] for a in mb2),
                      " · ".join(a[1].replace(" BREAKOUT, NOT IN TREND", "") + " " + a[2].split(" · ")[0] for a in mb2), "high", ""), False))
    out_ += [(a, False) for a in mbk]
    out_ += [(a, False) for a in ebd + ebk]
    # the event links (radar/event.py, the user Nov 17 2026: "reason of alert has to be clear explanation"): on the session that
    # reacts to a bellwether's report, an alert on a stock with a 1st-impact link to it (radar/bellwethers.json) ends with the
    # event, the stock's tie and the bellwether's own sentence about it; a GROUP MOVE of a linked theme with the theme's
    ev_sym, ev_theme = event_reasons(sys.argv[sys.argv.index("--events") + 1], today) if "--events" in sys.argv else ({}, {})
    mctx_ = None
    for (key, title, msg, prio, tvs), is_grouped in out_:
        if key.startswith(("grp:", "thm:")):               # the move's context: who reported, what moves the other way
            try:
                if mctx_ is None:
                    mctx_ = move_context_data(launch_p, S_all, E_all)
                syms_ = [x.strip() for x in title.rsplit(": ", 1)[-1].split(",")]
                msg += move_context(key[4:], syms_, live, mctx_[0], mctx_[1], today, key.startswith("thm:"))
            except Exception as e:                          # never at the cost of the alert itself
                print(f"move context: {e!r}", file=sys.stderr)
        why_ = ev_theme.get(key[4:]) if key.startswith("grp:") else ev_sym.get(key.split(":")[0])
        if why_ and not key.startswith("summary:"):
            msg += " · why: " + why_
        line = f"{now:%H:%M} {title}: {msg}"
        it = {"key": key, "time": f"{now:%H:%M}", "title": title, "msg": msg, "tv": tvs,
              "kind": "summary" if key.startswith("summary:") else "trigger" if is_trigger(key, title) else "heads-up",
              "groups": _GROUPS.get(key.split(":")[0], [])}
        if is_grouped:
            it["grouped"] = True
        state.setdefault("items", []).append(it)
        if topic and not is_grouped and not key.split(":", 1)[-1].startswith(PAGE_ONLY):     # the morning breakouts: the portal only
            try:
                if key.endswith((":ebd", ":ebdr", ":ebdr2")) or key.split(":", 1)[-1].startswith("para"):      # the short side (the earnings breakdown, the parabolic shorts): a falling chart as its tag, plain dashes in the phone's title
                    send(topic, title.replace(" · ", " - "), msg, prio, tvs, "chart_with_downwards_trend")
                else:
                    send(topic, title, msg, prio, tvs)
            except Exception as e:
                print("alert not sent:", e, file=sys.stderr)
                state["items"].pop()
                continue
        print(line)
        state.setdefault("log", []).append(line)
        state["sent"].append(key)
        if key.endswith(":ema21bl"):
            state["sent"].append(key[:-2])
    state["sent"] = sorted(set(state["sent"]))
    # which of today's triggers still hold (from 9:35, when find() runs): the portal moves the others out of their box
    if not early:
        try:
            for key, title, msg, tvs in update_holding(state, found, live, doc, now):     # back in its box: the portal only
                state.setdefault("items", []).append({"key": key, "time": f"{now:%H:%M}", "title": title, "msg": msg, "tv": tvs,
                                                      "kind": "trigger", "groups": _GROUPS.get(key.split(":")[0], [])})
                state.setdefault("log", []).append(f"{now:%H:%M} {title}: {msg}")
                state["sent"] = sorted(set(state["sent"]) | {key})
                print(f"{now:%H:%M} {title}: {msg}")
        except Exception as e:                      # never at the cost of the alerts
            print(f"holding not updated: {e!r}", file=sys.stderr)
    state["ep_orh"] = dict(_EP_ORH)
    json.dump(state, open(state_p, "w"), indent=1)
    print(f"alerts: {len(out_)} new, {len(state['sent'])} today" + ("" if topic else " (no NTFY_TOPIC: logged, not sent)"))


if __name__ == "__main__":
    main()
