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

## Session routine (the user's cheat sheet)

**Start of every session** (the user pastes this):

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

**End of every session** (the user pastes this):

> We're wrapping up. 1) Update HANDOFF.md with what we changed and agreed today (rules with my example dates, what is
> live, what is only on the test branch, open items). 2) If I agreed new reads, add them to tools/examples.txt and
> rewrite tools/expected_reads.txt. 3) Commit and push that (docs and tools only), and check nothing is left
> uncommitted. 4) Give me a 5-line summary: live, test only, open.

**How long a session**: one topic or one working day, whichever comes first (roughly 30–50 of the user's messages;
fewer when they are screenshot- and replay-heavy). Wrap up early when Claude Code compacts the conversation, or when
Claude starts asking again about agreed things or gets them wrong. The 8:45 AM grading has its own session: leave it
alone.

## Changes on Nov 2 2026 (made in the grading session, pushed straight to main at the user's request each time,
## WITHOUT the test-branch step; `tools/replay.py --regress` afterwards: every agreed example reads the same)

- **Alerts crash fixed** (27e1421): a local `since` hid the `since()` helper; every live run with a breakout or pop
  alert crashed and sent nothing (since Oct 28 afternoon). LION and W broke out Oct 29 with no phone alert.
- **Breakouts on the 1-minute checks** + **"touched its buy point, back under"** heads-up (live.py / fast.py now carry
  today's high, row index 7). 1-minute checks only **9:31-12:00 and 3:00-4:00 PM ET** (the user's choice).
- **Pre-market prices**: since the Nov 1 clock change Yahoo's pre-market 5-minute bars stop at 8:30; radar/pmlive.py
  now takes the newest of Yahoo's bars, Yahoo's live preMarketPrice and Alpaca's last SIP bar (NXT, ENPH missed Nov 2).
- **Pre-market grading**: own session (session_01PkbDanMRsWYc9PUezGyf1N), trigger trig_01EhkhyMeC5yC4H4sFxsqUVQ at
  **8:45 AM ET**, final price check 8:57, saved by 9:05, never skips grading when late, reports "prices as of";
  reliable-sources rule (primary sources or major outlets; social media / flash sites / AI summaries = rumor, C at best,
  F if the move rests on it); "why is it moving today" search for every stock; asset news for treasury-type companies.
  The old trigger trig_01V4NoRakoyHHyi7AdnuGTCW is disabled. Graded table: gap and vs 200 SMA / vs 50 EMA from the
  pre-market price at grading time (radar/premarket_build.py takes the live scanner file).
- **Launch laggards** (new tab): a launch day under the 200 SMA, 2x+ volume, closing over its 1-month high, only on
  earnings or an A/B pre-market grade; 5 closes in a row over the 200 SMA -> moves to Launches tagged "from laggards".
  Live list + phone/desktop alerts; the launch watch list now reaches 60% under the 200 SMA (`L["lag_under200"]`).
