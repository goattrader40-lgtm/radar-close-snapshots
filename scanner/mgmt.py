"""The user's trade management (Nov 1 2026), shared by every test.

  targets   sell 1/3 when the price is 2 ADRs over the buy (the stock's ADR the day before), 1/3 at 5 ADRs
  stop      the entry stop; after the first 1/3 is sold, the rest at breakeven (from the next bar)
  runners   out on a daily close under the 10 EMA (a strong stock) or the 21 EMA: both tested (runner=10 / 21); that close
            takes whatever is still open, at any time
  order     a bar (5-minute, 1-minute or a day) that touches both the stop and a target counts the stop first
"""


def run(a, k, buy, stop, bars=None, same_day_high=None, runner=21):
    """the trade bought at `buy` on day k: on `bars` (the intraday bars from the buy's bar on) or, without them, the
    day's high for the targets (a stop under the day's low can't be hit that day); then day by day"""
    st = a.st
    c, o, h, l = st.c, st.o, st.h, st.l
    ema = a.e10 if runner == 10 else a.e21
    adr = float(st.adr[k - 1])
    t1, t2 = buy * (1 + 2 * adr / 100), buy * (1 + 5 * adr / 100)
    R = buy - stop
    S = dict(stop=stop, left=1.0, got=0.0, be=False, s1=False, s2=False, how=None)

    def out(px, how):
        S["got"] += S["left"] * px
        S["left"] = 0.0
        S["how"] = how
        return True

    def step(bo, bh, bl):
        if bl is not None and bl <= S["stop"]:
            return out(min(S["stop"], bo), "breakeven" if S["be"] else "stop")
        if bh >= t1 and not S["s1"]:
            S["got"] += max(t1, bo) / 3; S["left"] -= 1 / 3; S["s1"] = True
        if bh >= t2 and not S["s2"]:
            S["got"] += max(t2, bo) / 3; S["left"] -= 1 / 3; S["s2"] = True
        if S["s1"] and not S["be"]:
            S["stop"], S["be"] = max(S["stop"], buy), True
        return False
    done, end = False, k
    if bars:
        for n, x in enumerate(bars):
            if step(buy if n == 0 else x["o"], x["h"], x["l"]):
                done = True
                break
    elif same_day_high is not None:
        step(buy, same_day_high, None)
    if not done and c[k] < ema[k]:
        done = out(c[k], f"daily {runner} EMA close")
    j = k + 1
    while not done and j < c.size:
        end = j
        if step(o[j], h[j], l[j]):
            done = True
        elif c[j] < ema[j]:
            done = out(c[j], f"daily {runner} EMA close")
        j += 1
    if not done:
        out(c[-1], "open at the end")
    return dict(ret=100 * (S["got"] / buy - 1), R=(S["got"] - buy) / R if R > 0 else 0.0, risk=100 * R / buy, how=S["how"],
                days=end - k, t1=S["s1"], t2=S["s2"], same_day=end == k and S["how"] in ("stop", "breakeven"),
                mg=float(100 * (h[k:end + 1].max() / buy - 1)))


def cols(x, pre="", suf=""):
    """the result columns of a trade for the spreadsheet: risk %, result %, R, win, reached +2 / +5 ADR, exit"""
    return {f"{pre}risk_pct{suf}": round(x["risk"], 2), f"{pre}result_pct{suf}": round(x["ret"], 2), f"{pre}R{suf}": round(x["R"], 2),
            f"{pre}win{suf}": int(x["ret"] > 0), f"{pre}reached_2ADR{suf}": int(x["t1"]), f"{pre}reached_5ADR{suf}": int(x["t2"]),
            f"{pre}exit{suf}": x["how"]}


def sold_at_close(x, a, k, buy, risk_pct, why="sold at the close"):
    """the same buy sold at day k's close (a failed breakout / not a launch), unless already out that day; a +2 / +5 ADR
    target reached that day (its high) is sold there first"""
    if x["days"] == 0 and x["how"] in ("stop", "breakeven"):
        return x
    st = a.st
    adr = float(st.adr[k - 1])
    t1, t2, hi, px = buy * (1 + 2 * adr / 100), buy * (1 + 5 * adr / 100), float(st.h[k]), float(st.c[k])
    got, left = 0.0, 1.0
    if hi >= t1:
        got += t1 / 3; left -= 1 / 3
    if hi >= t2:
        got += t2 / 3; left -= 1 / 3
    got += left * px
    R = buy * risk_pct / 100
    return dict(x, ret=100 * (got / buy - 1), R=(got - buy) / R if R > 0 else 0.0, how=why, t1=hi >= t1, t2=hi >= t2, days=0)
