#!/usr/bin/env python3
"""The user's 1-hour 21 EMA pullback test (Nov 1 2026).

  python3 scanner/probe_pb1h.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json
  (needs ALPACA_KEY_ID / ALPACA_SECRET: 30-minute bars for the 1-hour 21 EMA, 5-minute bars for the trade)

  stocks    liquid ($10+, $20M+ and 600K+ shares a day) with an ADR of 4%+
  uptrend   daily 10 EMA > 21 EMA > 50 EMA, a new 20-day high within the last 10 sessions (still advancing), at
            most 50% over the 200 SMA
  setup     a day that closes under the 1-hour 21 EMA (regular session; 1-hour bars built from 30-minute bars:
            9:30-10:30 ... 15:30-16:00); the next day gaps up (any size) and its 5-minute opening range stays above
            that 1-hour 21 EMA (its low over it)
  entry     the break of the 5-minute opening range high (at that high, or the bar's open when it jumps over it);
            the stop at the opening range low = 1R
  manage    +2R: the stop to breakeven; +3R: sell 1/3; +5R: sell 1/3; the rest runs until a daily close under the
            21 EMA (whatever is still open, at any time) or the breakeven stop. A 5-minute bar or a day that touches
            both a stop and a target counts the stop first
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
        for i in range(max(a.start, first), c.size - 1):
            if not (a.liq_noadr[i] and st.adr[i] >= 4 and a.e10[i] > a.e21[i] > a.e50[i] and c[i] <= 1.5 * a.s200[i]):
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


def hourly_ema(rows):
    """{date: (the day's last 1-hour close, the 1-hour 21 EMA at the close)} from 30-minute bars, regular session"""
    hours = []                                              # (date, hour index, close)
    for b in rows:
        t = datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(pc.NY)
        mins = t.hour * 60 + t.minute
        if not 570 <= mins < 960:
            continue
        hi = (mins - 570) // 60                             # 9:30-10:30 = 0 ... 15:30-16:00 = 6
        key = (t.date().isoformat(), hi)
        if hours and hours[-1][:2] == key:
            hours[-1] = (key[0], hi, b["c"])
        else:
            hours.append((key[0], hi, b["c"]))
    out, e, k = {}, None, 2 / 22
    for d, hi, c in hours:
        e = c if e is None else e + k * (c - e)
        out[d] = (c, e)
    return out


def trade(a, k, b5, ema):
    """the trade on day k from its 5-minute bars b5, None when the opening range isn't above the 1-hour 21 EMA"""
    st, c, o, h, l, e21 = a.st, a.st.c, a.st.o, a.st.h, a.st.l, a.e21
    orh, orl = b5[0]["h"], b5[0]["l"]
    if not orl > ema:
        return None
    m = next((x for x in range(1, len(b5)) if b5[x]["h"] > orh), None)
    t = dict(broke=m is not None, gap=float(100 * (o[k] / c[k - 1] - 1)), cushion_adr=float(100 * (orl / ema - 1) / st.adr[k - 1]))
    if m is None:
        return t
    buy = max(orh, b5[m]["o"])
    R = buy - orl
    if R <= 0:
        return None
    stop, left, got, be = orl, 1.0, 0.0, False
    t2, t3, t5 = buy + 2 * R, buy + 3 * R, buy + 5 * R
    sold3 = sold5 = False
    hit = {"2R": False, "3R": False, "5R": False}
    end_j, how = k, None

    def step(bo, bh, bl):
        nonlocal stop, left, got, sold3, sold5, be, how
        if bl <= stop:                                      # the stop first
            px = min(stop, bo)
            got += left * px
            left = 0.0
            how = "breakeven" if be else "stop"
            return True
        if bh >= t2:
            hit["2R"] = True
        if bh >= t3 and not sold3:
            got += max(t3, bo) / 3; left -= 1 / 3; sold3 = hit["3R"] = True
        if bh >= t5 and not sold5:
            got += max(t5, bo) / 3; left -= 1 / 3; sold5 = hit["5R"] = True
        if hit["2R"] and not be:
            stop, be = max(stop, buy), True                 # from the next bar
        return False
    done = False
    for x in b5[m:]:
        if step(x["o"] if x is not b5[m] else buy, x["h"], x["l"]):
            done = True
            break
    if not done and c[k] < e21[k]:
        got += left * c[k]; left = 0.0; how = "21 EMA close"; done = True
    if not done:
        for j in range(k + 1, c.size):
            end_j = j
            if step(o[j], h[j], l[j]):
                done = True
                break
            if c[j] < e21[j]:
                got += left * c[j]; left = 0.0; how = "21 EMA close"; done = True
                break
        if not done:
            got += left * c[-1]; left = 0.0; how = "open at the end"
    ret = 100 * (got / buy - 1)
    t.update(ret=ret, R=(got - buy) / R, risk=100 * R / buy, days=end_j - k, how=how, same_day=end_j == k and how in ("stop", "breakeven"),
             r2=hit["2R"], r3=hit["3R"], r5=hit["5R"], mg=float(100 * (h[k:end_j + 1].max() / buy - 1)))
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
    EM = {s: hourly_ema(b30.get(pc.alp(s), [])) for s in syms}
    setups = []
    for s, i in cand:
        d = A[s].st.dates[i]
        x = EM[s].get(d)
        if x and x[0] < x[1]:                              # the day closed under the 1-hour 21 EMA
            setups.append((s, i, x[1]))
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
            t = trade(A[s], i + 1, b, e)
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
