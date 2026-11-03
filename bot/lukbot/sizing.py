"""Position size from the stop (Luk's one formula: position = risk / stop distance), with the caps that keep a tight
stop from becoming an oversized, gap-exposed position."""
import math
from dataclasses import dataclass

from .config import Config


@dataclass
class Size:
    shares: int
    position_pct: float        # % of equity
    risk_pct: float            # % of equity lost at the stop (after the caps)
    stop_pct: float            # stop distance, % of the entry
    stop_adr: float            # stop distance in ADRs
    binding: str               # which limit set the size: risk, tier cap, capacity, gap cap
    reject: str = ""           # why no trade ("" = OK)


def tier_cap(cfg: Config, dvol_m: float) -> float:
    """the largest position (% of equity) for a stock trading `dvol_m` $M a day (20-day average); 0 = too illiquid"""
    for floor, cap in cfg.tier_caps:
        if dvol_m >= floor:
            return cap
    return 0.0


def stop_ok(cfg: Config, entry: float, stop: float, adr_pct: float, side: int = 1):
    """(stop %, stop in ADRs, reason or "") for a long (side 1) or a short (side -1)"""
    dist = (entry - stop) * side
    if dist <= 0:
        return 0.0, 0.0, "stop on the wrong side of the entry"
    sp = 100 * dist / entry
    sa = sp / adr_pct if adr_pct > 0 else float("inf")
    if sp > cfg.max_stop_pct:
        return sp, sa, f"stop {sp:.2f}% is wider than {cfg.max_stop_pct}%"
    if sa > cfg.max_stop_adr:
        return sp, sa, f"stop {sa:.2f} ADR is wider than {cfg.max_stop_adr} ADR"
    if sp < cfg.min_stop_pct or sa < cfg.min_stop_adr:
        return sp, sa, f"stop {sp:.2f}% ({sa:.2f} ADR) is tighter than noise"
    return sp, sa, ""


def size_position(cfg: Config, equity: float, entry: float, stop: float, adr_pct: float, dvol_m: float,
                  mult: float = 1.0, side: int = 1, gap_pct: float = None, earnings_soon: bool = False,
                  trades_done: int = 10 ** 9) -> Size:
    """the shares to buy (side 1) or short (side -1).
    mult       the brake's multiplier (Brake.multiplier)
    gap_pct    the stock's bad overnight gap (95th percentile of |open / prev close - 1| over 250 sessions), % ;
               None = gap_default_adr ADRs (3 ADRs into earnings)
    trades_done live trades so far: under cfg.start_trades the risk is cfg.start_risk_pct"""
    sp, sa, why = stop_ok(cfg, entry, stop, adr_pct, side)
    if why:
        return Size(0, 0.0, 0.0, sp, sa, "stop", why)
    base = cfg.start_risk_pct if trades_done < cfg.start_trades else cfg.risk_pct
    risk = base * mult
    if risk <= 0:
        return Size(0, 0.0, 0.0, sp, sa, "brake", "the brake is at 0: no new trades")
    if dvol_m * 1e6 < cfg.capacity_multiple * equity:
        return Size(0, 0.0, 0.0, sp, sa, "capacity", f"${dvol_m:.0f}M a day is under {cfg.capacity_multiple:.0f}x your equity")
    cap_tier = tier_cap(cfg, dvol_m)
    if cap_tier <= 0:
        return Size(0, 0.0, 0.0, sp, sa, "tier", f"${dvol_m:.0f}M a day is under the lowest liquidity tier")
    g = gap_pct if gap_pct is not None else (3.0 if earnings_soon else cfg.gap_default_adr) * adr_pct
    limits = {
        "risk": 100 * risk / sp,                                        # % of equity
        "tier cap": cap_tier,
        "capacity": 100 * cfg.adv_cap_pct / 100 * dvol_m * 1e6 / equity,
        "gap cap": 100 * cfg.gap_budget_pct / g if g > 0 else float("inf"),
    }
    binding = min(limits, key=limits.get)
    pos_pct = limits[binding]
    shares = int(math.floor(equity * pos_pct / 100 / entry))
    if shares <= 0:
        return Size(0, 0.0, 0.0, sp, sa, binding, "less than one share")
    pos_pct = 100 * shares * entry / equity
    return Size(shares, round(pos_pct, 2), round(pos_pct * sp / 100, 3), round(sp, 3), round(sa, 3), binding)


def financed_stop(entry: float, stop: float, trim_frac: float, trim_price: float, side: int = 1) -> float:
    """the stop on the rest after selling `trim_frac` at `trim_price` that makes the whole trade's worst case exactly 0:
    banked = f * (trim - entry); the rest (1 - f) may lose that much: stop = entry - f * (trim - entry) / (1 - f).
    15% at +4R -> -0.71R (Luk moves to breakeven, which locks +0.6R but leaves the core no room)"""
    gain = (trim_price - entry) * side
    return entry - side * trim_frac * gain / (1 - trim_frac)
