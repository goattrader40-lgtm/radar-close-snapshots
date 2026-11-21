# Handoff: how to work on the Theme & Group Radar

New session: work in this repo (goattrader40-lgtm/radar-close-snapshots) with push access. Start the session with
the repo selected; if it is missing or read-only, tell the user at once (claude.ai/connect-github, or a new session
with the repo selected) before any other work.
Keep the sessions tidy (the user, Nov 3 2026): every session for this portal carries the tag `project:radar` and a
title starting "Radar: " (e.g. "Radar: work session (Nov 4)"). At the start, set them on your own session with the
claude-code-remote tools set_session_tags and set_session_title (get_session with no id gives your session id).
Other projects live in their own repo with their own HANDOFF.md, tag and title prefix.

Read this first in every new session. It is what earlier sessions agreed with the user; the code comments carry the
same rules with the user's examples (scanner/launch.py, scanner/run.py, radar/alerts.py), and the portal legend
(docs/index.html) shows them to the user. Keep this file current: before a session ends, update it with what changed.
Older session notes and every past change, unchanged: HANDOFF_ARCHIVE.md (index at the top; search it, don't read it
all). CLAUDE.md, which Claude Code loads by itself, carries the start routine, the short commands and the ground rules.

## Session routine (the user's cheat sheet)

**Start of every session**: the user types /start (any first message works too: CLAUDE.md runs the same routine;
scheduled runs such as the 8:45 grading skip it). It does what the user used to paste:

> Repo: goattrader40-lgtm/radar-close-snapshots. Read HANDOFF.md first and follow its ground rules (no change without
> my explicit go; test branch first; replay my examples with tools/replay.py --regress; 2-year check; push to main
> only when I say "go live"). Tell me in 5 short lines what you understood, what is live now and what is open. Then
> wait for my task.

**Short commands during the session** (what each one means):

| The user says | Claude does |
|---|---|
| "explain first" | the reasoning and the dates/prices it would change, no code |
| "test it" | builds it on a test branch only, replays the examples, shows what changed |
| "2-year check" | runs radar-tools.yml `catalyst` on the test branch, reports the numbers per signal |
| "go live" | pushes to main, rebuilds Launches (picks.yml), checks the result |
| "replay TICKER from DATE to DATE" | tools/replay.py on that stock: what the portal and alerts did each day |
| "add it to the examples" | the agreed read goes into tools/examples.txt and tools/expected_reads.txt |
| "stop" | stops and waits |

**End of every session**: the user types /wrapup. It does what the user used to paste, then moves the status sections
older than the last 2 sessions into HANDOFF_ARCHIVE.md, so this file stays small:

> We're wrapping up. 1) Update HANDOFF.md with what we changed and agreed today (rules with my example dates, what is
> live, what is only on the test branch, open items). 2) If I agreed new reads, add them to tools/examples.txt and
> rewrite tools/expected_reads.txt. 3) Commit and push that (docs and tools only), and check nothing is left
> uncommitted. 4) Give me a 5-line summary: live, test only, open.

**How long a session**: one topic or one working day, whichever comes first (roughly 30–50 of the user's messages;
fewer when they are screenshot- and replay-heavy). Wrap up early when Claude Code compacts the conversation, or when
Claude starts asking again about agreed things or gets them wrong. The 8:45 AM grading has its own session: leave it
alone.

## Status at the end of the session "Radar: theme chips on Today's gainers (Nov 18)" (Wed Nov 18 ~10:55 AM ET - Sat Nov 21 2026 ~12:40 PM ET; session_01PkbDak4wNj9qyumu6CQx8R)

**In one line: seven alert changes, all live on main, nothing left on a test branch (claude/compassionate-volta-5ichnh = main): the
📊 "Breakouts, not in trend" box with its own settings, the 🔥 Theme moving up alert (3+ morning breakouts of one theme), GROUP
MOVE from 9:40 with ADR 4%+ only, the 3-minute opening range, BACK ON alerts for ⚡ and (1.5x volume) 🎯, the morning boxes from
their own From time (9:31 at the earliest), the EARLY gap heads-up for the followed names. NONE WAS SEEN ON LIVE PRICES BY THIS
SESSION (stand-in levels only; the Thu Nov 19 and Fri Nov 20 opens ran the first six, unchecked). FIRST THING NEXT SESSION: Mon Nov
23's alerts.json: `:mbo2` / `mbatch2` / `thm:` / `<kind>backHHMM` keys, `:early` keys with "gapping" in the title from 9:31, the
first `grp:` at 9:40 or later, levels.json rows with 5 values from 9:33; and ask the user how the 📊 box and the 🔥 alerts
behaved on Nov 19-20 (too many? the 📊 settings saved in alerts/morning2.json?).**

