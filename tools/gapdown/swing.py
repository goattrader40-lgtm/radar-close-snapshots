#!/usr/bin/env python3
"""The gap-down short held past the close (the user, Nov 24 2026: "you can find another strategies ... see what works").

  python3 swing.py trades_out.json features.json gaps_clean.json bars_6y.json.gz

The same entry (the break of the first 3-minute candle's low, stop at the range high), other exits:
  close      out at the stop or the day's last price (part 1)
  hold N     the stop stays; out at the close of session N (1 = the gap day)
  EMA 10/21  the EP playbook's management mirrored: 1/3 bought back 10% under the entry, the stop of the rest then at
             the entry, the rest out on the first daily close over the 10 / 21 EMA
From the second session on the daily bars decide (the open over the stop = out at the open; the day's high at the stop =
out at the stop, before anything else that day).
And the close short, the mirror of play 2: sold short at the gap day's last price, stop at the gap day's high."""
import gzip, json, sys
bars_path = sys.argv[4]
sys.argv = sys.argv[:4]
import mirror as M
R, F, G = M.R, M.F, M.G
BARS = json.load(gzip.open(bars_path, "rt"))["bars"]
IDX, EMA = {}, {}


def series(sym):
    if sym not in IDX:
        bs = BARS.get(sym) or []
        IDX[sym] = {b[0]: i for i, b in enumerate(bs)}
        c = [b[4] for b in bs]
        EMA[sym] = (M.__dict__.get("ema") or __import__("features").ema)(c, 10) if False else None
    return BARS.get(sym) or [], IDX[sym]


def ema(x, n):
    a, out, e = 2 / (n + 1), [], None
    for v in x:
        e = v if e is None else a * v + (1 - a) * e
        out.append(e)
    return out


_E = {}


def emas(sym):
    if sym not in _E:
        c = [b[4] for b in BARS.get(sym) or []]
        _E[sym] = (ema(c, 10), ema(c, 21))
    return _E[sym]


def later_days(key, k):
    """the daily bars after the entry day, at the minute bars' prices: [(o, h, l, c, close over the 10 EMA, over the 21 EMA)]"""
    d, sym = key.split()
    bs, idx = series(sym)
    i = idx.get(d)
    if i is None:
        return []
    e10, e21 = emas(sym)
    return [(b[1] * k, b[2] * k, b[3] * k, b[4] * k, b[4] > e10[j], b[4] > e21[j]) for j, b in enumerate(bs[i + 1:], i + 1)]


def hold(key, row, entry, stop, r_day, stopped_day, n):
    """out at the close of session n (1 = the entry day), the stop unchanged"""
    if stopped_day or n <= 1:
        return r_day
    days = later_days(key, row["scale"])[:n - 1]
    px = None
    for o, h, l, c, *_ in days:
        if o >= stop:
            px = o
            break
        if h >= stop:
            px = stop
            break
        px = c
    if px is None:
        return r_day
    return (entry - px) / (stop - entry)


def trail(key, row, entry, stop0, sw, which, target=0.10, part=1 / 3):
    """the mirrored EP management from the state at the entry day's close (sw); which: 4 = the 10 EMA, 5 = the 21 EMA"""
    pos, pnl, took, stop = sw["pos"], sw["pnl"], sw["took"], sw["stop"]
    tgt = entry * (1 - target)
    if pos > 0:
        days = later_days(key, row["scale"])
        last = None
        for d in days:
            o, h, l, c = d[:4]
            last = c
            if o >= stop:
                pnl += pos * (entry - o); pos = 0; break
            if h >= stop:
                pnl += pos * (entry - stop); pos = 0; break
            if not took and l <= tgt:
                pnl += part * (entry - min(o, tgt)); pos -= part; took, stop = 1, min(stop, entry)
            if d[which]:
                pnl += pos * (entry - c); pos = 0; break
        if pos > 0:                                       # still open at the end of the data: marked at the last close
            pnl += pos * (entry - (last if last is not None else row["c"]))
    return pnl / (stop0 - entry)


def table(label, ts, extra_cols=True):
    if len(ts) < 25:
        print(f"{label:<50} {len(ts)} trades")
        return
    out = []
    def agg(rs):
        n = len(rs)
        return f"{100 * sum(1 for r in rs if r > 0) / n:>4.0f}% {sum(rs) / n:>+6.2f}R {sum(rs):>+6.0f}R"
    base = [t[3]["r"] for t in ts]
    cols = [("close", base)]
    for n in (2, 3, 5, 10):
        cols.append((f"hold {n}", [hold(t[0], t[1], t[2]["entry"], t[3]["stop"], t[3]["r"], t[3]["stopped"], n) for t in ts]))
    cols.append(("EMA 10", [trail(t[0], t[1], t[2]["entry"], t[3]["stop"], t[3]["sw"], 4) for t in ts]))
    cols.append(("EMA 21", [trail(t[0], t[1], t[2]["entry"], t[3]["stop"], t[3]["sw"], 5) for t in ts]))
    print(f"{label:<50} {len(ts):>5} | " + " | ".join(f"{nm}: {agg(rs)}" for nm, rs in cols))
    return dict(cols)


