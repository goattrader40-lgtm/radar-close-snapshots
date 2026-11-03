"""One object your bot talks to: sizing + portfolio checks + the brake + trade management + the journal.

    from lukbot import Config, LukSession
    s = LukSession(Config(), equity=250_000, journal="journal/trades.jsonl")
    acts, why = s.plan_entry(symbol, side=1, trigger=49.40, stop=48.77, adr_pct=5.1, dvol_m=180, group="Quantum",
                             held=s.held(prices), regime="GREEN", setup="21 EMA & AVWAP reclaim", reclaim_level=49.35)
    ibkr.execute(acts)                      # or your own order code
    ... s.on_entry_fill(sym, fill_price, qty, "2026-11-04")
    ... s.on_price(sym, price) / s.on_fill(sym, tag, qty, price) / s.close_check(...) / s.daily_close(...)
"""
import datetime as dt

from .brake import Brake
from .config import Config
from .journal import Journal
from .manage import Trade, TradeManager
from .portfolio import Candidate, Held, check_entry
from .sizing import size_position


class LukSession:
    def __init__(self, cfg: Config, equity: float, journal: str = "journal/trades.jsonl", trades_done: int = 0,
                 today: dt.date = None):
        self.cfg, self.equity = cfg, equity
        self.brake = Brake(cfg, equity, today)
        self.tm = TradeManager(cfg)
        self.journal = Journal(journal)
        self.trades = {}               # symbol -> Trade (open or pending)
        self.trades_done = trades_done
        self.meta = {}                 # symbol -> what to journal (setup, regime, m, gap)

    # ---- state ------------------------------------------------------------------------------------------------
    def update_equity(self, equity: float, today: dt.date = None):
        self.equity = equity
        self.brake.update_equity(equity, today)

    def held(self, prices: dict, gaps: dict = None) -> list:
        gaps = gaps or {}
        return [Held(s, t.side, t.shares, t.entry, t.stop, prices.get(s, t.entry), t.group, gaps.get(s, 0.0), t.financed)
                for s, t in self.trades.items() if t.shares > 0]

    # ---- entry ------------------------------------------------------------------------------------------------
    def plan_entry(self, symbol: str, side: int, trigger: float, stop: float, adr_pct: float, dvol_m: float,
                   group: str = "", held: list = None, regime: str = "GREEN", distribution_bounce: bool = False,
                   a_setup: bool = False, gap_pct: float = None, earnings_sessions: int = None, resistance: float = None,
                   reaction_setup: bool = False, event_tomorrow: bool = False, event_today_before_release: bool = False,
                   excess_liq_after: float = None, setup: str = "", reclaim_level: float = None, manual: bool = False):
        """([Action], [reasons]): the entry with its stop, or [] and why not"""
        if manual and not self.brake.manual_allowed(regime):
            return [], ["override lock: the brake is at its lowest, no manual trades"]
        ok, why = self.brake.new_entry_allowed()
        if not ok:
            return [], [why]
        m, mwhy = self.brake.multiplier(regime, distribution_bounce, a_setup)
        sz = size_position(self.cfg, self.equity, trigger, stop, adr_pct, dvol_m, m, side, gap_pct,
                           earnings_soon=earnings_sessions is not None and earnings_sessions <= 1, trades_done=self.trades_done)
        if sz.reject:
            return [], [sz.reject] + mwhy
        g = gap_pct if gap_pct is not None else self.cfg.gap_default_adr * adr_pct
        cand = Candidate(symbol, side, trigger, stop, sz.shares, group, g, earnings_sessions, resistance, reaction_setup)
        bad = check_entry(self.cfg, self.equity, held or [], cand, event_tomorrow, event_today_before_release, excess_liq_after)
        if bad:
            return [], bad
        t = Trade(symbol, side, stop, reclaim_level=reclaim_level, group=group, setup=setup)
        self.trades[symbol] = t
        self.meta[symbol] = dict(setup=setup, regime=regime, brake_m=m, size=sz.__dict__, manual=manual, trigger=trigger,
                                 stop0=stop, notes=cand.notes)
        return self.tm.entry_orders(t, trigger, sz.shares, adr_pct), [f"size {sz.position_pct}% ({sz.binding}), "
                                                                       f"risk {sz.risk_pct}%, stop {sz.stop_pct}% = {sz.stop_adr} ADR"] + mwhy + cand.notes

    def on_entry_fill(self, symbol: str, price: float, qty: int, date: str):
        self.brake.record_entry()
        self.meta[symbol]["slippage_entry_pct"] = round(100 * (price / self.meta[symbol]["trigger"] - 1), 3)
        return self.tm.on_entry_fill(self.trades[symbol], price, qty, date)

    # ---- management ---------------------------------------------------------------------------------------------
    def on_price(self, symbol: str, price: float):
        return self.tm.on_price(self.trades[symbol], price)

    def on_fill(self, symbol: str, tag: str, qty: int, price: float, history: dict = None, date: str = ""):
        t = self.trades[symbol]
        acts = self.tm.on_fill(t, tag, qty, price, history)
        if t.closed:
            self._close(t, date)
        return acts

    def close_check(self, symbol: str, price: float, prev_ema_fast: float, prev_ema21: float, adr_pct: float, day0: bool):
        return self.tm.on_close_check(self.trades[symbol], price, prev_ema_fast, prev_ema21, adr_pct, day0)

    def daily_close(self, symbol: str, close: float, ema_fast: float, ema21: float, adr_pct: float):
        return self.tm.on_daily_close(self.trades[symbol], close, ema_fast, ema21, adr_pct)

    def next_open(self, symbol: str, range_low: float, range_high: float, price: float):
        return self.tm.on_next_open(self.trades[symbol], range_low, range_high, price)

    def event_eve(self, symbol: str, kind: str):
        return self.tm.on_event_eve(self.trades[symbol], kind)

    def _close(self, t: Trade, date: str):
        r = t.r_result()
        self.brake.record_exit(r, t.stopped)
        self.trades_done += 1
        self.journal.record(symbol=t.symbol, side=t.side, opened=t.opened, closed=date, entry=t.entry, r=round(r, 3),
                            stopped=t.stopped, sessions=t.sessions, exit_mode=t.exit_mode, fills=t.fills, **self.meta.get(t.symbol, {}))
        del self.trades[t.symbol]
