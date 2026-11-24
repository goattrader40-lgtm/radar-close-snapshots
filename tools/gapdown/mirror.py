#!/usr/bin/env python3
"""The gap-down short study with the gap-up rules mirrored (the user, Nov 24 2026): yesterday vs the 50 EMA / 200 SMA, the
open vs the 1- / 3- / 6-month and 52-week lows and the 21-day closing low, the room down to the 3-month low.

  python3 mirror.py trades_out.json features.json gaps_clean.json

Same trades and rules as report.py (the stop 0.5%+ away, out at the stop or the day's last price)."""
import json, math, sys
feat_path, gaps_path = sys.argv[2], sys.argv[3]
sys.argv = sys.argv[:2]
import report as R
F = json.load(open(feat_path))
G = json.load(open(gaps_path))
MD = R.MARKET_DAYS


def tstat(ts):
    rs = [t[3]["r"] for t in ts]
    n = len(rs)
    m = sum(rs) / n
    sd = math.sqrt(sum((r - m) ** 2 for r in rs) / (n - 1))
    return m / (sd / math.sqrt(n)) if sd else 0


def show(label, ts):
    if len(ts) < 25:
        print(f"{label:<58} {len(ts)} trades")
        return
    s, y = R.stats(ts), R.years(ts)
    ex = R.stats([t for t in ts if t[0].split()[0] not in MD])
    print(f"{label:<58} {s['n']:>5} win {s['win']:>5.1f}% avg {s['avg']:>+6.3f}R total {s['total']:>+7.1f}R net {s['net_avg']:>+6.3f}R t {tstat(ts):>+5.2f} | "
          + "  ".join(f"{k[2:]}: {v['n']}/{v['avg']:+.2f}/{v['total']:+.0f}" for k, v in y.items())
          + (f" | ordinary {ex['n']}/{ex['win']}%/{ex['avg']:+.3f}/{ex['total']:+.0f}" if ex else ""))


def facts(key, row, tr):
    f, g = F.get(key), G.get(key)
    if not f or not g:
        return None
    o = g["o"]                                        # the official open, Yahoo's basis like the levels
    entry = tr["entry"] / row["scale"]
    d = {"u50": f["pc"] < f["ema50"], "u200": None if f["sma200"] is None else f["pc"] < f["sma200"],
         "o_u200": None if f["sma200"] is None else o < f["sma200"], "o_u50": o < f["ema50"],
         "o_u1m": o < f["low21"], "o_u3m": None if f["low63"] is None else o < f["low63"],
         "o_u6m": None if f["low126"] is None else o < f["low126"], "o_u52w": None if f["low252"] is None else o < f["low252"],
         "o_ucl21": o < f["clow21"], "room3m": None if f["low63"] is None else (entry / f["low63"] - 1) * 100,
         "off_high": (1 - f["pc"] / f["high252"]) * 100, "u21": f["pc"] < f["ema21"], "u10": f["pc"] < f["ema10"],
         "stack_dn": f["ema10"] < f["ema21"] < f["ema50"], "stack_up": f["ema10"] > f["ema21"] > f["ema50"]}
    return d


def sel(n, s, cond, **kw):
    def extra(key, row, tr):
        d = facts(key, row, tr)
        return d is not None and bool(cond(d, row, tr))
    return R.trades(n, s, extra=extra, **kw)


