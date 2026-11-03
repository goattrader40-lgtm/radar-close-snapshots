import json, itertools, numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
RD=(__import__("os").environ.get("RD") or "/tmp/rd")+"/"
tg=json.load(open(RD+"probe_combo_tags.json")); F=tg["fields"]; T=tg["tags"]
luck=json.load(open("tools/combo_luck.json"))
def tag(t, w):
    v=T.get(f'{t["symbol"]}|{t["date"]}')
    if not v: return None
    d=dict(zip(F,v)); return dict(g=d["group_"+w], rs=d["rs_"+w], tr=d["trend_"+w])
bp=json.load(open(RD+"probe_buypoints.json"))["trades"]; lv=json.load(open(RD+"probe_launch_live.json"))["trades"]
BRK={"base breakout","bull flag breakout","bull pennant breakout","pattern pivot","pop"}
PB={"retest","21 EMA retest","21 EMA undercut & reclaim","50 EMA undercut & reclaim","breakout undercut & reclaim","push","follow-through"}
E=[]  # entry, kind, R, win, pct, ran20, date, sym, tags
for t in lv:
    x=tag(t,"prev")
    if x: E.append(dict(entry="Launch day (live alert, 5-min ORH)",kind="launch day",R=t["R"],win=t["win"],pct=t["result_pct"],ran20=None,date=t["date"],sym=t["symbol"],**x))
for t in bp:
    cs=t["bought"]=="close"
    if "min5_R" in t:
        x=tag(t,"day" if cs else "prev")
        if x: E.append(dict(entry="Buy point, 5-min ORH",kind=t["buy_point"],R=t["min5_R"],win=t["min5_win"],pct=t["min5_result_pct"],ran20=t["ran20"],date=t["date"],sym=t["symbol"],**x))
    if "close_R" in t:
        x=tag(t,"day")
        if x: E.append(dict(entry="Buy point, bought at the close",kind=t["buy_point"],R=t["close_R"],win=t["close_win"],pct=t["close_result_pct"],ran20=t["ran20"],date=t["date"],sym=t["symbol"],**x))
MID=sorted(e["date"] for e in E)[len(E)//2]
TS=lambda e:e["g"] is not None and e["g"]>=.9
TOP=lambda e:e["g"] is not None and e["g"]>=.97
RS=lambda e,v:(e["rs"] or 0)>=v
def stats(R):
    if not R: return None
    r=np.array([e["R"] for e in R]); p=np.array([e["pct"] for e in R]); r20=[e["ran20"] for e in R if e["ran20"] is not None]
    h1=[e["R"] for e in R if e["date"]<MID]; h2=[e["R"] for e in R if e["date"]>=MID]
    return dict(n=len(R), won=100*np.mean([e["win"] for e in R]), avg=p.mean(), med=float(np.median(p)), avgR=r.mean(), totR=r.sum(),
                ran20=100*np.mean(r20) if r20 else None, h1=np.mean(h1) if len(h1)>=10 else None, h2=np.mean(h2) if len(h2)>=10 else None, n1=len(h1), n2=len(h2))
HDR=["Count","Won","Avg trade","Median","Avg R","Total R","Ran 20%+","1st half avg R (to May 8 2026)","2nd half avg R","Both halves +"]
def vals(s):
    both=None if s["h1"] is None or s["h2"] is None else ("yes" if s["h1"]>0 and s["h2"]>0 else "no")
    return [s["n"], s["won"]/100, s["avg"]/100, s["med"]/100, s["avgR"], s["totR"], None if s["ran20"] is None else s["ran20"]/100, s["h1"], s["h2"], both]
GRN, RED, BOLD = Font(color="2E7D32"), Font(color="C62828"), Font(bold=True)
HFILL=PatternFill("solid", fgColor="EDE7DD"); SFILL=PatternFill("solid", fgColor="F7F3EC"); PICK=PatternFill("solid", fgColor="E3F1E4")
wb=Workbook(); wb.remove(wb.active)
def sheet(name, sections, first_col="Launches", widths=None, note=None):
    ws=wb.create_sheet(name[:31]); row=1
    if note:
        ws.cell(row=1,column=1,value=note).alignment=Alignment(wrap_text=True, vertical="top"); ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=11); ws.row_dimensions[1].height=60; row=3
    for title, rows in sections:
        c=ws.cell(row=row,column=1,value=title); c.font=Font(bold=True,size=12); row+=1
        for j,h in enumerate([first_col]+HDR):
            c=ws.cell(row=row,column=j+1,value=h); c.font=BOLD; c.fill=HFILL; c.alignment=Alignment(wrap_text=True)
        row+=1
        for lab, R, hl in rows:
            s=stats(R)
            if not s: continue
            ws.cell(row=row,column=1,value=lab)
            for j,v in enumerate(vals(s)):
                c=ws.cell(row=row,column=j+2,value=v)
                if j in (1,2,3,6): c.number_format="0.0%" if j!=1 and j!=6 else "0%"
                if j in (4,5,7,8): c.number_format="+0.00;-0.00" if j!=5 else "+0;-0"
                if j in (2,3,4,5,7,8) and isinstance(v,(int,float)): c.font=GRN if v>0 else RED if v<0 else Font()
                if j==9: c.font=GRN if v=="yes" else RED
            if hl:
                for j in range(1,12): ws.cell(row=row,column=j).fill=PICK
                ws.cell(row=row,column=1).font=BOLD
            row+=1
        row+=1
    ws.column_dimensions["A"].width=58
    for j in range(2,12): ws.column_dimensions[get_column_letter(j)].width=12
    ws.freeze_panes="B1" if not note else None
    return ws
