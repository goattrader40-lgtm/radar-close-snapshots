#!/usr/bin/env python3
"""Every 5%+ gap-down day since Jan 2023 in the liquid universe, from the 6-year daily bars (radar-study bars_6y.json.gz).
  gap      = the open vs the close of the session before, -5% or lower
  liquid   = the close before $10+, 20-day average volume 700K+ shares, 20-day average dollar volume $20M+ (the 20 sessions
             before the gap day), market cap $700M+ (today's cap: the file holds only those)
Writes the per-year request files {date: [symbols]} and gaps.json (the day's facts for the analysis)."""
import gzip, json, sys, collections
src, outdir = sys.argv[1], sys.argv[2]
d = json.load(gzip.open(src, 'rt'))
caps = d['market_cap']
rows = {}
skip = {'SPY', 'QQQ'}
for sym, bs in d['bars'].items():
    if sym in skip or not caps.get(sym):
        continue
    last_close = bs[-1][4]
    for i in range(20, len(bs)):
        date, o, h, l, c, v = bs[i]
        if date < '2023-01-01':
            continue
        pc = bs[i - 1][4]
        if pc <= 0 or o <= 0:
            continue
        gap = o / pc - 1
        if gap > -0.05:
            continue
        w = bs[i - 20:i]
        av = sum(x[5] for x in w) / 20
        adv = sum(x[4] * x[5] for x in w) / 20
        if pc < 10 or av < 700_000 or adv < 20_000_000:
            continue
        # ADR 20 (the scanner's: average of high/low - 1), for reference
        adr = sum(x[2] / x[3] - 1 for x in w if x[3] > 0) / 20 * 100
        rows[f"{date} {sym}"] = {"pc": pc, "o": o, "h": h, "l": l, "c": c, "v": v, "gap": round(gap * 100, 2),
                                 "av20": round(av), "adv20": round(adv), "adr": round(adr, 2),
                                 "cap_then": round(caps[sym] * pc / last_close) if last_close else None,
                                 "pc2": bs[i - 2][4]}
by_year = collections.defaultdict(lambda: collections.defaultdict(list))
for k in rows:
    date, sym = k.split()
    by_year[date[:4]][date].append(sym)
for y, req in sorted(by_year.items()):
    json.dump({k: sorted(v) for k, v in sorted(req.items())}, open(f"{outdir}/gapdown_{y}.json", "w"), separators=(",", ":"))
    n = sum(len(v) for v in req.values())
    big = sorted(req.items(), key=lambda kv: -len(kv[1]))[:4]
    print(y, "days", len(req), "stock-days", n, "busiest", [(k, len(v)) for k, v in big])
json.dump(rows, open(f"{outdir}/gaps.json", "w"), separators=(",", ":"))
print("total", len(rows), "open>=10:", sum(1 for r in rows.values() if r["o"] >= 10),
      "gap<=-8:", sum(1 for r in rows.values() if r["gap"] <= -8), "gap<=-10:", sum(1 for r in rows.values() if r["gap"] <= -10),
      "cap_then>=700M:", sum(1 for r in rows.values() if (r["cap_then"] or 0) >= 7e8))
