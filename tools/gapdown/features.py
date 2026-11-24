#!/usr/bin/env python3
"""The gap-down study's chart facts the evening before each gap day, the mirror of the gap-up rules (the user, Nov 24 2026:
"for the gap-ups we have some rules, 1 month, 3 months, the resistance, 21 day ... for the short it has to be in the other
direction").

  python3 features.py bars_6y.json.gz gaps_clean.json features.json

Per stock-day, from the daily bars up to the session before (Yahoo's prices, the same basis as the gap's open):
  ema10 / ema21 / ema50 / sma200   at yesterday's close (sma200 null with under 200 sessions)
  low21 / low63 / low126 / low252  the lowest LOW of the 21 / 63 / 126 / 252 sessions before (the 1- / 3- / 6-month and
                                   52-week lows: the mirror of the Resistance column's highs, scanner/launch.py RES_SPANS)
  clow21                           the lowest CLOSE of the 21 sessions before (the mirror of the 21-day closing high)
  high252                          the highest high of the 252 sessions before
  pc / plow / phigh                yesterday's close, low and high
  n                                sessions of history before the gap day"""
import gzip, json, sys


def ema(x, n):
    a, out, e = 2 / (n + 1), [], None
    for v in x:
        e = v if e is None else a * v + (1 - a) * e
        out.append(e)
    return out


def main():
    bars = json.load(gzip.open(sys.argv[1], "rt"))["bars"]
    gaps = json.load(open(sys.argv[2]))
    want = {}
    for k in gaps:
        d, s = k.split()
        want.setdefault(s, set()).add(d)
    out = {}
    for s, days in want.items():
        bs = bars.get(s)
        if not bs:
            continue
        c = [b[4] for b in bs]
        e10, e21, e50 = ema(c, 10), ema(c, 21), ema(c, 50)
        for i, b in enumerate(bs):
            if b[0] not in days or i < 22:
                continue
            j = i - 1                                    # yesterday
            lo = lambda n: min(x[3] for x in bs[max(0, i - n):i])
            out[f"{b[0]} {s}"] = {
                "n": i, "pc": c[j], "plow": bs[j][3], "phigh": bs[j][2], "ema10": round(e10[j], 4), "ema21": round(e21[j], 4), "ema50": round(e50[j], 4),
                "sma200": round(sum(c[i - 200:i]) / 200, 4) if i >= 200 else None,
                "low21": lo(21), "low63": lo(63) if i >= 63 else None, "low126": lo(126) if i >= 126 else None,
                "low252": lo(252) if i >= 252 else None, "clow21": min(c[i - 21:i]),
                "high252": max(x[2] for x in bs[max(0, i - 252):i])}
    json.dump(out, open(sys.argv[3], "w"), separators=(",", ":"))
    print("stock-days", len(gaps), "with features", len(out), "no 200 SMA", sum(1 for v in out.values() if v["sma200"] is None))


if __name__ == "__main__":
    main()
