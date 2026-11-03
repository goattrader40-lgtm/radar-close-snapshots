# Martin Luk's method: what it means for your IBKR bot and the Radar

Study and proposal, Nov 3 2026 (session "Radar: Martin Luk study"). **Nothing here is built or live.** Under your
ground rules each step waits for your "test it", then a replay and (where it applies) the 2-year check, then "go live".
The numbers come from `plans/martin-luk/luk_risk_sim.py` (run it: `python3 plans/martin-luk/luk_risk_sim.py`).

## Delivered (Nov 3 2026)

- **Task 1, the bot:** `bot/lukbot` on this branch. Sizing, portfolio checks, the brake, trade management (trim,
  financed stop, daily-close trail with MOC orders, day-0 cut, earnings and event cuts), journal, Radar feed and an
  IBKR (`ib_async`) adapter. 29 tests pass; `bot/README.md` shows how to plug it in.
- **Task 2, the portal:** branch `test/luk`, display only. On Launches: Trend, AVWAP, Exit line and Stop · size
  columns, a pullback-zone tag and the market gauge strip. On 3-SETUPS: a Trend tag. Waiting for your "go live".
- **The article** is by James Muninn (@Muninn), "How To Trade Like Future Market Wizard Martin Luk". He logged 112
  streams (211 hours) and reconstructed ~100% of Luk's 2026 swing trades: 461 campaigns (604 trades).

  | | Muninn's dataset | Kinfo verified |
  |---|---|---|
  | Win rate | 19.3% (89 / 372) | 20.4% |
  | Average gain per trade | +0.95% | +0.90% |
  | Win / loss | 8.0:1 | ~7:1 |

  Other numbers from the article:
  - Risk: 0.5% a trade in 2025, **0.3% in 2026**, with a **1.28% median stop** set on the 1/5-minute AVWAP.
  - Average loss −1.30%.
  - Through August 2026 the account was +844.5%, then +150% in October.
  - Against Qullamaggie's 905 trades: 24.6% wins, a 2.40% median stop (the daily candle low), an average winner of
    +26.7%, holds of several weeks on the 10-day SMA.

---

## 0. The short answer

1. **Luk's risk per trade is set about right.** He risks 0.3–0.5% per trade, more on A+ setups when he has a cushion.
   On his published numbers that is about **1/16 of the size that grows the account fastest (full Kelly 7.9%)**. If his
   edge were 3–4x smaller, the fastest-growth size would be 2–3%, and 0.5% would still be a safe fraction of it. It is
   high enough to compound and low enough to survive 17–26 losses in a row, which are normal at a 20% win rate.
2. **His weak spots are not the per-trade risk.** They are (a) **choppy months**: in December 2025 he took 74 trades,
   won 9 and lost 26.6%; (b) **overnight gaps** on 25–35% positions at 200–350% gross exposure. His "total open risk
   under 2.5%" counts only the stops, not the gaps; and (c) **the fat tail**: 10 trades made 220R of his 300R. Without
   them the edge falls from +0.65R to +0.18R a trade.
3. **A bot can do better than him on (a) and (b)**: use the same 0.5% risk unit plus four limits.
   - **A mechanical brake**: a drawdown ladder, a losing-streak brake and monthly loss limits.
   - **A gap-risk cap per position.**
   - **A cap per group**, using the Radar's group rank.
   - **A financed stop**: after selling 15% at +4R, move the stop to −0.71R instead of breakeven. The worst case is still
     0R, and the core gets room for the shakeouts Luk says the market loves.

   In the simulation of a choppy year, the brake cuts the bad-case (95th-percentile) drawdown from 58% to 24% and the
   worst month from −20% to −9%. In a clean year it gives up some upside.
4. **The edge is in waiting for the pullback, not in the early trigger.** An independent 10-year backtest of his rules
   used real 1-minute prints and real spreads. **His own first-hour 1/5-minute entry earned about zero after costs**
   (−45% in 2026). The confirmed version earned **9.6%/yr of alpha (t 2.5)**: the stock touched the 9 EMA, reclaimed it
   and was in the upper part of its range at 3:54 PM, bought 3:55. **Your own tests say the same thing**:
   - Ready bought on the 5-minute opening-range high came out about breakeven.
   - Breakouts with a 5-minute stop lose.
   - Reclaims and pops beat base breakouts.
   - Luk dropped base breakouts himself: 2.3% of his longs, against 65.9% pullbacks.
5. **For the Radar**: seven additions, in this order.
   1. A **Trend** column: Leading / Mediocre / Lagging / Pillar.
   2. **AVWAP levels**.
   3. An **exit line** per launch: the 10 EMA for fast leaders, the 21 EMA for steady ones.
   4. A **position-size helper**.
   5. A **market breadth gauge**: green / yellow / red.
   6. A **"Pullback zone" read and a 10 EMA reclaim buy point**.
   7. A **Short watch**: former leaders' weak bounces and parabolic tops.

   Display-only items first; anything that adds a buy point goes through a study first (A–Z plan, section 4).

---

## 1. What Luk does (sources at the end; ⚑ = his own words, ◇ = the article you sent, ○ = third-party)

