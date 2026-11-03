# lukbot: Martin Luk-style risk and trade management for your IBKR bot (Task 1)

A drop-in module for your IBKR bot. It doesn't scan or pick stocks; it decides **how much**, **whether it's allowed**
and **how to manage** each trade, then hands your bot ready-made orders. Pure Python with no packages needed; the IBKR
part uses `ib_async` (`pip install ib_async`).

Tests: `python3 -m unittest discover -s bot/tests -v` (29 tests).

## What it does

| Part | File | Rule (defaults in `config.py`) |
|---|---|---|
| Size | `sizing.py` | position = risk ÷ stop. Risk **0.3%** of equity (Luk 2026; 0.25% for your first 50 live trades). Capped by: **35 / 25 / 15%** by liquidity ($100M+ / $50M+ / $20M+ a day), 1% of the stock's daily $ volume, and a **gap cap** (position × its bad overnight gap ≤ 2% of equity). Stop ≤ 5% and ≤ ½ ADR, ≥ 0.6% and ≥ 0.2 ADR. The stock must trade 50× your equity a day |
| Checks | `portfolio.py` | open risk ≤ **2.5%** (financed positions count 0), ≤ 2 positions and ≤ 60% gross per Radar group, gross ≤ your account's limit, market gap budget ≤ 8%, no entry with earnings in 2 sessions, **≥ 3R of room** to the next resistance, no entry on a macro-event day before the release, IBKR excess liquidity ≥ 10% after the trade; **rotation** (sell half of the 2 weakest) when buying power is full |
| Brake | `brake.py` | multiplies the risk: 5–10% under the equity high ½, 10%+ ¼; 5 losses in a row ½ until a +2R winner; 3 stops today → stop; month −8% ¼, −12% paper only; market YELLOW ½ / RED 0; first bounce after a distribution day ½; in a drawdown max 2 new positions a day; back by the **ramp** ¼ → ½ (2 winners) → full (new high or green month); **override lock** (no manual trades at ¼). `LOOSE_BRAKE` = 8 / 15% steps |
| Manage | `manage.py` | entry = stop-limit with the stop attached at IBKR. **Trim 15% at +4R** → stop on the rest to the **financed stop** (−0.71R: the trade can't lose) or breakeven (`stop_after_trim="breakeven"`, Luk's). Breakeven after the 2nd close over +2R. **Core exits on a daily close** under the **10 EMA** (fast leader) or **21 EMA** (steady), decided when the trim fills. 15:47 ET: clearly under → **MOC** order; too close to call → wait for the official close, then out on the next morning's 5-minute low break or by 10:00. **Day 0:** under the entry and the reclaimed level at 15:50 → out at the close. Earnings / macro event next session and not financed → cut to half. Optional: sell 20% into a 4-ADR extension |
| Journal | `journal.py` | one line per trade (R, stopped, setup, regime, brake, slippage, fills); `stats()` compares with Luk: 19–20% wins, 7–8:1 payoff, the top-10 share, the worst streak |
| Radar | `radar_feed.py` | reads `setups/launch.json`: buy point, ADR, $ volume, group, RS, resistance, and from the Task 2 portal fields the trend, AVWAP, exit line, pullback zone and the market gauge |
| IBKR | `ibkr.py` | brackets (parent STP LMT + child STP), stop modify, MOC, `whatIfOrder` margin check, positions to reconcile, kill switch (cancels everything except the stops). `dry_run=True` prints the orders |
| Glue | `session.py` | `LukSession`: the one object your bot calls |

## Plugging it into your bot

```python
from lukbot import Config, LukSession, radar_feed
from lukbot.ibkr import IBKR

cfg = Config()                      # Config(risk_pct=0.5, stop_after_trim="breakeven") = Luk 2025; Config(**LOOSE_BRAKE)
broker = IBKR(port=7497, dry_run=True).connect()           # paper first; dry_run prints orders
s = LukSession(cfg, equity=broker.account()["NetLiquidation"], journal="journal/trades.jsonl")

doc = radar_feed.load()                                    # the Radar's launch.json from main
mode, dist_bounce = radar_feed.regime(doc)
for p in radar_feed.plans(doc, min_rs=80):
    # YOUR bot decides the live trigger and stop (the flush low / today's low / the 1-5 minute AVWAP), then:
    acts, why = s.plan_entry(p["symbol"], 1, trigger, stop, p["adr_pct"], p["dvol_m"], group=p["group"],
                             held=s.held(prices), regime=mode, distribution_bounce=dist_bounce,
                             resistance=p["resistance"], setup=p["setup"], reclaim_level=level,
                             excess_liq_after=broker.excess_after(p["symbol"], "BUY", qty, trigger))
    broker.execute(acts) if acts else print(p["symbol"], why)

# your event loop feeds it:
s.on_entry_fill(sym, fill_price, qty, date)        # when the entry fills
broker.execute(s.on_price(sym, price))             # every price update (the +4R trim)
broker.execute(s.on_fill(sym, tag, qty, price, history))  # trim / stop / MOC fills (history: closes, EMAs, ADR)
broker.execute(s.close_check(sym, price, prev_ema10, prev_ema21, adr, day0))   # 15:47 ET
broker.execute(s.daily_close(sym, close, ema10, ema21, adr))                   # after 16:00
broker.execute(s.next_open(sym, range_low, range_high, price))                 # 9:35 ET
broker.execute(s.event_eve(sym, "earnings"))       # the session before a report / FOMC / CPI / payrolls
s.update_equity(net_liq, today)                    # every update; the brake reads it
```

Dry run on the Nov 2 close (MNDY, buy point 97.00 from the Radar, a 1.28% stop like Luk's median, $250K):
`size 18.55% (gap cap), risk 0.237%, stop 1.278% = 0.237 ADR` → `BUY 478 MNDY STP LMT 97.00 / 97.52` + `SELL 478 STP 95.76`.
The gap cap set the size because no real overnight-gap number was given. Pass `gap_pct` (the stock's 95th-percentile
overnight gap) for real sizes.

## Before real money
1. Paper account for 4–6 weeks; check each order type once (bracket, modify, MOC before 15:50, the kill switch).
2. Choose the stop trigger method (`IBKR(trigger_method=...)`): with 1–1.5% stops, one bad "last" print can hit them.
3. Live at 0.25% for the first 50 trades (automatic), then 0.3%.
4. Every month: `stats()` on the journal vs Luk's numbers and `plans/martin-luk/luk_risk_sim.py`'s bands.
