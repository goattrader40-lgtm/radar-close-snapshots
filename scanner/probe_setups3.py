#!/usr/bin/env python3
"""The 2-year check of the new 3-SETUPS (your Nov 1 2026 design): are its buy points, on stocks without a launch day,
as good as the Launches ones?

  python3 scanner/probe_setups3.py --bars BARS.json.gz --stocks radar-data/stocks.json --out OUT.json

The Watchlist's feeder lists don't exist for past years, so they are rebuilt from the daily bars with each list's entry
rule (scanner/settings.json): 1-EP/GAP a gap over 5% on 2.5x volume, 1-UPDAY up 4%+ on 1x+ volume, 2-POOL the first close
back over the 50 EMA after 2+ under it or a momentum leader (1W 10%+, 1M 25%+, 3M 50%+, 6M 50%+ over the 200 SMA); all
with the standard filters (price $10+, liquid, ADR 3.5%+, over the 50 EMA, 30%+ over the 52-week low). A stock is then
read every day by the same rules as the evening scan (launch.s3_read) until it leaves: the 1-lists' gap / up-day low
lost, 15 sessions without reaching 3-SETUPS, 2-POOL under the 200 SMA, or the 3-SETUPS exits (2 closes under the 50 EMA,
62 sessions without a new high, ADR under 3.2%); 120 sessions at most.

Scored (ran 10% / 20% = the high within 20 sessions; failed = a close under the entry day's low within 5 sessions):
  Triggered today  bought at that day's close, by setup
  Ready            bought the next day if it trades over the trigger (at the open when it gaps over it), by setup;
                   how often the trigger is hit the next day
  Setting up       how often it reaches Ready or Triggered within 10 sessions
"""
import argparse, collections, datetime, json, multiprocessing, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402

L = launch.L
A = {}
FIRST = 0
GROUPS, GS, POS = {}, {}, {}


def feeder(a, i):
    """the feeder list a stock would come on at bar i (None = none)"""
    st = a.st
    c = st.c
    std = bool(a.liq_noadr[i] and st.adr[i] >= 3.5 and c[i] > a.e50[i] and c[i] >= st.low52[i] * 1.3)
    if std and a.gap[i] > 5 and a.rv[i] >= 2.5:
        return "1-EP/GAP"
    if std and a.chg[i] >= 4 and a.rv[i] >= 1:
        return "1-UPDAY"
    if a.liq_noadr[i] and st.adr[i] >= 3.5 and c[i] > a.e50[i] and c[i - 1] < a.e50[i - 1] and c[i - 2] < a.e50[i - 2]:
        return "2-POOL"
    if std and i >= 126 and ((c[i] / c[i - 5] - 1) >= 0.10 or (c[i] / c[i - 21] - 1) >= 0.25 or (c[i] / c[i - 63] - 1) >= 0.50
                             or ((c[i] / c[i - 126] - 1) >= 0.50 and c[i] > a.s200[i] and c[i] >= st.low52[i] * 1.5)):
        return "2-POOL"
    return None


def outcome(st, k, e):
    n = st.c.size
    hi = st.h[k:min(n, k + 20)].max()
    return dict(ran10=bool(hi >= e * 1.1), ran20=bool(hi >= e * 1.2), fail5=bool((st.c[k:min(n, k + 6)] < st.l[k]).any()),
                r20=float(100 * (st.c[k + 20] / e - 1)) if k + 20 < n else None)


def one(sym):
    a = A[sym]
    st = a.st
    n = st.c.size
    trig, ready, setting, seq = [], [], [], []
    i0, src, was_in, ever = None, None, False, False
    for j in range(max(a.start, FIRST), n - 21):
        if i0 is not None:
            end = (j - i0 > 120 or (st.c[j] < a.e50[j] and st.c[j - 1] < a.e50[j - 1])
                   or (src != "2-POOL" and st.c[j] < st.l[i0]) or (src != "2-POOL" and not ever and j - i0 >= 15)
                   or (src == "2-POOL" and st.c[j] < a.s200[j]) or (was_in and st.adr[j] < L["off_adr"]))
            if end:
                i0, was_in = None, False
        if i0 is None:
            f = feeder(a, j)
            if f:
                i0, src, was_in, ever = j, f, False, False
            continue
        x = launch.s3_read(a, i0, j, was_in)
        if x is None:
            was_in = False
            continue
        sec, setup, f, bp, away_adr, c, adr, tight, z = x
        was_in = ever = True
        seq.append((j, sec))
        if sec == "Triggered today":
            trig.append(dict(setup=setup, src=src, **outcome(st, j, st.c[j])))
        elif sec == "Ready" and bp:
            k = j + 1
            hit = bool(st.h[k] > bp)
            r = dict(setup=setup.split(" (")[0], src=src, hit=hit, tight=tight >= 2, sym=sym, k=k, bp=float(bp),
                     theme=launch.best_group(sym, POS[st.dates[j]], GROUPS, GS)[0] if st.dates[j] in POS else -1,
                     vb=f.get("vol_build"), age=j - i0, depth=f.get("base_depth_adr"), away=away_adr,
                     hi52=float(c / st.high52[j]) if st.high52[j] else None, adr=adr)
            if hit:
                r.update(outcome(st, k, max(float(st.o[k]), float(bp))))
            ready.append(r)
        else:
            setting.append(dict(setup=setup, j=j))
    # Setting up: reached Ready or Triggered within 10 sessions
    later = [j for j, s in seq if s != "Setting up"]
    for r in setting:
        r["became"] = any(r["j"] < j <= r["j"] + 10 for j in later)
    return sym, trig, ready, setting


