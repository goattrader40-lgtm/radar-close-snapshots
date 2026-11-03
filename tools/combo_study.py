"""Study (Nov 3 2026): group rank x RS x Trend on every tested entry (radar-data probe_combo_tags.json + the trade files).
   RD=dir python3 tools/combo_study.py OUT.json [shuffles]  ->  every combination (n, avg R, both halves) and the luck line
   (the same search on shuffled tags: the best lift luck finds per entry, for cells of 50 / 150 / 300+ trades)"""
import json, sys, itertools, random
import numpy as np
RD = (__import__("os").environ.get("RD") or "/tmp/rd") + "/"   # radar-data probe_combo_tags.json, probe_buypoints.json, probe_launch_live.json
tags = json.load(open(RD + "probe_combo_tags.json"))
F = tags["fields"]; T = tags["tags"]
def tg(t, when):
    v = T.get(f'{t["symbol"]}|{t["date"]}')
    if not v: return None
    d = dict(zip(F, v))
    w = "prev" if when == "prev" else "day"
    return dict(g=d["group_" + w], rs=d["rs_" + w], tr=d["trend_" + w], trd=d["trend_" + w + "_days"])
bp = json.load(open(RD + "probe_buypoints.json"))["trades"]
lv = json.load(open(RD + "probe_launch_live.json"))["trades"]
BRK = {"base breakout", "bull flag breakout", "bull pennant breakout", "pattern pivot", "pop"}
PB = {"retest", "21 EMA retest", "21 EMA undercut & reclaim", "50 EMA undercut & reclaim", "breakout undercut & reclaim", "push", "follow-through"}
E = []   # (entry, kind, R, win, ran20, date, tags)
for t in lv:
    x = tg(t, "prev")
    if x: E.append(("launch day live ORH", "launch day", t["R"], t["win"], None, t["date"], x))
for t in bp:
    close_sig = t["bought"] == "close"
    if "min5_R" in t:
        x = tg(t, "day" if close_sig else "prev")      # a close signal's 5-min buy is the next morning
        if x: E.append(("5-min ORH", t["buy_point"], t["min5_R"], t["min5_win"], t["ran20"], t["date"], x))
    if "close_R" in t:
        x = tg(t, "day")
        if x: E.append(("bought at the close", t["buy_point"], t["close_R"], t["close_win"], t["ran20"], t["date"], x))
dates = sorted(e[5] for e in E); MID = dates[len(dates)//2]
GF = {"any group": lambda g: True, "Top/Strong": lambda g: g is not None and g >= .90, "Top": lambda g: g is not None and g >= .97, "not top 10%": lambda g: g is None or g < .90}
RF = {"any RS": lambda r: True, "RS 97+": lambda r: r is not None and r >= .97, "RS 90+": lambda r: r is not None and r >= .90, "RS 80+": lambda r: r is not None and r >= .80, "RS under 80": lambda r: r is None or r < .80}
POS = {"Up", "Turn up", "Reclaim", "Resting"}
TF = {"any trend": lambda t: True, "Up": lambda t: t == "Up", "Up/Turn up": lambda t: t in ("Up", "Turn up"), "positive trend": lambda t: t in POS, "Negative": lambda t: t == "Negative", "no label": lambda t: t == ""}
KF = {"all": lambda k: True, "breakouts": lambda k: k in BRK, "pullbacks": lambda k: k in PB}
def kinds_for(entry):
    ks = sorted({e[1] for e in E if e[0] == entry})
    return [("all", KF["all"])] + ([("breakouts", KF["breakouts"]), ("pullbacks", KF["pullbacks"])] if entry != "launch day live ORH" else []) + [(k, (lambda kk: lambda k: k == kk)(k)) for k in ks if k != "launch day"]
def cells(rows, labels=None):
    out = []
    for entry in sorted({e[0] for e in rows}):
        R0 = [e for e in rows if e[0] == entry]
        for kn, kf in kinds_for(entry):
            R1 = [e for e in R0 if kf(e[1])]
            for (gn, gf), (rn, rf), (tn, tf) in itertools.product(GF.items(), RF.items(), TF.items()):
                R = [e for e in R1 if gf(e[6]["g"]) and rf(e[6]["rs"]) and tf(e[6]["tr"])]
                if len(R) < 30: continue
                r = np.array([e[2] for e in R])
                h1 = [e[2] for e in R if e[5] < MID]; h2 = [e[2] for e in R if e[5] >= MID]
                out.append(dict(entry=entry, kind=kn, group=gn, rs=rn, trend=tn, n=len(R), avgR=float(r.mean()), medR=float(np.median(r)),
                                t=float(r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))) if len(r) > 2 and r.std() > 0 else 0,
                                win=100 * np.mean([e[3] for e in R]), ran20=None if R[0][4] is None else 100 * np.mean([e[4] for e in R if e[4] is not None]),
                                h1=float(np.mean(h1)) if len(h1) >= 10 else None, h2=float(np.mean(h2)) if len(h2) >= 10 else None, n1=len(h1), n2=len(h2), totR=float(r.sum())))
    return out
if __name__ == "__main__":
    C = cells(E)
    json.dump(dict(mid=MID, n=len(E), cells=C), open(sys.argv[1], "w"))
    # the luck line: shuffle the tags among trades of the same entry and kind, best avgR of cells with n>=50
    if len(sys.argv) > 2:
        random.seed(1); mx = []
        for it in range(int(sys.argv[2])):
            by = {}
            for i, e in enumerate(E): by.setdefault((e[0], e[1]), []).append(i)
            E2 = list(E)
            for k, ix in by.items():
                tg_ = [E[i][6] for i in ix]; random.shuffle(tg_)
                for i, x in zip(ix, tg_): E2[i] = E[i][:6] + (x,)
            c2 = cells(E2)
            base = {(b["entry"], b["kind"]): b["avgR"] for b in c2 if b["group"] == "any group" and b["rs"] == "any RS" and b["trend"] == "any trend"}
            mx.append({f"{en}|{m}": max([c["avgR"] - base[(c["entry"], c["kind"])] for c in c2 if c["entry"] == en and c["n"] >= m and c["h1"] is not None and c["h2"] is not None and c["h1"] > 0 and c["h2"] > 0] or [0]) for en in {e[0] for e in E} for m in (50, 150, 300)})
            print(it, mx[-1], flush=True)
        json.dump(mx, open(sys.argv[1] + ".null.json", "w"))
