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

## Episodic pivot alert: a volume pace of 3x+, was 4x (LIVE Nov 5 2026 ~8:50 PM ET, the user's "go live"; branch test/ep3x)

- The user (Nov 5 evening): "change the rule for the episodic pivot: 3 rvol at least, everything else stays the same".
  radar/alerts.py find() `ep = rv >= 3`, docs/index.html EPIV.rv 3, the Alerts tab's explanation, the rules workbook. The
  power day keeps 4x. The EP otherwise: a 6%+ gap, the open over the 21-day closing high (below), over the 1-month high
  and the 200 SMA. Nov 5's morning record (live_history.json, 97 movers 9:35-11:00): the same EPs at 3x as at 4x (CHYM
  only). Regress: every example the same.

## Power day / EP alerts must open over the 21-day closing high (LIVE Nov 5 2026 ~8:25 PM ET, the user's "go live"; branch test/epopen)

- **Why** (the user, Nov 5 evening: "the whole point is to gap up above it, meaning the opening price has to be above the
  21-day highest closing price to be eligible for an episodic pivot"; "it applies to both of them", the EP and the power
  day): WRBY Nov 5 opened $25.93, under its 21-day closing high $26.52 (the code grader had it "not eligible: under the
  21-day high close" at 9:18), and still fired a POWER DAY at 12:35 on a 1-cent pass of its $27.00 1-month high
  ($27.01, +26.9%, 5.0x), then closed $26.10.
- **Code**: scanner/launch.py saves each launch-watch stock's highest close of the last 21 sessions in launch.json
  `watch_close_high_21d` (beside the watch rows; their layout unchanged; the same number as the code grader's hi21);
  radar/alerts.py find() and docs/index.html lnLive (alerts only: the Launching today table lists as before) need
  today's open over it for the power day and the EP. No number (a watch list from before) = not checked: it starts with
  the Nov 6 4:40 PM scan, so Monday Nov 9's alerts (tonight's scan was not re-run: a dry build tonight got bars only
  through Nov 4).
- **Tested**: the job's find() on Nov 5 with the Nov 4 watch list: WRBY no power day; ADMA, EPAM, EWTX, MGNI, XERS, U
  power days and CHYM's EP unchanged. WRBY then gets "A launch" at 12:35 (its own rules: allowed, the user). Regress:
  every agreed example the same. radar-tools `launchdry KO` on the branch: 591 of 591 watch stocks got the number,
  equal to the code grader's (WRBY 26.52, CHYM 30.46, ADMA 11.75, EPAM 143.80, EWTX 40.49). Rules workbook updated.

## Alert boxes hold only what still holds, like a ladder (LIVE Nov 5 2026 ~8:45 PM ET, the user's "go live"; branch test/boxhold)

- **The user's rules** (Nov 5 evening): a trigger goes into its box (🚀 / ⚡ / 🎯 / ↩️); when it stops meeting its own
  requirements later in the day (all of them, volume too) it leaves the box; when it meets them again it comes back. "It's
  like a ladder": a Launches stock's power day / EP (⚡) that stops meeting its rules steps down to 🚀 Launching now while it
  still meets a launch's rules, else to 👀; a launch, a pattern breakout (Watchlist or Launches) or a pullback entry that
  fails steps down to 👀 Heads-ups; at the end of the day what didn't hold goes in the 👥 report of failures. An alert that
  doesn't meet its buy requirements is a heads-up (👀: touched the buy point, the 9:50 volume check, back over a level, the
  21 EMA retest alone). **No rule changes**: "whatever the rule is, it's the rule; you're only placing the right triggers in
  the right boxes" (the retest: tests the breakout / base level and the 10 or 21 EMA, then back over the level, reclaiming
  that EMA).
- **Code**: radar/alerts.py `still_holds` / `update_holding` (main(), each run from 9:35): every trigger it sent today is
  checked again with the same code that sent it: find() on the latest prices (levels, % up, volume pace), then the same
  1-minute chart tests main() runs before sending (the retest's low in the zone and the 10 EMA / 21 EMA test, the 21 / 50
  EMA reclaim's undercut and upper half, the reversal's top half, the 1- / 5-min entry: the range's high broken and the
  price over its low, the stop). alerts.json: `hold` {at, keys, now: every trigger its rules find right now}, `lost`
  {key: at, price}, `back`. docs/index.html drawAlog `place()`: the box each line sits in now; the page tracks its own
  triggers (TREND) the same way (localStorage plost / pback / pnow). In a box a stepped line starts with ↓; the log says
  what happened ("↓ no longer holding since 4:05 PM ($109.78): down to 👀 Heads-ups"). The end-of-day report uses the job's
  verdict at the close (its last check at or after 3:58 PM): a power day that stepped down to a launch counts as held (as
  a launch); the gap-out-of-base entries by their stop.
- **Nov 5 replay at the close** (the Nov 4 watch list, Nov 5's alerts and 4:10 PM prices; Yahoo's chart is blocked in the
  session, so the retest lows and opening ranges came from the alerts' own texts): ⚡ ADMA, MGNI, U, XERS; 🚀 EPAM (stepped
  down: volume pace 3.6x, under 4x), WRBY's catalyst gap (its failed power day not shown twice), APP, PRKS (laggards);
  🎯 CERT, RPD, XERS, ACHC / ENOV gaps, ENOV's entries (over the $28.15 stop); ↩️ EAT, PRGO; the rest ↓ in 👀 (ELF
  $109.78, WRBY's base high, the confirmations whose pace fell under 2x, GCT's gap at 1.8x after 9:50 ...).
- **Check Friday Nov 6 (the first live day)**: alerts.json gets hold / lost / back after 9:35; the boxes move within about 5
  minutes of a failure; the 1-minute chart tests (retest, entries) work live. Open: a power day replaces the stock's A
  launch alert, so a power day that steps down shows its own line in 🚀 (marked ↓).

## End of day = today's buy-point triggers only (LIVE Nov 5 2026 ~7:50 PM ET, the user's "go live"; branch test/eodtrig)

