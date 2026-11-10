# Blind test (Nov 10 2026): 20 random launches outside tools/examples.txt, read day by day by the engine.
# Run from a folder holding radar-data stocks.json; writes blind/data.json. The page: template.html with __DATA__ = that JSON
# (status lines "In the base" / "Below the 21 EMA" left out). Seed 1109, launches Jun 1 - Sep 10 2026, 40 sessions each.
import sys, json, time, random, warnings
warnings.filterwarnings("ignore")
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, R + "/scanner"); sys.path.insert(0, R + "/tools")
import launch
SIGNALS = ("Launch day", "breakout", "Breakout", "Retest", "Tight", "Pop", "Flag", "Bull flag", "Bull pennant", "Pennant", "Push", "21 EMA retest", "21 EMA undercut", "50 EMA undercut", "try of")
A, groups, GS, cal, S = launch.load(R + "/history/bars_2y.json.gz", "stocks.json")
ev = launch.detect(A, groups, GS, cal, S)
used = {l.split()[0] for l in open(R + "/tools/examples.txt") if l.strip() and not l.startswith("#")}
meta = {r["symbol"]: r for r in json.load(open("stocks.json"))}
cand = [(s, i) for s, i, k, gs, gn in ev if "2026-06-01" <= A[s].st.dates[i] <= "2026-09-10" and s not in used]
print("launches in window", len(cand), "attrs", [x for x in dir(A[cand[0][0]]) if x.startswith("e")])
random.seed(1109); random.shuffle(cand)
out, seen = [], set()
for s, i0 in cand:
    if s in seen or len(out) >= 20: continue
    seen.add(s)
    a = A[s]; st = a.st
    i1 = min(len(st.dates) - 1, i0 + 40)
    t = time.time(); reads = []
    for j in range(i0, i1 + 1):
        f = launch.follow(a, i0, j)
        if j == i0 or any(w in f["stage"] for w in SIGNALS):
            reads.append(dict(d=st.dates[j], c=round(float(st.c[j]), 2), leg=f["leg"], read=f["stage"], bp=f["buy_point"], pat=f["pattern"]))
    b0 = max(0, i0 - 90)
    out.append(dict(sym=s, ex=meta.get(s, {}).get("exchange", ""), name=meta.get(s, {}).get("name", ""), launch=st.dates[i0], grade=launch.grade(a, i0),
                    bars=[[st.dates[j]] + [round(float(x[j]), 2) for x in (st.o, st.h, st.l, st.c)] + [int(st.v[j])] for j in range(b0, i1 + 1)],
                    e10=[round(float(a.e10[j]), 2) for j in range(b0, i1 + 1)] if hasattr(a, "e10") else None,
                    e21=[round(float(a.e21[j]), 2) for j in range(b0, i1 + 1)],
                    e50=[round(float(a.e50[j]), 2) for j in range(b0, i1 + 1)] if hasattr(a, "e50") else None,
                    reads=reads))
    print(s, st.dates[i0], len(reads), "reads", round(time.time() - t), "s", flush=True)
json.dump(out, open("blind/data.json", "w"))
print("done", sum(len(x["reads"]) for x in out), "reads")