| | Rule | Source |
|---|---|---|
| Result | 2024 USIC +283.1%; **2025 USIC stock division +969.8%**, 1st (579 competitors in the 2025 event; +1,358% YTD in November, then December −26.6%) | official USIC releases, ◇ |
| Trades | 2024: 104 wins / 319 losses (24.6%), avg win +15%, avg loss −3%. 2025: 209 / 731 (22.2%). 2026 dataset: 461 trades, 305 full −1R, 211 stopped on day 1, longest streak 33 losses, 10 trades = +220R of +300R | ○ (his podcast numbers), ◇ |
| Risk / trade | "Portfolio risk per trade = 0.5%. Max position sizing = 35%… smaller portfolio risk if I am testing the water… more risk on A+ setups if I have cushion. Not hard rules." 0.3–0.5% in 2026 | ⚑ X post, ◇ |
| Stop | "Stop = 1.5–5%"; at most **half the ADR**; the low of the day (5-minute entry candle's low if the day's low is over 5% away); shorts: the high of the day / the breakdown candle | ⚑, ⚑ guest article Feb 2025 |
| Size | position = risk ÷ stop, so a tight stop gives a big position: 20–30% typical, 35% cap; 25–30% for small/micro caps (gap risk); faster-ADR names get wider stops and smaller size | ⚑, ◇ |
| Exposure | 4–8 core positions (up to 11–12), **200–350% gross** on IBKR portfolio margin (280% peak 2025, 315–350% Aug 2026); "without margin… maybe 300 or 400%" | ◇ |
| Drawdown habit | "should've opened less new positions and trimmed more partials… Thursday's equity curve low is my line of defence"; 2021: a −50% drawdown (small caps / SPACs, revenge trading) | ⚑ X post, ○ |
| Setups (long) | **65.9% pullbacks vs 2.3% base breakouts.** The stock proves strength first, then pulls back 3–7 days into the rising 9 EMA / 21 EMA / anchored VWAP | ◇ |
| Triggers | AVWAP / VWAP reclaim 29.6% · intraday wedge / micro-trendline break 19.2% · 1/5/15-minute ORB 17.1% · opening flush undercut & reclaim 10.4% | ◇ |
| AVWAP anchors | catalyst days, swing highs, swing lows; never buy a pullback basing under the AVWAP from the high | ◇, ○ |
| Exits | 2024: sold 30–50% at +2–3R, which cut his 20R+ runners. 2025–26: **trim 10–15% at +3–5R to "finance the stop"**, then trail the **85–90% core on the daily close**: under the 9 EMA (fast leaders) or the 21 EMA (steady trends). Wicks don't count. SMCI: sold the core early, missed +200% ("a 40R+ mistake") | ◇ |
| Holding | long winners 7.4 days (9.0 on the 9 EMA trail), short winners 6.9 days (2–3 on parabolic/washouts), **losers 0.54 days**; 45.8% of all trades stop out on day 1, often within 15–90 minutes | ◇ |
| Shorts | 42% of 2026 trades, **more than half of net R**, 23.5% win rate vs longs 16.9%. Setups: (1) **weak bounce** of a former leader into its declining 9/21 EMA and AVWAP after a breakdown under the 21 EMA on volume (2–4 light-volume days up); (2) **parabolic short**. Covers into panic when the indices are extended (SNDK Jul 2026: short ~1,560 at the declining 9/21 EMA, held through 1,300, covered 1,100) | ◇ |
| Long/short switch | no macro forecasts: (1) his own trade feedback: consecutive stop-outs → stop forcing longs; (2) **watchlist breadth**: 90 of ~100 momentum names look terrible → flip to shorts | ◇ |
| Scans | Potent (yesterday's strong movers: mcap > $100M, 1-week volatility > 3.5%, over the 21 EMA, $50M+ traded), Pre-market (gappers, $50M+), Leader (weekend: 30-day biggest movers, $300M+ a week, top ~2%); lists **leading / mediocre / lagging / pillar (mega caps)**; market health = the leading list expanding or contracting; prefers ADR 5%+; prep ~30 min (15–20 in corrections) | ○ (Substack comment attributed to him; videohighlight summary) |
| Index rule | no longs while the index is under its 9/21 EMAs | ○ |

**Caveats.**
- He is 1 of 579 contestants: a winner is the right tail by construction.
- Most of the edge is discretion: which stock, when to sit out. No rule captures that.
- The article's 2026 statistics are its author's dataset, not audited.
- The USIC accounts are $20K–$1M, and margin is allowed.

### 1.1 The X accounts in the article, checked (Nov 3 2026)

X can't be opened from this session, so this comes from web search of the posts. Their own posts are quoted;
"secondary" means someone else's summary.

**@martinlukkt (Luk himself).** What his posts say:
- Mar 2025: the 0.5% / 1.5–5% / 35% rules, "not hard rules".
- Jun 2025: "20% drawdown… I should've opened less new positions and trimmed more partials… Thursday's equity curve
  low is my line of defence".
- Mar 2025: "The best lesson I've learned over the past 3 months is determining the market conditions by my own
  trades. Everything else is just noise."
- Aug 2025: "Down 8.5% on Friday… Sizing too aggressively on shorts. I held massive short positions going into
  Jackson Hole. I only sold 15% of the original exposure into strength." He was strongly short-biased and missed
  strength in small caps and non-tech; if conditions aren't fully favourable, stand aside.
- Jan 30 2026: closed his GLD/SLV shorts early: "I can't keep my promise of holding into the 50 EMA".
- Mar 2026: "Shorted at the first bounce into the declining 9 EMA after the close below it… I'm a chronic overtrader".
- Jun 2026: "On bounce days after a distribution day, I was often tempted to go long… stopped out. Those losing trades
  guided me to… the pullback short setup… tricky and deadly".
- A fan site (martinluk.com) shows his chart: EMAs, ADR, **low-of-day distance**, $ volume; screeners Premarket /
  Leader / Potent.
- Comments attributed to him: partials of ~10% once up 3+ ADRs; trails on the 9 or 23 EMA.

What it changes here:
- (1) The brake caps **new positions while in a drawdown** (his own fix).
- (2) The bot carries out the exit he couldn't stick to (GLD/SLV).
- (3) The breadth gauge counts **distribution days** and flags the bounce day after one.
- (4) The Short watch gets a fast variant: the first close under the 9 EMA, then the first bounce into the falling 9
  EMA.
- (5) The size helper shows the **low-of-day distance** in % and ADRs, like his chart.
- (6) S3 also tests a trim at +3 ADRs.
- (7) A **scheduled-event rule** (his Jackson Hole lesson): the day before FOMC, CPI, payrolls or Jackson Hole, cut
  positions that aren't financed yet to half, and add nothing new on the event day before the release.
- (8) His own trades as the first regime signal: that is the streak brake and the 3-stops-a-day rule.

**@Qullamaggie (Kristjan Kullamägi).** From his own site:
- Risk 0.25–1% a trade, rarely more. Positions mostly 10–20%, and never more than 30% of the account overnight in one
  stock.
- Sell 1/3–1/2 after 3–5 days and move the stop to breakeven. Trail the rest on the 10- or 20-day MA: the first close
  below.
- Secondary: index filter = the 10-day over the 20-day MA; daily $ volume about 50× your account.

What Luk took: his "biggest mentor", about 80% of his style. Luk then changed three things: much smaller trims, a 35%
cap, and pullbacks instead of breakouts.

What it changes here:
- Your current management is close to Qullamaggie's, so S3 compares all three: his, yours, Luk's.
- The bot's size check gets the **$ volume ≥ 50× account** rule.
- The gauge shows both QQQ 10>20 SMA and 9>21 EMA.

**@markminervini.** From his own posts:
- **Progressive exposure**: "when your trading is going well you press… when not doing well you cut back".
- Pilot buys first, then "step on the gas" once they work.
- "never get bold when running cold"; "never let a good size gain turn into a loss"; "define your stop before you
  enter"; "never average down".
- Sell half of two laggards to finance a new full position.
- Gaps: "that's where correct position sizing and progressive exposure come into play".
- Secondary: risk 1.25–2.5%, stops ≤ 7–8%.

What Luk took: the Stage 2 template, volatility contraction, progressive exposure.

What it changes here:
- The brake gets a **ramp back**: after a red spell, 0.25× pilots, 0.5× after 2 winners, 1.0× once the month is green,
  instead of jumping straight back to full.
- **Rotation when buying power is full**: sell the weakest half-positions to fund an A setup. That was Luk's 315%
  ceiling in August.
- Your "30% over the 52-week low" rule is already from his template.

**@alphatrends (Brian Shannon).**
- AVWAP from earnings / gap days ("gap" appears 270 times in his book), swing highs and lows, and IPOs.
- The "VWAP handoff": re-anchor where price found support.
- The 5-day MA is his short-term sentiment line.

What Luk took: AVWAP on 1- and 5-minute charts from catalyst days, swing highs and lows (he uses the AlphaTrends
AVWAP).

What it changes here: step C uses the anchors Shannon uses: the gap day's first bar, the latest top, the pullback low
(the handoff), and the **IPO for new listings**. The 5-day line is used for parabolic shorts.

**@jaredtendler.**
- The inchworm: raise the back of your range (your C-game), not just the peak.
- An A/B/C-game map.
- Tilt types: mistake, hating to lose, injustice, revenge, entitlement.

What Luk took: maps his A/B/C game and stops tilt spirals.

What it changes here:
- The bot becomes the C-game floor: the brake, plus an **override lock**. No manual trades or size-ups while the brake
  is at 0.25× or off.
- Every manual override is logged with a C-game tag.

**@JLawStock (J Law).**
- Two-time USIC $1M+ division winner: 2024 +353.9%, +1,499% over 2 years.
- "Align strategies with market conditions". Hong Kong-based, so longer, multi-wave swings.
- Secondary, unconfirmed: aims for 5:1 reward/risk; no trades in the first 15 minutes.

What Luk took: J Law introduced Luk to momentum trading (Feb 2023 seminar) and to the USIC.

What it changes here:
- A pre-trade check: **room to the next resistance ≥ 3R**. The Radar's Resistance column already has the levels.
- S5 also tests **no entries before 9:45**, which fits the first-hour spread finding.

**Not found:**
- The article's 6th mentor (cut off in your screenshots).
- Any source other than the article that names J Law, Minervini or Tendler as his mentors. A search of his own
  material names only Qullamaggie and Shannon.

---

## 2. Task 1: How good is his risk strategy, and how should your bot manage trades

### 2.1 The math (one year of 461 trades matching his published totals, 4,000 simulated years each)

Fixed risk per trade, trades drawn at random (so a year can catch more or fewer of the big winners):

| Risk / trade | Median year | Bad year (5th pct) | Median max DD | Bad DD (95th pct) | P(DD > 25%) |
|---|---|---|---|---|---|
| 0.25% | +104% | +46% | 6.3% | 10.6% | 0% |
| 0.30% | +135% | +57% | 7.6% | 12.4% | 0% |
| **0.50%** | **+300%** | **+106%** | **12.3%** | **19.9%** | **0.7%** |
| 0.75% | +656% | +181% | 18.0% | 28.8% | 12% |
| 1.00% | +1,289% | +267% | 23.1% | 36.7% | 39% |
| 2.00% | +10,116% | +832% | 41.9% | 61.5% | 100% |

The same year **without the 10 best trades** (the edge without the fat tail, +0.18R a trade):

| Risk / trade | Median year | Bad year | Median max DD | Bad DD | P(DD > 25%) |
|---|---|---|---|---|---|
| 0.30% | +25% | −4% | 10.0% | 17.8% | 0.5% |
| **0.50%** | **+44%** | **−8%** | **16.2%** | **28.6%** | **10%** |
| 1.00% | +90% | −17% | 30.4% | 50.0% | 74% |

The same year with **winners 40% smaller** (slippage, exiting runners early): 0.5% risk → median +27%, bad year −17%,
bad DD 33%.

**What this says.**
- **0.3–0.5% is the right zone, and 0.5% is the top of it** for anyone whose edge is unproven at his level. At 1% the
  median looks great, but if the fat tail doesn't show up (no top-10 trades), 3 years in 4 have a 25%+ drawdown.
- **The worst losing streak is 17 in a typical year and 26 in a bad one, even with no regimes at all.** His 33 in a
  row is beyond that. Real losses cluster in choppy markets, which is what the brake in 2.4 is for.
- **Full Kelly (7.9%) is irrelevant in practice.** The growth-optimal size collapses to 2–3% as soon as the tail
  shrinks. Sizing for the edge you hope to have is how traders blow up. Luk's own 2021 −50% came from overtrading
  small caps, not from the per-trade risk.

**Regimes** (12 months a year; a "chop" month = his December: ~70 trades, 12% winners, winners capped at 3R):

| Policy at 0.5% base | Chop months | Median year | Bad year | Median max DD | Bad DD | Worst month (median / bad) |
|---|---|---|---|---|---|---|
| fixed 0.5% | 1 in 12 | +196% | +33% | 20.3% | 38.0% | −15.3% / −23.2% |
| **brake** | 1 in 12 | +132% | +20% | **11.5%** | **17.0%** | **−7.6% / −10.7%** |
| brake, loose | 1 in 12 | +158% | +24% | 13.7% | 19.8% | −9.5% / −12.4% |
| fixed 0.5% | 1 in 4 | +56% | −39% | 33.4% | 57.6% | −20.2% / −25.2% |
| **brake** | 1 in 4 | +44% | **−14%** | **15.5%** | **24.3%** | **−9.2% / −11.1%** |
| brake, loose | 1 in 4 | +53% | −17% | 18.4% | 27.0% | −11.1% / −12.7% |
| fixed 0.5%, 2% of stops gap to −2…−6R | 1 in 4 | +32% | −53% | 37.6% | 65.0% | −22.4% / −28.3% |
| brake, same gaps | 1 in 4 | +28% | −20% | 17.0% | 27.9% | −9.5% / −11.8% |

**What this says.**
- **The brake is insurance.** It costs 10–30% of the upside in a clean year and halves the drawdown in a choppy one.
  The "loose" brake sits in between. In the simulation, a month like his December (−26.6%) comes out around −9% to
  −11% with the brake.
- **Gaps are a real cost.** If just 2% of stops gap through to 2–6R, the median year drops from +56% to +32%. The
  independent backtest found the same: in its version of his morning entry, 1.9% of trades gapped through their stop,
  and those gaps alone lost more than the strategy's whole net loss.
- **The 2.5% "open risk" is the stop risk only.** 8 positions × 30% × a −5% market gap with beta 1.5 is about −18% of
  the account overnight, whatever the stops say. Portfolio margin lets you hold that; it doesn't make it safe.

### 2.2 The financed stop (his "trim to finance the stop", made exact)

Sell a fraction **f** at **+kR**, and you bank f·k R. The stop on the rest that makes the worst case exactly 0R is
**−f·k / (1 − f) R**:

| Trim | at +3R | at +4R | at +5R |
|---|---|---|---|
| 10% | stop −0.33R | −0.44R | −0.56R |
| **15%** | −0.53R | **−0.71R** | −0.88R |
| 20% | −0.75R | −1.00R (the original stop) | −1.25R |

Luk moves the rest to breakeven, which locks +0.6R but gives the core no room. The **financed stop (−0.71R after 15%
at +4R)** still can't lose. It leaves 0.71R of room under the entry for the shakeouts behind his move from breakouts
to pullbacks ("my losing trades took out my stop at LOD and rallied back"). The bot can then step the stop up to
breakeven after the 2nd daily close over +2R. Whether this beats breakeven is study S3 (section 4, J).

### 2.3 Why the bot's entry matters more than its exit (three independent sources agree)

| Evidence | Early intraday trigger | Confirmed reclaim |
|---|---|---|
| Independent backtest (CRSP + TAQ 1-minute + NBBO spreads, 2016–Aug 2026) | his own entry (first-hour flush, break of the 1/5-minute high): 166 trades/yr, 13% win, **+0.04% a trade after spreads, −2.2%/yr, −59% DD**; first-hour spreads 3–8× the closing spread | touched the 9 EMA, reclaimed, upper 60% of range at 3:54, bought 3:55: **Sharpe 0.83, DD −13%, 9.6%/yr alpha (t 2.5)**, 29% win, +14.3% / −2.9% |
| Your tests (Nov 1, test/pb1h) | **Ready on the next day's 5-minute ORH ≈ breakeven** whatever the exit or filter; breakouts with the 5-minute stop −0.1 to −0.3R; follow-through on the 5-minute entry −0.67R | bought at the close: pop +0.37R, bull pennant +0.29R, push +0.22R, 21 EMA undercut & reclaim +0.20R; base breakout −0.07R, bull flag −0.21R (none beyond luck yet) |
| Luk | breakouts stopped working for him after 2024 ("stopped out on the shakeouts"); 2.3% of his longs now | 65.9% pullbacks; "if the market loves shaking out, then I'm going to trade the shakeout" |

Two more findings from that backtest matter for the bot:
- **The 9 EMA trail added little over a fixed 10-day hold**: CAGR 12.1% both ways, Sharpe 0.83 vs 0.78.
- **The 9 EMA is a sharp peak**: the 5 or 13 EMA halved the edge.

So the order of importance for your bot is: **(1) which stock and which day (pullback timing), (2) the entry
confirmation, (3) size and the brake, (4) the exit.** Most traders work on these in reverse.

Your rule 7 (enter only on the 5-minute ORH, stop under the day's low) is the entry the evidence likes least. I'm not
proposing to change it without a test. Study S5 (L) puts it head to head with the flush & reclaim and the 3:50 PM
close-confirm on the same pullback days, with spreads.

### 2.4 The trade-management spec for your IBKR bot (same, similar, better)

**Risk unit.** `R$ = equity × 0.5% × m`. `m` is the brake multiplier below (start at 0.25% for the first 50 live trades).

**Position size** = the smallest of:
1. `R$ / (entry − stop)`, the risk size.
2. Liquidity tier cap: **35%** of equity for tier 1 ($100M+/day traded), **25%** tier 2 ($50–100M), **15%** tier 3
   ($20–50M, your floor).
3. **1% of the 20-day average $ volume** (capacity and slippage).
4. **Gap cap**: position × G ≤ 2% of equity. G = the stock's 95th-percentile overnight gap down over 250 sessions
   (2× ADR if unknown; 3× ADR into earnings).

**Stop rules.**
- Stop distance ≤ min(5%, **0.5 ADR**) and ≥ max(0.6%, 0.2 ADR). Too tight is noise, too wide is not his setup.
- With 0.5% risk and a 35% cap, any stop under 1.43% is capped and risks less than planned. That's fine.

**Portfolio checks before every entry.**
- **Heat**: open risk at the stops of positions not yet financed, plus the new one, ≤ 2.5% (5R).
- **Group cap**: ≤ 2 positions and ≤ 60% gross in one group (the Radar's best group per stock).
- **Gross cap**: your account type's limit (cash 100%, Reg-T 200% overnight), plus IBKR `whatIfOrder` showing
  `ExcessLiquidity` ≥ 10% of net liquidation after the trade.
- **Market gap budget**: Σ position% × G ≤ 8% of equity.
- **Earnings**: no new entry with earnings in the next 2 sessions, unless the setup *is* the earnings reaction.
- **Room**: the next overhead resistance (the Radar's 3/6/9-month and 52-week highs) at least 3R above the entry
  (J Law aims for 5:1).
- **Capacity**: the stock's 20-day $ volume at least 50× your account (Qullamaggie's rule of thumb).
- **Rotation** (Minervini): with buying power full and an A setup triggering, sell half of the 2 weakest positions
  (closest to their stops in R) instead of skipping the trade.
- **Scheduled events** (Luk, Jackson Hole Aug 2025, −8.5% in a day): the day before FOMC / CPI / payrolls / Jackson
  Hole, cut positions that aren't financed yet to half; no new entries on the event day before the release.

**The brake** (m = the smallest that applies):

| Condition | m |
|---|---|
| equity within 5% of its high | 1.0 |
| 5–10% under the high (loose: 8–15%) | 0.5 |
| 10%+ under the high (loose: 15%+) | 0.25 |
| 5 losses in a row (loose: 7) | ≤ 0.5 until a +2R winner |
| 3 stop-outs today | 0 for the rest of the day |
| month −8% (loose −10%) | 0.25 · month −12% (loose −15%): 0, paper only until month end |
| Radar breadth gauge YELLOW / RED | 0.5 / 0 for new longs |
| optional "cushion" (his A+ rule): month +5% and equity at its high | 1.5 on A-grade setups only |
| equity 5%+ under its high (his Jun 2025 fix: "opened less new positions") | at most 2 new positions a day |
| the first bounce day after an index distribution day (his Jun 2026 post) | 0.5 for new longs that day |
| **ramp back** (Minervini's pilot buys): after any step under 1.0 | 0.25 → 0.5 after 2 winners → 1.0 once the month is green or at a new high |
| **override lock** (Tendler): while m ≤ 0.25 | no manual trades and no manual size-ups; every override logged |

m climbs back by the ramp, not in one jump. This is the mechanical version of "less when my P&L says so", Minervini's
progressive exposure and Tendler's A/B/C-game. **The bot cannot tilt; Luk did in December.**
(The simulation in 2.1 covers only the drawdown, streak and monthly steps. The ramp, the new-positions cap and the
distribution-day rule are added from the accounts in 1.1 and are not simulated yet.)

**Order flow (state machine per position).**

```
PLAN      from the Radar's signals.json or your pick: setup, trigger, stop rule, exit line (10 / 21 EMA), group, earnings
CHECK     size, heat, group, gap, gross / whatIfOrder, brake m > 0, regime     -> skip with the reason logged
ENTER     (a) trigger break: STP LMT at the trigger, limit +0.1 ADR (no chasing)
          (b) flush & reclaim: armed when price trades 0.15+ ADR under the level in the first 60 min; buy stop over the
              reclaim bar's high; stop = the flush low
          (c) close-confirm: 3:50-3:55 PM, touched and reclaimed the level, upper 60% of the day's range: marketable LMT
          child STP order sent with the parent (bracket), explicit trigger method, outsideRth = False
DAY 0     15:50: under the entry and under the reclaimed level -> out at the close (his losers last 0.54 days; study S3)
TRIM      price >= entry + 4R (3R for slow names): sell 15% (LMT); the stop on the rest -> entry - 0.71R (financed)
          after the trim fills: modify the stop's quantity and price in one call (an OCA group with a reduce type
          also works: check on the paper account that it shrinks the stop the way you expect)
          after the 2nd daily close over +2R: stop -> breakeven
TRAIL     the core exits on a daily CLOSE under its exit line (10 EMA fast / 21 EMA steady); wicks don't count
          15:47: today's EMA recomputed with the live price; under it by 0.1+ ADR -> MOC (NYSE cutoff 15:50, Nasdaq 15:55;
          NYSE won't let you cancel after 15:50); within +/-0.1 ADR -> hold; if the official close is under it -> sell at
          the next morning's 5-minute range low break or by 10:00
EXTENDED  close 4+ ADR over the 10 EMA (parabolic): sell another 15-25% into strength the next morning (optional; S3)
EARNINGS  before the report: not financed -> cut to <= 50% or exit; financed -> hold the core on its stop
JOURNAL   R, MAE / MFE in R, days, setup, trigger, regime, brake m, slippage vs plan (entry and stop), gap events
```

"Fast" vs "steady" is decided when the trim fills. Fast = over the last 10 sessions the average close is 1+ ADR over
the 21 EMA, with at most 1 close under the 10 EMA. Steady = everything else. The rule is tested in S3.

**IBKR notes** (check them against your setup):
- The `ib_async` library (the maintained successor of `ib_insync`) handles brackets (parent `transmit=False`, child
  `parentId`), OCA groups, `whatIfOrder`, account tags (`NetLiquidation`, `GrossPositionValue`, `ExcessLiquidity`,
  `Cushion`) and MOC orders.
- **Every stop lives at IBKR, never only in the bot.** Reconcile positions against the bot's state on every
  (re)connect. Add a kill switch: max orders a minute, max positions, a daily P&L stop.
- **Portfolio margin** needs $110K net liquidation to enable ($100K to keep) and options approval. **Reg-T** is 2×
  overnight.
- The **$25K pattern-day-trader rule**: the SEC approved FINRA's Rule 4210 change on Apr 14 2026 (effective Jun 4 2026;
  brokers phase it in up to Oct 2027). It is replaced by intraday margin. Check what IBKR applies to your account now.
- **Shorts** (if ever): check shortable shares (generic tick 236) and the borrow fee, respect Reg SHO Rule 201 (the
  short-sale restriction after a −10% day), and never add to a short on a bounce against it.

### 2.5 Same, similar or better: summary

| | Luk | Your bot, proposed |
|---|---|---|
| Risk unit | 0.3–0.5%, discretionary up/down | 0.5% × m; m mechanical (brake + regime); 0.25% for the first 50 live trades |
| Position cap | 35% (25–30% small caps) | 35 / 25 / 15% by liquidity tier, plus a capacity cap and a **gap cap** |
| Open risk | < 2.5% at the stops | same, plus a **market gap budget** and a **group cap** |
| Trim | 10–15% at +3–5R → breakeven | 15% at +4R → **financed stop −0.71R**, breakeven after the 2nd close over +2R |
| Core exit | daily close under the 9 / 21 EMA | the same rule, executed with MOC at 15:47–15:50 or the next morning |
| Bad months | −26.6% Dec 2025 | brake: about −9% in the same month (simulation) |
| Entries | discretionary 1/5/15-minute | the entry type chosen by study S5 (flush & reclaim / close-confirm / ORH), each measured live |

---

## 3. Task 2: What his method changes on the Radar

### 3.1 What the Radar already does like Luk (no change needed)

- **Group rank** (Qullamaggie-style 1/3/6-month) and **RS 97+** ≈ his weekend Leader scan (top ~2%).
- Liquidity ($20M+, 700K+ shares), ADR 3.5–4%+ and the 52-week-low rule ≈ his Potent and Pre-market scan floors.
- **Pullback entries**: 21 EMA retest, 21 EMA undercut & reclaim, 50 EMA undercut & reclaim, breakout undercut &
  reclaim, retest held, push, pop. That is his "trade the shakeout".
- **3:45 PM "holding into the close"** alerts (retest, 50 EMA reclaim, breakout reclaim) are the close-confirm entry the
  independent backtest found the edge in.
- **Launches as a tracking list**, not a buy list (your rule 7). He doesn't buy launch days either; he waits for proof
  and a pullback.

### 3.2 What's missing (G1–G10)

| # | Luk does | The Radar today | Proposal |
|---|---|---|---|
| G1 | 9 EMA pullback in a leading stack: the fast leader's entry | 10 EMA used only for flags / surfing / push; no 10 EMA reclaim buy point | a **10 EMA touch & reclaim** close-confirm buy point (the 10 is the 9 in practice; your examples use the 10; S1 tests both) |
| G2 | AVWAP from the catalyst day, the swing high, the swing low; never buys under the AVWAP from the high | none | **AVWAP levels** (launch day, last breakout, latest top, momentum-start low, earnings day) + a confluence tag |
| G3 | proves strength, then a 3–7 day pullback into the rising 9/21 EMA + AVWAP (IONQ: May 11 breakout over 49.44, 7 days down, May 20 bought 49.35 at the 21 EMA & AVWAP, 2% stop, rode the 9 EMA to 73.65) | 21 EMA retest needs 5+ days in the base and 1.25+ ADRs off the high; no named "pullback zone" | a **"Pullback zone, day N"** read with the levels and "buy the reclaim" |
| G4 | 4 intraday triggers; only 17% are ORBs | 5-minute ORH (you); gap-out-of-base 1/5-minute | test **flush & reclaim** and **AVWAP/VWAP reclaim** vs the 5-minute ORH on minute bars (S5); for the bot |
| G5 | watchlist breadth (leading / lagging lists expanding or contracting); own stop-outs; index 9/21 | group status and rank; no market gauge | a **breadth gauge** green / yellow / red, also read by the bot |
| G6 | shorts: 42% of trades, half his R | long only | a **Short watch** (display first): former leaders' weak bounces, parabolic tops |
| G7 | trail on the 9 EMA (fast) or the 21 EMA (steady) | "the first close under the 21 EMA = exit signal" | an **Exit line** column: 10 EMA (fast) / 21 EMA (steady) + a 3:45 PM heads-up |
| G8 | size from the stop: tight stop → 20–35% position | none | a **Size** helper column: stop %, size at 0.5% risk, liquidity tier |
| G9 | Leader scan: top ~2% by 1-month move, $300M+ a week; lists leading / mediocre / lagging / pillar | RS (plain) on the Watchlist; MOMENTUM-1W/1M/3M/6M weekly in 2-POOL | a **Trend** column (Leading / Mediocre / Lagging / Pillar) everywhere; a "Leaders RS 98+" view; liquidity **tier** shown (never a filter: "show, don't eliminate") |
| G10 | hardly ever buys the breakout itself (2.3%) | Launches follow breakouts and pullbacks | no design change (rule 3); the **first pullback after a launch / leg** is named as its own buy point once G3 passes |

### 3.3 Today, through his eyes (the Nov 2 close, from setups/launch.json)

- **Launches (115)**: 43 Leading (close > 10 > 21 > 50 EMA), 22 Mediocre, **50 Lagging** (close under both the 10 and
  21 EMA). More lagging than leading: his breadth read would be "don't force longs, cut size".
- **The watch universe (562 liquid names)**: 34% close over the 21 EMA, 31% over the 50 EMA, **14%** with close > 21 >
  50. Narrow.
- **In a rough pullback zone today** (1–4 ADRs off the high, the close within 1 ADR over the 10 or 21 EMA, 21 > 50):
  17 Launches. For example:
  - MNDY and WDAY: Top group, "surfing the 10 & 21 EMA on dry volume".
  - CART, ARQT, KNSA: RS 96, in the base.
  - MAZE: "retest held + confluence".

  These are the names a Pullback-zone read (G3) would put on top. They're an illustration, not signals: the rule isn't
  tested.

---

## 4. A to Z: the implementation plan

Each step lists what it touches. **Display-only** steps (B–G) add no buy point, so they need the test branch and
`tools/replay.py --regress` but no 2-year check (your rule 2). **Studies** (H–N) run only on test branches, and the
2-year runs are the "ask first" kind: the reason is given with each. Every rule change updates `rules/make_rules.py`
and `HANDOFF.md` in the same commit (rule 6b).

### Phase 0: your decisions
**A.** Answer the questions in section 5. Nothing starts before that.

### Phase 1: display only (test branch `test/luk-display`; no 2-year check)
**B. Trend column (G9).** `scanner/launch.py`: `stack(a, i)`:
- Leading = close > 10 > 21 > 50 EMA with the 10 and 21 rising.
- Lagging = close < 10 < 21 with both falling.
- Pillar = market cap $200B+.
- Mediocre = the rest.

Field `stack` on launches, laggards, the 50 EMA undercut tab and setups3 rows; `scanner/run.py` for the other three
lists. Portal: a column + filter on Watchlist, Launches, Launch laggards and the Pre-market graded gappers.

**C. AVWAP levels (G2).** `avwap(a, k0, i)` = Σ typical price × volume ÷ Σ volume from day k0. This is a daily
approximation; the bot computes it exactly from minute bars. Anchors:
- the launch day i0;
- the last breakout day;
- the latest top ("from the high");
- the momentum-start low (`momentum_start()`);
- the last earnings day (`earnings_of()`), from the gap day's first bar (Shannon);
- the pullback low once it holds (Shannon's "handoff": the core's line of defence);
- the IPO, for listings under 200 sessions (the engine already treats them separately).

Fields `avwap_launch`, `avwap_bo`, `avwap_high`, `avwap_low`, `avwap_earn`. Portal: an AVWAP column (the nearest level
under the price, with its anchor), and a **confluence** tag when 2+ of the 10 EMA / 21 EMA / an AVWAP sit within 0.25
ADR of each other.

**D. Exit line (G7).** Launches column "10 EMA (fast)" / "21 EMA (steady)" (rule in 2.4), and the day it closed under
it. The existing "first exit" (21 EMA) stays as it is.

**E. Size helper (G8).** Stop % (to today's low or the setup's stop), "size at 0.5% risk" as % of the account (cap by
tier), and the liquidity tier T1/T2/T3. Uses `settings.json` → a new `"risk"` block (risk_pct, caps per tier, gap
budget). The math runs in the portal; nothing is filtered.

**F. Breadth gauge (G5).** Computed in `launch.py daily()` over the momentum universe (Launches + 3-SETUPS + the feeder
lists):
- % Leading and % Lagging, and their change vs 5 sessions ago;
- failed breakouts in the last 5 sessions (closed back under the level within 3) vs all breakouts;
- gap-downs;
- QQQ / SPY / IWM against their 9 and 21 EMA (Luk) and their 10- vs 20-day MA (Qullamaggie);
- index distribution days in the last 25 sessions (down on higher volume than the day before) and "first bounce after
  a distribution day" (Luk's Jun 2026 post).

Output: `launch.json` → `"breadth"`, plus `regime.json` on radar-data with one row per day (history for S4 and for the
bot). Portal: one strip over the tabs: "Market: YELLOW · Leading 37% (−6 in 5 days) · Lagging 43% · failed breakouts 4
of 9 · QQQ over 9/21". The thresholds are placeholders until S4 sets them.

**G.** Replay `--regress` (nothing may change), rules workbook, HANDOFF; you look at the portal on the test branch;
"go live" for B–F.

### Phase 2: studies (test branch `test/lukstudy`; tools only, never main)
**H. S1, the pullback timing (G1, G3).**
- Reason for the 2-year run: it would add buy points.
- Every Launches and 3-SETUPS stock over 2 years: the 10 EMA (and 9 EMA) touch & reclaim, closing in the upper 60%
  of the day with the stack Leading, against your 21 EMA retest / undercut & reclaim / base breakout on the same
  stocks.
- Measured like the 2-year check (ran 10% / 20% in 20 sessions, failed in 5) plus R with `mgmt.py`.
- `scanner/probe_pullback.py`, radar-tools cmd `pullback`.

**I. S2, AVWAP.** Do pullbacks that hold or reclaim an AVWAP do better? Does confluence (2+ levels) help? Is the
launch anchor or the high anchor the one that matters? (Same runs as H.)

**J. S3, management.** On the 5,783 buy points (`scanner/mgmt.py` gets `run_luk()`), same entries and stops, compare:
- Luk: 15% at +4R, then breakeven **or** financed −0.71R; core on the 10 / 21 EMA close (fast/steady rule); the
  same-day cut; the optional sell-into-extension.
- Luk, the other version attributed to him: ~10% partials once up 3+ ADRs, trail on the 9 / 23 EMA.
- Yours: 1/3 at +2 ADR, 1/3 at +5 ADR, breakeven, runners on the 10 / 21 EMA close.
- Qullamaggie: 1/3–1/2 after 3–5 days, breakeven, the rest on the first close under the 10 / 20-day MA.

Reported by trigger type and by half (both halves must agree).

**K. S4, regime.**
- Reason: it would gate alerts and the bot's size.
- Rebuild the breadth gauge's history from daily bars and set it against the forward result of every buy point.
- Question: does "Leading % low and falling", "failed breakouts high" or "QQQ under its 9/21" cut more losers than
  winners?
- Sets green/yellow/red from percentiles, not guesses. Reports the cost too: the winners it would have skipped.

**L. S5, intraday triggers.**
- Alpaca SIP 1-minute bars, as `radar/sipcal.py` already uses, with a spread charge per minute of day.
- On S1's pullback days: your 5-minute ORH vs the flush & reclaim (stop at the flush low) vs the AVWAP/VWAP reclaim vs
  the 3:50 close-confirm.
- Each one also run with no entries before 9:45 (J Law's "not in the first 15 minutes").
- This picks the bot's entry types (2.4 ENTER a/b/c).

**M. S6, shorts (only if you answer yes in section 5).**
- Former leaders = were on Launches or RS 90+ in the last 120 sessions.
- Breakdown: a close under the 21 EMA on 1.5x+ volume after 10+ closes over it.
- Weak bounce: 2–4 days up on under-average volume into the falling 10/21 EMA or the AVWAP from the high, no close
  over the 21 EMA.
- Fast variant (Luk's GLD/SLV short, Mar 2026): the first close under the 9 EMA, then the first bounce into the falling
  9 EMA.
- Parabolic: 3+ up days, 4+ ADRs over the 10 EMA, climax volume.
- Entries: the day's low break / the 15-minute breakdown; stop at the high of day; cover into 2–3 ADRs under the 10
  EMA or on a close over it.
- Results by regime mode.

**N. Report.**
- One table per study, by half-period.
- Your examples replayed with `tools/replay.py`: IONQ May 11–Jun 3 2026, MRVL Mar 31–May 7 2026, SNDK Jul 7–28 2026
  (short), plus any you add.
- You decide what passes.

### Phase 3: new reads and alerts (only what passed; test branch, `--regress`, 2-year check, then "go live")
**O. "Pullback zone, day N" (G3)** in `follow()` and `s3_read()`. All of these must hold:
- the stock proved strength: a close 1.25+ ADR over its last breakout level, or a new high, in the last 10 sessions;
- day 3–7 of the pullback;
- 1.25–4 ADRs off the high;
- 10 > 21 > 50 EMA, rising;
- the low within 0.5 ADR of the 10 / 21 EMA or an AVWAP;
- volume on the pullback at or under its average.

Status text: "Pullback zone, day 5: 10 EMA 51.20 · 21 EMA 49.80 · AVWAP (launch) 49.40, buy the reclaim". On 3-SETUPS
it is Ready.

**P. "10 EMA reclaim (entry)" buy point (G1)**: the low under the 10 EMA (or the AVWAP), the close back over it in the
upper 40% of the day, stack Leading. `radar/alerts.py` gets `ema10`: from 3:45 PM "holding into the close", like the
retest. Desktop now; phone when you activate it.

**Q. AVWAP in the reads (G2)**: "+ AVWAP (launch) 49.40" in the retest / reclaim confluence text.

**R. Exit-line heads-up (G7)**: from 3:45 PM, a launch trading 0.1+ ADR under its exit line ("the close decides").

**S.** Examples into `tools/examples.txt` / `expected_reads.txt` (only after you agree the reads), `--regress`, the
2-year check, rules workbook, HANDOFF, then "go live" and the Launches rebuild (`picks.yml`).

### Phase 4: regime into the alerts and the bot
**T. Breadth mode on alerts**: YELLOW/RED put "market YELLOW: half size" at the top of long alerts. It's text, not a
filter, unless S4 shows a filter pays.

**U. `signals.json` on radar-data** (evening + intraday): for each actionable name the setup, trigger type, level,
stop rule, ADR, liquidity tier, best group, exit line, earnings date and the regime multiplier. The bot's only input
from the Radar: one-way and read-only, so the Radar never places orders.

### Phase 5: the short side (only with your yes)
**V. Short watch tab** (display first): former leaders, the breakdown day, the weak-bounce read (Ready), the parabolic
read (Watch); desktop alerts on the 15-minute breakdown / VWAP fail; a cover guide using index extension (SPY/IWM ADRs
under their 10 EMA, down days in a row: "Day 1 of the breakdown: hold; extended: cover into panic").

### Phase 6: the bot (your IBKR code; attach its repo to a session)
**W. Risk engine**: sizing, tier, capacity and gap caps, heat, group cap, the brake (2.4), with unit tests built on
`luk_risk_sim.py`'s cases.

**X. Position manager + IBKR layer**: the state machine in 2.4 (bracket, OCA trim/stop, financed stop, MOC trail,
same-day cut, earnings rule), restart-safe (state on disk, reconcile on connect), kill switch, journal.

**Y. Paper, then small.** IBKR paper account for 4–6 weeks: fills vs plan and slippage per trigger type. Then live at
0.25% risk for 50 trades, then 0.5% if the live expectancy is inside the simulation's bands.

**Z. Monthly review**: the journal (win rate, average win / loss in R, expectancy, the top-10 share, streaks, gap
events, slippage) against the Monte Carlo bands. Reset the brake's thresholds from your own data; update HANDOFF.

**Suggested order**: A → B–G (one session) → H, J, K (studies) → L → O–S for what passed → T–U → W–Z, alongside, since
the bot work doesn't touch the Radar → V/M only if you want shorts.

---

## 5. Your decisions (numbered, like your feedback)

1. **9 or 10 EMA?** My pick: keep your 10 (same in practice, your examples use it); S1 tests the 9 too.
2. **After the first trim**: (a) Luk: 15% at +4R → breakeven; (b) my pick: 15% at +4R → the financed −0.71R, breakeven
   after the 2nd close over +2R; (c) keep your 1/3 at +2 ADR, 1/3 at +5 ADR until S3 decides.
3. **Brake**: standard (5% / 10% drawdown steps) or loose (8% / 15%)?
4. **Account**: cash, Reg-T or portfolio margin, and roughly what size? This sets the gross cap, the liquidity tiers
   and whether 25–35% positions make sense at all.
5. **Shorts**: do you want the Short watch (display only first)? Should the bot ever short?
6. **Entries**: keep the 5-minute ORH only, or test the flush & reclaim and the 3:50 close-confirm against it (S5)?
7. **Order**: start with B–G (display only), or the studies first?
8. **The bot's code**: which repo? It isn't in this session. Attach it and I'll map 2.4 onto its structure.

---

## Sources

- Official results: [2025 USIC results (Business Wire, Feb 2 2026)](https://www.businesswire.com/news/home/20260202090143/en/), [2024 USIC results](https://www.businesswire.com/news/home/20250127956815/en/2024-United-States-Investing-Championship-Final-Results)
- His words: [X: "Stop = 1.5-5% · risk per trade 0.5% · max position 35%"](https://x.com/martinlukkt/status/1906196925122310291), [X: "20% drawdown… my line of defence"](https://x.com/martinlukkt/status/1931289636279922807), [guest article: 283% in USIC 2024](https://tradingresourcehub.substack.com/p/martin-luk-283-usic-2024-key-lessons)
- Interviews: [TraderLion podcast, +969% pullback strategy (Jan 31 2026)](https://podcasts.apple.com/us/podcast/969-return-in-1-year-the-winning-pullback-strategy/id1586336923?i=1000747508894), [TraderLion, 283% in 1 year (Apr 2025)](https://podwise.ai/episodes/3678850), [TraderLion thread: $1,300 start, 2021 −50%](https://x.com/TraderLion/status/2018716934406107198)
- Write-ups: [Kyna Kosling: his study process](https://tradingresourcehub.substack.com/p/martin-luk-study-process), [Decoding the +969%](https://mistakesoninvesting.substack.com/p/decoding-martin-luks-record-969-championship), [Financial Wisdom: pullback strategy](https://www.financialwisdomtv.com/post/martin-luk-s-pullback-trading-strategy-how-the-2025-u-s-investing-champion-finds-low-risk-high-re), [Financial Wisdom: swing strategy](https://www.financialwisdomtv.com/post/martin-luk-s-1358-swing-trading-strategy-from-gamestop-blow-up-to-us-investing-champion), [Forex Club profile](https://en.forexclub.pl/Martin-Luk-969-in-a-year-who-is-the-winner-of-the-US-Investing-Championship-and-how-does-he-trade/), [video summary: winning strategy](https://videohighlight.com/v/-6lPuMFSMG0), [Finetiq: AVWAP-EMA flush](https://ideas.finetiqsystems.com/en/ideas/avwap-ema-flush/)
- Independent backtest (CRSP + TAQ, 2016–2026): [rootchunhe/martin-luk-backtesting](https://github.com/rootchunhe/martin-luk-backtesting)
- The X accounts (1.1):
  - Luk: [Jackson Hole −8.5% lessons (Aug 2025)](https://x.com/martinlukkt/status/1959493436366897399), [market conditions from his own trades (Mar 2025)](https://twitter.com/martinlukkt/status/1905647784021393509), [distribution-day bounces → pullback short (Jun 2026)](https://x.com/martinlukkt/status/2064365486218060139), [GLD/SLV short at the declining 9 EMA (Mar 2026)](https://x.com/martinlukkt/status/2029074929736384773), [closed GLD/SLV early (Jan 2026)](https://x.com/martinlukkt/status/2017290915820478648), [fan reference: layout & screeners](https://martinluk.com/), [Substack comments (screener values, partials)](https://tradingresourcehub.substack.com/p/martin-luk-283-usic-2024-key-lessons/comments)
  - Qullamaggie: [his 3 setups (risk, size, sells)](https://qullamaggie.com/my-3-timeless-setups-that-have-made-me-tens-of-millions/), [sell 1/3–1/2 after 3–5 days (quote)](https://x.com/AsymTrading/status/1706716710735085833)
  - Minervini: [Progressive Exposure](https://x.com/markminervini/status/1293567014720745472), [trade largest when best](https://x.com/markminervini/status/1864122686076801164), [gaps and sizing](https://twitter.com/markminervini/status/970065583382450176), [rotation](https://x.com/markminervini/status/1260379022938251266), [his rules](https://x.com/markminervini/status/1859625009469112773)
  - Shannon: [gaps in his AVWAP book](https://x.com/alphatrends/status/2017668778545299489), [CMT podcast on AVWAP](https://cmtassociation.org/podcast/fill-the-gap-episode-sixty-one-anchored-vwap-legend-brian-shannon-cmt/), [5-day MA cheat sheet](https://alphatrends.net/archives/podcast/brian-shannon-shares-his-5-day-moving-average-cheat-sheet/)
  - Tendler: [the inchworm concept (TraderLion)](https://traderlion.com/trading-psychology/the-inchworm-concept/)
  - J Law: [market conditions thread](https://x.com/JLawStock/status/1883099593627574744), [trading from Hong Kong](https://x.com/JLawStock/status/1872983332327440872), [11 lessons (TraderLion)](https://traderlion.com/profile/j-law/11-lessons-from-j-law/), [two-year record](https://www.prnewswire.com/apac/news-releases/j-law-sets-two-year-record-with-1-499-return-in-us-investing-championship-302698517.html)
  - Moglen's 4-hour interview (risk, margin, sizing, sell rules): [announcement](https://x.com/RichardMoglen/status/2014030484611977625)
- IBKR / rules: [IBKR portfolio margin ($110K / $100K)](https://ibkb.interactivebrokers.com/es/node/83), [IBKR MOC orders](https://www1.interactivebrokers.com/en/trading/orders/moc.php), [NYSE closing auction (3:50 PM)](https://www.nyse.com/publicdocs/nyse/NYSE_Auctions_Closing_Process_Fact_Sheet.pdf), [PDT rule change 2026 (E*TRADE)](https://us.etrade.com/knowledge/library/margin/pattern-day-trading-rule-change)
- The article you sent (screenshots, Nov 3 2026): the 2026 dataset statistics marked ◇.
