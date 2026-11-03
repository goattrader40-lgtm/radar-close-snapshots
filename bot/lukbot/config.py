"""Every number the trade manager uses, in one place. Percent values are percents (0.3 = 0.3%).

Defaults follow Martin Luk's published numbers (his X posts; James Muninn's audit of 461 of his 2026 stream trades:
0.3% risk a trade in 2026, 0.5% in 2025, a 1.28% median stop, positions 20-30% capped at 35%, trims of 10-15% at
+3-5R, the core trailed on the daily close under the 9 EMA (fast leaders) or the 21 EMA (steady trends)), plus the
improvements in plans/martin-luk/PLAN.md section 2.4 (brake, gap cap, group cap, financed stop, event rule).
"""
from dataclasses import dataclass, field


@dataclass
class Config:
    # ---- risk unit -------------------------------------------------------------------------------------------
    risk_pct: float = 0.30                  # % of equity lost at the stop (Luk 2026: 0.3; 2025: 0.5)
    start_risk_pct: float = 0.25            # for the first `start_trades` live trades
    start_trades: int = 50

    # ---- position caps ---------------------------------------------------------------------------------------
    # (20-day average $ volume in $M, the largest position as % of equity): Luk caps 35% in liquid leaders, less in
    # small caps because of gap risk
    tier_caps: tuple = ((100.0, 35.0), (50.0, 25.0), (20.0, 15.0))
    adv_cap_pct: float = 1.0                # position <= 1% of the stock's 20-day average $ volume
    capacity_multiple: float = 50.0         # the stock trades >= 50x your equity a day (Qullamaggie's rule of thumb)
    gap_budget_pct: float = 2.0             # position% x its bad overnight gap (95th pct) <= 2% of equity
    gap_default_adr: float = 2.0            # bad gap when unknown = 2 ADRs (3 ADRs into earnings)
    market_gap_budget_pct: float = 8.0      # sum over positions of position% x bad gap <= 8% of equity

    # ---- stop width -----------------------------------------------------------------------------------------
    max_stop_pct: float = 5.0               # Luk: "Stop = 1.5-5%"
    max_stop_adr: float = 0.5               # and never over half the ADR
    min_stop_pct: float = 0.6               # tighter than this is noise
    min_stop_adr: float = 0.2

    # ---- portfolio --------------------------------------------------------------------------------------------
    heat_max_pct: float = 2.5               # open risk at the stops of positions not yet financed, incl. the new one
    group_max_positions: int = 2            # per Radar group (theme / industry)
    group_max_gross_pct: float = 60.0
    gross_max_pct: float = 200.0            # cash 100, Reg-T 200 overnight, portfolio margin up to ~300
    min_excess_liq_pct: float = 10.0        # IBKR ExcessLiquidity after the trade, % of net liquidation
    max_positions: int = 10
    earnings_block_sessions: int = 2        # no new entry with earnings this close (unless the setup is the reaction)
    room_min_r: float = 3.0                 # next overhead resistance at least 3R above the entry (J Law aims for 5:1)

    # ---- management -------------------------------------------------------------------------------------------
    trim_at_r: float = 4.0                  # sell `trim_frac` at +4R ...
    trim_frac: float = 0.15
    stop_after_trim: str = "financed"       # "financed": the stop that makes the worst case 0R; "breakeven": Luk's
    be_after_closes_over_r: float = 2.0     # then breakeven after 2 daily closes over +2R
    be_after_n_closes: int = 2
    fast_lookback: int = 10                 # fast leader: over the last 10 sessions the average close is 1+ ADR over
    fast_avg_adr_over_21: float = 1.0       # the 21 EMA, with at most 1 close under the 10 EMA -> trail the 10 EMA
    fast_max_closes_under_10: int = 1
    fast_ema: int = 10                      # Luk uses the 9; the Radar uses the 10 (same in practice)
    steady_ema: int = 21
    trail_buffer_adr: float = 0.1           # at 15:47 a price this far under the line -> sell MOC; closer -> wait for the close
    day0_cut: bool = True                   # under the entry and the reclaimed level at 15:50 on day 0 -> out at the close
    extension_adr: float = 4.0              # a close 4+ ADRs over the fast EMA = parabolic ...
    extension_sell_frac: float = 0.0        # ... sell this much next morning (0 = off; Muninn: Luk sold half GME into strength)
    earnings_keep_frac_unfinanced: float = 0.5   # before a report, an unfinanced position is cut to this
    event_cut_frac_unfinanced: float = 0.5  # the day before FOMC / CPI / payrolls / Jackson Hole (Luk, Aug 2025: -8.5%)

    # ---- the brake (m multiplies risk_pct) --------------------------------------------------------------------------
    dd_steps: tuple = ((5.0, 0.5), (10.0, 0.25))          # equity this far under its high -> m; loose: ((8, .5), (15, .25))
    streak_losses: int = 5                                  # 5 losses in a row -> m <= 0.5 until a +2R winner
    streak_mult: float = 0.5
    streak_reset_r: float = 2.0
    day_stops_max: int = 3                                  # 3 stop-outs today -> no new trades today
    month_loss_steps: tuple = ((8.0, 0.25), (12.0, 0.0))    # month to date -8% -> 0.25, -12% -> paper only
    dd_new_positions_trigger: float = 5.0                   # 5%+ under the high -> at most 2 new positions a day
    dd_new_positions_per_day: int = 2                       # (Luk, Jun 2025: "should've opened less new positions")
    regime_mult: dict = field(default_factory=lambda: {"GREEN": 1.0, "YELLOW": 0.5, "RED": 0.0})
    distribution_bounce_mult: float = 0.5                   # the first bounce day after an index distribution day
    ramp: tuple = (0.25, 0.5, 1.0)                          # coming back (Minervini's pilot buys)
    ramp_wins_to_step: int = 2
    cushion_mult: float = 1.0                               # 1.5 = Luk's "more risk on A+ setups with a cushion"
    cushion_month_pct: float = 5.0
    override_lock_at: float = 0.25                          # m at or under this: no manual trades or size-ups


LOOSE_BRAKE = dict(dd_steps=((8.0, 0.5), (15.0, 0.25)), streak_losses=7, month_loss_steps=((10.0, 0.25), (15.0, 0.0)))
LUK_2025 = dict(risk_pct=0.5, stop_after_trim="breakeven")