L=[e for e in E if e["entry"].startswith("Launch")]
CP=[e for e in E if e["entry"].endswith("close") and e["kind"] in PB]
OP=[e for e in E if e["entry"].endswith("ORH") and e["kind"] in PB]
OB=[e for e in E if e["entry"].endswith("ORH") and e["kind"] in BRK]
CB=[e for e in E if e["entry"].endswith("close") and e["kind"] in BRK]
CPOP=[e for e in E if e["entry"].endswith("close") and e["kind"]=="pop"]
GT=lambda R:[("★ Top group (top 3%)",[e for e in R if TOP(e)],0),("Strong group (3-10%)",[e for e in R if TS(e) and not TOP(e)],0),("other groups",[e for e in R if not TS(e)],0)]
RB=lambda R:[("RS 97+",[e for e in R if RS(e,.97)],0),("RS 90-96",[e for e in R if RS(e,.9) and not RS(e,.97)],0),("RS 80-89",[e for e in R if RS(e,.8) and not RS(e,.9)],0),("RS under 80",[e for e in R if not RS(e,.8)],0)]
TB=lambda R:[("Trend "+(x or "no label"),[e for e in R if e["tr"]==x],0) for x in ("Up","Turn up","Reclaim","Resting","Negative","")]
# Top 3
top=[("1. Pullback buy points, bought at the close: Top/Strong group + RS 80+ + Trend Up",
      [("all pullback buy points (bought at the close)",CP,0),("+ Top/Strong group",[e for e in CP if TS(e)],0),("+ Top/Strong + Trend Up",[e for e in CP if TS(e) and e["tr"]=="Up"],0),
       ("+ Top/Strong + Trend Up + RS 80+  ← OPTION 1",[e for e in CP if TS(e) and e["tr"]=="Up" and RS(e,.8)],1),("   of them: retest",[e for e in CP if e["kind"]=="retest" and TS(e) and e["tr"]=="Up" and RS(e,.8)],0),
       ("   of them: push",[e for e in CP if e["kind"]=="push" and TS(e) and e["tr"]=="Up" and RS(e,.8)],0),("   of them: 21 EMA retest",[e for e in CP if e["kind"]=="21 EMA retest" and TS(e) and e["tr"]=="Up" and RS(e,.8)],0),
       ("Trend Up alone (no group filter)",[e for e in CP if e["tr"]=="Up"],0),("same combination, bought the next morning on the 5-min ORH",[e for e in OP if TS(e) and e["tr"]=="Up" and RS(e,.8)],0)]),
     ("2. Launch day (live alert, 5-min ORH): Trend Up the day before, or Top/Strong group launching from under the 21 EMA",
      [("all launch days (live)",L,0),("Trend Up the day before",[e for e in L if e["tr"]=="Up"],0),("Top/Strong group, under the 21 EMA the day before",[e for e in L if TS(e) and e["tr"]=="Negative"],0),
       ("either of the two  ← OPTION 2",[e for e in L if e["tr"]=="Up" or (TS(e) and e["tr"]=="Negative")],1),("skip: no Trend label the day before",[e for e in L if e["tr"]==""],0)]),
     ("3. Pop out of the consolidation, bought at the close (small sample)",
      [("all pops (bought at the close)",CPOP,0),("Trend Up  ← OPTION 3",[e for e in CPOP if e["tr"]=="Up"],1),("Top/Strong group",[e for e in CPOP if TS(e)],0),("other groups",[e for e in CPOP if not TS(e)],0)]),
     ("Not in the top 3: breakouts with your 5-min ORH entry",
      [("all breakouts (base, flag, pennant, pivot, pop)",OB,0),("base breakouts",[e for e in OB if e["kind"]=="base breakout"],0),("base breakouts, Top/Strong + RS 80+",[e for e in OB if e["kind"]=="base breakout" and TS(e) and RS(e,.8)],0),
       ("base breakouts, Top/Strong + RS 80+ + Trend Up",[e for e in OB if e["kind"]=="base breakout" and TS(e) and RS(e,.8) and e["tr"]=="Up"],0),("bull flag breakouts",[e for e in OB if e["kind"]=="bull flag breakout"],0),
       ("bull flag breakouts, Top/Strong + RS 80+",[e for e in OB if e["kind"]=="bull flag breakout" and TS(e) and RS(e,.8)],0)])]
