#!/usr/bin/env python3
"""The first candle's size against the stock's ADR (the user, Nov 28 2026: "did you measure to their ADR, don't you
think it's better judgment?").

  python3 adr_check.py trades_out.json features.json gaps_clean.json reasons.json scen.json vwap_bd.json

The break of the first 3-minute candle's low on earnings gap-downs of 8%+ (full first candles). The stop distance
(short price to the candle's high) in % of the price and in ADRs (the 20-day average of high / low - 1, the evening
before); and the gap in ADRs."""
import json, sys
scen_path = sys.argv[5]
import vwap_bd_report as V
S, up, E8, R = V.S, V.up, V.E8, V.S.R

if __name__ == "__main__":
    S.SC = json.load(open(scen_path))
    thin = lambda t: R.ROWS[t[0]]["3"]["first"] > 0 or R.ROWS[t[0]]["3"]["rbars"] < 3
    e8 = [t for t in S.trades("orb") if E8(t[2]) and not thin(t)]
    adr = lambda t: R.ROWS[t[0]]["adr"]
    sa = lambda t: t[3]["risk_pct"] / adr(t)                 # the stop distance in ADRs
    ga = lambda t: -t[2]["gap"] / adr(t)                     # the gap in ADRs
    q = lambda a, p: sorted(a)[int(len(a) * p)]
    a = [adr(t) for t in e8]
    s = [sa(t) for t in e8]
    print(f"{len(e8)} trades. ADR: p10 {q(a, .1):.1f}% median {q(a, .5):.1f}% p90 {q(a, .9):.1f}%.  Stop distance in ADRs: p10 {q(s, .1):.2f} p25 {q(s, .25):.2f} median {q(s, .5):.2f} p75 {q(s, .75):.2f} p90 {q(s, .9):.2f}")
    print("\n### the stop distance in ADRs")
    print(V.HEAD)
    for lo, hi in ((0, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0), (1.0, 1.3), (1.3, 1.8), (1.8, 99)):
        print(V.line(f"stop {lo}-{hi if hi < 99 else ''} ADR away", [t for t in e8 if lo <= sa(t) < hi]))
    for th in (0.6, 0.7, 0.8, 1.0):
        print(V.line(f"stop under {th} ADR", [t for t in e8 if sa(t) < th]))
        print(V.line(f"stop {th} ADR or more", [t for t in e8 if sa(t) >= th]))
    print("\n### the stop distance in % of the price (the earlier table)")
    print(V.HEAD)
    for lo, hi in ((0.5, 2), (2, 3.5), (3.5, 5), (5, 8), (8, 100)):
        print(V.line(f"stop {lo}-{hi}% away", [t for t in e8 if lo <= t[3]["risk_pct"] < hi]))
    print("\n### which yardstick says it better: the two against each other (cut at 3.5% and at 0.8 ADR)")
    print(V.HEAD)
    for lab, f in (("tight by both (under 3.5% and under 0.8 ADR)", lambda t: t[3]["risk_pct"] < 3.5 and sa(t) < 0.8),
                   ("tight in % only (under 3.5%, but 0.8 ADR or more: a slow stock)", lambda t: t[3]["risk_pct"] < 3.5 and sa(t) >= 0.8),
                   ("tight in ADR only (3.5%+, but under 0.8 ADR: a fast stock)", lambda t: t[3]["risk_pct"] >= 3.5 and sa(t) < 0.8),
                   ("wide by both", lambda t: t[3]["risk_pct"] >= 3.5 and sa(t) >= 0.8)):
        print(V.line(lab, [t for t in e8 if f(t)]))
    print("\n### by the stock's ADR: does the same % cut work for slow and fast stocks?")
    print(V.HEAD)
    for lab, lo, hi in (("ADR under 3% (slow)", 0, 3), ("ADR 3-5%", 3, 5), ("ADR 5%+ (fast)", 5, 99)):
        g = [t for t in e8 if lo <= adr(t) < hi]
        print(V.line(lab + ", every trade", g))
        print(V.line(lab + ", stop under 3.5%", [t for t in g if t[3]["risk_pct"] < 3.5]))
        print(V.line(lab + ", stop 3.5%+", [t for t in g if t[3]["risk_pct"] >= 3.5]))
        print(V.line(lab + ", stop under 0.8 ADR", [t for t in g if sa(t) < 0.8]))
        print(V.line(lab + ", stop 0.8 ADR+", [t for t in g if sa(t) >= 0.8]))
    print("\n### strong yesterday, the stop in ADRs")
    print(V.HEAD)
    for lo, hi in ((0, 0.6), (0.6, 0.8), (0.8, 1.0), (1.0, 1.5), (1.5, 99)):
        print(V.line(f"strong, stop {lo}-{hi if hi < 99 else ''} ADR", [t for t in e8 if up(t[2]) and lo <= sa(t) < hi]))
    print(V.line("strong, stop under 0.8 ADR", [t for t in e8 if up(t[2]) and sa(t) < 0.8]))
    print(V.line("strong, stop 0.8 ADR+", [t for t in e8 if up(t[2]) and sa(t) >= 0.8]))
    print("\n### the gap in ADRs (earnings days, every gap of 5%+, full first candles)")
    print(V.HEAD)
    allE = [t for t in S.trades("orb") if t[2]["earn"] == 1 and not thin(t)]
    for lo, hi in ((0, 1.5), (1.5, 2.5), (2.5, 3.5), (3.5, 5), (5, 99)):
        print(V.line(f"gap {lo}-{hi if hi < 99 else ''} ADR", [t for t in allE if lo <= ga(t) < hi]))
    print(V.line("gap 5-8% but 2.5+ ADR (a big gap for a slow stock)", [t for t in allE if t[2]["gap"] > -8 and ga(t) >= 2.5]))
    print(V.line("gap 5-8% and under 2.5 ADR", [t for t in allE if t[2]["gap"] > -8 and ga(t) < 2.5]))
    print(V.line("gap 8%+ but under 2.5 ADR (a normal gap for a fast stock)", [t for t in allE if t[2]["gap"] <= -8 and ga(t) < 2.5]))
    print(V.line("gap 8%+ and 2.5+ ADR", [t for t in allE if t[2]["gap"] <= -8 and ga(t) >= 2.5]))
