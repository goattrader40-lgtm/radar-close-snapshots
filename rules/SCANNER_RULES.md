# Scanner rules

As of Nov 3, 2026. Source of truth: `scanner/launch.py`, `scanner/settings.json`, `radar/` and the morning grading instructions. Spreadsheet version: `rules/scanner_rules.xlsx`.

## Launch must-pass

| Rule | Requirement | Notes |
|---|---|---|
| Liquid | Price $10+, 20-day avg $ volume $20M+, 700K+ shares a day (20-day avg), ADR 3.5%+ | Your settings (scanner/settings.json, 'launch') |
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
| A+ | Volume 3x+, a 6%+ gap and a base breakout, jumping from under the 200 SMA to over it ('go day'). Laggards top out at A (they close under the 200 SMA) |
| A | Volume 3x+ and a base breakout, with a 3%+ gap or a 10%+ day |
| B | Two of the four ingredients |
| C | The rest |

## Breakout grade

| Grade | Rule | History, Aug 2025 - Nov 2026 (ran 10%+ / 20%+ in 20 days) |
|---|---|---|
| A | Early breakout (1st or 2nd since the launch, within 50 sessions) in a Top or Strong group (group rank top 10%, G2), volume building the 5 days before (1.1x+ the 50 before) | 63% / 37% (379 crosses of the top); closed as a breakout 73% / 43% (157) |
| B | Early plus one of those two | 52% / 22% |
| C | The rest | 45% / 17% |
| Changed Nov 3 2026 | The group rank replaced 'theme Leading' (the user). Same test with the old Leading theme: A 59% / 31% (375), closed as a breakout 68% / 37% (136). Top only (top 3%) gave fewer A's (168) at 65% / 38% | - |

## Off the list

| Reason | Rule |
|---|---|
| 50 EMA | 3 closes in a row under the 50 EMA (after 2 it waits in the 50 EMA undercut list for the reclaim) |
| 200 SMA | Off while its last 2 closes are under the 200-day SMA; back the first close over it (the user, Nov 3 2026: only while under); not laggards (under it by design); the real 200 SMA (a new listing without one is not held back) |
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

## Live lists