def orh_trades(ready):
    """your entry on the Ready stocks the next day: over the 5-minute opening range high (at that high, or the bar's open
    when it jumps over it), the stop at the opening range low the whole way (a bar that breaks the high and that low
    counts as stopped); else out on the first close under the 21 EMA (as the Launches test)"""
    import probe_catalyst as pc                 # Alpaca's 5-minute bars (ALPACA_KEY_ID / ALPACA_SECRET)
    by_day = collections.defaultdict(list)
    for r in ready:
        by_day[A[r["sym"]].st.dates[r["k"]]].append(r)
    out = []
    for d, rs in sorted(by_day.items()):
        t0 = datetime.datetime.fromisoformat(d + "T09:30").replace(tzinfo=pc.NY)
        syms = sorted({r["sym"] for r in rs})
        bars = collections.defaultdict(list)
        for c0 in range(0, len(syms), 100):
            q = {"symbols": ",".join(pc.alp(s) for s in syms[c0:c0 + 100]), "timeframe": "5Min", "feed": "sip", "adjustment": "split",
                 "limit": 10000, "start": pc.iso(t0), "end": pc.iso(t0 + datetime.timedelta(minutes=390))}
            while True:
                res = pc.get("https://data.alpaca.markets/v2/stocks/bars", q)
                for s_, rows in (res.get("bars") or {}).items():
                    bars[s_].extend(rows)
                if not res.get("next_page_token"):
                    break
                q["page_token"] = res["next_page_token"]
            pc.time.sleep(0.3)
        for r in rs:
            b = bars.get(pc.alp(r["sym"]))
            if not b or not b[0]["t"].startswith(pc.iso(t0)[:16]):
                continue                                    # no 9:30 bar: left out
            a = A[r["sym"]]
            st, k = a.st, r["k"]
            orh, orl = b[0]["h"], b[0]["l"]
            m = next((x for x in range(1, len(b)) if b[x]["h"] > orh), None)
            t = dict(setup=r["setup"], src=r["src"], over_trigger=orh >= r["bp"], broke=m is not None,
                     **{x: r.get(x) for x in ("theme", "vb", "age", "depth", "away", "hi52", "adr")})
            if m is not None:
                t.update(variants(a, k, b, m, orh, orl))
            out.append(t)
    return out