note=("Combination study, Nov 3 2026 (branch test/combo). Every buy point the Launches tab gave Aug 2025 - Oct 2026 and every launch-day alert, "
      "traded with your management (1/3 at +2 ADR, 1/3 at +5 ADR, runners out on a 21 EMA close; stop under the day's low, or the 5-minute low on the ORH entry). "
      "Group / RS / Trend as the portal showed them: at the signal day's close for a close buy, the close before for a launch-day or breakout buy. "
      "Avg trade / Median = % per trade; R = result / risk. Kept only when both halves are positive. The luck line (sheet 'Luck check'): the best lift a search on shuffled labels finds.")
sheet("Top 3", top, "Combination", note=note)
sheet("Launch day (live ORH)", [("By group",GT(L)),("By RS (the close before)",RB(L)),("By Trend (the close before)",TB(L)),
      ("Group x Trend",[(f"{g} + Trend {t or 'no label'}",[e for e in L if gf(e) and e["tr"]==t],0) for g,gf in (("Top/Strong",TS),("other groups",lambda e:not TS(e))) for t in ("Up","Negative","Resting","Reclaim","")])])
sheet("Pullbacks (close)", [("By buy point",[(k,[e for e in CP if e["kind"]==k],0) for k in sorted(PB)]),("By group",GT(CP)),("By RS",RB(CP)),("By Trend",TB(CP)),
      ("Group x RS x Trend",[(f"{g} + {rn} + Trend {t}",[e for e in CP if gf(e) and RS(e,rv) and e["tr"]==t],0) for g,gf in (("Top/Strong",TS),("other groups",lambda e:not TS(e))) for rn,rv in (("RS 80+",.8),("any RS",0)) for t in ("Up","Negative")])])
