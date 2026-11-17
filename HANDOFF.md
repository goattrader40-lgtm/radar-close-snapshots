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

## Status of the session "Radar: Start days stay on until they fail + 0.8 ADR start (BILL, Nov 16)" (Mon Nov 16 2026, ~11:30 AM - 8:30 PM ET; session_01PkbDakpheN6wD5vCKyUvBf; in progress)

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
  evening bars without the Nov 16 close); a retry is scheduled ~02:50 UTC; else the Tue Nov 17 4:40 PM scan applies the rules
  (expected: ~47 rows, none before Nov 1, QNT / VOYG / PL off). Not touched: the START DAY alert, the
  "start <date>" line under launches, Launches. Scratch scripts of the measurements: this session's scratchpad only (decide.py,
  behave.py, late.py, late2.py, both.py: the numbers are in the rules rows).
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
| Opening ranges (+ Filter "ORH") | radar/levels.py from day.py's 5-minute live update, 9:36 on -> radar-data levels.json (stocks up 2%+) |
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