- **Power days must close over their 1-month high** (previous 20 sessions' highest high); regular launches unchanged.
- **Portal**: Type column + type filter on Launches; Resistance column (overhead 3/6/9-month and 52-week highs) on
  Watchlist, Launches, Launch laggards; vs 50 EMA on the pre-market tables (+ an Above 50-day EMA filter); ETF vs 50
  EMA / 200 SMA on Groups (theme ETF, industry ETF), sector/related ETF labelled as such; desktop alerts: ticker search,
  each tab shows its own alerts.
- **rules/**: `scanner_rules.xlsx` + `SCANNER_RULES.md`, generated by `rules/make_rules.py`.
- **Went live after test (Nov 2 evening, the user's "go live")**: liquidity = **700K+ shares and $20M+ traded, both
  20-day averages, everywhere** (Watchlist lists, Launches 600K -> 700K, pre-market gappers, themes' liquid names,
  Gainers / pre-market filters; settings.json keys min_avg_vol_20d / min_dollar_vol_20d_millions); and **laggards top
  out at grade A** (A+ needs the jump over the 200 SMA; NCLH Oct 29 2026 was an A+ laggard).
- **Studies (test/gapstudy, scanner/probe_gapgroups.py, radar-tools `gapgroups`)**: 3,720 gap-ups 2024-26 by their
  group at the prior close: Leading faded 49% (+0.3% from the open, 40% ran 20%+), Turning up 57% / Not trending 56%
  (28-30% ran 20%+); group 1-month up 8%+ faded 50% vs down 57%; 1-week alone doesn't change the gap day. Launches:
  Turning up on the launch day ran 20%+ 17% vs Leading 30% / Not trending 27%. The old "65% of A+ with the theme
  confirmed ran 20%+" did not reproduce over 20 sessions (27% vs A 23%).
- **Group rank (went live Nov 2 evening, the user's "build and go live")**: `group_rank()` in scanner/launch.py, in
  launch.json `group_rank` after each close. Every theme (vs themes) and industry (vs industries), 3+ stocks: median
  1/3/6-month return, each a percentile among its kind, averaged, ranked again (Qullamaggie style). **Top = top 3%,
  Strong = 3-10%**, the rest a rank number only (no Lagging / Emerging tags: below the top 10% no band beat the bottom
  half; breadth added nothing). A stock's group rank = its best-ranked theme or industry. Portal: Groups tab Rank (with
  the change vs 5 sessions ago) and Tier columns; Group rank column on Pre-market graded gappers, Launches, Launch
  laggards. Display only: the news grade, the launch grade and the old Leading / Turning up status (breakout grades)
  are unchanged. Test (scanner/probe_grouprank.py bands, radar-tools `grouprank` on test/gapstudy), 2 years, ran 20%+
  in 20 days: gap-ups Top 44% (739) / Strong 37% (457) / 10-20% 28% / 20-50% 29% / bottom half 29%; launches 35% / 31%
  / 23% / 22% / 21%. The gap-day fade barely changes (52% vs 53-57%).
- **Leader inside the group (went live Nov 2 late evening, after test, the user's "go live")**: each group_rank row
  carries `order` = its stocks best first (each stock's own 1/3/6-month return ranked among the group's stocks,
  averaged). Under every Group rank cell: the group and the stock's place in it ("#2 of 14 in it"). A green **"#1 in
  group"** tag on Pre-market graded gappers only (#1 of its best-ranked group, 5+ stocks). Not on Launches on purpose
  (leaders launching did worse, see Open item 7). **Group rank column added to the Watchlist** (all four lists, after
  Grade). Stocks over $2T stay out (the user: no need; settings.json max_mcap 2e12), so NVDA isn't ranked and AI
  Compute shows no rank.

- **Breakout alert grade uses the group rank (Nov 3 2026, the user: "it should replace with new")**: A = early (1st /
  2nd breakout within 50 sessions of the launch) + its best group Top or Strong (top 10%) + volume building; B = early +
  one; C = the rest. launch.py writes `group_tier_now` / `group_rank_now` on every launch and laggard row (best_ranks());
  radar/alerts.py grade_breakout and the page's desktop alerts read them (no field = the old Leading theme). Test
  (scanner/probe_bograde.py on test/bograde, radar-tools `bograde`; base breakouts after launches Aug 2025 - Nov 2026,
  2,743 crosses of the top), ran 10% / 20%+ in 20 sessions: new A 63% / 37% (379), avg +1.02R; old Leading A 59% / 31%
  (375), +0.48R; closed as a breakout: new A 73% / 43% (157), +2.47R vs old 68% / 37% (136), +1.76R. Top-only: 168 A's,
  65% / 38%. B 52% / 22%, C 45% / 17%.

- **Long explanations fold away (Nov 3 2026, the user: "too much on a portal")**: six long notes are closed
  `<details class="tgr-legend tgr-more">` boxes, one line each until tapped (Themes table, the drill-down list,
  pre-market scanner, pre-market grades, the big Launches note, the data footer); each remembers open / closed in
  that browser (localStorage `radar-more-<key>`). Keep new long notes inside such a box.

- **(Nov 3 2026, the user's "do all three")** (a) **History test table** on the Launches tab: by the group rank on the
  launch day (Top / Strong / other), by RS (97+ / under) and launch grade x tier; replaced "theme confirmed / lone
  wolf" (hindsight). backtest() uses rank_history() (the group and market rank on every day; matches group_rank() on
  the last day). (b) **RS column on Launches / Launch laggards**: market rank 1-99 (group_rank() "_rs", launch rows
  `rs_now`), green with a star at 97+. (c) **3-SETUPS triggers on the phone** (alerts.py find(): a setups3 name not on
  Launches / laggards, its buy point at or over the last close, trading over it; key SYM:s3, once a day) and in the
  1-minute checks (fast.py symbols). radar-tools `launchbt` = the launch build + History test on a branch, published
  to radar-data launch_dry.json / launch_bt_dry.json (not to main).

- **RS on the Watchlist + the RS test on buy points (Nov 3 2026, the user: "yes for both")**: launch.json
  group_rank.rs = every stock's RS; a plain RS column on the Watchlist (no highlight: information only). Test
  (scanner/probe_bograde.py on test/bograde, all buy points after launches Aug 2025 - Nov 2026, RS at the close
  before): no edge after the launch. Base breakouts RS 97+ ran 20%+ 25% (377), +0.19R vs RS 90-96 24%, +0.99R; A-grade
  breakouts with RS 97+ 29% / -0.2R vs under 97 39% / +1.3R; RS 97+ in a Top/Strong group 23% / -0.11R. All buy points
  RS 97+ 27% (642), +0.17R vs 21-23%. The RS edge is on the launch day only (History test: 58% vs 32% ran 20%+).

- **Earnings tab (went live Nov 3 2026, the user's "build it go live"; no Claude)**: radar/earnings.py -> radar-data
  earnings.json, earnings.yml (weekdays ~7:10-8:55 AM ET, final by 9:00; 4:50 / 6:30 / 8:30 PM ET; Sunday 6 PM ET).
  Who: Nasdaq's calendar Mon-Fri of the week, passing scanner/settings.json "earnings" on the last close ($700M+ cap,
  $30M+ and 600K+ shares 20-day averages, $10+, ADR 3.5%+, 30%+ over the 52-week low); stays for the week. Two tables
  by the PRE-MARKET price vs the 200 SMA; NOT filtered on the 50 EMA (the user: show it, don't eliminate). Columns:
  Read (Strong bullish / Bullish / Mixed / Somewhat bearish / Bearish from fixed points, see rules E1), EPS (actual vs
  estimate), EPS growth, Revenue, Rev growth, Guidance (raised / lowered / reaffirmed / given, guided revenue vs the
  street), Guide growth, Move (pre-market / after hours), Group rank, RS, then vs 200D, vs 50 EMA, vs 20D high
  ("cleared"), over the 52-week low. Results from the SEC press release (8-K 2.02, ex-99; the SEC_UA secret holds the
  contact, the user's email, trimmed in code), EPS Yahoo > release > Nasdaq (Nasdaq's post-report EPS was off: PLTR
  0.32 vs 0.44). Estimates saved before the report (this first week many were first seen after: no revenue estimate).
  GV in earnings.py = the release reader's version: bump it to re-read the week's releases after a reader fix.
  Checked by hand Nov 3 against the releases: PLTR, HNGE, LIFE, LSCC, AEHR, ON, XMTR, TEM, SHOP (low-thirties = 32%).
  radar-tools `earnings` / `earnprobe SYM ...` run it / the source check on any branch. No phone alerts (the user).
  Views (live Nov 3, the user's "go live"): All week / **Today's reactions** = the last trading day's after-close +
  today's before-open reports / **Day 2** = the session before (Mon morning: Thu after close + Fri before open; Wed
  morning: Mon after close + Tue before open); earnings.json "react" {t0, p1, p2} and "extra_days" (last week's days
  fetched for Mon / Tue). The ticker column is frozen when a table scrolls right. A listing without a 200 SMA yet
  shows in the top table as "new" (LIFE).
  Every Earnings column sorts on a header click (live Nov 3; empty values last; default = reported first, newest first).
  The week grid is ordered like the Earnings Whispers card (live Nov 3, the user): most liquid first (20-day $ volume),
  grouped by area (the stock's first core theme's category; no theme: its industry's usual area, SWKS -> AI & Semis;
  an auto group by its own name), the area with the biggest name first, then theme, then $ volume; $1B+ a day = a big
  chip (AMD, SMCI, ALAB, ANET together Tue Nov 3 after close).
  The Stock column is narrow (live Nov 3, the user: "too big"): "Tue AM" = before the open, "Mon PM" = after the close; the date and time in the cell's tooltip.

- **Alert rules (live Nov 3 2026, the user's "go live, a")**: every alert, phone (radar/alerts.py main, from
  base_stocks.json) and desktop (the portal's runAlerts, from stocks.json), fires only when the price is 30%+ over the
  52-week low at that moment; 3-SETUPS triggers (key SYM:s3) only while the price is over the 200 SMA (ECHO Nov 3
  2026: base top 100.90 under its 200 SMA 106.63, the alert at 101.19 on 0.9x). Not changed (the user chose a only):
  the 3-SETUPS alert text (it says the section, "Ready", and no "(light)" on the desktop).
- **Watchlist**: vs 21 EMA and vs 50 EMA columns after Rel vol (live price vs the last close's EMAs; sortable).
- **Phone alerts: leave them as they are (the user, Nov 3 2026)**: "I don't really use phone alerts; when I decide I'll
  activate the phone and tell you." Don't restart the Radar day job or change anything for the phone until then. The
  Nov 3 day job ran on the old code; the new alert rules reach the phone with the next morning's job on their own.

- **(Nov 3 2026, on test/pmrs until "go live")** plain RS column on the Pre-market graded gappers (RS 97+ on gap-ups
  added nothing inside a Top / Strong group); **Launching today** shows the Group rank cell (place in the group) and
  RS (★ at 97+) instead of the old "theme · Turning up" status; the **phone launch alerts** say the same (watch fields
  [15] group rank text, [16] RS; alerts.py gtext(), the old status only when they are missing); the **first column of
  every table stays put** when it scrolls sideways (CSS sticky, opaque background).
  Also **"Group on launch day"** replaces "Theme then -> now" on Launches / Launch laggards: the best group's rank at
  the launch day's close (launch rows group_rank_launch / group_tier_launch / group_pct_launch, from
  rank_history(full=True) + launch_day_rank()). The lone-wolf tag still uses the old status (the user, Nov 3: keep it;
  a new-rank version needs its own test).

## Status at the end of the last session (Nov 3 2026, the Earnings session)

- **Live on main** (each after the user's "go live"; `tools/replay.py --regress`: every agreed example reads the same):
  the **Earnings tab** (radar/earnings.py, earnings.yml, no Claude: Nasdaq calendar + Yahoo + SEC press releases;
  the views All week / Today's reactions / Day 2; sortable columns; frozen narrow Stock column); **every alert needs
  the price 30%+ over the 52-week low** when it fires, and **3-SETUPS alerts only over the 200 SMA** (ECHO Nov 3);
  **Watchlist vs 21 EMA / vs 50 EMA** columns. Details under "Changes on Nov 2 2026" (the Nov 3 entries).
- **Test branches**: `test/earnings` and `test/alerts52` are the same as main (nothing waiting). `test/pmrs` was merged
  by another session (not this one).
- **The SEC_UA secret** (the user's contact for the SEC) is set by the user; earnings.py trims its line break.
- **Phone alerts: left alone** at the user's wish (they don't use them yet); the Nov 3 day job ran on the old code.
- **No new agreed reads** this session (tools/examples.txt unchanged).
- **First thing to check next session**: the Earnings tab after the 7:10-8:55 AM runs (estimates saved before the
  report from Wed Nov 4 on, so the revenue surprise fills in); Day 2 moves forward each morning (Wed Nov 4: Mon after
  close + Tue before open).
- **Open from this session**: the Earnings reader's misses (fix + bump GV); revenue from the release's tables (SHOP:
  ≈ from growth); the 3-SETUPS alert text ("Ready" in a trigger alert, no "(light)" on the desktop): offered as (b),
  the user chose (a) only.

## Status at the session before (Nov 2 - early Nov 3 2026)

- **Live on main**: everything in "Changes on Nov 2 2026" above: the group rank (Groups tab Rank / Tier; Group rank
  column with the place in the group on Pre-market graded gappers, Watchlist, Launches, Launch laggards; "#1 in
  group" tag on pre-market gappers only); the **breakout alert grade on the group rank** (Top or Strong instead of
  "theme Leading", phone and desktop); the **long explanations folded** into one-line boxes. Launches rebuilt after
  each go live (115 launches, 19 in a Top group, 7 Strong). `tools/replay.py --regress`: every agreed example reads
  the same.
- **Test branches**: `test/grouprank`, `test/groupleader`, `test/bonew`, `test/foldnotes` are merged (nothing left).
  Studies only, not for main: `test/gapstudy` (probe_gapgroups / probe_grouprank / probe_leaders, radar-tools
  `gapgroups` / `grouprank` / `leaders`) and `test/bograde` (probe_bograde with copies of test/pb1h's
  probe_buypoints.py and mgmt.py, radar-tools `bograde`); results on radar-data probe_*.json. `test/pb1h` as before.
- **Decided by the user**: no Emerging tag (the test rejected it), no $2T+ stocks, breakout grades stay A / B / C
  (Top and Strong count the same: no A+ split, the data didn't support one).
- **First thing to check next session**: a breakout alert's text reads "group ★ Top <group> #n/N" or "group Strong
  ..." or "group not top 10% ..."; the pre-market graded gappers show the Group rank column; the folded boxes.
- **Nothing is waiting on the user's go from this session** (a market-wide RS and 3-SETUPS phone triggers were
  built Nov 3, see above). Older open items below.

## Status at the end of the session before (Nov 1 2026, evening)

- **Live on main** (Launches rebuilt from the Oct 30 close, 119 launches): everything under "What the user agreed"
  below. New tonight: **gap out of base** (alerts + portal), the **bull flag** redefined, the **bull pennant**, the
  **breakout undercut & reclaim**, the **try-of-the-top** reads, the **50 EMA undercut tab** (with its reclaim entry;
  off the list at the 3rd close under the 50 EMA), the names "Bull flag" / "Bull pennant", and the 1-minute check
  watching the tab. The status shows a breakout undercut & reclaim setup ("under its breakout level $X since (date)
  (N closes), holding over the 50 EMA"); its alert arms from the 2nd close under, after the stock advanced (a first
  version armed it after 1 close: fixed and live the same evening). Before the setup the status says it too: "closed
  back under its breakout level $X (1st close): a 2nd close under, holding over the 50 EMA, sets up a breakout undercut
  & reclaim" (CAI Oct 6 2026), or "back under its breakout level $X: the breakout didn't advance, the base is still
  valid" (AEHR Feb 12-19 2026, W Oct 30). After the last rebuild (119 launches): SIMO, CRM, NOW, ASST in the 50 EMA
  undercut tab; 1st close under: CDW, SHOP, RBRK, RGEN, TEAM; back under without an advance: CTSH, KVYO, MNDY, W, SAIL,
  GTLB, ZETA, HPQ, IQV. All agreed examples pass (`tools/replay.py --regress`).
- **Watchlist table controls** (Nov 2 2026, live): the "Other entries" column sorts on a click (A to Z first, names
  without entries at the bottom), so the coils group together when the coil is the first entry; the Section column
  header is a dropdown (all / Triggered today / Ready / Setting up on 3-SETUPS; the sections or dates on the other
  lists) that shows one section, in step with the Section box above the table. Clicking Section no longer sorts.
  Open: a coil listed second (APPN Nov 2: "flag trendline 50.3, coil 50.85") doesn't sort with the coils.
- **Watchlist note fixed** (Nov 2 2026): the "About these lists" box described the old Tight / 21 / 50 EMA pullback
  screens; it now describes 3-SETUPS as it is. The user: don't touch anything about the 50 EMA undercut there (3-SETUPS
  still drops a name at 2 closes under the 50 EMA).
- **3-SETUPS** (Nov 2 2026): the breakout undercut & reclaim is a "Triggered today" signal; the evening scan was re-run
  by hand on the new engine (Oct 30 close): 55 names, 8 Triggered (TTAN bull flag breakout; IOT, AI, BSP 21 EMA retest;
  VSXY, DXC, CART retest held; CDNA breakout), 21 Ready, 26 Setting up (bull flag / bull pennant names).
- **Coded but switched off**: the **momentum cutoff** (`L["max_run_pct"] = 0`). The user decides the rule (see Open
  items); turning it on is that one setting (plus the 200 SMA test if they pick B).
- **Only on a test branch**: `test/pb1h` holds the backtest tools (scanner/probe_*.py, scanner/mgmt.py = the user's
  trade management, tools/analyze.py, tools/reset_analysis.py, tools/extension_analysis.py, tools/momentum_cutoff.py,
  tools/test_results.py = the spreadsheet tools/test-results.xlsx, radar-tools.yml commands buypoints / gapbase /
  gapretest / launchlive / launchorh / earnings ...). Its engine is main's. Not merged to main (tools, not live).
- **Agreed reads added tonight** (tools/examples.txt): AEHR Feb 11 - Apr 10 2026 (Mar 31 50 EMA undercut & reclaim,
  Apr 2 bull flag breakout with the 50 EMA note, Apr 6 base breakout); APLD May 4 2026 (the textbook bull flag);
  CAI (Aug 19 bull flag, Aug 20 base breakout, Sep 3 / Sep 10 retests, Sep 14 bull flag, Sep 15 base breakout, **Oct 9
  breakout undercut & reclaim**, **Oct 21 the 3rd try of the top**, Oct 22-26 tight, Oct 27 base breakout); RPD Oct 8
  (the 3rd try of its 1-month base top 13.25 under the main base Aug 27 and the bigger base Aug 11); ARM Apr 13 is a
  **bull pennant** breakout. Not patterns: ACN Oct 29 (a drop and bounce), APPN Sep 14, AEHR Feb 20 (the Feb 11
  breakout never advanced: the base stayed valid).
- **The phone**: the user still has to subscribe the ntfy app; Monday Nov 2 is the first session with the gap-out-of-base
  and breakout-reclaim alerts live.

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

## The system

| What | Where |
|---|---|
| Portal | https://goattrader40-lgtm.github.io/radar-close-snapshots/ (docs/index.html, GitHub Pages) |
| Watchlist (nightly) | scanner/run.py → setups/latest.json (1-EP/GAP, 1-UPDAY, 2-POOL); 3-SETUPS right after by scanner/launch.py --watchlist (scanner.yml only; a Follow-button rebuild keeps the evening's setups3) |
| Launches (nightly + picks) | scanner/launch.py → setups/launch.json; the user's picks: setups/picks.json |
| Live alerts (phone, ntfy) | radar/alerts.py (every 5 min, 1 min at the open/close via radar/fast.py), radar/eod_alerts.py (after the close; also the 3-SETUPS Ready list as one text file) |
| Desktop alerts | the portal (docs/index.html) while it is open: launches, breakouts, and every 3-SETUPS trigger |
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

0. **Earnings tab, first live week**: check the reads with the user (Wed-Fri reports get estimates saved before
   the report); the guidance reader's misses go in as fixes with a GV bump. Not done: revenue from the release's
   tables (SHOP-style releases give only growth up front: ≈ from growth), the prior quarter's growth (acceleration).

1. **The momentum cutoff** (the user will say which rule): no buy points once the stock has run too far from its
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
8. Older: move the Launches rules box to the top of the tab; picks reading their history from the start; an intraday
   surge alert without a gap; the 3-SETUPS weaker Ready groups (kept as is).

## Tests run on Nov 1 2026 (test/pb1h)

Aug 2025 - Oct 2026, the user's management (1/3 at +2 ADR, 1/3 at +5 ADR, the runners out on a 10 / 21 EMA close),
after 0.15% costs, the risk floored at 1%:

- No filter combination beat luck (shuffled data found as many "winning" combinations). Launch-day 5-minute entry,
  held: +0.11R a trade (t 3.5), regime-dependent (the 2nd half +0.04R).
- Breakouts with the 5-minute stop lose (-0.1 to -0.3R); held through the day with the day's-low stop they are
  positive, but that stop is only known at the close. Follow-through on the 5-minute entry: avoid (-0.67R).
- Gap retest (6%+ launch-type gap, the retest holding the 10 / 21 EMA): no reliable edge (+0.19R at the close, t 0.5,
  only positive in the 1st half); after a plain big gap-up day: -0.44R.
- Gap out of base, 1-minute entry, held: +0.37-0.40R on 91 trades, the 2nd half negative.
- Momentum: see open item 1.

