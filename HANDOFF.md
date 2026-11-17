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

## Status of the session "Radar: Start days stay on until they fail + 0.8 ADR start (BILL, Nov 16)" (Mon Nov 16 2026, ~11:30 AM - 4:30 PM ET; session_01PkbDakpheN6wD5vCKyUvBf; in progress)

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

## Status of the session "Radar: AZTA breakout alert (Nov 16)" (Mon Nov 16 2026 ~11:30 AM ET - Tue Nov 17; session_01PkbDajZLtZ51Kk895bqYFw)

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
- **Told the user, no answer**: with "every touch", AZTA Nov 16 (low 44.32, close 47.22) also reads "retest held" and would send
  the 3:45 PM alert, though they had said Nov 16 was "just confirmation".
- **Open, for another session (the user: "leave that alone")**: a GAP retest rule (AEHR Feb 12-17 2026: back to where it gapped
  from on Feb 11 and held; the scan only knows the retest of a broken base top).
- **Not done**: the alert text "nothing traded above it for N sessions" is still false for a top poked in the last 3 sessions
  (WRBY 31.75 over 31.50 on Nov 11 2026): offered, not taken up. AZTA is not in tools/examples.txt (offer "add it to the
  examples"). long_bars.json now has 185 symbols (+ AZTA CDW GEO HNGE AMRX GCT WAT).

## Status at the end of the session "Radar: 21-day / 62-day high columns (Nov 13)" (Fri Nov 13 ~0:30 - 2 AM ET and Sat Nov 14 2026 ~noon - 5 PM ET; session_01PkbDahhagkKkQ2rkgKsLuZ)

**In one line: the Days 21H / 62H columns (Nov 13), then on Sat Nov 14 nine go lives on the Watchlist's 1-lists and the Launches
tab, all on main, nothing left on a test branch. FIRST THING NEXT SESSION: the Mon Nov 16 evening scan is the first real run of
the four 1-list rule changes (they were tested on made-up bars and on the ~175 long-bar stocks only).**

- **The 1-lists as they stand after Nov 14** (scanner/settings.json, scanner/run.py, scanner/screens.py; rules/SCANNER_RULES.md):
  **1-EP/GAP on**: gap of more than 5%, relative volume 2x+ (was 2.5x), the gap day closes up 5%+ (new), the standard
  filters at that close. **Off**: 2 closes in a row under the 50 EMA, or a close below the close of the day before the gap
  (new: VIR Nov 12 2026, 12.12 under 12.21), or the user's x (new). No 15-day limit any more.
  **1-UPDAY on**: up 4%+, relative volume 1x+, the standard filters (unchanged). **Off**: 2 closes under the 50 EMA, a close
  below the low of the FIRST day it came on (was: the latest up day's low; RKLB Nov 13 2026 left on 63.20, its first-day low
  was 54.96), 15 trading days without reaching 3-SETUPS (kept), or the user's x (new).
- **First checks Mon Nov 16 after the evening scan** (scanner/state.json and its log): (1) 1-UPDAY rows have `first_day` and
  the 43 rows with a raised line got their first day's low back; (2) 1-EP/GAP rows have `pre_close`; VIR and NXT leave if
  still under it ("closed below the pre-gap close"); (3) what joined 1-EP/GAP with the 2x volume and the 5% close (the 2x
  was never measured); (4) a first real x: picks.json `removed_lists`, the log's "removed by you"; (5) the Watchlist rows'
  Other entries show "inside day"; (6) Days 21H / 62H in the session (one more than at the close, or 0d over the high).
- **Open, the user to decide**: the 15 trading days off 1-UPDAY too (my last answer: leave it, look again after a week of
  scans; offered a Friday Nov 20 check of what joined / left 1-UPDAY and the list's size: no answer); a stock on 1-EP/GAP
  not shown on 1-UPDAY as well (offered); Download for TradingView on the 50 EMA undercut table (offered); one combined
  search result table on Launches (offered); a standing Coil buy column (overtaken by Other entries on Launches).
- **A correction made to the user (Nov 14)**: the five 15-day removals from 1-UPDAY were first shown with their 1-month
  gains (misleading: mostly before the removal); from the removal day FDS +4.0%, PCOR +2.6%, SGRY +1.9%; only ADMA was off
  every list and then moved (its Nov 5 gap put it on 1-EP/GAP the same day).


- **LIVE (the user's "go live", Sat Nov 14 2026 ~1 PM ET, branch claude/watchlist-launch-column-filters-ia4hqf, commit d1a2b9a):
  1-UPDAY holds the low of the FIRST day it came on the list.** The user: "what about if one stock did up 1st day lets say 6%
  next day another 5%, if 3rd day it closed below 2nd days low would it take it off from list?", "it should have counted the
  low of 1st day it got into our table", "1# fix it". Before: each repeat up day replaced the row's `low` with that day's low
  (and the stock left on a close under it). Now (scanner/run.py step): a repeat up day keeps the row's `low` and `first_day`;
  it still moves the row to that day's section and restarts the 15 days (`added`). Once, rows from before (no `first_day`)
  get the low of the day they came on, from the state log's last "added" (43 of the 136 rows on Nov 13 had a raised line:
  CGON, UPBD, ELAN, WWW ...). The portal's Watchlist rule text and the rules workbook (1-UPDAY row) follow. Not touched:
  Launches, alerts, 3-SETUPS; 1-EP/GAP has no low rule (`delete_below_gap_low` is false).
  Tested with made-up bars only (this session can't fetch real bars): +6%, +5%, then a close 1% under day 2's low: main
  removes it, the fix keeps it (line 29.40, not 31.47); a close under day 1's low leaves in both; the one-time repair
  restores the day-1 low. No `--regress` (launch.py untouched), no 2-year check. scanner.yml was NOT re-run (Saturday: no new
  session to process). **First check Mon Nov 16 after the evening scan**: scanner/state.json 1-UPDAY rows have `first_day`;
  the 43 rows' `low` went down to their first day's; the removals "closed below the up-day low" quote the first day's low.
- **LIVE (the user's "task1 # go live", Sat Nov 14 2026 ~2 PM ET, same branch, commit e797659): 1-EP/GAP has no 15-day limit.**
  The user: "lets take that 15 day clock, we dont need it there". scanner/run.py step: "15 trading days with no setup" now
  removes from 1-UPDAY only; an EP gap stays until 2 closes in a row under the 50 EMA (`delete_below_gap_low` is still false).
  The portal's Watchlist rule text and the rules workbook (1-EP/GAP row) follow. Tested with made-up bars: a gap stock quiet
  over its 50 EMA leaves on day 15 on main, stays with the change; the 1-UPDAY stock still leaves on day 15. Why (the list's
  log since Oct 5): 71 added, 17 removed, only 3 by the 15 days (RXO, XP, BRZE: nothing lost), 14 by the 50 EMA; an EP
  stock with ADR 3.5-4% could never reach 3-SETUPS (ADR 4%+) and always expired. Takes effect at the Mon Nov 16 evening scan.
- **LIVE (the user's "3#task go live", Sat Nov 14 2026 ~1:40 PM ET, same branch, commits 42a536b + 6789ee6, merge bdbe3b5):
  Other entries as a column on every list table.** The user: "i need you add other entries as a column in all watchlist
  tabs" (they could not find the coil / Other entries on Launches, nor on the phone). (1) scanner/launch.py follow(): every
  Launches / laggard / 50 EMA undercut row carries `other_entries` (the Watchlist's `entries`: flag_trendline, coil,
  pullback_tight_day, level, bigger_base, flat_top; breakout left out). (2) docs/index.html: catalog column and + Filter
  "Other entries" (`otherOf`: the Launches row's other_entries, else the Watchlist row's entries, else its coil; text
  filter: has "coil"); AUTO_X: the Launches, 50 EMA undercut and laggards tables get it once by itself, after Away (LAY._auto
  marks; the x in the column list takes it off for good; "Reset this table" brings it back); the Watchlist's Other entries
  no longer has class c2 (it was hidden under 560 px). Display only. Tested: `--regress` "every agreed example reads the
  same"; the page on desktop / phone, fresh and with a saved layout, all 5 Watchlist lists, no page errors. Launches rebuilt
  (picks.yml, 1:42 PM ET, the Nov 13 close): 225 rows carry other_entries, 49 non-empty (TMDX coil 96.45 + level 97.56,
  ELAN coil 26.91, ZM flat top 100.65). Rules workbook: one row.
- **LIVE (the user's "go live", Sat Nov 14 2026 ~2:50 PM ET, same branch, commit 6fb1b40, merge 15c1f57): an x next to the
  ticker on 1-EP/GAP and 1-UPDAY.** The user: "i need to add x button next to tickers for ep/gap and upday so if i see some
  wrong i can delete it myself". docs/index.html: the button on those two lists (removeListed, after a confirm) saves
  setups/picks.json `removed_lists` {list: {symbol: {added, at}}} with the Follow key; hidden at once on every device
  (wlGone: PICKS + localStorage 'radar-wl-removed'; wlRows). scanner/run.py step: the evening scan takes a row off whose
  `added` is at or before the removed one ("removed by you (the x on the Watchlist)"); a new gap / up day on a later day
  puts it back. picks.yml gate: such a save rebuilds nothing. The stock's other lists keep it. Until the evening scan the
  list's count on its button, the Scan lists and TREND still include it. Tested: the page on desktop / phone with a
  stand-in for the GitHub save (x on 54 / 135 rows, none on 2-POOL, the row gone, a second browser hides it, no page
  errors); the scan with made-up bars (removed rows leave, one comes back on a new gap 4 sessions later). Rules workbook:
  one row. **First check**: the user's first real x (picks.json has removed_lists; the Monday scan logs "removed by you").
- **LIVE (the user's "do volume 2x+ go live on ep/gap", Sat Nov 14 2026 ~3:30 PM ET, same branch, commits 2f4e62b + the 2x
  one): 1-EP/GAP entry = a gap of more than 5%, relative volume 2x+ (was 2.5x), AND the gap day closes up 5%+.** The user:
  "do we have requirement that ep/gap day has to close above 5%?" (no: only the open and the volume were checked), "put that
  as a requirement it has to close above 5% for the day!!!". scanner/settings.json EP-GAPUP-BREAKOUT {gap_pct 5, rel_vol 2,
  close_chg_pct 5}; scanner/screens.py (chg >= close_chg_pct). A gap that fades goes on 1-UPDAY if it still closes up 4%+.
  Rows already on the list are not touched. The portal's rule text and the rules workbook follow. Tested with made-up gap
  stocks (8% gap: close +9% on EP; +4.5% -> 1-UPDAY; +1% -> no list; 2.2x on EP, 1.8x -> 1-UPDAY). Real data, the close
  rule only: of the 45 names that came on 1-EP/GAP in the 11 saved scans Oct 29 - Nov 13, one would have been kept off:
  CHYM Nov 5 2026 (gap +6.4%, closed +1.0% at 30.18; 33.55 on Nov 13, +11%): told the user. The 2x volume was NOT measured
  (how many more names): **first check** the 1-EP/GAP additions of the Mon Nov 16 scan. Not touched: the EP alerts
  (radar/alerts.py), Launches.
- **LIVE (the user's "task6# go live", Sat Nov 14 2026 ~2:35 PM ET, same branch, commit 155080e, merge 60af082): "inside day"
  in Other entries.** The user on AXGN Nov 11-13 2026 ("it looks coil to me am i missing something?"): "lets call this kind
  of days inside days, all coil rules apply, so when i check in column other entries it should show it as inside day... if
  both is true it shows strongest one which is coil". scanner/msf.py inside_days(): a mother day, then 2+ days in a row
  inside its high and low WHATEVER their bodies, the close over the 200 SMA; buy = the last inside day's high, stop = the
  mother day's low. run.py entries (inside_day, inside_day_stop) and launch.py other_entries (inside_day), ONLY when there
  is no coil. Display only: no alert; the Coil buy column / filter stay the strict coil. AXGN: Nov 12 (-5.5%, body 4.2% vs
  half its ADR 2.8%) is why the coil counted 1 of 2; inside day 51.48 (Nov 9), 51.10 (Nov 10), 57.46 (Nov 13). `--regress`
  "every agreed example reads the same". Launches rebuilt (picks.yml 2:37 PM ET, the Nov 13 close): 235 rows, 4 coils, 22
  inside days, AXGN "inside day 57.46". About 5x as frequent as coils (told the user; some loose: YOU buy 58.99, mother low
  51.27). The Watchlist lists get it at the Mon Nov 16 scan.
- **LIVE (the user's "task2# agree with that solution.. go live", Sat Nov 14 2026 ~3:10 PM ET, commit 6295e78, merge 4c5a2bb):
  1-EP/GAP: off on a close below the pre-gap close.** scanner/run.py: every EP row carries `pre_close` (the close before the
  gap; the FIRST gap's while it is on the list; old rows get it once from the bar before their `added` day); settings
  `delete_below_pre_gap_close: true`; removal text "closed below the pre-gap close X (the gap is given back)". VIR: pre-gap
  close 12.21 (Nov 6), gap Nov 9, closed 12.12 Nov 12 -> off, a day before -17.8% to 9.96. A dip under the gap day's low
  that holds inside the gap stays (TREX, SMG, ICLR). Tested on the real long bars (175 symbols, the last 30 sessions, with
  and without): VIR and NXT (96.02) leave Nov 12, MOH Nov 9 (203.35 under 207.85; 209.49 on Nov 13); the one-time backfill
  on the saved state removes VIR and NXT. **First check Mon Nov 16**: state.json EP rows have pre_close; VIR / NXT leave if
  still under. The portal's rule text and the rules workbook follow.
- **LIVE (the user's "go live", Sat Nov 14 2026 ~3:40 PM ET, same branch, commit 117c201): the Launches tab's ticker search
  covers every table.** The user (RKLB): "when i search rklb in launch it should show in any of those 3 tables (now it only
  pulls names from launch tables)". docs/index.html: #ln-search ("Find a ticker") also filters the 50 EMA undercut and
  Start days tables; #ln-found next to it says "RKLB": Launches n · 50 EMA undercut n · Start days n ↓ · Watchlist: its
  lists / not on a list. Tested on desktop / phone (RKLB, AXGN, a partial, no match, cleared), no page errors. Rules
  workbook: one row. The user followed RKLB that afternoon (a pick, Launches row grade You, 2:52 PM ET); confirmed to them:
  with the first-day low 54.96 RKLB would still be on 1-UPDAY (Nov 13 close 61.53; its first close under the 50 EMA 62.36).
- **LIVE (the user's "1#go live", Sun Nov 15 2026 ~11:20 AM ET, same branch, commit b99bcf2, merge 3548e91): a start day's
  close must be 30%+ over the 52-week low.** The user: "in order stocks gets to start list it had to go above 30% above 52
  week low ... its your flaw in design", "30% rule is the point, we are not interested in any stock close to their 52 week
  low, stock can be below the day before but in order to get alerted and stocks gets to our starts list table it has to
  pass that requirement", "we are not interested in dead bounces!!!!". Found on the START DAY alert's first live day (Fri Nov
  13): 3 start days, 0 alerts: NU (+11.7%, over its ORH 12.39) blocked by the alerts' 30% gate (18.0% over 11.20) while the
  table, built Nov 12 without that gate, showed it; MOD never traded over its ORH 146.50 (the day's high: by design); HROW
  was not on the start watch. My first suggestion (exempt the alert) was the wrong way round. scanner/launch.py start_raw:
  `c[i] >= low52 * 1.3`: the Start days table, the "start <date>" line under a launch, the reset start, the start watch's
  "first". `--regress` "every agreed example reads the same". Launches rebuilt (picks.yml, the Nov 13 close): Start days 45
  -> 32 (out: UBER 11.1%, HONA, AVGO Nov 10 14.6%, HROW, NU, CEG, NRG, AVAV, FN, FLR, MTZ, EQPT, TLN 29.8%); 25 Launches rows
  and 3 50 EMA rows lost their "start" line (APP Nov 4, TMDX, SMG, LYFT, POOL, SPOT ...; FDS Jun 26 -> Jul 1). **AVGO Nov 10
  2026 was a start day the user agreed on Nov 12: told them twice; they chose the rule** (the other agreed ones pass: RKLB,
  TTEK, LUNR, LSCC, AMD, ZM, SONO). The table's note on the portal now says the 21 EMA (the 50 EMA = the confirmation).
  Seen in the same rebuild, NOT from this change: EMBJ (launch Nov 10, B) left Launches because Yahoo served 1 bar for it
  that day (a renamed ticker's history): it should come back when Yahoo serves the history again: to check.
- **OUTAGE, my mistake (Sun Nov 15 2026, 11:43 AM - 12:57 PM ET, about 75 minutes): the portal's code did not load.** The
  fail-rule go live (6bb992d) put "the start day's low" inside a single-quoted text string in docs/index.html: the
  apostrophe ended the string, a syntax error, every tab empty. I had only run `--regress` for that change, not the page.
  Found while testing the next change; fixed in 0c75a07 ("the low of the start day"). **Lesson for every session: any edit
  of docs/index.html gets a page load test (Playwright, no page errors) before the push, even a one-line text change.**
- **LIVE (the user's "task 3 and task 4 do it test it then go live", Sun Nov 15 2026 ~1:00 PM ET, merge dc9141f): the Start
  days x and the column "Start day over 21D high".** (1) An x next to every ticker of the Start days table ("so any tickers
  doesnt look to me manually i can delete from start list"): picks.json `removed_starts` {symbol: {date}}; hidden on every
  device (sdGone / sdKept), left out of the TradingView file and of the search line; a later start day shows again;
  picks.yml gate: no rebuild. (2) Column "Start day over 21D high" ("showing in column if it was closing above 21d highest
  close"; first named "Over 21D high", the user: "needs to be for start day so column name needs to be different"): Yes /
  No + % of the start day's close vs the highest close of the 21 sessions before it (launch.json `date_vs_hc21_pct`,
  start_fields). Tested on desktop / phone with a stand-in for the save (x on all 28 rows, the row gone, a second browser
  hides it, the sort, no page errors); `--regress` same. Launches rebuilt (the Nov 13 close): 4 of the 28 start days closed
  over their 21D high (SONO +6.7%), 24 under (RKLB -13.7%, MOD -11.9%, AMD -8.7%). Rules workbook: one row.
- **LIVE (the user's "go live", Sun Nov 15 2026 ~1:40 PM ET, commit d35d9ce): in the Columns box a click on a column marked
  "added" takes it off again.** The user: "21 day closing high, i cant take it off from columns, weird" (the Start days
  table): the green "added" chip only ever added; the x was only in the "In this table" list further down. The chip now
  reads "added · click to remove" and calls delCol. Page-tested before the push on the merged page (desktop / phone, Start
  days and Launches tables, both tables still fill, no page errors).
- **The user's question "which option makes sense based on these numbers" (Nov 15): my answer: the LIVE fail rule** (under
  the start day's low and the 21 EMA), not the third condition: of the 31 extra stocks it removes, 23 were not runners and
  8 were. No answer yet: the rule stays as it is until they say otherwise. Offered: an alert for the GLOB type (started,
  dipped holding its gap, back over the start day's low and the 21 EMA: 8 of 15 ran 10%+); the theme check.
- **LIVE (the user: "this recommendation accepted", "apply zone rule here too", "fix only line thing, dont touch other parts",
  "run the test provide result and go live on that"; Sun Nov 15 2026 ~7:15 PM ET, same branch, merge 6b8f20a): three
  scan changes, no page file touched.**
  1. **Bull flag: where the falling line starts** (scanner/launch.py flag_anchor, L flag_twin 0.05): the line starts at the
     day after the top when that day's high is within 0.05 ADR under the top's (TOST: top Nov 4 2026 36.01, Nov 5 35.99: the
     line was 35.84 on Nov 13, now 34.05). 0.25 ADR moved the agreed CAI Sep 14, ZS Oct 21, TTAN Oct 30 2026: not used.
     `--regress` same. **2-year check, asked first and run on main and on the branch the same evening** (probe_catalyst
     buy_points.current): flag 747 -> 786; ran 10% 53 -> 54%, ran 20% 25 -> 25%, failed 39 -> 39%, median +0.3 -> +0.3;
     "flag, decisive" 601 -> 630 (56 / 27 / 37 -> 56 / 27 / 36); all buy points 6,171 -> 6,205, 50 / 24 / 42 unchanged.
     Launches after the rebuild (the Nov 13 close): EQX, ISRG, SRAD lost their flag line as the next trigger (Base top now),
     POOL's pennant line 222.66 -> 221.68, NTSK's 25.93 -> 22.45 (close 21.75). TOST Nov 13 is STILL no flag for the scan:
     lower lows on 2 of 5 pullback days (the rule: more than half) and the pullback's volume 1.14x (the rule: 1.1x or less):
     told the user, who chose to leave those.
  2. **Inside day: the zone, and used up on a trigger** (scanner/msf.py inside_days -> buy, stop, triggered): the inside days
     make a zone (their highest high / lowest low); a later day under it ends the pattern; a day over the buy is the
     trigger ("inside day triggered <buy>" that day, then nothing). TOST: buy 35.56 Nov 6, 35.20 Nov 9, gone Nov 10 (33.57);
     AXGN 51.48 / 51.10 Nov 9-10, triggered Nov 11, 57.46 Nov 13. Launches: inside days 22 -> 4 (AXGN, CNXC, BBY, NAVN), 2
     "triggered" (PAY 34.30, PRMB 24.00). My first two tries were wrong (any day inside the mother bar kept it armed; then
     "each day inside the day before": the user: "not a good suggestion").
  3. **Coil: the zone rule too** (msf.py run_symbol coilZoneLo): a later day under the lowest low of the coil's inside days
     ends it. Long-bar stocks, ~2 years: 916 coil days -> 793; the removed ones did as well as the kept (over the buy next
     day 59% vs 53%, ran 5%+ in 5 sessions 45% vs 44%): told the user. Launches: coils 4 -> 3 (LFST gone).
  Rules workbook: three rows. **The user's rule from now (Nov 15): "before you fix anything you gotta tell me and i confirm
  1st": explain and wait for the confirmation before building, on a test branch too.**
- **Still open from the TOST review (each needs the user's confirmation first)**: Days 21H / the 21-day closing high from
  real closes (TOST 6d, should be 7d: the user asked how it is coded, "dont change"); the retest after a close under the
  level; the day's alerts on the Launches row; one read for the Watchlist 1-lists and Launches; the Columns chip
  "(already in this table)" that does nothing for a built-in column (the user: "no action needed").
- **Open, found Nov 15 on TOST (Fri Nov 13 2026), the user: "couple flaws", "information is messed up": explained, nothing
  changed, each needs a go.** TOST (launch Nov 4, C; top 36.01 Nov 4, lower highs 35.99 35.56 35.20 34.67 34.37 34.37; Nov 13
  low 33.40, close 34.68 +3.5% on 0.8x) broke its flag line, held its breakout level 33.53 and reclaimed the 10 / 21 EMA.
  (1) **The bull flag was not read**: flag_at draws the line from the top keeping every high under it; Nov 5's 35.99 next
  to the 36.01 top makes it almost flat (35.84 on Nov 13); the user's line along the lower highs is ~34.05. The other flag
  tests pass (1.8 ADRs deep, a 6 ADR pole, 5 lower highs); flag_shape also returned None (not looked into further). A main
  pattern: explain, replay the agreed flags, ask about the 2-year check. (2) **The retest was not read on Nov 13**: the
  engine counted it Nov 10 (low 33.57) and Nov 11 (33.34) and allows another only on a lower low; Nov 12 closed 33.52, a
  cent under the level, Nov 13 reclaimed it: the alerts (their own rules) sent "RETEST HOLDING into the close" at 3:45 PM,
  the Launches row showed no trigger and "Holding after the launch attempt", so no 3-SETUPS "Triggered today" (it is on
  TREND, Up 1d, 1-UPDAY and 2-POOL). (3) **What the alerts fired is not shown on the Launches row.** (4) **Days 21H / the
  21-day closing high can be a day off**: radar/pipeline.py rebuilds closes from each day's % change, a drift under 1%:
  TOST reads 6d (Nov 5, 35.12) where the bars say 7d (Nov 4, 35.37); 3 of the 175 long-bar stocks have the wrong day (TOST,
  TRU 4d vs 16d, VFC), 12 have the 21-day closing high off by 0.5%+ (it also feeds the EP alert's 21-day-closing-high
  rule). (5) The Watchlist rows of the 1-lists read the MSF engine (TOST: Base forming, buy 37.20), the Launches row the
  launch engine (Base top 36.02): two reads of one stock. Suggested order: the flag line, the retest after a close under
  the level, the alerts on the row; then real closes for the day counts.
- **Open, the user asked for my suggestion (Nov 15): the logic of what takes a stock off the Start days table.** Numbers
  (421 start days on the ~175 long-bar stocks, ~2 years, the 30% rule on; "ran" = 15%+ within 20 sessions; base rate 42%;
  the rule only matters inside the table's 5 sessions): the old rule (close under the pre-start close) takes 21% off, the
  LIVE rule (close under the start day's low and the 21 EMA) 28%, the user's tuned idea (those two AND under the pre-start
  close) 21%; stocks kept ran 48-51%, stocks taken off ~20%, whatever the rule. The 31 "GLOB type" rows (under the start low
  and the 21 EMA but holding the gap) ran 26%. The user's ideas checked on the 37 GLOB-type cases of the last 260 sessions:
  a rising 21 EMA after the start: no difference; the dip staying clear of the pre-start day's BODY (by the lows): 4 of 5
  were winners (AEHR, SMCI, PACS, RKLB) vs 4 of 31 when it went in, but it drops GLOB (low 34.60 vs 34.70) and APLD (+69%);
  by closes it IS the third condition. 15 of the 37 bounced back while holding the gap, 8 ran 10%+ (APLD Apr 8 2026 +69%,
  AEHR Jul 15 +49%, SMCI Jul 22 +48%, GLOB Oct 1 +36%, PACS Apr 8 +21%). GLOB bounced on its 5th session after the start,
  the day the table drops it by age. The theme check (was the theme advancing) not done. My suggestion: see the chat of
  Nov 15; the user to decide.
- **LIVE (the user's "below low of start day and below 21 ema both has to be true, go live do it", Sun Nov 15 2026 ~11:45 AM
  ET, same branch, merge 6bb992d): the Start days table's fail rule.** A row leaves after 5 sessions ("getting old agreed")
  or sooner when the start FAILS: a close under the start day's LOW that is also under the 21 EMA, both together ("start
  failing should mean closing below the start day, very simple approach, thats the whole point, but that has to be below 21
  ema as well"); before: a close under the close of the day before the start day. scanner/launch.py `start_listed` (the
  table only). **My choice, told the user: the "start <date>" line under a launch keeps the older rule (`start_holds`)**,
  because with the new one GLOB's agreed start Oct 1 2026 (launch Oct 22; Oct 2-7 "testing gap holding up") would fail on Oct
  2 (35.10 under its start low 36.82 and its 21 EMA 36.22): ask again if they want one rule for both. `--regress` "every
  agreed example reads the same". Long-bar stocks, last 75 sessions: 599 listed stock-days -> 577. Launches rebuilt (the Nov
  13 close): Start days 32 -> 28, out: CRWV (start Nov 11 at 60.77, now 53.13), COHR (Nov 11, 234.51 -> 218.15), CNH, PLAB
  (Nov 9). The portal note and the rules workbook follow. EMBJ still off Launches (Yahoo's 1 bar): to check Monday.
- **LIVE (the user's "go live", Sat Nov 14 2026 ~4:40 PM ET, same branch, commits a378575 + 3781a0c): two page changes on the
  Launches tab.** (1) The ticker search shows each table's match under the box: the user: "you didnt do that search ticker
  correctly, if i search ticker, it has to pull that ticker from all tables under launch tab" (the tables were filtered, but
  the Start days match sat two cards down and the "Start days 1 ↓" note was missed). #ln-found now holds buttons, e.g.
  "Start days: RKLB · Nov 9 · +10.9% · close $58.86 ↓" / "50 EMA undercut: CNH · launched Nov 9 ↓", that scroll to that
  table. Offered, no answer: one combined result table at the top instead. (2) **Download for TradingView on the Start days
  table** ("i need download tradingview for this table as well"): #ln-sd-dl, the rows on screen (search and column filters
  applied), one ###Start day <date> section per start day, newest first. Tested on desktop / phone: 45 rows, 5 sections;
  with RKLB searched only RKLB; no page errors. Offered: the same button on the 50 EMA undercut table.
- **Asked Nov 14, no go yet: take the 15 trading days off 1-UPDAY too?** My answer: yes (since Oct 5 it removed 5: ADMA, EFOR,
  FDS, PCOR, SGRY, four of them up since and back through other lists; 20 of the 50 rows never on 3-SETUPS have ADR under 4%
  and can never beat it; risk: the list grows now that the first-day low removes fewer). Also answered: an inside day needs
  3 candles like the coil (mother + 2); the same ticker can be on 1-EP/GAP and 1-UPDAY from different days (26 are), never
  from the same day; RKLB was never in the 50 EMA undercut table (1 close under it).
- **Answered Nov 14, no change: why RKLB is on no list.** Start day Nov 9 2026 (Launches' Start days table, confirmed Nov
  10); on 1-UPDAY and 2-POOL Nov 10 (+6.5%, the first close over the 50 EMA; low 54.96); Nov 11 +5.5% raised its line to
  63.20 (the flaw fixed today); Nov 13 closed 61.53 -> off 1-UPDAY ("closed below the up-day low 63.2": with the first-day
  low 54.96 it would have stayed) and off 2-POOL the same day (the Friday refresh: under the 200 SMA 78.28). Never an EP gap
  (no 5%+ gap closing over the 50 EMA); no launch (under the 200 SMA). Offered: put it back on 1-UPDAY by hand, or Follow it.
- **Answered Nov 14, no change: AXGN Nov 10 2026 was not a coil for the code** (bars fetched with radar-tools `long`: the
  175 saved symbols + AXGN). Nov 5 wide day (51.85 / 47.57); Nov 6 inside it but its body 68% of the range (max 50%) -> it
  became the new mother day; Nov 9 high over Nov 6's; Nov 10 low 49.23 under Nov 9's 49.48: inCnt 0. By eye Nov 6, 9, 10 sit
  inside the Nov 5 bar (closes 50.02, 50.64, 50.89), then +15.2% Nov 11. Offered, no go: keep the wide mother day while
  later days stay inside it. Also seen: no Watchlist scan was saved on Nov 10 (setups commits go Nov 9 -> Nov 11).
- **Open, the user to decide (asked Nov 14: "what can be done so this kind of stocks doesnt stay on that list", VIR)**: VIR
  gapped Nov 9 2026 (+7.7%, 4.2x, close 13.65, gap-day low 13.11, pre-gap close 12.21), closed 12.12 on Nov 12 (the gap
  erased) and 9.96 on Nov 13 (-17.8%, ~9x, 10.6% under the 50 EMA 11.14); still on 1-EP/GAP (1 close under the 50 EMA).
  Offered: A. a close under the gap day's low (the existing switch; would remove 8 of 54 today incl. shallow retests TREX,
  ICLR, SMG); B. a close under the pre-gap close = the gap fully erased (VIR and NXT of the 30 names with long bars; TREX, SMG
  stay): RECOMMENDED; C. one close 1 ADR+ under the 50 EMA. Not built. Also noted, no go: a returning stock keeps its EP tag
  (EXTR, TLN came back through 2-POOL without it).
- **Answered Nov 14, no change**: the coil column: on Launches it is the optional "Coil buy" (⚙ Columns, type coil), not shown
  by default and not named "Other entries" (the user could not find it; offered: a standing Coil buy column on Launches: no
  go); the Watchlist's "Other entries" (and Pattern, Rel vol, Added, Themes) are hidden on a phone held upright (class c2,
  under 560 px; offered to show it: no go). Why MOD / CBRS / KLAR / CGON / VKTX were not on 1-EP/GAP on Nov 13 (MOD, CBRS
  under the 50 EMA; KLAR, CGON, VKTX no 5% gap; KLAR, VKTX under 30% over the 52-week low). The standard filters are checked
  at the up day's own close.

- **LIVE (the user's "go live", Fri Nov 13 2026 ~0:50 AM ET, branch claude/watchlist-launch-column-filters-ia4hqf, merge
  754cbb1): Days 21H / Days 62H, two columns and + Filter.** The user: "days of from 21 day high and days of from 62 day",
  "i just want to see if its been 3 days since that day or 5 days", "highest closing price day is considered high day",
  "make column name short". (1) radar/pipeline.py high_ago(): stocks.json `hc21_ago` / `hc62_ago` = sessions since the
  highest CLOSE of the last 21 / 62 sessions (0 = the last close; the newest day on a tie), `hc21_date` / `hc62_date`,
  `close_high_62` (None with fewer sessions). (2) docs/index.html: catalog columns "Days 21H" / "Days 62H" (hiAgo; hover: the
  high, its date, the distance), on every stock table's column list and in + Filter, which starts as "at most" for these two
  (xfOp0). In the session (LIVE_ON): a live price over that close reads 0d, else the stored count + 1, so it follows the
  5-minute live updates from 9:30 (the user asked "as of 930 am or end of day ... twice a day or every 1hr?": answered: every
  5 minutes in the session, settled by the evening build). A display only: no rule, buy point or alert reads it. Rules
  workbook: one row. Tested: the page with the Nov 12 files and stand-in values (236 Launches / 100 Watchlist rows right, both
  filters, no page errors), again after merging main; high_ago on made-up series only. No `--regress`, no 2-year check, no
  Launches rebuild (nothing in launch.py changed). radar-day `daily` started after the push to fill the Nov 12 close.
  **First check Fri Nov 13**: stocks.json has `hc21_ago`; in the session the counts read one more than at the close (or 0d
  over the high); after the evening build they match the charts.
  **After the refresh (radar-day `daily`, 05:53 UTC Nov 13, the Nov 12 close), checked on the real file**: 3,275 of 3,299 stocks
  have `hc21_ago`, 3,257 `hc62_ago` (the rest too newly listed: a dash); the 146 with Days 21H = 0 all closed at their 21-day
  closing high; the 62-day count is never under the 21-day one. By hand: NVDA 16d (221.26, Oct 21) and 27d (238.48, Oct 6);
  AMD 0d (585.30, Nov 12) / 27d (650.40, Oct 6); MBGL 0d / 0d; RKLB 1d (66.15, Nov 11) / 61d (78.61, Aug 18).
  Good to know: 61d on Days 62H (20d on Days 21H) is the oldest day of the window: a stock falling the whole time reads it
  (told the user). Go live met another session's go live on main: rules/scanner_rules.xlsx conflicted (a binary file) and was
  rebuilt with `python3 rules/make_rules.py` from the merged make_rules.py; the merged page re-tested.
- **Decided with the user**: days, not %; the high day = the highest CLOSING day; short names (offered "Days off 21D high" /
  "Days off 62D high" as longer names: no answer, the short ones stay).
- **Test only**: nothing (the branch is merged).
- **Open / first check Fri Nov 13**: in the session the counts read one more than at the close, or 0d with the price over the
  high close (LIVE_ON; not seen live yet); after the evening build they match the charts. Nothing else open from this session.

## Status at the end of the session "Radar: full portal review, build continued (Nov 12)" (Wed Nov 11 2026 evening - Fri Nov 13 ~1:30 AM ET; session_01PkbDajtNcuGe22aVKWcF77)

(An older copy of this section, as it stood before this wrap-up, was moved to HANDOFF_ARCHIVE.md by the Days 21H / Days 62H
session's wrap-up the same night: this one is the complete one.)

**In one line: the chart reading is LIVE, all of it, with its alerts (4 go lives the night of Nov 12-13, listed below); test/cleanlaunch = main.
FIRST THING NEXT SESSION: how the new alerts behaved in their first live session (Fri Nov 13), see "Open" at the end of this section.**

**Read first, as before: tools/chart_examples.txt and tools/user_answers_2026-11-10.txt (now on main too)**: this
session added about 40 more of the user's charts in their words (the launch is the FIRST day, the rest is follow-through;
climax tops; dying trends; the walk through the live Launches list of Nov 5-9), each with the engine's read and every test.

- **LIVE (the user, Nov 12 2026: "regarding themes, premarket things tasks get them live if you already tested it"; branch
  test/themespm = main + only these pieces, commit 70eb9fa, pushed ~10:30 PM ET Nov 11; Launches rebuilt 10:31 PM, 12a57fc):**
  1. **Themes**: themes and industry groups ranked on their TRADABLE stocks, 4+ for a ★ Top / Strong tier (launch.py group_rank:
     GR_TIER_MIN, `thin`); the **Heating up** column (heat 1-99, 🔥 = 90+ with 60%+ up) on Themes and Industry groups, "Heating
     up" and "RS 1W-1M" in the column list (launch.json group_rank rows: heat, week, breadth, hot; rs_week); **one pack** where a
     theme and an industry group share 75%+ (same_as: the group shows the theme's name and rank); the homes (theme_adds.json:
     XNCR KYMR PTCT BAX HGV OSPN STEP BRKR; industry_groups.json: PDFS, KBR, AMTM, STEP). After the rebuild (Nov 11 close): 4
     themes and 4 industry groups hold a tier (★ Top: IT Services & Consulting; IT Consulting & Outsourcing, Software: Vertical
     & Industry, Software: Finance & Banking), 50 themes / 139 groups under 4 tradable stocks, 14 one-pack pairs, Launches 148 +
     6 laggards as before. **This changes which Launches rows carry ★ Top / Strong** (the tier feeds the stars and the grade).
  2. **Pre-market: the Theme event card and the theme bounce list** (radar/theme_event.py, pmlive.py, day.py,
     premarket_build.py, the page). An event shows when the live scan finds one (8+ tradable stocks and 30%+ of an area
     gapping 5%+ the same way).
  Checked before the push: `--regress` 0 differences on that branch (no launch read changed), the group rank on 2 years of
  bars, all 8 tabs with the live data and with the new rank, no page error. Rules workbook: 6 rows (theme event, bounce list,
  tradable rank, Heating up, one pack, homes).
- **LIVE (the user's "go live", Thu Nov 12 2026 ~11:40 AM ET, branch test/earnhead, commit f1c1dfd):**
  1. **Earnings tab: a report that is out without an SEC filing yet** (the user: "see earnings nbis.. its 905 come on": NBIS
     reported before the open, its 6-K reached the SEC at 9:22 AM, after the last morning run, so the tab said "reports Thu"
     until the evening). radar/earnings.py takes radar-data pmnews.json as a 4th argument: a row whose report time has passed
     with no filing read gets `out_headline` (the pre-market news headline: title, at, source, url) and the page shows "Out ·
     not read yet" + that headline where it said "reports Thu". earnings.yml also runs at 9:10 and 9:20 AM ET (window 7:00 - 9:40 AM); the hourly
     runs to 2:00 PM were taken out the same day, a34ae1f (the user: "no need to 2pm... i need those by market open after that
     not interested"). Tested: radar-tools `earntest` on the branch (386 rows, 0 errors, NBIS read), the page
     with NBIS simulated at 7:15; the first live run 11:41 AM: 0 errors. Not built (offered): reading the release from the
     wire (GlobeNewswire / Business Wire) when the filing is missing; HBM (no filing, no headline) still reads "reports Thu".
  2. **+ Filter wording** (the user: "it should be ORH 5min above or not"): the three level filters read "Above the 5-min
     opening range high (ORH): any / Yes / No", "Above yesterday's high (PDH): ...", "Above the 21-day closing high: ..."
     (docs/index.html LVLF / LVLO; the saved values stay 'Over it' / 'Under it', so saved filters keep working; the Alerts
     tab's morning-breakout extra filter too). Tested on Gainers with live data.
  3. **Earnings tab: read without the SEC filing** (the user: "#18 yes do that", "do this so we get news as in nbis"; branch
     test/earnwire, 8ff3424, ~12:20 PM ET Nov 12). radar/earnings.py late_reports(): a report that is out (today's or last
     evening's) with no filing read gets 1. the release on a newswire the news feed links to (use_release, the same reader as
     the filing) and, when the wire refuses (GlobeNewswire: 403 for AVEX and HBM in the test), 2. the EPS / revenue / revenue
     guide exactly as the feed's earnings headlines print them (hl_read: "Q4 Adj. EPS $0.43 Beats $0.42 Estimate, Sales
     $447.062M Beat ..."; "Raises FY2026 Sales Guidance from ... to ... vs ... Est"). Alpaca's news API (earnings.yml now has
     the ALPACA keys). The read ends "· from the news headlines, no SEC filing yet"; the filing replaces it when it comes.
     Tested with `earntest`, then the first live run 12:20 PM: 0 errors, HBM "Mixed" (revenue $765.9M, +4.0% vs est; EPS
     $0.34), AVEX "Bullish" (guidance raised, +11.7% vs street). By code, no Claude.
  4. **+ Filter: short names and a search that finds them** (the user's "go live", ~1:30 PM ET Nov 12, cf3d250; the user: "i
     cant even find now 5min over filter", "above orh-5min is better than this so long filter name"). The level filters are
     now "Above ORH-5min", "Above PDH", "Above 21D closing high" (chip and search list alike: the morning's rename had left
     the search list on the old name); the + Filter search ignores spaces and hyphens ("5min", "5 min", "5-min") and finds them
     by "above" / "over" too. Saved values unchanged ('Over it' / 'Under it').
  5. **Theme event: the reason line by code** (same push; the user: "i dont want this to be done by claude, it has to be done
     by code"). docs/index.html drawPmEvent: under the event line, "Why (the leaders' own news)": the catalyst and headline
     of the event's first 4 leaders that have any in pmnews.json (the code news feed), with source, time and link; else "a
     market or sector move". Tested with a simulated event on the Nov 12 scan. **So the 8:45 task's instructions need NO
     change** (the "NOT DONE" item below is dropped: the user does not want Claude for it).
  6. **"Aerospace & Defense (all)", a wide list, and 4 homes** (the user's "go live. aerospace", ~2:20 PM ET Nov 12, 6d97190;
     Launches rebuilt 2:25 PM). The user: aerospace & defense stocks "popping up, not even in your theme / industry list"
     (MIR, AVEX). Found: 40 of the 60 have no theme, 45 no tight group, and they do not move together (KRMN 0.45, AVEX 0.41,
     BETA 0.32, MIR 0.39 vs the 0.6 a pack needs; no pack among them). launch.py group_rank: GR_WIDE = ("Aerospace &
     Defense",): the whole broad industry as one loose row "Aerospace & Defense (all)" (kind ind, `wide`, no tier), ranked
     and with a heat on its tradable stocks, placed among the industry groups WITHOUT entering their ranking (checked: every
     other group's rank, tier and heat identical with and without it; `--regress` 0). The page: the row in the Industry groups
     table, tag "wide list"; a click lists all 60 stocks. After the rebuild (Nov 11 close): #165 of 217, heat 96 🔥 (week
     +9.9%, 96% of its 25 tradable stocks up). Homes (0.6+ and the business matches, the homes test on the 340 tradable
     stocks with no pack): industry_groups.json EGO -> Gold, SIBN -> Medical Devices, NESR -> Oil & Gas Equipment &
     Services; theme_adds.json BCAX -> Small & Mid-cap Biotech (they join at the next weekly theme build).
     **The tech check the user asked for** (262 tradable tech stocks: 178 in a theme, 172 in a tight group, 67 in neither):
     nothing added. The liquid ones without a home are loners (ORCL 0.45, APP 0.27, SHOP 0.57, SPOT, SNPS / CDNS, RDDT, RBLX:
     decided earlier to stay "· other" with RS). To ask the user: SITM -> Optics & CPO (0.71), TTD (0.64 Enterprise SaaS),
     AMBA (0.61 AI Connectivity, on the waiting list), SIMO tracks Semi Subsystems (0.76) better than its Memory & Storage.
  Also seen that morning: rules/make_rules.py defines the sheet "E1 Earnings tab" twice (the 2nd, 4 rows, overwrites the 1st,
  longer one): the two new Earnings rows were added to the 2nd; the lost rows of the 1st are not restored (to look at).
  The user's other points that morning were not faults: FIGR was up 9% on that morning's Q3 report ("im wrong about figr");
  "Pre-mkt gap" (the first pre-market trade vs the close) can read +0.8% while "Pre-mkt chg" is +9%: offered to hide or rename
  it, not answered.
- **LIVE (the user's "go live", Thu Nov 12 2026 ~9:40 PM ET = Nov 13 02:40 UTC; test/cleanlaunch merged with main, commit
  dfd3554; picks.yml started right after): THE CHART READING, all of it.** Everything listed under "on `test/cleanlaunch`"
  below is now on main, EXCEPT radar/alerts.py, which stays as it was on main (the Nov 10 alert changes are only on the
  branch history; the alerts know none of the new reads). On top of that list, agreed and built this evening (the user's AMD
  2026 charts, in their words in tools/chart_examples.txt; rules in rules/SCANNER_RULES.md "L5 Off the list"; settings at the
  end of `L` in scanner/launch.py):
  1. **End of cycle: warning, then off** (the user chose A: "8th and 9th october end of cycle.. 12th october you take this off
     the list", "july 7th is good take off!!!"): `stalled_high()`: a high less than 1 ADR over (or under) the peak before it
     with a 1.5 ADR+ pullback between, then within 5 sessions a 1 ADR+ down day and a close under that peak and the 10 EMA ->
     "END OF CYCLE WARNING" in FRONT of the status; off on the first close under the 21 EMA. A failed breakout that still
     closes over the 21 EMA is now this warning too (before: off that day; ALAB Oct 8 2026 warning, off Oct 9). AMD: warning
     Jul 1, off Jul 7 (516.11); warning Oct 8, off Oct 12 (594.24).
  2. **Top watch** (`churn_at`, a status note): 2+ up and 2+ down days of 1 ADR+ in 10 sessions, net under 1 ADR, at a
     stalled high.
  3. **New trend start after a reset** (`reset_start`, a way back onto the list, NOT a launch rule): a start day after 3+
     lower swing highs since the 60-session top, the 5-day range at 60% or less of its widest, closing over the last lower
     high. AMD Sep 8 2026 back on at 505.74 (before: Sep 21 at 615.52). As a launch day of its own it would be a new launch
     rule: ask the user for the 2-year check first.
  4. **ADR minimum on the highest 20-day ADR of the last 63 sessions** (`adr_look`; the user: "amd never was 3.4% adr stock..
     its beta name", "agree with your adr fix"): `Arr.liquid`; the group ranking keeps today's ADR (`Arr.liquid20`).
  5. **Range stock note** (`whiplash`): the close crossed the 50 EMA 10+ times in the 60 sessions before the launch (the
     user on ANET Apr-Oct 2026: "too much whiplash"; BETA: "fell back to range"). A note only, the stock stays.
  Full-market test build before the push (Nov 11 close): 256 launches (live before: 148), 192 off waiting (105 two closes under
  the 50 EMA, 79 end of cycle, 8 failed breakouts), 21 warnings, 1 top watch, 35 range notes, 4 reset starts (M, BILL, XYZ Oct
  15, GEN Oct 29), 79 start days. `--regress`: 209 lines differ from tools/expected_reads.txt, which is NOT rewritten yet (only
  after the user agrees the reads). The user will review charts and send corrections ("you can make it better later").
  LIVE LIST after the rebuild (picks.yml run 49, 02:42 UTC Nov 13, the Nov 12 close; the first run, 48, saved nothing: the
  guard, its bars ended Nov 11): 236 launches, 5 in the 50 EMA tab, 208 off waiting (111 two closes under the 50 EMA, 88 end
  of cycle, 9 failed breakouts), 23 warnings, 32 range notes, 4 reset starts, 68 start days; AMD (a launch day Nov 12), NET
  and ANET on.
  To look at with the user: are the 21 warnings too quick (many from the Nov 4-10 dip: AEM, WPM, AU, IAG); 35 range notes
  (12+ crossings would leave 17); AMD comes back Jul 10 2026 on a flag attempt and goes off again Jul 16.
- **LIVE (the user's "go live", Thu Nov 12 2026 ~11 PM ET = Nov 13 ~04:00 UTC; test/cleanlaunch 344f16e): THE START DAY re-read**
  (the user's corrections to my alert examples, in their words in tools/chart_examples.txt; rules: SCANNER_RULES "L5 Off the
  list", the 3 rows above "End of cycle"; settings `start_down, start_down_look, start_first, red_adr, red_look, gap_keep`):
  1. **Start day = the FIRST strong close over the 21 EMA after a downtrend, the 50 EMA not needed** (`Arr.start_raw` +
     `start_day`; RKLB: "clear downtrending stock, november 9th was a start point upward.. and 10th confirmation!!!"): 6+ of
     the 10 closes before under the 21 EMA and the 21 EMA lower than 10 sessions before; only the first while its move holds
     (TTEK: "start is 15th october.. nov12 nothing"); the close over the high of every violent red candle (1.5 ADR+ down) of
     the 5 sessions before. The Start days rows carry `confirmed` (the first close over the 50 EMA) and `over_50ema`.
     Matches the user: RKLB Nov 9, TTEK Oct 15 only, LUNR Nov 9, LSCC Nov 9, AVGO Nov 10, AMD / ZM / SONO Nov 11, NAVN none.
     Differs: AMD's plain start is now Sep 4 2026 (Sep 8 stays the reset start, back on the list); APP's start Nov 4 (the
     launch stays Nov 5). Not found, as before: MRVL Sep 16, XERS Sep 17, VERX Oct 1 2026.
  2. **A first-day launch on a gap keeps half of its gap** (`gap_keep`; LUNR Nov 12 2026 gapped 17.8%, closed +7.0% at its
     low: "big big red candle", no launch) and is not inside a violent red candle (`Arr.red_inside`).
  3. **Wording**: a list stock's strong close back over the 21 EMA reads "21 EMA undercut & reclaim on a strong day", not
     "Pop over the 21 EMA" (the user: AMD Jun 11 2026 "we already have buy point of 21 ema undercut and reclaim"); the
     2-close undercut rule is unchanged (ANF).
  Test build (Nov 12 close): 238 launches, 206 off waiting, 62 start days (Nov 9: 25, the market's bounce day), 50 first-day
  launches. `--regress` 209 lines, expected_reads.txt still not rewritten.
  LIVE LIST after the rebuild (picks.yml, 04:24 UTC Nov 13, the Nov 12 close): 236 launches, 207 off waiting, 62 start days;
  RKLB and LUNR start Nov 9, LUNR no longer a launch, TTEK not in the table, AMD on the list.
- **LIVE (the user's "do alerts go live", Thu Nov 12 2026 ~11:50 PM ET = Nov 13 ~04:50 UTC; test/cleanlaunch 0dc53b4): THE ALERTS
  FOR THE NEW READS** (radar/alerts.py = main's alerts + only this; the Nov 10 alert changes stay out). Rules: SCANNER_RULES
  "L5 Off the list", the row "Phone alerts for the new reads".
  1. **START DAY alert** (`find_start`, key `:start`, any liquid stock, from 9:36): launch.json `start_watch` (`start_watch_of`
     in launch.py: tonight's stocks that can make a start day tomorrow, 379 on Nov 12: [21 EMA, 50 EMA, ADR, red candle high,
     under 200, reset lower highs, last lower high, first, tv]) -> live: over the 21 EMA, up 1 ADR+, pace 1x+ (the user answered
     "a" to "all of them or only stronger": read as ALL, 1x), over the red candle's high, top half of the day, over the 5-min
     ORH; the message has the stop (today's low), the risk in ADRs, the 50 EMA confirmation, the tags "launch size, from under
     the 200 SMA" / "NEW TREND after a reset" (high priority). After an earlier start only the reset start alerts (AMD Sep 8).
  2. **21 EMA reclaim on a strong day** (key `:ema21strong`): a followed launch that closed under its 21 EMA and over the 50
     EMA trades back over the 21 EMA on a 2%+ gap that opened over it or up 1 ADR+.
  3. **END OF CYCLE WARNING blocks the buy alerts** of a followed launch (my recommendation; the user did not answer B: ask
     again if they object).
  Simulated with the day's closing values on the 174 long-bar stocks (scratch only): Nov 6 FLY, IONQ; Nov 9 LSCC, LUNR, MPWR,
  RKLB, UBER; Nov 10 AVGO; Nov 11 AMD, IBKR, SONO, ZM; Nov 12 none; Sep 4 2026 AMD (plain), Sep 8 AMD "after a reset". NOT
  tested live: the first real session is Fri Nov 13: check alerts.json for `:start` keys and the count (a bounce day like Nov 9
  had 25 start days market-wide: if too many, 1.5x volume or the confirmation). Not done: the "follow-through" / "range stock"
  words in the alert texts; the eod_alerts.py texts.
- **LIVE (the user's "go live after test", Fri Nov 13 2026 ~12:50 AM ET = ~05:50 UTC; test/cleanlaunch 7e0677c):**
  1. **BREAKOUT OF ITS FALLING RANGE alert** (the user: "breakout of falling range its good alert"; alerts.py `find_range`, key
     `:rangebo`, daytime from 9:36, high priority): launch.json `range_watch` (`range_watch_of` in launch.py: tomorrow's line for
     every list stock, on the list or off it waiting; 56 on Nov 12) -> live: over the line and the 21 & 50 EMA, a 1 ADR+ day or a
     2%+ gap, pace 1x+ or 1 ADR+, top half, over the 5-min ORH; not for a warned stock. Simulated on closing values: INTC Apr
     1 2026, COHR Apr 8 (missed AMD and MTSI that day, not looked into), MRVL Aug 4 (+ TREX extra), FDS Oct 8, SONO Nov 11.
  2. **2nd higher low in the base: in the after-the-close message** (radar/eod_alerts.py, high priority; the user: "2nd higher
     low can be end of day trigger"), **and on the 21 EMA as well as the 50 EMA** (launch.py `hl2_on(k, t, e)`; "could be on 21
     emas as well not necessarily would be 50 ema"; same tests on either). 12 since Aug 2026 on the long-bar stocks, 7 on the
     21 EMA; the 21 EMA ones were mixed after (SMCI Sep 1 +6% in 5 sessions, TRU Aug 11 -1%, DELL Oct 13 -19%, PGNY Aug 4 -16%):
     to look at with the user. APPN Sep 28-29 2026 (the original example) not re-checked. `--regress` still 209 lines.
  None of the new alerts (start day, 21 EMA reclaim, falling range, the warning block) has run on live prices: first session
  Fri Nov 13.
- **DROPPED (see 5 above; kept for the record): the 8:45 task's instructions.** update_trigger from this session was refused ("a
  routine's instructions can be changed only from the conversation the routine posts into"). Until then the event card shows
  without the news line ("why"). The text to paste into the 8:45 conversation was given to the user in this session (4
  additions: rm event_news.json in step 1; theme_event.json in step 4; a new step 6b that searches once for the news behind the
  event and writes /root/pm/event_news.json; the 3rd argument of `finish` and pm_event.json in the publish). **First check next
  session**: whether the user did it, and whether the Nov 12 morning scan and grading ran clean (premarket_live.json has
  "events"; the Heating up column filled).
- **NOW LIVE (see the go live above; was: not live), on `test/cleanlaunch` (main merged in at 0a1c4ad, then more commits; the chart-reading work):** everything of
  the Nov 11 session plus, from this one (settings at the end of `L` in scanner/launch.py, each with the user's example):
  - **a. Falling range only on a big day (1 ADR+) or a 2%+ gap** (the user: VEEV Sep 30 and APPN Oct 8 2026 "nothing to do with
    falling range", "just building base up"): those two are gone; INTC Apr 1, AMD Apr 8, COHR Apr 8, MRVL Aug 4 2026 stay.
  - **b. First day (a launch under the 200 SMA)**: the day before under the 21 or 50 EMA, today over both, up 5%+ on 1.3x+,
    under the 200 SMA, with a 5%+ gap or a close over its 1-month high; later launch-size days are tagged "a follow-through
    day of the launch" and do not replace it (move_ended). GLOB Oct 1 (was Oct 22), FLY Nov 6, APP Nov 5, CAI Aug 6, REAL Oct
    15, PCOR Oct 5 2026. **OPEN: it dates ATRC Jun 26 2026; the user said Jul 24** ("bull flag plus break out of 200 sma"; Jun
    18 "range bound day").
  - **c. CLIMAX RISK tag** (a tag only): an 8%+ gap, 90%+ over the 200 SMA, closed in the lower half (APP, HOOD Feb 13 2025).
  - **d. Pop over the 21 EMA** (a short swing entry; MRVL Sep 4 / Sep 16 2026; the user on its 8 extra reads: "yes they look
    good").
  - **Launch attempt zone 1.5 ADRs** under a 3- / 6-month high (was 0.5): WRBY, ITT, RLAY Nov 9 2026 read "attempt". The user
    then took WRBY and VSAT back ("was launch but failed my bad... i did hindsight"): **to re-judge whether 1.5 stays**.
  - **Start day** (the user: "as long as it did breakthrough 21/50 changed the tide that day with volume its the start day",
    "usually gap up", "above 1 rvol for sure", minimums unchanged): NOT a launch rule (tested as one: 2,200 -> 3,345 launches in
    2 years, ANF Aug 3 2026 and ATRC Jul 24 lost). Built as **"start <date>" under the launch date** and a **Start days
    table** under the Launches list (launch.json trend_start..., start_days; the user: "test it 1 and 2 both makes sense").
  - **The full-market test build** (radar-tools `launchdry AAPL` on the branch, Nov 11 close, no news tags): **219 launches
    (live 148)**, 7 in the 50 EMA tab, 190 off the list waiting, 41 first-day launches, 27 attempts, 50 rows with a start
    line, **72 start days (34 not on Launches)**.
  - `--regress`: tools/expected_reads.txt was REWRITTEN at the wrap-up (Nov 13) from the live engine, with 2 AMD examples
    added to tools/examples.txt: it is the live engine's baseline, not line-by-line agreed reads; the 2-year numbers of each
    idea are in tools/chart_examples.txt ("THE TEST of a-d", "THE START-DAY TEST").
- **Open (this session), first things to check:**
  1. **The new alerts' first live session, Fri Nov 13**: alerts.json keys `:start`, `:ema21strong`, `:rangebo`; how many came
     (the user took "all" start days at 1x volume; a bounce day like Nov 9 had 25 market-wide: 1.5x or the 50 EMA confirmation
     would cut it), whether the opening-range and day-low fetches worked, the evening message's 2nd higher low. All of them
     were only simulated on closing values.
  2. **The user is reviewing an Excel file** (sent Nov 13, not in the repo: every start day, falling-range breakout, 2nd
     higher low, warning / off / back on, 21 EMA reclaim and first-day launch the engine reads on the ~175 long-bar stocks, Aug
     1 - Nov 12 2026, with the move after): expect corrections, to the test branch first.
  3. To tighten with the user's eye: the 21 EMA version of the 2nd higher low (DELL Oct 13 2026 -19%, PGNY Aug 4 -16% in 5
     sessions); the END OF CYCLE WARNING on a market dip (23 on Nov 12: AEM, WPM...); the range note's cut (10 crossings: 32
     notes; 12 would halve it); AMD back on Jul 10 2026 on a flag attempt and off again Jul 16.
  4. Asked, not answered: should a warned stock's buy alerts be blocked (built so) or sent with the warning; the reset start
     as a launch day of its own (a new launch rule: the 2-year check, ask first).
  5. Not done: "follow-through" / "range stock" in the older alert texts; the falling-range alert missed AMD and MTSI Apr 8
     2026 and sent TREX Aug 4 in the simulation (not looked into); APPN Sep 28-29 2026 not re-checked after the 21 EMA change;
     MRVL Sep 16, XERS Sep 17, VERX Oct 1 2026 still no start day; ATRC, the 1.5 ADR attempt zone (above); the Nov 10 alert
     changes stay out of main (in the branch history before 0a1c4ad's merge; alerts.py on main = the old one + this session's
     three alerts).
- **Not replayed** (no bars fetched): CDW Oct 8, DLTR Oct 14, ENOV Oct 13 / Nov 4, RAL, "KTS" Oct 13 and "PPLI" Sep 25 / Nov 3
  2026 (the last two tickers to confirm). The user's modest first days no rule catches: TREX, LYFT, POOL, SMG, TOST Oct 15,
  FBIN, PAR, VCEL Nov 4, XERS Sep 17, VERX Oct 1, PGNY Oct 7 (most were under the ADR / liquidity / price minimums that day,
  which the user keeps). Claude's reading, not confirmed: their days cluster on Oct 8 and Oct 14-15 2026, weak Nasdaq days.
- **Good to know**: `git diff main..branch` split by hunks and `git apply` is how the themes / pre-market pieces were taken
  out of the branch (tools: none saved). A `long` run replaces the file: the list is now 176 symbols (the 161 + BETA FLY GLOB
  MRVL WRBY FBIN PAR VSAT ITT RLAY + TTEK LUNR LSCC AVGO SONO). picks.yml's guard keeps an older-close rebuild out: run it
  again when the list did not change after a go live.

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

