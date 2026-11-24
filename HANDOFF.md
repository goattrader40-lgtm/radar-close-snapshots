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

## Status of the session "Radar: theme event NVDA (Nov 23)" (Mon Nov 23 2026 ~9:25 AM ET -; session_01PkbDamTXwjMVcVxZ5a25nk; in progress)

- **LIVE (the user's "go live", Mon Nov 23 2026 afternoon; branch claude/trusting-wright-vet5st, fast-forward onto main): the
  theme event's Why line names the source, and a CEO named / reinstated reads "Leadership change".** The user: "theme event
  today is totally wrong. bcs board reinstated nvda why its not on theme event". NVDA was in the event (260 stocks, #1 leader,
  +31.5% at 9:20, $165.06 vs the $125.53 close), but the Why line read "NVDA: Sector move: AI Chips & CPUs — NVIDIA Former CEO
  Jensen Huang Agrees to Senate Testimony", MU's Nov 18 news, SNDK's Sat Nov 21 story, TSM "Sector move" (from NVDA). Causes:
  the 8:45 grading wrote no pm_event.json, so the card read only pmnews.json (8:35, before the news); the 9:20 code grader
  (codegrade.json) HAD read the 8-K 5.02 "NVIDIA Board Reinstates Jensen Huang as President, CEO and Board Director", but as
  "Filing, not classified" = weak news, so sector_moves turned it into "Sector move".
  1. **radar/codegrade.py classify**: on a gap UP, a CEO / president named, reinstated or returning (LEADER_IN: the release
     headline or an 8-K 5.02's text; not a vice president, not a resignation) = catalyst "Leadership change", news C (grades
     unchanged); not in weak_news, so never a sector move, the peers' "with their own news" names it, no headline / earlier
     news replaces it. Gap-down resignations read as before ("Executive change", A/B). The alert news text (news_words) shows
     it instead of "nothing of its own today".
  2. **docs/index.html drawPmEvent** (when no pm_event.json): the newest news (codegrade.json rows / news, else pmnews.json:
     the News column's order); own news only (not Sector move / Earlier news / After earnings / no news / routine / Executive
     change, a "(headline)" only if its ts is today); the source = the first of the 8 leaders with own news ("Why: the source
     looks like NVDA: Leadership change — ..."), up to 3 other event stocks with own news, "Following NVDA (no news of their
     own): MU, AMD, SNDK, SPCX, TSM, NBIS, CRWV"; no leader with own news: "a market or sector move" + the event stocks with own
     news. A first try named ZS (earnings) the source by $ volume: changed to leaders only. The card's legend note updated.
  Tested: classify on NVDA's saved first line (-> Leadership change, C), a resignation down (Executive change, A), the pattern on
  7 sentences; the page in Chromium on today's radar-data files (stored news: "none of the leaders ..."; NVDA's row as the fixed
  code reads it: the line above), 0 page errors; `--regress` "every agreed example reads the same". Rules workbook: the news
  row and the theme event row. No 2-year check, no Launches rebuild (no launch rule). Not tested: the real 8-K through the SEC
  (blocked from the container), the Nov 11 semis day.
  **Check the next pre-market with a theme event**: the card's Why line (code news time shown), any "Leadership change" in the
  News column.
- **Offered, no answer**: the metals miners (Gold / Silver Miners, Metals & Mining 40 of 44) as their own event line instead of
  one 260-stock event with the AI names.
- **The audit (the user, Mon Nov 23 evening: "do the audit of my portal ... we had so many alerts")**: no job failed (the 9
  "cancelled" Radar day runs = newer backup starts replacing waiting ones; the day job handed over at 1:05 PM as designed);
  all 8 tabs load on desktop with today's data, 0 page errors; the evening scan of Nov 23 wrote dip.json (2,838 stocks),
  resistance.json (2,832 levels; report 8 broke out e.g. KYMR, 17 inside, 14 rejected), ep_pullback.json (10 plans, BSP new;
  no BUY that day; YOU READY 10:20 then under its EP low $51.27 -> off, as agreed), latest.json (no EP names on 1-UPDAY, no
  15-day removals), 3-SETUPS 79 (0 from START DAYS: GOLD / POWL / PWR / SPHR under the 200 SMA, ZIM ADR 2.6%, GEO under the
  50 EMA, COMP no setup), 6M % on 171 of 173 2-POOL rows. No res_* ticked in the 📈 / 📊 boxes yet (no ABOVE alerts).
  Alerts Nov 23: 650 items, ~138 phone pushes (76 before 10 AM), 435 from the 📈 / 📊 boxes (portal only), 272 of them BACK ON.
  Found, not fixed (pre-existing, told the user): on a phone the Theme event card's text runs past the screen (752px in a
  358px card) and Launches / Watchlist scroll sideways a little; the 8:45 grading graded 12 but wrote no pm_event.json (no
  event yet at 8:45, or skipped: not known). Dropped: my idea of a trend rule for 📊 (it is the not-in-trend box).