- **How it went with the user (for the next session)**: two of my mistakes cost them time. (1) "move the GROUP MOVE time to
  9:40" was built as "alerts before 9:40 don't count" and reported as "3 alerts instead of 8" before showing what was behind
  the numbers (the user: "you cant do stuff without my confirmation... all i asked you change time", "you really messed me up
  today"); the fix was a table of the 8 group alerts, the stocks behind each and what the change did to it, then their version.
  (2) the first theme alert (3 stocks up 3%+) was built before measuring: 34 alerts a day. So: show the table of what changes,
  by ticker and time, BEFORE building; a question ("do you still go live for this?", "what is this you asking me to do go
  live?") is not a go.


- **LIVE (the user's "ok go do what you gotta check adn go live", Wed Nov 18 2026 after the evening scan, commit c92c51e, branch
  claude/compassionate-volta-5ichnh merged with main): five alert changes. NONE HAS RUN ON LIVE PRICES: FIRST CHECK Thu Nov 19
  from 9:33 AM ET** (tested with stand-in levels: cloud sessions can't read Yahoo).
  Started from: all 12 Cybersecurity stocks up 5-13% on Nov 18 (TENB first at 9:53, PANW 10:00, QLYS 10:03, ...) with no
  important alert ("howcome we didnt get any important priority alert that all cybersecurity stocks moving up as a group").
  Found: the GROUP MOVE alert counts stocks that ALERTED (2+), once a day per group; Cybersecurity's was spent at 9:35 on three
  pullback heads-ups (NTSK, SAIL, RPD); PANW, CRWD, QLYS, TENB, S were under their 50 EMA, on no list, and could not alert.
  1. **📊 Breakouts, not in trend: a second morning box** (the user: "another tab alerts for stocks not in trend, basically not
     eligible for setups i have in morning breakout alerts"; "separate filters i can adjust"). radar/alerts.py: kind `mbo2`
     (keys SYM:mbo2, SYM:mbo2backHHMM, mbatch2HHMM:mbo2), its own settings alerts/morning2.json (load_morning2: none saved = the
     📈 settings with the five trend boxes off; NOT SAVED YET: the user will tighten it), its own levels (state mbo2_lv). A stock
     that passes the trend boxes ticked in the 📈 settings at the live price is left out (morning_trend_ok: "good logic like
     it"); one that fired in 📈 does not fire here. Same true state and BACK ON alert as 📈, portal only. day.py morning_args
     passes --morning2; fast.py reads its candidates each minute too. docs/index.html: the two settings boxes side by side
     (.mbo-split; MBI / MBC / withI: one code for both), the 📊 box (code n), its sound and voice ("Breakout, not in trend, P A
     N W, volume 1.3 times"). Replay of Nov 18 with the copied settings (radar-tools `morning above200=0 above50=0 e10_e21=0
     e21_e50=0`): 62 fire, 20 of them in 📈, so about 42 in 📊: **it rings a lot until the user tightens it (told them: before
     9:25 the first morning)**.
  2. **🔥 Theme moving up: 3+ morning breakouts of one theme** (from 📈 or 📊; tight members, fit 0.7+; themes and tight
     industry groups, one alert for the same stocks, the theme names it): THEME MOVING UP, key thm:<theme>, once a day per
     theme, a trigger, phone too, its own box (code t; the user: "just keep it with its own box, if i dont like then we can
     move back to morning breakouts"), sound and voice ("Theme moving up, Cybersecurity, 3 breakouts"). alerts.py
     theme_members / theme_breakouts. Nov 18 replay: PANW 9:53, CRWD 10:07, S 10:10 -> the alert at 10:10, the only theme
     that day. **Dropped after measuring**: a first version, 3 tight members up 3%+ (the user's first pick): 34 alerts a day on
     22 sessions (Oct 20 - Nov 18; 87 on Nov 9), 3 up 4%+ 23 a day, 5%+ with half the theme and themes only 3 a typical day
     but 29 on Nov 9 (the user: "i m looking for real alerts"; they then proposed the morning-breakout route). The replay tool
     (radar/probe_themeup.py, radar-tools `themeup`) was removed with it; the numbers are in the rules row.
  3. **GROUP MOVE: the alert is sent from 9:40, and only ADR 4%+ stocks count** (GROUP_FROM, GROUP_MIN_ADR; the page's own
     group tags use the ADR rule too). **My mistake, corrected with the user**: I first built "alerts before 9:40 don't count"
     (5 of the day's 8 group alerts vanished); the user: "we are only changing alert time, still if something happened
     between 930-940 it has to show". Now every alert of the day counts and a group made at 9:35 alerts at 9:40. Nov 18
     replay: 8 group alerts -> 5 (MD 3.73%, WAT 3.42%, BSY 3.20% ADR not counted). The single-stock alerts are unchanged.
  4. **3-minute opening range** (the user: "2min/3min/5min", keep 1min): ORH_START 3 = 9:33, morning_levels n=3; levels.py
     keeps a 5th value (rows [high 5, low 5, high 1, high 2, high 3], read from 9:33); the picker in both settings boxes and
     the + Filter "Above ORH" chip read 1min / 2min / 3min / 5min; probe_morning orh_min=3.
  5. **BACK ON alert for ⚡ and 🎯** (the user: "i need sounds for episodic pivots as well for back on.... and pattern
     breakouts with 1.5 volume"; "for now portal only"): a power day / EP that stopped holding and holds again gets one BACK
     ON alert; a pattern breakout (breakout, confirm, gapbase, gob1, gob5, basebreak, pop, s3) only with a volume pace of
     1.5x+; at most one every 15 minutes a stock; portal only (keys SYM:<kind>backHHMM, BACK_RE; update_holding returns
     them). 🚀 and ↩️ still come back silently; 📈 / 📊 keep their own.
  Tested: the alert job on the Nov 18 11:05 prices with stand-in levels (20 in 📈, 29 in 📊, none in both, one theme alert, no
  repeat on a second run, lost / back and the 15-minute limit, 5 of 19 returning breakouts at 1.5x+ alerted); the page on
  desktop / phone with that record (the split boxes, each box edited and reset alone, every voice line, 5 tabs, 0 page
  errors), again after the merge with main. Rules workbook: 3 new rows, 3 changed. No `--regress`, no Launches rebuild
  (launch.py untouched), no 2-year check (alerts and settings).
- **LIVE (the user's "go live", Wed Nov 18 2026 ~4:55 PM ET, commit 8ba96bf): the two morning boxes run from their own From
  time, 9:31 at the earliest** (the user: "if i choose 932 or 933 meaning 3 orh breakout it should sound around 934 or 935...
  its every 1min"). Found: main() held the morning breakouts to 9:35 with every other alert (`not early`), though the Nov 17
  change let the box take a 9:31 / 9:32 start: a 1- or 2-minute range never fired before 9:35. radar/alerts.py: that gate is
  off for the morning boxes only (the 1-minute check runs them from 9:31); and a stock that fires gets its levels kept at once
  (check_morning: before, one that fired in the range's first minute had none, so it could not leave / re-enter its box).
  Tested (stand-in levels): 📊 at 3min / From 9:33 fires at 9:33, 📈 at 9:35 / 5min at 9:35, both at 9:35 = nothing before
  9:35, out at 9:36 and back at 9:52. Told the user the Rel vol is rough before 9:35. Rules workbook: the 📈 row.
  **Not seen on live prices: check Thu Nov 19** (the user's From times decide; both boxes are saved / default at 9:35 now).
- **LIVE (the user's "go live", Sat Nov 21 2026, after a merge with main): the EARLY gap heads-up (9:31-9:34) also for the
  followed names** (the user, Nov 18: "gap heads up can you include my wl (ep + trend + start + setups) too"; "i accept your
  proposal... we are just adding correct?"). The regular one (find_early) reads launch.json `watch` (liquid stocks: $10+,
  $20M+ and 700K+ a day, ADR 3.5%+; EP and power day alerts read the same list), which drops a stock launched in the last 20
  sessions: 34 of 49 1-EP/GAP names, 38 of 94 3-SETUPS names, 13 of 44 Start days on Nov 18, all on Launches. radar/alerts.py
  find_early_lists / list_names: a name on Launches (with the 50 EMA undercut tab and the laggards), 3-SETUPS, Start days or
  a Watchlist list (setups/latest.json: 1-EP/GAP, 1-UPDAY, 2-POOL, the TREND names' sources) that is not on `watch`, gapping
  up 5%+ (EARLY_LIST_GAP) and over its open: one quiet heads-up, key SYM:early, "AZTA EARLY: gapping +5.5% (on Launches,
  3-SETUPS, 1-EP/GAP)", with its buy point cleared or not; none when the stock gets another alert in the same check (a gap
  out of base). day.py lists_args passes --lists (setups/latest.json, read once a job) to fast.py (which now also reads the
  Start days, every 3-SETUPS name and the lists' names each minute) and to the 1-minute alerts run. The 5% and the quiet
  heads-up were my defaults: the user did not answer those two. Merge: day.py conflicted with the other session's
  events_args (both kept: `*lists_args(), *events_args()`). Tested (stand-in 9:32 run): AZTA, ANET, HAWK, PRKS, SLS fire; ENR
  (under its open), CDW (3% gap) don't; TMDX gets its gap out of base instead; no repeat the next minute; the Nov 18 tests
  again on the merged code; the page on 5 tabs, 0 errors. Rules workbook: one row. **Not seen on live prices: check Mon Nov
  23 at 9:31-9:34** (alerts.json `:early` keys with "gapping" in the title; the minute read's time with the extra names).
- **Answered, no change**: the Gainers tab already has the theme buttons ("Group moves today", above the theme table; the user:
  "if thats the way i dont need it"); the gainers table updates every minute for stocks up 2%+ (9:31-11:00 since the other
  session's Nov 18 change, was 10:30), every 5 minutes for the rest.
- **Check (was for Thu Nov 19; NOT DONE by this session, still to do)**: alerts.json keys :mbo2, mbatch2, thm:, <kind>backHHMM and their box / sound on the page; the first
  GROUP MOVE at 9:40 or later; levels.json rows with 5 values from 9:33; the minute read's time with the 📊 candidates added
  (687 stocks in the replay); alerts/morning2.json on main once the user saves.
- **Open**: themes moving DOWN in their own box (the user: "lets do ups and see how it reacts, then we can do down ones"); the
  BACK ON alerts on the phone ("you can add phone as well": later); a cap or a market filter if 🔥 fires too often on rally
  days (not measured for the breakout version: only Nov 18 could be replayed).
- **Test only**: nothing.

## Status at the end of the session "Radar: MBGL / AVEX miss (Nov 12)" (Thu Nov 12 - Sat Nov 21 2026; session_01PkbDaiSjzGPJPtohD3UF2C)

Its first part (Nov 12-13: the coil on Launches, the full + Filter list, the MBGL / AVEX findings) is in the archive under the title
'Status of the session "Radar: MBGL / AVEX miss (Nov 12)"'. What came after (Nov 15 - 21):

- **LIVE (the user's "go live", Sat Nov 21 2026 ~11:30 AM ET, branch test/resrange, merge d89b0d0; Launches rebuilt 11:32 AM,
  4fcdacb): the Resistance column as ranges, the 1-month high, joined labels, broken support, and Resistance as a column to add.**
  The user (VERX): "look at last feb 3rd and nov 10th 25 all the way to that, every day was trying to break that support, finally
  that day broke down really bad ... that day is considered next big resistance for the ticker, that's why nov 5th it stalled at
  that number"; "the way i see it 18.50-18.90 range was the support"; "do as range for all"; "yes add 1month"; "if 1month and
  3month same then it has to show 1month/3month".
  1. **Every level is a range** (scanner/launch.py resistance(): [label, top, bottom, ...], lowest first): the 1-, 3-, 6-, 9-month
     and 52-week high (21 / 63 / 126 / 189 / 252 sessions) from the span's highest CLOSE (bottom) to its highest HIGH (top); a
     level counts when its top is 0.5%+ over the close and the buy point (so the 1-month high does not repeat a base-top buy
     point). Spans with the same range (both ends within 0.5%) share one entry, the labels joined ("1m/3m", "6m/9m/52w").
  2. **Broken support** (broken_support(), settings BS): the breakdown day closes under the lowest close of the 40 sessions before
     it, down 1.5+ ADRs on 1.5x+ volume; the range before it = back while the closes stay within 4 ADRs of each other, 20+
     sessions; the zone = that range's lowest close to half an ADR over it; 3+ separate tests (a low in the zone or within a
     quarter ADR over it, tests 4+ sessions apart); gone once a close is back over the zone's top; wicks under the floor that
     closed back do not move it. Entry ["bs", top, bottom, range from, range to, breakdown day, tests]. **VERX**: closes
     18.55-20.71 from Nov 3 2025 to Feb 2 2026, 5 tests; Feb 3 2026 -15.1% (4.2 ADRs) on 3.7x; zone 18.55-18.88; the highs of
     Nov 5 2026 (18.53) and Nov 16 2026 (18.57) turned back at its bottom; its buy point 18.57 sits inside the zone. An older
     VERX zone 23.87-24.24 (floor Aug 8 - Oct 28 2025, broke Oct 29 2025). **The thicknesses (half an ADR, 4 ADRs, a quarter ADR)
     are Claude's, fitted on VERX alone.**
  3. **The page** (docs/index.html resCell / resAway / resLo ...): "1M/3M $36.84-38.07 +1.6%", "Broken support $18.55-18.88
     +7.7%"; one price when the two ends are within 0.5%; the % is to the BOTTOM of the range (was to the highest high), "in it"
     when the price is inside; the cell shows the nearest level, the nearest broken support and the farthest high, the tooltip
     all of them (with the floor's dates, tests and breakdown day). A level saved before this ([label, level]) shows as one
     price, as before. **Resistance in Columns: + add** (catalog `res`, RESK: the Launches / laggards row, the 50 EMA undercut
     row, the Start days row (start_days rows now carry `resistance`), launch.json `watch_resistance` for the 888 launch-watch
     stocks, else the Watchlist row).
  Tested: `--regress` "every agreed example reads the same"; radar-tools `setupsdry` on the branch (Nov 20 close): the same 134
  launches, 12 in the 50 EMA undercut tab, 27 start days, no launch date / grade / buy point / status / read changed; broken
  support overhead on 11 of 134 Launches rows (TTD 16.79-17.20, HGV 48.31-49.14, POOL 252.28-255.77, EPAM 200.00-203.54, PRKS
  48.60-49.43, CHKP 214.03-216.49, INTA 52.76-53.47, PRMB 30.79-31.20, CRI 50.40-51.27, UPBD 28.44-28.81, VERX), 14 of 182
  Watchlist stocks, 97 of the 888 watch stocks; the page with the dry files and with the old files (0 page errors; the column
  added on the 50 EMA undercut and Start days tables). After the go live: the rebuilt launch.json identical to the evening's but
  for the levels; VERX on Launches reads "Broken support $18.55-18.88 +7.7% | 52W $20.62-20.82 +19.7%". Rules workbook: the
  Resistance row rewritten and a broken-support row. A display only: no launch rule, buy point or alert reads the levels.
  **First checks**: (1) the Watchlist rows still carry the old single prices (latest.json is written by the evening scan only):
  after the Mon Nov 23 scan, setups/latest.json `resistance` entries have 3+ elements and VERX reads the zone there too (the
  evening scan was NOT re-run by hand: it may resend the phone's Ready list); (2) Launching today with the added Resistance
  column (empty on a weekend, not tested); (3) the user was asked to check 2-3 of the 10 other zones on their charts.
- **The start day's move (Nov 15, built here)**: "up 1 ADR+, or up 4%+ that is also 0.8 ADR+" (ZETA Nov 9 2026: +4.5% on 2.2x with a
  5.39% ADR, missed 1 ADR; TTEK Oct 15 2026 +3.5% with a 2.8% ADR kept: the user's "start is 15th october"), branch
  test/start4pct 3b9d5b4. **It went live on Nov 16 through the session "Start days stay on until they fail + 0.8 ADR start (BILL,
  Nov 16)"** (see there). On Nov 21 this session twice told the user it was still waiting for a go live: wrong, corrected the
  same day. test/start4pct and test/resrange can be deleted.
- **Answered, no change** (Nov 13 - 21): FLY Nov 6 2026 was on 1-EP/GAP and 2-POOL, not on Launch laggards (closed 20.76 under its
  1-month high 20.96 by the wicks, its AST SpaceMobile news never graded: the 8:45 list had dropped it) and came on Launches as
  a first day when the chart reading went live Nov 12; the first-day rule is under the 200 SMA only (the user's WRBY Nov 5 read;
  2 years: 127 under it 32% ran 20%+ / 38% failed, 73 over it 29% / 51%); the Watchlist's "Added: all" header is a day picker,
  not a sort; "vs 200 SMA >= 0" = over the 200 SMA; VERX's highs on Nov 5 2026 (1- to 9-month 18.53 / close 17.59; 10-month
  20.40; 52-week 20.86).
- **Answered, no change (Nov 21, after the go live): TMDX's 95-97 and why broken support does not show it.** The user: "tmdx 97-95
  range isnt it new resistance that you built we did for verx?", "tdmx that range 95 held it over 23 sessions?", "is it part of
  resistance or it will throw some fake things?". TMDX held a floor 26 sessions (Mar 30 - May 5 2026: lows 93.08 Mar 30, 95.46
  Mar 31, 96.01 Apr 2, then a bounce to 120.91 Apr 17, then 97.01 Apr 29, 97.20 Apr 30, 96.63 May 4, 94.61 May 5), gapped down
  May 6 2026 (high 78.00, close 72.92, -23.2% = 4.8 ADRs on 8.1x) and every rally since stopped at 95-98 (Aug 19 94.99, Aug 21
  95.18, Nov 9 95.30, Nov 10 97.55, Nov 18 98.78 close 96.43, Nov 19 97.19). The live rule misses it (2 visits, not 3; the
  closes not within 4 ADRs: the 23% bounce). On Aug 19 the column would have read "1M/3M 93.97-94.99" and then "6M
  148.00-151.00" (not a 120 level). **The test** (2 years, liquid stocks, ADR 3.5%+; after the price first comes back up to a
  zone: rejected = a close 1.5 ADRs under it before a close 1.5 ADRs over it, within 20 sessions; vs a placebo zone of the same
  thickness 3 ADRs higher): the live floor rule 180 zones, 51% rejected vs 36% placebo; a looser floor (2 visits, a bounce
  allowed: catches TMDX) 362 zones, 48% vs 44%; a gap-down zone (the last close before a gap down) 380, 49% vs 45%; coming
  back 20+ sessions later: live rule 48% vs 37% (66 zones), looser floor 41% vs 42%, gap down 43% vs 46%. **Advised and agreed:
  no change** (the user: "so you advising no change correct?"). The VERX zone kept as a caution level (moderate confidence: a
  first, rougher test "no close over the top in 10 sessions" showed no edge; this test was run AFTER the go live). Untested
  idea, offered: count a zone only after it rejected the price once.
- **Outside the portal: a TradingView script for the user's charts** (the user: "this is pinescript, dont change anything on these
  stuff that i already have"; "you doing pinescript thats for tradingview it has nothing to do with our portal radar at all").
  Their "Moving Averages For All Timeframes" (JohnMuchow, MPL 2.0, Pine v5) unchanged byte for byte, plus a section at the end:
  boxes from DAILY bars on daily and intraday charts, labelled with their range: 1M / 3M / 6M / 9M / 52W / ATH (highest close to
  highest high, joined labels) and broken support (the portal's rule, 3 nearest zones); a level shows while it was overhead at
  the last daily close; alerts through "Any alert() function call": NEAR (within X% under a box, X a setting, 0 = off), INSIDE
  (always), BREAKOUT (over the top of a box overhead at the last close, its own tick box), each once a day per box. NOT in the
  repo (the license allows reuse only in open-source TradingView scripts); not compiled here (no TradingView in the session):
  the user said it "looks good" after the first version; the alert version is not confirmed yet. Answered: TradingView has
  watchlist alerts (paid plans, regular hours only); whether they accept a custom indicator's alert() is not confirmed.
- **Open, each needs the user's go**:
  - **The 15% / 3x exception** (the user, Nov 13: "if stock up 15%, volume over 300% it should automatically qualify for launch or
    launch laggard depending of its 200 sma position ... and it should trigger that time ... and regarding news its big gap, do
    that as well as a rule"; then interrupted by the first-day question). Explained, not built; unanswered: keep the liquidity
    minimums (suggested yes), how big a "big gap" is (suggested 10%), and the 2-year check (a new rule: asked, with the reason).
    FLY Nov 6 passes it; FLY Nov 9 (2.6x) and MBGL Nov 12 (2.0x) do not.
  - First days over the 200 SMA too (the user asked "it could be above 200 sma as well?"; the numbers above; no decision).
  - A click on "Added" sorting the Watchlist by date (offered Nov 13, no answer).
  - Broken support: the buy-point tag "inside broken support: clear over $18.88" (offered, no answer); highs and floors older
    than 52 weeks / 2 years (offered, no answer); "None: at highs" also shows when nothing sits over the buy point (THC, W in
    the 50 EMA undercut tab, Nov 20: seen, not changed).
  - **Desktop "Resistance alerts" on the Alerts tab** (the user, Nov 21: "can we something like that for our desktop alerts (with
    settings) the way i have for my morning breakouts and breakouts not trend ones, with same settings, only thing you add there
    1m/3m/6m/52w and ath, i choose which one ... combination of orh ... where it would feed itself from? ... i would need volume on
    alerts sound for sure"). Not explained or built here: the user is taking it to a NEW session with a prompt given here (a
    third box like 📈 / 📊: tick boxes per level incl. ATH and broken support, NEAR % / INSIDE / BREAKOUT, an ORH combination,
    its own sound and the volume in the voice; to explain first: where it feeds from, levels for every stock it watches, the
    ATH needing more than 2 years of bars, how often it checks).
  - Still open from the first part (archive): the coil alert to look at later, the pre-market blind spot 9:10-9:30, young
    listings (52-week low / 200 SMA), the code grader's "no daily bars" bug.
- Data: radar-tools `long` re-run on Nov 21 with the 135 symbols another session had fetched that morning plus the examples and
  VERX (long_bars.json: 153 symbols).

## Status of the session "Radar: watchlist restructuring (Nov 21)" (Sat Nov 21 2026; session_01PkbDajfJpUeWXECPJeGVh4; in progress)

- **LIVE (the user's "1# go live", Sat Nov 21 2026, branch ccr-ab7f572a-fksxkd merged with main, 726c01d): two tags next to the
  ticker on every Watchlist list** (3-SETUPS, 2-POOL, 1-UPDAY, 1-EP/GAP, START DAYS, TREND). The user: "trend shows state of the
  stock ...but i mainly try grab something from setup or ep gap or start... it has to be actionable thing", "i liked your trend tag
  thing", "so tag for trend tag and tag for momentum!!!".
  1. **Trend tag** (docs/index.html trendTag; live in the session like the Trend column; every stock gets exactly one, first match):
     FULL TREND = 10 EMA > 21 EMA > 50 EMA > 200 SMA, the 50 EMA higher than the day before ("50 ema has to be rising in full
     trend (meaning bigger than yesterday)"), price over the 21 EMA; NEW TREND = price over the 21 and 50 EMA, not all of that
     yet; CAUTION = 10 > 21 > 50 in order, price under the 21 EMA ("not a pullback: to be cautious, if it reclaims good sign,
     if not it has to prove itself"); NO TREND = the rest. The Trend column (Up / Resting / Reclaim / Turn up / Negative) is
     unchanged. Nov 20 close: 3-SETUPS 66 = 37 / 9 / 18 / 2, 1-EP/GAP 20 / 6 / 14 / 0, START DAYS 4 / 6 / 6 / 11.
  2. **Momentum tag** (momTag): a stock on 2-POOL's Momentum section shows MOM 3M (its Why has 3M) or else MOM 1M, "only one of
     them"; 6M is added only when it is up 100%+ in 6 months ("for 6month show if its over 100%": perf_6m_pct, a new field on
     the scan's rows, scanner/run.py details: **the 6M part shows from the Mon Nov 23 evening scan**); the 1-week test and a
     6-month gain under 100% show nothing. The pool's numbers are unchanged. Nov 20: of 134 Momentum names 43 show 1M, 11 3M,
     19 are up 100%+ in 6 months, 68 show no tag.
  Both are in + Filter and Columns ("Trend tag", "Momentum tag") and in a folded box "The tags next to a ticker". Tested in a
  browser on desktop / phone (every list, every tab, 0 page errors; + Filter FULL TREND on 3-SETUPS = 37 rows), again after the
  merge with main (the Resistance-ranges session had gone live). Rules workbook: 2 rows (T1 Trend column). No `--regress`, no
  Launches rebuild (launch.py untouched), no 2-year check (tags). **Not seen on the live page / live prices: check Mon Nov 23.**
- **LIVE (the user's "go live", Sat Nov 21 2026 ~12:30 PM ET, merge f4210a6; Launches rebuilt 12:29 PM, d5d2201): the EPISODIC
  PIVOT / POWER DAY alert on new rules, and two tags on 1-EP/GAP. NONE OF IT HAS RUN ON LIVE PRICES: FIRST CHECK Mon Nov 23 from
  9:31 AM ET** (tested with each example day's daily bar as the live price; the 3-minute opening range with a stand-in).
  The user: "fix to ep alert so we dont miss it". Found: of the 40 names on 1-EP/GAP on Nov 20 only 28 met the alert's rules at
  the close of their gap day (APP Nov 5, WING Oct 28, TMDX Nov 6 under the 200 SMA; HAWK, LFTO Nov 13 without one; KD Nov 4
  opened 14.91 under its 21-day closing high 15.20; AZTA, UPBD, PCOR, KVYO, CHYM under 3x), and CGON (launched Nov 6, +23.7% gap
  on 8.2x Nov 16) could not ring: launch.json watch drops a stock launched in the last 20 sessions.
  1. **The EP alert** (radar/alerts.py find, EP_GAP / EP_RV / EP_MIN_PRICE / EP_ORH_MIN), on the LIVE price: a 5%+ gap (was 6%), a
     volume pace of 2.2x+ (was 3x), over the 50 EMA (new), $10+ now (was last night's close: POET closed 8.59 the day before its
     Apr 21 2026 EP day), 30%+ over the 52-week low (main() already checked it for every alert: I first told the user it was
     new), over the highest close of the last 21 sessions; **NO 200 SMA rule, NO 1-month-high rule** ("1month i agree its same
     thing"). The 21-day level: a stock that OPENED over it rings as before and holds while the price is over it (CHYM Nov 5
     rings at the open, out when back under 30.46); one that opened under it ("its for laggards starts ... alert would just ring
     and sound when it passes 2 true states: above orh, plus above the level") rings when the price is over its **3-minute
     opening range high** AND over the level (main(): ep_orh_ok, the high read once a stock and kept in the state file
     `ep_orh`; the alert says "opened X% under it"). The user's first idea, an open within 1% under the level, was dropped
     for this ("we dont need 1% rule then").
  2. **Power day**: keeps gap 8%+, up 10%+, 3x+, on the same rules (no 200 SMA, no 1-month high). **The Launches table's own
     power day (the evening scan) is unchanged**: a live POWER DAY under the 200 SMA is not a launch that evening, and the
     "Launching today" table on the Launches tab still tags by the old rules (told the user; offered to align, no answer).
  3. **The 9:31-9:34 early heads-up** follows: every 5%+ gap over the 50 EMA, $10+ ("EP gap", 8%+ "power-day gap"), over or
     under the 200 SMA, with how it opened vs its 21-day closing high; the catalyst / launch shapes as before (more early
     heads-ups on earnings mornings: told the user). The other session's find_early_lists (the followed names) runs after it.
  4. **launch.json `ep_watch`** (scanner/launch.py, L ep_watch_min_price 7): the names ONLY this alert reads on top of `watch`:
     a liquid stock launched in the last 20 sessions, and a stock liquid but for its price closing $7-10. 111 names on the
     Nov 20 close (62 launched, 49 at $7-10). `watch` is unchanged (888, identical); fast.py reads their prices each minute.
     A stock under its 200 SMA rings as an EP when it meets the rules; the laggard-launch alert stays for the ones that don't;
     the EP stands for the stock's catalyst gap, A launch and laggard launch.
  5. **1-EP/GAP list: no rule change, two tags next to the ticker** (the user: "i agree with your recommendation regarding ep
     list.. we keep it as is, and we add your faded tag next to ticker", "agree with everything you recommended"): FADED = the
     EP day closed below its open or in the bottom half of its day's range; UNDER 21D HIGH = it closed at or under the highest
     close of the 21 sessions before (scanner/run.py ep_day -> the row's `ep_day`; a fact of that day, fixed). **They show
     from the Mon Nov 23 evening scan** (so does the Momentum tag's 6M). On 629 list EP days of Jan 1 - Sep 25 2026: a close
     under the EP day's low within 5 sessions FADED 50% vs 30%, UNDER 21D HIGH 48% vs 35%; after 20 sessions it evens out
     (higher than the EP day's close 47% / 47% and 43% / 48%; ran 20%+ 30% / 31% and 35% / 30%): a warning for the first days.
  Numbers the user saw (2026, daily bars; the alert rows are estimates, no minute history): the list rule 629 EP days, 55% ran
  10%+, 31% ran 20%+ (195), 44 ran 50%+, 37% failed (a close under the EP day's low within 5 sessions); the old alert 187 days
  / 49% / 27% (51) / 33%; the new alert 463 / 57% / 32% (147) / 40%; by market: Jan-Feb 28% ran 20%+, Mar-May 40-43%, Jun-Sep
  19-22%. A gap in ADRs was tested and not taken (87% of list EPs gapped 1 ADR+ anyway; the ones under 1 ADR, the fastest
  stocks, ran 20%+ 40% vs 30%); gap 5-5.5% ran 20%+ 38%. Expect about 2-3 EP alerts a day, 10+ on a heavy earnings day.
  Tested: 32 cases old rules vs new (every example above; each rule alone; 30 rounds of random prices on the real watch list:
  4,187 other alerts identical, 0 different); main() three runs on stand-in files (sent, KD out of the box under its 3-minute
  high, BACK ON); the scan on the branch vs the same scan on main's code (radar-tools `setupsdry` on both: launches, setups3,
  start_days, watch identical); `--regress` "every agreed example reads the same"; scanner/run.py end to end on a copy with
  history/bars_2y.json.gz; the page on desktop / phone, 0 page errors; again after the merge with main (the other session's
  early heads-up for the followed names had gone live in alerts.py / fast.py / day.py). Rules workbook: 5 rows. No 2-year
  check (alert settings and tags). After the push picks.yml by hand: launch.json has ep_watch 111, launches 134 the same.
  **Check Mon Nov 23**: alerts.json `:ep` / `:power` keys (how many; any under the 200 SMA; one with "opened X% under" and
  "3-minute opening range high"), `:early` count 9:31-9:34, the state's `ep_orh`, the minute tick's time with 111 more
  quotes; Monday evening: `ep_day` on the 1-EP/GAP rows and `perf_6m_pct` in setups/latest.json.
- **Decided with the user this session (no build needed)**: the Watchlist feeds stay as they are ("we are only interested in
  fast movers thats why setup feeds from updays and fast movers 1 month 3 month and 6 months": NO whole-market trend list, NO
  feed change); nothing is dropped (1-UPDAY, 2-POOL stay); the 2-POOL momentum numbers are NOT changed (25% / 50% / 100% was
  asked, then left: "without checking anything, the way they are now"); **the 1-EP/GAP list rules stay as they are** ("i agree
  with your recommendation regarding ep list.. we keep it as is"): on 629 list EP days of 2026 no gap / volume number raised
  the 31% that ran 20%+, a 2.2x volume rule lost 12 winners (AEHR Mar 31 +176%) and a 21-day-closing-high rule 31.

## Status of a chat session outside the Radar sessions (Fri Nov 20 2026 ~10:40 AM - 9:20 PM ET; session_01PkbDanJN5CDcjcEmx8eMXh)

- **LIVE (the user's "go ahead ok others as well, as long as they meet liquidity requirement", Fri Nov 20 2026 ~9:10 PM ET, merge of
  test/theme-business): themes by business line.** The user (the IT Services & Consulting table, ACN INFY CTSH BR TYL IT EPAM
  G EXLS DOX KD DXC): "they cant be in same theme ... maybe they are in different line of business and this pile up not
  accurate"; "its not only about that one, other themes might have issues"; "you would move them to correct themes right?".
  1. radar/pipeline.py: an automatic add now also needs the business line (base_group: the industry groups' lines) of one of
     the theme's core stocks. One that fails for its best-fitting theme joins the theme of its own line it tracks best, by
     the same tests; with none it stays in its industry group / an automatic group. Hand-approved names (theme_adds.json
     "adds") pass for their theme. New theme_adds.json "keep": 27 names the user kept under another label (13 smaller regional
     banks; WK VERX BL NCNO BILL OTEX in Enterprise SaaS; VZLA SSMR; MBC ALLE; KR; POOL SITE; SNN): they pass the line test
     for that theme only and still need 0.6+, the sector and the liquidity floors.
  2. Gartner (IT) out of the IT Services & Consulting core (research subscriptions).
  3. Dry run (radar-tools `groupsdry` on the branch, Nov 20 close): 251 automatic adds -> 198. Moved 11: BR, JKHY -> Fintech &
     Payments; TYL, ROP, AMPL -> Enterprise SaaS; ECG, LGN -> Data Center Builders & REITs; PTEN -> Offshore Drillers; CVE ->
     Oil Majors; KOS -> Shale & Permian E&P; SBSW -> Silver Miners. Out of their theme 57 (19 in an automatic group: Pipelines &
     Midstream, Beverages, Household Products, Info Services & Staffing ...; 15 in a tight industry group; 23 in neither: LPL SNX
     DOCN GTX BWXT CTRI MWH GDDY TRMB DOCS CHKP DOX IBM ZM SEIC WAB CLMT ZTS ABSI RXRX WY LKQ TNL). ASX has no theme now (out
     of AI Chips & CPUs; under 0.6 / the semi floor with Semi Test & Packaging, where the user approved it): told the user.
     IT Services & Consulting: CTSH EPAM GLOB EXLS DXC INFY G ACN + KD CNXC GDYN.
- **LIVE, same merge: a theme's bellwethers are its two largest CORE stocks** (radar/event.py all_bellwethers; Keysight, an
  automatic add, had been read as Semi Test & Packaging's first reading on Nov 20). On the Nov 20 files: CNQ EC IBM PH Q ROP
  SWK UL out; AME ENTG EOG INFY MO OC PAYX YPF in (150 still).
- **LIVE, same merge: the context on GROUP MOVE / THEME MOVING UP alerts** (radar/alerts.py move_context; the user, Nov 20:
  IT services up 2-5% the morning after GLOB's report, "we were supposed to have reason for that today we didnt get it").
  Two facts, worded as context, never the cause: "also reported" (a stock of the group with today as its reaction session
  that gapped 5%+; its Earnings-tab reading, the gap, where it is now) and "moving the other way" (up to 3 themes whose
  tight members are 2%+ the other way on average, when the group is 1%+ either way; a THEME MOVING UP alert only when the
  theme is up). Replayed on Nov 20's 33 group / theme alerts with the 10:35 prices: 26 got a line; IT Consulting &
  Outsourcing read "also reported: GLOB (Somewhat bearish ...; gap +8.7%, now +2.8%) ... +3.9% on average; moving the
  other way: Neoclouds & AI Hosting -10.7%, Memory & Storage -10.1%, Optics & CPO -9.7%". **Not seen live yet: the first
  GROUP MOVE on Mon Nov 23 is the check.** The bellwether "why" (alert_reasons) is still OFF: the user's call.
- Rules workbook: 3 rows (automatic theme members, the bellwether rule, the move context). No `--regress` (launch.py
  untouched; the bars need a job on main), no 2-year check (no pattern, buy point or scan rule).
- **Explained, no change (Nov 20)**: ACN had no morning breakout alert because its 20-day ADR (3.84%) is under the boxes'
  ADR 4%+; DXC and IT fired in 📊 at 9:35; GDYN, KD, DOX under Rel vol 0.8x; CNXC under $30M a day; GLOB never back over its
  opening range high. **Open: EPAM passed every filter at 10:35 and did not alert** (the box was on ORH-3min from 9:29 and
  saved ORH-5min at 10:14): replay it (radar-tools `morning`).

## Status of a chat session outside the Radar sessions (Thu Nov 19 2026 ~11:25-11:45 AM ET; session_01PkbDanQBJvqxfoMDBsGdZG)

- **LIVE (the user's "go live", Thu Nov 19 2026 11:41 AM ET, merge 9c9f6f9 of test/backon-quiet): a morning breakout BACK ON
  after its box's End time is silent**, 📈 and 📊. The user: "back on alert runs every 15min correct, i dont want to hear any
  sound (meaning just silent) after cut off time"; the End was 10:15 (saved 10:18 that day) and NTAP, CLS, TWST, GNRC, NTRA
  (📊), TDC, AMPL (📈) rang BACK ON 11:21-11:31. docs/index.html only: quietBack(key) (keys SYM:mbobackHHMM / SYM:mbo2backHHMM,
  the key's time later than the box's saved End; 📊 with nothing saved = 📈's) -> notify: no sound, no voice, no sticky pop-up,
  no flashing title; the line stays in the log and the stock goes back in its box. The job (alerts.py morning_holding) is
  unchanged: it still writes the back-on alerts all day. Inside the window BACK ON rings as before; the other boxes ring all
  day. Checked on that day's alerts.json: 67 back-on alerts, 31 after 10:15 silent, 36 inside the window with sound; 10:15
  rings, 10:16 is silent. **Not seen in a browser**: the first BACK ON after the go-live is the check (the user refreshes the page).
  Open: alerts/morning2.json is still not saved (📊 follows 📈's window and filters; 135 alerts in 📊 by 11:25 that day).

## Status of the session "Radar: gap news and NVDA ecosystem links (Nov 17)" (Tue Nov 17 2026 ~5:10 PM ET - Wed Nov 18 ~11:30 PM ET; session_01PkbDanF5dAAQH9AZXNPE3K; in progress)

- **LIVE (the user's "Ok. sounds good" to my "go live now, with the Event card only", Wed Nov 18 2026 ~11:22 PM ET, merge f462127;
  branch claude/eloquent-babbage-xub6om): the Event card on the Pre-market tab. The "why" on the alerts is BUILT and SWITCHED
  OFF** (radar/bellwethers.json `alert_reasons` false: alerts.py and day.py do nothing with it; the user agreed to switch it on
  after ~3 sessions of the card reading right: ask before touching it).
  The user (NVDA's report, Nov 17): "it has major implications for all companies depend on nvda ... our code should be able
  connect dots"; "logic and rationale should be accurate linking"; "reason of alert has to be clear explanation ... price and
  volume makes me decide, new direct link, fundamental news helps conviction"; then "when direct link thats top top, then themes
  same line of business ... most rational direct link then derivatives"; "i gave examples" (not a list: the rules are general).
  1. **An event = a bellwether reports** (radar/event.py, run by the Earnings job after earnings.py -> radar-data events.json;
     by code, no Claude). 150 bellwethers: the written maps in radar/bellwethers.json (NVDA, MSFT, GOOGL, AMZN, META) and, by rule,
     the two largest liquid stocks of each of the 73 named themes whatever their ADR (the user: "agree"). One the Earnings tab
     doesn't carry (MSFT / GOOGL under 3% ADR, WMT) gets its own row (the day from Yahoo, estimates saved before the report, the
     release read with the tab's reader). The card is up from the morning of the report to 8 PM ET of the reaction session;
     several at once: a button each.
  2. **Level 1, on top: direct ties and rivals**, each stock written out with its reason. A 📄 opens the linked company's own
     annual report where it names the bellwether (CRWV: "approximately 67% of our revenue from our top customer, Microsoft";
     warrants issued to Amazon by ALAB, CRDO, AAOI, JBL, FLEX, STM). 9 links have no such proof (ANET, AVGO, NVDA, MRVL under the
     cloud giants: the suppliers write "Customer A"): written from public deals, the reason says "Not named in its annual
     report" (the user kept them, and the rivals).
  3. **Level 2, the same theme** (the user: "add full build"): "same business" = the other tradable stocks of the bellwether's
     own theme (up to 12), with its sentence on their niche when the report has one WITH A FIGURE (niches written for
     Cybersecurity only); "its theme is in the report" = the 6 largest stocks of another theme when the report has a sentence
     with that theme's words (radar/theme_words.json, 70 themes) and a figure. No direct tie is claimed; the reason says demand
     for the whole group or business taken from it, and the card shows each peer "moving with / against" the bellwether (the
     user: "direction for peers: agree 100%"). Suppliers of suppliers (the map's step / spend entries) stay off.
  4. **What it said** = the bellwether's own sentence from its SEC results filing (every exhibit: NVDA's press release and CFO
     commentary), first one that names the stock. **The line on top**: the Earnings tab's reading, speeding up or slowing (this
     quarter's growth vs the quarter before's and vs what next quarter's guide implies; the user: "acceleration could be this
     quarter and their guidance is a sign"; a guide read 12%+ off the street is left out), the bellwether's own lead number
     (NVDA Data Center, AMZN / META the capital-spending guide), "Growing fastest".
  Tested: two live test builds (NVDA Nov 17: revenue $115.8B vs $108.7B, +103% y/y, the quarter before +106%, guide $130.0B
  +4.1%; 37 direct + 19 same-theme stocks. PANW Nov 18: $3.44B +39%, NGS ARR +66% to $9.73B, PANW +9.1% after hours, all 12
  peers up); replays of past reports (radar-tools `eventreplay SYM prev|DATE ...` -> events_replay.json): NVDA Aug 26, META
  Oct 21, MSFT / GOOGL Oct 28, AMZN Oct 29 (all 28 linked stocks closed lower the next session), CRWD Aug 26 (+20.5%, all 12
  peers up), PANW Sep 1 (-9.3%, 11 of 12 down), MU Sep 30, RKLB Nov 9; the merged page on desktop / phone, every tab, with and
  without an events file, 0 page errors; the alerts get nothing while the switch is off. After the push earnings.yml run by
  hand (11:24 PM ET): events.json with PANW (out, 12 peers), `alert_reasons` false, 0 errors; earnings.json 130 rows, 0 errors.
  Rules workbook: 4 rows (event links, level 2, the link finder, the alert reason as switched off). No `--regress` (launch.py
  untouched), no Launches rebuild, no 2-year check (no pattern, buy point or scan rule).
- **First checks Thu Nov 19**: the card at the open for PANW's reaction session (moves from the pre-market scan, then live);
  WMT, BABA, PDD before the open (own rows: the first live run of that path with a real report; tested only on NVDA, where
  the EPS did not come through), GAP / ROST / KEYS after the close; the Earnings job still on time with the extra step.
- **The link finder** (radar/probe_links.py, radar-tools `links` -> radar-data probe_links.json, ~10 minutes, nothing live
  reads it): the newest annual report of 2,010 tradable stocks searched for 18 bellwether names, each sentence sorted (a share
  of revenue, a stake / warrant, sells to it, buys from it, agreement, rival, a tool it uses, mention). It proposes; I read
  every sentence before a link went into the map. It added NVIDIA's right to buy 30 million IREN shares.
- **Known weak spots (told the user)**: the earnings call is not read (not at the SEC; the news feed had 1 headline after NVDA's
  report), so MSFT's and GOOGL's spending guide and PANW's per-niche numbers are missing; the theme word list is mine and has
  run on eight real reports (fixed so far: "cryptography" matched Crypto; PANW's "About" paragraph and dateline were quoted:
  a theme / niche quote now needs a figure); some quotes are thin (NVDA's one optics sentence is about a Cisco module); the
  Earnings tab's guidance reader misread TGT Nov 18 (a guide -15% vs the street: its own bug, not fixed here).
- **Open, the user to decide**: switching the alert reason on (after ~3 sessions); written maps for AVGO, TSM, MU, SPCX
  (MU and SPCX are covered by the theme rule); niches for other themes; unscheduled news events (a rocket launch, a
  contract): not built, "later". The power contracts (CEG, TLN, VST under the cloud giants) are written and off.
- **Not taken (the other session's build)**: claude/funny-wright-b2z88z (the reason on morning breakout / GROUP MOVE alerts from
  Yahoo / Alpaca headlines, the user had not approved it): its own Nov 16 replay left 11 of 14 alerts without a reason and
  the Medicaid headline came 3.5 hours late. Told the user; this session's event links are the answer for scheduled reports.
- Test files on radar-data: events_test.json, events_replay.json, probe_links.json (the portal reads none).

## Status of the session "Radar: move Watchlist tabs left/right (Nov 18)" (Wed Nov 18 2026 ~12:20 PM ET - Thu Nov 19; session_01PkbDaiB9dTkk1MWcV4oJQi; in progress)

- **LIVE (the user's "go live", Thu Nov 19 2026, branch test/wltabmove, merge 05be6b5): the Watchlist list buttons (3-SETUPS,
  2-POOL, 1-UPDAY, 1-EP/GAP, START DAYS, TREND) drag left / right exactly like the main tabs** (the user: "can you make it a way
  that i can move this tabs left or right", "do exactly how other tabs i move"; the main tabs have had it since Nov 6). The
  user was annoyed I made it sound complicated: it is a copy of the main-tab feature, say so plainly. docs/index.html: an
  IIFE after the main-tab one, localStorage `radar-wl-order` (per browser), a "↺ order" button next to the row when moved;
  clicking a button still opens its list, the page still opens on 3-SETUPS. Tested in a browser: drag START DAYS to the front,
  click it (44 rows), reload keeps it, ↺ order resets, main tabs untouched, 0 page errors. Page layout only: no rules workbook
  row (the main-tab drag has none either), no `--regress`, no Launches rebuild, no 2-year check.
- **Test only**: nothing.

## Status of the session "Radar: Cybertruck morning breakout alerts (Nov 18)" (Wed Nov 18 2026, from ~2:50 PM ET; session_01PkbDaivTc9D2kGvMMYMMLt; in progress)

- **LIVE (the user's "ok go live", Wed Nov 18 2026 ~4:20 PM ET, merge 8b4b75b of test/movers11): the movers every minute 9:31-11:00
  (was to 10:30), and a "How often prices update" note on Groups & themes and Gainers & losers.** The user: "these 936-1030 can
  you do 932-11 am", "yes do 931", "put both places so i know how often prices gets updated". radar/day.py movers_window
  (9,31)-(11,0); docs/index.html: the 20-second page check to 11:00 (n.m > 660), the live line "every minute to 11:00", the note
  (data-upd, under the controls of both tabs, filled in drawLiveLine with the last full / 2%+ update time). Morning breakout
  alerts (their own 9:35-10:30 window) and Launches untouched. Tested: movers_window 9:30 no / 9:31 / 10:59 yes / 11:00 no; the
  page on desktop / phone with the live data (both notes, 0 page errors). Rules workbook: 1 row. No `--regress`, no Launches
  rebuild, no 2-year check (a timing). **FIRST CHECK Thu Nov 19**: live.json fast_at keeps moving every minute 10:30-11:00.
  My mistake, corrected with the user: I first wrote the 1-minute window starts 9:36 (it is 9:31 since Nov 17).
- **Answered, no change**: none of the Cybersecurity stocks (CRWD PANW FTNT ZS NET OKTA S RBRK TENB QLYS SAIL NTSK RPD FROG,
  +6-15% Nov 18) gave a morning breakout: the move built after 10:00 on Rel vol 0.4-0.9x (OKTA TENB QLYS SAIL RPD RBRK NET),
  CRWD / PANW / ZS under the 50 EMA, S / TENB / OKTA / QLYS 10 EMA under the 21; NTSK met every setting at 10:37 (after the
  10:30 end). The user's saved settings (alerts/morning.json, 9:24 AM): 9:35-10:30, 2%+, Rel vol 1x, the trend rules. Offered,
  no answer: Rel vol 0.7x, an 11:00 end, no 10 > 21, a group-move alert. Neoclouds on the Gainers tab (4%+, Rel vol 0.8x): only
  RIOT (+7.9%) passed at 2:50 PM, HUT +6.2% at 0.76x; the miners +2.5-3.7%. **Open**: the user says more neoclouds were 4%+ when
  they looked: asked for a screenshot (not seen in our data; live_history logs only 5%+).

## Status of the session "Radar: why AVEX isn't on the EP watchlist (Nov 17)" (Tue Nov 17 2026, from ~1:25 PM ET; session_01PkbDameNZtixLSWb6F7Thg; in progress)

- **LIVE (the user's "go live for two changes already tested", Tue Nov 17 2026 ~2:55 PM ET, commit 9cd7f74): two changes.**
  1. **The Watchlist's relative volume is on 20 days (was 10)**: the day's volume vs the average of the 20 sessions before, for
     the 1-EP/GAP 2x and the 1-UPDAY 1x tests and the Rel vol saved on the Watchlist rows (scanner/screens.py REL_VOL_DAYS,
     scanner/settings.json screeners.rel_vol_days 20, set in run.py build). The user: "Tradingview shows 200 rvol ... for rvol it
     should 20". Launches, Start days and the portal's Rel vol column were already on 20. Measured (radar-tools `rvdays` ->
     radar-data probe_rvdays.json, scanner/probe_rvdays.py; 30 sessions Oct 7 - Nov 17, 2,912 stocks): 1-EP/GAP 82 -> 81 (only
     FSLY Oct 9: 3.29x on 10 days, 1.95x on 20); 1-UPDAY 793 -> 799 (86 join, 80 leave, all near 1x: LSCC Nov 11 0.94x -> 1.18x
     joins, LQDA Nov 11 1.54x -> 0.93x leaves). **First check: the Tue Nov 17 evening scan** (setups/latest.json settings
     screeners.rel_vol_days 20; the "why" of new rows carries the 20-day figure).
  2. **Start days is the list START DAYS on the Watchlist tab, next to 1-EP/GAP** (the user: "can we move start day to watchlist
     next to ep/gap watchlist", "do it"; my recommendation was move, not show in both). docs/index.html: the card #ln-sd-card
     moved from the Launches tab to the Watchlist tab, shown when the list picker is on START DAYS (the list's own table, rules,
     Section and + Filter are hidden then; the ticker box filters it); drawStartDays is its own function (was a block of
     drawLaunches); the Launches search shows a Start days match as a button that opens it on the Watchlist tab. Same rules,
     columns, x, download and note; it reads launch.json start_days and does NOT feed 3-SETUPS. The Launches tab now has
     Launching today, Launches, 50 EMA undercut, Trending groups, History test.
  Tested: the page on desktop / phone with the live files (46 rows, sort, the ticker filter, back to 1-EP/GAP 49 rows, the jump
  from the Launches search; 0 page errors). Rules workbook: 2 rows. No `--regress` (launch.py untouched; this session has no
  long bars), no Launches rebuild (told the user, launch.py untouched), no 2-year check (a list threshold and a page move).
- **Answered, no change**: AVEX is not on 1-EP/GAP because its gap day Nov 12 2026 (gap +12.5%, +13.4%, close 13.76) closed under
  its 50 EMA 13.93 ("every list needs a close above the 50 EMA"); FRVO Nov 9 2026 (+26.0%, gap +0.1%, close 11.38, 50 EMA 13.03)
  had no gap and is under the 50 EMA too (it passed 1-UPDAY's move and volume). Both are on Start days (the user: "its good
  that its on start day"). Offered, not taken up: dropping the 50 EMA test for 1-EP/GAP / 1-UPDAY. Neither would be an EP
  alert (FRVO no gap; both under the 200 SMA stand-in and under the 21-session closing high); the START DAY alert went live Nov
  13, after both. The lists show about 4:27-4:35 PM ET (Nov 16: 4:27 / 4:28). The user does NOT want start days added to the
  table during the day ("its ok the way its now, as long as it fires alert").
- **LIVE (the user's "go live", Tue Nov 17 2026 ~3:15 PM ET, commit fdef44c): the START DAY alert sounds like an important
  alert** (the user: "does it make sound bcs its important one... and say volume?", "test it for sound"). docs/index.html: its
  own chime (TONES s: three rising notes at full volume; a heads-up's is one short quiet tick), the voice says "Start day, R K L
  B, volume 1.8 times" (sayOf / isStart; was "Heads up, R K L B", no volume), announced right after the EPs (announce, sndOf),
  and a START DAY example in the Alerts tab's sound test. radar/alerts.py find_start: the phone alert at high priority every
  time (was high only with the "new trend after a reset" / "launch size" tag). It stays in the 👀 Heads-ups box; its rules and
  text are unchanged. Tested: the page's own sound test in a browser with the sound and voice captured (START DAY 587 / 880 /
  1175 Hz at full volume and "Start day, R K L B, volume 1.8 times"; the plain heads-up still its quiet tick and "Heads up");
  0 page errors. Rules workbook: 1 row. **Not seen: a real START DAY alert on live prices; the phone priority starts Wed Nov 18**
  (the running day job keeps Tuesday's alerts.py until its next start). No `--regress`, no Launches rebuild, no 2-year check
  (how an alert sounds).
- **Test only**: nothing.

## Status of the session "Radar: opening range 1/2/5-min choice (Nov 17)" (Tue Nov 17 2026, from ~10:10 AM ET; session_01PkbDajetWCG8Sskm5kAjad; in progress)

- **LIVE (the user's "go live", Tue Nov 17 2026 ~10:45 AM ET, branch claude/loving-wozniak-p738we): ONE "Above ORH" filter with a
  1min / 2min / 5min picker, the same picker in the morning breakout box, the minute reads from 9:31. FIRST CHECK Wed Nov 18 at
  9:31-9:37 AM ET: none of it has run on a live open** (the running day job keeps Tuesday's code until its next start).
  The user: "above orh, then when i put it does 1min, if i put 2min it does 2 mins, if i put 5min it does 5min, so basically
  just 1 filter", "same for alerts", "start 931".
  1. **+ Filter (every tab)**: the chip "Above ORH-[1min / 2min / 5min]: any / Yes / No" (docs/index.html: f.m on the filter,
     orhM / orhOf(s, m)); a filter saved before is the 5-minute one; the ORH column stays the 5-minute high.
  2. **radar/levels.py**: levels.json rows are now [high 5, low 5, high 1, high 2] (+ `part`: the stocks read before 9:36).
     The 1-minute high (the 9:30 bar) from 9:31, the 2-minute (9:30-9:32) from 9:32, both from Yahoo's 1-minute chart; the
     5-minute pair from 9:36 from its 5-minute chart, as before. A stock is read again only when its next range is finished.
  3. **radar/day.py**: movers_window and the levels step start at 9:31 (were 9:36).
  4. **Morning breakout** (radar/alerts.py, the Alerts tab box): `orh_min` 1 / 2 / 5 in alerts/morning.json (5 when not
     saved); the window starts no earlier than 9:31 / 9:32 / 9:35; the alert names the range; 5 reads the 5-minute chart as
     before, 1 / 2 the 1-minute chart (morning_levels n); levels kept for another range are read again. The user's saved From
     is 9:35: the box tells them to set 9:31 / 9:32 (not changed for them). radar-tools `morning orh_min=1 start=09:31`
     replays it.
  Tested: stand-in runs minute by minute (levels.py 9:30-9:50, load_morning, morning_levels, check_morning after a range
  change); the page on desktop / phone (old filter = 5min, the choice kept after a reload, each range its own high, the
  search, the Alerts box; 0 page errors); a REAL read on the branch (radar-tools `moverstest`, now with a fresh read of every
  mover: 209 stocks' ranges in 3.2 s). Rules workbook: 3 rows. No `--regress` (launch.py untouched), no Launches rebuild, no
  2-year check (a filter and an alert setting).
- **LIVE (the user's "go live", Tue Nov 17 2026, later that morning): the morning breakout box uses the + Filter's wording**:
  "Above PDH" (was "Over yesterday's high") and "Above ORH-[1min / 2min / 5min]" (was "Over the [1-min] opening range
  high"), also in its "Now:" / "After Save:" lines (the user: "why you didnt do same wording for both", "do both above pdh
  and above orh (then your mins)"). Page wording only (docs/index.html); the alert messages are NOT changed (the user:
  "sound alerts message we are not changing"). Tested: the box on the page, 0 page errors.
- **LIVE (the user's "go live", Tue Nov 17 2026 ~11:40 AM ET): the 📈 Morning breakouts box holds only what still meets the
  settings; a stock back on alerts.** The user: "it was supposed to be in true state, meaning when it gets out it takes out of
  box, when it gets back in it just alerts that its back in" (TSCO Nov 17: alerted 9:45 at 38.72 over PDH 38.58 and ORH 38.38,
  at 11:20 38.29 and still in the box). The Nov 5 rule ("whatever doesn't hold, it has to be taken from that box") was live for
  🚀 ⚡ 🎯 ↩️ only; the morning box had been built Nov 9 as "a one-time morning call" (the builder's choice). Now:
  radar/alerts.py morning_holding: holding = EVERY setting of the box (the user: "whatever i choose in that filters": % up,
  Rel vol, Above PDH, Above ORH, the price / trend rules, the + Filters; not the time window), checked all day at each live
  update on the levels kept at the alert (mbo_lv); state lost / back for SYM:mbo; back on = one alert "SYM MORNING BREAKOUT
  BACK ON" (key SYM:mbobackHHMM, portal only), at most one every 15 minutes a stock (MORNING_BACK_EVERY; the user: "return
  alert at most once", read as agreeing to the 15 minutes: told them, to correct if they meant once a day). docs/index.html:
  the 📈 box steps down to 👀 Heads-ups (↓) and back like the other boxes; the BACK ON line is in the log only. Tested: TSCO's
  day through morning_holding with the saved settings (out 11:20, back 11:40 with the alert, a 2nd return 10 minutes later
  silent, out on Rel vol 0.8x with the price over both levels); the page with the day's real alerts.json (holding, stopped,
  back on), 0 page errors. Rules workbook: 2 rows. **Not seen on live prices: check Wed Nov 18** (alerts.json lost / back keys
  ending :mbo, :mboback items). The other boxes still come back silently ("holding again" note, no alert): offered the same
  alert there, no answer.
- **LIVE (the user's "go live", Tue Nov 17 2026 ~11:55 AM ET): the Earnings tab's saved ADR minimum is 3%** (was 3.5%;
  earnings/rules.json on main, the user's saved rules: only min_adr changed, saved_at / by updated). The user: "why acm wasnt
  in my earnings reactions today", "drop adr to 3% so i dont miss stuff like this anymore". ACM (reported Nov 17 before the
  open, +10%, EP alert 9:35) has ADR 3.09%. Eligible stocks 794 -> 977. **My mistake, corrected with the user**: I first said
  ACM also failed "30% over the 52-week low": that is the DEFAULT (scanner/settings.json); the user's saved rule is 0% since
  Nov 9, so only the ADR kept it off (read earnings.json `rules`, not the defaults). The 52-week-low test on the pre-market
  price (the user's "lets apply that") was therefore not needed and NOT built. No code changed; defaults and the rules
  workbook unchanged (they describe the defaults). earnings.yml run by hand after the push (11:50 AM ET): 115 -> 122 rows, 0
  errors, ACM on (reported Nov 16 after the close, reaction +12.6%, read Mixed).
- **Seen, told the user**: a 5-minute high read an hour later is 0.1-1% HIGHER than the 9:36 read for 16 of 205 stocks (SMWB
  8.90 -> 9.00, ECG 84.86 -> 85.35), from either chart: Yahoo adds late prints to the first bars. So a high read in the first
  minutes can be a little low (a stock shows "above" a few cents early); the 1- and 2-minute highs are read again at 9:32 /
  9:36. Offered, not built: one more read of all the ranges around 9:45.
- **Check Wed Nov 18**: levels.json saved_at ~9:31 with rows [null, null, high 1, null], the 2-minute highs at 9:32, the
  5-minute ones at 9:36 and `part` empty after; live.json fast_at from 9:31; the day job's ticks on time 9:31-9:36.

## Status at the end of the session "Radar: Start days stay on until they fail + 0.8 ADR start (BILL, Nov 16)" (Mon Nov 16 2026 ~11:30 AM - 10:15 PM ET; session_01PkbDakpheN6wD5vCKyUvBf)

**In one line: the Start days table now works like Launches: no age limit, no 50 EMA rule, the newest start only, fresh from Nov
1 2026, off on a close 1 ADR under the start close (early) or 1 ADR under the 21 EMA after a 2 ADR run (late), 43 sessions
without a new high; the start day's move is 1 ADR or 4%+ with 0.8 ADR; the note folds. Three go lives, all on main, the portal
rebuilt (47 rows). Nothing left on a test branch. FIRST THING NEXT SESSION: Tue Nov 17's 4:40 PM scan (the first real run of the
1 ADR lines: who left, who stayed; LSCC -0.9 ADR and MTCH -0.5 ADR were one red day from the line) and the first live START DAY
alerts under the 0.8 ADR rule (alerts.json `:start` keys).**

- **The Start days rules as they stand (scanner/launch.py L; rules/SCANNER_RULES.md)**: ON = the 9 start-day tests, the move = up
  1 ADR+, or up 4%+ that is also 0.8 ADR+ (ZETA Nov 9 2026). OFF = a close under the start day's low that is also under the 21 EMA;
  a close 1 ADR+ under the start day's close (QNT Nov 6 -> off Nov 16); once it has closed 2 ADR+ over the start close, a close
  1 ADR+ under the 21 EMA; 43 sessions from its highest point without a new high; the user's x; a newer start day replaces it
  (and when that one fails the stock is off). No age limit, no 50 EMA rule, no ADR floor to stay (buyouts like BWIN stay until a
  line fires). Shown: start days from Nov 1 2026 only.
- **Open / the user to decide**: none from this session. Offered, no answer: "back on <date>" under a launch date on the Launches
  row (BILL: off Sep 23 - Oct 15 is invisible); a tighter reset (BILL's 3 lower highs are weak). Not built, measured: a "2 ADR off
  the top close under the 21 EMA" line (loses MU / TWLO); "back under both EMAs = off" (loses 35 runners).

- **LIVE (the user's "go live", Mon Nov 16 2026 ~4:25 PM ET, branch claude/youthful-brahmagupta-i7nqxp, merge 01d562b): the
  Start days table keeps a start day like a launch, and the start day's move takes 4%+ with 0.8 ADR+.** Four parts:
  1. **No age limit** (was 5 sessions, "getting old agreed" Nov 15). The user: "i want start days act like launch day meaning i
     dont want them disappear from list unless criterias i put becomes invalidated", "take this rule off, so they will stay
     alive!!!". scanner/launch.py L start_list_days = 0 (0 = no limit).
  2. **No 50 EMA rule on the table** (was: 2 closes in a row under the 50 EMA, in the first 10 sessions only when also under the
     close before the start day). The user: "if stock coming out of correction it could be 2 times below 50 ema but still
     above start day". start_listed = the fail rule (a close under the start day's low that is also under the 21 EMA) + 62
     sessions from its highest point without a new high ("keep it"). WRBY Apr 14 2026 (start 23.14, low 21.03) closed under
     its 50 EMA Apr 23 - May 6 without closing under 21.03, +23% May 7: the old rule took it off Apr 29, now it stays.
     The user's other idea, 2 or 3 closes under the 21 EMA, was measured and not taken (~179 stocks, 403 start days Nov 2024 -
     Sep 2026, 205 ran 15%+ within 40 sessions; runners still on the table when they ran: 50 EMA rule 131, 2 closes under the
     21 EMA 117, 3 closes 124, the 50 EMA from session 21 137, no 50 EMA rule 140).
  3. **Only the newest start day counts**: when it fails the stock is off the table, an older start day does not come back (the
     user: "if newer start day fails it should get off the list (bcs its below start and below 21 ema!!!"). Before, the table
     fell back to an older start still holding (~1,180 stock-days in 12 months on the ~179 stocks).
  4. **The start day's move: up 1 ADR+, OR up 4%+ that is also 0.8 ADR+** (the user's Nov 15 choice in the session "Radar: MBGL
     / AVEX miss (Nov 12)", branch test/start4pct 3b9d5b4, never live until now: "yes lets go with 4% and 0.8adr", then "yes
     lets do that what you highlighed" for the version that keeps TTEK Oct 15). ZETA Nov 9 2026 (+4.5% on 2.2x, ADR 5.39% = 0.84
     ADR) is a start day; TTEK Oct 15 (+3.5%, 1.24 ADR) stays one. In the scan (start_raw, start_move) AND the live START DAY
     alert (radar/alerts.py find_start reads start_pct / start_pct_adr from launch.json rules): simulated +4.5% at 0.83 ADR
     alerts, +3.9% at 0.72 ADR does not, +5.5% as before. That session's 2-year numbers: 1,228 -> 1,319 start days, ran 20%+ 26%
     -> 27%, failed 32% -> 32%.
  Kept, the user's answers: the 3.5% ADR minimum to get on ("3.5% is fine"); no ADR rule to take a row off (buyouts like DV
  0.2%, BWIN, SLN 0.4%, BRZE 0.7% stay: told the user); your x; a newer start replaces the row. Not touched: Launches, the
  "start <date>" line under a launch (start_holds), the 1-lists. The page note on the Start days table and the rules
  workbook (two rows: "Start day: the move", "Start days table: no age limit, no 50 EMA rule, the newest start only") follow.
  Tested: `--regress` "every agreed example reads the same"; the full-market dry run (radar-tools launchdry, the Nov 13 close):
  the table 28 -> 205 rows (all 28 stay; new recent: ZETA Nov 9, OSCR Nov 9, TNGX Nov 10, DPC Nov 12; ages 0-4: 32, 5-10: 34,
  11-20: 31, 21-40: 36, 41-62: 14, older: 58, the oldest TXG Oct 20 2025 +343%, PEB Nov 7 2025, DNTH Jan 13 2026, NAVN Mar 26
  2026; 86 already on Launches); the page with 205 rows on desktop / phone, no errors, and the merged page with the live file.
  No 2-year check (a table rule; the move change brought its own numbers). Launches rebuilt after the push (picks.yml, 4:27 PM
  ET, the Nov 16 close, 158fe1d): Start days 194 rows (rules start_list_days 0, start_pct 4), BILL Oct 15 (+22.8%), ZETA Nov 9,
  RKLB Nov 9, WRBY Nov 5 on; the newest HUBS Nov 16. **First check Tue Nov 17**: the evening scan's
  launch.json start_days (~200 rows, rules start_list_days 0, start_pct 4); the START DAY alerts of the session (0.8 ADR ones).
- **LIVE (the user's "go live", Mon Nov 16 2026 ~8:17 PM ET, merge ed395a8): four more Start days changes.**
  1. **The note folds away** ("▶ What a start day is, and what takes it off the table", closed until clicked, remembered per
     browser like the other boxes; the user: "make it that i can minimize it as others").
  2. **The early line: off on a close 1 ADR+ under the start day's close** (L start_off_adr = 1). The user: QNT, VOYG, LSCC,
     MTCH "obvious failures", "we need better rule what takes it off". Measured on 750 start days (Nov 2024 - Sep 2026, 314 stocks
     incl. every stock of the Nov 16 table): 71% of the losers (never +5% in 40 sessions) close 1 ADR+ under the start close
     within 5 sessions, 24% of the winners (ran 15%+); 2 closes under the 21 EMA split them 65% / 24% (worse). Runners still on
     the table when they ran: 65% (the live rule alone 71%; the user's "2 closes under the 21 EMA, or under the 50 EMA when the 21
     is over the 50" 60%; half the start day's move given back 60%; 0.5 ADR 51%, chosen against: it took BILL Oct 16, HOOD, MU, LITE
     off before their runs). QNT Nov 6 (37.57, ADR 9.1%, line 34.17) off Nov 16; VOYG, PL, AEVA, ZLAB, TDW, AMLX Nov 16, RH Nov 6,
     OUST Nov 5, CENX Nov 13, SONO Nov 12. LSCC (-0.9 ADR) and MTCH (-0.5) stay until their next red close: the user asked
     twice; "back under both EMAs = off" was measured and refused (35 more runners lost: HOOD, NFLX, SPOT Apr 2025, TWLO; only 1 of
     them came back with a new start day before its run; it takes RKLB Nov 9 off).
  3. **Fresh start: the table shows no start day before Nov 1 2026** (L start_from; "i want to start it fresh and see how it does").
  4. **The late line: once a start has closed 2 ADR+ over its start close, one close 1 ADR+ under the 21 EMA takes it off** (L
     start_late_adv = 2, start_late_adr = 1; the user: "stock can go 30-40% up after start day, but later if it fades i dont want
     it on my list"). 629 start days with 80 sessions after: removed too early (a new high within 20 sessions) 26%, 8 days after
     the top, 3.7 ADR given back; 2 closes under the 50 EMA 30% / 10 days; 2 closes under the 21 EMA 46% / 7 days (the user
     asked; told them the 50 EMA has the better data, then found this one better still); trailing 3 ADR stop 26% / 9 days.
     MU Aug 8 2025 off Nov 20 (after the run), LITE Jan 20 2026 off Mar 6 (after +120%), HOOD Apr 2025 kept.
  Tested: `--regress` same; the full-market dry runs on the branch (the Nov 16 close): the table 194 -> 47 rows (135 before Nov
  1, 12 by the 1 ADR line, 0 by the late line that day); the page on desktop / phone, no errors, with the dry file and the
  merged page with the live file. Rules workbook: 2 rows. No 2-year check (table rules). **The portal's table is NOT rebuilt
  yet**: picks.yml ran twice after the push (01:17 and 01:28 UTC, both green, nothing saved: most likely the guard, Yahoo's
  evening bars without the Nov 16 close); the retry at 02:52 UTC (9:52 PM ET, 8d5bda0) SAVED: 47 rows, none before Nov 1,
  QNT / VOYG / PL off, LSCC / MTCH / ZETA / RKLB on. The portal shows the new table. Not touched: the START DAY alert, the
  "start <date>" line under launches, Launches. Scratch scripts of the measurements: this session's scratchpad only (decide.py,
  behave.py, late.py, late2.py, both.py: the numbers are in the rules rows).
- **LIVE (the user's "go live", Mon Nov 16 2026 ~10:00 PM ET, merge a7048c0): the Start days table's no-new-high window is 43
  sessions** (about 2 months; the user: "62 sessions is like 3 months"). Launches keep their 62 (L off_days); the table has its
  own L start_stale_days = 43 (stale(days=)). With the 1 ADR lines in place a tidy-up rule only: on 570 start days 62 removed 0,
  43 removed 4, none wrongly. `--regress` same; the merged page tested; the table unchanged tonight. Rules workbook: one row.
- **Measured for the user, no rule built (Nov 16 evening)**: LSCC / MTCH look-alikes in history. LSCC-like (ran, then 2 ADR back
  from the best close under the 21 EMA within 8 sessions): 16 cases, 50% made a new high within 40 sessions, only 12% of those
  after a fresh start day (MU Aug 2025 +73%, TWLO, WRBY ground back up; ZETA Nov 2024 -39%, CELH, TEM never). MTCH-like (small
  start, under both EMAs within 5 sessions): 50 cases, 82% new high (the base rate 83%), 71% without a new start day (MGNI, SPHR,
  GLXY, MSTR +47-66%). So "they'll make a new start day if alive" does not hold and no extra line was added; the 1 ADR lines
  handle a further fade. A "2 ADR off the top close under the 21 EMA" line was measured too (runners kept 62% -> 57%, loses MU and
  TWLO, takes LSCC off): not built.
- **Answered, no change**: why BILL is on Launches: its Aug 13 2026 launch (base breakout +5.4% on 2.1x, close 51.31, C), off
  Sep 23 (2 closes under the 50 EMA), back on Oct 15 by the reset start (3 lower highs since the Aug 13 top 52.60, range 5.5% ->
  3.3%, closed 46.92 over the last lower high 45.88 and both EMAs); without the reset rule it would be back Nov 2 (flag line
  49.50); new high Nov 9 = 61 sessions after the top (one short of the 62-session rule). BILL's only start day since Oct 1 was
  Oct 15 (+6.2%, 1.1x). Seen, offered, no answer: the reset's "3 lower highs" are weak for BILL (Aug 28 50.35, Sep 15 50.33 two
  cents lower with a higher Sep 3 50.89 between, Oct 12 45.88); the Launches row does not show "back on <date>" (off Sep 23 -
  Oct 15 is invisible).
- Data: radar-tools `long` re-run with BILL added (long_bars.json: 179 symbols).
- **The other session "Radar: MBGL / AVEX miss (Nov 12)"** (session_01PkbDaiSjzGPJPtohD3UF2C) is idle waiting for /wrapup; its
  0.8 ADR change is live through this go live (test/start4pct can be deleted).

## Status of the session "Radar: missing earnings on the list (Nov 16)" (Mon Nov 16 2026, from ~9:25 AM ET; session_01PkbDajdEo2jtmt5tLkCvv4; in progress)

- **LIVE (the user's "nvda earnings go live", Mon Nov 16 2026 ~11:20 AM ET, commit 29a7ffc): the Earnings tab has no market cap
  ceiling.** The user sent the Earnings Whispers card of the week of Nov 16 ("howcome most of these as an example $nvda missing
  from our earnings list"). Found: nothing broken; of its 83 names 15 were on our list, 17 are not in stocks.json, 51 fail the
  user's Earnings rules (37 on ADR 3.5%: HD, DIS, WMT, TGT ...), and NVDA ($3,925B, ADR 4.09%) failed only the `max_mcap` 2e12
  of scanner/settings.json "earnings": a ceiling agreed Nov 2 for the scans ("no $2T+ stocks"), copied into the Earnings rules
  on Nov 3, not one of the tab's six boxes and not in its "Who" text. The user: "fix that ceiling for earnings only". Removed
  from "earnings" only ("standard" keeps it: the scans, Watchlist, Launches, group rank unchanged). Tested on the Nov 13 close:
  NVDA is the only stock it adds (AAPL, MSFT, GOOGL, AMZN, TSM fail the ADR). earnings.yml run by hand 11:24 AM ET: 111 rows, 0
  errors, NVDA on Tue Nov 17 after the close. Rules workbook: the Earnings "Who shows" row. No page file touched.
- **Answered, no change**: POWL was on the list all along (Mon Nov 16 after close; in the "Under the 200-day SMA" table, -34.6%).
  When the Gainers rows showed with "4% + Above ORH-5min" (from live_history.json, which logs at 5%+): AVEX 9:37 -> the 9:40
  read, MOH 9:38, TSCO / POWL 9:52, FUN 10:31, BILL 10:34; the table is up to 5 minutes late and the opening range highs
  first arrive with the 9:40 read (levels.py runs after the 5-minute update from 9:36); the page polls every 90 seconds.
- **LIVE (the user's "go lvie both", Mon Nov 16 2026 ~2:00 PM ET, commits 0bc5e9d + f77e1b9): two changes. FIRST CHECK Tue Nov
  17 at 9:36 AM ET: neither has run on live prices.**
  1. **The movers every minute, 9:36-10:30** (the user, on the Gainers tab with "up 4%+ and Above ORH-5min": "is there anyway
     we can have every 1min after 5min close"; AVEX over its range high 12.64 at 9:37, shown with the 9:40 read). New
     radar/movers.py: the stocks up 2%+ (in the last full read or an earlier minute, or with an opening range today) are
     re-read and put on top of the last full update -> live.json with `fast_at` / `fast_n` (`saved_at` stays the full
     read's); radar/day.py `movers_once` runs it after fast_once in `movers_window` (9:36-10:30), then levels.py (so the
     opening range highs come at 9:36, not with the 9:40 read), and publishes both each minute. docs/index.html: the 20-second
     check runs to 10:30 (was 10:00); the live line adds "stocks up 2%+ from <time> (every minute to 10:30)". The alerts do
     not read the merged file (they keep live.json's full read and live_fast.json). Tested: stand-in quotes (under 2% not
     read, a stock that fell back still followed, an older quote ignored); a REAL read on a copy (radar-tools `moverstest`
     -> radar-data movers_test.json: 360 movers in 1.2 s); the page on desktop / phone, no page errors. NOT seen: the 9:36
     run reading ~300 opening ranges inside the minute, the step inside the day job, a minute tick running long. Check
     Tuesday: live.json has fast_at between the 5-minute marks from 9:36; levels.json saved_at ~9:36-9:37; the day job's
     later ticks on time. A stock that jumps from under 2% inside one 5-minute gap still waits for the next full read
     (offered: 1% in that window, not built).
  2. **Gap out of base: a 1x volume pace all day, 2x gets its own alert** (the user: "i want to drop 2x to 1x, and when it gets
     to 2x it can alert me"). KVYO Nov 16 2026: base top 22.20 alert 9:35 (right), 9:50 "OUT, vol 1.1x under 2x", then
     "1-min / 5-min high broke" (22.72) only at 12:30 with the volume at 2.0x and the price at 23.76: the rule "after 9:50
     a trigger needs 2x" held them (the user's chart: the break around 10:30; not confirmed: no minute record, radar-tools
     `replay` gives nothing for a stock not in launch.json `watch`). radar/alerts.py find_gob: the buy and the 9:50 check at
     `gob_rv` (1), the new key `:gob2x` "gap out of base: volume now 2.0x" at `gob_rv20` (2) from 9:50, only after a gap
     alert that did not already say 2x+; the "out at 9:50" words only before 9:50. Page legend and BOX_OF (gob2x), rules
     workbook. Tested with KVYO's numbers through find_gob (9:46, 9:50 at 1.1x and 0.8x, 10:31, 12:30) and the page load;
     no `--regress` (launch.py untouched), no Launches rebuild, no 2-year check (an alert threshold). The running day job
     keeps the old alerts.py until its next start: in effect from Tue Nov 17.
- **Explained, no change**: the morning breakout box (Alerts tab) is the 1-minute version of the same idea with its own
  rules (5%+, 1x, over PDH and ORH, above the 200 SMA / 50 EMA, 10 > 21 > 50; the user has saved no settings): MOH 9:38, CNC
  9:39, TSCO 9:52 (it crossed its range high 37.88 at +3.9%: the 5% rule made it late). Suggested: 4% there (the user's
  to save on the tab). Seen, not changed: a followed stock's plain breakout alert fired on a gap-out-of-base day (KVYO
  9:35) though the legend says it stays quiet; the 1-minute checks stop 12:00-3:00.

## Status at the end of the session "Radar: AZTA breakout alert (Nov 16)" (Mon Nov 16 2026 ~11:30 AM ET - Tue Nov 17; session_01PkbDajZLtZ51Kk895bqYFw)

**In one line: the retest after a launch re-read (4 parts, one go live), all on main, nothing left on a test branch. FIRST THING
NEXT SESSION: how many retest / reclaim alerts came on Tue Nov 17 (alerts.json), the first live session with a retest every day.**


- **LIVE (the user's "yes all looks good go live", Nov 17 2026; branch claude/practical-archimedes-o1zddh merged with main): the
  retest after a launch, and a broken base top is no breakout again** (scanner/launch.py only; radar/alerts.py and the page
  untouched; rules workbook: 4 rows). Found on AZTA: launched Nov 11 2026 (gap to 46.55, high 50.06, close 48.90) over its Oct 6
  top 46.41 (that day's open 43.76 = the body top); Nov 12 low 43.52 close 43.86, Nov 13 low 43.15 close 45.65; Nov 16 at 10:50
  the phone said "B breakout: Base top 46.41, nothing traded above it for 431 sessions, 1st breakout since the launch, leg 2".
  The user: "today was supposed to be retest", "we have rule ... retests previous highs body open and close, and closes above".
  1. **The launch's retest level = the highest top it closed over** (the 6- or 3-month high when it cleared it, bodies from 20
     sessions before that top; before: only the 20 sessions before the launch, AZTA 41.27-41.71). The higher level stays in play
     until the pullback's low comes into the 20-day level's zone (SPOT Oct 28 2026 536.74, ACN Oct 6 2026 192.58: their agreed
     retests are unchanged); a dip under the higher level that stays over the lower one is its undercut (CAI Aug 18 2026).
  2. **A retest counts from the day after the breakout** (L retest_first=1; was the 3rd session), **every day that touches the
     zone and closes over the body top is a retest** (the user on SPOT Oct 28 & 29 2026: "anytime it touches that area its called
     retest/holding, but i would need alert for that": the existing 3:45 PM "RETEST HOLDING" alert is per day), and a down day's
     own high counts for the 1.5 ADR pullback (APPN Oct 16 2026). The two other tests STAY (1.5 ADRs off the high since the
     breakout; a close 1.25 ADRs over the level first): the user asked "dont you think all 3 tests needed?", my answer: keep 2
     and 3. So GMAB Sep 24 2026 and CAI Aug 12-13 2026 are still no retest (the user had called them retests: not raised again).
  3. **A base top broken in the last 3 sessions by a breakout the scan counted** (the launch day, or a base breakout, closing
     more than 0.5% over it) **is no buy point**: no breakout / touched / gap-out-of-base alert on it (base_top leaves the last 3
     sessions out, so the old top came back as fresh). Kept: a poke that closed back under, a caution close, a failed breakout,
     and a close over a 20-day high inside a bigger base that was no breakout (APPN Oct 9-13 2026 keeps 39.67: my first build
     dropped it, the user: "october 12th and 13th was trying breakout last 20 days high inside same base"). The user agreed DOCU
     Sep 1 (65.25), AXTI May 27 (134.00), AEHR Feb 12-13 2026 (31.84).
  4. **Breakout undercut & reclaim after ONE close under the level**, when the day back over it keeps its low in the retest zone
     and is no retest by itself (the user on CAI Aug 18-19 2026: "maybe we call this breakout undercut reclaim, as we do for 21 ema
     undercuts"): added to another read of that day (CAI Aug 19 stays the bull flag breakout, AMD Jun 11 2026 the 21 EMA undercut
     & reclaim), the status itself otherwise (COHR Mar 9 2026); reclaim_level is set the evening of the 1st close under, so the
     "back over its breakout level" heads-up and the 3:45 PM alert fire that day.
  Reads the user agreed: AZTA Nov 12 & 13 retest; ACN Oct 7 retest, Oct 8 push; SPOT Oct 28 & 29 retest; APPN Oct 16 & 19; CAI
  Aug 14, 17 retest, Aug 18 undercut, Aug 19 reclaim; COHR Mar 9, AMD Jun 11. `--regress`: 53 lines differed, no agreed read lost;
  tools/expected_reads.txt rewritten at the go live. **No 2-year check: the user's decision ("i dont think we need 3#")**; I had
  recommended it (it adds retest days after every launch).
  **Launches rebuilt after the go live** (picks.yml, 7:28 PM ET Nov 16, the Nov 16 close): 213 launches; AZTA "Retest of the
  breakout level 43.76-46.41 held", no buy point, zone 39.68-46.41, no gap-out-of-base level; 8 rows read a retest that day
  (AZTA ZETA CYRX SG GXO MOS EL VSXY), 1 the breakout undercut & reclaim (DLTR). **First check Tue Nov 17**: the retest /
  reclaim alerts in alerts.json (how many a day now that every touch counts), and no "breakout" on a just-broken top.
- **Cleared up with the user after the go live**: "every touch" = every DAY: one retest alert per stock per day (the 3:45 PM
  "RETEST HOLDING", plus at most one "pulling back to its breakout level" heads-up); 3 days in a row = 3 alerts ("if it
  happens 3 days in a row we get three alerts": yes). Before: only the first day, or a later day on a lower low.
- **Test only**: nothing. AZTA Nov 11-16 2026 is in tools/examples.txt (added at the wrap-up; expected reads rewritten).
- **Told the user, no answer**: with "every touch", AZTA Nov 16 (low 44.32, close 47.22) also reads "retest held" and would send
  the 3:45 PM alert, though they had said Nov 16 was "just confirmation".
- **Open, agreed in principle, to build in a NEW session (Nov 17 2026): the reason on the after-the-open alerts.** MOH Nov 16
  2026 (+11.3%, the 9:38 AM morning breakout; CNC, HUM, ELV up with it: a Medicaid work-requirement delay) alerted with only
  its Nov 12 news. The user: "when i see breaking out and news there!!!", "news just adds extra layer", price and volume come
  first. To build, by code (no Claude): when a morning breakout / GROUP MOVE alert fires, look up that stock's newest headlines
  since the last close and put the reason on the alert. Checked with radar-tools `news` (radar-data probe_news.json): the
  Alpaca feed the code reads NEVER had the Medicaid story; Yahoo did ("Medicaid Work Requirement Delay Pushes Molina, Centene
  Stocks Higher", Barron's, under MOH / CNC / ELV), but probe_news.py does not record Yahoo's publish time: so Yahoo has to
  be a second source, and its timestamps captured first. **Asked, not done: a 2-3 month history check** of groups moving
  together under 5% at the open, up or down (3+ stocks of one theme / group gapping 2-5%: how often, how they did after, and
  whether a headline was out before the open); the pre-market group check is NOT to be built unless that shows an edge.
  Pre-market prices are not stored historically: use the open vs the prior close from the daily bars. Gap-downs are already
  covered like gap-ups for 5%+ gappers (Nov 16: 11 up, 104 down; the group line; the Theme event card).
- **Open, for another session (the user: "leave that alone")**: a GAP retest rule (AEHR Feb 12-17 2026: back to where it gapped
  from on Feb 11 and held; the scan only knows the retest of a broken base top).
- **Not done**: the alert text "nothing traded above it for N sessions" is still false for a top poked in the last 3 sessions
  (WRBY 31.75 over 31.50 on Nov 11 2026): offered, not taken up. long_bars.json now has 185 symbols (+ AZTA CDW GEO HNGE AMRX GCT WAT).

## Code grade next to Claude's (LIVE Nov 4 2026 ~6:15 PM, the user's "go live"; branches test/codegrade, test/lag50)

- **What**: radar/codegrade.py grades every gapper on the pre-market list (not only Claude's top 12), no Claude, at
  ~8:52 / 9:05 / 9:18 AM ET (.github/workflows/codegrade.yml -> radar-data codegrade.json + codegrade_log.json). The
  Pre-market tab's graded gappers show a **Code grade** column after Claude's Grade (≠ = they differ; hover for why).
  **Claude's grade stays the official one** (alerts, Launch laggards, the A/B news rules) for 1-2 weeks; then the user
  decides (codegrade_log.json holds each day's code and Claude grades; outcomes from the bars).
- **Stage** at the last close ("rising" = vs 5 sessions ago; one day only repeats the price test: NVDA May 5 2026):
  2 uptrend = 21 EMA > 50 EMA > 200 SMA, the 21 and 50 rising; 3 pullback = over the 200, the 50 over it, not 2;
  1 basing = over the 200 with the 50 under it, or under the 200 without 4; 4 downtrend = under the 200, the 21 under
  the 50, both falling (ALAB Nov 4: a breakdown though its 50 is still over its 200). Not the Trend column (10/21/50,
  day to day) and not the ★ stars: separate jobs.
- **Eligible** gap-ups at the pre-market price: 30%+ over the 52-week low, ADR 3.5%+, over the 50 EMA, over the
  highest **close** of the last 21 sessions (the user's #3; KD Nov 4 was 0.7% under it: "—", but the 9:32 EARLY alert
  caught it), a laggard at most 20% under the 200; **no cap over the 200** (leaders run 200-300% over it).
- **News** from the SEC filings since the last close (classify): F offering / ATM / delisting / reverse split / going
  concern (debt offerings aren't dilution: HCA); earnings from the Earnings tab, else the release (earn_fields);
  takeover / FDA / trial / contract vs market cap / executive change from the release.
- **Grade**: stage 2 / 3 A / B news = A / B; stage 1 / 4 now over the 200 = **⤴ reversal** A+ (A news) / A (B news);
  still under the 200 = **W** laggard watch (A / B news or earnings, the Launch laggards rule); else "—"; C / F as they
  are. A 5-8% gap one grade lower (YOU Nov 4: an A reversal on a 6.3% gap, +23.8%); 15x+ ATR over the 50 SMA at most C,
  10x+ flagged "extended" (the user's setting); A+ only in a leading / turning-up group (group_status, the backtest's
  rule). Gap-downs: the news grade, B -> A when a stage-2 stock gaps under its 50 and 200.
- **Backtest** (scanner/probe_codegrade.py, radar-tools `codegrade` -> radar-data probe_codegrade.json, every event saved
  with its levels for re-scoring; 4,727 gap-ups Apr 2025 - Nov 2026): A+ 14: held 64%, ran 20%+ 62%, r20 +16%, trade
  +18%; A / B didn't beat C (no estimates in history: the live side-by-side will tell); W crossed the 200 within 60
  sessions 77%, +6.5% the 20 sessions after; excluded groups worst (28%+ over the 200 -> later replaced by the ATR rule;
  under the 50; under the 21-day high); 15x+ ATR trade -7.2%; reversals in a leading group r20 +16% vs -3.5%.
- **(a) live**: the pre-market list (premarket_build.py prepare, used by Claude and the code) drops stocks under 30% over
  the 52-week low and gap-ups under the 50 EMA (Nov 4: 102 -> 59; FSLR, PLUG, CRWV, IREN, SPCX, RIOT, NVTS out).
- **(b) live**: a laggard launch must close over its 50 EMA (launch.py laggard, alerts.py laggard alert). Backtest:
  laggard-type gaps under the 50: 16, all broke the low, trade -5.2%; over it: 151, trade +2.5%, 72% crossed the 200.
  Regress: every example the same; Launches rebuilt (RRX, NCLH stay).
- Tools: radar-tools `codelive <asof>` (today's list -> codegrade_test.json), `runners` (today's 8%+ gainers vs the
  21-day closing high), `reltext`, `earntest`.
- **Open**: (1) after 1-2 weeks: compare the log (code vs Claude, by outcome) and decide; (2) a "W crossed the 200"
  alert (where the laggard edge is); (3) a double beat (revenue and EPS) may deserve B (KD Nov 4 read C); (4) no
  follow-up alert when KD cleared its base high after the 9:32 EARLY heads-up: answered Nov 4 night (it fired; the log
  hid it: see "KD missing from the desktop alert log"); (5) stars x code grade, once
  there's live history; (6) HELE missed the 700K average volume by 3%: the user's call; (7) Nov 4's codegrade.json /
  log entry was made after the close (the first test run).

## The user's ground rules

1. **No change without an explicit go.** Explain the reasoning first and get it agreed ("dont do anything without
   finalizing rationale"). A question from the user is not a go.
2. **Test before live.** Work on a test branch (`test/...`), replay the agreed examples (`tools/replay.py --regress`),
   report, then wait for the go. Pushing to `main` is going live: only when the user says so ("go live").
   **The 2-year check only when the user changes a main pattern, a buy point or adds a new rule — and ask first, with
   the reason it's needed** (Nov 1 2026: "next time ask me, and tell me the reason why we should do it"). Not for
   thresholds of the list, the table, alerts or the off-list rules.
3. **Never change the Launches design while fixing something else** (the Watchlist, the portal...). Say what a change
   would touch before making it.
4. The ntfy topic is private: it is in the `NTFY_TOPIC` secret only. Never write it in a file, a commit or a message.
5. Don't work around a permission denial; tell the user and let them decide.
6. Commits: end with the attribution lines the session gives; no model names anywhere else.
6b. **The rules workbook follows the code**: any change to a rule, a threshold, a buy point, an alert or the grading
   updates `rules/make_rules.py` and re-runs it (`python3 rules/make_rules.py`) in the same commit, so
   `rules/scanner_rules.xlsx` and `rules/SCANNER_RULES.md` always match what is live (the user, Nov 2 2026).
7. How the user trades: enters only on a break of the 5-minute opening-range high; stop under the day's low. Launches
   (and catalyst launches) are for tracking a stock and finding the best entry: a breakout or a pullback.
8. How the user talks: short numbered feedback with dates, prices and chart screenshots. Answer point by point with
   dates and prices, in plain words, and say which of their reads the code matches and which it doesn't.
(CLAUDE.md holds a word-for-word copy of these rules and of the short commands: change both together.)

## The system

| What | Where |
|---|---|
| Portal | https://goattrader40-lgtm.github.io/radar-close-snapshots/ (docs/index.html, GitHub Pages) |
| Watchlist (nightly) | scanner/run.py → setups/latest.json (1-EP/GAP, 1-UPDAY, 2-POOL); 3-SETUPS right after by scanner/launch.py --watchlist (scanner.yml only; a Follow-button rebuild keeps the evening's setups3) |
| Launches (nightly + picks) | scanner/launch.py → setups/launch.json; the user's picks: setups/picks.json |
| Live alerts (phone, ntfy) | radar/alerts.py (every 5 min, 1 min at the open/close via radar/fast.py), radar/eod_alerts.py (after the close; also the 3-SETUPS Ready list as one text file) |
| Desktop alerts | the portal (docs/index.html) while it is open: launches, breakouts, and every 3-SETUPS trigger |
| 📈 Morning breakouts (portal only) | radar/alerts.py check_morning (any stock, 9:35-10:30 by default); the user's settings and + Filters: alerts/morning.json on main (Alerts tab, Save); replay: radar-tools `morning` |
| Opening ranges (+ Filter "Above ORH" 1min / 2min / 5min) | radar/levels.py from day.py's live updates and minute reads, 9:31 on -> radar-data levels.json (stocks up 2%+) |
| Data branch | `radar-data`: stocks.json, long_bars.json, probe_catalyst.json, alerts.json, gradelog.json |

GitHub jobs: `scanner.yml` (4:40 PM ET: Watchlist + Launches), `picks.yml` "Follow picks" (rebuilds Launches; run it
after a change goes live), `radar-day.yml` (live alerts), `premarket.yml`, `radar-tools.yml` (cmd `catalyst` = the
2-year check → radar-data probe_catalyst.json; cmd `setups3` = the 3-SETUPS check, incl. the Ready opening-range trades →
radar-data probe_setups3.json; cmd `setupsdry` = tonight's 3-SETUPS without saving → radar-data setups_dry.json;
cmd `launchdry SYM ...` = the Launches build with test picks; cmd `long SYM ...` = daily history → radar-data
long_bars.json). The evening scan can be re-run by hand (scanner.yml, workflow_dispatch) to rebuild 3-SETUPS. A new
dispatch cancels a pending one in the same group. The run logs are not readable from a session (403): errors go into
the published JSON.

The 8:45 AM pre-market grading is a scheduled task (trig_01EhkhyMeC5yC4H4sFxsqUVQ) that runs in its own session
(session_01PkbDanMRsWYc9PUezGyf1N);
nothing else uses Claude.

## Checking a change

```
gh workflow run radar-tools.yml --ref main -f cmd="long GMAB ANF RPD SPOT ACN SMCI ATRC CAI NTSK APPN VEEV ZS ARM TTAN LIFE GDDY INFQ HLIT"
git fetch -q origin +refs/heads/radar-data:refs/remotes/origin/radar-data   # after ~2 minutes (a shallow clone needs the full refspec)
python3 tools/replay.py --regress                    # every agreed example vs tools/expected_reads.txt
python3 tools/replay.py ARM 2026-03-25 2026-05-29 --pick --all     # one stock, every day
gh workflow run radar-tools.yml --ref <test-branch> -f cmd="catalyst"   # the 2-year check (~5 min), then
git fetch -q origin radar-data && git show origin/radar-data:probe_catalyst.json   # buy_points.current per signal
```
Only rewrite tools/expected_reads.txt (`--regress --write`) after the user agreed the new reads.
Testing a portal change (from the Nov 3-5 sessions; details in the archive): serve docs/ with `python3 -m http.server`
and drive it with Playwright (it loads radar-data from raw.githubusercontent.com); compare with main's page served the
same way, and test with the real live data files too. Cloud sessions can't reach github.io, Yahoo or Nasdaq (proxy
403): data work goes through the radar-tools jobs. Other sessions edit docs/index.html the same day: fetch main
before merging and re-test the merged page.

## What the user agreed (Launches), with their examples

- **Launch day** (all of these): opens up, closes up 5%+ in the top half of the day's range on 1.5x+ volume, over the
  200 SMA and at most 28% over it the day before, 30%+ over the 52-week low, liquid ($10+, $20M+ and 600K+ shares a
  day, ADR 3.5%+). A close in the lower half is no launch.
- **Power day** (Nov 1 2026): volume 4x+, an **8%+ gap and a 10%+ day** (was 10% / 15%); may start up to 50% over the
  200 SMA and close in the lower half if it keeps half its gap ("faded") (ARM Mar 25 2026: a 9.9% gap, +16.4% on 6.1x,
  48% of its range: now a faded power day). A power day is never replaced by a later day: the days after it are its
  continuation (INFQ May 21 2026, not May 22; HLIT May 22, not May 26). Another stronger day can still replace a
  regular launch (APPN Aug 5 → Aug 7).
- **Catalyst launch**: a 5%+ gap on earnings / news, closes up, still in the gap, over at least its 1-month base, and
  **2x+ volume** (Nov 1 2026).
- **Reversal day** (Nov 1 2026, GDDY Oct 30 2026): opens under the day before's close, closes up 8%+ in the top half of
  its range on 2x+ volume, over its **1-month high by the wicks and bodies** (the previous 20 sessions' highest high:
  a regular breakout, the close over it), with the same 200 SMA, 52-week-low and liquidity rules. Tagged "reversal";
  it never blocks a regular launch. The live job alerts it the moment it meets the rules (the top half checked on
  today's 1-minute chart); the close confirms it. The 2-year check: 41 reversal launches, launch-day ORH trades 67%
  won, median +3.4%, 47% ran 20%+, 17% ran 50%+ (all launches: 45%, −1.1%, 28%, 7%).
- **Off the list** (Nov 1 2026): **3 closes in a row under the 50 EMA** (after 2 the launch moves to the **50 EMA
  undercut tab** under the Launches table; the next session has to close back over the 50 EMA, which puts it back on
  Launches; the reclaim (low under the 50 EMA and the open, the close back over it in the upper half of the day) is the
  **50 EMA undercut & reclaim** entry, no depth limit: AEHR Mar 31 2026 after Mar 27 & 30); **62 sessions from its highest point without a
  new high** ("a $60 high 5 days ago with the stock at $55 today counts from the $60 day"; picks too; once off it stays
  off); **ADR under 3.2% after the launch** (a launch day still needs 3.5%; TECH 0.2% after a buyout-like gap, BRZE);
  a newer launch of the same stock; the user's ✕ (that launch and older ones; a launch on a later day shows again).
  **No 120-session limit.** The first close under the 21 EMA is only the exit signal.
- **The Launches table**: Status at most 3 lines (click for all), an ADR column between Status and Base day (red under
  3.5%); a ✕ on every row; the rules box "What counts as a launch day, a power day, and what takes a stock off the list".

- **Leg**: a close more than 0.5% over a base top is a breakout and a new leg (CAI Oct 27 2026, 2.4%). A close over it
  but within 0.5% is a **breakout with caution** (still a trigger); its follow-through starts the leg: within 3
  sessions it opens over the day before's close and closes more than 0.5% over the top (ARM Apr 17 → Apr 20; GMAB
  Aug 14 → Aug 17; ATRC Aug 7 → Aug 11). A close under the top is no breakout. Breakouts a few days apart are one leg
  (RPD Oct 22 / 23). A flag break or a pop is an entry in the base, not a leg.
- **Tops** are named by their reach: a 1-, 3- or 6-month high. A bigger base's high right above is named (VEEV Oct 9:
  out of its 1-month base 291.40 and the falling line, closed 296.13 under its 6-month high 296.24: a double
  breakout, not out of the main base; RPD Oct 22 out of 13.87, its 6-month high 14.80 broken the next day).
- **Retest, as agreed Nov 16-17 2026 (AZTA; details in that session's status)**: after a launch the level is the highest top
  it closed over (AZTA 43.76-46.41, its Oct 6 top), the 20-day one once the pullback reaches it (SPOT Oct 28, ACN Oct 7); from
  the day after the breakout; every day that touches the zone and closes over the body top is a retest with its alert (SPOT
  Oct 28 & 29, APPN Oct 16 & 19, CAI Aug 14 & 17); one close under and back over, the low in the zone, is the breakout
  undercut & reclaim (CAI Aug 18-19, COHR Mar 9); a top already broken is no breakout again (DOCU Sep 1, AXTI May 27).
- **Retest** of the breakout level (bodies or wicks): after a real pullback, the low back at the level, the close over
  it and the 21 EMA, and over the 10 EMA unless the low tested the 21 EMA (ARM Mar 30 no; Mar 31 yes + 10 EMA; Apr 7
  yes + 21 EMA; GMAB Oct 2, ACN Oct 7, CAI Sep 3 / Sep 10, SPOT Oct 28, ANF Oct 23). The stock must move up the first
  sessions after the breakout before a dip counts (GMAB).
- **Push** out of the 21 EMA with a gap after the retest's touch (ANF Aug 21, ACN Oct 8); none while still under a
  flag's falling line (ARM Apr 8). (CAI Oct 9 is a breakout undercut & reclaim, below.)
- **Breakout undercut & reclaim** (Nov 1 2026, the user's name; CAI Oct 9 2026): after a breakout that first advanced
  (a close 1.25+ ADRs over the level: not AEHR Feb 20 2026, its Feb 11 breakout fell right back, the base stayed
  valid), **2+ closes back under the breakout level** (the broken base's top, its bodies) holding over the 50 EMA, then
  the close back over it within 5 sessions: an entry, once per breakout (CAI: under 28.01 Oct 6-8, closed 29.70 Oct 9).
  One close under and back is a retest (GMAB Oct 2, ACN Oct 7). Alerts: back over the level (heads-up), from 3:45 PM
  holding into the close.
- **Bull flag** (named so Nov 1 2026; the user's definition: the pole, then a descending channel right after its high,
  volume drying up, then the momentum surge out of it; APLD Mar 31 - May 4 2026 is the textbook one): the top at least
  a 1-month high; the pole = a run of 4+ ADRs made by the trend into it, not one gap day (a high that only retests an
  older top is the 2nd try of a flat top, no pole: ARM May 6); the high and 4+ pullback days (5 candles: the breakout
  comes 5 to **22** sessions after the top; AEHR Apr 2 on the 21st); 1.25–4 ADRs deep; 3+ lower highs; **a descending
  channel: lower highs on at least half and lower lows on more than half of the days down to the flag's low, no higher
  swing low after it** (not ACN Oct 29 2026: 2 lower lows of 4, a pause and a V); **the drift down at or under 1.1x
  the 20-day average volume** (APLD 0.82x, AEHR 0.81x, your flags 0.71-1.04x; not APPN Sep 2026 1.17x, ARM Mar 26-30
  1.75x, VEEV Aug 28-31 1.62x); riding the 10 or 21 EMA (3+ days within an ADR: kept, it takes none of the user's
  flags off); no close half an ADR under the 21 EMA **unless the falling line is intact, the line is in the upper half
  of the pole and the drop came on light volume (no day down half an ADR+ on 1.3x+): then closes under the 21 / 50 EMA
  are allowed and the breakout says "closed under the 50 EMA during the flag (dates): you judge the grade"** (AEHR Mar
  26-30 2026, its line 40.65 broken Apr 2; not APPN Sep 8 2.4x, not LIFE Sep 16-17 2.1x / 2.3x); a controlled pullback, no violent drop (a gap down of 0.7+ ADR closing 1+ ADR
  down on 1.3x+ volume: ARM Apr 27–28 and May 7, ZS Oct 5: no flag). The line runs through the highs; a try that
  pokes half an ADR+ over it and closes back under is a failed try, the line stays (ARM Apr 10 failed, Apr 13 broke
  at 149.00). Entry: the close over the line and the 10 & 21 EMA; the alert fires at the line during the day. Within
  0.5% over the line = caution: the line stays the next trigger one more day, then the base top (TTAN Oct 30: 84.26
  over 84.00, next 84.28, then 87.75). Tag: the volume dried up the 2 days before (ZS Oct 21). Examples: SMCI Jun 28
  2023, CAI Aug 19 / Sep 14, VEEV Sep 23, ZS Oct 21, TTAN Oct 30, ARM Apr 13. A flag inside a base is an earlier
  entry (more room, less risk); the base can still turn into another pattern.
- **Bull pennant** (Nov 1 2026, a symmetrical triangle; ARM Mar 25 - Apr 13 2026): the same pole, length, depth and
  rules, but converging: lower highs and a **higher swing low after the first low** (ARM: highs Mar 25, Apr 1 stepping
  down, lows Mar 30, Apr 7 stepping up: contraction, then the expansion out of it), the volume after its first low at
  or under 1.1x. The trigger is the falling upper line: "Bull pennant breakout" (ARM Apr 13 at 149.00).
- **21 EMA retest** (entry in the base): 5+ days into the base and 1.25+ ADRs off its high, a controlled pullback (the
  3 days before not all up, the closes held over the 21 EMA); the low under the 21 EMA and under the open, the close
  back over it in the upper half of the day. Once per pullback (TTAN Oct 29, ARM May 18, NTSK Oct 1, VEEV Sep 21; not
  VEEV Sep 15, a gap down after 3 up days).
- **21 EMA undercut & reclaim** (strong): the same after 2 closes under the 21 EMA by less than half an ADR, the
  momentum traders' exit (SMCI Jun 27 2023, ANF Oct 1, RPD Sep 30; not APPN Sep 14, 1.3 ADRs under = a breakdown; not
  CAI Oct 5, it opened at its low).
- **Tight days** under the base high: tight bodies close to the high, stacked, not a staircase up, not drifting down
  (ANF Oct 15–16, CAI Oct 22–26, ARM Apr 14–16). Tight at the high on the right side = a breakout coming; tight days
  drifting down = a flag forming.
- **Double breakout** tag: a squeeze under a falling line from the base top with higher lows, broken with the top the
  same day (ARM May 20, ATRC Aug 7, CAI Oct 27, VEEV Oct 9); not when the day before was already at the top (GMAB
  Oct 23, a U shape) or a flag already broke that line (ARM Apr 17).
- **3rd try** (ascending triangle): the high is the 1st try, a 2nd **within 0.2 ADR** of it after a real pullback (CAI
  Oct 16 2026 at 0.23 ADR under was no try), then a shallower pullback: the 3rd try usually breaks out (ARM Apr 24 /
  May 6 → May 20); not a falling wedge (VEEV Aug) and not a 2nd try that breaks out right away (a U or flat top: GMAB,
  ACN, ARM Apr 16–17). **The try day has its own heads-up read** (Nov 1 2026): "the 3rd try of the top today" for the
  main base's top (CAI Oct 21 2026, 32.89 after Sep 23 and Oct 6); a smaller base's top tried under the main base is
  named as such with the bases above (RPD Oct 8 2026: its 1-month top 13.25, the main base Aug 27 and the bigger base
  Aug 11 above).
- **Pop out of the consolidation** (entry in the base): ANF Oct 5.
- **Status**: "In the base" once the stock is 1.25+ ADRs under its high.
- **Watchlist flag** (scanner/run.py our_flag) follows the same flag rule (bull flag or bull pennant).
- **Gap out of base** (Nov 1 2026, live): a Launches stock that closed at or under its base high (the base top or an MSF
  pivot; not a flag line or a pop) and opens above it; only with ADR 4%+, 600K+ shares and $30M+ a day (20-day
  averages), market cap $700M+. Phone alerts: the gap (volume pace 1x+), the 1-minute and the 5-minute opening range
  high broken (with the stop, the range's low, and the risk in ADRs), and at 9:50 the volume check (under 2x = out); a
  trigger after 9:50 needs 2x+. Its plain breakout alert stays quiet that day. The portal tags the row.

**Agreed Nov 12-13 2026 (the list ON / OFF, the start day, the new alerts; all live; the user's words in tools/chart_examples.txt):**
- **A regular pullback stays on**: AMD May 19 2026 ("its not breakdown of the chart, its regular pullback"): no close under
  the 21 EMA, light volume, the 10 > 21 > 50 EMA rising.
- **End of cycle = stalled at the highs + a violent break; off on the close under the 21 EMA** ("higher highs very close each
  other", "6th october doesnt really count bcs it stalled right away", "volatility goes up.. but doesnt make [progress]..
  distribution days"): AMD warning Jul 1, off Jul 7 2026 ("july 7th is good take off!!!"); warning Oct 8, off Oct 12 ("8th and
  9th october end of cycle.. 12th october you take this off the list"). The warning shows in the status ("would be great in
  status bar").
- **The start day = the first strong close over the 21 EMA after a downtrend, the 50 EMA is the confirmation**: RKLB Nov 9
  2026 ("clear downtrending stock, november 9th was a start point upward.. and 10th confirmation!!!"), TTEK Oct 15 only
  ("nov12 nothing, its wild move down and up bad"), LSCC Nov 9, AVGO Nov 10, AMD / ZM / SONO Nov 11; NAVN none ("just
  consolidation"); a gap that closes at its low is no launch (LUNR Nov 12: "big big red candle").
- **The new trend start after a reset**: AMD Sep 8 2026 ("after climax stock need time to reset the energy.. keeps making
  lower high.. september 3rd was a sign.. volatility contracting since july 14th, every time swing becomes smaller").
- **The ADR minimum is tested on the 3-month high ADR** ("amd never was 3.4% adr stock.. its beta name"); the minimum itself
  is unchanged.
- **Range stocks are no candidates** (ANET Apr-Oct 2026: "too much whiplash to 21ema and 50 ema.. not nicely trending up";
  BETA: "nov3 was launch but.. now it fell back to range"): a note, the stock stays.
- **On a list stock the strong close back over the 21 EMA is the 21 EMA undercut & reclaim** (AMD Jun 11 2026), not a "pop".
- **The 2nd higher low is an end-of-day trigger and can sit on the 21 EMA as well as the 50 EMA**; **the falling-range
  breakout "its good alert"** (daytime).
- "as i review charts and etc, you can make it better later correct?": yes, each correction goes to the test branch first.

## What the user agreed (Watchlist 3-SETUPS, Nov 1 2026)

- The Tight / PB 21 / PB 50 screens are gone. Every stock on 1-EP/GAP, 1-UPDAY and 2-POOL is read by the Launches
  engine like a pick from the day it came on its list (launch.s3_read, the same code the 2-year check uses):
  **Triggered today** (base breakout, flag break, pop, 21 EMA retest or undercut & reclaim, retest held, push),
  **Ready** (its trigger within **0.7 ADR** over the close, in a base of 5+ days or tight 2+ days), **Setting up** (a
  flag forming, a 21 EMA pullback set up, near the retest zone after a real pullback).
- In: liquid with an **ADR of 4%+** (3.2%+ once on). Off: as Launches (50 EMA, 62 sessions, ADR under 3.2%) or the
  user's ✕ (back only when it comes on a feeder list again). No size limit. A stock 3-SETUPS took is "promoted" in
  run.py (not deleted from its feeder list for 15 days without a setup).
- Alerts: **desktop notifications for every trigger during the day; the phone gets only the Ready list once after the
  close, as one text file** (no Ready phone alerts during the day). A stock also on Launches alerts from Launches.
- The Watchlist table: Why next to Grade (every list); on 3-SETUPS the Launches status in grey under Why.
- The check (Aug 2025 – Oct 2026, the feeder lists rebuilt from daily bars): Triggered today 6,713 buy points, 28% ran
  20%+, 42% failed (Launches buy points 23% / 42%); Ready bought at the trigger the next day 27% / 51%. **Ready bought on
  the next day's 5-minute opening range high is about breakeven** whatever the exit (stop at the 5-minute low: 10% won,
  −0.1% average; the day-low stop: 16%, −0.2%; half at +2R: 30%, −0.1%) and whatever the filter (theme, volume
  building, age, 52-week high, depth, distance, ADR: all −0.9% to +0.3%). The user keeps the Ready list as it is: a
  shortlist, not a buy-everything list.

The 2-year check after these rules (Oct 31 2026; ran 20% = 20%+ within 20 sessions, failed = closed under the entry
day's low within 5 sessions): base breakouts 1,057 (22% / 33%; within 0.5% 17% / 45%; half an ADR+ over 24% / 24%),
double breakouts 117 (24% / 30%), 3rd try 32 (28% / 31%), flags 428 (21% / 39%; within 0.5% of the line 17% / 47%),
21 EMA retest 417 (23% / 46%), undercut & reclaim 98 (26% / 47%, 56% ran 10%+), retests 629 (24% / 49%), pushes 174
(26% / 50%); all 2,985 buy points (22% / 41%).

## Open items: the to-do list for the next session (each needs the user's go)

**Keep in this file until the Nov 18 check-in has run**: the section "Code grade next to Claude's (LIVE Nov 4)" (the
Nov 11 and Nov 18 code-grade check-ins read HANDOFF.md); after that, /wrapup moves it to the archive.

- In the status section "Radar: MBGL / AVEX miss (Nov 12)" above: the coil alert to look at later (the user's
  request), the pre-market blind spot 9:10-9:30, young listings (52-week low / 200 SMA), the code grader's
  "no daily bars" bug.
- Moved to the archive on Nov 17: still open there: **the first checks of the Mon Nov 16 evening scan were NOT done** (the
  1-list changes: `first_day` and the first-day lows on 1-UPDAY, `pre_close` on 1-EP/GAP with VIR / NXT leaving, what joined
  1-EP/GAP at 2x volume, a first real x, "inside day" on the Watchlist rows, Days 21H / 62H in the session); the 15 trading
  days off 1-UPDAY too (the user to decide); a stock on 1-EP/GAP not shown on 1-UPDAY as well, Download for TradingView on the
  50 EMA undercut table, one combined search table on Launches (offered); from the TOST review: Days 21H from real closes,
  the day's alerts on the Launches row, one read for the Watchlist 1-lists and Launches (the retest after a close under the
  level is now the one-close breakout undercut & reclaim, Nov 17); the GLOB-type alert (offered); EMBJ off Launches on
  Yahoo's 1 bar (to check); the Start days fail rule there is overtaken by the Nov 16 Start days session
  ["Radar: 21-day / 62-day high columns (Nov 13)"].
- Moved to the archive on Nov 17 (the complete copy of the section the Nov 13 pointer below names): nothing new to add to that
  pointer ["Radar: full portal review, build continued (Nov 12)"].
- Moved to the archive on Nov 14 (the section the line above calls "above"): still open there: the coil alert to look at
  later (nothing alerts on a coil; the user's request), the pre-market blind spot 9:10-9:30 (MBGL Nov 12), young listings'
  52-week low / 200 SMA (AVEX, MBGL), the code grader's "no daily bars" bug; done since: `coil` on the Launches rows (and
  Other entries / inside day there, Nov 14) ["Radar: MBGL / AVEX miss (Nov 12)"].
- Moved to the archive on Nov 13: first check: the user's first morning with Scan (which list / filters they use)
  ["Radar: watchlist/launches scanner tab (Nov 12)"].
- Moved to the archive on Nov 13: still open there: the Trend 50 EMA "rising" rule (the user is thinking; "2 days in a row"
  offered) and the code grader's STAGE to one day or not; a 2-year check of the stars under the new rule (offered); one
  headline parser instead of two; FIGR's buyback headline; HUBS labelled "Earnings (headline)"; the "Pre-mkt gap" rename /
  hide (no answer); to check: earnings.yml at 7:05 / 7:35 / 8:35 / 8:50 / 9:05 AM and stocks.json tr[4]
  ["Radar: Earnings reader fix + pre-market grading (Nov 4)"].
- Moved to the archive on Nov 13: still open there: the chart reading to review with the user (warnings too quick?, the
  range notes, AMD Jul 10 2026, ATRC Jun 26 vs the user's Jul 24, the 1.5 ADR attempt zone); tools/expected_reads.txt NOT
  rewritten (209 lines differ); the START DAY alerts' first live day (alerts.json `:start` keys, how many); END OF CYCLE
  WARNING blocking buy alerts (the user did not answer); the alert / eod_alerts texts; tech homes to ask (SITM, TTD, AMBA,
  SIMO); "E1 Earnings tab" defined twice in rules/make_rules.py; the wire reading for a report without a filing (HBM);
  the charts not replayed; tools/chart_examples.txt is the user's charts in their words: read it before chart work
  ["Radar: full portal review, build continued (Nov 12)"].
- Moved to the archive on Nov 12: still open there: the user's answers they will "compile and provide all at once" (go
  live or not for test/cleanlaunch, the 135-row list, more charts of each kind); tools/expected_reads.txt not rewritten
  (188 differing lines); AEHR Jan 16 2026 still read as a launch attempt (the user: not one) ["Radar: full portal review,
  build (Nov 11)"].
- Moved to the archive on Nov 12: still open there: the "Above 21-day EMA" tick box (offered, no answer); to check: c200 in
  stocks.json and vs 200 SMA moving in the session; KLIC / ASX / SIMO in their themes after the next theme build; SITM and
  FSLY without a theme (the user to say) ["Radar: pre-market scanner vs EMA columns (Nov 11)"].
- Moved to the archive on Nov 11: still open there: the alert changes agreed Nov 6 and never live (branch test/brkvoice:
  short breakout titles, a "back over its level" alert, the end-of-day pop-up of what didn't hold; and the unanswered "then
  rest see where the volume is"); the morning breakouts' +5% rule made TRAX / TGTX alert late (suggested: a week of both
  replays); test/morningcheck (after_alert) waits for a go; asked Nov 10, no answer: a stock without a 200 SMA in the
  morning alert, the morning replay every day, a longer alert window; alerts/morning.json and premarket/rules.json are not
  saved on main ["Radar: alert sound volume (Nov 10)"].
- Moved to the archive on Nov 11: still open there: the build-list items not built yet (the one rulebook: alerts and page
  ask launch.py; every name on a launch day; the scan naming the tight-day EMA hold; "leader" in place of lone wolf; join
  at 0.6 / leave under 0.45; a weekly new-pack finder); what is built on test/cleanlaunch from Nov 10 (no entry under the
  200 SMA, no limit over it, power day 3x, the alerts' 1x volume pace / 0.7 ADR risk / tight-day EMA hold: tested only
  with a stand-in for the day's low); blind test 1; the Nov 10 decisions (yes: "W crossed the 200" alert, a double beat =
  B, a news run ~9:25; dropped for good: the momentum cutoff, the power day's +10%, HELE's 700K, the official open from
  Alpaca, the layouts export / import, the FCF backtest; VCEL: don't change); blocked, the user to decide: saving their
  recovered words of the Oct 26 session into the repo ["Radar: full portal review (Nov 9)"].
- Moved to the archive on Nov 10 (evening): still open there: news for stocks that move after the open (not only 5%+
  gappers), the morning breakouts on the phone (later) ["Radar: earlier news + morning breakout alert (Nov 9)"].

**Decided by the user on Nov 10 2026** (the status section "Radar: full portal review (Nov 9)": the yes list, the
items dropped for good, VCEL): read it before raising any item below.
- Moved to the archive on Nov 10: if the user saved Graded gappers rules, premarket/rules.json on main and the 8:45
  task's prepare line prints "rules" (never checked) ["Radar: TradingView import replaces my list (Nov 7)"].

**Still open in sections moved to HANDOFF_ARCHIVE.md on Nov 8** (pointers, not copies: the archive section is in
brackets; some may be done or overtaken since, so check there before raising one):
- First things to check Monday Nov 9, besides the Nov 7 list: the 4:25 PM scan from the day job, the power day / EP
  open rule in the job's alerts, today's triggers live on the rows, Tuesday's 5 AM labels ["Radar: work session
  (Nov 6)"]; the 8:05 / 8:35 news runs, pmnews.json, the News column by ~8:07, the 8:45 code run's headline log
  ["Radar: pre-market news for every 5%+ gapper (Nov 6)"].
- To confirm with the user: a report from before the last close (VCEL) now reads "After earnings", news C, in the
  code grader, while the user had said "don't change anything" about VCEL: keep it? [same Nov 6 section]
- Offered, not decided: "Show lone wolves" unticked hides new launches (tick it, or drop the filter and keep the
  tag); a "Now" column on the ★ Launch watch after 9:30; an EPAM-type stepped-down power day ["work session (Nov 6)"].
- Offered, not decided: event news keeps a gapper the filters drop (FLY); the "before the last close" rule for the
  8:45 task (VCEL); headline reads to watch (OBX, posts on X) ["pre-market news for every 5%+ gapper (Nov 6)"].
- The user agreed to look at it later (not built): the alerts decide "triggered" with their own copy of the rules,
  the engine at the close with its own; names and conditions can differ (MANE Nov 6) ["One pullback heads-up"].
- The Launch laggards tab is left out of the end-of-day box (the user's call); EAT / PRGO got a live retest alert
  the scan didn't (seen, not acted on) ["End of day = today's buy-point triggers only"].
- "W crossed the 200": keep W names 60 sessions, alert on the first close over the 200 and put them on the
  Watchlist / Launches that day (proposed, the user's call) ["Phone alerts crashed after 9:34", "The morning"].
- Earnings reader: URGN one product's revenue and guide, ADEA's cut outlook read "reaffirmed", DUOL EPS bases;
  VRDN, LQDA, PCVX, TNGX without revenue ["Earnings reader fix", "Earnings tab, second round"].
- Waiting for the user's go: in premarket_build.py finish, an A/B without a downloaded filing or release drops to C;
  the grader gets the filings since the last close; DUOL's Nov 4 A in gradelog: correct or keep ["Earnings reader fix"].
- Offered, no answer: Export / Import of the table layouts between devices ["Radar: work session (Nov 4)", Nov 4-5].
- Launches Group tick-box filter (test/grfilter, conflicts with main: rebuild first); Base day from the base's high
  (MRNA); where ACN's "135 off the 52W high" came from ["Radar: work session (Nov 4)", Nov 3-4].
- Alerts: the 1 ADR breakout-level confluence distance; the retest zone at 0.2 ADR (RPD Nov 3, explain first);
  GROUP MOVE at 3 stocks for themes of 20+ if noisy ["Status at the end of the alerts session (Nov 3 evening)"].
- Stars: rename / caveat ★★ ("promising, not proven"); an earnings star (needs 2 years of earnings dates); the
  3-SETUPS alert text ["the last session (Nov 3 evening - Nov 4)", "the session before (Nov 3)"].

New from Nov 5 (alerts / pre-market day, session_01PkbDakDe1EUNP5wQZf4wMH), unanswered (the power day's +10%, the official
open and the FCF backtest were dropped for good by the user on Nov 10):
- **TREND triggers and the W (200 SMA) alerts in GitHub's job** (radar/alerts.py), so they reach every device like the
  other alerts; today they come only from the open portal page. Offered, not decided.
- **Earnings tab, EPAM Nov 5**: EPS -26% (GAAP) on the tab vs Claude's adjusted beat; check the reader pairs GAAP with
  GAAP and adjusted with adjusted.
- Check-in still to run: Nov 18, 5:40 PM ET (code grade vs Claude grade; the Nov 11 one ran: see this session's status).

0. **Earnings tab, first live week**: check the reads with the user (Wed-Fri reports get estimates saved before
   the report); the guidance reader's misses go in as fixes with a GV bump. Not done: revenue from the release's
   tables (SHOP-style releases give only growth up front: ≈ from growth), the prior quarter's growth (acceleration).

1. **The momentum cutoff: DROPPED by the user (Nov 10 2026, "drop it... already told Claude"); never raise it again.** (Was: the user will say which rule): no buy points once the stock has run too far from its
   momentum's start (the low of its last rest of 40+ sessions without a new 6-month high; AEHR: Nov 21 2025, 18.70).
   **A**: 300%+ from that start (2 years of buy points past it: -0.4 to -0.8R whatever the entry, both halves; blocks
   AEHR May-Jun 2026, SMCI Jul 12 - Aug 2023, but also the user's LIFE Oct 20-30 2026 at +335-368%). **B**: 300%+ and
   140%+ over the 200 SMA at once (keeps LIFE, 85-98% over it; but that LIFE-like group lost -0.65 to -0.75R). The time
   since the start added nothing. Code: `L["max_run_pct"]` in scanner/launch.py (0 = off); the status then reads
   "EXTENDED: +X% from its momentum start (date), no buy points" and the stock's alerts stay quiet.
2. (From Nov 1, not checked in the Nov 2 group-rank session) CDW, SHOP, RBRK, RGEN, TEAM: a 2nd close under their breakout level (holding over the 50 EMA) makes
   them breakout undercut & reclaim setups, alerting from Tuesday; check the reads and alerts with the user.
3. **The spreadsheet** (tools/test-results.xlsx on test/pb1h, sent to the user Nov 1 evening): the live engine's
   5,783 buy points; each trigger sheet = only the days the engine read as that breakout (engine_read), failed crosses
   on their own sheet, sheets for bull flag / bull pennant / breakout undercut / 50 EMA / gap retest / momentum. The
   corrected analysis (tools/analysis.json, bought at the close, runners 21 EMA): pop +0.37R (90), bull pennant +0.29R
   (47), push +0.22R (170), 21 EMA undercut & reclaim +0.20R (100), breakout undercut & reclaim +0.07R (116), 50 EMA
   reclaim -0.04R (138), base breakout -0.07R (997), bull flag -0.21R (228); none beyond luck (t under 1.6). Go
   through it with the user if they ask.
4. **"No reset yet" tag** (AEHR's Mar 5-19 2026 buy points, 1R losers before the momentum reset at the 50 EMA): the
   user's momentum rule (1) may replace it; ask if they still want a tag.
5. (From Nov 1, not checked in the Nov 2 group-rank session) check the first live gap-out-of-base and breakout-reclaim alerts, the 50 EMA tab, and the evening
   Ready file (after the user subscribes ntfy).
6. Offered, never decided: require the 10 / 21 EMA at the level for a retest; a fairer breakout stop test (0.7 ADR
   under the buy, then the day's low); trigger a bull flag on the higher of the line and the day before's high.
7. Group rank and leaders: DONE and live (Nov 2, see Changes). Decided: no Emerging / Lagging tags, no breadth rule,
   no $2T+ stocks, no "#1 in group" tag on Launches. Study results for reference (scanner/probe_leaders.py on
   test/gapstudy, groups of 5+ stocks, ran 20%+ in 20 days): gap-ups in a Top group: the group's #1 61% (54) vs #2-3
   51% (65) vs the rest 41-42%, but the average 20 days later no better (+3.1% vs +3.6%) and more faded on the gap day
   (57% vs 49%). Launches: the group's #1 20% (86) vs the rest of its group 29% (570). Examples: SNDK #1 in Memory &
   Storage at every month-end Sep 2025 - Jun 2026; DELL #2 in AI Servers Feb 2026 while the group ranked low, #1 Mar
   and May; in the CPUs theme INTC, not AMD, led Mar-Jun 2026. Still open, only if the user asks: (a) the stock's rank
   vs the whole market helped launches (top 3% of all stocks 34% (100) vs 25%; with a Top/Strong group 40% (52), avg
   +6.1%): DONE Nov 3 as the RS column on Launches (and plain on the Watchlist); (b) DONE Nov 3: the rank replaced Leading in the breakout
   grade; (c) DONE Nov 3: 3-SETUPS triggers on the phone and in the 1-minute checks. Emerging: tested and rejected (gap-ups 24% ran 20%+
   vs bottom half 29%; launches 20%, avg -5.5%).
9. **Industry groups / themes (live Nov 3, the group-rank session)**: first check Wed Nov 4 after the close that the
   portal's Industry list shows "Groups" with Strength, Network & App Delivery and Aerospace Components appear, and
   Launches rows show the new group names. The weekly profiles.json refresh (day.py, when 7+ days old) is untested live:
   check it ran by Nov 10. Waiting names (join when 0.6+): AMBA (AI Connectivity group), GEN, IPGP and the 11 theme adds
   under 0.6 (LNG, OKE, RDWR, VCYT, ...). The user may still send moves from proposed_groups_v3.xlsx / tech_review.xlsx
   (edits go in radar/industry_groups.json or radar/theme_adds.json, test branch first). Decided: no pair groups
   (CDNS-SNPS, NFLX-SPOT, JOBY-ACHR: use RS); big loners (META, APP, SHOP, ORCL, RBLX, RDDT) stay "· other" with RS.
8. Older: move the Launches rules box to the top of the tab; picks reading their history from the start; an intraday
   surge alert without a gap; the 3-SETUPS weaker Ready groups (kept as is).