def by_year(label, ts, which=4):
    rs = {}
    for t in ts:
        rs.setdefault(t[0][:4], []).append(trail(t[0], t[1], t[2]["entry"], t[3]["stop"], t[3]["sw"], which))
    md = [trail(t[0], t[1], t[2]["entry"], t[3]["stop"], t[3]["sw"], which) for t in ts if t[0].split()[0] not in M.MD]
    print(f"    {label} by year: " + "  ".join(f"{y}: {len(v)}/{sum(v) / len(v):+.2f}/{sum(v):+.0f}" for y, v in sorted(rs.items()))
          + (f" | ordinary {len(md)}/{sum(md) / len(md):+.3f}/{sum(md):+.0f}" if md else ""))


def close_short(cond=None, weak=None):
    """the mirror of play 2: short at the gap day's last price, stop at the gap day's high; [(key, row, entry, stop)]"""
    out = []
    for key, row in R.ROWS.items():
        if row["o"] < 10 or key not in F:
            continue
        tr = row.get("3")
        if not tr:
            continue
        entry, stop = row["c"], row["h"]
        if stop <= entry or (stop - entry) / entry * 100 < R.MIN_RISK:
            continue
        d = M.facts(key, row, dict(tr, entry=entry))
        if d is None or (cond and not cond(d, row, tr)):
            continue
        pos = (row["c"] - row["l"]) / (row["h"] - row["l"]) if row["h"] > row["l"] else 0.5
        if weak is not None and not weak(pos, row):
            continue
        out.append((key, row, entry, stop))
    return out


def close_table(label, cs):
    if len(cs) < 25:
        print(f"{label:<50} {len(cs)} trades")
        return
    def agg(rs):
        n = len(rs)
        return f"{100 * sum(1 for r in rs if r > 0) / n:>4.0f}% {sum(rs) / n:>+6.2f}R {sum(rs):>+6.0f}R"
    cols = []
    for n in (2, 3, 5, 10):
        cols.append((f"hold {n}", [hold(k, row, e, s, 0.0, 0, n) for k, row, e, s in cs]))
    sw0 = lambda s: {"pos": 1.0, "pnl": 0.0, "took": 0, "stop": s}
    cols.append(("EMA 10", [trail(k, row, e, s, sw0(s), 4) for k, row, e, s in cs]))
    cols.append(("EMA 21", [trail(k, row, e, s, sw0(s), 5) for k, row, e, s in cs]))
    print(f"{label:<50} {len(cs):>5} | " + " | ".join(f"{nm}: {agg(rs)}" for nm, rs in cols))


if __name__ == "__main__":
    up = lambda d: (not d["u50"]) and d["u200"] is False
    p1b = lambda d, r, t: up(d) and d["o_u50"] and d["o_u200"] is True and d["o_u1m"]
    print("== the opening-range short (3-min range, stop range high) with other exits: win% / avg R / total R ==")
    sets = [("every 5%+ gap", lambda d, r, t: True), ("gap 8%+", lambda d, r, t: r["gap"] <= -8),
            ("strong yesterday, gap 8%+", lambda d, r, t: up(d) and r["gap"] <= -8),
            ("strong yesterday, gap 8%+, opens under 50 EMA", lambda d, r, t: up(d) and r["gap"] <= -8 and d["o_u50"]),
            ("mirror of play 1b", p1b),
            ("downtrend yesterday, gap 8%+", lambda d, r, t: d["u50"] and d["u200"] is True and r["gap"] <= -8)]
    for name, cond in sets:
        ts = M.sel("3", "rh", cond)
        table(name, ts)
        by_year("EMA 10", ts, 4)
        by_year("EMA 21", ts, 5)
    print("\n== ordinary days only ==")
    for name, cond in sets:
        table(name + " (ordinary)", [t for t in M.sel("3", "rh", cond) if t[0].split()[0] not in M.MD])
    print("\n== the close short (mirror of play 2): short at the gap day's close, stop at the gap day's high ==")
    for name, cond in sets:
        close_table(name, close_short(cond))
        close_table("  closed in the lowest quarter of its range", close_short(cond, weak=lambda pos, row: pos <= 0.25))
        close_table("  closed in the top half of its range", close_short(cond, weak=lambda pos, row: pos >= 0.5))
    print("\n== the later break of the range low (3-min range, stop range high, out at the close) ==")
    def late(key_suffix, cond):
        out = []
        for key, row in R.ROWS.items():
            t = row.get("3" + key_suffix)
            tr = row.get("3")
            if row["o"] < 10 or not t or not tr or t["risk_pct"] < R.MIN_RISK:
                continue
            d = M.facts(key, row, dict(tr, entry=t["entry"]))
            if d is None or not cond(d, row, tr):
                continue
            out.append((key, row, dict(tr, entry=t["entry"], m=t["m"]), {"r": t["r"], "stop": t["stop"], "stopped": t["stopped"], "risk_pct": t["risk_pct"], "exit": t["exit"]}))
        return out
    for name, cond in sets:
        M.show(name + ": first break (part 1)", M.sel("3", "rh", cond))
        M.show("   a break at 9:45 or later", late("L15", cond))
        M.show("   a break at 10:00 or later", late("L30", cond))
