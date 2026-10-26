# Setup scanner

Runs steps 1–3 of your TradingView workflow every trading day at about 4:40 PM ET
(GitHub Actions → **Setup scanner**). Results are in [`setups/`](../setups/):

- [`setups/README.md`](../setups/README.md): today's 3-SETUPS table, today's adds and deletes, and the other lists.
- `setups/tradingview/*.txt`: one import file per list, with a `###` section per date or setup type
  (TradingView → Watchlist menu → Import list).
- `setups/latest.json`: everything in machine form, for the portal and bots. `setups/history/` keeps each day.

## What it does

| Step | Screener (your filters + the standard ones) | Goes to | When |
|---|---|---|---|
| 1 | EP-GAPUP-BREAKOUT: gap > 5%, rel vol ≥ 2.5 | 1-EP/GAP, section = date | daily |
| 1 | HOTTEST STOCKS: change ≥ 4%, rel vol ≥ 1 | 1-UPDAY, section = date | daily |
| 2 | 50 EMA FIRST CLOSE: first close above the 50 EMA after 2+ closes below | 2-POOL › 50 EMA reclaim | daily |
| 2 | MOMENTUM-1W > 10% · 1M > 25% · 3M > 50% · 6M > 50% (+ above 200 SMA, 50%+ above the 52-week low) | 2-POOL › Momentum | weekly (Friday) |
| 3 | DAILY TIGHTNESS · PULLBACK TO 21EMA-MAIN · PULLBACK TO 50EMA, run on 1-EP/GAP + 1-UPDAY + 2-POOL | 3-SETUPS › Tight / PB 21 / PB 50 | daily |

Standard filters on every screener: price ≥ $10, market cap $700M–$2T, 30-day average volume > 700K,
price × 30-day average volume > $20M, ADR ≥ 4%, price above the daily 50 EMA, price at least 30% above the
52-week low. DAILY TIGHTNESS: 40%+ above the 52-week low, at most 30% below the 52-week high, volume at least 20%
under the 30-day average, and today's range ≤ 0.8 × the average range of the previous 10 days; today and at least
3 of the last 5 days must be tight days like that.

Into 3-SETUPS only if it is above the 200 SMA. (Higher high + higher low and the 300% no-chase rule are off — your
choice, Oct 25; both are settings.) The grade shows setup quality only; it never blocks a move to 3-SETUPS.
Each 3-SETUPS name also gets the Momentum Setup Finder (v29.4, coil = 3 candles) columns: grade, pattern, buy point, coil /
pullback / trendline / level / flat-top entries, and whether the 21 / 50 EMA intraday trigger is armed.

Deletes: 2 closes in a row below the 50 EMA (any list) · 1-EP/GAP and 1-UPDAY: 15 trading days without reaching
3-SETUPS · 1-UPDAY: a close below the up-day low (a close below the gap low no longer deletes from 1-EP/GAP) ·
2-POOL at the weekly refresh: below the 200 SMA, no longer liquid · 3-SETUPS: a close below the 200 SMA, and a weekly
trim to the best 30
(recent hit first, then grade, then MSF score).

Not yet: FUNDAMENTAL-GROWTH (needs revenue data), orange / red flags, earnings dates.

## Files

- `settings.json`: every number above. Change it and the next run uses it.
- `fetch.py`: downloads the bars (Nasdaq symbol list, Yahoo daily bars).
- `screens.py`: the screeners. `run.py`: the lists. `msf.py`: Momentum Setup Finder daily engine (a line-by-line
  port of the Pine script, checked against it on the test charts).
- `state.json`: the lists as of the last run (the scanner's memory).
