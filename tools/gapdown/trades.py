#!/usr/bin/env python3
"""The gap-down short study (the user, Nov 23 2026): one row per stock-day and opening range, from the 1-minute SIP bars.

  python3 trades.py gaps.json share5.json ticks.json OUT.json raw_gapdown_2023.json.gz [raw_gapdown_2024.json.gz ...]

The mirror of the EP gap-up study's opening-range buy (radar/probe_orh.py orh_trade):
  range     the first 3- (or 5-) minute candle that traded (9:30 for 98%; a late NYSE open: the candle it opened in)
  entry     the first 1-minute bar after the range whose low goes under the range low: sold short at the range low (at
            the bar's open when it opens under it)
  stop      "rh" the range high;  "dh" the day's high at the moment of the entry
  exit      the stop (bought back at the stop, at the bar's open when it opens over it), else the day's last price
  R         (entry - exit) / (stop - entry)
A 1-minute bar can't order its own high and low. When the entry's own minute also traded at or over the stop, that
minute's trades (radar/probe_ticks.py) say which came first: the stop after the break = stopped (-1R); the high before
the break = the trade goes on (and for "dh" that high is the day's high, so it is the stop). Without the trades: stopped.

Checks against the daily bar (Yahoo) before a stock-day is used: see check()."""
import gzip, json, sys

RANGES = (3, 5)
HALF_DAYS = {"2023-07-03", "2023-11-24", "2024-07-03", "2024-11-29", "2024-12-24", "2025-07-03", "2025-11-28", "2025-12-24",
             "2026-07-02"}      # the session ends at 1:00 PM: the bars after it are after-hours trades
SKIP_DATES = {"2023-01-24"}        # the NYSE opening-auction glitch: wrong opening prints, later cancelled (FCX, SHEL, UBER, WPM ...)
SKIP_KEYS = {"2023-08-04 FWONK"}   # Liberty's reclassification that morning (holders got Liberty Live shares): not a gap


def check(bs, g):
    """(None, scale) when the minute bars agree with the daily bar, else (the reason, None).
    scale = minute price / daily price: Yahoo's daily bars are also adjusted for spin-offs (MMM, DD, DHR, WDC, FDX ...),
    Alpaca's minute bars for splits only, so a stock-day whose open, low and close all differ by the same factor is kept
    and read at the minute bars' prices (the prices as traded). After that: the low within 1.5%, the last price within
    3% of the official close (the closing auction prints after the last minute bar); the open and the high within 5%
    (the first print and a stray print before the opening auction can differ from the official open and high)."""
    if len(bs) < 60:
        return "under 60 bars", None
    if bs[0][0] >= 15:
        return "no bar before 9:45", None
    o, h, l, c = bs[0][1], max(b[2] for b in bs), min(b[3] for b in bs), bs[-1][4]
    k = sorted((o / g["o"], h / g["h"], l / g["l"], c / g["c"]))
    k = (k[1] + k[2]) / 2                    # the middle of the four ratios: one stray print doesn't set the scale
    if abs(k - 1) <= 0.015:
        k = 1.0
    if abs(l / (g["l"] * k) - 1) > 0.015 or abs(c / (g["c"] * k) - 1) > 0.03:
        return "low / close differs", None
    if abs(o / (g["o"] * k) - 1) > 0.05:
        return "open differs", None
    if abs(h / (g["h"] * k) - 1) > 0.05:
        return "high differs", None
    return None, k


def walk(later, entry, stop, close):
    """the trade after its entry minute: (exit, stopped)"""
    for x in later:
        if x[2] >= stop:
            return max(x[1], stop), 1
    return close, 0