- **LIVE (the user's "Go live!", Mon Nov 23 2026 evening): the 📈 / 📊 morning boxes' BACK ON once a stock a day, only inside
  the box's own From-End window** (the user: "stop the morning's boxes back on after the boxes end time ... at most one back
  on per stock per day in their time frame"). radar/alerts.py morning_holding: the alert needs in_morning(M, now) and no
  earlier BACK ON of that stock in that box today (state mbo_back / mbo2_back); MORNING_BACK_EVERY (15 minutes) removed.
  Outside the window the stock still moves in and out of its box silently. The ⚡ / 🎯 BACK ON rules are unchanged. Tested: a
  stand-in stock flipping in and out 9:45-16:06 (one BACK ON at 9:50, the rest silent); Nov 23's alerts replayed: BACK ON 272
  -> 75, all alerts 650 -> 453 (TTAN's 8, THC 4:05 PM, SN 4:00 PM silent); `--regress` "every agreed example reads the
  same". Rules workbook: the "Alert boxes hold what holds" row. **Check Tue Nov 24**: alerts.json mbobackHHMM / mbo2backHHMM
  keys only between the box's From and End, one per stock.

## Status of the session "Radar: 7-day-low pullback column question (Nov 21)" (Sat Nov 21 2026 ~4:25 PM ET -; session_01PkbDahohHKiAyA9NYCdZQ7; in progress)

- **LIVE (the user's "go live", Sat Nov 21 2026 evening; branch claude/nice-maxwell-10pa6l merged with main): the DIP list on the
  Watchlist tab ("Dip to the 7-day low"), a screen of its own. NOT SEEN ON LIVE PRICES: FIRST CHECK Mon Nov 23 in the session
  (the list near the close), and Mon evening that the scan rewrote setups/dip.json (date 2026-11-23).**
  The user: "10 EMA above 21 above 50, and a new 20-day high in the last 10 days; wait 5-9 trading days after that high for a
  dip; buy at the close on the day the close is the lowest of 7 days but still above the 21 EMA"; "from highest, meaning wick"
  (for counting the days in this screen only: **the Days 21H column stays on closes**); "instead of these columns shouldnt we
  just build this filter and scan/screen like that"; "whole market plus switch"; "i want numbers from my morning box"; "i dont
  want it to be deeper than 25%".
  1. **The list** (docs/index.html: the DIP button next to TREND, #dip-card, dipSet / dipRows / drawDip): always 10 > 21 > 50 EMA
     and the price over the 21 EMA (trendOf, live in the session); the high = the highest HIGH of the last 21 sessions, its day a
     new 20-day high (over the highs of the 20 sessions before it), no higher high since; the user's numbers (localStorage
     `radar-dip`, an empty box = off, Reset): the high within 10 sessions, 5 to 9 sessions of dip, the close (live price) the
     lowest close of 7 sessions today included, depth at most 25%; liquidity = the 📈 box's saved numbers until changed here
     (Nov 21: $5+, $0.7B+, 700K+, $30M+, ADR 4%+, 20%+ over the 52-week low); "Only my lists" (Launches + 50 EMA undercut,
     laggards, the Watchlist lists, Start days); its own table (On = the stock's lists), Download for TradingView. No alerts;
     no other list, Launches rule or column changed.
  2. **The data**: setups/dip.json, the evening scan (scanner/launch.py write_dip, only with --watchlist, after
     write_resistance): {date, rows: {SYM: [sessions since the high, the high, its date, 1 = a new 20-day high on its day, the
     last 15 closes]}} for every stock the scan loads (2,883 on Nov 20; not the $2T+ stocks: told the user). A session newer
     than the file (live, or a newer stocks.json) = one more day at the live price; a price over the high = out. The file on
     main now is the branch's dry run (radar-tools `setupsdry` also publishes radar-data dip_dry.json), the Nov 20 close.
  Nov 20 close: 9 of 407 liquid stocks pass: PPLI (high 44.37 Nov 12, 6 days, -6.4%), FLYW, SHAK (on no list), SARO, FBIN, PRKS,
  REZI, XNCR, REPL (-19.0%); 7 of 9 within 0.6% over the 21 EMA; 2 biotech (XNCR, REPL).
  Tested in a browser with the dry file (desktop / phone, each number changed / emptied, Only my lists 140 searched, sort,
  Reset, the other lists and 5 tabs, 0 page errors), again after the merge with main (the 1-UPDAY / START DAYS session had gone
  live). Rules workbook: 1 row. No 2-year check (a screen). The Columns "+ add" button attached itself to the table: not tested.
- **Offered, no answer**: a "Leave out biotech" tick box (the user: "i dont want to see bunch of biotech stocks"); a study of
  which depth worked best over 2 years for this setup (the user asked "10-15 is sweet spot? what you recommend": not measured).

## Status of the session "Radar: Resistance alerts box (Nov 21)" (Sat Nov 21 2026 ~1:15 PM ET -; session_01PkbDakoHKZ2tgMSvkWcZxx; in progress)

- **LIVE (the user's "Go live, and i want this to be ready for monday morning", Sat Nov 21 2026; branch claude/friendly-carson-ia63f6
  merged with main): the resistance levels as a FILTER of the two morning boxes (no new box), the all-time high, and a silent
  end-of-day report. NONE OF IT HAS RUN ON LIVE PRICES: FIRST CHECK Mon Nov 23 from 9:35 AM ET.** The user first asked for a third
  box (NEAR / INSIDE / BREAKOUT, its own sound), then: "maybe we dont need add another box ... you add those options here";
  "you are just adding new filter above 1m high/3month/6/9/52w/ath, and i choose which one, when other filters aligns with it it
  fires"; "stock can open up above 1month high, it would have to wait to breakout of orh to trigger ... at orh both states has to
  be true above the level and orh"; "i dont need inside alerts ... silent and end of day report"; "im only interested in breakout
  level"; "here im only requesting we work on alerts" (the Resistance column is NOT changed).
  1. **📈 and 📊 settings**: tick boxes "Above: 1M / 3M / 6M / 9M / 52W / ATH / Broken support" and "Only my lists" (alerts/
     morning.json / morning2.json keys res_1m ... res_bs, lists_only; all off by default = the boxes exactly as before: 1,200
     random cases identical to the old code). A ticked level: the price over the TOP of that range (its highest high), the range
     overhead at the last close, at the same moment as every other setting incl. the ORH (radar/alerts.py RES_KEYS,
     ticked_levels, morning_alert; morning_static leaves out stocks with no ticked level in reach, so fast.py reads fewer).
     A joined range ("1m/3m") counts when any label is ticked. Only my lists = Launches (+ 50 EMA undercut, laggards),
     3-SETUPS, Start days, the Watchlist's lists (list_names).
  2. **The alert**: title "ARM MORNING BREAKOUT +4.1% · ABOVE 1M"; the text adds "above its 1M $a-b", "also cleared ...", "next:
     3M $a-b, +x%", the trend tag at the live price (FULL / NEW TREND / CAUTION / NO TREND, the Watchlist tag's rule); the
     voice "Morning breakout, V E R X, above 1 month 3 month, volume 1.8 times" (docs/index.html sayOf; an example in the sound
     test). Same sound, one alert a stock a day (the user: "one alert.. the way its now"); it holds in its box only while over
     the level; BACK ON as before.
  3. **The levels**: setups/resistance.json, written by the evening scan (scanner/launch.py write_resistance, only with
     --watchlist) for every stock it loads (2,879 on Nov 20; the $2T+ stocks are not in the scan: NVDA, AAPL ... have no
     levels, so a ticked box never fires on them: told the user): the Resistance column's ranges without its buy-point floor,
     plus the ATH. radar/day.py resistance_args reads it once a job and passes --resistance to fast.py and alerts.py.
  4. **The all-time high**: radar/ath.py (Yahoo monthly range=max, then the daily bars of the top months: highest close to
     highest high; a reference close so the scan rescales after a split) -> radar-data ath.json; .github/workflows/ath.yml every
     Saturday 13:17 UTC and radar-tools `ath` (`ath SYM ...` -> ath_test.json). First full run Nov 21: 3,208 stocks, 0 missing
     (AZTA 124.15-124.79 Nov 2021, VERX 58.95-60.71 Feb 2025, ARM's = its 52W: "6m/9m/52w/ath"). Without a row: a stock listed
     inside the 2 years gets its bars' high, any other none.
  5. **🧱 Resistance at the close** (Alerts tab, folded, silent): broke out / inside / rejected at the close vs the levels
     overhead the day before, the 📈 box's price / liquidity / ADR / 52W low / only-my-lists settings, no trend boxes, no ORH.
     Nov 20: 0 broke out, 1 inside (ENR), 17 rejected (KVYO, XERS, VIA, TDC, VCEL ...).
  **For Monday (the user's ask)**: the evening scan doesn't run on weekends, so setups/resistance.json on main is the branch's
  dry-run file (radar-tools `setupsdry`, the Nov 20 close, with ath.json): exactly what the scan writes. From Mon Nov 23 evening
  the scan writes it itself. **Nothing is ticked yet: the user ticks levels in the boxes and Saves.**
  Tested: stand-in minute runs (ARM's levels, 1M ticked: 9:36 $327 over the 1M top 325.48 under the ORH 330 nothing; 9:38 $331
  fires; 9:45 $324 out of the box; 10:05 back on; 3M ticked: $331 nothing, $337.50 fires); the page on desktop / phone, 0 page
  errors, the voice captured; `setupsdry` on the branch: launches 134, setups3 66, start_days 27, ema50_undercut 12, watch and
  ep_watch identical to main's; `--regress` "every agreed example reads the same". Rules workbook: 2 rows. No 2-year check
  (an alert filter), no Launches rebuild (no launch rule changed).
  **Check Mon Nov 23**: the boxes' level ticks once saved (alerts/morning.json res_*), a "· ABOVE" alert and its voice, the job
  log (alerts.json) without "no resistance levels"; Mon evening: setups/resistance.json date 2026-11-23 and its report on the
  Alerts tab; Sat Nov 28: ath.yml ran.
- Data: long_bars.json on radar-data had only SPOT / SPY (another session's fetch); re-run `long` with the 24 example stocks +
  VERX (30 symbols now: the 153 of the morning are gone; re-fetch others when needed).

## Status at the end of the session "Radar: 1-UPDAY / 1-EP/GAP / START DAYS -> 3-SETUPS (Nov 21)" (Sat Nov 21 - Sun Nov 22 2026 ~11:45 PM ET; session_01PkbDaj2rqMQ1qnsD48H7ev)

**In one line: two changes live on main (the Watchlist tasks 1-3; EP PULLBACKS, the list and the READY / BUY alerts), a long EP
trading study (the user's playbook, plays 1 / 1b / 4 / 3b, in their Excel), the study tools on the session branch only. NONE OF
IT HAS RUN ON LIVE PRICES OR IN AN EVENING SCAN YET. FIRST THINGS MON NOV 23: during the day, alerts.json keys :epr10 / :epr21 /
:epb10 / :epb21 (if a planned name touches: BRBR, ENR on the 10 EMA; BRBR, ENR, GKOS, HLF, PCOR, PGNY, REZI, UPBD, YOU on the
21 EMA), the ⚡ box and the Watchlist's EP PULLBACKS "Watch now" view; after the evening scan, setups/ep_pullback.json dated
Nov 23 (its bought list from the day's BUYs), setups/latest.json (1-UPDAY without the 1-EP/GAP names, no "15 trading days" in
changes_today) and 3-SETUPS rows with source "START DAYS".**

- **How it went with the user (for the next session)**: the study cost them patience: numbers changed between tables and
  between Excel copies (different exit rules per table, an old file with the same name), and the user found a data flaw I
  should have caught (DELL Feb 27 / Mar 10 / Mar 31 2026 read against their 15-minute chart: "you need to analyze and check your
  datas"; "to much back and forth, you could have done way better"). So: one exit rule for every table, one file with a new
  name per version, every number recomputed when a rule changes, and the user's own example charts checked against the data
  before a table goes out.

- **LIVE (the user's "go live", Sun Nov 22 2026 ~11:40 PM ET, 7ca443e on main; Launches rebuilt by picks.yml): EP PULLBACKS,
  the 10 / 21 EMA first touch after an EP day, as a Watchlist list and live alerts** (the user, Nov 22 2026 evening ET; the code comments say Nov 23: "show this live,
  this 10 ema and 21 ema things as they happen as alert, or current status when its true"; "we should get alert when its
  ready ... then when its in true state it could alert, buy point confirmed"; "it has to say in alert message ep pullback buy
  10 ema"; box: "shouldnt be good to be in same box with episodic pivot" -> the ⚡ box). The rules are the playbook's plays 4
  and 3b of this session's EP study (below), one place: **radar/epp.py** (used by the alerts and the tests).
  1. **The plays.** EP day = the 1-EP/GAP rule, gap at most 20%, no biotech / pharma (stocks.json industry), the newest EP of
     the last 30 sessions. **10 EMA**: within 10 sessions, no daily close more than 5% under the EP day's close since; the first
     touch of the rising 10 EMA (today's low at or under its value at the last close); READY = touched it AND traded under the EP
     day's close (the dip; without it 64 trades -28R; a stop under the EP close only got them to ~0R); BUY = the first 15-minute
     candle from READY on closing over the 10 EMA and VWAP, not more than 5% under the EP close (268 trades 29% won +0.70R +187R
     worst drop 24R; 5-minute candles +0.58R, 1-minute +0.33R, 10-minute +0.49R (asked Nov 22), 30-minute +0.58R, without VWAP +0.37R). **21 EMA**: within 30 sessions, never a trade
     under the EP day's low; READY = the first touch of the rising 21 EMA; BUY = the first 15-minute candle closing over the 21 EMA
     and VWAP while today's low holds over the EP low (276 trades 26% won +0.62R +171R; 5-minute +0.36R, 10-minute +0.35R, 30-minute +0.64R but 249 trades +158R); under the EP low first
     = off, silently (they made +68R but nearly all in 2025, -44R without the best 5: not in the rule, no alert). Stop = today's
     low at the buy; exits 1/3 at +10%, breakeven, the rest on a daily close under the 21 EMA. Not the 3:45-4:00 candle. One try
     per EP and EMA. The user's base rule for the 10 EMA (no close under the base the EP broke) was tested: better alone
     (+199R, drop 17R) but less money in the full set in 6 of 9 account setups: not used (the playbook's "Play 4 vs 4b").
  2. **Evening**: scanner/launch.py write_ep_pullback -> **setups/ep_pullback.json** (the --watchlist run of scanner.yml; per
     stock: ep, c0, l0, gap, days (counting the next session), p10 / p21 {level = the EMA at the close, up, floor, status
     wait / flat (EMA not rising: a touch is no trade) / used (touched) / out / late}); ep_bought: the BUY alerts of the day
     (scanner.yml now passes radar-data alerts.json, --alerts) and the last file's, followed with the daily bars to the exit
     (the buy day's low under the stop = stopped; the +10% sale from the next day on: the daily bar can't order the buy day's
     high), a closed trade kept 5 sessions. settings.json **ep_pullback** (e10_max_sessions 10, e10_floor_pct 5,
     e21_max_sessions 30, max_gap_pct 20, skip_industries, near_pct 3, first_sale_pct 10). The committed file is the Nov 20
     close's plan (Mon Nov 23): 10 EMA BRBR, ENR; 21 EMA BRBR, ENR, GKOS, HLF, PCOR, PGNY, REZI, UPBD, YOU.
  3. **Live**: radar/alerts.py **find_epp** (day.py epp_args passes the file to the 5-minute and the 1-minute jobs): a name's
     Yahoo 1-minute chart (chart_bars_today, with volume for VWAP) is read once its price is within 5% over the level (at most
     40 a run; the 1-minute job only re-reads names already READY). Keys SYM:epr10 / epr21 (READY, heads-up) and SYM:epb10 /
     epb21 (BUY, trigger, TRIGGERS): "SYM EP PULLBACK READY - 10 EMA" / "SYM EP PULLBACK BUY - 10 EMA $px" with the stop, the
     risk, the first sale, the EP day; state["epp"] keeps each BUY (found again every run while the price is over its stop, so it
     holds in its box; under it: lost) and SYM:off21. Exempt from the 3-SETUPS 200 SMA filter (an EP pullback can be under it).
  4. **Page** (docs/index.html): the Watchlist list **EP PULLBACKS** (its own card like DIP): tonight's plan, "Watch now only"
     (on by itself during market hours: BUY / READY from today's alerts.json, NEAR = within near_pct over the level from the live
     price), the Bought table; the ⚡ box takes the READY and the BUY (isTrigger, BOX_OF, place(): a READY heads-up stays in ⚡,
     a BUY whose stop is hit steps down to 👀 with its note), filed under the Watchlist tab, the voice "E P pullback buy, 10 E M A,
     D E L L". Rules workbook: W1 and A1 rows.
  Tested: epp.check vs the study's own logic on all 1,539 touch days (1,514 identical, 25 = a missing last minute of a 15-minute
  candle: the live one uses the candle's last trade); the live job simulated every 5 minutes on DELL Mar 10 2026 (READY 9:45,
  BUY 10:30 141.44 stop 137.50) and Mar 31 (READY 11:35, BUY 12:45 159.07 stop 155.37) = the study; the evening file on the Mar 9
  / Mar 30 bars (DELL waiting at 140.56 / 156.73); ep_bought on DELL Mar 10 (1/3 Mar 16, out Jul 2, +44.0R vs the study's +43.9R);
  alerts.py main twice on stand-in files (one push, holds, nothing repeated); launch.py --watchlist end to end (the file next to
  dip.json); the page in Chromium with stand-in session data (plan, watch now, ⚡ box, a stopped BUY down to 👀, an off name):
  0 page errors; `--regress` "every agreed example reads the same". No 2-year check (the study is its test).
  **Check Mon Nov 23**: alerts.json items with :epr / :epb keys (if any name touches), the EP PULLBACKS list on the page; the
  evening scan: setups/ep_pullback.json dated Nov 23, bought filled from Monday's BUYs. Not built: a phone push for NEAR (the
  list only).
- **The EP trading study (Nov 21-22, research; the user's playbook)**: Jan 2023 - Nov 2026 (2022 left out, a bear market), real
  stops, the user's exits. The set to trade, all intraday: **play 1** morning 3-minute ORH (yesterday over the 50 EMA, gap
  5-20% opening over the 1-month high and the 200 SMA, the ORH buy at least 5% under the 3-month high), **play 1b** (yesterday
  under the 50 EMA and the 200 SMA, the gap opens over both and the 1-month high, no 3-month room), **play 4** (10 EMA) and
  **play 3b** (21 EMA) as above; same stock: one open trade per type (EP-day buy, 10 EMA, 21 EMA), a third only after both
  sold 1/3. 749 trades +0.82R +612R worst drop 29R; $50k at 0.5% a trade, 2% open-risk cap, cash: $158.6k (drop 11.2%).
  Skips: a stock under its 50 EMA but over its 200 SMA yesterday; play 2 (the close buy) is the close version of 1b. The Excel
  (EP_playbook_FINAL_Nov22.xlsx) was sent to the user (the scratchpad is not kept); the study's test tools stay on the session
  branch (radar/probe_orh.py, probe_raw.py, study.sh, history/orh_*.json), not on main.
- **Answered, no change**: 10-minute candles for the EP pullback buy (the user, Nov 22: "have you tested 10 min?"): no better
  (numbers in the EP PULLBACKS entry above), 15 stays; "BUY" is one event in three places: the phone push, the ⚡ box on the
  Alerts tab, the "Now" column of the Watchlist's EP PULLBACKS list (then its Bought table). The user's own trading bot for
  plays 1 / 1b (one bot rule for both; only play 1 has the 3-month room row): the rows were worded in chat, nothing built here.
- **Test only** (branch claude/gifted-mendel-civxei, for the study, not for main): radar/probe_orh.py, probe_bars.py,
  probe_raw.py, radar/study.sh and its `orh / bars6y / raw` line in radar-tools.yml, history/orh_*.json (1-minute SIP bars of
  the EP days and the touch days); the branch radar-study holds the 1-minute data. The scratchpad scripts and the Excel's
  builder are not kept (the Excel EP_playbook_FINAL_Nov22.xlsx is with the user).
- **Open, each needs the user's go**: (1) the morning EP alert lined up with plays 1 / 1b (yesterday over / under the 50 EMA,
  the 200 SMA and the 1-month high at the open, the 3-month room for play 1: offered as a separate change, not asked for);
  (2) a phone push for NEAR on EP pullbacks (the list only now); (3) the study files on the public repo's branches (the session
  branch, radar-study): keep or delete (asked, no answer).

- **LIVE (the user's "tasks 1-3 go live", Sat Nov 21 2026, merge ee34096 on top of the other session's be57c80; Launches rebuilt
  by picks.yml): the three Watchlist changes agreed in the session "watchlist restructuring (Nov 21)". They show from the Mon
  Nov 23 evening scan (run.py and launch.py --watchlist run only then).**
  1. **1-UPDAY: no 15-day rule** (settings.json lists.new_mover_days_without_setup 0 = off; run.py skips the check when 0). Off
     only on 2 closes under the 50 EMA, a close under the FIRST day's low, or the user's x.
  2. **A stock on 1-EP/GAP is not shown on 1-UPDAY** (run.py write_outputs: hidden in latest.json / the TradingView file /
     history, kept in state.json with its own line, so it shows on 1-UPDAY again if it leaves 1-EP/GAP and still holds its
     first-day low). Nov 20: 18 names hidden, 94 -> 76. 3-SETUPS already read those names from 1-EP/GAP (no change there).
  3. **START DAYS feeds 3-SETUPS** (launch.py setups3 + newest_start(), the same rule as the Start days list; removed_starts_of
     reads the user's x on a start day). Read from the start day; a stock already on 1-EP/GAP, 1-UPDAY or 2-POOL keeps that
     list's day; the 3-SETUPS rules unchanged: ADR 4%+ and a close over the 200 SMA to come on (my suggestion (a), taken with
     the user's "1-3 do it": a start under the 200 SMA joins once it closes over it). Nov 20 dry run (radar-tools setupsdry on
     the branch): the same 66 names (the only new candidate, CXW, had no setup); Start days 27 and Launches 134 identical. On
     the Oct 23 bars with start_from opened to June: 12 of 100 holding start names came on (RHI, ARXS, RBRK triggered; ZYME,
     CAI, FROG Ready; SHOP, NRIX, SYRE, ASST, BHVN, MRNA setting up); the x keeps one off.
  Tested: backfill Sep-Oct 2026 main vs branch (no 15-day removals, EP names only on 1-EP/GAP), `--regress` "every agreed
  example reads the same" (before and after the merge), the page 0 errors with the new rule text. Rules workbook: the 1-UPDAY,
  1-EP/GAP, START DAYS and 3-SETUPS rows. No 2-year check (list rules). **Check Mon Nov 23 evening**: setups/latest.json counts
  (1-UPDAY without the EP names, no "15 trading days" in changes_today), 3-SETUPS rows with source "START DAYS".
- **SPOT / the EP list ADR test (answered, no change; the user: "so you advise no change on it??", answered yes)**: SPOT Oct 22
  2026 (gap +6.8%, +11.1%, 3.2x) missed 1-EP/GAP only on the ADR that day, 3.35% < 3.5% (3-month high 4.54%). Jan 2 2025 - Oct
  23 2026: the list 1,278 EP days, 25% ran 20%+ (close), 36% broke the EP low in 5 days; the Launches-style 3-month ADR would add
  194 days (3.5%) / 119 (4%), 5% ran 20%+. The list for the user's chart check: tools/ep_spot_check.xlsx (first sheet = the 119).
  Offered if they find tradable ones: let them in only when also on Launches.
- **The EP trade study (answers only, nothing built)**: today's 1-EP/GAP rules, 1,251 EP days Jan 2025 - Oct 23 2026, bought at the
  EP day's CLOSE (no minute bars for the 5-minute ORH entry), stop the EP day's low (median risk 6.4% = 1.1 ADR): up 20%+ at a
  high within 20 sessions 30%, failed (a close under the pre-EP close within 20) 35%. Exits: half at 2 ADR, a quarter at +20%,
  the rest a close under the 21 EMA: +236R (+0.19R a trade, 35% winners, 64% full stops; last 12 months -46R, Jan-Oct 2025
  +282R). The user's plan (1/3 at 2-3 ADR or 10-20% within 5 days, the rest breakeven, trail): the 21 EMA trail +256R to
  +317R, "the higher of the 10 / 21 EMA" +105R to +158R; best +20% / 3 ADR with the 21 EMA (+317R / +311R, +0.25R); +15% with
  the 21 EMA the only one positive in the last 12 months (+4R). Scripts were in the session's scratchpad (not kept).

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
- **AGREED, NOT BUILT (the user's gos, Sat Nov 21 2026 afternoon; the message was interrupted before any build: test branch
  first, as always). FIRST THING NEXT SESSION:**
  1. **The 15 trading days off 1-UPDAY too** ("take 15 day rule of for upday as well"; off 1-EP/GAP since Nov 14). scanner/run.py
     step: the `name == "1-UPDAY" ... new_mover_days_without_setup` line. Since Oct 5 it removed 5 (ADMA, EFOR, FDS, PCOR, SGRY).
  2. **START DAYS feeds 3-SETUPS** ("ok feed it to setups!!!", "if useful then it needs feed something too"). Today it feeds only
     the START DAY alert, the "start <date>" under a launch and the reset way back onto Launches; 19 of the 27 start names are not
     in 3-SETUPS, 5 are on no feeder (AAON, CXW, IMVT, SPHR, ZIM). **Open inside it**: 3-SETUPS needs a close over the 200 SMA
     and ADR 4%+ to come on, 9 of the 27 are under the 200 SMA: asked twice (let them in, or wait until over), the user said
     "1# agreed" without choosing: ask once more before building.
  3. **A stock on 1-EP/GAP is not shown on 1-UPDAY** ("i thought anything in ep/gap isnt shown in upday - i agree with that
     recommendation"); 18 names are on both now (from different days; the same day already goes to 1-EP/GAP only).
- **Answered (the user's 5#, Nov 21): which 3-SETUPS status is actionable.** They meant "where i have to check in setups whats
  status is actionable? ready or triggered", not a new list (I first read it as a request for one place: wrong). The answer
  given: **Ready** = tomorrow's breakout candidates (base top, bull flag / pennant line within 0.7 ADR over the close);
  **Triggered today** = a buy point fired today, and the ONLY place a pullback entry shows (retest held, 21 EMA retest /
  undercut & reclaim, push: their trigger is the close back over the level, so they never show as Ready); **Setting up** =
  forming, watch only. Daily: Ready first, then Triggered today. No build asked.
- **SPOT, my mistake and a find (explain first, no change agreed)**: the user asked whether the 1-EP/GAP "gap given back" rule
  fails SPOT. I first answered on the wrong gap (Oct 30 2026, +3.2%): the user, "your spot gap was wrong". The EP gap is **Oct 22
  2026**: close 525.34 the day before, open 561.29 (+6.8%), close 583.66 (+11.1%), 3.2x. The gap-given-back rule would NOT
  have failed it (lowest close since: 538.40 on Oct 28, its agreed retest day, over 525.34; no close under the 50 EMA). What
  kept SPOT off 1-EP/GAP altogether: **the Watchlist's ADR minimum of 3.5% is tested on that day's 20-day ADR (3.35% on Oct
  22)**, while Launches tests the highest 20-day ADR of the last 63 sessions (4.54%: L adr_look, the user's Nov 12 rule "amd
  never was 3.4% adr stock"), so SPOT launched Oct 22 and never came on the EP list. To propose: the same ADR test on the
  Watchlist lists (scanner/screens.py standard); measure what it adds first.
  **Resolved (the user: "spotty is not on my ep lsit")**: they meant why SPOT is NOT on the EP list; I misread it as "why is it
  on" and wrote a wrong first line into the prompt I gave them (corrected). The issue to fix is the ADR test above: the user
  wants SPOT-type EPs on 1-EP/GAP.
- **Decided with the user this session (no build needed)**: the Watchlist feeds stay as they are ("we are only interested in
  fast movers thats why setup feeds from updays and fast movers 1 month 3 month and 6 months": NO whole-market trend list, NO
  feed change); nothing is dropped (1-UPDAY, 2-POOL stay); the 2-POOL momentum numbers are NOT changed (25% / 50% / 100% was
  asked, then left: "without checking anything, the way they are now"); **the 1-EP/GAP list rules stay as they are** ("i agree
  with your recommendation regarding ep list.. we keep it as is"): on 629 list EP days of 2026 no gap / volume number raised
  the 31% that ran 20%+, a 2.2x volume rule lost 12 winners (AEHR Mar 31 +176%) and a 21-day-closing-high rule 31.

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
| 📈 Morning breakouts (portal only) | radar/alerts.py check_morning (any stock, 9:35-10:30 by default); the user's settings and + Filters: alerts/morning.json on main (Alerts tab, Save); the level ticks read setups/resistance.json (evening scan) and radar-data ath.json (ath.yml, Saturdays); replay: radar-tools `morning` |
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

- Moved to the archive on Nov 22 (check there before raising one):
  - First checks Mon Nov 23 (its seven alert changes never seen on live prices): alerts.json `:mbo2` / `mbatch2` / `thm:` /
    `<kind>backHHMM` keys, `:early` keys with "gapping" in the title from 9:31 (the followed names too), the first `grp:` at
    9:40 or later, levels.json rows with 5 values from 9:33; ask the user how 📊 and 🔥 behaved, alerts/morning2.json once
    saved ["Status at the end of the session "Radar: theme chips on Today's gainers (Nov 18)""].
  - Still open there: the 15% / 3x launch exception (unanswered: keep the liquidity minimums, how big a "big gap" is, the
    2-year check), first days over the 200 SMA too, a click on "Added" sorting the Watchlist, the broken-support buy-point
    tag and highs older than 52 weeks (offered, no answer); from its first part: the coil alert to look at later, the
    pre-market blind spot 9:10-9:30, young listings (52-week low / 200 SMA), the code grader's "no daily bars" bug
    ["Status at the end of the session "Radar: MBGL / AVEX miss (Nov 12)" (Thu Nov 12 - Sat Nov 21 2026)"].
  - The code grade next to Claude's: the 2-week check-in ran Nov 18, the user's decision is not recorded (see the line
    further down); stars x code grade once there is history ["Code grade next to Claude's (LIVE Nov 4 2026 ...)"].
- Moved to the archive on Nov 21 (from the sessions below; check there before raising one):
  - EPAM passed every morning-breakout filter at 10:35 on Nov 20 and did not alert (the box went ORH-3min -> ORH-5min at 10:14):
    replay it with radar-tools `morning` ["a chat session outside the Radar sessions (Fri Nov 20 2026 ...)"].
  - The first BACK ON alert after its go live not yet seen in a browser ["a chat session outside the Radar sessions (Thu Nov 19
    2026 ...)"].
  - The user to decide: the alert reason switched on (after ~3 sessions), written maps for AVGO / TSM / MU / SPCX, niches for
    other themes, unscheduled news events ("later"); the Earnings guidance reader misread TGT Nov 18 (not fixed); the Nov 19
    first checks (PANW card, WMT / BABA / PDD rows, GAP / ROST / KEYS) not confirmed ["Radar: gap news and NVDA ecosystem
    links (Nov 17)"].
  - Themes moving DOWN in their own box; BACK ON alerts on the phone ("later"); a cap or market filter if 🔥 fires too often;
    the Nov 19 first checks of its five alert changes not confirmed ["Radar: theme chips on Today's gainers (Nov 18)"].
  - The BACK ON alert for ⚡ and, at 1.5x volume, 🎯 was built in the session "theme chips on Today's gainers (Nov 18)" (the
    "offered, no answer" two lines below is done for those two boxes).
  - Offered, no answer: Rel vol 0.7x, an 11:00 end, no 10 > 21, a group-move alert for the morning box; the user's neoclouds
    screenshot (4%+ not seen in our data) ["Radar: Cybertruck morning breakout alerts (Nov 18)"].
  - Offered, not taken up: dropping the 50 EMA test for 1-EP/GAP / 1-UPDAY; not seen: a real START DAY alert on live prices
    ["Radar: why AVEX isn't on the EP watchlist (Nov 17)"].
  - Offered, no answer: the BACK ON alert for the other boxes; one more read of all the opening ranges ~9:45 ["Radar: opening
    range 1/2/5-min choice (Nov 17)"].
  - Offered, no answer: "back on <date>" under a launch date on the Launches row (BILL); a tighter reset (BILL's 3 lower highs)
    ["Radar: Start days stay on until they fail + 0.8 ADR start (BILL, Nov 16)"].
  - Offered, not built: a 1% movers threshold inside the 5-minute gap; seen, not changed: a followed stock's plain breakout
    alert on a gap-out-of-base day (KVYO 9:35), the 1-minute checks stopping 12:00-3:00 ["Radar: missing earnings on the list
    (Nov 16)"].
  - To build in a new session (agreed in principle): the news reason on after-the-open alerts (Yahoo as a second source, its
    times captured first); asked, not done: a 2-3 month history check of group moves under 5% at the open; for another
    session: a GAP retest rule (AEHR Feb 12-17 2026); not done: the "nothing traded above it for N sessions" text (WRBY Nov
    11); told, no answer: AZTA Nov 16 reads "retest held" (the user: "just confirmation") ["Radar: AZTA breakout alert (Nov 16)"].
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
- The Nov 18 5:40 PM ET check-in (code grade vs Claude grade, 2 weeks) ran; the user's decision (code only, code + Claude,
  keep Claude) is not recorded here: ask.

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

