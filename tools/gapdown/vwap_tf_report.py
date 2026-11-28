#!/usr/bin/env python3
"""Play 2 (the opening low broken, the pop to VWAP under the range high fails) by candle size.

  python3 vwap_tf_report.py trades_out.json features.json gaps_clean.json reasons.json scen.json vwap_tf.json"""
import json, sys
tf_path = sys.argv[6]
sys.argv = sys.argv[:6]
import scen_report as S
TF = json.load(open(tf_path))
COST = 0.001
up = S.up
LABEL = {"1": "1-minute", "2": "2-minute", "3": "3-minute", "5": "5-minute", "10": "10-minute", "15": "15-minute",
         "3w4": "3-minute, 4 candles of patience", "1w14": "1-minute, 14 candles of patience"}


def play2(size, before=90):
    S.SC = {k: {"vwap": v[size]} for k, v in TF.items() if size in v}
    return S.play2(before)


def row(label, ts):
    s = S.stat(ts)
    if not s or s["n"] < 25:
        return f"| {label} | {len(ts)} | | | | | | | |"
    net = sum(t[3]["r"] - COST * t[3]["entry"] / (t[3]["stop"] - t[3]["entry"]) for t in ts) / len(ts)
    rs = sorted(t[3]["r"] for t in ts)
    return (f"| {label} | {s['n']:,} | {s['win']:.1f}% | {s['avg']:+.2f} | {s['total']:+.0f} | {net:+.2f} | {s['risk']:.1f}% | "
            f"{'/'.join(f'{v:+.0f}' for v in s['years'])} | {sum(rs[-10:]):+.0f} |")


HEAD = "| Candle | Trades | Win | Avg R | Total R | Avg R after costs | Median stop distance | R by year 23/24/25/26 | Top 10 trades R |\n|---|---|---|---|---|---|---|---|---|"
SETS = [("earnings + gap 8%+, signal before 11:00", lambda d: d["earn"] == 1 and d["gap"] <= -8, 90),
        ("earnings + gap 8%+, signal before 10:00", lambda d: d["earn"] == 1 and d["gap"] <= -8, 30),
        ("earnings + strong + gap 8%+, before 11:00", lambda d: d["earn"] == 1 and d["gap"] <= -8 and up(d), 90),
        ("earnings + strong + gap 8%+, before 10:00", lambda d: d["earn"] == 1 and d["gap"] <= -8 and up(d), 30),
        ("strong + gap 8%+ (any news), before 11:00", lambda d: d["gap"] <= -8 and up(d), 90),
        ("earnings + gap 5-8%, before 11:00", lambda d: d["earn"] == 1 and d["gap"] > -8, 90),
        ("every 5%+ gap, ordinary days, before 11:00", lambda d: d["day"] not in S.MD, 90)]
if __name__ == "__main__":
    for name, cond, before in SETS:
        print(f"\n### {name}")
        print(HEAD)
        for size in ("1", "2", "3", "5", "10", "15", "3w4", "1w14"):
            print(row(LABEL[size], [t for t in play2(size, before) if cond(t[2])]))
    print("\n### earnings + gap 8%+: when the signal comes, 3-minute vs 5-minute candles")
    print(HEAD.replace("| Candle |", "| Candle, signal time |"))
    for size in ("3", "5"):
        ts = [t for t in play2(size, 400) if t[2]["earn"] == 1 and t[2]["gap"] <= -8]
        for lab, lo, hi in (("9:36-9:45", 0, 15), ("9:45-10:00", 15, 30), ("10:00-10:30", 30, 60), ("10:30-11:00", 60, 90), ("after 11:00", 90, 400)):
            print(row(f"{LABEL[size]}, {lab}", [t for t in ts if lo <= t[2]["m"] < hi]))
    # same days, both sizes: which fires first and how they compare
    a = {t[0]: t for t in play2("3") if t[2]["earn"] == 1 and t[2]["gap"] <= -8}
    b = {t[0]: t for t in play2("5") if t[2]["earn"] == 1 and t[2]["gap"] <= -8}
    both = set(a) & set(b)
    print(f"\nearnings + gap 8%+, before 11:00: 3-minute fires on {len(a)} days, 5-minute on {len(b)}, both on {len(both)}; "
          f"on those: 3-minute avg {sum(a[k][3]['r'] for k in both) / len(both):+.2f}R, 5-minute avg {sum(b[k][3]['r'] for k in both) / len(both):+.2f}R; "
          f"3-minute earlier on {sum(1 for k in both if a[k][2]['m'] < b[k][2]['m'])}, same minute {sum(1 for k in both if a[k][2]['m'] == b[k][2]['m'])}, later {sum(1 for k in both if a[k][2]['m'] > b[k][2]['m'])}")
    only3, only5 = set(a) - set(b), set(b) - set(a)
    print(f"3-minute only: {len(only3)} trades avg {sum(a[k][3]['r'] for k in only3) / max(1, len(only3)):+.2f}R; 5-minute only: {len(only5)} trades avg {sum(b[k][3]['r'] for k in only5) / max(1, len(only5)):+.2f}R")