def short(bs, n, tick=None):
    """tick: {minute: the probe_ticks row} for this stock-day"""
    start = bs[0][0] // n * n                # the first 3- / 5-minute candle that traded
    rng = [b for b in bs if b[0] < start + n]
    after = [b for b in bs if b[0] >= start + n]
    if not rng or not after:
        return None
    ro, rc = rng[0][1], rng[-1][4]
    rh, rl = max(b[2] for b in rng), min(b[3] for b in rng)
    out = {"ro": ro, "rc": rc, "rhi": rh, "rlo": rl, "rv": sum(b[5] for b in rng), "first": bs[0][0], "rbars": len(rng),
           "color": "red" if rc < ro else "green" if rc > ro else "doji"}
    hi = rh
    for j, b in enumerate(after):
        if b[3] < rl:
            entry = min(b[1], rl)
            t = 570 + b[0]
            out.update(t=f"{t // 60:02d}:{t % 60:02d}", m=b[0], entry=round(entry, 4), close=bs[-1][4],
                       low_after=min(x[3] for x in after[j:]), vol_before=sum(x[5] for x in rng) + sum(x[5] for x in after[:j]))
            for name, stop in (("rh", rh), ("dh", hi)):
                if stop <= entry:
                    out[name] = None
                    continue
                amb, same = (1 if b[2] >= stop else 0), None       # same: what the minute's trades said
                if amb:
                    tk = (tick or {}).get(b[0])
                    hit = None
                    if tk and tk.get("n") and tk.get("entry") is not None:
                        hit = next((v for ks, v in tk["stops"].items() if abs(float(ks) - stop) < 1e-6), None)
                    if hit == 0:
                        same = "high first"
                        if name == "dh" and tk.get("pre_hi"):
                            stop = max(stop, tk["pre_hi"])        # the day's high when the range low broke
                    else:
                        same = "stopped" if hit == 1 else "stopped (no trades read)"
                if same and same.startswith("stopped"):
                    exit_, stopped = stop, 1
                else:
                    exit_, stopped = walk(after[j + 1:], entry, stop, bs[-1][4])
                risk = stop - entry
                out[name] = {"stop": round(stop, 4), "exit": round(exit_, 4), "stopped": stopped,
                             "r": round((entry - exit_) / risk, 4), "amb": amb, "same": same,
                             "risk_pct": round(risk / entry * 100, 3)}
            return out
        hi = max(hi, b[2])
    return out


def main():
    gaps = json.load(open(sys.argv[1]))
    sh = json.load(open(sys.argv[2]))
    share5, med = sh["share5"], sh["median"]
    ticks = {}
    for key, v in json.load(open(sys.argv[3]))["rows"].items():
        date, sym, minute = key.split()
        ticks.setdefault(f"{date} {sym}", {})[int(minute)] = v
    rows, bad, errors, seen = {}, {}, [], set()
    for path in sys.argv[5:]:
        d = json.load(gzip.open(path, "rt"))
        errors += d.get("errors") or []
        for key, bs in d["bars"].items():
            date, sym = key.split()
            sym = sym.replace(".", "/")
            key = f"{date} {sym}"
            g = gaps.get(key)
            if not g or date in SKIP_DATES or key in SKIP_KEYS:
                continue
            seen.add(key)
            bs = sorted(b for b in bs if b[0] < (210 if date in HALF_DAYS else 390))
            if not bs:
                continue
            why, k = check(bs, g)
            if why:
                bad[key] = [why, bs[0][0], bs[0][1], max(b[2] for b in bs), min(b[3] for b in bs), bs[-1][4], len(bs)]
                continue
            s5 = min(max(share5.get(sym, med), 0.01), 0.05)      # the stock's normal share of a day's volume in its first 5 minutes
            row = {"gap": g["gap"], "pc": round(g["pc"] * k, 4), "o": bs[0][1], "h": max(b[2] for b in bs), "l": min(b[3] for b in bs),
                   "c": bs[-1][4], "scale": round(k, 4), "o_daily": round(g["o"] * k, 4), "av20": g["av20"],
                   "adr": g["adr"], "nbars": len(bs), "dayvol": sum(b[5] for b in bs)}
            for n in RANGES:
                tr = short(bs, n, ticks.get(key))
                if tr:
                    tr["rvol"] = round(tr["rv"] / (g["av20"] * s5 * n / 5), 3)
                    tr["pct_adv"] = round(tr["rv"] / g["av20"] * 100, 3)
                row[str(n)] = tr
            rows[key] = row
    missing = sorted(k for k in gaps if k not in seen and k.split()[0] not in SKIP_DATES and k not in SKIP_KEYS)
    json.dump({"rows": rows, "bad": bad, "missing": missing, "errors": errors}, open(sys.argv[4], "w"), separators=(",", ":"))
    print("gap days", len(gaps), "with bars", len(seen), "used", len(rows), "dropped by the checks", len(bad),
          "no bars", len(missing), "fetch errors", len(errors))
    why = {}
    for v in bad.values():
        why[v[0]] = why.get(v[0], 0) + 1
    print("dropped:", why, "| no bars:", missing)


if __name__ == "__main__":
    main()
