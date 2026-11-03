"""The brake: how much of the risk unit the bot may use right now (m from 0 to 1, 1.5 with the optional cushion).

Mechanical versions of: Luk's "smaller portfolio risk if I am testing the water" and "should've opened less new
positions" (20% drawdown, Jun 2025), Minervini's progressive exposure (pilot buys back in, step up as they work),
Tendler's C-game floor (no manual overrides while the brake is on), and Luk's distribution-day lesson (Jun 2026).
In the simulation (plans/martin-luk/luk_risk_sim.py) the drawdown / streak / month steps cut a choppy year's bad-case
drawdown from 58% to 24% and its worst month from -20% to -9%.
"""
import datetime as dt

from .config import Config


class Brake:
    def __init__(self, cfg: Config, equity: float, today: dt.date = None):
        self.cfg = cfg
        today = today or dt.date.today()
        self.high = equity
        self.equity = equity
        self.month = (today.year, today.month)
        self.month_start = equity
        self.day = today
        self.day_stops = 0
        self.day_entries = 0
        self.streak = 0                  # losses in a row
        self.streak_brake = False        # set at `streak_losses`, cleared by a +2R winner
        self.ramp_idx = None             # None = full size; else an index into cfg.ramp
        self.ramp_wins = 0

    # ---- inputs -----------------------------------------------------------------------------------------------
    def update_equity(self, equity: float, today: dt.date = None):
        today = today or dt.date.today()
        if (today.year, today.month) != self.month:
            self.month, self.month_start = (today.year, today.month), self.equity
        if today != self.day:
            self.day, self.day_stops, self.day_entries = today, 0, 0
        self.equity = equity
        if equity > self.high:
            self.high = equity
            self.ramp_idx, self.ramp_wins = None, 0          # a new equity high: back to full
        if self.ramp_idx is None and self._raw() < 1.0:
            self.ramp_idx, self.ramp_wins = 0, 0             # any step under 1: come back by the ramp later
        elif self.ramp_idx is not None and self._raw() >= 1.0 and self.month_pct() > 0:
            self.ramp_idx, self.ramp_wins = None, 0          # the brake has cleared and the month is green: full

    def record_entry(self):
        self.day_entries += 1

    def record_exit(self, r_multiple: float, stopped: bool):
        """a closed trade (or a stopped piece of one): its result in R and whether the initial stop was hit"""
        if stopped:
            self.day_stops += 1
        if r_multiple < 0:
            self.streak += 1
            if self.streak >= self.cfg.streak_losses:
                self.streak_brake = True
        else:
            self.streak = 0
            if r_multiple >= self.cfg.streak_reset_r:
                self.streak_brake = False
            if self.ramp_idx is not None and r_multiple > 0:
                self.ramp_wins += 1
                if self.ramp_wins >= self.cfg.ramp_wins_to_step:
                    self.ramp_idx, self.ramp_wins = self.ramp_idx + 1, 0
                    if self.ramp_idx >= len(self.cfg.ramp) - 1:
                        self.ramp_idx = None

    # ---- outputs ----------------------------------------------------------------------------------------------
    def drawdown_pct(self) -> float:
        return 100 * (1 - self.equity / self.high) if self.high > 0 else 0.0

    def month_pct(self) -> float:
        return 100 * (self.equity / self.month_start - 1) if self.month_start > 0 else 0.0

    def _raw(self) -> float:
        """the drawdown, streak and month steps (the part the simulation tested)"""
        m, dd, mtd = 1.0, self.drawdown_pct(), self.month_pct()
        for lim, mult in self.cfg.dd_steps:
            if dd >= lim:
                m = min(m, mult)
        if self.streak_brake:
            m = min(m, self.cfg.streak_mult)
        for lim, mult in self.cfg.month_loss_steps:
            if mtd <= -lim:
                m = min(m, mult)
        return m

    def multiplier(self, regime: str = "GREEN", distribution_bounce: bool = False, a_setup: bool = False):
        """(m, reasons): multiply the risk unit by m; 0 = no new trades"""
        c, why = self.cfg, []
        m = self._raw()
        if m < 1.0:
            why.append(f"drawdown {self.drawdown_pct():.1f}% / month {self.month_pct():+.1f}% / streak {self.streak}")
        if self.ramp_idx is not None and m >= 1.0:          # the steps have cleared: come back by the ramp
            m = c.ramp[self.ramp_idx]
            why.append(f"ramp back step {self.ramp_idx + 1} of {len(c.ramp)}")
        if self.day_stops >= c.day_stops_max:
            m = 0.0
            why.append(f"{self.day_stops} stop-outs today")
        rm = c.regime_mult.get(regime, 0.5)
        if rm < 1.0:
            m = min(m, rm)
            why.append(f"market {regime}")
        if distribution_bounce:
            m = min(m, c.distribution_bounce_mult)
            why.append("first bounce after a distribution day")
        if (a_setup and c.cushion_mult > 1 and m >= 1.0 and self.month_pct() >= c.cushion_month_pct
                and self.equity >= 0.98 * self.high):
            m = c.cushion_mult
            why.append("cushion: A setup with the month up")
        return m, why

    def new_entry_allowed(self) -> (bool, str):
        if self.drawdown_pct() >= self.cfg.dd_new_positions_trigger and self.day_entries >= self.cfg.dd_new_positions_per_day:
            return False, f"in a {self.drawdown_pct():.1f}% drawdown: {self.day_entries} new positions today already"
        if self.day_stops >= self.cfg.day_stops_max:
            return False, f"{self.day_stops} stop-outs today"
        return True, ""

    def manual_allowed(self, regime: str = "GREEN") -> bool:
        """the override lock (Tendler's C-game floor): no manual trades or size-ups while the brake is at its lowest"""
        return self.multiplier(regime)[0] > self.cfg.override_lock_at
