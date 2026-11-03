"""The checks before every new entry: open risk (heat), the group cap, gross exposure, the market gap budget,
earnings, room to resistance, scheduled macro events and IBKR's own margin check."""
from dataclasses import dataclass, field

from .config import Config


@dataclass
class Held:
    """a position the bot holds, as the checks need it"""
    symbol: str
    side: int                  # 1 long, -1 short
    shares: int
    entry: float
    stop: float
    price: float
    group: str = ""
    gap_pct: float = 0.0       # its bad overnight gap, %
    financed: bool = False     # trimmed and its stop moved so that the worst case is 0R or better

    @property
    def value(self) -> float:
        return abs(self.shares) * self.price

    @property
    def open_risk(self) -> float:
        """$ lost if the stop is hit from here (0 once financed: the trim paid for it)"""
        if self.financed:
            return 0.0
        return max(0.0, (self.price - self.stop) * self.side) * abs(self.shares)


@dataclass
class Candidate:
    symbol: str
    side: int
    entry: float
    stop: float
    shares: int
    group: str = ""
    gap_pct: float = 0.0
    earnings_sessions: int = None      # sessions until its next report (None = unknown / far)
    resistance: float = None           # the next overhead level (the Radar's Resistance column); None = none
    reaction_setup: bool = False       # the setup IS the earnings reaction (a gap on the report)
    notes: list = field(default_factory=list)


def check_entry(cfg: Config, equity: float, held: list, cand: Candidate, event_tomorrow: bool = False,
                event_today_before_release: bool = False, excess_liq_after: float = None) -> list:
    """the reasons the new trade is refused; [] = all checks passed"""
    out = []
    value = cand.shares * cand.entry
    risk = abs(cand.entry - cand.stop) * cand.shares
    if len(held) >= cfg.max_positions:
        out.append(f"{len(held)} positions already (max {cfg.max_positions})")
    heat = sum(h.open_risk for h in held) + risk
    if 100 * heat / equity > cfg.heat_max_pct:
        out.append(f"open risk would be {100 * heat / equity:.2f}% (max {cfg.heat_max_pct}%)")
    if cand.group:
        same = [h for h in held if h.group == cand.group]
        if len(same) >= cfg.group_max_positions:
            out.append(f"{len(same)} positions in {cand.group} already (max {cfg.group_max_positions})")
        g_val = sum(h.value for h in same) + value
        if 100 * g_val / equity > cfg.group_max_gross_pct:
            out.append(f"{cand.group} would be {100 * g_val / equity:.0f}% of equity (max {cfg.group_max_gross_pct:.0f}%)")
    gross = sum(h.value for h in held) + value
    if 100 * gross / equity > cfg.gross_max_pct:
        out.append(f"gross exposure would be {100 * gross / equity:.0f}% (max {cfg.gross_max_pct:.0f}%)")
    gap_load = sum(h.value / equity * h.gap_pct for h in held) + value / equity * cand.gap_pct
    if gap_load > cfg.market_gap_budget_pct:
        out.append(f"a bad overnight gap across the book would cost {gap_load:.1f}% (max {cfg.market_gap_budget_pct}%)")
    if (cand.earnings_sessions is not None and cand.earnings_sessions <= cfg.earnings_block_sessions
            and not cand.reaction_setup):
        out.append(f"earnings in {cand.earnings_sessions} session(s)")
    if cand.resistance is not None and risk > 0:
        room_r = (cand.resistance - cand.entry) * cand.side / abs(cand.entry - cand.stop)
        if 0 < room_r < cfg.room_min_r:
            out.append(f"only {room_r:.1f}R to the resistance at {cand.resistance:.2f} (min {cfg.room_min_r}R)")
    if event_today_before_release:
        out.append("a scheduled macro event today, before its release")
    if event_tomorrow and not cand.reaction_setup:
        cand.notes.append("macro event tomorrow: this position is cut to half at today's close unless financed")
    if excess_liq_after is not None and 100 * excess_liq_after / equity < cfg.min_excess_liq_pct:
        out.append(f"IBKR excess liquidity after the trade {100 * excess_liq_after / equity:.0f}% (min {cfg.min_excess_liq_pct:.0f}%)")
    return out


def rotation_candidates(held: list, need_value: float) -> list:
    """Minervini's rotation when buying power is full: the weakest positions (closest to their stop in R) to sell half
    of, until `need_value` is freed. Returns [(symbol, shares to sell)]"""
    def r_now(h):
        r = abs(h.entry - h.stop) or 1e-9
        return (h.price - h.entry) * h.side / r
    out, freed = [], 0.0
    for h in sorted(held, key=r_now):
        if freed >= need_value:
            break
        q = abs(h.shares) // 2
        if q > 0:
            out.append((h.symbol, q))
            freed += q * h.price
    return out
