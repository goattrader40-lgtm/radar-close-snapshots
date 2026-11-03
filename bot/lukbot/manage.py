"""Managing a trade from entry to exit, the way Luk does it, made mechanical and broker-agnostic.

Every handler returns a list of Action objects; your bot (or lukbot.ibkr.IBKR) turns them into orders. Feed it:
  on_entry_fill(...)      when the entry fills
  on_price(...)           intraday prices (every few seconds or every 1-minute bar)
  on_fill(...)            when one of its exit orders fills (trim, stop, MOC ...)
  on_close_check(...)     at 15:47 ET with the live price and yesterday's EMAs (the daily-close trail, the day-0 cut)
  on_daily_close(...)     after 16:00 with the official close and today's EMAs
  on_next_open(...)       after the first 5 minutes of the next session (the 5-minute range)
  on_event_eve(...)       the session before earnings or a macro event (FOMC, CPI, payrolls, Jackson Hole)

The rules (plans/martin-luk/PLAN.md, section 2.4):
  stop      at IBKR from the first second (a child order of the entry), never only in the bot
  trim      15% at +4R; the rest's stop -> the financed stop (worst case 0R, -0.71R) or breakeven (Luk)
  ratchet   breakeven after the 2nd daily close over +2R
  trail     the core exits on a daily CLOSE under its line: the 10 EMA for a fast leader, the 21 EMA for a steady one
            (decided when the trim fills); before the trim the 21 EMA. 15:47: clearly under -> MOC (NYSE cutoff 15:50,
            Nasdaq 15:55); within 0.1 ADR -> wait for the official close, then out on the next morning's 5-minute low
  day 0     under the entry and under the reclaimed level at 15:50 on the entry day -> out at the close
  events    unfinanced positions cut to half the session before earnings / a macro event
"""
from dataclasses import dataclass, field

from .config import Config
from .sizing import financed_stop


@dataclass
class Action:
    kind: str                  # "BUY" | "SELL" | "MODIFY_STOP" | "CANCEL"
    symbol: str
    qty: int
    order_type: str = "LMT"    # "LMT" | "MKT" | "MOC" | "STP" | "STP LMT"
    price: float = None        # limit price
    stop: float = None         # stop (aux) price
    tag: str = ""              # entry, stop, trim, trail, day0, next_open, extension, earnings, event, ratchet
    reason: str = ""
    deadline: str = ""         # e.g. "10:00": switch to MKT if not filled by then


def ema_today(prev_ema: float, price: float, n: int) -> float:
    """today's EMA if the day closed at `price`"""
    k = 2 / (n + 1)
    return prev_ema + k * (price - prev_ema)


def is_fast_leader(cfg: Config, closes: list, ema_fast: list, ema21: list, adr_pct: float) -> bool:
    """over the last `fast_lookback` sessions: the average close 1+ ADR over the 21 EMA and at most 1 close under the
    fast EMA -> trail the fast EMA; else the 21 EMA"""
    n = min(cfg.fast_lookback, len(closes), len(ema_fast), len(ema21))
    if n < 3 or adr_pct <= 0:
        return False
    c, f, s = closes[-n:], ema_fast[-n:], ema21[-n:]
    over = sum(100 * (c[k] / s[k] - 1) / adr_pct for k in range(n)) / n
    under10 = sum(1 for k in range(n) if c[k] < f[k])
    return over >= cfg.fast_avg_adr_over_21 and under10 <= cfg.fast_max_closes_under_10


