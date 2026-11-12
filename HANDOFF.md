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

## Status of the session "Radar: full portal review, build continued (Nov 12)" (Wed Nov 11 2026 evening - night ET; session_01PkbDajtNcuGe22aVKWcF77)

**Read first, as before: tools/chart_examples.txt and tools/user_answers_2026-11-10.txt ON THE BRANCH test/cleanlaunch**: this
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
- **NOT DONE, the user has to do it: the 8:45 task's instructions.** update_trigger from this session was refused ("a
  routine's instructions can be changed only from the conversation the routine posts into"). Until then the event card shows
  without the news line ("why"). The text to paste into the 8:45 conversation was given to the user in this session (4
  additions: rm event_news.json in step 1; theme_event.json in step 4; a new step 6b that searches once for the news behind the
  event and writes /root/pm/event_news.json; the 3rd argument of `finish` and pm_event.json in the publish). **First check next
  session**: whether the user did it, and whether the Nov 12 morning scan and grading ran clean (premarket_live.json has
  "events"; the Heating up column filled).
- **NOT LIVE, on `test/cleanlaunch` (main merged in at 0a1c4ad, then more commits; the chart-reading work):** everything of
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
  - `--regress` on the branch: 209 lines differ from tools/expected_reads.txt (NOT rewritten); the 2-year numbers of each
    idea are in tools/chart_examples.txt ("THE TEST of a-d", "THE START-DAY TEST").
- **Still to do before the chart reading can go live**: the alerts (radar/alerts.py) know none of it and still say "with
  caution"; the user's decisions (the Launches list 148 -> 219, ATRC, the attempt zone, d's reads); rewrite
  tools/expected_reads.txt once agreed; merge main again and re-test the page.
- **Not replayed** (no bars fetched): CDW Oct 8, DLTR Oct 14, ENOV Oct 13 / Nov 4, RAL, "KTS" Oct 13 and "PPLI" Sep 25 / Nov 3
  2026 (the last two tickers to confirm). The user's modest first days no rule catches: TREX, LYFT, POOL, SMG, TOST Oct 15,
  FBIN, PAR, VCEL Nov 4, XERS Sep 17, VERX Oct 1, PGNY Oct 7 (most were under the ADR / liquidity / price minimums that day,
  which the user keeps). Claude's reading, not confirmed: their days cluster on Oct 8 and Oct 14-15 2026, weak Nasdaq days.
- **Good to know**: `git diff main..branch` split by hunks and `git apply` is how the themes / pre-market pieces were taken
  out of the branch (tools: none saved). A `long` run replaces the file: the list is now 171 symbols (the 161 + BETA FLY GLOB
  MRVL WRBY FBIN PAR VSAT ITT RLAY).

## Status at the end of the session "Radar: full portal review, build (Nov 11)" (Wed Nov 11 2026 afternoon - evening; session_01PkbDajNX1kVmKBSagSkYW9)

**Read first, before anything else: tools/chart_examples.txt and tools/user_answers_2026-11-10.txt ON THE BRANCH
test/cleanlaunch** (`git show origin/test/cleanlaunch:tools/chart_examples.txt`): the user's 51 marked buy days, and from
this session their clean charts (DOCU, AXTI Feb 20 - May, COHR's buy days), their 7 would-not-trade charts (XMTR, NBIS, NVDA,
ALAB, MU, COHR May-June, CAI before Aug 6) and their answers, in their words, each with the engine's read. Never ask again
for what those two files answer. tools/blindtest/answers2_2026-11-11.txt: the blind test 2 marks (22 right, 17 wrong, 3
unsure; launch days 7 / 7; 13 of 18 charts "not clean").

- **Nothing went live in this session.** Everything is on **`test/cleanlaunch`** (the chart-reading code as of 1096495; later commits are examples and handoff only). It has main up to
  1dd16e4; main moved on since (the Earnings calendar's Yahoo fallback, c3ebfb1: it touched radar/theme_adds.json and
  rules/make_rules.py, which this branch changed too). **Before any go live: merge main in, re-run
  `python3 rules/make_rules.py`, `--regress`, and re-test the page.** tools/expected_reads.txt was NOT rewritten (the
  replay differs on ~100 lines by design; the user agreed some of them, not all: see "the proof" below).
