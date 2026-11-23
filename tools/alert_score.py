# Score today's buy alerts on the exact minute bars.
#   python3 score.py <alerts.json> <probe_alertbars.json.gz> <out.json>
# Entry = the price the alert quoted; stop = the day's low at the alert (the alert's own stop when it gave one);
# after the alert: stopped (traded under the stop) or not, the best gain reached before that, the close.
import collections, gzip, json, re, sys

al = json.load(open(sys.argv[1]))
pb = json.load(gzip.open(sys.argv[2], "rt"))
B = pb["rows"]
LIVE = json.load(open(sys.argv[4]))["rows"] if len(sys.argv) > 4 else {}
FULL = pb.get("bars_to") == "16:00"

FAMILY = {  # kind -> (family label, order)
    "epb10": "EP pullback BUY (10 EMA)", "epb21": "EP pullback BUY (21 EMA)",
    "ep": "Episodic pivot", "power": "Power day",
    "mbo": "Morning breakout (in trend)", "mbo2": "Breakout, not in trend",
    "breakout": "Pattern breakout (Launches)", "catalyst": "Catalyst gap", "push": "Push out of the 10 / 21 EMA",
    "gob1": "Gap out of base (1-min high)", "gob5": "Gap out of base (5-min high)",
    "ema21strong": "21 EMA reclaim, strong day (heads-up)",
    "start": "Start day", "rangebo": "Falling-range breakout", "basebreak": "Base breakout after a catalyst", "s3": "3-SETUPS trigger",
}


def price_of(kind, it):
    t, m = it["title"], it["msg"]
    if kind in ("mbo", "mbo2"):
        x = re.match(r"\$([\d,.]+)", m)
    elif kind in ("ep", "power"):
        x = re.search(r"\$([\d,.]+) over its 21-day closing high", m)
    elif kind == "breakout":
        x = re.match(r"\$([\d,.]+) over the", m)
    elif kind == "catalyst":
        x = re.search(r"vol [\d.]+x for the time of day · \$([\d,.]+)", m)
    elif kind in ("push", "ema21strong"):
        x = re.search(r"now \$([\d,.]+)", m)
    elif kind in ("gob1", "gob5"):
        x = re.match(r"\$([\d,.]+) over the", m)
    elif kind in ("start", "rangebo"):
        x = re.search(r"\$([\d,.]+) over the", m)
    elif kind in ("epb10", "epb21"):
        x = re.search(r"\$([\d,.]+)\s*$", t)
    else:
        x = re.search(r"\$([\d,.]+)", m)
    return float(x.group(1).replace(",", "")) if x else None


def stop_of(kind, it):
    m = it["msg"]
    x = (re.search(r"stop under the day's low \$([\d,.]+)", m) or re.search(r"stop: today's low \$([\d,.]+)", m)
         or re.search(r"stop \$([\d,.]+), (?:its|today's) low", m))
    return float(x.group(1).replace(",", "")) if x else None


rows = []
skipped = collections.Counter()
for it in al["items"]:
    k = it["key"]
    if ":" not in k or k.startswith(("grp:", "thm:", "summary:", "mbatch")):
        continue
    sym, kind = k.split(":", 1)
    if kind not in FAMILY:
        continue
    bars = B.get(sym)
    if not bars:
        skipped["no bars " + sym] += 1
        continue
    hh, mm = map(int, it["time"].split(":"))
    ma = hh * 60 + mm - 570                       # the alert's minute (the check ran in it)
    entry = price_of(kind, it)
    before = [b for b in bars if b[0] <= ma]     # the day's low up to and including the alert's minute
    after = [b for b in bars if b[0] > ma]       # what happened from the next minute on
    if entry is None or not before or not after:
        skipped[f"no price / bars around the alert {k}"] += 1
        continue
    low0 = min(b[3] for b in before)
    stop_txt = stop_of(kind, it)
    stop = min(stop_txt, low0) if stop_txt else low0
    # the quoted price can be a touch off the minute bars; keep the entry inside the alert minute's neighbourhood
    if stop >= entry:
        stop = min(low0, entry * 0.999)
        if stop >= entry:
            skipped[f"stop at or over the entry {k}"] += 1
            continue
    risk = entry - stop
    peak, stopped_at, t_peak = entry, None, None
    for b in after:
        if b[3] < stop:
            stopped_at = b[0]
            break
        if b[2] > peak:
            peak, t_peak = b[2], b[0]
    close = (LIVE.get(sym) or [None])[0] if FULL else None
    close = close or bars[-1][4]
    hhmm = lambda m: f"{(570 + m) // 60:02d}:{(570 + m) % 60:02d}"
    r_close = -1.0 if stopped_at is not None else (close - entry) / risk
    orh5 = max((b[2] for b in bars if b[0] < 5), default=None)
    rows.append(dict(orh5=orh5, over_orh=bool(orh5 and entry > orh5), sym=sym, kind=kind, fam=FAMILY[kind], time=it["time"], entry=entry, stop=round(stop, 4), stop_from="alert" if stop_txt else "day's low",
                     risk_pct=round(100 * risk / entry, 2), stopped=hhmm(stopped_at) if stopped_at is not None else None,
                     peak_pct=round(100 * (peak / entry - 1), 2), peak_r=round((peak - entry) / risk, 2), peak_at=hhmm(t_peak) if t_peak is not None else None,
                     close=close, close_pct=round(100 * (close / entry - 1), 2), r=round(r_close, 2),
                     day_low=min(b[3] for b in bars), day_high=max(b[2] for b in bars),
                     result="failed" if stopped_at is not None else "worked" if close > entry else "held, no gain"))

json.dump(dict(full=FULL, bars_to=pb.get("bars_to"), rows=rows, skipped=dict(skipped)), open(sys.argv[3], "w"), indent=0)
print("bars to", pb.get("bars_to"), "| alerts scored", len(rows), "| skipped", dict(skipped), "| missing bars", pb.get("missing"), "| errors", pb.get("errors"))
order = list(dict.fromkeys(FAMILY.values()))
print(f"\n{'family':34} {'n':>4} {'worked':>7} {'flat':>5} {'failed':>7} {'+1R':>5} {'+2R':>5} {'avg R':>7} {'avg % close':>11} {'avg peak %':>10}")
tot = collections.Counter()
for fam in order:
    rs = [r for r in rows if r["fam"] == fam]
    if not rs:
        continue
    n = len(rs)
    w, f, h = sum(r["result"] == "worked" for r in rs), sum(r["result"] == "failed" for r in rs), sum(r["result"] == "held, no gain" for r in rs)
    r1, r2 = sum(r["peak_r"] >= 1 for r in rs), sum(r["peak_r"] >= 2 for r in rs)
    held = [r for r in rs if r["result"] != "failed"]
    print(f"{fam:34} {n:4} {w:7} {h:5} {f:7} {r1:5} {r2:5} {sum(r['r'] for r in rs) / n:7.2f} {sum((r['close_pct'] if not r['stopped'] else -r['risk_pct']) for r in rs) / n:11.2f} {sum(r['peak_pct'] for r in rs) / n:10.2f}")