@dataclass
class Trade:
    symbol: str
    side: int                          # 1 long, -1 short
    stop: float                        # the live stop
    reclaim_level: float = None        # the level the setup reclaimed (AVWAP / EMA / range high); day-0 cut uses it
    group: str = ""
    setup: str = ""
    entry: float = 0.0
    shares: int = 0                    # open now
    shares0: int = 0                   # at entry
    risk: float = 0.0                  # R per share = |entry - initial stop|
    opened: str = ""
    sessions: int = 0                  # daily closes since the entry
    trimmed: bool = False
    financed: bool = False
    be_done: bool = False
    closes_over: int = 0
    exit_mode: str = "steady"          # "fast" (10 EMA) or "steady" (21 EMA)
    trim_sent: bool = False
    watch_close: bool = False
    exit_next_open: bool = False
    extension_next_open: bool = False
    exits_sent: set = field(default_factory=set)
    fills: list = field(default_factory=list)     # (tag, qty, price)
    stopped: bool = False

    @property
    def closed(self) -> bool:
        return self.shares0 > 0 and self.shares <= 0

    @property
    def close_side(self) -> str:
        return "SELL" if self.side > 0 else "BUY"

    def r_now(self, price: float) -> float:
        return (price - self.entry) * self.side / self.risk if self.risk > 0 else 0.0

    def r_result(self) -> float:
        """the whole trade's result in R (the initial risk on the initial size)"""
        if not self.shares0 or self.risk <= 0:
            return 0.0
        pnl = sum(q * (p - self.entry) * self.side for _, q, p in self.fills)
        return pnl / (self.risk * self.shares0)


