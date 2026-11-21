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

