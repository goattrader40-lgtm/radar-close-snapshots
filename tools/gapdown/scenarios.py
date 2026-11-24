#!/usr/bin/env python3
"""The gap-down day's other shorts: the stock pops first, retests something, then drops (the user, Nov 24 2026: "sometimes
... they just pop it first, and kind of retest something, and then they drop it hard").

  python3 scenarios.py trades_out.json features.json OUT.json raw_gapdown_2023.json.gz [...]

Every stock-day of trades_out.json (the checked ones, open $10+ is applied later), read again minute by minute. 5-minute
candles and the session VWAP are built from the 1-minute bars. One trade per stock-day and scenario, the first signal
before 3:00 PM; out at the stop or the day's last price; R = (entry - exit) / (stop - entry).

  vwap    POP TO VWAP AND FAIL: after a leg down (a 5-minute close under VWAP and a low 1%+ under it) a 5-minute candle
          touches VWAP from below; that candle or one of the next two closes red and back under VWAP: short at that
          close, stop at the pop's high
  level   POP TO A BROKEN LEVEL AND FAIL: the gap opened 1%+ under a daily level (yesterday's low, the 21-day closing
          low, the 1-month low, the 50 EMA, the 200 SMA, yesterday's close); a 5-minute candle reaches it from below;
          that candle or one of the next two closes red and back under it: short at that close, stop at the pop's high
          (the nearest level over the open that gets retested first)
  orlre   RETEST OF THE OPENING LOW FROM BELOW: the 3-minute range low broke, the price went 1%+ under it, then a
          5-minute candle comes back to it; that candle or one of the next two closes red under it: short at that
          close, stop at the retest's high
  r2g     POP OVER THE OPEN, THEN LOSES IT: the price trades 1.5%+ over the 9:30 open, then a 5-minute candle closes back
          under the open: short at that close, stop at the day's high
  lod     BOUNCE, THEN A NEW LOW OF THE DAY: the low of the day holds 10+ minutes while the price bounces 1.5%+ off it,
          then that low breaks: short at the low (at the bar's open if it opens under it), stop at the bounce's high"""
import gzip, json, sys

HALF_DAYS = {"2023-07-03", "2023-11-24", "2024-07-03", "2024-11-29", "2024-12-24", "2025-07-03", "2025-11-28", "2025-12-24", "2026-07-02"}
LAST = 330                         # no new short from 3:00 PM
TOUCH, WAIT = 0.999, 2


def five(bs):
    """[(start minute, o, h, l, c, VWAP at its end, index of its last 1-minute bar)]"""
    out, cur, pv, vol = [], None, 0.0, 0.0
    for idx, b in enumerate(bs):
        pv += (b[2] + b[3] + b[4]) / 3 * b[5]
        vol += b[5]
        k = b[0] // 5 * 5
        if cur is None or cur[0] != k:
            if cur:
                out.append(tuple(cur))
            cur = [k, b[1], b[2], b[3], b[4], 0.0, idx]
        else:
            cur[2], cur[3], cur[4], cur[6] = max(cur[2], b[2]), min(cur[3], b[3]), b[4], idx
        cur[5] = pv / vol if vol else b[4]
    if cur:
        out.append(tuple(cur))
    return out


def result(bs, idx, m, entry, stop, at_close=True):
    """the trade from the 1-minute bar after idx (a short at a candle's close) or from idx itself (a stop order filled in it)"""
    if stop <= entry:
        return None
    exit_, stopped = bs[-1][4], 0
    if not at_close and bs[idx][2] >= stop:          # filled and stopped inside one minute: counted as stopped
        exit_, stopped = stop, 1
    else:
        for x in bs[idx + 1:]:
            if x[2] >= stop:
                exit_, stopped = max(x[1], stop), 1
                break
    t = 570 + m
    return {"t": f"{t // 60:02d}:{t % 60:02d}", "m": m, "entry": round(entry, 4), "stop": round(stop, 4), "exit": round(exit_, 4), "stopped": stopped,
            "r": round((entry - exit_) / (stop - entry), 4), "risk_pct": round((stop - entry) / entry * 100, 3)}


def reject(F, bs, i0, level_of, ready):
    """the first 5-minute candle from i0 that reaches its level from below (ready(i) says the set-up before it is there),
    then closes red back under it within WAIT candles: (candle index, the pop's high)"""
    hi, wait = None, 0
    for i in range(i0, len(F)):
        k, o, h, l, c, vw, idx = F[i]
        if k >= LAST:
            return None
        lv = level_of(i)
        if hi is None:
            if not (ready(i) and h >= lv * TOUCH and F[i - 1][4] < lv):
                continue
            hi, wait = h, 0
        else:
            hi, wait = max(hi, h), wait + 1
        if c < lv and c < o:
            return i, hi
        if wait >= WAIT:
            hi = None
    return None


