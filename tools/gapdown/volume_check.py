#!/usr/bin/env python3
"""Does high volume make the earnings gap-down short better? (the user, Nov 28 2026)

  python3 volume_check.py trades_out.json features.json gaps_clean.json reasons.json scen.json vwap_bd.json

The break of the first 3-minute candle's low on earnings gap-downs of 8%+, by: the first candle's volume vs normal, the
stop distance (the first candle's size), and (hindsight) the whole day's volume vs the 20-day average."""
import json, sys
scen_path = sys.argv[5]
import vwap_bd_report as V
S, up, E8, R = V.S, V.up, V.E8, V.S.R

if __name__ == "__main__":
    S.SC = json.load(open(scen_path))
    e8 = [t for t in S.trades("orb") if E8(t[2])]
    thin = lambda t: R.ROWS[t[0]]["3"]["first"] > 0 or R.ROWS[t[0]]["3"]["rbars"] < 3
    dayrel = lambda t: R.ROWS[t[0]]["dayvol"] / R.ROWS[t[0]]["av20"]
    print("### the first 3-minute candle's volume vs normal")
    print(V.HEAD)
    for lo, hi in ((0, 5), (5, 10), (10, 20), (20, 1e9)):
        print(V.line(f"rel vol {lo}-{hi if hi < 1e9 else ''}x", [t for t in e8 if lo <= t[2]["rvol"] < hi]))
    print("### the same, strong yesterday")
    print(V.HEAD)
    for lo, hi in ((0, 5), (5, 10), (10, 20), (20, 1e9)):
        print(V.line(f"rel vol {lo}-{hi if hi < 1e9 else ''}x", [t for t in e8 if up(t[2]) and lo <= t[2]["rvol"] < hi]))
    print("### the stop distance = the first candle's size (full first candles)")
    print(V.HEAD)
    full = [t for t in e8 if not thin(t)]
    for lo, hi in ((0.5, 2), (2, 3.5), (3.5, 5), (5, 8), (8, 100)):
        print(V.line(f"stop {lo}-{hi}% away", [t for t in full if lo <= t[3]["risk_pct"] < hi]))
    print(V.line("stop up to 3.5% away", [t for t in full if t[3]["risk_pct"] < 3.5]))
    print(V.line("stop 3.5%+ away", [t for t in full if t[3]["risk_pct"] >= 3.5]))
    print(V.line("stop up to 3.5% away, strong yesterday", [t for t in full if t[3]["risk_pct"] < 3.5 and up(t[2])]))
    print(V.line("stop 3.5%+ away, strong yesterday", [t for t in full if t[3]["risk_pct"] >= 3.5 and up(t[2])]))
    print(V.line("thin first candle (a late open or a minute without a trade)", [t for t in e8 if thin(t)]))
    print("### hindsight: the whole day's volume vs the 20-day average")
    print(V.HEAD)
    for lo, hi in ((0, 3), (3, 5), (5, 1e9)):
        print(V.line(f"day volume {lo}-{hi if hi < 1e9 else ''}x", [t for t in e8 if lo <= dayrel(t) < hi]))
