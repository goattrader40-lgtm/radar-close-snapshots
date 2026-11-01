#!/usr/bin/env python3
"""The user's 1-hour 21 EMA pullback test (Nov 1 2026).

  python3 scanner/probe_pb1h.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json
  (needs ALPACA_KEY_ID / ALPACA_SECRET: 30-minute bars for the 1-hour 21 EMA, 5-minute bars for the trade)

  stocks    $10+, a 20-day average of $30M+ and 700K+ shares a day, a market cap of $700M+, an ADR of 4%+, over the 200
            SMA, 30%+ over the 52-week low
  uptrend   daily 10 EMA > 21 EMA > 50 EMA, a new 20-day high within the last 10 sessions (still advancing), at
            most 50% over the 200 SMA
  setup     a day that closes under the 1-hour 21 EMA (regular session; 1-hour bars built from 30-minute bars:
            9:30-10:30 ... 15:30-16:00); the next day gaps up (any size) and its 5-minute opening range stays above
            that 1-hour 21 EMA (its low over it)
  entry     the break of the 5-minute opening range high (at that high, or the bar's open when it jumps over it);
            the stop at the opening range low = 1R
  manage    +2R: the stop to breakeven; +3R: sell 1/3; +5R: sell 1/3; the runners out on a daily close under the daily
            21 EMA or the breakeven stop, whichever comes first (that daily close closes whatever is open, at any time). Followed on the 5-minute bars the entry day, the 1-hour bars after; a bar that
            touches both a stop and a target counts the stop first
"""
import argparse, collections, datetime, json, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402
import probe_catalyst as pc  # noqa: E402  (Alpaca helpers)


def candidates(A, first):
    """(sym, i) with the daily conditions on day i and a gap up on day i + 1"""
    out = []
    for s, a in A.items():
        st = a.st
        c, h, o = st.c, st.h, st.o
        av20, dv20 = launch.roll_mean(st.v, 20), launch.roll_mean(c * st.v, 20) / 1e6
        for i in range(max(a.start, first), c.size - 1):
            if not (c[i] >= 10 and av20[i] >= 700000 and dv20[i] >= 30 and st.adr[i] >= 4 and a.e10[i] > a.e21[i] > a.e50[i] and a.s200[i] < c[i] <= 1.5 * a.s200[i]
                    and c[i] >= st.low52[i] * 1.3):                # the standard: over the 200 SMA, 30%+ over the 52-week low
                continue
            if int(np.argmax(h[i - 19:i + 1])) < 10:          # the 20-day high made within the last 10 sessions
                continue
            if o[i + 1] > c[i]:
                out.append((s, i))
    return out


def bars(syms, start, end, tf):
    """{symbol: [bar]} from Alpaca for these symbols between two NY datetimes"""
    out = collections.defaultdict(list)
    for c0 in range(0, len(syms), 50):
        q = {"symbols": ",".join(pc.alp(s) for s in syms[c0:c0 + 50]), "timeframe": tf, "feed": "sip", "adjustment": "split",
             "limit": 10000, "start": pc.iso(start), "end": pc.iso(end)}
        while True:
            res = pc.get("https://data.alpaca.markets/v2/stocks/bars", q)
            for s, rows in (res.get("bars") or {}).items():
                out[s].extend(rows)
            if not res.get("next_page_token"):
                break
            q["page_token"] = res["next_page_token"]
        pc.time.sleep(0.3)
    return out