def block(n, s):
    print(f"\n=========== {n}-minute range, stop {R.STOP_NAME[s]} ===========")
    show("all", R.trades(n, s))
    print("-- yesterday's close vs the 50 EMA / 200 SMA")
    show("under the 50 EMA", sel(n, s, lambda d, r, t: d["u50"]))
    show("over the 50 EMA", sel(n, s, lambda d, r, t: not d["u50"]))
    show("under the 200 SMA", sel(n, s, lambda d, r, t: d["u200"] is True))
    show("over the 200 SMA", sel(n, s, lambda d, r, t: d["u200"] is False))
    show("under the 50 EMA and the 200 SMA (downtrend)", sel(n, s, lambda d, r, t: d["u50"] and d["u200"] is True))
    show("under the 50 EMA, over the 200 SMA", sel(n, s, lambda d, r, t: d["u50"] and d["u200"] is False))
    show("over the 50 EMA and the 200 SMA (uptrend)", sel(n, s, lambda d, r, t: not d["u50"] and d["u200"] is False))
    show("over the 50 EMA, under the 200 SMA", sel(n, s, lambda d, r, t: not d["u50"] and d["u200"] is True))
    show("10 < 21 < 50 EMA (stacked down)", sel(n, s, lambda d, r, t: d["stack_dn"]))
    show("10 > 21 > 50 EMA (stacked up)", sel(n, s, lambda d, r, t: d["stack_up"]))
    print("-- where the gap opens")
    show("opens under the 1-month low", sel(n, s, lambda d, r, t: d["o_u1m"]))
    show("opens over the 1-month low", sel(n, s, lambda d, r, t: not d["o_u1m"]))
    show("opens under the 21-day closing low", sel(n, s, lambda d, r, t: d["o_ucl21"]))
    show("opens over the 21-day closing low", sel(n, s, lambda d, r, t: not d["o_ucl21"]))
    show("opens under the 3-month low", sel(n, s, lambda d, r, t: d["o_u3m"] is True))
    show("opens under the 1-month, over the 3-month low", sel(n, s, lambda d, r, t: d["o_u1m"] and d["o_u3m"] is False))
    show("opens under the 6-month low", sel(n, s, lambda d, r, t: d["o_u6m"] is True))
    show("opens under the 52-week low", sel(n, s, lambda d, r, t: d["o_u52w"] is True))
    show("opens under the 200 SMA", sel(n, s, lambda d, r, t: d["o_u200"] is True))
    show("opens over the 200 SMA", sel(n, s, lambda d, r, t: d["o_u200"] is False))
    show("yesterday over the 200 SMA, opens under it", sel(n, s, lambda d, r, t: d["u200"] is False and d["o_u200"] is True))
    show("yesterday over the 50 EMA, opens under it", sel(n, s, lambda d, r, t: not d["u50"] and d["o_u50"]))
    print("-- room down to the 3-month low (the short price over it)")
    show("already under the 3-month low", sel(n, s, lambda d, r, t: d["room3m"] is not None and d["room3m"] <= 0))
    show("0-5% over the 3-month low", sel(n, s, lambda d, r, t: d["room3m"] is not None and 0 < d["room3m"] < 5))
    show("5-15% over the 3-month low", sel(n, s, lambda d, r, t: d["room3m"] is not None and 5 <= d["room3m"] < 15))
    show("15%+ over the 3-month low", sel(n, s, lambda d, r, t: d["room3m"] is not None and d["room3m"] >= 15))
    print("-- yesterday's close under the 52-week high")
    for lo, hi in ((0, 10), (10, 25), (25, 50), (50, 101)):
        show(f"{lo}-{hi}% under the 52-week high", sel(n, s, lambda d, r, t: lo <= d["off_high"] < hi))
    print("-- the mirrored plays (gap 5-20%)")
    g520 = lambda r: -20 <= r["gap"] <= -5
    p1 = lambda d, r, t: g520(r) and d["u50"] and d["o_u1m"] and d["o_u200"] is True and d["room3m"] is not None and d["room3m"] >= 5
    p1nr = lambda d, r, t: g520(r) and d["u50"] and d["o_u1m"] and d["o_u200"] is True
    p1b = lambda d, r, t: g520(r) and not d["u50"] and d["u200"] is False and d["o_u50"] and d["o_u200"] is True and d["o_u1m"]
    show("short play 1: yday under 50 EMA, opens under 1M low + 200 SMA, 5%+ room to 3M low", sel(n, s, p1))
    show("  the same without the room rule", sel(n, s, p1nr))
    show("  the same, room under 5% (the ones the rule drops)", sel(n, s, lambda d, r, t: p1nr(d, r, t) and not p1(d, r, t)))
    show("short play 1b: yday over 50 EMA + 200 SMA, opens under both + 1M low", sel(n, s, p1b))
    show("plays 1 + 1b", sel(n, s, lambda d, r, t: p1(d, r, t) or p1b(d, r, t)))
    show("the mirror of the skip: yday over 50 EMA, under 200 SMA", sel(n, s, lambda d, r, t: g520(r) and not d["u50"] and d["u200"] is True))
    show("everything else (gap 5-20%)", sel(n, s, lambda d, r, t: g520(r) and not p1(d, r, t) and not p1b(d, r, t)))
    print("-- the mirrored plays with the gap 8%+ (8-20%)")
    g8 = lambda r: -20 <= r["gap"] <= -8
    show("short play 1, gap 8-20%", sel(n, s, lambda d, r, t: p1(d, r, t) and g8(r)))
    show("short play 1 without the room rule, gap 8-20%", sel(n, s, lambda d, r, t: p1nr(d, r, t) and g8(r)))
    show("short play 1b, gap 8-20%", sel(n, s, lambda d, r, t: p1b(d, r, t) and g8(r)))
    show("opens under the 1-month low, gap 8-20%", sel(n, s, lambda d, r, t: d["o_u1m"] and g8(r)))
    show("opens over the 1-month low, gap 8-20%", sel(n, s, lambda d, r, t: not d["o_u1m"] and g8(r)))
    show("yday over 50 EMA + 200 SMA (uptrend), gap 8-20%", sel(n, s, lambda d, r, t: not d["u50"] and d["u200"] is False and g8(r)))
    show("yday under 50 EMA + 200 SMA (downtrend), gap 8-20%", sel(n, s, lambda d, r, t: d["u50"] and d["u200"] is True and g8(r)))


if __name__ == "__main__":
    n_feat = sum(1 for k, r in R.ROWS.items() if r["o"] >= 10 and k in F)
    print("stock-days with chart facts:", n_feat, "of", sum(1 for r in R.ROWS.values() if r["o"] >= 10))
    for n, s in (("3", "rh"), ("5", "rh")):
        block(n, s)