class TradeManager:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    # ---- entry ------------------------------------------------------------------------------------------------
    def entry_orders(self, t: Trade, trigger: float, shares: int, adr_pct: float) -> list:
        """a stop-limit entry at `trigger` (no chasing more than 0.1 ADR past it) with its stop attached"""
        lim = trigger * (1 + t.side * 0.1 * adr_pct / 100)
        open_side = "BUY" if t.side > 0 else "SELL"
        return [Action(open_side, t.symbol, shares, "STP LMT", price=round(lim, 2), stop=round(trigger, 2), tag="entry",
                       reason=f"{t.setup}: trigger {trigger:.2f}, limit {lim:.2f}"),
                Action(t.close_side, t.symbol, shares, "STP", stop=round(t.stop, 2), tag="stop", reason="the initial stop, at IBKR")]

    def on_entry_fill(self, t: Trade, price: float, qty: int, date: str) -> list:
        t.entry, t.shares, t.shares0, t.opened = price, qty, qty, date
        t.risk = abs(price - t.stop)
        t.fills = []
        return []

    # ---- intraday ---------------------------------------------------------------------------------------------
    def on_price(self, t: Trade, price: float) -> list:
        c = self.cfg
        if t.closed or t.trimmed or t.trim_sent:
            return []
        if t.r_now(price) >= c.trim_at_r:
            q = max(1, int(round(t.shares0 * c.trim_frac)))
            t.trim_sent = True
            return [Action(t.close_side, t.symbol, q, "LMT", price=round(price, 2), tag="trim",
                           reason=f"+{t.r_now(price):.1f}R: sell {int(100 * c.trim_frac)}% to finance the stop")]
        return []

    def on_fill(self, t: Trade, tag: str, qty: int, price: float, history: dict = None) -> list:
        """an exit order filled. history (for the trim): {"closes": [...], "ema_fast": [...], "ema21": [...], "adr_pct": x}
        up to yesterday, to decide fast or steady"""
        c = self.cfg
        t.fills.append((tag, qty, price))
        t.shares -= qty
        if tag == "stop":
            t.stopped = not t.trimmed and not t.be_done
            return []
        if t.shares <= 0:
            return [Action("CANCEL", t.symbol, 0, tag="stop", reason="flat: cancel the resting stop")]
        out = []
        if tag == "trim":
            t.trimmed = True
            new = t.entry if c.stop_after_trim == "breakeven" else financed_stop(t.entry, t.stop, qty / t.shares0, price, t.side)
            if (new - t.stop) * t.side > 0:
                t.stop = new
            t.financed = True
            if history:
                t.exit_mode = "fast" if is_fast_leader(c, history["closes"], history["ema_fast"], history["ema21"], history["adr_pct"]) else "steady"
            out.append(Action("MODIFY_STOP", t.symbol, t.shares, "STP", stop=round(t.stop, 2), tag="stop",
                              reason=f"financed: stop {t.stop:.2f} ({t.r_now(t.stop):+.2f}R) on the {t.shares} left; "
                                     f"core trails the {'10' if t.exit_mode == 'fast' else '21'} EMA close"))
        else:
            out.append(Action("MODIFY_STOP", t.symbol, t.shares, "STP", stop=round(t.stop, 2), tag="stop",
                              reason=f"{tag}: the stop now covers the {t.shares} left"))
        return out

    # ---- around the close ---------------------------------------------------------------------------------------
    def line_ema(self, t: Trade) -> int:
        return self.cfg.fast_ema if t.exit_mode == "fast" else self.cfg.steady_ema

    def on_close_check(self, t: Trade, price: float, prev_ema_fast: float, prev_ema21: float, adr_pct: float,
                       day0: bool) -> list:
        """15:47 ET: the daily-close trail and the day-0 cut, sent as market-on-close orders"""
        c = self.cfg
        if t.closed or "trail" in t.exits_sent:
            return []
        if day0 and c.day0_cut and t.r_now(price) < 0 and (t.reclaim_level is None or (price - t.reclaim_level) * t.side < 0):
            t.exits_sent.add("trail")
            return [Action(t.close_side, t.symbol, t.shares, "MOC", tag="day0",
                           reason="day 0: under the entry and the reclaimed level at the close (Luk's losers last half a day)")]
        n = self.line_ema(t)
        line = ema_today(prev_ema_fast if n == c.fast_ema else prev_ema21, price, n)
        gap = (line - price) * t.side
        buf = c.trail_buffer_adr * adr_pct / 100 * price
        if gap > buf:
            t.exits_sent.add("trail")
            return [Action(t.close_side, t.symbol, t.shares, "MOC", tag="trail",
                           reason=f"closing under its {n} EMA {line:.2f} (price {price:.2f})")]
        t.watch_close = gap > -buf
        return []

    def on_daily_close(self, t: Trade, close: float, ema_fast: float, ema21: float, adr_pct: float) -> list:
        """after the official close (today's EMAs included)"""
        c = self.cfg
        if t.closed:
            return []
        t.sessions += 1
        out = []
        n = self.line_ema(t)
        line = ema_fast if n == c.fast_ema else ema21
        if t.watch_close and (close - line) * t.side < 0:
            t.exit_next_open = True
        t.watch_close = False
        if t.trimmed and not t.be_done and c.stop_after_trim != "breakeven":
            if t.r_now(close) >= c.be_after_closes_over_r:
                t.closes_over += 1
            if t.closes_over >= c.be_after_n_closes and (t.entry - t.stop) * t.side > 0:
                t.stop, t.be_done = t.entry, True
                out.append(Action("MODIFY_STOP", t.symbol, t.shares, "STP", stop=round(t.stop, 2), tag="ratchet",
                                  reason=f"{c.be_after_n_closes} closes over +{c.be_after_closes_over_r}R: stop to breakeven"))
        if c.extension_sell_frac > 0 and (close - ema_fast) * t.side >= c.extension_adr * adr_pct / 100 * close:
            t.extension_next_open = True
        return out

    def on_next_open(self, t: Trade, range_low: float, range_high: float, price: float) -> list:
        """after the first 5 minutes of the session: the exits decided at yesterday's close"""
        c = self.cfg
        out = []
        if t.closed:
            return out
        if t.exit_next_open:
            t.exit_next_open = False
            lvl = range_low if t.side > 0 else range_high
            out.append(Action(t.close_side, t.symbol, t.shares, "STP", stop=round(lvl, 2), tag="next_open", deadline="10:00",
                              reason=f"closed under its {self.line_ema(t)} EMA: out on the 5-minute range break, or by 10:00"))
        if t.extension_next_open:
            t.extension_next_open = False
            q = int(t.shares * c.extension_sell_frac)
            if q > 0:
                out.append(Action(t.close_side, t.symbol, q, "LMT", price=round(price, 2), tag="extension",
                                  reason=f"{c.extension_adr}+ ADRs over the {c.fast_ema} EMA: sell into strength"))
        return out

    def on_event_eve(self, t: Trade, kind: str) -> list:
        """the session before earnings ("earnings") or a macro event ("event"): cut an unfinanced position"""
        c = self.cfg
        if t.closed or t.financed or kind in t.exits_sent:
            return []
        keep = c.earnings_keep_frac_unfinanced if kind == "earnings" else c.event_cut_frac_unfinanced
        q = t.shares - int(t.shares0 * keep)
        if q <= 0:
            return []
        t.exits_sent.add(kind)
        return [Action(t.close_side, t.symbol, q, "MOC", tag=kind,
                       reason=f"{kind} next session and not financed: cut to {int(100 * keep)}%")]