def hourly(rows):
    """{date: [1-hour bar dict(i, o, h, l, c, ema)]} from 30-minute bars, regular session (9:30-10:30 ... 15:30-16:00),
    the 1-hour 21 EMA after each close"""
    hours = []
    for b in rows:
        t = datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(pc.NY)
        mins = t.hour * 60 + t.minute
        if not 570 <= mins < 960:
            continue
        key = (t.date().isoformat(), (mins - 570) // 60)
        if hours and hours[-1]["key"] == key:
            x = hours[-1]
            x.update(h=max(x["h"], b["h"]), l=min(x["l"], b["l"]), c=b["c"])
        else:
            hours.append(dict(key=key, o=b["o"], h=b["h"], l=b["l"], c=b["c"]))
    out, e, k = collections.defaultdict(list), None, 2 / 22
    for x in hours:
        e = x["c"] if e is None else e + k * (x["c"] - e)
        out[x["key"][0]].append(dict(i=x["key"][1], o=x["o"], h=x["h"], l=x["l"], c=x["c"], ema=e))
    return out


def trade(a, k, b5, ema, H, entry=None):
    """the trade on day k from its 5-minute bars b5 (H = the stock's 1-hour bars by date); None when the opening range
    isn't above the 1-hour 21 EMA of the day before's close"""
    st, c, o, h, l, e21 = a.st, a.st.c, a.st.o, a.st.h, a.st.l, a.e21
    orh, orl = b5[0]["h"], b5[0]["l"]
    if not orl > ema:
        return None
    m = next((x for x in range(1, len(b5)) if b5[x]["h"] > orh), None) if entry is None else entry[0]
    t = dict(broke=m is not None, gap=float(100 * (o[k] / c[k - 1] - 1)), cushion_adr=float(100 * (orl / ema - 1) / st.adr[k - 1]))
    if m is None:
        return t
    buy = max(orh, b5[m]["o"]) if entry is None else entry[1]       # entry = (bar, price) given by the caller
    R = buy - orl
    if R <= 0:
        return None
    S = dict(stop=orl, left=1.0, got=0.0, be=False, sold3=False, sold5=False, how=None, r2=False)
    t2, t3, t5 = buy + 2 * R, buy + 3 * R, buy + 5 * R

    def out(px, how):
        S["got"] += S["left"] * px
        S["left"] = 0.0
        S["how"] = how
        return True

    def step(bo, bh, bl):
        if bl <= S["stop"]:                                 # the stop first
            return out(min(S["stop"], bo), "breakeven" if S["be"] else "stop")
        if bh >= t2:
            S["r2"] = True
        if bh >= t3 and not S["sold3"]:
            S["got"] += max(t3, bo) / 3; S["left"] -= 1 / 3; S["sold3"] = True
        if bh >= t5 and not S["sold5"]:
            S["got"] += max(t5, bo) / 3; S["left"] -= 1 / 3; S["sold5"] = True
        if S["r2"] and not S["be"]:
            S["stop"], S["be"] = max(S["stop"], buy), True
        return False

    def hour_exit(x):                                       # no 1-hour exit: the runners go on the daily 21 EMA close
        return False

    hk = {x["i"]: x for x in H.get(st.dates[k], [])}
    end_j, done = k, False
    for n, x in enumerate(b5[m:], m):
        if step(buy if n == m else x["o"], x["h"], x["l"]):
            done = True; break
        tt = datetime.datetime.fromisoformat(x["t"].replace("Z", "+00:00")).astimezone(pc.NY)
        end = tt.hour * 60 + tt.minute + 5 - 570                          # minutes from 9:30 at this bar's end
        hi = end // 60 - 1 if end % 60 == 0 else 6 if end >= 390 else None   # it closes a 1-hour bar
        if hi is not None and hi in hk and hour_exit(hk[hi]):
            done = True; break
    if not done and c[k] < e21[k]:
        done = out(c[k], "daily 21 EMA close")
    j = k + 1
    while not done and j < c.size:
        end_j = j
        hb = H.get(st.dates[j])
        if hb:
            for x in hb:
                if step(x["o"], x["h"], x["l"]) or hour_exit(x):
                    done = True; break
        elif step(o[j], h[j], l[j]):
            done = True
        if not done and c[j] < e21[j]:
            done = out(c[j], "daily 21 EMA close")
        j += 1
    if not done:
        out(c[-1], "open at the end")
    ret = 100 * (S["got"] / buy - 1)
    t.update(ret=ret, R=(S["got"] - buy) / R, risk=100 * R / buy, days=end_j - k, how=S["how"],
             same_day=end_j == k and S["how"] in ("stop", "breakeven"), r2=S["r2"], r3=S["sold3"], r5=S["sold5"],
             mg=float(100 * (h[k:end_j + 1].max() / buy - 1)))
    return t


def summ(ts):
    tr = [t for t in ts if t and t.get("broke")]
    if not tr:
        return dict(setups=len(ts), trades=0)
    ret, R = np.array([t["ret"] for t in tr]), np.array([t["R"] for t in tr])
    hows = collections.Counter(t["how"] for t in tr)
    return dict(setups=len(ts), broke_orh_pct=round(100 * len(tr) / len(ts)), trades=len(tr),
                win=round(100 * float(np.mean(ret > 0))), avg_pct=round(float(ret.mean()), 2), med_pct=round(float(np.median(ret)), 2),
                avg_R=round(float(R.mean()), 2), med_R=round(float(np.median(R)), 2), total_R=round(float(R.sum()), 1),
                reached_2R=round(100 * float(np.mean([t["r2"] for t in tr]))), reached_3R=round(100 * float(np.mean([t["r3"] for t in tr]))),
                reached_5R=round(100 * float(np.mean([t["r5"] for t in tr]))),
                stopped_same_day=round(100 * float(np.mean([t["same_day"] for t in tr]))),
                exits={k: round(100 * v / len(tr)) for k, v in hows.items()},
                risk_med_pct=round(float(np.median([t["risk"] for t in tr])), 2), days_med=int(np.median([t["days"] for t in tr])),
                ran20=round(100 * float(np.mean([t["mg"] >= 20 for t in tr]))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    first = 200
    cand = candidates(A, first)
    syms = sorted({s for s, i in cand})
    print(len(cand), "daily candidates in", len(syms), "stocks")
    # the 1-hour 21 EMA: 30-minute bars from 15 sessions before the window
    t0 = datetime.datetime.fromisoformat(cal[first - 15] + "T09:30").replace(tzinfo=pc.NY)
    t1 = datetime.datetime.fromisoformat(cal[-1] + "T16:00").replace(tzinfo=pc.NY)
    b30 = bars(syms, t0, t1, "30Min")
    HB = {s: hourly(b30.get(pc.alp(s), [])) for s in syms}
    del b30
    setups = []
    for s, i in cand:
        d = A[s].st.dates[i]
        x = HB[s].get(d)
        if x and x[-1]["i"] == 6 and x[-1]["c"] < x[-1]["ema"]:   # the day closed under the 1-hour 21 EMA
            setups.append((s, i, x[-1]["ema"]))
    print(len(setups), "setups (closed under the 1-hour 21 EMA, gap up the next day)")
    by_day = collections.defaultdict(list)
    for s, i, e in setups:
        by_day[A[s].st.dates[i + 1]].append((s, i, e))
    ts = []
    for d, rs in sorted(by_day.items()):
        t0 = datetime.datetime.fromisoformat(d + "T09:30").replace(tzinfo=pc.NY)
        b5 = bars(sorted({s for s, i, e in rs}), t0, t0 + datetime.timedelta(minutes=390), "5Min")
        for s, i, e in rs:
            b = b5.get(pc.alp(s))
            if not b or not b[0]["t"].startswith(pc.iso(t0)[:16]):
                continue
            t = trade(A[s], i + 1, b, e, HB[s])
            if t is not None:
                t.update(sym=s, date=d)
                ts.append(t)
    out = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), first=cal[first], last=cal[-1],
               daily_candidates=len(cand), setups=len(setups), with_opening_range_over_the_ema=len(ts),
               all=summ(ts),
               by_gap={k: summ([t for t in ts if f(t["gap"])]) for k, f in (("gap under 1%", lambda g: g < 1), ("gap 1-3%", lambda g: 1 <= g < 3),
                                                                            ("gap 3-6%", lambda g: 3 <= g < 6), ("gap 6%+", lambda g: g >= 6))},
               by_cushion={k: summ([t for t in ts if f(t["cushion_adr"])]) for k, f in (("opening range low within 0.5 ADR over the EMA", lambda x: x < 0.5),
                                                                                       ("0.5-1 ADR over", lambda x: 0.5 <= x < 1), ("1+ ADR over", lambda x: x >= 1))},
               examples=[{k: (round(v, 2) if isinstance(v, float) else v) for k, v in t.items()} for t in ts if t.get("broke")][-30:])
    json.dump(out, open(a_.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "examples"}, indent=1))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        json.dump(dict(error=traceback.format_exc()[-3000:]), open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
        raise