- **1. Pre-market: theme event line + theme bounce list** (the user's Nov 11 "I accept your proposal"; built, tested on
  the Nov 11 9:25 scan). radar/theme_event.py: an AREA (a theme category of themes.json, else the sector) has an event when
  8+ of its tradable stocks (market cap $700M+, 700K+ shares and $20M+ a day, ADR 3%+; no 50 EMA / 52-week-low rule) and
  30%+ of them move 5%+ the same way; pmlive.py puts `events` into premarket_live.json (day.py passes themes.json);
  premarket_build.py prepare writes theme_event.json, finish takes an optional 3rd file (event_news.json: {"why",
  "sources"}) -> pm_event.json. The page (docs/index.html): the card "Theme event" at the top of the Pre-market tab and
  the bounce list under it (Pre vs 21 / 50 / 200, Close vs 21 / 50; "✔ over both" first). Nov 11: 93 stocks, AI & Semis
  63 of 83, AI Infrastructure 30 of 62; 7 back over both EMAs (ENTG, AVGO, PLAB, AMD, ANET, WOLF, LSCC). Grades and the
  graded list unchanged. **At go live the 8:45 task (trig_01EhkhyMeC5yC4H4sFxsqUVQ) needs one more step**: read
  /root/pm/out/theme_event.json; when it is not empty, search once for the market / sector news behind it, write
  /root/pm/event_news.json, pass it as the 3rd argument of `finish`, and publish /root/pm/out/pm_event.json too.
