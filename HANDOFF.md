# Handoff: how to work on the Theme & Group Radar

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
Claude starts asking again about agreed things or gets them wrong. The 8:47 AM grading has its own session: leave it
alone.

## Status at the end of the last session (Nov 1 2026)

- **Live on main** (Launches rebuilt, the evening scan re-run by hand): everything under "What the user agreed" below,
  including this session's launch-day rules, off-list rules, the ✕ buttons, the Launches table (narrower Status, ADR
  column), the new 3-SETUPS and its alerts, and the Watchlist's Why column next to Grade. The 2-year check script counts
  flag breaks within 0.5% of the line (was on `test/flag-inside-base`). All agreed examples pass
  (`tools/replay.py --regress`); tools/expected_reads.txt is unchanged.
- **Only on a test branch**: nothing. Every `test/...` branch of this session is merged (`test/launch-day-rules`,
  `test/remove-launch`, `test/off-list-rules`, `test/wl-why`, `test/setups3`, `test/ready-desktop-only`).
- **Agreed in this session**: LIFE's Oct 8 (21 EMA undercut & reclaim), Oct 20 (pop) and Oct 21 (breakout, leg 1) reads;
  INFQ's launch is May 21 2026 and the days after it are continuation (a power day is never replaced); HLIT Apr 30 2026
  stays out (it failed liquidity: about $9M a day, ADR about 2.9%): **don't change the liquidity rules for it**.
- **Launches after the rebuild (Oct 30 close)**: 109 launches (was 130). Off: TECH (ADR 0.2% after its Jun 25 gap,
  buyout-like), BRZE, CBZ, VEEV (ADR 3.04%), SYNA, ROKU, DV and the other ADR-under-3.2% names. Back on (older than
  120 sessions, still making new highs): AMN, HNGE, ILMN. Reversal launches on the list: GDDY Oct 30, FLS Oct 29,
  BEAM Oct 28, CART Oct 23.
- **3-SETUPS at that close**: 56 stocks: 8 Triggered today (TTAN flag breakout; IOT, AI, BSP 21 EMA retest; VSXY, DXC,
  CART retest held; CDNA breakout), 23 Ready (LIFE 44.81 0.5 ADR away tight ×4, APPN 50.41, ACN 259.39, EAT, CBRL,
  HUBS, MNDY...), 25 Setting up.
- **The phone**: the user hasn't subscribed the ntfy app to the topic yet; the first evening Ready file goes out after
  the Nov 2 close.

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

The 8:47 AM pre-market grading is a scheduled task (trig_01V4NoRakoyHHyi7AdnuGTCW) that runs in its own session;
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
- **Off the list** (Nov 1 2026): 2 closes in a row under the 50 EMA; **62 sessions from its highest point without a
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
- **Push** out of the 21 EMA with a gap after the retest's touch (ANF Aug 21, ACN Oct 8, CAI Oct 9); none while still
  under a flag's falling line (ARM Apr 8).
- **Bull flag**: the top at least a 1-month high; the pole = a run of 4+ ADRs made by the trend into it, not one gap
  day (a high that only retests an older top is the 2nd try of a flat top, no pole: ARM May 6); the high and 4+
  pullback days (a 5-day base); 1.25–4 ADRs deep; 3+ lower highs; surfing the 10 or 21 EMA (3+ days within an ADR);
  no close half an ADR under the 21 EMA; a controlled pullback, no violent drop (a gap down of 0.7+ ADR closing 1+ ADR
  down on 1.3x+ volume: ARM Apr 27–28 and May 7, ZS Oct 5: no flag). The line runs through the highs; a try that
  pokes half an ADR+ over it and closes back under is a failed try, the line stays (ARM Apr 10 failed, Apr 13 broke
  at 149.00). Entry: the close over the line and the 10 & 21 EMA; the alert fires at the line during the day. Within
  0.5% over the line = caution: the line stays the next trigger one more day, then the base top (TTAN Oct 30: 84.26
  over 84.00, next 84.28, then 87.75). Tag: the volume dried up the 2 days before (ZS Oct 21). Examples: SMCI Jun 28
  2023, CAI Aug 19 / Sep 14, VEEV Sep 23, ZS Oct 21, TTAN Oct 30, ARM Apr 13. A flag inside a base is an earlier
  entry (more room, less risk); the base can still turn into another pattern.
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
- **3rd try** (ascending triangle): the high is the 1st try, a 2nd within a quarter ADR after a real pullback, then a
  shallower pullback: the 3rd try usually breaks out (ARM Apr 24 / May 6 → May 20); not a falling wedge (VEEV Aug)
  and not a 2nd try that breaks out right away (a U or flat top: GMAB, ACN, ARM Apr 16–17).
- **Pop out of the consolidation** (entry in the base): ANF Oct 5.
- **Status**: "In the base" once the stock is 1.25+ ADRs under its high.
- **Watchlist flag** (scanner/run.py our_flag) follows the same flag rule.

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

## Open items (not done; each needs the user's go)

- Move the Launches rules box to the top of the tab (asked, not answered).
- Picks reading their history from the start; an intraday surge alert without a gap (offered earlier).
- 3-SETUPS: the check found two weaker Ready groups (on its list 31+ days: −0.9%; base under 2 ADRs deep: −0.7%); the
  user chose to keep the list as it is.
- Phone: subscribe the ntfy app to the topic (the user's side); check the first evening Ready file after the Nov 2 close.