def variants(a, k, b, m, orh, orl):
    """the same entry (over the 5-minute opening range high) with three exits:
      A  stop at the opening range low the whole way, else the first close under the 21 EMA
      B  your usual stop: under the entry day's low, from the next day; else the first close under the 21 EMA
      C  as A, but half sold at +2R (R = entry - opening range low) and the stop on the rest moved to the entry
    when one 5-minute bar or one day touches both the target and the stop, the stop counts first"""
    st, c, o, h, l, e21 = a.st, a.st.c, a.st.o, a.st.h, a.st.l, a.e21
    n = c.size
    buy = max(orh, b[m]["o"])
    rA = buy - orl
    out = {}

    def done(ret_pct, j_out, risk_pct, same_day):
        mg = 100 * (h[k:j_out + 1].max() / buy - 1)
        return dict(ret=ret_pct, mg=mg, risk=risk_pct, R=ret_pct / risk_pct if risk_pct else None,
                    mgR=mg / risk_pct if risk_pct else None, same_day_stop=same_day)
    # A
    if any(x["l"] <= orl for x in b[m:]):
        out["A"] = done(100 * (orl / buy - 1), k, 100 * rA / buy, True)
    else:
        j_out, sell = n - 1, c[-1]
        for j in range(k + 1, n):
            if l[j] <= orl:
                j_out, sell = j, min(orl, o[j]); break
            if c[j] < e21[j]:
                j_out, sell = j, c[j]; break
        out["A"] = done(100 * (sell / buy - 1), j_out, 100 * rA / buy, False)
    # B
    stop = float(l[k])
    j_out, sell = n - 1, c[-1]
    for j in range(k + 1, n):
        if l[j] <= stop:
            j_out, sell = j, min(stop, o[j]); break
        if c[j] < e21[j]:
            j_out, sell = j, c[j]; break
    out["B"] = done(100 * (sell / buy - 1), j_out, 100 * (buy - stop) / buy if stop < buy else None, False)
    # C
    tgt = buy + 2 * rA
    half, rest, j_out, same = None, None, None, False
    for x in b[m:]:
        if half is None:
            if x["l"] <= orl:
                rest, j_out, same = orl, k, True; break
            if x["h"] >= tgt:
                half = max(tgt, x["o"])
        elif x["l"] <= buy:
            rest, j_out = buy, k; break
    if rest is None:
        for j in range(k + 1, n):
            if half is None:
                if l[j] <= orl:
                    rest, j_out = min(orl, o[j]), j; break
                if h[j] >= tgt:
                    half = max(tgt, o[j])
                    if c[j] < e21[j]:
                        rest, j_out = c[j], j; break
                    continue
                if c[j] < e21[j]:
                    rest, j_out = c[j], j; break
            else:
                if l[j] <= buy:
                    rest, j_out = min(buy, o[j]), j; break
                if c[j] < e21[j]:
                    rest, j_out = c[j], j; break
        if rest is None:
            rest, j_out = c[-1], n - 1
    ret = 100 * ((0.5 * half + 0.5 * rest) / buy - 1) if half is not None else 100 * (rest / buy - 1)
    out["C"] = done(ret, j_out, 100 * rA / buy, same)
    out["C"]["took_half"] = half is not None
    return out


def orh_summ(ts, v="A"):
    if not ts:
        return dict(n=0)
    tr = [t[v] for t in ts if t["broke"]]
    if not tr:
        return dict(n=len(ts), broke_orh_pct=0)
    ret, mg = np.array([t["ret"] for t in tr]), np.array([t["mg"] for t in tr])
    R = np.array([t["R"] for t in tr if t["R"] is not None])
    mgR = np.array([t["mgR"] for t in tr if t["mgR"] is not None])
    return dict(n=len(ts), broke_orh_pct=round(100 * len(tr) / len(ts)), trades=len(tr),
                stopped_same_day_pct=round(100 * float(np.mean([t["same_day_stop"] for t in tr]))),
                win=round(100 * float(np.mean(ret > 0))), avg=round(float(ret.mean()), 1), med=round(float(np.median(ret)), 1),
                ran20=round(100 * float(np.mean(mg >= 20))), ran50=round(100 * float(np.mean(mg >= 50))),
                risk_med_pct=round(float(np.median([t["risk"] for t in tr if t["risk"]])), 1),
                avg_R=round(float(R.mean()), 2) if R.size else None, med_R=round(float(np.median(R)), 2) if R.size else None,
                reached_2R=round(100 * float(np.mean(mgR >= 2))) if mgR.size else None,
                reached_5R=round(100 * float(np.mean(mgR >= 5))) if mgR.size else None,
                **({"took_half_at_2R_pct": round(100 * float(np.mean([t["took_half"] for t in tr])))} if v == "C" else {}))


