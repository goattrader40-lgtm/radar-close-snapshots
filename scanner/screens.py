"""Your TradingView screeners, computed from daily bars.

TradingView wording → test used here (price = today's close):
  'X below Price by a% or more'   →  X <= price × (1 − a/100)
  'X below Price by 0% to b%'     →  price × (1 − b/100) <= X <= price
  'X above Price by 0% to b%'     →  price <= X <= price × (1 + b/100)
  Rel vol                          →  today's volume ÷ average of the previous 10 days
  Perf 1W / 1M / 3M / 6M / 1Y      →  close vs the close 5 / 21 / 63 / 126 / 252 bars ago
  Avg vol 30D                      →  average volume of the last 30 days, today included
"""
import numpy as np

import msf


def roll_mean(x, n):
    out = np.full(x.size, np.nan)
    c = np.cumsum(np.insert(x, 0, 0.0))
    out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def roll_ext(x, n, fn):
    out = np.full(x.size, np.nan)
    for i in range(x.size):
        out[i] = fn(x[max(0, i - n + 1):i + 1])
    return out


class Stock:
    """Everything the screeners and lists need for one symbol, for every bar."""

    def __init__(self, sym, bars, bench, p, mcap, exchange=None):
        self.sym, self.mcap, self.exchange = sym, mcap, exchange
        self.dates = [b[0] for b in bars]
        self.pos = {d: k for k, d in enumerate(self.dates)}
        self.df = msf.run_symbol(bars, bench, p)
        d = self.df
        self.o, self.h, self.l, self.c, self.v = (d[k].to_numpy() for k in ("open", "high", "low", "close", "volume"))
        self.ema21, self.ema50, self.sma200, self.adr = (d[k].to_numpy() for k in ("ema21", "ema50", "sma200", "adr"))
        self.avgv30 = roll_mean(self.v, 30)
        self.dv30 = self.c * self.avgv30 / 1e6
        prev10 = np.full(self.v.size, np.nan)
        prev10[1:] = roll_mean(self.v, 10)[:-1]
        with np.errstate(divide="ignore", invalid="ignore"):
            self.relvol = self.v / prev10
        rng = self.h - self.l
        self.rng_avg10_prev = np.full(rng.size, np.nan)   # average day range of the previous 10 days
        self.rng_avg10_prev[1:] = roll_mean(rng, 10)[:-1]
        self.low52 = roll_ext(self.l, 252, np.min)
        self.high52 = roll_ext(self.h, 252, np.max)

    def perf(self, i, bars):
        return 100 * (self.c[i] / self.c[i - bars] - 1) if i - bars >= 0 else np.nan

    def standard(self, i, S):
        c = self.c[i]
        return bool(c >= S["min_price"] and S["min_mcap"] <= self.mcap <= S["max_mcap"]
                    and self.avgv30[i] > S["min_avg_vol_30d"] and self.dv30[i] > S["min_dollar_vol_30d_millions"]
                    and self.adr[i] >= S["min_adr"] and (not S["above_ema50"] or self.ema50[i] < c)
                    and c >= self.low52[i] * (1 + S["min_pct_above_52w_low"] / 100))

    def tight_day(self, k, t):
        """a quiet day: volume at least X% under the 30-day average and a narrow range (DAILY TIGHTNESS settings)"""
        if k < 1:
            return False
        ok = self.v[k] <= self.avgv30[k] * (1 - t["vol_below_avg30_pct"] / 100)
        if t.get("range_vs_avg10_max"):
            ok = ok and self.h[k] - self.l[k] <= t["range_vs_avg10_max"] * self.rng_avg10_prev[k]
        return bool(ok)

    def below50(self, i, n):
        """closed below the daily 50 EMA on each of the last n days"""
        return i - n + 1 >= 0 and all(self.c[k] < self.ema50[k] for k in range(i - n + 1, i + 1))

    def screens(self, i, cfg):
        """names of the screeners this stock passes today (standard filters included)"""
        S, X = cfg["standard"], cfg["screeners"]
        c = self.c[i]
        hits = []
        std = self.standard(i, S)
        if i < 2:
            return hits
        gap = 100 * (self.o[i] / self.c[i - 1] - 1)
        chg = 100 * (c / self.c[i - 1] - 1)
        if std and gap > X["EP-GAPUP-BREAKOUT"]["gap_pct"] and self.relvol[i] >= X["EP-GAPUP-BREAKOUT"]["rel_vol"]:
            hits.append("EP-GAPUP-BREAKOUT")
        if std and chg > X["HOTTEST STOCKS"]["chg_pct"] and self.relvol[i] > X["HOTTEST STOCKS"]["rel_vol"]:
            hits.append("HOTTEST STOCKS")
        nb = X["50 EMA FIRST CLOSE"]["closes_below_before"]
        if std and c > self.ema50[i] and self.below50(i - 1, nb):
            hits.append("50 EMA FIRST CLOSE")
        for name in ("MOMENTUM-1W", "MOMENTUM-1M", "MOMENTUM-3M", "MOMENTUM-6M"):
            m = X[name]
            ok = std and self.perf(i, m["bars"]) > m["perf_pct"]
            if ok and m.get("above_sma200"):
                ok = c > self.sma200[i]
            if ok and m.get("min_pct_above_52w_low"):
                ok = c >= self.low52[i] * (1 + m["min_pct_above_52w_low"] / 100)
            if ok:
                hits.append(name)
        t = X["DAILY TIGHTNESS"]
        n_need, n_look = t.get("min_tight_days", 1), t.get("within_last_days", 1)
        if std and c >= self.low52[i] * (1 + t["min_pct_above_52w_low"] / 100) and c >= self.high52[i] * (1 - t["max_pct_below_52w_high"] / 100) \
                and self.tight_day(i, t) and sum(self.tight_day(k, t) for k in range(max(0, i - n_look + 1), i + 1)) >= n_need:
            hits.append("DAILY TIGHTNESS")
        for name in ("PULLBACK TO 21EMA-MAIN", "PULLBACK TO 50EMA"):
            m = X[name]
            e = self.ema21[i] if m["ema"] == 21 else self.ema50[i]
            ok = std and c * (1 - m["max_above_ema_pct"] / 100) <= e <= c
            if ok and m.get("above_sma200"):
                ok = self.sma200[i] < c
            if ok and m.get("ema21_over_ema50"):
                ok = self.ema21[i] >= self.ema50[i]
            if ok:
                hits.append(name)
        return hits
