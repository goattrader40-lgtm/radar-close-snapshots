# Launch scanner rules

As of Nov 2, 2026. Source of truth: `scanner/launch.py`. Spreadsheet version: `rules/launch_rules.xlsx`.

## Must pass (all)

| Rule | Requirement | Notes |
|---|---|---|
| Liquid | Price $10+, 20-day avg $ volume $20M+, 600K+ shares a day, ADR 3.5%+ | Your settings (scanner/settings.json) |
| History | 200+ sessions | A newer listing needs 60+ sessions and uses its average close since listing as the 200 SMA |
| Above 52-week low | Close 30%+ above the 52-week low | - |
| 200 SMA | Close ABOVE the 200 SMA; the day before at most 28% above it (power day: up to 50%) | Laggards are the exception: they close UNDER it |
| No repeats | No other launch in the previous 20 sessions | Unless the stock closed under its 21 EMA since then |

## Launch types

| Type | Gap | Day's move | Volume (x 20-day avg) | Must clear 1-month (20-day) high? | Other conditions | Shown as |
|---|---|---|---|---|---|---|
| 1. Launch (regular) | Opened up (any gap) | +5%+, closes in the top half of the range | 1.5x+ | No (it is a grade ingredient: 'Base BO') | - | Type: Launch |
| 2. Power day | 8%+ | +10%+ | 4x+ | YES (since Nov 2, 2026) | May start up to 50% over the 200 SMA; closing in the lower half but holding half the gap = 'faded' | Type: Power day |
| 3. Catalyst | 5%+ | Closes up (can be under +5% or below the top half) | 2x+ | YES (by the candle bodies) | Earnings that day / the evening before, or an A/B pre-market grade; closes over the prior day's high | Type: Catalyst |
| 4. Reversal | Opened DOWN | +8%+, closes in the top half | 2x+ | YES | - | Type: Reversal |
| 5. Delayed | - | A regular launch | - | No | Within 10 sessions after a faded 3%+ gap on 3x+ volume that held its base; graded with that gap day | Type: Delayed |
| 6. Follower | - | +2%+, closes in the top half | 2x+ | YES (20-day high) | Within 10 sessions of an A/B launch by another stock in its theme | Type: Follower (follows XYZ) |
| 7. Laggard | Opened up | +5%+, closes in the top half | 2x+ | YES (since Nov 2, 2026) | Closes UNDER the 200 SMA; MUST have earnings or an A/B news grade that day; moves to Launches after 5 closes in a row over the 200 SMA | Launch laggards tab; then 'from laggards' on Launches |
| Your pick | - | - | - | - | Added with the Follow button; followed like a launch, no launch day to grade | Type: Your pick |

## Launch grade

| Grade | Rule |
|---|---|
| Ingredients | Volume 3x+ · gap 3%+ · base breakout (close over the previous 20 days' high) · a 10%+ day |
| A+ | Volume 3x+, a 6%+ gap and a base breakout, jumping from under the 200 SMA to over it ('go day') |
| A | Volume 3x+ and a base breakout, with a 3%+ gap or a 10%+ day |
| B | Two of the four ingredients |
| C | The rest |

## Breakout grade

| Grade | Rule | 2-year history (ran 10%+ / 20%+ in 20 days) |
|---|---|---|
| A | Early breakout (1st or 2nd since the launch, within 50 sessions) in a Leading theme, volume building the 5 days before | 62% / 35% |
| B | Early plus one of those two | 51% / 24% |
| C | The rest | 40% / 15% |

## Off the list

| Reason | Rule |
|---|---|
| 50 EMA | 3 closes in a row under the 50 EMA (after 2 it waits in the 50 EMA undercut list for the reclaim) |
| Stale | 62 sessions from its highest point without a new high |
| ADR | ADR (20 days) drops under 3.2% |
| Removed | You removed it with the X button |

## Tags

| Tag | Meaning |
|---|---|
| earnings | Launched on its earnings report (that day or the evening before) |
| news | The pre-market grading gave it an A or B that morning |
| faded | Power day that closed in the lower half of its range but held half its gap |
| cleared 1/3/6-mo base | The biggest base the launch day closed over (by the candle bodies) |
| neglected | 40+ days since its high, or a 25%+ correction |
| lone wolf | None of its groups has trended since the launch |
| tight x2 | 2+ tight days just under the buy point |
| retest held | Pulled back to the broken base top and closed back over it |
| gap out of base | Opened over last night's base high |
| from laggards | Launched under the 200 SMA, then 5 closes in a row over it: moved to Launches |
| Resistance column | Overhead 3/6/9-month and 52-week highs past the buy point, nearest first, with % away |

## Live & alerts

| What | When | Rule |
|---|---|---|
| Launching today | Every 5 min, 9:30 AM-4:00 PM ET | Watch list stocks meeting the launch rules on live prices (volume = pace for the time of day) |
| Laggards launching today | Every 5 min, 9:30 AM-4:00 PM ET | Under the 200 SMA, earnings/A-B news today, opened up, +5%+, 2x+ volume pace, over its 1-month high |
| 1-minute checks | 9:31 AM-12:00 PM and 3:00-4:00 PM ET | Big gap-ups (catalyst gap, power day, A+/A launch) and the followed launches' breakouts |
| Breakout alert | Every check | A followed launch trading over its buy point on 1x+ volume pace, after closing under it the day before |
| Touched & back under | Every check | Traded over the buy point (today's high) but is back under it: a heads-up, not a breakout |
| Table update | After the close (scan about 4:40 PM ET) | Launches that held at the close are added, dated that day |
