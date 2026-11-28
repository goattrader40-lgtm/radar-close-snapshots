#!/usr/bin/env python3
"""The user's second earnings gap-down short (Nov 28 2026): "opens, goes up, sometimes hits previous some days' low, then
fades, and breaks down VWAP".

  python3 vwap_bd.py trades_out.json features.json OUT.json raw_gapdown_2023.json.gz [...]

On n-minute candles (3 and 5) with the session VWAP:
  the pop    the day's high is 0.5%+ over the 9:30 open and the candle before closed at or over VWAP (the price is up
             and over VWAP)
  the short  the first candle after that which closes under VWAP: short at that close; stop = the day's high so far;
             out at the stop or the day's last price. The first signal of the day, before 3:00 PM.
Saved per stock-day and candle size: the trade, pop_pct (the day's high over the open, %), the prior lows the pop
reached ("tag": yesterday's low, the lowest low of the 3 / 5 / 10 / 21 sessions before, the 21-day closing low, each
only when the gap opened under it; reached = the high came within 0.3% under it or over it), over_pct (how far over the
nearest tagged low the high went, %), orl (1 = the first 3-minute candle's low was already broken)."""
import gzip, json, sys
import scenarios as S

LEVELS = (("yesterday's low", "plow"), ("3-day low", "low3"), ("5-day low", "low5"), ("10-day low", "low10"), ("1-month low", "low21"), ("21-day closing low", "clow21"))


def breakdown(bs, n, row, feat, pop=0.005):
    F = S.candles(bs, n)
    if len(F) < 6:
        return None
    op, hi = bs[0][1], bs[0][2]
    for i, f in enumerate(F):
        k, o, h, l, c, vw, idx = f
        if k >= S.LAST:
            return None
        hi_before = hi
        hi = max(hi, h)
        if i == 0 or F[i - 1][4] < F[i - 1][5] or hi < op * (1 + pop):
            continue
        if c < vw:
            t = S.result(bs, idx, k + n - 1, c, hi)
            if not t:
                return None
            t["pop_pct"] = round((hi / op - 1) * 100, 2)
            if feat:
                sc = row["scale"]
                tags = [(nm, feat[key] * sc) for nm, key in LEVELS if feat.get(key) and feat[key] * sc > op * 1.002 and hi >= feat[key] * sc * 0.997]
                if tags:
                    near = min(tags, key=lambda x: x[1])
                    t["tag"], t["over_pct"] = [nm for nm, _ in tags], round((hi / near[1] - 1) * 100, 2)
                t["below_any"] = 1 if any(feat.get(key) and feat[key] * sc > op * 1.002 for nm, key in LEVELS) else 0
            r3 = row.get("3") or {}
            t["orl"] = 1 if "m" in r3 and r3["m"] < t["m"] else 0
            return t
    return None


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
            bs = sorted(b for b in bs if b[0] < (210 if date in S.HALF_DAYS else 390))
            r = {str(n): breakdown(bs, n, row, feats.get(key)) for n in (3, 5)}
            r = {k: v for k, v in r.items() if v}
            if r:
                out[key] = r
    json.dump(out, open(sys.argv[3], "w"), separators=(",", ":"))
    print("stock-days", len(rows), "| signals:", {k: sum(1 for v in out.values() if k in v) for k in ("3", "5")},
          "| tagged a prior low (5-min):", sum(1 for v in out.values() if v.get("5", {}).get("tag")))


if __name__ == "__main__":
    main()
