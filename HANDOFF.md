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

## Status of the session "Radar: MBGL / AVEX miss (Nov 12)" (Thu Nov 12 - Fri Nov 13 2026; session_01PkbDaiSjzGPJPtohD3UF2C)

- **LIVE (the user's "go live", Fri Nov 13 2026 ~0:30 AM ET, branch test/coilfilter, merge c9b1b59): the coil on Launches and a
  + Filter that lists everything.** The user: "i want to see coil pattern in launches table", "can you add that feature here
  as a filter ... nothing really available on filter part here". (1) scanner/launch.py follow(): every Launches / laggard /
  50 EMA undercut row carries `coil` / `coil_stop` (the MSF coil at that close, r.early / r.earlyStop, the same as the
  Watchlist's Other entries). (2) docs/index.html: column catalog "Coil buy" (hover: the stop) and "Away (coil buy)" %;
  + Filter "Coil buy: Has a coil / No coil" (COILK: the Launches row, else the Watchlist row). (3) + Filter on every tab
  lists all its criteria when opened (the table's columns, then the catalog group by group); typing narrows it as before.
  A display only: no buy point, trigger or alert reads the coil. Tested: `--regress` "every agreed example reads the same";
  radar-tools setupsdry on the branch (it got the Nov 11 bars only: 11 Launches rows with a coil + PAY from the Watchlist =
  12 with "Has a coil", vs ELAN and PAY before); the page with that file (no page errors). Rules workbook: the + Filter row
  and a coil row. Launches rebuild after the merge (picks.yml, 9:17 PM ET): NOT saved: the guard kept the Nov 12 list because Yahoo served
  bars only to Nov 11 that evening (as Nov 3). Until a later rebuild or the Nov 13 evening scan saves `coil` on the Launches
  rows, "Has a coil" finds only the Launches stocks also on the Watchlist. **First check**: setups/launch.json rows have `coil`.
- **Open, the user's requests / findings of this session** (questions only until the go live above; each needs a go):
  - **The coil alert: to look at later** (the user, Nov 13: "note this in notes for me, take a look at this alert later").
    A coil (MSF, scanner/msf.py: a mother day, then 2+ inside days with small bodies, over the 200 SMA; buy = the last
    inside day's high, stop = the mother day's low) shows in the Watchlist's "Other entries" ("coil 14.54", LFST
    Nov 12) and, since the go live above, as Coil buy on Launches. Nothing alerts on it: no phone, desktop or Alerts-tab alert at the coil buy or at the mother day's high;
    an alert comes only when another trigger sits there (GME / PAY Nov 12: a pop next to the coil price). The coil as a column /
    + Filter on Launches (asked the same night): done, see LIVE above.
  - **MBGL / AVEX Nov 12, explained, not fixed** (the user: "big miss"): (1) the pre-market scanner is blind 9:10-9:30
    (Alpaca free plan 15 minutes late, Yahoo's bars stop at 8:30, Yahoo's quote gave nothing for MBGL): MBGL showed
    +2.4% ($20.41, 8:35) at 9:25, opened +6.0% ($21.12), $22.62 by 9:35; 450 of 1,954 rows had a price from 8:35 or
    earlier at 9:25. Offered: a minute-by-minute check of MBGL's pre-market trades, then a real-time price for the last
    20 minutes and the time of each price on the page. (2) Young listings (AVEX IPO Apr 17 2026, MBGL spin-off Jul 1 2026):
    the 52-week low is the lowest since listing (MBGL $16.95 dropped it at the open: 24.6% over it) and the "200 SMA" in
    launch.py / alerts.py is the average since listing (AVEX $19.44; its high $15.51, so no launch / EP alert; the laggard
    alert needed its 1-month high $15.81); stocks.json has none. The user's point: they have no real 52-week low. (3) A bug:
    the code grader's stage() fails on a stock with no 200 SMA and says "no daily bars" (AVEX 9:23). (4) MBGL's ADR 3.23%
    at the Nov 11 close, under the 3.5% Launches minimum, kept it off the alert watch list (the user's rule; it made
    Launches at the Nov 12 close, B, ADR 3.51%).

## Status at the end of the session "Radar: watchlist/launches scanner tab (Nov 12)" (Thu Nov 12 2026 evening ET; session_01PkbDahfhKW69XD7xkjXjNm)

- **LIVE (the user's "go live", Thu Nov 12 2026 ~6:05 PM ET, branch test/listscan, commit 946beca): Scan your lists on the
  Pre-market scanner and on Gainers.** The user: "can i have a scanner that screens my watchlist or launches whatever i
  choose it automatically scans those tickers"; "all these under premarket scanner gap up, i go choose one of those, instead
  of scanning market it would scan my chosen watchlist very simple"; "for live market we have gainers tab ... where i choose
  my watchlist it only tracks those". docs/index.html: a **Scan:** button row under Gap ups / Gap downs (#pml-scan) and under
  Gainers / Losers (#g-scan): Whole market (the default) · Launches (launch.json launches + ema50_undercut, minus the ✕
  ones) · My picks (pickedNow: the followed stocks) · Launch laggards · 3-SETUPS (minus its ✕) · 2-POOL · 1-UPDAY · 1-EP/GAP
  · TREND (trendSrc), each with its count (scanSet(); the choice in localStorage 'radar-scan-list' {pm, g}). A list = only
  its names; the boxes and + Filter apply inside it; a line says the names, how many traded pre-market, how many pass.
  Unchanged: S.gpass / S.gset (the gainer dot on Groups, the count at the top), the theme event card, the graded gappers and
  their rules box, alerts, Launches. Rules workbook: one row in P3, one in G1.
  Decided with the user: a Scan choice on the existing scanners, not a new card; no rows for names without a pre-market
  trade ("no need"); no pop-up for a list stock gapping over its buy point (offered, not wanted).
  Tested (Playwright, the Nov 12 9:25 scan and the Nov 12 close, vs main's page): Whole market identical (gap ups 50, gap
  downs 189, gainers 9, losers 63, the chips and theme tables); every list's rows on that list; the counts = the Watchlist
  tab's (3-SETUPS 100, 2-POOL 257, 1-UPDAY 144, 1-EP/GAP 52, TREND 210), Launches 149 (116 traded pre-market; gap ups with the
  default boxes: AMD XERS PRGO ZYME VRDN CNC APPN PACS DLTR); remembered after a reload; phone 390 px no sideways scroll; no
  page errors. Page only: no `--regress`, no 2-year check, no Launches rebuild.
  Good to know: the pre-market scan (radar/pmlive.py) covers stocks with $300M+ market cap and 300K+ shares a day; the default
  boxes (0.5-5% change, ADR 4%+ ...) still screen the list, so a list stock gapping 8% is hidden until the box is widened.
- **Test only**: nothing (test/listscan is merged).
- **First check Fri Nov 13**: the user's first morning with Scan (any feedback on which list / filters they use).

## Status at the end of the session "Radar: Earnings reader fix + pre-market grading (Nov 4)" (Nov 4 - Thu Nov 12 2026; session_01PkbDakDe1EUNP5wQZf4wMH)

- **LIVE (the user's "go live", Thu Nov 12 2026 ~1:05 PM ET, branch test/earnrev, merge 7037cc8): three Earnings tab fixes.**
  The user (Nov 12): "WHY REV GROWTH MISSING FROM AVEX?" ... "it could have compared last q at least"; NBIS empty at 8:46
  AM; "we had 805 835 855 905 didnt we" (the tab's updates were on GitHub's own timer).
  1. **Revenue from Yahoo's earnings chart** (radar/earnings.py Y.summary(chart=True), per()): when neither the SEC release
     nor Yahoo's revenue history has the new quarter, the earnings chart's newest quarter is used, only when the chart's
     quarter before it equals last quarter's saved revenue (rev_prev, within 0.5%). rev_src "Yahoo (earnings chart)".
     Nov 12 13:04 build: NBIS $980.8M (+8.1% beat, q/q +68.4%, +571% y/y), ABSI $0.30M (-47.7%, q/q -4.4%, -19.6% y/y),
     QNT $9.1M (q/q +13.2%), FRVO $0.1M (q/q +2.7%). AVEX was already filled by the other session's news-feed reading
     (late_reports, "news headline": $189.7M, q/q -6.0%). 25 reported rows still have no revenue (mostly drug developers).
  2. **Guidance from the headline when the release has none** (headline_guide, step 4b): a report whose SEC release has no
     guidance in it, or one out with no release read when the news feed gave none, takes it from pmnews.json's earnings
     headline (Benzinga: Raises / Lowers / Affirms / Narrows / Sees ... Guidance; a from-to range read by its numbers).
     guide.src = "headline"; the page shows "· from the headline". NBIS: "Affirms FY2026 Sales Guidance of $3.0-3.4B vs
     $3.372B Est" -> Reaffirmed, -5.1% vs street (its 6-K, read at 9:22 AM, had no guidance). It overlaps the other
     session's hl_read / late_reports (same day, merged at da7d0aa): theirs reads reports with NO filing from the whole news
     feed; this one fills a release without guidance. Two headline parsers now (hl_read and headline_guide): could be one.
  3. **The day job starts the Earnings update at 7:05, 7:35, 8:35, 8:50 and 9:05 AM ET** (the user's times; radar/day.py
     er_started; GitHub's own schedule stays as a backup; Nov 5-12 it ran 1-2 real morning builds a day, Nov 12 only 8:12).
     **First check Fri Nov 13**: earnings.yml workflow_dispatch runs at those times and earnings.json built_at follows.
  Tested: radar-tools `earntest` on main vs the branch (386 rows, 0 errors, 5 rows changed as above); the page with the
  new file (AVEX / NBIS rows, no page errors); the slot logic simulated (a job starting at 8:12 runs 8:12, 8:35, 8:50, 9:05).
- **LIVE (the user's "go live", Thu Nov 12 2026 ~4:05 PM ET, branch test/trend50, merge 90ce403): the Trend base's 50 EMA
  "rising" = higher than the day before** (the user: "50 ema rising menain is this today higher than yesterday not 5 days
  ago"; was 5 sessions ago since Nov 3). radar/pipeline.py trend_at (e50[i] > e50[i-1]); stocks.json tr[4] = the 50 EMA the
  session before (was 4 sessions before); live (docs/index.html trendOf, radar/alerts.py live_trend): today's 50 EMA at the
  live price vs the last close's. Unchanged: the 10 / 21 "rising" (already vs the day before), the list rules in
  scanner/launch.py (the 21 / 50 EMA vs 5 sessions before), the code grader's STAGE (SLOPE = 5). It changes the Trend column
  everywhere, the TREND list and its triggers, and the ★ stars (★ = Trend Up at the last close): their tested +0.33R was
  measured on the old rule; a 2-year check of the stars was offered, not asked for. Tonight's day job loaded the old code:
  radar-day `daily` and picks.yml were re-run after it on main. **First check**: Nov 13 stocks.json trend / tr[4] from the
  new rule. The comparison (radar-tools groupsdry, Nov 12 close): 7 of 3,327 labels changed, all from none to positive (TSLA,
  CDNS, RAL, MSGE, WS -> Up; NSC -> Reclaim; SPH -> Turn up); the TREND list 227 -> 228 (RAL joins). Explained to the user after
  go live: with a one-day test an EMA rises exactly when the price is over yesterday's EMA, so on the Trend label (price over
  the 21 EMA, which is over the 50) the 50 EMA check no longer filters anything. **The user is thinking about it** (also
  offered: 'higher than yesterday 2 days in a row'). **Also open, the user to decide**: the code grader's STAGE (codegrade.py
  SLOPE = 5: Stage 2 needs the 21 and 50 EMA higher than 5 sessions ago) to one day or not.
- **Report only, no change (Nov 11 one-week check, code grade vs Claude, Nov 5-11 gap-ups)**: code A 3 names, avg +13.5%
  to Nov 11 (XERS +35.9%, MGNI +12.3%, APPN -7.8%); code B (5) no better than C (16), both +2.8%; Claude A +7.2% > B +3.5% > C
  +0.9%, Claude's B held 5/9 vs code B 1/5. Where both gave letters and differed (6): code right 3 (PTON, U, TLN), Claude 2
  (EPAM, IMVT), 1 mixed (VCEL). The bigger gap is coverage: the code's best (XERS, MGNI, AZTA) were never on Claude's list;
  Claude's best (FROG A +15.6%, TMDX B +16.6%) were cut by the code's filters. Stars: no edge yet (10 names). The Nov 18
  check (5:40 PM ET, scheduled in this session) is still to run; outcomes came from close/latest.json's git history.
- Answered, no change (Nov 12 morning): FIGR's news was that morning's Q3 release (SEC 6:47 AM); "Pre-mkt gap" is the first
  pre-market trade vs the close (TradingView's definition), so a stock with news after 4 AM shows a small gap and a big change
  (FIGR +0.83% vs +9.18%); offered to rename / hide it, not answered.
- **Test only**: nothing (test/earnrev is merged). Earlier this session (Nov 4-5, all live then): the Alerts tab and its 7
  boxes, the pre-market grading by 9:05 (Claude and code side by side), RS / group / Trend on every alert, the end-of-day
  held / didn't hold lines: see the archived sections of Nov 4-5.
- **Open, from this session** (each needs the user's go): one headline parser instead of two (hl_read / headline_guide);
  FIGR's buyback headline missing from its News line (seen Nov 12, not fixed); HUBS Nov 12 labelled "Earnings (headline)"
  for a CEO change + reaffirmed guidance (its report was Nov 4; not fixed); the "Pre-mkt gap" rename / hide (asked, no
  answer). **First things to check Fri Nov 13**: the day job's earnings.yml runs at 7:05 / 7:35 / 8:35 / 8:50 / 9:05 and
  earnings.json's built_at; the Nov 18 code-vs-Claude check-in (5:40 PM ET).

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

- In the status section "Radar: MBGL / AVEX miss (Nov 12)" above: the coil alert to look at later (the user's
  request), the pre-market blind spot 9:10-9:30, young listings (52-week low / 200 SMA), the code grader's
  "no daily bars" bug.
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

