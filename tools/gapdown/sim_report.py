#!/usr/bin/env python3
"""The replay's tables (sim_ebd.py's output next to the study's trades).   python3 sim_report.py SIM.json <work dir>"""
import collections, json, os, sys
sim = json.load(open(sys.argv[1]))
rows = json.load(open(os.path.join(sys.argv[2], "out_final3.json")))["rows"]
feats = json.load(open(os.path.join(sys.argv[2], "features.json")))


def st(rs):
    n = len(rs)
    if not n:
        return "no trades"
    w, l = [r for r in rs if r > 0], [r for r in rs if r <= 0]
    return (f"{n:>4} trades  win {100 * len(w) / n:>4.1f}%  avg win {sum(w) / max(1, len(w)):+.2f}R  avg loss {sum(l) / max(1, len(l)):+.2f}R  "
            f"EV {sum(rs) / n:+.3f}R  total {sum(rs):+.0f}R")


study = {}
for k, v in sim.items():
    row = rows[k]
    tr = row.get("3")
    if v["earn"] == 1 and row["gap"] <= -8 and tr and "t" in tr and tr.get("rh") and tr["rh"]["risk_pct"] >= 0.5:
        study[k] = (tr, tr["rh"])
al = {k: v for k, v in sim.items() if v["alert"]}
print("stock-days replayed", len(sim), "| alerts", len(al), "| on non-earnings days", sum(1 for v in al.values() if v["earn"] != 1))
print("study trades", len(study), "| alerted", len(set(study) & set(al)), "| alert without a study trade", len(set(al) - set(study)))
no = [k for k in study if k not in al]
why = collections.Counter("already back at the candle's high before a check (skipped)" if sim[k]["skip"] else "first break after 3:00 PM" if study[k][0]["m"] >= 330
                          else "never under the low at a check (a wick)" for k in no)
for w, n in why.most_common():
    ks = [k for k in no if ("skipped" in w) == bool(sim[k]["skip"]) and (("3:00" in w) == (study[k][0]["m"] >= 330 and not sim[k]["skip"]))]
    print(f"  no alert: {w}: {n}; the study's result on them {sum(study[k][1]['r'] for k in ks):+.0f}R")
print()
print("the study (short at the candle's low)        ", st([x[1]["r"] for x in study.values()]))
both = sorted(set(study) & set(al))
print("the alerted days, short at the candle's low  ", st([study[k][1]["r"] for k in both]))
print("the alerted days, short at the alert's price ", st([al[k]["alert"]["r"] for k in al]))
d = collections.Counter(min(al[k]["alert"]["m"] - study[k][0]["m"], 6) for k in both)
print("minutes from the break to the alert:", {(f"{m}" if m < 6 else "6+"): n for m, n in sorted(d.items())})
slip = sorted(100 * (1 - al[k]["alert"]["price"] / al[k]["alert"]["lv"]["orl"]) for k in al)
print(f"the alert's price under the candle's low: median {slip[len(slip) // 2]:.2f}%, 3 in 4 within {slip[int(len(slip) * .75)]:.2f}%, 9 in 10 within {slip[int(len(slip) * .9)]:.2f}%")
print()
g = collections.defaultdict(lambda: ([], []))
for k, v in al.items():
    a = v["alert"]
    f = feats.get(k) or {}
    pc = rows[k]["pc"]
    strong = bool(f.get("ema50") and f.get("sma200") and pc > f["ema50"] and pc > f["sma200"])
    tight = "TIGHT" in a["title"]
    for name in ("tight (candle under 0.8 ADR)" if tight else "wide (0.8 ADR or more)", "strong yesterday" if strong else "not strong yesterday",
                 ("tight + strong" if tight and strong else "tight, not strong" if tight else "wide + strong" if strong else "wide, not strong"),
                 "year " + k[:4], "alert " + ("9:33-9:45" if a["m"] < 15 else "9:45-10:30" if a["m"] < 60 else "10:30-12:00" if a["m"] < 150 else "12:00-3:00")):
        g[name][0].append(a["r"])
        if k in study:
            g[name][1].append(study[k][1]["r"])
for name in sorted(g):
    print(f"{name:<30} at the alert's price: {st(g[name][0])}   |  at the candle's low: {st(g[name][1])}")
print()
print("the box: alerts", len(al), "| stop seen", sum(1 for v in al.values() if v["stopped"]), "| stop touched on the 1-minute bars", sum(v["alert"]["stopped_bars"] for v in al.values()),
      "| BACK ON sent", sum(1 for v in al.values() if v.get("back")), "| over the low at the close (not stopped)", sum(1 for v in al.values() if v["lost"] and v["lost"]["why"] == "low"))
miss = [k for k, v in al.items() if v["alert"]["stopped_bars"] and not v["stopped"]]
print("stop touched but never seen by the box:", len(miss), miss[:10])
wrong = [k for k, v in al.items() if v["stopped"] and not v["alert"]["stopped_bars"]]
print("box says stopped, bars say no:", len(wrong), wrong[:10])
per_day = collections.Counter(k.split()[0] for k in al)
days = sorted(per_day.values())
print(f"alert days {len(per_day)}; alerts a day on those: median {days[len(days) // 2]}, most {days[-1]} ({per_day.most_common(3)})")
rd = {k: v for k, v in sim.items() if v.get("ready")}
if rd:
    print()
    ends = collections.Counter((v.get("ready_end") or {}).get("ebdr", {}).get("why", "open at the close") for v in rd.values())
    print("READY lines", len(rd), "| on non-earnings days", sum(1 for v in rd.values() if v["earn"] != 1), "| how they ended:", dict(ends))
    lag = collections.defaultdict(lambda: ([], []))
    for k, (tr, rh) in study.items():
        if k not in rd:
            continue
        d = tr["m"] - rd[k]["ready"][0]["m"]
        name = "the break in the READY minute itself" if d <= 0 else "the break 1 minute after READY" if d == 1 else "the break 2+ minutes after READY"
        lag[name][0].append(rh["r"])
        if rh["risk_pct"] / rows[k]["adr"] < 0.8:
            lag[name][1].append(rh["r"])
    for name in sorted(lag):
        print(f"{name:<38} at the candle's low: {st(lag[name][0])}   |  tight: {st(lag[name][1])}")

