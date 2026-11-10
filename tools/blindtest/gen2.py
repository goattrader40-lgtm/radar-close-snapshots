# Blind test 2 (Nov 10 2026): 20 new random launches (seed 1110, Jun 1 - Sep 10 2026), read by the test/cleanlaunch engine, a
# stock no longer read from the day the list rules take it off. Run from a folder holding radar-data stocks.json.
import sys, json, random, warnings, numpy as np
warnings.filterwarnings("ignore")
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import launch
L = launch.L
SIG = ("Launch day", "breakout", "Breakout", "Retest", "Tight", "Pop", "Flag", "Bull flag", "Bull pennant", "Pennant", "Push", "21 EMA retest", "21 EMA undercut", "50 EMA undercut", "try of")
A, groups, GS, cal, S = launch.load(R + "/history/bars_2y.json.gz", "stocks.json")
ev = launch.detect(A, groups, GS, cal, S)
used = {l.split()[0] for l in open(R + "/tools/examples.txt") if l.strip() and not l.startswith("#")}
used |= set("PGY REAL AVNT REPL PBF IBKR THC EGO KBH ALM VIAV IPGP VGNT NRIX ZETA MPWR FDS NET GLXY MTSI".split())
used |= set("AMD DELL MU TWLO UBER XYZ ZM NVDA SHOP SNDK TSLA NFLX NIO NTSK ZS INTC ARM EPAM APPN U ACN XMTR OKTA RHI RPD ATRC XERS PGNY PCOR APP VCEL KD CPRI GKOS UPBD XNCR WING DUOL".split())
meta = {r["symbol"]: r for r in json.load(open("stocks.json"))}
cand = [(s, i) for s, i, k, gs, gn in ev if "2026-06-01" <= A[s].st.dates[i] <= "2026-09-10" and s not in used]
print("launches in the window:", len(cand))
random.seed(1110); random.shuffle(cand)
def off_on(a, i0, j):
    st = a.st
    if j >= i0 + 3 and all(st.c[m] < a.e50[m] for m in (j - 2, j - 1, j)): return "3 closes in a row under the 50 EMA"
    if launch.under200(a, max(i0, j - L["off_200"]), j): return "2 closes in a row under the 200 SMA"
    if st.adr[j] < L["off_adr"]: return f"ADR {st.adr[j]:.1f}%, under 3.2%"
    if launch.stale(a, i0, j): return "62 sessions without a new high"
    return None
out, seen = [], set()
for s, i0 in cand:
    if s in seen or len(out) >= 20: continue
    seen.add(s); a = A[s]; st = a.st
    i1 = min(len(st.dates) - 1, i0 + 40); reads = []; last = i1
    for j in range(i0, i1 + 1):
        why = off_on(a, i0, j) if j > i0 else None
        if why:
            reads.append(dict(d=st.dates[j], c=round(float(st.c[j]), 2), leg=None, read="Taken OFF the list: " + why + ". No more reads or alerts for this launch.", bp=None, pat="")); last = min(i1, j + 8); break
        f = launch.follow(a, i0, j); t = f["stage"]
        if j == i0 or (any(w in t for w in SIG) and not t.startswith(("In the base", "Below the 21 EMA", "Closed under", "Running", "Consolidation"))):
            reads.append(dict(d=st.dates[j], c=round(float(st.c[j]), 2), leg=f["leg"], read=t, bp=f["buy_point"], pat=f["pattern"]))
    b0 = max(0, i0 - 90); rng = range(b0, last + 1)
    r2 = lambda v: None if v != v else round(float(v), 2)
    typ = "power day" if a.power(i0) else "reversal day" if a.reversal(i0) and not a.candidate(i0, catalyst=False) else "launch"
    out.append(dict(sym=s, ex=meta.get(s, {}).get("exchange", ""), name=meta.get(s, {}).get("name", ""), launch=st.dates[i0], grade=launch.grade(a, i0), typ=typ,
                    day=f"{a.chg[i0]:+.1f}%, gap {a.gap[i0]:+.1f}%, {a.rv[i0]:.1f}x volume",
                    bars=[[st.dates[j]] + [round(float(x[j]), 2) for x in (st.o, st.h, st.l, st.c)] + [int(st.v[j])] for j in rng],
                    e5=[r2(a.e5[j]) for j in rng], e10=[r2(a.e10[j]) for j in rng], e21=[r2(a.e21[j]) for j in rng], e50=[r2(a.e50[j]) for j in rng], s200=[r2(st.sma200[j]) for j in rng], reads=reads))
    print(s, st.dates[i0], typ, launch.grade(a, i0), len(reads), "reads", flush=True)
json.dump(out, open("blind/data2.json", "w"), separators=(",", ":"))
print("total reads", sum(len(x["reads"]) for x in out))