- **2. Chart reading, built in scanner/launch.py** (settings in `L`, each with the user's example in the comment):
  - **Launch attempt**: a launch-size day closing under its 1-month high (RPD Sep 14, ATRC Jul 24 2026), or within half an
    ADR under a 3- / 6-month high (RHI Oct 23 2026, AEHR Feb 11 2026: the user, "attempt / launch"); not when it closed
    over every candle body of 6 months and within 1% of the wick high (**GMAB Aug 7 2026 stays a launch**: "gap out of
    base breakout and launch and episodic pivot... popped out of consolidation line"). The close over the high reads
    "confirms the launch attempt" (AEHR Feb 24). **AEHR Jan 16 2026 is NOT an attempt** (the user: "follow through day,
    nothing fundamentally changed"); the engine still reads it as one.
  - **List rules**: off after 2 closes under the 50 EMA (was 3), or while neither the 21 nor the 50 EMA is higher than 5
    sessions before, or the day a base breakout fails; back on the day it breaks out (base, flag, follow-through, falling
    range, launch-size day, 50 EMA undercut & reclaim) closing over the 21 and 50 EMA: "BACK ON THE LIST" (AMD Apr 8 /
    16, INTC Apr 1, MU Apr 22 2026; AXTI Feb 20 2026). Not for picks. launch.json gets `off_watch`. **The list grows: 97
    -> 135 rows on the Oct 23 data** (41 came back, 3 left): the user asked what it means, was told, has not decided.
  - **Long bases** named by their length ("cleared its 19-month base", "a 21-month high"); **falling range** 23-90
    sessions broken over the 21 & 50 EMA on 1x+ volume or a full-ADR day, not in the 5 sessions after a launch (INTC Apr 1,
    AMD Apr 8, COHR Apr 8 2026; NBIS Aug 14 gone); **failed breakout** (back under the top and the breakout day's low
    within 2 sessions: SNDK Mar 20, PGY Aug 28, ALAB Oct 8 2026); "breakout with caution" -> **"breakout attempt"**; the
    **flag line** redrawn by a poke under 0.75 ADR (PGY's flag is Aug 21, not Aug 13); **50 EMA undercut & reclaim after
    ONE close under** (the user: "change it, one close is ok"; COHR Mar 31 2026; the 21 EMA one stays at 2: ANF Oct 1
    kept, Claude's view, the user asked "what you think?"); **the hold** in the 10 sessions after a launch / attempt
    ("Holding after the launch": AEHR Feb 12-19, ALAB Sep 24 - Oct 2 2026) and "the launch did not hold" (first close
    under the 21 EMA: NBIS Aug 20 2026).
  - tools/chart_check.py: the 51 chart buy days, **29 -> 34 named and on the list**. radar/alerts.py and the alert texts
    are untouched (they still say "with caution").
- **3. Themes, built** (launch.py group_rank + the page): ranked on **tradable stocks, 4+ for a tier** (28 of 99 themes,
  53 of 217 groups; tiers 10 -> 7 and 20 -> 9); **Heating up** column (heat 1-99 = the group's median 1-week move + the
  share up on the week; 🔥 = 90+ with 60%+ up) on Themes and Industry groups, "Heating up" and "RS 1W-1M" in the column
  list; **one pack** where a theme and an industry group share 75%+ (15 pairs: the group shows the theme's name and
  rank); **homes**: of 343 pack-less tradable stocks 25 track a pack at 0.6+, 11 added by hand where the business matches
  (theme_adds.json: XNCR KYMR PTCT BAX HGV OSPN STEP BRKR; industry_groups.json: PDFS, KBR, AMTM, STEP); no new pack
  found among the rest.
- **The proof so far**: `--regress`: no agreed read lost except by design (AEHR Feb 11 -> attempt, ATRC Oct 30 off on a
  failed breakout, wording); new unjudged reads: VEEV Sep 30, APPN Oct 8 2026 (falling range), SMCI Aug 10 2023 and NBIS
  Aug 25 2026 (50 EMA reclaim after one close; NBIS is a would-not-trade chart). **The 2-year check** (the user: "that's
  fine"; run on GitHub and, like for like, in the session: the branch this morning vs with these rules, 2,200 launches):
  all buy points 5,037 -> 5,086, ran 20%+ 26% / 26%, failed 43% / 43%; flags 689 -> 674 (25 -> 26% ran); the new falling
  range 104: 31% ran, 47% failed, median -3.7%. It stops at the 2nd close under the 50 EMA: the way back is not measured.
  scanner/probe_catalyst.py now counts "Bull flag / Bull pennant breakout" again (its flag rows were empty since Nov 1).
  All 8 tabs load with no page error (the Oct 23 launch file and the Nov 11 scan).
- **Tested and NOT built** (don't repeat): a follow-through-day rule (3 versions: best caught 4 of 6, hit 6 of 36 liked
  launches; the days it marked ran 20%+ MORE often, 34% vs 26%); "launch failed" on a close under the gap day's open
  (the user: "no... it would possibly pull back, test its base, if it holds then it's ok": AEHR Feb 12); "choppy" by
  crossings of the 21 EMA (clean charts cross as often); "off on a close under the 10 and 21 EMA" (hits AEHR Mar 26, ZS
  Oct 16, GMAB Sep 10, CAI Oct 1 / 6 before agreed buys).
- **The user's new rules of thumb, not in the engine**: a launch must change the stock's character, not continue a move
  (SLG Jun 9, CNH Sep 2, LITE Aug 12, AEHR Jan 16; the AI stocks: lows Mar 9 / Mar 30 2026, the character-change day Apr
  8, then follow-through days); no launch under a falling line of lower highs (RMBS Jun 18, ALAB Sep 4); another base's
  high above is resistance (ALHC Jun 26); **CAI's launch is Aug 6 2026 even under the 200 SMA** (the engine: Aug 7);
  a strong day after earnings on under 1.5x volume can start it (COHR Feb 6); **the dying trend**: each new high closer
  to the last, then the EMAs roll over (COHR +21.5 / +13.2 / +6.5%, AXTI +48.7 / +6.8%); **a gap over the 21 EMA is a
  go even in a downtrend, as a short swing** (AXTI Jul 31, Sep 17 2026: 2-week runs); a trend that lasts needs a higher
  low, then a higher high; the day the uptrend breaks ends the trade (ALAB, MU Oct 8 2026).
- **Built at the end (the user's go, Nov 11 2026, APPN: "you can add this as a buy point in base, very strong one")**: **the
  2nd higher low in the base** (launch.py hl2_on, settings hl2_*): after a drop of 2.5+ ADRs in the base down to the 50 EMA
  that holds (every close since over it) and a bounce of 1.25+ ADRs, 5+ sessions later the low is at or over the 1st low,
  tests the 50 EMA and the day closes back over it in the upper half, the 50 EMA rising; once per base. APPN Sep 28 2026
  (the 1st low 33.28 Sep 10, the 2nd 33.35, closed 35.02 over the 50 EMA 34.54): reads. It also reads COHR Mar 17 2026
  (not judged by the user). No agreed read changed. Also from this chart: APPN's launch is Aug 6 2026 for the user (Aug 7
  too: volume + gap); the engine says Aug 7.
- **Done at the end**: the `long` fetch (161 symbols to Nov 11, with DOCU COHR AXTI ALAB NBIS); tools/examples.txt has DOCU,
  COHR (pick from Feb 6), AXTI (pick from Feb 20), APPN (to Nov 10), ALAB, NBIS; **tools/expected_reads.txt still not
  rewritten** (`--regress` lists 188 differing lines: today's rule changes plus the 6 new examples). DOCU Nov 11: the
  engine has its flag line 81.16 as the next buy point (matches the user's chart).
- **Asked of the user (they will "compile and provide all at once")**: go live or not; the 135-row list (keep the way
  back, or only on a base breakout / launch-size day); 3-5 more charts each of: dying trends (and ones that kept going),
  follow-through days, launches under the 200 SMA, launches on light volume, gap-over-the-21-EMA swings, choppy charts;
  VEEV Sep 30 and APPN Oct 8 2026 right or wrong; NBIS Aug 25 2026 (assumed wrong).
- **First things next session**: the user's new charts (see "Asked of the user"); for each, save it in their words in
  tools/chart_examples.txt, replay it, say where the engine matches. A `long` run replaces the file: pass every symbol again.
- **Good to know**: a session can't run probe_catalyst.py whole (no Alpaca keys: it hangs on the news step); its
  buy_points() alone runs in ~25 minutes on history/bars_2y.json.gz. Playwright needs `proxy: {server: HTTPS_PROXY, bypass:
  'localhost,127.0.0.1'}` to load the local page. The engine needs `pip install numba numpy pandas`; history/bars_2y.json.gz
  ends Oct 23; sessions before Oct 26 can't be reached.

## Status of the session "Radar: pre-market scanner vs EMA columns (Nov 11)" (Wed Nov 11 2026 morning; session_01PkbDajamht2fhC31vMGzcy)

- **Live (the user's "test it and go live", branch test/pmvs21, merge f7da91b): the pre-market comparisons carry
  their own names, and the 21 EMA is there.** The user (Nov 11, a screenshot of the scanner at 8:40): "this numbers are
  yesterdays closing numbers comparison not premarket"; "i need pre mkt vs 21 premkt vs50 and pre mkt vs200". Found:
  vs 200D / vs 50 EMA on the scanner were already on the pre-market price; the "vs 21 EMA" the user had added with
  + add is a catalog column on the regular-hours price (yesterday's close before the open), and its 21 EMA came from
  launch.json's watch list (one day old that morning, see below). docs/index.html only:
  1. Pre-market scanner (pml-table): **Pre-mkt vs 21 EMA** (new, key vs_21e), **Pre-mkt vs 50 EMA** (was vs 50 EMA),
     **Pre-mkt vs 200 SMA** (was vs 200D), in that order after ADR%; the same keys (vs_50e, vs_200), so saved layouts
     and filters keep working; the new column lands after ADR% in a saved layout. The 21 EMA = stocks.json tr[2]
     (e21Of: the last close's, 3,211 of 3,313 stocks). INTC Nov 11 9:15: $61.45 = -19.9% / -31.4% / -29.5%.
  2. Graded gappers: the two headers renamed the same way (the numbers as before). The Earnings tab's vs 200D /
     vs 50 EMA were left as they are (its layout keys come from the header text: a rename would reset a saved layout).
  3. Column list / + Filter (every table): new "Pre-mkt vs 21 EMA / 50 EMA / 200 SMA" in the Pre-market group
     (pm_vs21, pm_vs50, pm_vs200: today's scan only); **vs 21 EMA** (vs21e) now reads stocks.json tr[2] first, so it
     works for every stock (Gainers too) and is never a day old; the descriptions of vs 21 EMA / vs 50 EMA / vs 200D
     say: regular-hours price, live during the session, yesterday's close before the open.
  **Market hours** (the user: "make sure during market hours i would have filters to compare market hr price to
  21ema/50 ema and 200 sma"): + Filter -> vs 21 EMA / vs 50 EMA / vs 200D, "≥ 0" = over it, on Gainers, Watchlist,
  Launches, Earnings (the price is live in the session; the averages are the last close's). Tested with Playwright on
  the 9:15 scan against main's page: the same 71 rows, no page errors, a saved layout kept; the three filters on
  Gainers / Watchlist / Launches (16 / 51 / 122 rows). Rules workbook: a row in "P3 Pre-market scanner". No scanner
  code touched: no `--regress`, no Launches rebuild.
- **Not offered tick box**: "Above 21-day EMA" next to the scanner's two tick boxes was offered, not answered (the
  + Filter on Pre-mkt vs 21 EMA ≥ 0 does the same).
- **Live (the user's "go live", Nov 11 ~10:15 AM ET, branch test/scanfallback, merge 8f4bd6a): the evening scan no
  longer dies when Nasdaq refuses its stock list.** The scan had failed since Tue Nov 10 4:34 PM ET (scanner.yml runs
  38-41: 4:34 PM, 5:16 PM and both early-morning safety runs): scanner/fetch.py symbols() got "HTTP Error 403:
  Forbidden" from Nasdaq's screener (api.nasdaq.com), so setups/latest.json and setups/launch.json stayed at Nov 9
  (the user: "big problem"). Now fallback_symbols(): when an exchange's list fails 3 times, market cap and exchange
  come from radar-data stocks.json (the day job's file: 2,744 stocks over $700M on Nov 11; all 159 Launches and 298
  Watchlist names in it, 1 of 723 launch-watch names missing, CSIQ); the log prints "FALLBACK LIST". Tested here on
  the fallback step only (Yahoo can't be reached from a session). picks.yml (Follow picks, safe in market hours:
  launch.py drops the unfinished day) run at 10:15 AM rebuilt Launches as of the Nov 10 close (saved 10:19, commit 8dbb707: 153 launches, 745 on the
  launch watch list, 1 new launch Nov 10: EMBJ; not checked whether Nasdaq answered or the fallback was used). The Watchlist lists (run.py) can't be rebuilt in market hours (run.py would
  take today's unfinished day as a close): the 4:25 PM scan processes Nov 10 and Nov 11 together. The job logs can be
  read from a session with the GitHub tools (get_job_logs). Why Nasdaq: its screener is the scan's only source of
  the full US stock list with market cap and exchange (Yahoo gives the bars).
- **Live (the user's "go live", Nov 11 ~10:40 AM ET, branch test/livema): built on the user's "test it", then:
  the pre-market columns renamed again, "Pre vs 21", "Pre vs 50", "Pre vs 200" (the user: "its too long"; scanner,
  Graded gappers, the column list; the Pre-mkt names above are gone). The scanner's own vs PDH is the pre-market
  price vs yesterday's high: kept as it is. First check after the Nov 11 close: stocks.json has c200 (the close
  snapshot and the nightly build were changed blind) and vs 200 SMA moves in the Nov 12 session.** (Nov 11: "vs 200d-change to sma. and during
  hours it has to use dynamic one meaning todays 21ema already different than yesterdays same for 50ema and 200 sma"):
  "vs 200D" renamed "vs 200 SMA" (Gainers, Earnings, the column list); during the session vs 21 EMA / vs 50 EMA /
  vs 200 SMA use today's moving averages: applyLive puts ema21_now / ema50_now / sma200_now on the live rows (EMA =
  the last close's + 2/(n+1) x (price - it), as trendOf; the 200 SMA + (price - c200) / 200, c200 = the close that
  drops out, added to snapshot.yml and pipeline.py: in stocks.json from the first close after go live, until then the
  200 SMA stays the last close's); maOf(sym) serves the column list / + Filter, Gainers' columns and its Above 200 SMA
  / Above 50 EMA boxes, the Watchlist's vs 21 EMA / vs 50 EMA. Not changed: alerts, Launches, the Trend label, the
  Earnings tab's numbers, the ETF columns. Tested live at 10:10 AM against main's page (MU $793.10: vs 50 EMA -13.0%
  -> -12.5%; no page errors; row counts the same). All tabs load with no page errors after merging main.

- **Live (the user's "go live", Nov 11 midday, branch test/pmthemes): the Pre-market scanner's group gaps and Themes
  column.** The user: "when i click those themes it takes me to themes tab, when i click i want it in same table just
  show me those tickers"; "i know for fact that klic, simo belongs to semi ecosystem" (their Themes cell was empty);
  "do b, next time no theme show industry group your fix a". docs/index.html drawPmLive: (1) a click on a group-gap
  chip sets S.pmsel and keeps the table on the stocks that chip counts (the chip dark, a "Showing X: n of N · show
  all" button; a second click clears; the row chips in the Themes column still open the Groups tab); (2) a stock in no
  theme shows its industry group in grey (stocks.json group), or its broad industry "· other" when it has no tight
  group (2,262 of 3,313 stocks have no theme, 1,704 of them no group either), and counts for its group's chip at
  fit 0.7+; (3) radar/theme_adds.json: KLIC, ASX -> Semi Test & Packaging, SIMO -> Memory & Storage. Tested on the
  Nov 11 9:25 scan: Cybersecurity (13) -> 13 rows on the same tab, 205 back on show all; 114 theme rows, 91 grey
  labels, 0 blank; no page errors. **To check after the next theme build**: whether KLIC, ASX, SIMO passed the 0.6
  tracking test (and the AI & Semis SEMI_FLOOR) and show in their themes; SITM and FSLY got no theme (the user to say).
  Only the scanner's Themes column has the fallback (not Gainers, Graded gappers or the column list).

- **Live (the user's "go live", Nov 11 ~3:30 PM ET, branch test/earncal, merge 4398262): the Earnings tab no longer
  goes blank when Nasdaq refuses its calendar.** The user's screenshot (Nov 11): only Monday in the week's tables,
  "329 of 0 reports". Cause: api.nasdaq.com/api/calendar/earnings answered 403 for every day from about Nov 9 evening
  (earnings.json errors; the job doesn't fail), and only reports already read were kept. radar/earnings.py: when a
  day's Nasdaq call fails, Yahoo's v7 quote (earningsTimestamp / earningsTimestampStart) is asked for every stock that
  passes the rules or is in the file, and a date on a failed day puts it on the calendar; a name already on a failed
  day stays; the fiscal quarter comes from Yahoo's estimates (yahoo_fq: the 0q quarter if it ended before the report
  day, else the one before), before / after the open from Yahoo's report time. Test build (radar-tools `earntest`,
  3:08 PM): 215 reports from Yahoo; Mon 41, Tue 15, Wed 7, Thu 19, Fri 0; all 41 new rows with a quarter and an EPS
  estimate, the 18 reported ones read (AZTA Strong bullish, CRWV Bullish, EMBJ Somewhat bearish). Limits told to the
  user: Friday 0 (none passing, or no Yahoo date yet: unknown); Yahoo can move a date to next quarter soon after a
  report, so a past day can be short. Rules workbook: the two "second source" notes. The first "go live" push was
  refused by the session's safety check ("fix it" was not taken as a go): the user then said "go live".
  **Check next session**: the live earnings.json after the dispatch at ~3:30 PM and the 4:50 PM run; whether Nasdaq
  answers again (then its rows win).

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

New from Nov 5 (alerts / pre-market day, session_01PkbDakDe1EUNP5wQZf4wMH), all unanswered by the user:
- **Power day vs episodic pivot**: drop the power day's +10% on the day, so the two differ only by the gap (8%+ vs
  6%+; the power day needs a 4x volume pace, the episodic pivot 3x since Nov 5 evening; both over the 1-month high and
  the 200 SMA)? Asked twice, no answer: leave as is until the user says.
- **FCF**: offered a backtest of whether free cash flow change y/y matters for gap-ups when growth is high. Not run.
- **The official open** from Alpaca's SIP feed instead of the first 1-minute bar (the gap is now the same all day, but
  it can differ a little from TradingView's open). Offered, not decided.
- **TREND triggers and the W (200 SMA) alerts in GitHub's job** (radar/alerts.py), so they reach every device like the
  other alerts; today they come only from the open portal page. Offered, not decided.
- **Earnings tab, EPAM Nov 5**: EPS -26% (GAAP) on the tab vs Claude's adjusted beat; check the reader pairs GAAP with
  GAAP and adjusted with adjusted.
- Check-ins already scheduled in that session: Nov 11 and Nov 18, 5:40 PM ET (code grade vs Claude grade comparison).

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