def scenarios(bs, row, feat):
    F = five(bs)
    out = {}
    if len(F) < 6:
        return out
    k = row["scale"]
    op = bs[0][1]
    # ── vwap: a leg down first
    leg = [False] * len(F)
    under = dn = False
    for i, f in enumerate(F):
        leg[i] = under and dn                          # as of the candles before i
        under = under or f[4] < f[5]
        dn = dn or f[3] < f[5] * 0.99
    r = reject(F, bs, 2, lambda i: F[i][5], lambda i: leg[i])
    if r:
        i, hi = r
        out["vwap"] = result(bs, F[i][6], F[i][0] + 4, F[i][4], hi)
    # ── level: the nearest broken daily level 1%+ over the open that the pop reaches first
    if feat:
        levels = [(nm, feat[key] * k) for nm, key in (("yesterday's low", "plow"), ("21-day closing low", "clow21"), ("1-month low", "low21"),
                                                     ("50 EMA", "ema50"), ("200 SMA", "sma200"), ("yesterday's close", "pc")) if feat.get(key)]
        best = None
        for nm, lv in levels:
            if lv < op * 1.01:
                continue
            r = reject(F, bs, 1, lambda i, lv=lv: lv, lambda i: True)
            if r and (best is None or r[0] < best[0][0] or (r[0] == best[0][0] and lv < best[2])):
                best = (r, nm, lv)
        if best:
            (i, hi), nm, lv = best
            t = result(bs, F[i][6], F[i][0] + 4, F[i][4], hi)
            if t:
                t["level"], t["level_px"] = nm, round(lv, 4)
                out["level"] = t
    # ── orlre: the 3-minute range low broken, 1%+ under it, then retested from below
    tr = row.get("3")
    if tr and "m" in tr:
        rl, mb = tr["rlo"], tr["m"]
        i0 = next((i for i, f in enumerate(F) if f[0] > mb), None)
        if i0 is not None:
            deep = [False] * len(F)
            lo = min((b[3] for b in bs if b[0] >= mb and b[0] < F[i0][0]), default=rl)
            for i in range(i0, len(F)):
                deep[i] = lo <= rl * 0.99
                lo = min(lo, F[i][3])
            r = reject(F, bs, max(i0, 1), lambda i: rl, lambda i: deep[i])
            if r:
                i, hi = r
                out["orlre"] = result(bs, F[i][6], F[i][0] + 4, F[i][4], hi)
    # ── r2g: 1.5%+ over the open, then a 5-minute close back under the open
    popped, hi = False, bs[0][2]
    for i, f in enumerate(F):
        if f[0] >= LAST:
            break
        hi = max(hi, f[2])
        if not popped:
            popped = f[2] >= op * 1.015
            if not popped or i == 0:
                continue
        if f[4] < op and (i == 0 or F[i - 1][4] >= op or f[2] >= op):
            out["r2g"] = result(bs, f[6], f[0] + 4, f[4], hi)
            break
    # ── lod: the low of the day held 10+ minutes with a 1.5%+ bounce, then broken
    lod, t_lod, bh = bs[0][3], bs[0][0], bs[0][2]
    for j, b in enumerate(bs[1:], 1):
        if b[0] >= LAST:
            break
        if b[3] < lod:
            if b[0] - t_lod >= 10 and bh >= lod * 1.015:
                out["lod"] = result(bs, j, b[0], min(b[1], lod), bh, at_close=False)
                break
            lod, t_lod, bh = b[3], b[0], b[2]
        else:
            bh = max(bh, b[2])
    return {a: v for a, v in out.items() if v}


def main():
    rows = json.load(open(sys.argv[1]))["rows"]
    feats = json.load(open(sys.argv[2]))
    out = {}
    for path in sys.argv[4:]:
        d = json.load(gzip.open(path, "rt"))
        for key, bs in d["bars"].items():
            date, sym = key.split()
            key = f"{date} {sym.replace('.', '/')}"
            row = rows.get(key)
            if not row:
                continue
            bs = sorted(b for b in bs if b[0] < (210 if date in HALF_DAYS else 390))
            s = scenarios(bs, row, feats.get(key))
            if s:
                out[key] = s
    json.dump(out, open(sys.argv[3], "w"), separators=(",", ":"))
    import collections
    c = collections.Counter(a for v in out.values() for a in v)
    print("stock-days", len(rows), "| signals:", dict(c))


if __name__ == "__main__":
    main()