sheet("Pullbacks (next-day ORH)", [("By buy point",[(k,[e for e in OP if e["kind"]==k],0) for k in sorted(PB)]),("By group",GT(OP)),("By RS",RB(OP)),("By Trend",TB(OP))])
sheet("Breakouts (5-min ORH)", [("By buy point",[(k,[e for e in OB if e["kind"]==k],0) for k in sorted(BRK)]),("By group",GT(OB)),("By RS",RB(OB)),("By Trend",TB(OB))])
sheet("Breakouts (close)", [("By buy point",[(k,[e for e in CB if e["kind"]==k],0) for k in sorted(BRK)]),("By group",GT(CB)),("By RS",RB(CB)),("By Trend",TB(CB))])
# all combinations
cells=json.load(open("tools/combo_cells.json"))["cells"]
base={(c["entry"],c["kind"]):c["avgR"] for c in cells if c["group"]=="any group" and c["rs"]=="any RS" and c["trend"]=="any trend"}
EN={"launch day live ORH":"launch day live ORH","5-min ORH":"5-min ORH","bought at the close":"bought at the close"}
ws=wb.create_sheet("All combinations")
H=["Entry","Buy point","Group","RS","Trend","Count","Won","Avg R","Median R","Total R","Ran 20%+","1st half R","2nd half R","Lift vs all","Both halves +","Luck line (95%)","Beats luck"]
for j,h in enumerate(H): c=ws.cell(row=1,column=j+1,value=h); c.font=BOLD; c.fill=HFILL
r=2
for c in sorted(cells,key=lambda c:-c["avgR"]):
    lift=c["avgR"]-base[(c["entry"],c["kind"])]; m=300 if c["n"]>=300 else 150 if c["n"]>=150 else 50 if c["n"]>=50 else None
    ll=luck[f'{c["entry"]}|{m}']["p95"] if m else None; both=c["h1"] is not None and c["h2"] is not None and c["h1"]>0 and c["h2"]>0
    row=[c["entry"],c["kind"],c["group"],c["rs"],c["trend"],c["n"],c["win"]/100,c["avgR"],c["medR"],c["totR"],None if c["ran20"] is None else c["ran20"]/100,c["h1"],c["h2"],lift,"yes" if both else "no",ll,
         "yes" if (ll is not None and both and lift>=ll) else "no"]
    for j,v in enumerate(row):
        x=ws.cell(row=r,column=j+1,value=v)
        if j in (6,10): x.number_format="0%"
        if j in (7,8,11,12,13,15): x.number_format="+0.00;-0.00"
    r+=1
ws.auto_filter.ref=f"A1:Q{r-1}"; ws.freeze_panes="F2"
for j,w in enumerate([22,26,12,12,14,8,7,8,9,8,9,10,10,10,9,10,9]): ws.column_dimensions[get_column_letter(j+1)].width=w
ws=wb.create_sheet("Luck check")
ws.append(["Entry | cells of N+ trades","Luck median","Luck 95%","Luck 99%"])
for k,v in luck.items(): ws.append([k,v["median"],v["p95"],v["p99"]])
ws.append([]); ws.append(["The best extra R per trade a search over every group x RS x Trend combination finds on SHUFFLED labels (200 runs), among combinations positive in both halves."])
ws.column_dimensions["A"].width=40
for c in ws[1]: c.font=BOLD; c.fill=HFILL
out="tools/combo_results.xlsx"
wb.save(out); print(out)
# markdown for chat
for title, rows in top:
    print("\n**"+title+"**\n")
    print("| Combination | Count | Won | Avg trade | Median | Avg R | Ran 20%+ | 1st half R | 2nd half R |"); print("|---|---|---|---|---|---|---|---|---|")
    for lab,R,hl in rows:
        s=stats(R)
        if not s: continue
        f=lambda x,fmt: "–" if x is None else fmt.format(x)
        b="**" if hl else ""
        print(f'| {b}{lab.replace("  ← ","  ← ")}{b} | {s["n"]} | {s["won"]:.0f}% | {s["avg"]:+.1f}% | {s["med"]:+.1f}% | {b}{s["avgR"]:+.2f}{b} | {f(s["ran20"],"{:.0f}%")} | {f(s["h1"],"{:+.2f}")} | {f(s["h2"],"{:+.2f}")} |')