- **Why** (the user, Nov 5 evening: the 👥 end-of-day list "is made up stuff": "it can only aggregate whatever has been
  triggered by our buy point rules; whatever from those triggers is still true at the end of day, show them"; "buy point
  triggers from the Watchlist tab and the Launches tab"; "TENB any trigger buy point? NTSK there was no buy point"): the
  old eodList took the pullback heads-ups (zone "in the retest zone", ema21zone "at the 21 EMA") and the scan's own
  retest_today, all checked against the breakout level. Nov 5: 19 of its 22 names had no buy point (TENB, NTSK 9:35
  heads-ups; OWL no alert at all; KOD "held" at $91.02 over the breakout level $38.73 while its alert was the 21 EMA $90.15).
- **Now** (docs/index.html eodEntries / eodLevel / eodList / eodLines): today's buy-point triggers (EOD_KINDS) filed on
  the Launches or Watchlist tab (tab code L / W: GitHub's alerts.json and the page's own log; no heads-ups, group moves,
  pre-market grades; Launch laggards not), each checked at the close against the level its own alert named (read from
  the alert's text): power day / catalyst / launch / ★ launching / reversal = the 4:40 PM scan put it on Launches dated
  today (else the reason: under +5%, under the 200 SMA, under the base high its alerts named); an EP also over the
  1-month high it named; breakout / 3-SETUPS / TREND / base high cleared / confirmed = the close over the level (within
  0.5% = with caution); gap out of base over the base high, the 1- / 5-min entries over their opening range high;
  retest over the level and the 21 EMA; push and breakout undercut & reclaim over their level; 21 EMA undercut / 21 EMA
  + breakout level / 50 EMA undercut over that EMA at the close (the upper half of the day isn't checked: no day low in
  the data); pop over its 10 & 21 EMA. Lines: "GCT ✓ HELD: gap out of base" (its failed triggers ✗ inside, click to
  open), one "✗ Didn't hold at the close: N Launches / Watchlist stocks" line per tab, filed under the trigger's tab;
  the pop-up "End of day: N of M triggered stocks still true". Rules workbook: "End of day (desktop, every device)".
- **Nov 5 on it**: 15 held (power days ADMA, EPAM, MGNI, U, XERS; gap out of base ACHC $34.79 > $32.87, GCT, ENOV, all
  three under their opening range entries; RPD $15.44 > $15.28, CERT, UPBD, AVAH, THC; retests EAT $212.66 > $206.43 and
  its 21 EMA, PRGO), 20 didn't (Launches 18: ELF $109.85 < $110.00, APPN, PACS, SKY, ... CHYM +1.0%, EWTX +3.6%, PRKS
  under its 200 SMA, WRBY $26.10 under its $27.00 base high; Watchlist 2: OLLI, WK). Display only: no regress or 2-year
  check needed.
- **Open**: the Launch laggards tab is left out (APP's laggard launch, the W crossings): the user's call. TREND triggers
  are page-only, so they show only on the device that fired them (until they move into the job). Seen, not acted on: EAT
  and PRGO got the job's 3:45 "RETEST HOLDING" while the evening scan's retest_today stayed False (each pullback's retest
  was already tried: Nov 2 / Oct 27, once per pullback); OWL the other way (retest_today, no live alert).

## One line per alert, one open all day, trend on the line, code catalyst (LIVE Nov 5 2026 evening, the user's "go live"; branch test/epfix)

- EPAM Nov 5: its power day showed twice (the page's 2:55 PM line, saved by the old version in 🚀, and the job's 9:35 AM in
  ⚡) with different gaps. runAlerts skips an alert GitHub's job already sent (jobKeys); drawAlog matches a saved line
  without a key by ticker + first words (sigOf) and keeps the earlier; a POWER DAY line is always in ⚡.
- The gaps: fill_opens takes a mover's open from the first 1-minute bar (Yahoo's quote has none for NYSE stocks for ~10
  min) and keeps it in /tmp/radar/out/opens.json, which a fresh job after the noon handover didn't have: it took Yahoo's
  quote open ($156.19 vs $157.71). day.py publishes opens.json with live.json and load_opens() restores today's.
- The strength line adds the Trend label (trendOf: "Trend Up 16d"); the opened alert drops the theme / rank / RS / group
  bullets it repeats.
- The Pre-market table's Catalyst and Reason: the code grader's "(code)" when Claude didn't grade the stock.

## RS + group on every alert; end-of-day held / didn't hold; ★★★ everywhere; search filters boxes (LIVE Nov 5 2026 ~5 PM, the user's "go live"; branch test/eodholds)

- Every box line: "RS 88 · ★ Top Software #2/214" (strengthParts: launch.json group_rank.rs + grBest; ★ Top = top 3% of
  groups, Strong = the next 7%, scanner/launch.py GR_TOP / GR_STRONG). The ⏰ lines have it in their text (test/pmrs).
- End of day (the user: "which retest held or not"): eodList(): after the evening scan (launch.json date today), each stock
  with a pullback alert today (EOD_KINDS: retest, zone, ema21, ema21bl, ema21zone, push, reclaimbo, reclaimbo2; not touch)
  plus retest_today: close vs retest_level (else last_breakout_top, else the 21 EMA) -> "✓ HELD / ✗ DID NOT HOLD at the
  close (after the close)" in 👥, ★★★ when hcReady; drawn on every device; one summary pop-up (alerts on). Nov 5: 12 held,
  10 didn't (ELF: retest holding at 3:45, under its level at the close).
- hcItem(): the job's retest / push / 21 EMA alerts get the ★★★ mark on every device (was only in an open page).
- A ticker search filters the boxes across every tab.

## Every device sees the day; power days in the EP box; EP in the job (LIVE Nov 5 2026 ~2 PM, the user's "do it"; branch test/everydevice)

- The user's phone (alerts off, notifications blocked) showed empty boxes while the job had sent 107 alerts: the boxes were
  filled only by a browser with alerts on. Now drawAlog() merges alerts.json (SRV, the job's record) with the page's own
  log (dedupe by key, which the log line now carries after the codes, and by text), sorted by time: every device.
- The ⏰ box fills with alerts off too (pop-ups only with alerts on, 8:45-9:25); its lines carry CGR.built_at (code) or
  "Pre-market" (Claude's, seen after 9:25).
- Power days in the ⚡ box (BOX_OF.power = 'e', spoken "Power day"); Launching now keeps catalyst / A launch / ★ / reversal /
  laggard. radar/alerts.py find(): ':ep' (4x+, gap 6%+, over the 1-month high and the 200 SMA), after the power day; main()
  skips a later launch / catalyst of an EP stock and an EP after a power day. Nov 5 9:35 replay: CHYM EP. Regress: same.
- Still page-only (not in the job): TREND triggers, W crossing the 200 (need the TREND list / W names in the job).
- The user (Nov 5): "power day has to be above the 200 SMA too, so the only difference is the gap %": it already is (the
  job and the page skip a stock at or under its 200 before the power-day test). The power day also needs +10% on the day;
  asked whether to keep that (then the gap and the day's gain differ) or drop it (only the gap: 8%+ vs 6%+).

## Alerts readable: key-fact bullets, click to open (LIVE Nov 5 2026 afternoon, the user's "go live"; branch test/bullets)

- ⏰ Pre-market lines (the user: "not user friendly, it should be bullet points: beat, raise, buyback, 50% FCF return,
  then guidance"): a headline (gap, catalyst, chart), then keyFacts(): beat / miss with revenue and EPS surprise, growth
  (faster / slower), buyback / % of FCF returned / FCF / first GAAP profit / dividend / deal / FDA picked from the reason,
  the guidance (raised / cut / given, vs street, y/y), ⚠ warnings (the Earnings tab cross-check isn't one). Numbers from
  the Earnings tab (EARN, the SEC release); no earnings row = the reason in short bullets. Green good, red ⚠.
- A click on a box line (the user: "click shows the message, then I go to TradingView; hover is hard to read") opens it in
  place: the short figures on one line, one fact per bullet, 📈 Chart and 📰 news buttons; a second click closes it
  (AL_OPEN keeps it open across refreshes). Only the Chart button opens TradingView; the log gets a Chart button.
- Open: EPAM Nov 5 read "EPS -26%" on the Earnings tab while Claude read adjusted EPS as a beat (GAAP vs adjusted pairing?).
- The user said yes (Nov 5): test/pmwindow live; power days also in the ⚡ EP box + the EP alert in the GitHub job and
  the boxes filled from GitHub's alerts.json on every device: being built (test branch first).

## Alerts walled off part by part (LIVE Nov 4 2026 ~11:45 PM, the user's "both"; branch test/safeparts)

- docs/index.html safe(name, fn): the W alerts (live / evening), TREND triggers, the Pre-market box, the sounds, the
  boxes and the bars each run inside it; an error stops only that part, PART_ERR names it on the alert card (the ⏱
  line: "⚠ Not working right now: <part> (<error>). The other alerts keep running."). The log line codes fall back to
  Launches / Heads-ups. Test: a null code-grade row stopped only the Pre-market box at 9:45.
- Check-ins scheduled in this session for Nov 5: 9:07 ET (both grades saved by 9:05? code grader runs at 8:45 / 8:55 /
  9:00?) and 9:45 ET (the GitHub job's alerts after 9:35, the morning record live_history.json, live.json fresh).

## The morning: Pre-market box, grades by 9:05, 20-second checks, W crossing the 200, bigger boxes (LIVE Nov 4 2026 ~10 PM, the user's "go live"; branch test/morning)

- **Grades by 9:05 (the user: "I need pre-market grading done not later than 9:05 to choose what to trade")**: Claude's
  8:45 grading saved at 8:57 on Nov 4 (fine). The code grader (about 40 s a run) ran only on GitHub's schedule (8:52 /
  9:05 / 9:18, often 5-20 min late): radar/day.py now starts codegrade.yml at 8:45, 8:55 and 9:00, right after that
  5-minute pre-market price update (the loop wakes on 5-minute marks before the open); the schedule stays as a backup.
- **⏰ Pre-market box (the user: "anything changes, I get an alert in a pre-market box")**: first box on the Alerts tab;
  the page diffs Claude's (premarket.json) and the code's (codegrade.json) grades on every check against its own copy
  (localStorage pmsnap per day): a gap-up becoming A+ / A / B, changing, losing it or leaving the list; Claude's A / B
  gap-downs. One pop-up per update and source ("⏰ Code grades changed (9:05 AM): TREX off the list (was B) · DUOL A (was
  B) · OSCR A (was C)"), click = the Pre-market tab; a line per stock with both grades ("DUOL Code A (was B) · Claude A");
  its own sound (C-E-G) and voice ("Pre-market. Code grades changed. T R E X, no longer B..."). Tag / chip "Pre-market".
  Only names that pass every filter (the user: "obviously only names over the 21-day high and all other filters"): a
  code A+ / A / B always does; Claude's A / B only when the code grader found it eligible (Nov 4: DUOL; not RIOT, NVTS,
  ARRY); before the code's first run it shows, marked "filters unchecked". Gap-downs stay on the Pre-market tab.
  (LIVE Nov 4 ~10:30 PM, test/pm200) Claude's A / B also needs the code's event not 'laggard': over the 200 SMA at the
  pre-market price, like every code A+ / A / B (under it = W).
  (LIVE Nov 4 ~11 PM, test/pmreason) Each Pre-market box line shows the full reason under it (the code's reason from the
  filing / earnings numbers and flags; Claude's sentence), up to 3 lines, and a 📰 news link (the SEC filing / Claude's
  first source); the box is two boxes wide; the log shows the news link instead of the address.
- **20-second checks**: tipSha() sends the browser's GitHub key (the Follow button's, radar-gh-key) when there is one
  (5,000 checks an hour; 401/403 -> retried without); with a key the page checks every 20 s from 8:45 to 10:00 ET. The
  alert card says which (⏱ line), with an "Add the key" button (the Follow button's key dialog) when there is none.
  (LIVE Nov 4 ~11:30 PM, test/fastcheck, the user: "make sure it does now") No key needed: tipSha() uses cache 'no-cache',
  so the browser sends the ETag and an unchanged answer is a 304, which GitHub doesn't count (tested: X-RateLimit-Remaining
  unchanged); only new commits count. 20-second checks for every browser 8:45-10:00; a 403/429 pauses them until
  x-ratelimit-reset (RL_UNTIL) and the ⏱ line says so. Browser test: checks at 0, 20, 40, 60 s.
- **Bigger boxes**: 4 across (3 / 2 / 1 on narrower screens), body-size text, 10.5-21 rem tall; the log up to 65% of
  the screen on the Alerts tab.
- **W crossing the 200 (the user approved the proposal)**: W names = codegrade_log.json grade W (gap-ups) of the last
  90 days (~60 sessions), loaded as CGL. Live: under its 200 SMA at the last close and over it now -> 👀 "KD W over its 200
  SMA now" (w200now); from 3:50 PM -> 🚀 "W CROSSING THE 200 into the close" (w200, a trigger); the evening build: closed
  over it -> 👥 "W closed over its 200 SMA (after the close)" (w200close). Tab Laggards. The backtest's W history is not
  seeded (it would mix into the code-vs-Claude log): the list fills from the live grader's W days. Not done: putting a W
  name on the Watchlist / Launches lists the day it closes over the 200 (a scanner change, launch.py: to test with the
  replay regress) - the user's call.
- **Double beat and raise -> B**: already the rule (a raise or a guide over the street = B unless the guide is cut); KD
  Nov 4 stays C (guidance reaffirmed, revenue -0.6% y/y; revenue +2.1% and EPS +10% beats). Asked: should a double beat
  with guidance reaffirmed be B too? The user: not sure, "the market is forward looking, a raise is different": no change.
- **Asked Nov 4 night: FCF y/y**: the code grade doesn't use free cash flow (Claude's grading reads the cash-flow
  statement for red flags). Offered: test in the backtest whether an FCF swing adds anything beyond growth before
  using it (likely a warning flag, e.g. FCF turned negative while growing, not a grade input).

## Alerts tab, alert boxes, the episodic pivot alert, sounds per box (LIVE Nov 4 2026 ~9 PM, the user's "go live"; branch test/alertboxes)

- **🔔 Alerts tab (the user, Nov 4: "should we have a separate tab for alerts")**: the Desktop alerts card moved from
  Launches / Watchlist to its own tab (#alerts): every tab's alerts, each line tagged Launches / Watchlist / Laggards
  (the tab set when it fired), chips All / Launches / Watchlist / Laggards (kept in localStorage radar-alerts-filter),
  the six boxes, the full log and search. Launches (Launch laggards) and the Watchlist show a bar on top with their
  count and newest 3 (most stars first); a click opens the Alerts tab. A summary pop-up's click opens it too.
- **Sounds (the user: "can it make a different sound for episodic pivot or box names")**: a trigger plays its box's tone
  (TONES: EP 3 quick rising, launching 2 rising = the old chime, pattern 1 bell, pullback 2 falling, group 2 low,
  heads-up a soft tick) and the voice (speechSynthesis) says box, stars, ticker spelled ("Launching now, two stars, K D").
  One check's triggers go together (BELLS / announce): each kind's tone once (EP first, at most 3), then the first 3
  read out (EPs first, then most stars, then box) + "and N more". Voice on/off button (radar-alerts-voice); Test plays
  each box's tone with its name. Nov 4 test at 9:45: "Launching now, two stars, B R K R. ... K D. ... one star, A R L O.
  And 52 more."; with CDW / OSCR as EPs: EP tone first, "Episodic pivot, C D W. Episodic pivot, O S C R. ..." 

- **Boxes (the user's layout, Nov 4)**: the Desktop alerts card shows 6 boxes above the full log, with the tab's alerts by
  kind, set when each fires (the 2nd code after the tab's in the log line's invisible marker; BOX_OF / boxOfKey):
  🚀 Launching now = power, catalyst, A+/A launch, ★ launching, reversal, laggard; 🎯 Pattern breakouts = breakout, confirm,
  gap out of base (gapbase, gob1/5/950), base high cleared, pop, 3-SETUPS & TREND triggers (every pattern's buy point:
  base top, inner base, flags, pennants, tight / high tight flag, flat base, cup, ascending triangle, Qullamaggie, MSF);
  ⚡ Episodic pivots = the EP alert; ↩️ Pullback entries = retest holding, 21 EMA retest / undercut, undercut & reclaim,
  push, 50 EMA back, touch, ★★★ (and a 3-SETUPS 21 EMA retest / retest held trigger); 👀 Heads-ups = early, near the buy
  point, retest zone, at the 21 EMA; 👥 Groups & news = group moves, pre-market grades, after-close heads-ups. Newest
  first by the alert's time, starred on top (bold), click for the chart; 3 across, 2, 1 on a phone.
- **EP alert (':ep', desktop only)**: the user's rule: volume pace 4x+, gap 6%+, over the 1-month high (the previous 20
  sessions' highest high, the power day's; the user agreed) and the 200 SMA, from the 9:35 check (allowed up to the
  power day's 200 SMA extension). A power day is an EP: no EP alert for it (power covers ':ep'); an EP covers that
  stock's catalyst gap, A launch and ★ launching pop-ups. A trigger (bell). Nov 4 data: DUOL, VRDN power days; PCOR's gap
  5.95% (no); CDW (+7.4% gap, +12.7%) and OSCR (+9.9% gap, +8.6%) at a 4.5x test pace -> EP box.

## KD "missing" from the desktop alert log: the log, not the alert (LIVE Nov 4 2026 ~7:30 PM, the user's "go live"; branch test/livelog)

- **What happened** (reproduced in Chromium at 9:45 AM Nov 4 on the Nov 3 lists and Trend labels, alerts on, empty log):
  the desktop **did** fire `★★ KD CATALYST GAP` and filed it on the Launches log; the job's 9:32 `KD EARLY` went to the
  **Watchlist** log (KD was on 2-POOL and, up 15%+, its live Trend label turned Reclaim: the Nov 3 rule files a TREND-list
  ticker's alerts there). The search "KD" on Launches could not find the starred line: the log read the first word after
  the time as the ticker ("★★"), so search missed it and a click on it opened **IT** (from "· IT Services & Consulting").
  The log kept only the newest **100** lines (71 by the first check): by the afternoon the 9:32-9:35 lines were gone,
  hence "No alerts for KD today on this tab" with nothing at all.
- **Not the volume**: every one of the 662 alerting stocks has its own volume curve and a pace in live.json; on the exact
  SIP minutes KD was 6.7x at 9:35 (POWER DAY needs 4x); the Alpaca correction (radar/sipcal.py) can't act before ~9:51
  (first snapshot 9:34 + 16.5 min) and never takes the volume under the SIP volume of 16 min before. The typical-curve
  fallback drafted for rvol_at was dropped (never needed).
- **Test branch**: docs/index.html log: the ticker read past the stars (search + chart link only; the tab a line is filed
  under is unchanged), a search looks through every tab's alerts and names the tab ("· on the Watchlist tab"), the log
  keeps 400 lines. radar/livelog.py + radar/day.py: the **morning record** live_history.json on radar-data (9:30-11:00,
  each watch-list stock gapping or up 5%+: time, price, chg, gap, volume, rel vol, the Alpaca correction in effect,
  the alerts the rules fire then; missing quotes), restored from radar-data after a job handover.
- **Which tab's log (the user, Nov 4 2026: "anything under watchlist is trigger under watchlist, any in launch trigger in
  launch, if duplicate trigger in launches")**: set when the alert fires (tabOfKey in docs/index.html, an invisible code at
  the end of the log line): Watchlist = the 3-SETUPS trigger and the live entries of a 3-SETUPS stock not on Launches /
  Launch laggards; Launch laggards = laggard launches and that list's stocks; Launches = the rest (power day, catalyst
  gap, A+/A launch, ★ launches, EARLY, 2nd trigger, reversal of any watch-list stock, whatever other list it is on; a
  stock on Launches and 3-SETUPS). Before, the tab followed the stock's lists when you looked, with the live Trend label
  (KD's EARLY sat on Watchlist). Browser test at 9:45 Nov 4: KD's EARLY and ★★ catalyst on Launches; Watchlist = 9
  3-SETUPS breakouts (NAVN, KSS, XMTR, KYMR, ARLO ...); group moves on every tab. Lines logged before keep the old filing.
- **TREND triggers (LIVE Nov 4 2026 ~9 PM with test/alertboxes, branch test/trendtrig; the user, Nov 4 night: only 3-SETUPS and TREND of the 5 Watchlist lists
  trigger, Launches has its own; "watchlist needs trigger for trend watchlist as
  well, setup and trend")**: desktop liveAlerts ':trend' = a TREND-list stock (2-POOL / 1-UPDAY / 1-EP/GAP, Trend Up / Turn
  up / Reclaim / Resting at the last close, not on Launches / Launch laggards / 3-SETUPS) trading over its buy point with
  the close under it; over the 200 SMA and 30%+ over the 52-week low (as 3-SETUPS); a trigger (bell); Watchlist tab. A
  stock with a launch-type alert today: no TREND pop-up, and its 3-SETUPS / TREND triggers are filed on Launches (ARLO Nov
  4). Nov 4 test: XNCR, BRZE (LW intraday); PCOR, RELY only their launch alerts. Phone (alerts.py) not done: on hold.
- **Answered Nov 4 night**: many triggers at once -> the 🔔 Alerts tab, the boxes and the sounds per box (live). Still
  open: the page checking every 20 s from 9:30 to 10:00 with the user's GitHub key (the 60-an-hour limit), not asked yet.

## Phone alerts crashed after 9:34 on Nov 4: fixed (LIVE Nov 4 2026 evening, the user's "go live"; test/alertfix)

- radar/alerts.py find() raised KeyError 'base_days' on 3-SETUPS rows (2-POOL / 1-UPDAY: AMLX, XMTR, TARS ...; added to the
  live checks on Nov 3) once one traded over its base top, so every 5-minute / 1-minute check from 9:35 failed: no phone
  alert and nothing in alerts.json after the 9:31-9:34 heads-ups (desktop alerts, computed in the browser, kept working).
  KD's POWER DAY at 9:35 ($15.30, +18.3%, vol 6.7x) is what the minute-by-minute replay fires (radar-tools `replay KD
  --every-minute` on test/kdreplay = last night's watch list). Fixed (base_days optional) and each followed row is now
  checked inside its own try (one bad row skips that stock only). Check after the Nov 5 open: alerts.json has items
  after 9:35.
- **Star logging live (test/starlog)**: the code grader logs each gapper's ★ star (★★ / ★ / ⚠, as the Stars column),
  Trend label and best group tier into codegrade.json / codegrade_log.json, for the stars x code grade comparison
  (check-ins scheduled Nov 11 and Nov 18, 5:40 PM ET, in session_01PkbDakDe1EUNP5wQZf4wMH). KD was ★★ on Nov 3.
- **Open: "W crossed the 200"**: the Watchlist and Launches take nothing under the 200 SMA; a W (laggard watch: real
  news, over the 50 and the 21-day closing high, under the 200) is where the backtest edge is once it crosses (77% within
  60 sessions, +6.5% the 20 after). Proposal: keep W names 60 sessions and alert on the first close over the 200, so
  they enter the over-200 world (Watchlist / Launches) on that day instead of after Launch laggards' 5 closes.

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

## Earnings tab, second round (live Nov 4 2026 ~1:15 PM, the user's "go live"; branches test/earnfix2, test/earnfix3; GV 8)

- **Revenue found 56 -> 79 of 89 reports**: "Net sales" / "Sales" too (SKY, SN, CE), "Total revenue" / "Net sales" rows in
  the tables further down (TVTX $224.6M, EL, CVI, PARR $3.05B where live had ~$2.06B from a growth %), the company's
  total before one product's sales (URGN $89.0M, not ZUSDURI's $68.0M), the exact table figure over a rounded headline
  (FBIN $1,113.7M, not "$1.1 billion" = a false -2.1% miss), 3-column tables (AMD this q | last q | last year).
- **EPS on one basis**: the old swap to Nasdaq's estimate when Yahoo's was 3x off (the MPC rule) is gone; Yahoo's
  estimate vs Yahoo's actual (FRSH +1000% -> +21.6%, LIFE +390% -> +25.1%, PCOR +264% -> +13.0%); Nasdaq's actual vs
  Nasdaq's estimate. EPS growth "n/m" under 5 cents a year ago (AEHR), "n/m (one-off)" when last year's quarter was
  2.5x+ and the release names a one-time gain (DUOL's $222.7M tax benefit).
- **Guidance**: every outlook section searched for the number (ALAB $730-750M +12.9%, RAL, BETA, VGNT); new vs prior
  numbers set raised / lowered / reaffirmed (ADEA, QDEL lowered; INSP narrowed = reaffirmed; "As of date | As of date"
  columns); one product's guide shown as "JELMYTO only", +1 / -1 (URGN); long-term targets ignored; results rows skipped.
- **New q/q**: EPS growth and Rev growth cells show "q/q" (vs last quarter, Yahoo) and "last q y/y" with ▲ speeding up /
  ▼ slowing (DUOL: +13.7% y/y, q/q +3.5%, ▼ last q +18.3%).
- Tested on all 86 releases (radar-tools `reltext`) and a full build (radar-tools `earntest` -> radar-data
  earnings_test.json, the portal doesn't read it); 22 reads changed by the fixes (AVT, Q, SOLS ... up; FBIN, PRGO,
  QDEL, OUST down); the Nov 3 hand-checked names unchanged except AEHR "n/m". Rules workbook updated.
- **Open**: Monday-Tuesday reports of the first week have no saved estimates (fixes itself next week); VRDN (one
  product), LQDA / PCVX / TNGX (no SEC release) have no revenue.

## Pre-market safety lock (live Nov 4 2026 ~2 PM, the user's go; branch test/pmlock; first used at the Nov 5 8:45 grading)

- radar/premarket_build.py finish, before the grades are saved: an A / B whose reason or flags hedge ("not confirmed",
  "unverified", "could not open") -> C; without a primary source (SEC, the company's site, a newswire with its release)
  -> C; an earnings gapper whose Earnings tab read points the other way -> one grade lower; every earnings gapper's
  flags carry the Earnings tab read. On Nov 4's grades: DUOL A -> C; RIOT A, NVTS B, ARRY B unchanged. No change to
  the 8:45 task's prompt is needed (finish() reads earnings.json from the checkout's radar-data).

## Earnings reader fix: this year's revenue, outlook tables (live Nov 4 2026 ~9:25 AM, the user's "fix it go live"; branch test/earnfix)

- **Why** (DUOL Nov 3 2026 after close, +20% pre-market): the Earnings tab read "Somewhat bearish, revenue miss -10.3%".
  The reader took last year's Q3 revenue ($271.7M, the first column of the release's table; actual $309.0M, +14%, a
  2% beat) and applied Q4's 14% growth to the full year (guide -2.1% vs street; the release's table: Q4 $322M, +2.4%).
  Now "Bullish". The 8:45 grader gave DUOL an A that morning without opening the release (its reason: "figures were
  not confirmed"): see Open below.
- radar/earnings.py (GV 5, the week re-read at 9:24): rev_from takes the figure that isn't last year's quarter when two
  come in a row (to the figure's own rounding; "$1.5 billion" is too rounded to tell: IT / KD), else the later year's
  column; guidance reads outlook tables under "(in millions)" after sentences with units, ranges with a minus sign or
  no second $ (ADEA 375-415), and the raised column of "Previous | Raised" tables (SOLS). Rules workbook updated.
- Checked on all 84 releases of the week (radar-tools `reltext` -> radar-data probe_reltext.json, the release texts
  for testing a reader fix offline): changed DUOL, DT, FRSH, SOLS, ADEA, each matching its release; PLTR HNGE LIFE
  LSCC AEHR ON XMTR TEM SHOP and VAL unchanged.
- **Open**: (1) URGN Nov 4 reads one product's revenue ($68.0M ZUSDURI) and one product's FY guide (JELMYTO ~$90M) as
  the company's (pre-existing, not from this fix); ADEA's cut outlook (395-435 -> 375-415) reads "reaffirmed".
  (2) DUOL EPS: Yahoo 1.32 vs 1.585 (-16.8%) while Nasdaq has 0.54 vs 0.55: different bases, not checked.
  (3) Pre-market grading (proposed, waiting for the user's go): a code gate in premarket_build.py finish (an A/B
  without a downloaded SEC filing / company release, or a reason saying "not confirmed", drops to C); then the
  grader gets the filings since the last close 4 PM (Friday 4 PM on Mondays) and the Earnings tab's numbers, and
  re-checks earnings.json at 8:57 for 8:30 reporters. (4) The user to decide: correct DUOL's Nov 4 A in gradelog
  or keep it as the record.

## Status at the end of the session "Radar: work session (Nov 4)" (Nov 4 midday - Nov 5 2026: the portal's tables)

- **Live on main** (each after the user's "go live"; display only: no scanner, alert or grading code touched, so no
  regress / 2-year check was needed; each checked in the browser against main and on the merged page):
  (1) Launch watch: ADR column, Claude's 8:45 grade in the Earnings cell, the Earnings tab's Read in its own "ER look"
  column; (2) your table layouts on all 20 tables: drag a header to move, ⚙ / "⚙ Columns" list to delete (✕) and bring
  back, Reset, + add from a catalog of ~50 stock columns; (3) column widths (drag a header's right edge; double-click /
  "Normal widths" = back); (4) Gainers & losers "Gap up / Gap down ≥" filter + a Gap catalog column; (5) the Desktop
  alerts explanation folds away ("What pops up, and when"); (6) + Filter on the Watchlist, Launches and Gainers.
  Details in the sections below.
- **Test branches**: test/lwcols, test/columns, test/colwidth, test/gapfilter, test/alertfold, test/xfilter = all
  merged (nothing waiting). **test/chgname** (the change columns renamed Change 1D / 1W / ...) = NOT wanted (the user, Nov 5: "no need, 1D
  would work"): don't merge it. Today's live change % is the catalog column "1D"; live Nov 5 (the user's go, branch test/chgalias):
  the search finds it by "1d", "today", "chg" or "change" (the names other tables use: Today, Chg, Day). test/grfilter (from before) still conflicts with main (see the older status).
- **Agreed with the user**: layouts, widths and + Filter filters are per browser (desktop and phone keep their own); the
  ticker column stays first; a filter on a table's column uses the value the cell shows; the + Filter picker is a search
  box only (no full list), a criterion already added is removed from the search ("✓ added") or its chip's ✕.
  No new agreed reads (tools/examples.txt unchanged).
- **Open (each needs the user's go)**: Export / Import of the layouts between devices (offered, no answer); the older
  open items below are unchanged (Launches Group tick-box filter on test/grfilter, Base day from the base's high, the
  1 ADR confluence distance, the retest zone, GROUP MOVE noise, ★★ caveat, Earnings reader misses, momentum cutoff).
- **First thing to check next session**: the user's own layouts / filters on the real portal (any table looking odd:
  ⚙ Columns → Reset this table); the Gap filter in the first 10 minutes after 9:30 (NYSE opens come late: those stocks
  are left out while a Gap is set); + Filter on Launches after the 4:40 PM scan (the rows rebuild, the filters re-apply).
- **Watch out**: other sessions edit docs/index.html the same day (Earnings reader, the desktop alert log): fetch main
  before merging and re-test the merged page. How this session tested the portal: serve docs/ with python3 -m
  http.server, Playwright against it (it loads radar-data from raw.githubusercontent.com), compare every table's
  header and rows with main's page served the same way (an empty layout must read the same), then drive the feature.
  A long shell command with a heredoc + background servers can trip the safety check: put the script in a file first.

## + Filter: your own filters on the Watchlist, Launches and Gainers (live Nov 5 2026, the user's "go live"; branch test/xfilter)

- **What**: a "+ Filter" button in the filter row of the Watchlist (.tgr-flt wl), Launches / Launch laggards (.tgr-flt ln)
  and Gainers & losers (#g-filters). The picker is a search box only (the user: "I don't want to see all column names"):
  typed letters list this table's own columns first ("In this table", the layout's order, deleted ones left out), then
  the column catalog ("More"); a criterion already added shows "✓ added · click to remove". A chip per filter: numbers
  ≥ / ≤ a value, Trend / Group rank / Stars / ER look / grades / Watchlist list pick from a list, text has / is / has no.
  Empty box = off; while set, a stock without a value is left out. ✕ removes. Saved in radar-filters (wl / ln / g .x).
  Gainers' "Reset to my defaults" clears its own.
- **How**: catalog criteria (f.id) run in fltPass (Watchlist / Launches: the counts in the note, "Filtered: ...",
  Download follow) and in passes() for Gainers (count, theme / industry tables follow). A table's own column (f.col):
  Gainers from the stock row's field (gField: same value as the cell); Watchlist / Launches from what the cell shows
  (xcApply after each draw: number = the cell's first number when 70%+ of the column's cells are numbers, else text;
  rows hidden with .xf-off, XHID[table] -> the Download skips them; "→ N shown" next to the chips). Trend / Group rank /
  Stars / ER look columns map to the catalog's pick lists (XF_COLCAT).
- Checked Nov 4 close data: Launches Base day ≥ 10 = 49 of 141, + Depth ≤ 25 = 37 (download 37); Watchlist TREND ADR% ≥ 4
  = 125 of 184, + Trend is Up = 97 (download 97); Gainers ADR% ≥ 6 = 19 of 142 (themes 29 -> 7), + Industry has
  "software" = 3. Rules sheet G1 notes it.

## Desktop alerts: the long explanation folds away (live Nov 4 2026 evening, the user's "go live"; branch test/alertfold)

- The Desktop alerts card (Launches / Launch laggards / Watchlist) shows a "▸ What pops up, and when" box (tgr-more,
  data-key alerts, closed by default, remembered) holding the long text (#ln-alert-more), then one short status line
  (#ln-alert-note: "On: pop-ups while this page is open ...; triggers stay on screen until you close them, heads-ups
  fade. Today:" / Off / blocked), then the log. Text only: no alert changed.

## Gainers & losers: Gap filter (live Nov 4 2026 evening, the user's "go live"; branch test/gapfilter)

- "Gap up ≥ __ %" next to "Up at least" (Losers: "Gap down ≥", keeps gap-downs of at least that size); off by default
  (PDEF g_gap null; Reset clears it; like the other Gainers filters it is not kept over a reload). Gap = today's open
  (live.json rows[sym][5]) vs yesterday's close (price / (1 + chg_1d)); applyLive writes stocks rows' open / gap_pct, and
  after the evening build (live.session == build asof) takes the open from the day's last live snapshot. While the box
  is set a stock without an open yet is left out (Yahoo's NYSE opens are empty the first ~10 minutes). Also a "Gap"
  column in the column catalog. Rules sheet G1 updated. Checked Nov 4 5 PM: Gap up ≥ 3 = 61 of 142 (KD +15.2% =
  14.91 on 12.94, DUOL +26.4%, PCOR +6.0%, against live.json / stocks.json); Losers Gap down ≥ 2 = 19 of 45.

## Your table layouts: move / delete / add columns on every table (live Nov 4 2026, the user's "go live"; branch test/columns)

- **What**: on all 20 tables (every tab) the user drags a header to move a column, hovers a header and clicks ✕ to
  delete it, and opens **⚙** (in the first header, next to Ticker) for the list: ↑ ↓ (phone), ✕, "+ bring back", Reset
  this table, and **+ Add a column** = a search over a catalog of ~50 stock columns (price / 1D-3M / off 52W high / over
  52W low, rel vol, ADR, $ vol, avg vol, vs 200D / 50 EMA / 21 EMA, Trend live / last close, Group rank, RS, Stars,
  earnings date, ER look, earnings move, pre-market grade / chg / gap / $ vol, Launches fields (Launched, grade, status,
  trigger, buy point, away, base day / length / depth, LD -> now, max, correction), Watchlist list / section / buy point
  / why, company, sector, industry, themes, index, revenue). An added column lands right after the ticker and sorts on
  a header click. Group tables (Themes, Industries, Gainers groups, Groups, History test, Track record) get move /
  delete only (no ticker in the rows).
- **How** (docs/index.html, "your table layouts"): the tables build as before; a MutationObserver on each tbody
  re-applies the layout after every draw (reorders cells by their header key, hides deleted ones with .col-off, adds
  catalog cells looked up by the row's ticker). Keys = the header's data-sort, else its text. Layout per tab + table
  (Launches and Launch laggards share ln-table but keep separate layouts), in localStorage `radar-layout` (per
  browser: desktop and phone keep their own). The old "Columns" tick boxes are gone; what they hid (radar-cols-<id>)
  carries over as deleted. Ticker stays first. A column added to a table's code later lands where the code puts it.
- **Column widths + Columns button (live Nov 4 2026, the user's "go live"; branch test/colwidth)**: drag a header's right
  edge to narrow / widen a column (every row follows; narrowed text wraps or is cut with …), double-click the edge =
  normal width, "Normal widths" in the list resets all widths (keeps the order). Saved in the same layout (`w`). A
  visible "⚙ Columns: move · resize · delete · + add" button sits above every table (the user didn't see the ⚙ in the
  first header at first).
- **No ✕ on the headers (live Nov 5 2026, the user's go; branch test/nohdrx)**: on narrow columns (1D, 63 px) the hover ✕
  sat on the label and closed columns by mistake; a header click now only sorts. Delete = ✕ on the column's row in the
  ⚙ Columns list; "+ bring back" there.
- **New table columns in code**: give the header a data-sort key (stable layout key). New stock data worth adding by
  hand: add a line to CATL.
- Checked: no saved layout = every table identical to main; delete / drag / add / sort / reload / bring back / Reset,
  Launches vs laggards separate, Earnings redraws keep it, Launches redraw as fast as before, phone menu.

## Launch watch: ADR column, earnings Read and grade (live Nov 4 2026 morning, the user's "go live"; branch test/lwcols)

- Pre-market tab, ★ Launch watch card only (display): an **ADR** column (adr_20 at the last close, base_stocks.json;
  red under 3.5%) after To base high; an **ER look** column after Earnings = the Earnings tab's **Read** (earnings.json
  read, points / why in the tooltip, sortable; the user: its own column, not inside Earnings); the **Earnings** cell adds **Claude's 8:45 AM grade** (premarket.json, graded today) with the
  catalyst / reason in the tooltip. Nov 4: IT / TRI Mixed, BRKR / KD Bullish, PCOR Strong bullish, SWKS / QDEL Somewhat
  bearish; no starred name was graded that morning (RIOT DUOL NVTS ARRY FSLR OSCR HCA PLUG), the badge checked with a
  fake row in the browser. Not a rule: no rules workbook change, no regress needed.

## 3-SETUPS: every buy point alerts live; Watchlist alert log; Group rank filter (live Nov 3 2026 late evening, the user's "go live")

- **Why** (AMPL Nov 3 2026): "Triggered today: Retest held" (its breakout level 15.93-16.18 with the 21 EMA) after the
  close, no alert in the day: 3-SETUPS names only alerted on a cross of the Buy point column (17.84, the next top).
  Agreed Nov 1 was "desktop alerts for every 3-SETUPS trigger".
- **Now**: scanner/launch.py saves each 3-SETUPS row's follow() fields (setups3 "live", S3_LIVE; also source / added);
  radar/alerts.py s3_rows() runs them through the Launches entry loop (breakout, flag line, pop, push, retest zone /
  holding, 21 EMA, breakout undercut & reclaim, gap out of base; tier from the stock's best group), row_of() for the
  chart checks; only over the 200 SMA; a name on Launches / laggards alerts from there only. fast.py watches them.
  The portal does the same (s3Live). Tested: AMPL at 3:46 -> "AMPL RETEST HOLDING into the close + 10 EMA & 21 EMA".
- **Watchlist tab: its own desktop alert log** (the card moves to the tab you are on): the alerts of stocks not on
  Launches / laggards; Launches shows its own; group moves on both. One pop-up per alert.
- **Group rank filter on the Watchlist** (all / ★ Top / Top + Strong, the stock's best group; with RS / Trend, kept in
  the browser; not on Launches). Nov 3: 3-SETUPS 63 -> 7 Top / 11 Top+Strong; TREND 137 -> 14 / 28.
- The evening scan was re-run by hand after go live (Nov 3 close, date checked): 53 on 3-SETUPS, all with live
  fields; the 200 SMA rule already took ECHO BLDR QDEL STOK TEX RH TNDM SHAK BEAM LEGN off.

## Alerts: triggers first, full log, group moves (live Nov 3 2026 evening, the user's "go live"; branch test/alertlog)

- **Why** (RPD Nov 3 2026, 3:46 PM): 28 alerts came due when the 3:45 "holding into the close" checks opened; the cap
  of 8 a run was applied BEFORE today's 1-minute chart checks (6 of the 8 slots failed them, only MAZE went out) and the
  other 21 became "21 more alerts: ... RPD, RPD ..." (tickers only, unchecked, marked sent, never retried, SPY chart on click).
- **Now** (radar/alerts.py main): the chart checks run first; **triggers** (TRIGGERS: power, catalyst, basebreak, launch,
  reversal, laggard, breakout, retest, reclaimbo2, ema50, push, pop, gapbase/gob1/gob5, confirm, s3, ema21bl, the 21 EMA
  undercut & reclaim, grp:) always get their own alert (MAX_TRIGGERS 15 a run); heads-ups fill the rest of 8, the others
  grouped in one alert naming each (ticker, kind, price). Every alert's full text is in alerts.json items (kind,
  grouped, groups) -> the portal's log shows each, click = its chart.
- **21 EMA retest alone = heads-up** (the user: "not a strong sign by itself"); holding over the breakout level too,
  today's low within 1 ADR over it = trigger "21 EMA RETEST + BREAKOUT LEVEL $x" (key SYM:ema21bl; RPD: low 14.41,
  level 13.84). One alert per move (a stock whose breakout-level retest holds doesn't also get the 21 EMA one).
- **Group moves** (the user: RPD and QLYS both Cybersecurity at 3:46): 2+ stocks of the same theme or tight industry
  group alerting the same day (any alert; loose "· other" industries don't count; a theme and a group with the same
  stocks = one move, the better-ranked names it): each alert adds "CYBERSECURITY MOVE: also QLYS retest holding 15:46",
  and one "GROUP MOVE: Cybersecurity (#18/99, 14 stocks): RPD, QLYS" alert a day per group (key grp:<group>, a trigger).
  Same tag on the portal's own pop-ups (gm in localStorage).
- **Desktop**: triggers and starred (★) alerts share one notify(): stay until closed, chime, flash the tab; log lines
  bold with a red dot, clickable. Merged with the Nov 4 stars work (★★★ also on ema21bl).
- **Not changed**: the scan's retest zone (RPD's low 0.45 ADR over the level still reads "21 EMA retest" after the
  close; widening the zone = its own "explain first"). Open: the 1 ADR for the confluence is my pick (ask); big themes
  (Enterprise SaaS 45 stocks) may give many GROUP MOVEs at 3:45: a 3-stock rule for 20+ stock themes if noisy.
- **Watch out**: the Follow picks run at 8:56 PM ET Nov 3 built from Yahoo bars without the Nov 3 candle (Yahoo
  rewrites the day's bar in the evening) -> a Nov 2 list; launch.json restored from 707ac36 (690f248). Don't run
  picks.yml in the evening without checking launch.json "date" afterwards.

## Status at the end of the session "Radar: work session (Nov 4)" (Nov 3 evening - early Nov 4 2026)

- **Live on main** (each after the user's "go live"; regress: every agreed example reads the same): the RS / Trend
  filters on the Watchlist and Launches, the narrower Group rank / Group on launch day / 21 EMA exit / Resistance cells,
  Download for TradingView on Launches (test/filters); Off 52W high, Correction (now) and Base length (the current base)
  on Launches (test/accurate; Base length / Correction show with the first Launches build on the new code, the Nov 4 4:40
  PM scan); the Follow picks guard (test/guard). Details in the entries below.
- **Only on a test branch**: `test/grfilter` = the Group tick-box filter on Launches / Launch laggards (★ Top / Strong /
  Rest / No rank, the Group rank column's tier; Nov 3 close: Top + Strong = 24 of 113). The user saw it but never said
  "go live". It now CONFLICTS with main in docs/index.html (another session added a Watchlist Group rank dropdown in the
  same .tgr-flt builder): rebuild it on top of main (reuse that session's style for Launches) before asking for the go.
- **Data fix**: setups/launch.json restored by hand to the Nov 3 build minus SLN (ea5222b) after the 9:10 PM rebuild.
- **No new agreed reads** (tools/examples.txt unchanged). Phone alerts, Alpaca, fetch.py untouched.
- **Open**: Launches Group filter (above); Base day still follows the Status (MRNA: top Oct 21 = Base length 10, Base day
  17): ask if it should count from the base's high; whether the user's "135 off the 52W high" for ACN came from another
  source (the portal: 12.6% under 291.09 at 254.56).
- **First thing to check next session**: after the Nov 4 4:40 PM scan, Launches rows carry trig_base_len /
  off_52w_high_pct / correction_now_pct (ACN-like rows: Base length = Base day); any Follow picks run in the evening logs
  "GUARD" if Yahoo serves an older close.

## Launches: accurate Base length, Off 52W high, Correction (live Nov 4 2026, the user's "go live"; branch test/accurate)

- **Off 52W high** replaces "% of 52W high" (that was the launch day's: ACN 73% = the Oct 1 close 212.30 / the Jan 14
  high 291.09): how far under the 52-week high now, live in the session (from stocks.json high_52w until the evening
  build writes launch rows' high_52w / off_52w_high_pct). ACN Nov 3: 12.6% under 291.09.
- **Correction** = the deepest drop after the 52-week high, to now (correction_now_pct / correction_low(_date); ACN 59.4%,
  Jan 14 291.09 -> Jun 22 118.15). The "neglected" tag still uses the launch day's (its tooltip says so).
- **Base length** = the current base: sessions since the trigger's base top was set (trig_base_len, day 1 = its high;
  ACN 9 = Base day 9, was 190). base_days is unchanged (the level's reach: nothing above 259.39 since Feb 2, 190
  sessions): in the tooltip and in the breakout alert text. Base day still follows the Status (some count from the leg's
  breakout: MRNA top Oct 21 = length 10, Base day 17): not changed, ask the user if they want it from the high.
- Launch rows only get the new fields with the next Launches build (4:40 PM scan); dry build 41762168151 (Nov 3 close)
  checked: ACN 9 / 12.5% / 59.4%. Regress: same.
- **Evening rebuild pitfall again (Nov 3, 9:10 PM)**: the user's ✕ on SLN ran Follow picks on Yahoo bars without the Nov 3
  candle -> a Nov 2 list; restored by hand (ea5222b: 690f248's list minus SLN). **Guard live (Nov 4, the user's go)**:
  picks.yml keeps the live setups/launch.json when the rebuild's "date" is older (log line "GUARD: ... not saved"); the
  picks / removals stay in picks.json for the next build. Only picks.yml (the scanner.yml 4:40 PM scan is unchanged).
  Not done (the user: no): Alpaca daily bars instead of Yahoo; Alpaca stays the intraday / pre-market volume source only.

## Portal filters and narrow columns (live Nov 4 2026, the user's "go live"; branch test/filters, display only)

- **RS and Trend filters** on the Watchlist (all five lists, TREND too) and on Launches / Launch laggards: an RS
  dropdown (All / 97+ / 90+ / 80+ = at least that RS) and a "Trend: ▾" dropdown of tick boxes (Up, Turn up, Reclaim,
  Resting, Negative, No trend "—"; any of the ticked, live Trend). One set for the Watchlist, one for Launches, kept in
  the browser (localStorage `radar-filters`). A Launches ticker search still ignores every filter. The table note says
  what is filtered. Nov 3 close: TREND + RS 97+ + Resting / Reclaim = 6 of 137; Launches RS 90+ + Up = 40 of 113.
- **Narrower cells**: Group rank (everywhere: "Strong #22/213" over "Financial Tech… #1/5", the name cut at ~8.5em, all
  of it in the tooltip), Group on launch day (the same, "(industry)" dropped), 21 EMA exit (date over the %), Resistance
  ("3M $101.32 +3.4%"); the long headers wrap on two lines.
- **Download for TradingView on Launches / Launch laggards**: the rows on screen (filters applied) in their order, one
  ###Launches (or ###Launch laggards) section, for TradingView's Watchlist menu → Import list.
- Merged with the conviction-stars work of the same day (a conflict in docs/index.html: both kept). Regress: same.

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

- **Conviction stars (LIVE Nov 4 2026, the user's "go live"; test branch test/stars, study on test/combo)**: the
  combination study (tools/combo_study.py, tools/combo_results.xlsx on test/combo; radar-tools `combotags` tags the
  tested trades with group / RS / Trend -> radar-data probe_combo_tags.json): group rank x RS x Trend on 5,493 live
  launch alerts and 5,783 Launches buy points, Aug 2025 - Oct 2026, the user's management, kept only when both halves
  are positive, plus a luck line (shuffled labels). Stars, from yesterday's close for a launch today: **★★** = best
  group Top/Strong and under the 21 EMA (+0.55R, 222); **★** = Trend Up (+0.33R, 1,203); **⚠ skip** = no Trend label
  (-0.05R, 822); all alerts +0.16R. **★★★** = a pullback entry (retest, push, 21 EMA retest / U&R, breakout U&R) on a
  launch with Top/Strong group, RS 80+, Trend Up, bought at the close, stop the day's low (+0.68R, 169; the only one
  that beat the luck line); the "★★★ on a pullback" tag on Launches only once retest_away (ran 1.25+ ADRs over the
  level: GDDY Nov 2026 didn't advance, no tag). Gap size checked: any gap up counts (0-4% ★★ +0.61R vs 4%+ +0.25R on
  36; ★ +0.33 vs +0.32): a regular launch needs only gap > 0 and a 5%+ day (69% of regular launches gapped under 4%).
  Not starred (tested): RS 97+ before the open (6 launches had it the day before), breakouts on the 5-min entry (2nd
  half negative everywhere), Launching today bought at the close (+0.04R), earnings (3 months of dates only).
  Portal: Pre-market tab "★ Launch watch" (the evening watch list, starred; from the pre-market scan after the list's
  close only names gapping up; Copy ★★ / ★ / all shown), Stars column on the graded gappers, ★ tag in the live scanner,
  Stars + Trend (yesterday) on Launching today, ★★★ tags on Launches; desktop alerts: ★★ / ★ in the launch alerts' titles
  and a ':stars' alert for a starred stock launching, ★★★ added on the desktop to the job's retest / push / ema21 /
  reclaimbo2 alerts; starred alerts stay until clicked, with a tone. Phone alerts unchanged (alerts.py untouched).
  Rules sheet A2. `tools/replay.py --regress`: same. The History test table's Top/Strong rows change with the Nov 4 4:40
  PM scan (today's groups; the 4:24 PM Nov 3 table still had the old industries: Top 198 -> 69).

## Tech review (Nov 3 2026, study only, branch `test/techreview`, radar-tools `techreview` -> radar-data probe_tech.json)

- 561 tech / growth stocks $2B+; 231 in no tight group and no theme. 116 move on their own (best fit under 0.5, no
  partner at 0.55+): META, APP, SHOP, RBLX, RDDT, CVNA, SE, TTWO, ... (their RS is what matters); 65 pairs only
  (CDNS-SNPS 0.77, NFLX-SPOT 0.58, AFRM-XYZ 0.58, JOBY-ACHR 0.69, HPQ-LOGI 0.61; ORCL tracks CRWV 0.60 only); 22 fit an
  existing theme/group at 0.6+ (GEN Enterprise SaaS, IPGP Semi Test & Packaging, AMBA AI Connectivity, TDC Software
  Collaboration, ...); new groups found: Network & App Delivery (FFIV AKAM FSLY NTCT ATEN RDWR, 0.54) and Aerospace
  Components (GE HWM HEI WWD SARO VSEC HXL, 0.52). Spreadsheet sent to the user (tech_review.xlsx).
- The user chose (on my recommendation) the two new groups + GEN / IPGP / AMBA / TDC, NOT pair groups (CDNS-SNPS,
  JOBY-ACHR: use RS). LIVE (merged to main Nov 3 evening; data from the Nov 4 after-close refresh): industry_groups.json (FFIV AKAM FSLY out of
  Cloud & Observability, NTCT ATEN RDWR out of Cybersecurity, TDC to Collaboration, AMBA to AI Connectivity), theme_adds
  (GEN Enterprise SaaS, IPGP Semi Test & Packaging). Dry run 41727414113: 147 tight groups (1,309 stocks); Network & App
  Delivery 0.52 (6), Aerospace Components 0.51 (6, HXL out); TDC in; AMBA, GEN, IPGP under 0.6 this week (they join
  in a week they qualify). Regress same, browser no errors.

## Status: hand-picked theme members (Nov 3 2026): LIVE (merged Nov 3; the after-close refresh rerun on the new code
## at 4:35 PM ET, Launches rebuilt: 145 groups, 1,293 stocks in them, 48 approved names in their themes)

- 60 stocks that were in no theme but moved with one at 0.6+ (the 304 the group test dropped, checked: 114 already in
  their theme, 84 in none; ~15 of those 84 were coincidence and left out) go in radar/theme_adds.json; pipeline.py adds
  each to its theme (core: ext; auto group: its members) only in weeks it tracks the theme at 0.6+, without the sector
  / liquidity filters of the automatic adds. Dry run 41714934810: 49 joined (12 under 0.6 this week, e.g. LNG, OKE,
  RDWR, VCYT); theme strengths about the same (Steel 0.69 -> 0.63 the largest). Regress: same. Browser: no errors.
- The 99 that fit another industry group are NOT moved (cross-business coincidence, e.g. DPZ / Insurance Brokers).
- Go live = merge test/themeadds into main (rules workbook updated in the branch).

## Status: industry groups by business line (Nov 3 2026, the group-rank session): LIVE (merged to main Nov 3, 3:27 PM ET)

- **Built on `test/groups`, not on main.** radar/industry_groups.json (90 hand groups, finest in tech; else the Yahoo
  industry from profiles.json; US banks split Regional $3B+ / Community); radar/pipeline.py prunes each group with the
  themes' co-movement test (0.6 floor, 3+ tight stocks) and writes groups.json + stocks.json `group`; scanner/launch.py
  ranks the tight groups with tiers and the loose stocks as "<industry> · other" (rank, no tier, capped just under
  Strong as a stock's best group); radar/day.py refreshes profiles.json weekly and publishes groups.json; the portal's
  Industry list defaults to **Groups** with a Strength column (Broad / Detailed unranked). Theme fix: "AI Compute"
  merged into **AI Chips & CPUs**.
- **Tests**: rolling (monthly re-prune, no look-ahead) launches in Top+Strong ran 20%+ 36.3% (193) vs 32.2% (376) now;
  2nd year 32.5% vs 30.7%; Top avg 20-day +8.5% vs +4.9%. Dry run (radar-tools `groupsdry`, run 41707525654): 145
  tight groups, 1,296 stocks, avg strength 0.64; 213 industry rows ranked (69 loose); radar-data *_dry.json. Browser:
  no errors. `tools/replay.py --regress`: every agreed example reads the same.
- **Go live** = merge test/groups into main (rules workbook already updated in the branch), then rebuild Launches
  (picks.yml) and run the day job so stocks.json / groups.json are written. Named groups have no ETF column yet.
- The user has `proposed_groups_v3.xlsx` to review; stock/group moves go into radar/industry_groups.json.

- **Trend column (live Nov 3 2026, after the user's read was confirmed)**: Watchlist, Earnings, Gainers, Launches (+
  laggards). Base: 10 EMA > 21 > 50 and the 50 higher than 5 sessions ago (the user added 10 > 21). First match wins:
  Negative (under the 21) / Reclaim (back over the 21 after a close under) / Turn up (5 EMA crosses over the 10, that
  day) / Up (base, over the 21 & 50, 10 & 21 rising) / Resting (base, 10 or 21 flat) / "-". Nd = sessions in it. Built
  in radar/pipeline.py (trend_at / trend_info -> stocks.json trend, trend_days, tr = [e5, e10, e21, e50, e50 4
  back, close]); live in the portal (today's EMA = last close's + 2/(n+1) x (price - it)). Until the nightly build
  carries it (from Wed Nov 4's build, the first on the new code), the portal reads radar-data trend.json of the same
  close (radar-tools `trendnow`, run by hand Nov 3 evening: 3,198 stocks). Rules sheet T1. radar-tools `pipedry` =
  the nightly build on a branch -> radar-data stocks_dry.json.
- **200 SMA rule (live Nov 3 2026, the user's go; takes effect with the Nov 4 4:40 PM scan)**: 3-SETUPS comes on only
  with a close over the 200 SMA and leaves after 2 closes in a row under it (scanner/launch.py s3_read; the dry run
  Nov 3: 63 -> 53, off ECHO BLDR QDEL STOK TEX RH TNDM SHAK BEAM LEGN); Launches: off **only while** its last 2 closes
  are under the 200 SMA, back the first close over it (the user chose this, "option 3": ACN Oct 2026 dipped under it
  right after its launch and then ran +33%; only BEAM off on Nov 3); laggards exempt (a laggard moved to the launch
  list follows it). The real 200 SMA only (st.sma200): a new listing without one is not held back (MWH). L["off_200"]=2.
- **TREND list (live Nov 3 2026)**: a 5th list on the Watchlist tab, built in the portal: every name on 3-SETUPS,
  2-POOL, 1-UPDAY, 1-EP/GAP and Launches whose Trend is Up / Turn up / Reclaim / Resting now (live); Section = where it
  came from (Launches first); sorted by the Trend, most days first; it leaves when the Trend turns Negative or loses
  its label (still on its own list). 137 names on Nov 3. Rules T1.

## Status at the end of the alerts session (Nov 3 evening 2026, session "Radar: work session (Nov 4)")

- **Live on main** (each after the user's "go live"; `tools/replay.py --regress`: every agreed example reads the same;
  details in the two sections at the top): (1) **alerts: triggers first, every alert in full, loud desktop triggers**
  (the 3:46 PM flood that swallowed RPD), the **21 EMA retest + breakout level** confluence as a trigger, **group
  moves** (2+ stocks of a theme / tight group alerting the same day: tag + one GROUP MOVE alert); (2) the **Watchlist
  Group rank filter** (all / ★ Top / Top + Strong); (3) **every 3-SETUPS buy point alerts live as on Launches** (AMPL)
  and the **Watchlist tab's own alert log**. Evening scan re-run by hand after (3): Nov 3 close, 53 on 3-SETUPS with
  their live fields, so the new alerts work from Wed Nov 4's session.
- **LIVE (the user's go at the wrap-up)**: `test/wllog` merged = the Watchlist alert log shows ONLY 3-SETUPS and TREND
  tickers not on Launches / laggards (the user: "only trend and setups trigger"); the Launches log keeps the rest
  (the 50 EMA undercut tab, pre-market grades; both leaked into the Watchlist log on main); GROUP MOVE on both.
  Browser-tested on main after the merge, no errors.
- **Agreed with the user** (no new agreed reads; tools/examples.txt unchanged): one pop-up per alert, a stock on both
  lists alerts from Launches; a 21 EMA retest alone is a heads-up, with the breakout level under it a trigger; group
  moves count at 2 stocks, themes and tight groups both; every 3-SETUPS buy point is an alert (not only the cross of
  the Buy point column).
- **Open (each needs the user's go)**: (b) the 1 ADR distance for the breakout-level
  confluence (my pick); (c) the scan's retest zone (0.2 ADR over the level: RPD Nov 3, low 0.45 ADR over it, reads
  "21 EMA retest", not "retest held") = an "explain first"; (d) if GROUP MOVEs are noisy at 3:45, 3 stocks for themes
  of 20+ stocks.
- **First thing to check Wed Nov 4**: the 3:45 PM run (each trigger its own pop-up, grouped heads-ups name each one,
  no "N more alerts" lines); 3-SETUPS entries alerting (Watchlist log); GROUP MOVE lines; the 4:40 PM scan keeps the
  setups3 "live" fields (scanner.yml uses the same launch.py --watchlist path).

## Status at the end of the last session (Nov 3 evening - Nov 4 2026: the combination study and the conviction stars)

- **Live on main** (the user's "go live", merged f4bc7ad; portal deploy checked, no browser errors; `tools/replay.py
  --regress`: every agreed example reads the same): the **conviction stars** (details in "Changes on Nov 2 2026" ->
  "Conviction stars"): Pre-market "★ Launch watch" (gapping up only, Copy buttons), Stars on graded gappers and
  Launching today, Trend (yesterday), ★★★ tags on Launches, starred desktop alerts. Phone alerts untouched.
- **Test / study branches**: test/stars = main (merged). test/combo = the study only (tools/combo_study.py,
  combo_xlsx.py, combo_results.xlsx, combo_cells.json, combo_luck.json; radar-tools `combotags`): not for main.
  The History test was re-run on today's groups (radar-tools `launchbt` on test/combo -> radar-data
  launch_bt_dry.json): Top 198 -> 69, Strong 188 -> 164 (+11.6% avg, 45% ran 20%+), RS 97+ in Top/Strong 53 -> 34
  (59% ran 20%+, median +2.5%); the portal's own table switches with the Nov 4 4:40 PM scan.
- **Agreed with the user (no new agreed reads; tools/examples.txt unchanged)**: the stars come from yesterday's
  close; buy only when a starred name actually launches (Launching today / its ★ alert), over the 5-minute opening
  range high, stop its low (buying every opening-range breakout of the list was NOT tested); any gap up counts (the
  user asked about 4%+ gaps: a regular launch needs only gap > 0 and a 5%+ day; 0-4% ★★ +0.61R (186) vs 4%+ +0.25R
  (36); ★ +0.33 vs +0.32; no gap filter); ★★★ = buy near the close, stop the day's low; a retest needs the stock to
  have advanced after the breakout (retest_away; GDDY Oct 30 - Nov 3 2026 didn't: no ★★★ tag). Buying Launching
  today at the close is NOT a star trade (+0.04R).
- **How strong each star is** (told to the user Nov 4): ★★★ proven (the only one over the luck line); ★ reliable,
  small edge (1,203 trades, the user's own Trend idea, p about 0.003 as one planned check); ★★ promising, not proven
  (found by the search, under the luck line: lift +0.39R vs luck 95% +0.44R). The ranking is by avg R.
- **Open (each needs the user's go)**: (1) rename / caveat ★★ on the portal ("promising, not proven"): offered,
  no answer yet; (2) 2 years of earnings dates to test an earnings star (only Aug-Oct 2026 dates exist: 26 of 321
  launches on earnings, 73% won but the same avg R); (3) the 3-SETUPS alert text (from Nov 3); (4) the Earnings
  reader's misses (from Nov 3).
- **First thing to check next session**: the ★ Launch watch from 7:00 AM (only gapping-up names), the first ★★ / ★
  desktop alerts with Launching today, any ★★★ alert at 3:45 PM (the 9 tagged: GPN BAH ICLR RHI GLOB APPN CRL MANH
  SLDE), the History test table on the new groups after the 4:40 PM scan, and the Nov 3 checks below (Trend in
  stocks.json, the 200 SMA rule, the Earnings tab).
- **Watch out**: this cloud session cannot reach github.io, Yahoo or Nasdaq (proxy 403); data work goes through
  radar-tools jobs and the GitHub tools; the portal's code can be checked locally with Playwright (it loads radar-data
  from raw.githubusercontent.com).

## Status at the session before (Nov 3 2026: Earnings, Trend, 200 SMA rule)

- **Live on main** (each after the user's "go live"; `tools/replay.py --regress`: every agreed example reads the same):
  the **Earnings tab** (no Claude; All week / Today's reactions / Day 2; week grid most liquid first, grouped by area;
  sortable; frozen narrow Stock column); **every alert needs the price 30%+ over the 52-week low**, **3-SETUPS
  alerts only over the 200 SMA**; **Watchlist vs 21 / vs 50 EMA**; the **Trend column** (Watchlist, Earnings,
  Gainers, Launches); the **TREND list** on the Watchlist; the **200 SMA rule** for 3-SETUPS and Launches (from the
  Nov 4 4:40 PM scan). Details in the Nov 3 entries above.
- **Test branches**: test/earnings, test/alerts52, test/trend, test/sma200, test/trendlist = main (nothing waiting).
  Other sessions merged test/pmrs, test/techgroups work (groups / theme adds) the same day: the rules workbook was
  regenerated after each merge (rules/scanner_rules.xlsx conflicts: always re-run rules/make_rules.py, never pick a side).
- **No new agreed reads** this session (tools/examples.txt unchanged).
- **Phone alerts: left alone** at the user's wish (they don't use them yet).
- **First thing to check next session (Wed Nov 4)**: the Trend in the morning (from trend.json of the Nov 3 close,
  live from 9:30); the Nov 4 nightly build carries the Trend in stocks.json itself (the first on the new pipeline
  code; then trend.json is no longer used); the 4:40 PM scan applies the 200 SMA rule (3-SETUPS should drop ECHO
  BLDR QDEL STOK TEX RH TNDM SHAK BEAM LEGN if still under; Launches: BEAM while under); the Earnings tab after the
  7:10-8:55 AM runs (estimates saved before the report from Nov 4 on).
- **Open from this session**: the Earnings reader's misses (fix + bump GV); revenue from the release's tables (SHOP);
  the 3-SETUPS alert text ("Ready" in a trigger alert, no "(light)" on the desktop; the user chose (a) only).
- **Watch out**: radar-tools keeps one pending run per group: a new dispatch cancels the waiting one (Nov 3: a
  setupsdry dispatch cancelled the waiting trendnow; other sessions use radar-tools too). Dispatch the next only once
  the previous is running.

## Status two sessions before (Nov 2 - early Nov 3 2026)

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

New from Nov 5 (alerts / pre-market day, session_01PkbDakDe1EUNP5wQZf4wMH), all unanswered by the user:
- **Power day vs episodic pivot**: drop the power day's +10% on the day, so the two differ only by the gap (8%+ vs
  6%+; both need 4x pace, over the 1-month high and the 200 SMA)? Asked twice, no answer: leave as is until the user says.
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
9. **Industry groups / themes (live Nov 3, the group-rank session)**: first check Wed Nov 4 after the close that the
   portal's Industry list shows "Groups" with Strength, Network & App Delivery and Aerospace Components appear, and
   Launches rows show the new group names. The weekly profiles.json refresh (day.py, when 7+ days old) is untested live:
   check it ran by Nov 10. Waiting names (join when 0.6+): AMBA (AI Connectivity group), GEN, IPGP and the 11 theme adds
   under 0.6 (LNG, OKE, RDWR, VCYT, ...). The user may still send moves from proposed_groups_v3.xlsx / tech_review.xlsx
   (edits go in radar/industry_groups.json or radar/theme_adds.json, test branch first). Decided: no pair groups
   (CDNS-SNPS, NFLX-SPOT, JOBY-ACHR: use RS); big loners (META, APP, SHOP, ORCL, RBLX, RDDT) stay "· other" with RS.
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

