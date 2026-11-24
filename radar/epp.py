#!/usr/bin/env python3
"""EP pullbacks: the first touch of the rising 10 / 21 EMA after an episodic pivot, bought on the 15-minute reclaim (the
user, Nov 23 2026: "we should get alert when its ready ... then when its in true state it could alert, buy point
confirmed"; "it has to say in alert message ep pullback buy 10 ema"). The rules come from the EP study of Nov 21-23 2026
(Jan 2023 - Nov 2026, 1-minute SIP bars, the 2022 bear market left out; the playbook's plays 4 and 3b):

  10 EMA (play 4)  the EP day (the 1-EP/GAP rule, gap at most 20%) up to 10 sessions back; since then no daily close more
                   than 5% under the EP day's close; today is the first touch of the 10 EMA (today's low at or under its
                   value at the last close), the EMA rising at the last close.
                   READY = touched it AND traded under the EP day's close (the dip; without it: 64 trades, -28R).
                   BUY   = the first 15-minute candle from READY on that closes over the 10 EMA and VWAP, not more than 5%
                           under the EP day's close: 268 trades, 29% won, +0.70R a trade, +187R, worst drop 24R
                           (5-minute candles: +0.58R; 1-minute: +0.33R; without VWAP: +0.37R).
  21 EMA (play 3b) the EP day up to 15 sessions back (30 until Nov 24 2026); since then never under the EP day's low; today
                   is the first touch of the 21 EMA, rising at the last close and not in the bottom quarter of the EP
                   day's range (its low to its close).
                   READY = touched it, today's low still over the EP day's low.
                   BUY   = the first 15-minute candle from READY on that closes over the 21 EMA and VWAP with today's low
                           still over the EP day's low. Under the EP day's low first: no buy (not part of the rule).
                   The two filters of Nov 24 2026 (the user, YOU Nov 23 2026: the 21 EMA 52.39 just over the EP low
                   51.27, "since the episodic pivot day this was just breaking down"), replayed Jan 2023 - Nov 2026:
                     the 21 EMA in the bottom quarter of the EP day's range: 225 touches, 30 trades, +2R        -> no trade
                     a touch in sessions 16-30: 121 trades, 17% won, -2R (16-20: -31R, a loss on every day)     -> no trade
                     what is left: 105 trades, 35% won, +1.63R, +171R, worst drop 16R (before: 254 trades, 25% won,
                     +0.68R, +174R, worst drop 35R; the study's own count was 276 trades, +0.62R, +171R).
                   The evening scan applies both (setups/ep_pullback.json: status "low" / "late"); this module's check()
                   is unchanged.
  Stop = today's low at the buy. Exits: 1/3 at +10%, the rest breakeven, then a daily close under the 21 EMA.
  The last candle (3:45-4:00 PM) is no buy (the study's: that is a buy at the close).

The evening list is scanner/launch.py write_ep_pullback (setups/ep_pullback.json); radar/alerts.py find_epp reads it with
today's 1-minute chart; this module is the rule both the alerts and the tests use."""

CANDLE = 15          # minutes of the confirming candle (the user's choice after the test: 15)
LAST_WINDOW = 25     # 15-minute windows in a session (9:30-4:00 = 26); the 26th (3:45-4:00) is no buy


def vwap_lows(bars):
    """today's VWAP and lowest low up to each 1-minute bar (bars: [(minute after 9:30, o, h, l, c, v)], sorted)"""
    cv = cpv = 0.0
    vw, lows, lo = [], [], float("inf")
    for m, o, h, l, c, v in bars:
        cv += v
        cpv += v * (h + l + c) / 3
        vw.append(cpv / cv if cv else c)
        lo = min(lo, l)
        lows.append(lo)
    return vw, lows


def check(bars, play, level, c0, l0, floor=None, now_min=None, candle=CANDLE):
    """the state of one EP pullback today from its 1-minute bars.
    play "10" or "21"; level = the EMA's value at the last close; c0 / l0 = the EP day's close / low; floor = the lowest buy
    (play 10: 5% under c0); now_min = minutes since 9:30 now (None = the whole day is known: the tests).
    Returns {"ready": (minute, low so far) | None, "buy": (candle end minute, price, stop, vwap, candle start minute) | None,
    "off": True when the 21 EMA play broke the EP day's low before a buy, "low": today's low so far, "vwap": the latest VWAP}"""
    bars = sorted(b for b in bars if b and b[0] is not None and 0 <= b[0] < 390)
    out = {"ready": None, "buy": None, "off": False, "low": None, "vwap": None}
    if not bars:
        return out
    if now_min is not None:                      # only finished minutes
        bars = [b for b in bars if b[0] < now_min]
        if not bars:
            return out
    vw, lows = vwap_lows(bars)
    out["low"], out["vwap"] = lows[-1], vw[-1]
    jt = next((j for j, b in enumerate(bars) if b[3] <= level), None)          # the touch
    if jt is None:
        return out
    if play == "10":
        jd = next((j for j, b in enumerate(bars) if b[3] < c0), None)          # the dip under the EP day's close
        if jd is None:
            return out
        j0 = max(jt, jd)
    else:
        j0 = jt
        if lows[j0] < l0:                                                       # touched only after breaking the EP low
            out["off"] = True
            return out
    out["ready"] = (bars[j0][0], lows[j0])
    # the 15-minute windows that ended (now_min) and whose last bar is at or after READY
    last = {}
    for j, b in enumerate(bars):
        last[b[0] // candle] = j
    for w in sorted(last):
        if w >= LAST_WINDOW:
            break
        end = (w + 1) * candle
        if now_min is not None and now_min < end:
            break
        j = last[w]
        if j < j0:
            continue
        c = bars[j][4]
        if play == "21" and lows[j] < l0:
            out["off"] = True
            return out
        if c > level and c > vw[j] and c > lows[j] and (floor is None or c >= floor):
            out["buy"] = (end, c, lows[j], vw[j], w * candle)
            return out
    if play == "21" and lows[-1] < l0:
        out["off"] = True
    return out


def hhmm(minute):
    """minutes after 9:30 -> "10:30" """
    t = 570 + minute
    return f"{t // 60:02d}:{t % 60:02d}"