def splits(ts):
    """what separates the Ready trades that work: each bucket with exit A (stop at the 5-minute low) and C (half at +2R)"""
    def cut(name, test):
        sel = [t for t in ts if test(t)]
        a, c = orh_summ(sel, "A"), orh_summ(sel, "C")
        return {name: {k: a.get(k) for k in ("trades", "win", "avg", "med", "ran20", "ran50")} | {"C_win": c.get("win"), "C_avg": c.get("avg")}}
    tests = [("theme leading", lambda t: t["theme"] == 2), ("theme turning up", lambda t: t["theme"] == 1),
             ("theme not trending", lambda t: t["theme"] == 0), ("no theme", lambda t: t["theme"] == -1),
             ("volume building 1.1x+", lambda t: (t["vb"] or 0) >= 1.1), ("volume not building", lambda t: (t["vb"] or 0) < 1.1),
             ("on its list 10 days or less", lambda t: t["age"] <= 10), ("on its list 11-30 days", lambda t: 10 < t["age"] <= 30),
             ("on its list 31+ days", lambda t: t["age"] > 30),
             ("within 10% of the 52-week high", lambda t: (t["hi52"] or 0) >= 0.9), ("10%+ under the 52-week high", lambda t: (t["hi52"] or 0) < 0.9),
             ("base under 2 ADRs deep", lambda t: (t["depth"] or 0) < 2), ("base 2-4 ADRs deep", lambda t: 2 <= (t["depth"] or 0) <= 4),
             ("base over 4 ADRs deep", lambda t: (t["depth"] or 0) > 4),
             ("trigger within 0.3 ADR", lambda t: t["away"] is not None and t["away"] <= 0.3), ("trigger 0.3-0.7 ADR away", lambda t: t["away"] is not None and t["away"] > 0.3),
             ("ADR 4-6%", lambda t: (t["adr"] or 0) < 6), ("ADR 6%+", lambda t: (t["adr"] or 0) >= 6),
             ("leading theme + volume building", lambda t: t["theme"] == 2 and (t["vb"] or 0) >= 1.1),
             ("leading theme + within 10% of the 52-week high", lambda t: t["theme"] == 2 and (t["hi52"] or 0) >= 0.9),
             ("leading theme + volume building + within 10% of the high", lambda t: t["theme"] == 2 and (t["vb"] or 0) >= 1.1 and (t["hi52"] or 0) >= 0.9)]
    out = {}
    for name, test in tests:
        out.update(cut(name, test))
    return out


def summ(rs):
    rs = [r for r in rs if "ran20" in r]
    if not rs:
        return dict(n=0)
    r20 = [r["r20"] for r in rs if r["r20"] is not None]
    return dict(n=len(rs), ran10=round(100 * np.mean([r["ran10"] for r in rs])), ran20=round(100 * np.mean([r["ran20"] for r in rs])),
                fail5=round(100 * np.mean([r["fail5"] for r in rs])), med20=round(float(np.median(r20)), 1) if r20 else None)


def main():
    global A, FIRST
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    global GROUPS, GS, POS
    A, GROUPS, GS, cal, S = launch.load(a_.bars, a_.stocks)
    POS = {d: k for k, d in enumerate(cal)}
    FIRST = 200
    with multiprocessing.get_context("fork").Pool(os.cpu_count() or 2) as pool:
        res = pool.map(one, sorted(A), chunksize=8)
    trig = [r for _, t, _, _ in res for r in t]
    ready = [r for _, _, rd, _ in res for r in rd]
    setting = [r for _, _, _, s in res for r in s]
    by = lambda rs, key: {k: summ([r for r in rs if r[key] == k]) for k in sorted({r[key] for r in rs})}
    hits = [r for r in ready if r["hit"]]
    out = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), first=cal[FIRST], last=cal[-22],
               triggered=dict(all=summ(trig), by_setup=by(trig, "setup"), by_list=by(trig, "src")),
               ready=dict(days=len(ready), hit_next_day_pct=round(100 * len(hits) / len(ready)) if ready else None, all=summ(hits),
                          by_setup=by(hits, "setup"), by_list=by(hits, "src"),
                          tight=summ([r for r in hits if r["tight"]]), not_tight=summ([r for r in hits if not r["tight"]])),
               setting_up=dict(days=len(setting), became_ready_or_triggered_10d_pct=round(100 * np.mean([r["became"] for r in setting])) if setting else None,
                               by_setup={k: dict(days=sum(1 for r in setting if r["setup"] == k),
                                                 became_pct=round(100 * np.mean([r["became"] for r in setting if r["setup"] == k])))
                                         for k in sorted({r["setup"] for r in setting})}))
    if os.environ.get("ALPACA_KEY_ID"):
        ts = orh_trades(ready)
        out["ready_orh"] = dict(all=orh_summ(ts), B_day_low_stop=orh_summ(ts, "B"), C_half_at_2R=orh_summ(ts, "C"),
                                by_setup={k: orh_summ([t for t in ts if t["setup"] == k]) for k in sorted({t["setup"] for t in ts})},
                                by_list={k: orh_summ([t for t in ts if t["src"] == k]) for k in sorted({t["src"] for t in ts})},
                                splits=splits(ts),
                                opening_range_over_trigger=orh_summ([t for t in ts if t["over_trigger"]]),
                                opening_range_under_trigger=orh_summ([t for t in ts if not t["over_trigger"]]))
    json.dump(out, open(a_.out, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    try:
        main()
    except Exception:                            # the run's log isn't readable from the session: the error goes out instead
        import traceback
        json.dump(dict(error=traceback.format_exc()[-3000:]), open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
        raise