| What | When | Rule |
|---|---|---|
| Launching today | Every 5 min, 9:30 AM-4:00 PM ET | Watch list stocks meeting the launch rules on live prices (volume = pace for the time of day) |
| Laggards launching today | Every 5 min, 9:30 AM-4:00 PM ET | Under the 200 SMA, earnings/A-B news today, opened up, +5%+, 2x+ volume pace, over its 1-month high |
| 1-minute checks | 9:31 AM-12:00 PM and 3:00-4:00 PM ET | Big gap-ups (catalyst gap, power day, A+/A launch) and the followed launches' breakouts |
| Breakout alert | Every check | A followed launch trading over its buy point on 1x+ volume pace, after closing under it the day before |
| Touched & back under | Every check | Traded over the buy point (today's high) but is back under it: a heads-up, not a breakout |
| Table update | After the close (scan about 4:40 PM ET) | Launches that held at the close are added, dated that day |

## Groups & themes

| Item | Rule |
|---|---|
| Group | Each of the stock's themes on the portal (or its industry when it has none), and one level up its area (AI & Semis, Software, Energy... or its sector) |
| Leading | 60%+ of the group's members close above their 50 EMA and its median 1-month change is +8% or more |
| Turning up | Half or more of the members close above their 21 EMA and its median 1-week change is positive |
| Not trending | Neither of the above |
| Theme then -> now | The group's status on the launch day and today; 'since' = the first day from the launch it was trending (Turning up or Leading) |
| Lone wolf | None of its groups has trended since the launch |
| Theme confirmed (2-year launch test) | Its theme turned up (Turning up or Leading) after the launch: A+ launches then ran 20%+ 65% of the time vs 52% for other A's |
| Breakout grade | Since Nov 3 2026 the group rank (Top or Strong, G2) counts toward an A/B breakout, not the Leading status above (L4) |
| Group rank | See G2: each theme ranked among themes and each industry among industries (Top 3%, Strong 3-10%); the Leading / Turning up status above still shows in 'Theme then -> now' |

## Live watch list

| Item | Rule |
|---|---|
| Universe | Every US stock with a market cap of $700M+ (Nasdaq's list; 2 years of daily bars) |
| Liquid | Price $10+, 20-day avg $ volume $20M+, 700K+ shares a day (20-day avg), ADR 3.5%+ |
| History | 200+ sessions (60+ for a new listing) |
| 200 SMA range | From 60% under to 50% over its 200 SMA (28-50% over: power days only; under it: laggards or once it trades back over) |
| Not launched | No launch in the last 20 sessions (those are followed on the Launches list) |
| Rebuilt | Every evening at the 4:40 PM scan |
| 5-minute checks | Live prices for all ~3,300 stocks (tables); the launch and laggard rules on the watch list |
| 1-minute checks | 9:31-12:00 and 3:00-4:00: the watch list plus Launches, Launch laggards and the 50 EMA undercut list |

## Watchlist lists

| List | Gets on | Leaves on | Sections |
|---|---|---|---|
| Every list needs | Price $10+, market cap $700M+, 20-day avg volume 700K+ shares and $20M+ a day (20-day), ADR 3.5%+, close above the 50 EMA, 30%+ above the 52-week low | - | - |
| 1-EP/GAP | Gap up of more than 5% at the open with relative volume 2.5x+ (no 200 SMA rule) | 2 closes in a row below the 50 EMA, or 15 trading days without reaching 3-SETUPS | The gap day (a new gap moves it to the newer section) |
| 1-UPDAY | Up 4%+ on the day with relative volume 1x+ (no 200 SMA rule) | 2 closes in a row below the 50 EMA, a close below the up day's low, or 15 trading days without reaching 3-SETUPS | The up day |
| 2-POOL | First close back above the 50 EMA after 2+ closes below it; or, refreshed every Friday, momentum leaders: +10% in 1 week, +25% in 1 month, +50% in 3 months, or +50% in 6 months (that one also above the 200 SMA and 50%+ over its 52-week low) | 2 closes in a row below the 50 EMA; at the Friday refresh, a close below the 200 SMA or no longer liquid | 50 EMA reclaim / Momentum |
| 3-SETUPS | A name from 1-EP/GAP, 1-UPDAY or 2-POOL that the Launches engine reads as a setup; ADR 4%+ and a close over the 200-day SMA to come on (no 200 SMA yet: not held back) | 2 closes in a row under the 50 EMA, 2 closes in a row under the 200-day SMA (Nov 3 2026), 62 sessions without a new high, ADR under 3.2%, or your X | Triggered today / Ready (trigger within 0.7 ADR over the close, in a base of 5+ days or tight 2+ days under it) / Setting up (flag forming, 21 EMA pullback set up, near a retest) |
| Other screens (settings) | Daily tightness: 40%+ over the 52-week low, within 30% of the 52-week high, volume 20%+ under its 30-day average, range at most 0.8x the 10-day average, 3 tight days in the last 5. Pullback to 21 EMA / 50 EMA: within 3% over that EMA, above the 200 SMA, 21 EMA over 50 EMA | - | - |

## Watchlist grade

| Grade | Rule |
|---|---|
| Trend first | 10 EMA above 21 EMA above 50 EMA, price above the 50 EMA and the 200-day SMA; otherwise no grade (-) |
| A+ | Last pullback from the 20-day high was 10-15% |
| A | A pullback of up to 20% (other than 10-15%) |
| B | A pullback of 20-30%, only for stocks with an ADR of 8%+ |
| Note | This grades the trend and the last pullback; the Launches tab grades the launch day itself, so the same stock can grade differently |

## Buy points (triggers)

| Trigger | What it is / requirements | Buy point | New leg? |
|---|---|---|---|
| Base top | Highest high of the last ~6 months, at least 5 sessions old, with a pullback of 1.25+ of the stock's own ADRs from it | The base top. Close more than 0.5% over it on 1x+ volume = base breakout. Within 0.5% = breakout with caution (follow-through within 3 sessions: opens over the day before's close and closes 0.5%+ over the top) | Yes |
| Bull flag (trendline) | Top at least a 1-month high after a run of 4+ ADRs; 5+ day base with 4+ pullback days, 1.25-4 ADRs deep, 3+ lower highs in a descending channel; volume at or under 1.1x the 20-day average; riding the 10 or 21 EMA (3+ days within 1 ADR); never closes more than 0.5 ADR under the 21 EMA; no violent drop | Tomorrow's value of the falling line along its highs; entry = close over the line and the 10 & 21 EMA | No (entry inside the base) |
| Bull pennant (trendline) | Same as the bull flag after the pole, but converging: lower highs and higher lows; volume after its first low at or under 1.1x average | The falling upper line | No (entry inside the base) |
| Pop out of the consolidation | Consolidation 1+ ADR under the top; volume dried up (5-day at or under 0.85x the 50-day); surfing the 10 & 21 EMA (closes within 1 ADR) above the 50 EMA; then a tight candle (range at or under 0.8 ADR, body at or under 0.5 ADR) | Next day opens above that candle's open and close and above the rising 10 & 21 EMA (the open is the trigger); once per base | No |
| 21 EMA retest | 5+ days into the base and 1.25+ ADRs off its high; controlled pullback (no advance the 3 days before, closes held over the 21 EMA) | Low goes under the 21 EMA and under the open, close comes back over it in the upper half of the day; once per pullback | No |
| Retest held | Once per breakout: after a real pullback, the low at the broken base top (bodies or wicks) | Close back over the top and the 21 EMA (holding over the 10 EMA, or the low tested the 21 EMA and reclaimed it) | No |
| Breakout undercut & reclaim | After a breakout, 2+ closes back under its level while holding over the 50 EMA | The close back over the level, within 5 sessions | No |
| 21 EMA undercut & reclaim | 2 closes under the 21 EMA by less than 0.5 ADR | The close back over the 21 EMA (strong signal) | No |
| Push out of the 21 EMA | After a retest, a push out of the 21 EMA with a gap (not while still under a flag's falling line) | The gap open | No |
| Double breakout | The base top and a falling line inside the base broken the same day | The base top | Yes |
| 3rd try (ascending triangle) | 1st try = the base high, a 2nd try within 0.25 ADR of it after a real pullback, then a shallower pullback (higher lows) | The base high on the 3rd try | Yes |
| Gap out of base | Opens over last night's base high (base top or a pattern pivot); needs ADR 4%+, 600K+ shares a day | Over the 1- or 5-minute opening range high, stop its low; out at 9:50 if the volume pace isn't 2x | - |
| MSF pattern pivot | Your MSF engine's pattern (High tight flag, Flat base, Cup with handle, ...) | The pattern's pivot | Yes |
| Which one is shown | The nearest trigger above the price | - | - |
| Exit signal | The first close below the 21 EMA | - | - |

## Legs & status

| Item | Rule |
|---|---|
| Leg 1 | The launch, when it closed out of its base or cleared at least its 1-month base (by the bodies); otherwise leg 0 (in base) until the first breakout |
| Later legs | A close out of a base (more than 0.5% over its top) or out of a flag at the highs; one leg per base; breakouts a few days apart are one leg |
| Late | Leg 4+ (breakouts got worse leg by leg in the 2-year test) |
| New run | A breakout after a rest of 40+ sessions without a new high starts again at leg 1 |
| Status: In the base | Under the top, no close above the level its leg broke out of, or 1.25+ ADRs off its latest high |
| Status: Consolidation (resting) | Surfing the 10 & 21 EMA on dry volume: closes within 1 ADR of both, above the 50 EMA, bodies 0.5 ADR or less, 5-day volume 0.85x or less of the 50-day |
| Status: others | Tight under the buy point, breakout, running, retest that held |
| tight x2 | 2+ tight days just under the buy point (within 1 ADR, bodies 0.5 ADR or less, sideways) |
| 50 EMA undercut list | 2 closes in a row under the 50 EMA: waits there for the reclaim next session; a 3rd close under takes it off |

## Pre-market grading

| Item | Rule |
|---|---|
| When | Starts 8:50 AM ET on weekdays; final price check at 8:57; posted by 9:05. If it starts late it still grades everything |
| Which gappers | Gap of 5%+ (up or down) at the latest pre-market price; market cap $700M+, 20-day avg volume 700K+, 20-day avg $ volume $20M+, ADR 3%+ |
| How many graded | Top 8 gap-ups and top 4 gap-downs by pre-market $ volume; the rest show ungraded under Show all |
| Prices | Newest of Yahoo's 5-minute bars, Yahoo's live pre-market quote and Alpaca (about 15 min behind); pre-market volume from Alpaca, about 15 minutes behind |
| Searches per stock | 'Why is <company> stock moving today'; the company's own news / 8-K; for asset-driven companies (crypto treasuries, miners, holding companies, single-drug biotechs) the asset's news too |
| Reliable sources only | Facts only from primary sources (company release, SEC filing, exchange/regulator notice, earnings release or call) or major outlets (Reuters, Bloomberg, WSJ/Barron's/MarketWatch, FT, CNBC, AP). Social media, crypto/flash sites, aggregators, blogs and AI summaries = rumor: C at best, F if the move rests only on it |
| No hindsight | Graded only from the news as it stood before the open, not from price action |
| Report | Phone notification with the save time, 'prices as of' time, counts and A/B tickers; PRICES STALE if prices are 15+ minutes old |
| Group rank | Each gapper shows its best group's rank after yesterday's close (G2), its place in that group and a '#1 in group' tag for a leader (group of 5+); beside the grade, not part of the news grade |

## Gap grades

| Direction | Grade | Meaning |
|---|---|---|
| Gap-up | A | Real fundamental change: beat with raised guidance or clear growth acceleration, FDA approval, signed takeover at a premium, signed transformational contract, confirmed inflection 7+ |
| Gap-up | B | Decent: meaningful contract or partnership, beat-and-raise with modest growth, early turnaround (inflection 4-6), index addition |
| Gap-up | C | Weak: analyst upgrade, sympathy, hype, talks/rumors with nothing signed, social-media posts or unconfirmed reports, no clear news |
| Gap-up | F | Warning: offering/ATM/convertible or other dilution, promotional release, reverse split, unconfirmed news, going-concern or delisting issues |
| Gap-down | A | Serious damage: guidance cut or withdrawn, big miss with weak outlook, lost major customer, failed trial, leadership ousted, accounting or fraud |
| Gap-down | B | Meaningful but contained: modest miss, cautious guide, offering or dilution, one-off charge, credible competitive threat |
| Gap-down | C | Weak or no real news: downgrade, sympathy, macro, strong report sold on valuation, unconfirmed reports (possible overreaction) |
| Both | Inflection 1-10 | Turnaround, Acceleration, New business, Margin, Deterioration or None (0); scored on size and how confirmed |

## Pre-market scanner

| Filter | Your default |
|---|---|
| Direction | Gap ups |
| Pre-market change | 0.5% to 5% |
| Price | $5+ |
| Market cap | $0.7B+ |
| Avg volume (20D) | 600K+ |
| Price x avg volume | $20M+ |
| ADR | 4%+ |
| 52-week low | 30%+ below price |
| Above 200-day SMA | off |
| Above 50-day EMA | off |
| Updates | Every 5 minutes, 7:00-9:29 AM ET |

## Gainers filter

| Filter | Your default |
|---|---|
| Direction | Gainers |
| Day's change | 4%+ |
| Price | $5+ |
| ADR | 3.5%+ |
| $ volume | $30M+ (20-day) |
| Above 200 SMA | on |
| Above 50 EMA | off |
| Market cap | $0.7B+ |
| Avg volume (20D) | 700K+ |

## Group rank

| Item | Rule |
|---|---|
| Groups | Every theme on the portal and every industry group, 3+ stocks with data; themes ranked only against themes, industry groups only against industry groups |
| Theme members added by hand | 62 stocks in no theme that moved with one at 0.6+ and match its business (radar/theme_adds.json, the user, Nov 3 2026), e.g. GNRC / SPXC / AAON / WCC in Data Center Power & Cooling, LWLG in Optics & CPO, ESI in Semi Test & Packaging; each joins only in weeks it still tracks the theme at 0.6+ (49 did on Nov 3; GEN and IPGP added from the tech review the same day), without the sector and liquidity filters of the automatic adds |
| Industry groups | By business line (radar/industry_groups.json: hand lists, finest in tech; else the Yahoo industry; US banks split Regional $3B+ / Community; from the tech review, Nov 3 2026: Network & App Delivery (FFIV AKAM FSLY NTCT ATEN RDWR) and Aerospace Components (GE HWM HEI WWD SARO VSEC HXL)). Each week the same co-movement test as the themes (120 sessions, market removed) drops the weakest member until every stock scores 0.6+ with the rest; a group needs 3+ tight stocks |
| Loose stocks | A stock that fits no tight group sits in '<industry> · other': ranked for information, never Top or Strong (when it is a stock's best group it counts at most as just under Strong) |
| Strength | Average pairwise co-movement of the members, the same scale for themes and industry groups (Groups & themes tab) |
| Group test (rolling, no look-ahead) | Groups re-pruned each month on past data only: launches in a Top or Strong group ran 20%+ 36.3% (193) vs 32.2% (376) with the Yahoo industries; 2nd year 32.5% vs 30.7%; Top launches avg 20-day +8.5% vs +4.9% |
| Score | Median 1-month, 3-month and 6-month return of the group's stocks; each ranked as a percentile among the groups of its kind; the three averaged and ranked again (Qullamaggie's 1/3/6-month lists) |
| Rank | #1 = best, shown as #2/99 (2nd of 99 themes); change vs 5 sessions earlier shown as up/down arrows |
| Top group (star) | Top 3% of its kind (about 3 themes and 3 industries) |
| Strong | Top 3-10% of its kind (about 7 themes and 5 industries) |
| The rest | Rank number only: below the top 10% no band did better than the bottom half in the 2-year test, so no Lagging or Emerging tag |
| Breadth | Not used: 98% of top-3% groups already had 60%+ of their stocks over the 50 EMA |
| When | After each close (the 4:40 PM scan, and each Launches rebuild); stays the same during the day |
| Stock's group rank | Its best-ranked group among its themes and its industry |
| Where it shows | Groups & themes tab (Rank, Tier); Group rank column on Pre-market graded gappers, Watchlist, Launches and Launch laggards |
| Place in its group | Under the rank: the group and the stock's place in it, e.g. '#2 of 14': its own 1-, 3- and 6-month returns, each ranked among the group's stocks, averaged |
| #1 in group tag | Pre-market graded gappers only: the stock is #1 in its best-ranked group and the group has 5+ stocks |
| Leader test: gap-ups | In a Top group the #1 ran 20%+ 61% (54) vs #2-3 51% (65) vs the rest 41-42%; but its average 20 days later was no better (+3.1% vs +3.6%) and it faded on the gap day more often (57% vs 49%) |
| Leader test: launches | No tag: the group's #1 launching ran 20%+ 20% (86) vs 29% for the rest of its group; in Top groups the bottom two-thirds did best (38%) |
| RS (market rank) | Each stock vs all the stocks the scanner follows: its own 1-, 3- and 6-month return, each a percentile, averaged and ranked again; RS 1-99 (99 = best), like IBD's RS rating. RS column on Launches / Launch laggards, green with a star at 97+ (top 3%); also on the Watchlist, plain |
| RS test: launches | RS 97+ on the launch day ran 20%+ in 20 days 34% (100) vs 25% for the rest; RS 97+ in a Top or Strong group 40% (52, avg +6.1%) |
| RS on the Watchlist | Shown as a plain number (no highlight) on all four lists: information only |
| RS test: buy points | No edge after the launch: base breakouts RS 97+ ran 20%+ 25% (377) vs RS 90-96 24%, 80-89 20%, 50-79 21%, with a lower avg result (+0.19R vs +0.99R for 90-96); A-grade breakouts with RS 97+ 29% / -0.2R vs A under 97 39% / +1.3R; all buy points RS 97+ 27% / +0.17R vs 21-23% / +0.15 to +0.75R. High-RS stocks are often extended by then |
| History test table | Launches tab: by the group rank on the launch day (Top / Strong / other) and by RS (97+ or under), and launch grade x group tier; replaced 'theme confirmed / lone wolf' (a theme trending within 10 sessions after the launch: hindsight) |
| In the grades | Part of the breakout alert grade (Top or Strong counts, L4); beside the news grade and the launch grade, not part of them |
| 2-year test: 5%+ gap-ups | Ran 20%+ within 20 days: Top 44% (739), Strong 37% (457), 10-20% 28%, 20-50% 29%, bottom half 29%. Gap-day fade about the same in every band (52-57%) |
| 2-year test: 10%+ gap-ups | Top 42% (142), Strong 42% (84), the rest 26-30% |
| 2-year test: launches | Top 35% (200, avg +4.4% in 20 days), Strong 31% (186, +1.5%), 10-20% 23%, 20-50% 22%, bottom half 21% |

## Alerts

| Alert | When it fires | Checked |
|---|---|---|
| 3-SETUPS triggers | Only while the price is over the 200-day SMA (the last close's); under it, no alert (the user, Nov 3 2026: ECHO's base top 100.90 under its 200 SMA 106.63) | Each live run |
| Every alert (phone and desktop) | Only when the price is at least 30% over the 52-week low at that moment (the user, Nov 3 2026); a stock without a 52-week low yet is not held back | Each live run (radar/alerts.py, the portal) |
| Pre-market grades | The morning's graded gappers | About 9:05 AM ET |
| Early heads-up | A 5%+ gap with a catalyst-gap / power-day / launch shape, before the volume can be read | 9:31-9:34, every minute |
| Power day | Volume pace 4x+, 8%+ gap, up 10%+, over its 1-month high, above the 200 SMA (at most 50% over it) | 1-minute and 5-minute checks |
| Catalyst gap | A neglected stock (under its 50 EMA or 200 SMA at the last close) gaps 5%+ on earnings or news with pace 3x+ and trades above both | 1-minute and 5-minute checks |
| Catalyst 2nd trigger | After a catalyst gap that hadn't cleared its base high: the base high cleared | Same |
| A+/A launch | Off the watch list, graded like Launching today | Same |
| Laggard launch | Under the 200 SMA, earnings or A/B news today, opened up, up 5%+, pace 2x+, over its 1-month high | Same |
| Gapping to buy point | A followed launch gaps 2%+ on 1.2x+ pace to within 2% under its buy point | Every check |
| Breakout (A/B/C) | A followed launch trades over its buy point on 1x+ pace after closing under it | 1-minute in the morning and last hour, else 5-minute |
| Touched & back under | Traded over the buy point since the last check but is back under it | Every check |
| Confirmation | In the 3 sessions after a base breakout, opens and trades above the base top on 2x+ pace | Every check |
| Pop / gap out of base | The pop out of the consolidation; an open over last night's base high | From the open |
| 3-SETUPS trigger | A 3-SETUPS name (any section, not also on Launches) trades over its buy point (which was at or over the last close); phone and desktop since Nov 3 2026 | 1-minute in the morning and last hour, else 5-minute |
| Retest zone / hold | Pulls into the retest zone of its last breakout; from 3:45 PM, holding into the close | Every check |
| After the close | Tight closes under a buy point, a retest of a broken base top that held; 3-SETUPS Ready list to the phone | After the 4:40 PM scan |
| 21 EMA retest / undercut & reclaim | From 3:45 PM, holding back over the 21 EMA after today's low went under it and the open. The retest alone is a heads-up (the user, Nov 3 2026: not a strong sign by itself); holding over its breakout level too, today's low within 1 ADR over it, is a trigger: 'RETEST + BREAKOUT LEVEL' (2 confluences, RPD Nov 3 2026); the undercut & reclaim (2 closes under) is a trigger | Every check |
| Rules | Each stock and kind once a day; phone via ntfy, desktop pop-ups while the portal page is open | - |
| Triggers vs heads-ups | Triggers (the buys): power day, catalyst gap + 2nd trigger, launches, laggard, reversal, breakout, retest holding, breakout undercut & reclaim, 50 EMA undercut & reclaim, push, pop, gap out of base, confirmation, 3-SETUPS trigger, 21 EMA undercut & reclaim, 21 EMA retest + breakout level. The rest are heads-ups. Desktop: a trigger pop-up stays until closed, chimes, flashes the tab and is bold with a red dot in the log; a heads-up fades | - |
| Group move | 2+ stocks of the same theme or tight industry group alerting the same day (any alert; the loose '· other' industries don't count; a theme and a group with the same stocks = one move, the better-ranked names it): each of their alerts adds 'CYBERSECURITY MOVE: also QLYS retest holding 15:46', and one 'GROUP MOVE: Cybersecurity (#18/99, 14 stocks): RPD, QLYS' alert a day per group, as a trigger (the user, Nov 3 2026: RPD and QLYS at 3:46 PM) | Each live run |
| A flood (many at once) | Today's 1-minute chart checks run first; then each run: every trigger gets its own alert (up to 15), heads-ups fill the rest of 8, the others grouped into one alert naming each (ticker, kind, price). Every alert's full text is saved: the portal's log shows each one, a click opens its chart (was: 'N more alerts' with tickers only, unchecked; RPD Nov 3 2026, 3:46 PM) | Each live run |

## Earnings tab

| Item | Rule |
|---|---|
| Who | Stocks on Nasdaq's earnings calendar Monday-Friday of this week (weekend: next week) passing on the last close: market cap $700M+, 20-day avg $ volume $30M+ and 600K+ shares, price $10+, ADR 3.5%+, 30%+ over the 52-week low (scanner/settings.json 'earnings'). Once on, it stays for the week |
| Two tables | Over / under the 200-day SMA on the pre-market price (before the open; live in the session). Not filtered on the 50 EMA: vs 50 EMA is a column (the user, Nov 3 2026) |
| Sources (no Claude) | Nasdaq calendar (date, before open / after close); Yahoo (report time, estimates saved before the report, EPS, quotes, daily bars); the SEC press release (8-K item 2.02, exhibit 99): revenue, adjusted EPS, guidance |
| EPS | Adjusted: Yahoo's actual, else the release's non-GAAP EPS, else Nasdaq's; vs the estimate (Nasdaq's estimate when Yahoo's is 3x+ off it). EPS growth vs the same quarter a year ago ('turned +' from a loss) |
| Revenue | The release's revenue figure before its outlook (checked within 0.6-1.7x of the estimate); else the release's 'revenue grew X%' x last year's quarter; else Yahoo's quarterly revenue. Growth vs the same quarter a year ago |
| Guidance | From the release's words: raised / lowered / reaffirmed / given / none; a revenue range or figure in the outlook (not a result or a company profile) -> its midpoint vs the analysts' estimate for that quarter or year, and vs the same period a year ago (Guide growth); 'low/mid/high-thirties' = 32/35/38% |
| Read points | Revenue beat +1 (2%+ +2) / miss -1 (-2); EPS beat +1 (10%+ +2) / miss -1 (-2); guidance raised +2, above the street +1 (+2 without a raise), below -2, lowered -3; revenue growth 25%+ +1 / shrinking -1; the move after the report +2%: +1, +5%: +2, -2%: -1, -5%: -2 |
| Read | 6+ Strong bullish, 3-5 Bullish, 0-2 Mixed, -1 to -3 Somewhat bearish, -4 or less Bearish |
| Columns at the end | vs 200D, vs 50 EMA (pre-market price vs the last close's SMA / EMA), vs 20D high (vs the highest high of the previous 20 sessions; 'cleared' = above it), over the 52-week low; Group rank and RS as on Launches |
| When | Weekdays about 7:10-8:55 AM ET (final by 9:00), 4:50 / 6:30 / 8:30 PM ET, Sunday 6 PM ET (earnings.yml -> radar-data earnings.json). No phone alerts |

## Trend column

| Trend | Rule (checked in this order, first match wins) |
|---|---|
| Base rule (the positive ones) | 10 EMA > 21 EMA > 50 EMA and the 50 EMA higher than 5 sessions ago (the user, Nov 3 2026) |
| 1 Negative | Price under the 21 EMA |
| 2 Reclaim | Price back over the 21 EMA after a close under it, with the base rule |
| 3 Turn up | The 5 EMA crosses over the 10 EMA that day, with the base rule |
| 4 Up | The base rule, price over the 21 and 50 EMA, the 10 and 21 EMA both higher than the session before |
| 5 Resting | The base rule, but the 10 or the 21 EMA not higher than the session before |
| - (none) | None of the above |
| TREND list (Watchlist) | Every name on 3-SETUPS, 2-POOL, 1-UPDAY, 1-EP/GAP and Launches whose Trend is Up, Turn up, Reclaim or Resting now (live); leaves when it turns Negative or loses its label (still on the list it came from); Section = where it came from (Launches first); sorted by the Trend, most days first (the user, Nov 3 2026) |
| Where / when | Watchlist, Earnings, Gainers, Launches (and laggards); at the close from the nightly build (stocks.json trend / trend_days / tr), live in the session (today's EMAs moved on with the live price); Nd = sessions in the state; sorts Up > Turn up > Reclaim > Resting > - > Negative |

## Open items

| Item | Status |
|---|---|
| Momentum cutoff | Coded but OFF (L['max_run_pct'] = 0): no buy points once the stock has run 300%+ from its momentum start (option A) or 300%+ and 140%+ over the 200 SMA (option B). Your decision |
| 'No reset yet' tag | Offered; may be replaced by the momentum cutoff |
| Retest needs the 10/21 EMA at the level | Offered, not decided |
| Bull flag trigger on the higher of the line and the day before's high | Offered, not decided |

## Agreed examples

| Ticker | From | To | Launch / pick | What you agreed |
|---|---|---|---|---|
| GMAB | 2026-08-07 | 2026-10-30 | launch | - |
| ANF | 2026-08-03 | 2026-10-30 | launch | - |
| ANF | 2026-08-26 | 2026-10-30 | launch | - |
| RPD | 2026-09-14 | 2026-10-30 | launch | the user, Nov 1 2026: Oct 8 the 3rd try of its 1-month base top 13.25 under the main base (Aug 27) and the bigger base (Aug 11) |
| SPOT | 2026-10-22 | 2026-10-30 | launch | - |
| ACN | 2026-10-01 | 2026-10-30 | launch | - |
| SMCI | 2023-05-03 | 2023-08-14 | launch | - |
| ATRC | 2026-07-24 | 2026-10-30 | launch | - |
| CAI | 2026-08-07 | 2026-10-30 | launch | the user, Nov 1 2026: Aug 19 bull flag, Aug 20 base breakout, Sep 10 retest + 21 EMA, Sep 14 bull flag, Sep 15 base breakout, Oct 9 21 EMA undercut & reclaim, Oct 21-26 tightening, Oct 27 base breakout |
| NTSK | 2026-09-14 | 2026-10-30 | launch | - |
| APPN | 2026-08-07 | 2026-10-30 | launch | - |
| VEEV | 2026-08-07 | 2026-10-30 | launch | - |
| ZS | 2026-09-14 | 2026-10-30 | launch | - |
| ARM | 2026-03-25 | 2026-05-29 | pick | - |
| TTAN | 2026-10-15 | 2026-10-30 | pick | - |
| LIFE | 2026-10-01 | 2026-10-30 | pick | the user agreed its Oct 8 undercut & reclaim, Oct 20 pop, Oct 21 breakout and Oct 30 flag (44.81) |
| AEHR | 2026-02-11 | 2026-04-10 | launch | the user agreed (Nov 1 2026): Mar 31 50 EMA undercut & reclaim, Apr 2 bull flag breakout (closed under the 50 EMA Mar 27 & 30), Apr 6 base breakout |
| APLD | 2026-04-14 | 2026-05-08 | launch | the user agreed (Nov 1 2026): May 4 the textbook bull flag breakout (pole Mar 31 - Apr 23, flag Apr 24 - May 1) |
