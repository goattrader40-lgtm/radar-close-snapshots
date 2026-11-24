#!/usr/bin/env python3
"""The gap-down study's gap list checked against Alpaca's daily bars (radar/probe_daily.py -> radar-study gapdown_daily.json.gz).

  python3 clean_gaps.py gaps.json gapdown_daily.json.gz gaps_clean.json

Yahoo's daily bars are adjusted for splits and spin-offs but not for cash payouts, and now and then a close is on another
basis (an ADR ratio change). So a "gap" can be a payout going ex that morning (ZIM, EC, PBR, PGR: dividends; APTV, UL:
spin-offs) or no gap at all (EMBJ Nov 17 2026). The gap that counts = the smaller of Yahoo's and Alpaca's with dividends
and spin-offs taken out; under 5% the stock-day is dropped, otherwise its gap is corrected."""
import gzip, json, sys

g = json.load(open(sys.argv[1]))
A = json.load(gzip.open(sys.argv[2], "rt"))["rows"]
out, dropped, changed = {}, {}, {}
for k, v in g.items():
    a = A.get(k.replace("/", "."))
    v = dict(v)
    if a:
        pc, op = a["s"][0], a["s"][1]
        ga = (op / pc - 1) * 100                                          # Alpaca's gap, prices adjusted for splits only
        gall = (a["a"][1] / a["a"][0] - 1) * 100 if a["a"] else ga        # ... and for dividends / spin-offs
        true = v["gap"]
        if abs(ga - v["gap"]) > 1.0 and k[:10] != "2023-01-24":
            true = ga                                                     # Yahoo's close before is on another basis
        if gall - ga > 1.0:
            true = max(true, gall)                                        # part of the "gap" is a payout going ex that morning
        if true > -5:
            dropped[k] = [v["gap"], round(ga, 2), round(gall, 2)]
            continue
        if abs(true - v["gap"]) > 0.01:
            changed[k] = [v["gap"], round(true, 2)]
            v["gap_yahoo"] = v["gap"]
            v["gap"] = round(true, 2)
    out[k] = v
json.dump(out, open(sys.argv[3], "w"), separators=(",", ":"))
print("kept", len(out), "| dropped: no real 5% gap", len(dropped), sorted(dropped), "| gap corrected", sorted(changed.items()))
