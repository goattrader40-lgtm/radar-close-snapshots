#!/usr/bin/env python3
"""A check, not a rule (the user, Nov 7 2026, LION): "never closed above that day, so that day is the base top, not the
day's poke above that still closed below". LION: Oct 20 made the high 12.88; no close above it since; Oct 29 went to
13.17 in the day and closed back under 12.88: a poke, not the base top. The engine took 13.17 (the highest high).

For every buy point on Launches (launches, laggards, your picks), the Watchlist's 3-SETUPS and the TREND list's feeder
lists (2-POOL, 1-UPDAY, 1-EP/GAP), at each evening read: the day whose high is that buy point (p) and whether p was a
poke: it went over an earlier high that has never been closed above since (t) and closed under it. Then the base top
by the rule = the highest such earlier high under the buy point. A buy point that isn't a day's high (a flag's line,
the 21 EMA ...) isn't checked. The next session's bar says whether each level traded and held into the close.

  python3 scanner/probe_basetop.py BARS.json.gz STOCKS.json OUT.json DATE=launch.json:latest.json [...]"""
import gzip
import json
import sys

TREND_ON = {"Up", "Turn up", "Reclaim", "Resting"}       # the page's TREND list (docs/index.html TREND_ON)
SPAN = 120                                               # the engine's larger base (scanner/launch.py base_top)


def rule_level(bars, p, i):
    """(level, its index) when day p's high was a poke, else None. Tops = days in the 120 sessions before i whose high
    no close has gone over since (through day i), each lower than every earlier one (a later, higher one closed under an
    earlier top: a poke)"""
    lo = max(0, p - SPAN)
    hi_close = -1.0
    never = [False] * (i + 1)
    for k in range(i, lo - 1, -1):                     # never closed above through day i
        never[k] = k < i and bars[k][2] > hi_close
        hi_close = max(hi_close, bars[k][4])
    tops = []
    for k in range(lo, i):
        if never[k] and all(bars[k][2] < bars[t][2] for t in tops):
            tops.append(k)
    if p in tops or not never[p]:
        return None
    under = [t for t in tops if t < p and bars[t][2] < bars[p][2]]
    if not under:
        return None
    t = max(under, key=lambda k: bars[k][2])
    return bars[t][2], t


def day_of_high(bars, bp, i):
    """the earliest day in the last 130 sessions whose high is the buy point (to the cent)"""
    for k in range(max(0, i - 130), i + 1):
        if abs(bars[k][2] - bp) <= max(0.006, bp * 0.0005):
            return k
    return None


def main():
    bars_p, stocks_p, out_p, pairs = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
    with gzip.open(bars_p, "rt") as f:
        B = json.load(f)["bars"]
    trend = {r["symbol"]: r.get("trend") for r in json.load(open(stocks_p))}
    out = {"note": __doc__.split("\n\n")[0], "reads": []}
    last_read = max(p.split("=", 1)[0] for p in pairs)
    for pair in pairs:
        day, paths = pair.split("=", 1)
        lp, wp = paths.split(":")
        L, W = json.load(open(lp)), json.load(open(wp))
        items = []
        for lst, name in (("launches", "Launches"), ("laggards", "Launch laggards"), ("setups3", "3-SETUPS")):
            for r in L.get(lst, []):
                items.append((name if not (r.get("pick") or r.get("grade") == "You") else "Launches (your pick)", r))
        onL = {r["symbol"] for _, r in items}
        seen = set()
        for n in ("2-POOL", "1-UPDAY", "1-EP/GAP"):
            for r in W.get("lists", {}).get(n, []):
                if r["symbol"] in onL or r["symbol"] in seen:
                    continue
                seen.add(r["symbol"])
                if day == last_read:
                    if trend.get(r["symbol"]) not in TREND_ON:
                        continue
                    items.append(("TREND (" + n + ")", r))
                else:
                    items.append(("TREND feeder " + n + " (Trend that evening not kept)", r))
        rows, skipped = [], 0
        for lst, r in items:
            sym, bp = r["symbol"], r.get("buy_point")
            bars = B.get(sym) or []
            dates = [b[0] for b in bars]
            if not bp or day not in dates:
                continue
            i = dates.index(day)
            if not bars[i][4] < bp:
                continue
            p = day_of_high(bars, bp, i)
            if p is None:
                skipped += 1
                continue
            rl = rule_level(bars, p, i)
            row = {"sym": sym, "list": lst, "pattern": r.get("pattern") or r.get("setup"), "buy_point": bp,
                   "bp_day": bars[p][0], "bp_day_close": round(bars[p][4], 2), "close": round(bars[i][4], 2),
                   "stage": (r.get("stage") or r.get("why") or "")[:140]}
            if rl:
                row.update(rule_level=round(rl[0], 2), rule_day=bars[rl[1]][0], rule_day_close=round(bars[rl[1]][4], 2),
                           rule_age=i - rl[1] + 1, changes=True)
            else:
                row.update(rule_level=None, changes=False)
            nxt = bars[i + 1] if i + 1 < len(bars) else None
            if nxt:
                row.update(next_day=nxt[0], next_high=round(nxt[2], 2), next_close=round(nxt[4], 2),
                           old_traded=nxt[2] > bp, old_held=nxt[4] > bp)
                if rl:
                    row.update(rule_traded=nxt[2] > rl[0], rule_held=nxt[4] > rl[0])
            rows.append(row)
        ch = [x for x in rows if x["changes"]]
        out["reads"].append({"read_of": day, "checked": len(rows), "not_a_high": skipped, "changes": len(ch),
                             "rows": sorted(rows, key=lambda x: (not x["changes"], x["list"], x["sym"]))})
    json.dump(out, open(out_p, "w"), indent=1)
    for rd in out["reads"]:
        print(f"read of {rd['read_of']}: {rd['checked']} buy points at a day's high, {rd['changes']} change; {rd['not_a_high']} not a day's high")
        for x in rd["rows"]:
            if x["changes"]:
                print(f"   {x['sym']:6} {x['list'][:28]:28} {x['buy_point']} ({x['bp_day']}, closed {x['bp_day_close']}) -> "
                      f"{x['rule_level']} ({x['rule_day']}, {x['rule_age']} days)  next {x.get('next_day')} H {x.get('next_high')} C {x.get('next_close')}")


if __name__ == "__main__":
    main()
