# Scanner rules

As of Nov 4, 2026. Source of truth: `scanner/launch.py`, `scanner/settings.json`, `radar/` and the morning grading instructions. Spreadsheet version: `rules/scanner_rules.xlsx`.

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
| 7. Laggard | Opened up | +5%+, closes in the top half | 2x+ | YES (since Nov 2, 2026) | Closes UNDER the 200 SMA but OVER the 50 EMA (Nov 4 2026: under both qualifies for nothing); MUST have earnings or an A/B news grade that day; moves to Launches after 5 closes in a row over the 200 SMA | Launch laggards tab; then 'from laggards' on Launches |
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
| Base length column | The current base: sessions since its top was set (day 1 = the high, like Base day); the tooltip gives how long nothing traded above that level |
| Off 52W high column | How far the price is under its 52-week high now (live in the session), not on the launch day |
| Correction column | The deepest drop after the 52-week high, to now (from the high to the lowest low since) |

## Live lists

| What | When | Rule |
|---|---|---|
| Launching today | Every 5 min, 9:30 AM-4:00 PM ET | Watch list stocks meeting the launch rules on live prices (volume = pace for the time of day) |
| Laggards launching today | Every 5 min, 9:30 AM-4:00 PM ET | Under the 200 SMA, earnings/A-B news today, opened up, +5%+, 2x+ volume pace, over its 1-month high |
| 1-minute checks | 9:31 AM-12:00 PM and 3:00-4:00 PM ET | Big gap-ups (catalyst gap, power day, A+/A launch) and the followed launches' breakouts |
| Breakout alert | Every check | A followed launch trading over its buy point on 1x+ volume pace, after closing under it the day before |
| Touched & back under | Every check | Traded over the buy point (today's high) but is back under it: a heads-up, not a breakout |
| Table update | After the close (scan about 4:25 PM ET) | Launches that held at the close are added, dated that day |

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
| Universe | Every US stock with a market cap of $700M+ (Nasdaq's list; when Nasdaq refuses it, the portal's own stock file of the last close, Nov 11 2026; 2 years of daily bars) |
| Liquid | Price $10+, 20-day avg $ volume $20M+, 700K+ shares a day (20-day avg), ADR 3.5%+ |
| History | 200+ sessions (60+ for a new listing) |
| 200 SMA range | From 60% under to 50% over its 200 SMA (28-50% over: power days only; under it: laggards or once it trades back over) |
| Not launched | No launch in the last 20 sessions (those are followed on the Launches list) |
| Rebuilt | Every evening at the 4:25 PM scan (a 4:30 AM safety run scans the last close if no evening run did) |
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
| Which gappers | Gap of 5%+ (up or down) at the latest pre-market price, then YOUR RULES from the boxes on the Graded gappers list (saved to premarket/rules.json; Claude's 8:45 grading and the code grader both read them, from their next run; the user, Nov 7 2026). Defaults: market cap $700M+, 20-day avg volume 700K+, 20-day avg $ volume $20M+, ADR 3%+; the pre-market price 30%+ over the 52-week low (the user, Nov 4 2026: under it qualifies for nothing, like every other list); a gap-up also over its 50 EMA (a tick box). Allowed: market cap $0.1-50B, avg volume 50K-10M, $ volume $1-1,000M, ADR 0-20%, 52-week low 0-200%; a value outside them is refused on the page, and the script uses the default instead |
| Code grade (next to Claude's for 1-2 weeks) | radar/codegrade.py, about 8:52 / 9:05 / 9:18 AM ET, no Claude, every gapper on the list. STAGE at the last close (rising = vs 5 sessions ago): 2 uptrend = 21 EMA > 50 EMA > 200 SMA, the 21 and 50 rising; 3 pullback = over the 200, the 50 over it, not 2; 1 basing = over the 200 with the 50 under it, or under the 200 without 4; 4 downtrend = under the 200, the 21 under the 50, both falling. ELIGIBLE gap-ups at the pre-market price: 30%+ over the 52-week low, ADR 3.5%+, over the 50 EMA, over the highest close of the last 21 sessions, a laggard at most 20% under the 200; no cap over the 200 (leaders run 200-300% over it). NEWS from the SEC filings since the last close: F offering / ATM / delisting / reverse split / going concern; A earnings beat + raise + growth 20%+ or 3+ pts faster, signed takeover, FDA approval, contract 25%+ of the market cap; B modest beat-and-raise, turnaround, positive trial, contract 5-25%; C the rest. GRADE: stage 2 / 3 A / B news = A / B; stage 1 / 4 now over the 200 = '⤴ reversal' A+ (A news) / A (B news); still under the 200 = W laggard watch (A / B news or earnings); else '—'. A 5-8% gap one grade lower; 15x+ ATR over the 50 SMA at most C, 10x+ flagged 'extended'; A+ only in a leading or turning-up group. Backtest Apr 2025 - Nov 2026 (4,727 gaps): A+ 14, r20 +16%, trade +18%; W crossed the 200 within 60 sessions 77%, +6.5% the 20 sessions after. Claude's grade stays the one alerts and Launch laggards use during the test (the user, Nov 4 2026) |
| News for every 5%+ gapper (code, live Nov 6 2026) | Every stock gapping 5%+ up or down gets its news, whether or not it passes the list's rules above (the user, Nov 6 2026: 'any gappers above 5%, their news'; FLY was 18% over its 52-week low and under its 50 EMA): the code grader's same SEC / Earnings-tab lookup, no grade, with the rule that kept it off the list. Sector move: <theme> = no news of its own today (none, only routine filings like a Form 4 / 144 / 10-Q, earnings from before the last close, a board change: news C) while 3+ stocks of its theme gap 5%+ the same way (its industry only when it has nothing at all), the biggest names and those with their own news named, then its own item. A report from before the last close (VCEL Nov 5, before the open, +13.9% that day) is not today's news: 'After earnings (Nov 5)', news C. Headlines: when the SEC has nothing of its own, the stock's own headline from Alpaca's news API (Benzinga, press releases included; not a movers list or a notice) is the catalyst if it's an event (sale talk, FDA / trial, offering, deal, buyback, earnings, analyst up / downgrade): '<kind> (headline)', news C, flagged 'no SEC filing on it yet' (FLY Nov 6: 'Firefly Aerospace Inks $1.3B Agreement With AST SpaceMobile', 7:31 AM). FDA / trial only on drug and device words: a 'Phase 1' needs a trial / study / data word after it (VSAT Nov 9: 'Viasat Selected By NASA For Phase 1 Of Network Extension ...' reads Deal / contract, not FDA / trial) |
| Earlier news (the last 2 sessions; the user, Nov 9 2026) | A gapper with nothing of its own today (no news, only routine filings, a board change, an analyst note; not 'After earnings', which names the report already, and not a filing the code couldn't classify: AKAM Nov 9, an 8-K offering convertible notes) gets its fundamental news of the last 2 sessions, if any: on Mon Nov 9 the news from Wed Nov 4 4 PM to Fri Nov 6 4 PM (FLY: Fri Nov 6's $1.3B AST engine deal, Benzinga 7:31 AM; 'when gappers and no news, link to prior days' news'; '2 sessions is max'; 'it has to be brand new fundamental change as in FLY'). Fundamental = earnings, a takeover (signed or talks), an FDA / trial result, a deal or contract, an offering or other dilution warning: the SEC filing's read first, else the stock's own headline of those kinds (Alpaca / Benzinga). Not: an executive change, analyst notes, buybacks, buying a company, sector moves, articles written after the move. Shows as 'Earlier news (Thu Nov 5): Earnings + raise: <the read> (SEC Nov 5 4:57 PM ET); today: <today's read>'. The news grade and the code grade don't change. Nov 9's test: 9 of 61 gappers (STLN, SLDB, UMC, TECK ...) |
| How many graded | Top 8 gap-ups and top 4 gap-downs by pre-market $ volume; the rest show ungraded under Show all |
| Prices | Newest of Yahoo's 5-minute bars, Yahoo's live pre-market quote and Alpaca (about 15 min behind); pre-market volume from Alpaca, about 15 minutes behind |
| Searches per stock | 'Why is <company> stock moving today'; the company's own news / 8-K; for asset-driven companies (crypto treasuries, miners, holding companies, single-drug biotechs) the asset's news too |
| Reliable sources only | Facts only from primary sources (company release, SEC filing, exchange/regulator notice, earnings release or call) or major outlets (Reuters, Bloomberg, WSJ/Barron's/MarketWatch, FT, CNBC, AP). Social media, crypto/flash sites, aggregators, blogs and AI summaries = rumor: C at best, F if the move rests only on it |
| Safety lock on A / B (code, no Claude) | Before the grades are saved (radar/premarket_build.py finish): an A or B whose reason or flags say the facts weren't confirmed / verified -> C; an A or B without a primary source (SEC filing, the company's own site, or a newswire carrying its release) -> C; an earnings gapper whose Earnings tab read (SEC release numbers) points the other way (gap-up read Bearish / Somewhat bearish, gap-down read Bullish / Strong bullish) -> one grade lower. The reason starts '⚠ Lowered from A: why'; every earnings gapper's flags carry the Earnings tab read. DUOL Nov 4 2026: A -> C ('exact revenue and guidance figures were not confirmed') |
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
| Above prev-day high | off (tick it to keep only stocks whose pre-market price is over yesterday's regular-hours high) (the user, Nov 6 2026) |
| Updates | Every 5 minutes, 7:00-9:29 AM ET |
| Theme event line (the user, Nov 11 2026: 'the most important thing happened in semis and it hasn't done anything related to it') | At the top of the Pre-market tab when many stocks of one area gap together: 8+ tradable stocks of an area (market cap $700M+, 700K+ shares and $20M+ a day, ADR 3%+; no 50 EMA or 52-week-low rule, so beaten-down leaders count) and 30%+ of that area up or down 5%+ in the latest scan (radar/theme_event.py, every 5 minutes with the live scan). An area = a family of themes (AI & Semis, AI Infrastructure, Software ...; a stock with no theme counts in its sector). The line names the areas, the count, the themes with 3+ gappers, the 8 leaders by pre-market $ volume, and the market / sector news behind it (the 8:45 grading searches it once). Nov 11 2026: 93 stocks, AI & Semis 63 of 83, AI Infrastructure 30 of 62. The grades and the graded list are unchanged |
| Theme bounce list (the user, Nov 11 2026) | Under the event line on a gap-up event: every gapper of the event with the pre-market price vs its 21 and 50 EMA (the last close's) and where the last close stood. Order: '✔ over both' first (under its 21 or 50 EMA at the last close, over both now: the go sign once the day closes there; AMD Sep 4-8 2026, MRVL Mar 6 2026), then over the 21 EMA nearest to the 50, then under both nearest to the 21; stocks already over both only with 'All of the event'. A watch list before the open, not a buy list; no alert, no grade |
| Pre vs 21 / 50 EMA / 200 SMA columns (the user, Nov 11 2026) | The latest pre-market price vs the 21-day EMA, 50-day EMA and 200-day SMA of yesterday's close (was 'vs 50 EMA' and 'vs 200D'; the 21 EMA is new). Also on the Graded gappers table (50 and 200) and, from the column list / + Filter, on every table before the open. The columns named vs 21 EMA, vs 50 EMA, vs 200 SMA (was vs 200D) use the regular-hours price: before the open yesterday's close vs yesterday's averages; during the session the live price vs today's moving averages (the EMAs move with the price as the Trend column's do; the 200 SMA swaps the close that drops out of its 200 days for the live price, from the first nightly build that saves that close, c200). The same on Gainers (its columns and the Above 200 SMA / Above 50 EMA boxes) and the Watchlist's vs 21 EMA / vs 50 EMA. As a + Filter, '>= 0' keeps the stocks over the average. Alerts, Launches and the Trend label are unchanged |
| Group gaps and the Themes column (the user, Nov 11 2026) | Group gaps = themes with 3+ tight (0.7+) members passing; a stock in no theme counts for its industry group (fit 0.7+). A click on a chip keeps the table on that group's gappers; a second click (or 'show all') shows all again. The Themes column shows the industry group in grey when a stock has no theme, and its broad industry '· other' when it has no tight group either. Hand adds (radar/theme_adds.json): KLIC, ASX -> Semi Test & Packaging, SIMO -> Memory & Storage (each joins while it tracks the theme at 0.6+) |
| News column | Why it gaps, for every 5%+ gapper: Claude's catalyst and reason when its 8:45 grading covered the stock, else the code grader's (code): news-only runs at 8:05 and 8:35 AM ET, then the code runs at 8:45, 8:55, 9:00, 9:10 and 9:20; 'after 8:05' before the first; 2 lines, hover for all, 📰 = the source (the user, Nov 6 2026: '805, 835 and 905') |

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
| Gap (today's open vs yesterday's close) | off (fill in a % to use it: gap up for Gainers, gap down for Losers; a stock without an open yet is left out while it's set) (the user, Nov 4 2026) |
| ✕ on TREND | Takes a stock off the Watchlist's TREND list and its TREND triggers on every device (setups/picks.json removed_trend) until it comes on 1-EP/GAP, 1-UPDAY or 2-POOL again or launches again; no Launches rebuild for it (the user, Nov 7 2026). 3-SETUPS has its own ✕ (removed_setups) |
| Your own filters (+ Filter) | none by default: search any criterion (the table's columns first, then the column catalog) and add it with a value (≥ / ≤, is, has); kept in the browser; Reset to my defaults clears them (also on the Watchlist and Launches, the user, Nov 4 2026) |
| + Filter: the morning breakout levels (the user, Nov 9 2026) | On every tab's + Filter (Gainers, Pre-market, Watchlist, Launches, Earnings), each 'Over it' or 'Under it': Yesterday's high (PDH: stocks.json high_1d, regular hours), 5-min opening range high (ORH: today's 9:30-9:35 high from Yahoo's 5-minute chart, radar/levels.py, for the stocks up 2%+ at a 5-minute update from 9:36), 21-day closing high (the highest close of the last 21 sessions, stocks.json close_high_21, as the EP rule), and EMA stack (live): 10 over 21, 21 over 50, 50 over the 200 SMA, 10 > 21 > 50, 10 > 21 > 50 > 200 SMA (the EMAs at the live price, as the Trend column). A stock without the value is left out while the filter is set. Also as columns (Columns: + add). Separate from the morning alert's own settings (the user: 'two sets') |

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
| Ranked on tradable stocks (the user, Nov 10 2026: 'with adr high') | A theme or industry group with 4+ tradable stocks (the launch list's liquidity: $10+, 700K+ shares and $20M+ a day, ADR 3.5%+) is ranked on those stocks' median 1-, 3- and 6-month moves, and only such a group can be ★ Top / Strong. With fewer it is ranked on all its stocks and gets a rank number, no tier. Oct 23 2026: 28 of 99 themes and 53 of 217 industry groups have 4+; tiers 7 themes (was 10), 9 groups (was 20) |
| Heating up (the user, Nov 10 2026: 'I need that column for sure') | Heat 1-99 for every theme and industry group: its stocks' median 1-week move and its breadth (the share of them up on the week), each ranked among the groups of its kind, averaged and ranked again. 🔥 = heat 90+ with 60%+ of its stocks up. A column on the Themes and Industry groups tables (next to the 1/3/6-month rank) and, from the column list, 'Heating up' (the stock's best group) on every table. The stock's own short-term rank: 'RS 1W-1M' in the column list (its 1-week and 1-month moves against every stock, 1-99), next to RS (1/3/6 months) |
| One pack, one name (the user, Nov 10 2026: 'yes... correct') | Where a theme and an industry group share three-quarters or more of their stocks (shared / all stocks of both), the industry group shows the theme's name, rank, tier and heat: 15 pairs on Oct 23 2026 (Cybersecurity, Refiners, Drug Distributors / Medical Distribution, Cruise Lines / Travel Services, Consumer Lending / Credit Services, Hotel REITs, Memory & Storage, Quantum Computing, Electric Utilities, Packaging, Paints & Coatings, Alt Asset Managers, Retail / Discount Stores, Apparel Retail, Power Generation). Where they share less both stay (Neoclouds, Nuclear & Uranium, Solar, AI Chips & CPUs, Optics & CPO, Gold Miners: the theme is the story, the group the business line) |
| Homes for stocks with no pack (the user, Nov 10 2026: 'they have to tightly move up and down same theme') | Nov 11 2026: of 343 tradable stocks in no theme and no tight group, 25 moved with an existing pack at 0.6+ (120 sessions to Oct 23); the ones whose business also matches were added by hand: themes XNCR, KYMR, PTCT (Small & Mid-cap Biotech), BAX (Medtech), HGV (Hotels), OSPN (Cybersecurity), STEP (Alt Asset Managers), BRKR (Life Science Tools & CROs); industry groups PDFS (Semi Equipment: Front-End), KBR and AMTM (Government IT & Defense Services), STEP (Alternative Asset Managers). Each joins only while it still tracks the pack at 0.6+. Among the other ~320 no group of 3+ moves together at 0.6+: no new pack was made |
| Wide list: Aerospace & Defense (all) (test branch; the user, Nov 12 2026: aerospace & defense stocks 'popping up, not even in your theme / industry list') | 40 of the 60 aerospace & defense stocks have no theme and 45 no tight group, and they do not move together (KRMN 0.45, AVEX 0.41, BETA 0.32 against the 0.6 a pack needs; no pack among them). So the whole broad industry also shows as one loose row in the Industry groups list, 'Aerospace & Defense (all)', tagged 'wide list': a rank and a heat on its tradable stocks, placed among the industry groups without entering their ranking (no other group's rank, tier or a stock's stars change), no Top / Strong. Click it for all its stocks. Homes added the same day (0.6+ and the business matches): EGO (Gold), SIBN (Medical Devices), NESR (Oil & Gas Equipment & Services), BCAX (Small & Mid-cap Biotech) |
| Breadth | Not used: 98% of top-3% groups already had 60%+ of their stocks over the 50 EMA |
| When | After each close (the 4:25 PM scan, and each Launches rebuild); stays the same during the day |
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
| Power day | Volume pace 4x+, 8%+ gap, up 10%+, over its 1-month high, above the 200 SMA (at most 50% over it); it has to open over the highest close of the last 21 sessions (the user, Nov 5 2026: WRBY opened 25.93 under its 26.52: no power day) | 1-minute and 5-minute checks |
| Episodic pivot | Volume pace 3x+ (the user, Nov 5 2026 evening; was 4x), 6%+ gap, over its 1-month high and the 200 SMA, and it opened over the highest close of the last 21 sessions (the user, Nov 5 2026: 'the whole point is to gap up above it'); a power day is one and alerts as the power day; in the ⚡ box with the power days | 1-minute and 5-minute checks |
| Catalyst gap | A neglected stock (under its 50 EMA or 200 SMA at the last close) gaps 5%+ on earnings or news with pace 3x+ and trades above both | 1-minute and 5-minute checks |
| Catalyst 2nd trigger | After a catalyst gap that hadn't cleared its base high: the base high cleared | Same |
| A+/A launch | Off the watch list, graded like Launching today | Same |
| Laggard launch | Under the 200 SMA but over the 50 EMA, earnings or A/B news today, opened up, up 5%+, pace 2x+, over its 1-month high | Same |
| Gapping to buy point | A followed launch gaps 2%+ on 1.2x+ pace to within 2% under its buy point | Every check |
| Breakout (A/B/C) | A followed launch trades over its buy point on 1x+ pace after closing under it | 1-minute in the morning and last hour, else 5-minute |
| Touched & back under | Traded over the buy point since the last check but is back under it | Every check |
| Confirmation | In the 3 sessions after a base breakout, opens and trades above the base top on 2x+ pace | Every check |
| Pop / gap out of base | The pop out of the consolidation; an open over last night's base high | From the open |
| 3-SETUPS entries | Every buy point of a 3-SETUPS name (not also on Launches: it alerts from there), exactly as on Launches: breakout over the buy point, flag / pennant line, pop, push, retest zone and retest holding into the close, 21 EMA retest / undercut & reclaim, breakout undercut & reclaim, gap out of base (the user, Nov 3 2026: AMPL's retest of its breakout level 15.93-16.18 with the 21 EMA had no alert). Only over the 200 SMA. Desktop: in the Watchlist tab's own alert log | 1-minute in the morning and last hour, else 5-minute |
| One pullback, one heads-up | When a stock is at its 21 EMA (the 21 EMA retest setup) and in the retest zone of its breakout level at the same check, one message names both: "MANE retesting its breakout level $130.90-$136.72 and its 21 EMA $130.11" (the user, Nov 6 2026: MANE got two at 9:35); the trigger later is unchanged | Every check |
| Retest zone / hold | Pulls into the retest zone of its last breakout; from 3:45 PM, holding into the close | Every check |
| After the close | Tight closes under a buy point, a retest of a broken base top that held; 3-SETUPS Ready list to the phone | After the 4:25 PM scan |
| Alert boxes hold what holds (every device) | A trigger stays in its box (🚀 ⚡ 🎯 ↩️) only while it still meets its own rule, all of it, volume too: GitHub's job re-checks every trigger it sent today at each live update (find() on the latest prices, then the same 1-minute chart tests it ran before sending: the retest's low and 10 / 21 EMA, the EMA reclaims' upper half, the reversal's top half, the 1- / 5-min entry over its stop) and publishes which hold (alerts.json hold / lost / back); the page does the same for its own (TREND). It works like a ladder (the user, Nov 5 2026): a power day / EP (⚡) that stops meeting its rules steps down to Launching now while it still meets a launch's rules (EPAM Nov 5: volume pace 3.6x, under 4x), else to Heads-ups; a launch, a pattern breakout or a pullback entry that stops holding steps down to Heads-ups, marked ↓ (the log notes when and the price); each goes back up when it meets its rules again; a stock up in ⚡ shows only there; a heads-up in those boxes (touched the buy point, the 9:50 volume check, back over a level, the 21 EMA retest alone) shows in Heads-ups. The end-of-day report uses the same verdict at the close (the user, Nov 5 2026: "whatever doesn't hold, it has to be taken from that box"; no rule changes) | Each live update (about every 5 minutes) |
| Tables live (Watchlist and Launches) | From 5 AM ET a read from an earlier close is shown for today: its Triggered today as triggered on its date (Triggered Thu, Nov 5), "today" in its texts as that date, its events dated, a base's day count moved on by the sessions since (XERS day 1 on Thu = day 2 on Fri). During the day, until the evening read: each buy-point trigger today shows on the stock's row with its state at the latest check (about every 5 minutes): "🔔 10:27 AM breakout over $41.42 · holding" or "↓ … back under since 11:24 AM ($41.38)"; a 3-SETUPS row holding one moves to the triggered part (the user, Nov 6 2026: "if the state of a stock changed, the table should reflect it within 5 minutes; only our triggers, the buy points; the rest once a day") | About every 5 minutes |
| End of day (desktop, every device) | Only today's buy-point triggers filed on the Launches and Watchlist tabs (GitHub's record and the page's own; no heads-ups, group moves or pre-market grades; not Launch laggards), each checked at the close against the level its own alert named: a power day / catalyst gap / launch / reversal = the evening scan made it a launch day (an episodic pivot also over the 1-month high it named); a breakout, 3-SETUPS / TREND trigger, base high cleared or breakout confirmed = the close over its level (within 0.5% = with caution); gap out of base = over the base high, the 1- / 5-min entries over their opening range high; retest holding = over the level and the 21 EMA; push, breakout undercut & reclaim = over their level; 21 / 50 EMA undercut & reclaim = over that EMA; pop = over its 10 & 21 EMA. One line per stock still true ('GCT ✓ HELD: gap out of base', its failed triggers marked ✗ inside), one 'Didn't hold' line per tab, one pop-up (the user, Nov 6 2026: the Nov 5 list had TENB, NTSK and others with no buy point, from the heads-ups) | After the 4:25 PM scan |
| 21 EMA retest / undercut & reclaim | From 3:45 PM, holding back over the 21 EMA after today's low went under it and the open. The retest alone is a heads-up (the user, Nov 3 2026: not a strong sign by itself); holding over its breakout level too, today's low within 1 ADR over it, is a trigger: 'RETEST + BREAKOUT LEVEL' (2 confluences, RPD Nov 3 2026); the undercut & reclaim (2 closes under) is a trigger | Every check |
| 📈 Morning breakout (any stock; the user, Nov 9 2026) | Any stock trading over yesterday's high AND its 5-minute opening range high (9:30-9:35), up 5%+ on the day, Rel vol 1x+ for the time of day ('a trigger for my alerts: any stock that has broken the PDH and the opening range 5-min high, +5% for the day, at Rvol over 1'). Base criteria (your Gainers tab's, ADR 4%+): price $5+, market cap $0.7B+, 700K+ shares and $30M+ a day (20-day averages), ADR 4%+; plus 30%+ over the 52-week low, over the 200 SMA, over the 50 EMA, 10 EMA over the 21, 21 over the 50 (the EMAs at the live price, as the Trend column); 50 EMA over the 200 SMA off by default. Every number adjustable, an empty box = that filter off, each tick box on / off, an On switch: the Alerts tab's '📈 Morning breakouts: your settings', saved to alerts/morning.json on main (set them before 9:25; the job re-reads them every 2 minutes). + Filter there adds or deletes extra criteria (the user, Nov 9 2026: 'so I can add / delete filters as I have in other parts of the portal'), saved with the boxes: over the 21-day closing high (the highest CLOSE of the last 21 sessions, as the EP rule: 'highest close'), gap at the open %, 1W / 1M / 3M %, % under the 52-week high, % vs the 200 SMA, % vs the 50 EMA, Trend (the live label), Group rank (★ Top / Strong), RS, themes / industry / sector has a word; a stock without a value for one that is set is left out. Only for this alert: the other alerts, the phone and the other + Filter sets don't change. The message: the price, % up, Rel vol, the two levels, the stop under the day's low (risk in % and ADRs), ADR, vs the 200 SMA, the EMA stack, the theme, and the news: today's own (SEC, Earnings tab, its headline), else its fundamental news of the last 2 sessions (P1 'Earlier news'). One alert when one fires, one batch alert ('MORNING BREAKOUTS (4): ...') when several fire in the same check; each stock has its line in the log and the 📈 box. Portal only (no phone yet); not a group move; stays in its box all day. Nov 9 replay with the defaults: 24 stocks, 10 of them 9:36-9:40 (CDNA 9:36, SHAK / TEM / SDGR / M 9:37 ...) | Every minute 9:35-10:30 (your window) |
| Rules | Each stock and kind once a day; phone via ntfy, desktop pop-ups while the portal page is open | - |
| Triggers vs heads-ups | Triggers (the buys): power day, catalyst gap + 2nd trigger, launches, laggard, reversal, breakout, retest holding, breakout undercut & reclaim, 50 EMA undercut & reclaim, push, pop, gap out of base, confirmation, 3-SETUPS trigger, 21 EMA undercut & reclaim, 21 EMA retest + breakout level, morning breakout. The rest are heads-ups. Desktop: a trigger pop-up stays until closed, chimes, flashes the tab and is bold with a red dot in the log; a heads-up fades. The voice says the box, the stars and the ticker, with the volume for the time of day for launches, EPs, power days, pattern breakouts and morning breakouts ('light' under 1x; none for pullbacks / retests, heads-ups, group moves, pre-market); a pattern breakout also says the pattern, the price point and the base's days (the Base length column): 'Pattern breakout, M H K, Base top, 151.25, volume 4.1 times, base 5 days' (MHK Nov 9 2026; the user, Nov 6 and Nov 10 2026) | - |
| Group move | 2+ stocks of the same theme or tight industry group alerting the same day (any alert; the loose '· other' industries don't count; a theme and a group with the same stocks = one move, the better-ranked names it): each of their alerts adds 'CYBERSECURITY MOVE: also QLYS retest holding 15:46', and one 'GROUP MOVE: Cybersecurity (#18/99, 14 stocks): RPD, QLYS' alert a day per group, as a trigger (the user, Nov 3 2026: RPD and QLYS at 3:46 PM) | Each live run |
| A flood (many at once) | Today's 1-minute chart checks run first; then each run: every trigger gets its own alert (up to 15), heads-ups fill the rest of 8, the others grouped into one alert naming each (ticker, kind, price). Every alert's full text is saved: the portal's log shows each one, a click opens its chart (was: 'N more alerts' with tickers only, unchecked; RPD Nov 3 2026, 3:46 PM) | Each live run |

## Conviction stars

| Star | Rule | Tested (Aug 2025 - Oct 2026, your management) | Buy |
|---|---|---|---|
| ★★ Strong launch | From yesterday's close: its best group ★ Top or Strong (top 10%) and closed under its 21 EMA (Trend Negative): a launch out of a pullback | +0.55R a trade on 222 live launch alerts, 42% won, both halves positive (all launch alerts +0.16R) | When it launches (Launching today, the ★★ desktop alert): over the 5-minute opening range high, stop its low |
| ★ Launch, trend up | From yesterday's close: Trend Up | +0.33R a trade on 1,203 live launch alerts, both halves positive | Same as ★★ |
| ⚠ skip | From yesterday's close: no Trend label | -0.05R a trade on 822 live launch alerts | Don't take it |
| ★★★ High conviction | A pullback entry (retest held, push out of the 21 EMA, 21 EMA retest or undercut & reclaim, breakout undercut & reclaim) on a launch in a ★ Top / Strong group, RS 80+, Trend Up; the 'on a pullback' tag only once it ran 1.25+ ADRs over its launch / breakout level (GDDY Nov 2026: no advance, no retest) | +0.68R a trade on 169, 36% won, 40% ran 20%+, both halves positive; the only combination that beat the luck test | Near the close (3:45-4:00 PM), stop under the day's low |
| Not starred (tested) | RS 97+ before the open (6 launches in 2 years had it the day before); breakouts on the 5-minute entry (2nd half negative in every combination); buying Launching today at the close (+0.04R); earnings (only 3 months of dates) |  |  |
| Gapping up | The Pre-market list shows only starred names gapping up in the pre-market scan (after the watch list's close; all of them before 7:00 AM): a launch opens up (5,492 of the 5,493 tested launch alerts). Any gap up counts: ★★ +0.54R on 0-2% gaps, +0.85R on 2-5%, -0.51R on 5%+ (28 trades); ★ +0.44R / +0.10R / +0.36R |  |  |
| Where | Pre-market tab: '★ Launch watch' (the evening scan's watch list, starred, Copy tickers) and a Stars column on the graded gappers; Launches tab: Stars and Trend (yesterday) on Launching today, ★★★ tags on Launches; desktop alerts with the stars stay on screen until clicked, with a tone. Phone alerts unchanged |  |  |

## Earnings tab

| Item | Rule |
|---|---|
| Who shows (your rules) | This week's reports (Nasdaq's calendar) for the stocks that pass your Earnings rules, checked on the last close before the stock first comes on the week's list (once on, it stays for the week): defaults (Nov 3 2026, scanner/settings.json) market cap $700M+, 20-day average $30M+ traded and 600K+ shares a day, price $10+, ADR 3.5%+, 30%+ over the 52-week low |
| Your rules in boxes (the user, Nov 9 2026) | 'This part, can you make it a filter so I can adjust whatever I want on those criteria': the Earnings tab's boxes (Mkt cap, $ vol 20D, Avg vol 20D, Price, ADR, 52W low), Save -> earnings/rules.json on main (GitHub key, like the Graded gappers rules); radar/earnings.py reads them at each run (out of range = the default, an empty box = that rule off). Stricter rules show at once on the page (it hides the reports already on the list that fail them); looser rules bring in more reports from the next Earnings update (weekdays 7:10-8:55 AM about every 15 min, 4:50, 6:30, 8:30 PM; Sunday 6 PM). At most 700 reports a week: past that, the less liquid newcomers are left out and the tab says how many. The boxes preview how many of the reports on the list they keep before you save |
| Why a big name can be missing (Nov 9 2026) | Not in the portal's universe ($300M+ US common stocks: no closed-end funds) or one of your rules; most often the 30% over the 52-week low (CEG 9%, NRG 11%, CRWV 14%, SE 6%, NU 7% on Nov 6's close) |
| Also on the tab | RS, Trend and + Filter for both tables (unchanged) |
| When it updates | Weekdays 7:05, 7:35, 8:35, 8:50 and 9:05 AM ET started by the day job (the user's times, Nov 12 2026; GitHub's own schedule ran once a morning Nov 5-12), GitHub's own schedule about 7:10-8:55 AM ET as a backup, then 9:10 and 9:20 AM ET for reports whose filing came late (NBIS Nov 12 2026 filed at 9:22 AM); nothing between the open and the close (the user, Nov 12 2026: 'i need those by market open after that not interested'), 4:50 / 6:30 / 8:30 PM ET, Sunday 6 PM ET |
| Revenue when the usual source is late (the user, Nov 12 2026, AVEX) | The revenue comes from the SEC release, else Yahoo's revenue history; when neither has the new quarter yet, Yahoo's earnings chart (it gets the quarter sooner), only when its quarter before the newest equals last quarter's revenue already saved (so the newest is this report's quarter). AVEX Nov 11 PM (no SEC results filing): $189.7M vs the $180.3M estimate (+5.2%), q/q -6.0% vs June's $201.8M; no y/y (listed recently, no Sep 2025 quarter) |
| Guidance from the headline (the user, Nov 12 2026, AVEX) | A report whose SEC release has no guidance in it, or one out with no release read when the news feed's headlines gave none (NBIS Nov 12 2026: 'Affirms FY2026 Sales Guidance of $3.0-3.4B vs $3.372B Est' -> reaffirmed, -5.1% vs street), takes its guidance from the earnings headline (Benzinga, the pre-market news): Raises / Lowers / Cuts / Affirms / Reaffirms / Narrows / Sees ... Guidance, the new range vs the street ('vs $X Est') and vs a year ago; a 'from ... to ...' range is read by its numbers (a narrowed range with a lower midpoint = lowered). Marked 'from the headline'; scored like a release's guidance; replaced by the release's own reading when the filing comes. AVEX: 'Raises FY2026 Sales Guidance from $700-720M to $820-840M vs $743M Est' -> raised, +11.7% vs street |
| Out, no filing yet (the user, Nov 12 2026, NBIS) | A report that is out (its time has passed) with no SEC filing to read yet shows 'Out · not read yet' and the pre-market news headline (source and time) where it said 'reports Thu'; the numbers and the read come when the filing arrives (a foreign company files its 6-K hours after the release) |
| Read without the SEC filing (the user, Nov 12 2026: 'yes do that'; by code, no Claude) | For a report that is out with no SEC filing yet (today's or last evening's): 1. the release itself on a newswire the news feed links to (GlobeNewswire, Business Wire, PR Newswire...), read like the filing; 2. else the EPS, revenue and revenue guide exactly as the news feed's earnings headlines print them ('Q3 EPS $0.43 Beats $0.42 Estimate, Sales $447.1M Beat $427.2M Estimate'; 'Raises FY2026 Sales Guidance from ... to ... vs ... Est'). The read then ends '· from the newswire / news headlines, no SEC filing yet'; the SEC filing replaces it when it arrives |

## Trend column

| Trend | Rule (checked in this order, first match wins) |
|---|---|
| Base rule (the positive ones) | 10 EMA > 21 EMA > 50 EMA and the 50 EMA higher than the day before (the user, Nov 12 2026: "50 ema rising means today higher than yesterday not 5 days ago"; was 5 sessions ago since Nov 3). During the session: the 50 EMA at the live price vs the last close's |
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
