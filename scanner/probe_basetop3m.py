#!/usr/bin/env python3
"""The 3-month check of the intact base top (the user, Nov 7 2026, LION: the base top is the high no day has closed
above since; a day that went over it and closed back under is a poke; a close over the 1-month high makes the new high
the top; base days from that top, depth from the base's highest point). The engine read both ways, the old rule
(launch.L["intact_top"] = 0: the highest high) and the new (= 1), every evening of the last ~3 months, on:
  Launches   the launches on the list that evening (detect + the list's off rules), launch.follow
  3-SETUPS   the Watchlist's feeder lists rebuilt from the bars (scanner/probe_setups3.py), launch.s3_read
  TREND      the other feeder names with Trend Up / Turn up / Reclaim / Resting (10 > 21 > 50 EMA, the 50 rising, the close
             over the 21 EMA), the Watchlist scan's buy point (msf pivot); new rule: a pivot set by a poke over the
             intact top goes back to that top
Each evening's buy point is the next session's trigger: traded over it (hit), held into the close, back under it
within 3 closes, failed (a close under the trigger day's low within 5 sessions), ran 10% / 20% within 20 sessions.

  python3 scanner/probe_basetop3m.py --bars BARS.json.gz --stocks stocks.json --out OUT.json [--sessions 63]"""
import argparse, datetime, json, multiprocessing, os, sys, traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch  # noqa: E402
import probe_setups3 as P3  # noqa: E402

L = launch.L
A, EV, CAL = {}, {}, []
START = 0
SHOW = ("LION", "DUOL", "RHI", "FA", "ELF", "ORKA", "ZETA", "TGTX", "FLS", "QLYS", "MANE", "IRON", "KNSA", "AMN")


def high_day(st, bp, j):
    """the day whose high is the buy point (the latest in the 130 sessions to day j), for finding it on the chart"""
    if not bp:
        return None
    for k in range(j, max(0, j - 130) - 1, -1):
        if abs(st.h[k] - bp) <= max(0.006, bp * 0.0005):
            return st.dates[k]
    return None


def outcome(st, k, lvl):
    n = st.c.size
    e = max(float(st.o[k]), lvl)
    hi = st.h[k:min(n, k + 20)].max()
    return dict(held=bool(st.c[k] > lvl), back3=bool((st.c[k:min(n, k + 3)] < lvl).any()),
                fail5=bool((st.c[k + 1:min(n, k + 6)] < st.l[k]).any()), ran10=bool(hi >= e * 1.1), ran20=bool(hi >= e * 1.2),
                r20=float(100 * (st.c[k + 20] / e - 1)) if k + 20 < n else None, days=int(min(20, n - k)))


def on_launches(a, i, j):
    """the list's off rules at day j for a launch on day i (launch.daily build), without the ✕"""
    c, e50 = a.st.c, a.e50
    if np.any((c[i + 3:j + 1] < e50[i + 3:j + 1]) & (c[i + 2:j] < e50[i + 2:j]) & (c[i + 1:j - 1] < e50[i + 1:j - 1])):
        return False
    if launch.stale(a, i, j) or a.st.adr[j] < L["off_adr"]:
        return False
    return not launch.under200(a, max(i, j - L["off_200"]), j)


def trend_on(a, j):
    e10, e21, e50, c = a.e10, a.e21, a.e50, a.st.c
    return bool(e10[j] > e21[j] > e50[j] and j >= 5 and e50[j] > e50[j - 5] and c[j] >= e21[j])


def trend_bp(a, j, new):
    """the Watchlist scan's buy point that evening (run.py: the msf pivot when it sees a pattern); new rule: a pivot set
    by a poke over the intact top (3 months) goes back to that top"""
    r = a.st.df.iloc[j]
    code = int(r.code)
    if not code or r.pivot != r.pivot:
        return None, None
    bp, pat = float(r.pivot), launch.msf.NAMES[code]
    if new:
        # only a level set by a poke moves: back to the high that poke went over (the month's highest high before it,
        # leaving out pokes), if no close has gone over that high since and it is over the close
        st, pk = a.st, launch.pokes(a)
        p = next((k for k in range(j, max(0, j - 130) - 1, -1) if abs(st.h[k] - bp) <= max(0.006, bp * 0.0005)), None)
        if p is not None and pk[p]:
            w = [k for k in range(max(0, p - 21), p) if not pk[k]]
            if w:
                t = max(w, key=lambda k: st.h[k])
                lvl = float(st.h[t])
                if st.c[j] < lvl and st.c[t + 1:j + 1].max() <= lvl * (1 + L["caution_pct"] / 100):
                    bp, pat = lvl, pat + " (intact top)"
    return bp, pat


def one(sym):
    a = A[sym]
    st = a.st
    n = st.c.size
    pos = {d: k for k, d in enumerate(st.dates)}
    js = [pos[d] for d in CAL[START:] if d in pos]
    if not js or js[0] < 200:
        return sym, [], {}, []
    out, show, now = [], {}, []
    s3state = {0: [None, None, False, False], 1: [None, None, False, False]}
    trstate = [None, None]
    evs = sorted(EV.get(sym, []))
    for j in range(max(js[0] - 130, 200), js[-1] + 1):
        rec = j in js
        # 3-SETUPS: the feeder state, each rule on its own (probe_setups3.one)
        rows = {}
        for v in (0, 1):
            L["intact_top"] = v
            S = s3state[v]
            i0, src, was_in, ever = S
            if i0 is not None:
                end = (j - i0 > 120 or (st.c[j] < a.e50[j] and st.c[j - 1] < a.e50[j - 1])
                       or (src != "2-POOL" and st.c[j] < st.l[i0]) or (src != "2-POOL" and not ever and j - i0 >= 15)
                       or (src == "2-POOL" and st.c[j] < a.s200[j]) or (was_in and st.adr[j] < L["off_adr"]))
                if end:
                    i0, was_in = None, False
            if i0 is None:
                f = P3.feeder(a, j)
                if f:
                    i0, src, was_in, ever = j, f, False, False
                s3state[v] = [i0, src, was_in, ever]
                continue
            x = launch.s3_read(a, i0, j, was_in)
            if x is None:
                was_in = False
            else:
                was_in = ever = True
                if rec:
                    sec, setup, f, bp, *_ = x
                    rows[("3-SETUPS", v)] = (bp, f.get("pattern") or setup, f)
            s3state[v] = [i0, src, was_in, ever]
        # TREND's feeder membership (the 1-lists 15 sessions, 2-POOL until under the 200 SMA; 120 at most)
        if trstate[0] is not None:
            i0, src = trstate
            if (j - i0 > 120 or (st.c[j] < a.e50[j] and st.c[j - 1] < a.e50[j - 1]) or (src != "2-POOL" and j - i0 >= 15)
                    or (src == "2-POOL" and st.c[j] < a.s200[j])):
                trstate = [None, None]
        if trstate[0] is None:
            f = P3.feeder(a, j)
            if f:
                trstate = [j, f]
        if not rec:
            continue
        # Launches: the newest launch up to day j still on the list
        ev = next((e for e in reversed(evs) if e <= j), None)
        if ev is not None and on_launches(a, ev, j):
            for v in (0, 1):
                L["intact_top"] = v
                f = launch.follow(a, ev, j)
                if not f.get("off_50ema"):
                    rows[("Launches", v)] = (f.get("buy_point"), f.get("pattern"), f)
        if trstate[0] is not None and trend_on(a, j) and not any(k[0] in ("Launches", "3-SETUPS") for k in rows):
            for v in (0, 1):
                bp, pat = trend_bp(a, j, v)
                rows[("TREND", v)] = (bp, pat, {})
        for lst in ("Launches", "3-SETUPS", "TREND"):
            if (lst, 0) not in rows and (lst, 1) not in rows:
                continue
            r = {"sym": sym, "list": lst, "date": st.dates[j]}
            for v in (0, 1):
                bp, pat, f = rows.get((lst, v), (None, None, {}))
                bp = float(bp) if bp and bp > st.c[j] else None
                d = {"bp": round(bp, 2) if bp else None, "pat": pat, "base_day": f.get("base_day"), "depth": f.get("base_depth_pct"),
                     "base_low": f.get("base_low_pct"), "top_date": f.get("buy_point_top_date") or high_day(st, bp, j)}
                if bp and j + 1 < n:
                    d["hit"] = bool(st.h[j + 1] > bp)
                    if d["hit"]:
                        d.update(outcome(st, j + 1, bp))
                r["old" if v == 0 else "new"] = d
            r["changed"] = r["old"]["bp"] != r["new"]["bp"]
            if j + 1 < n:
                out.append(r)
            elif st.dates[j] == CAL[-1]:
                now.append(r)
            if sym in SHOW and st.dates[j] in (CAL[-1], CAL[-2]):
                show[st.dates[j] + " " + lst] = r
    L["intact_top"] = 1
    return sym, out, show, now


def summ(rs, side):
    ds = [r[side] for r in rs if r[side]["bp"]]
    hits = [d for d in ds if d.get("hit")]
    r20 = [d["r20"] for d in hits if d.get("r20") is not None]
    pct = lambda k: round(100 * np.mean([d[k] for d in hits])) if hits else None
    return dict(reads_with_buy_point=len(ds), triggered=len(hits), held_into_close=pct("held"), back_under_3d=pct("back3"),
                failed_5d=pct("fail5"), ran10=pct("ran10"), ran20=pct("ran20"), median_20d=round(float(np.median(r20)), 1) if r20 else None)


def main():
    global A, EV, CAL, START
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--stocks", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sessions", type=int, default=63)
    a_ = ap.parse_args()
    L["intact_top"] = 0
    A, groups, GS, cal, S = launch.load(a_.bars, a_.stocks)
    P3.A = A
    CAL = cal
    START = len(cal) - 1 - a_.sessions
    ev = launch.detect(A, groups, GS, cal, S)
    for s, i, k, gs, gn in ev:
        EV.setdefault(s, []).append(i)
    with multiprocessing.get_context("fork").Pool(os.cpu_count() or 2) as pool:
        res = pool.map(one, sorted(A), chunksize=8)
    rows = [r for _, rs, _, _ in res for r in rs]
    show = {s: sh for s, _, sh, _ in res if sh}
    now = [r for _, _, _, nw in res for r in nw]
    out = dict(made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), first=cal[START], last_read_scored=cal[-2],
               note=__doc__.split("\n\n")[0], lists={})
    for lst in ("Launches", "3-SETUPS", "TREND"):
        rs = [r for r in rows if r["list"] == lst]
        ch = [r for r in rs if r["changed"]]
        out["lists"][lst] = dict(reads=len(rs), changed=len(ch), old=summ(rs, "old"), new=summ(rs, "new"),
                                 changed_old=summ(ch, "old"), changed_new=summ(ch, "new"))
    out["changed_rows"] = sorted([r for r in rows if r["changed"]], key=lambda r: (r["date"], r["list"], r["sym"]))
    out["show"] = show
    out["now"] = sorted(now, key=lambda r: (r["list"], r["sym"]))
    json.dump(out, open(a_.out, "w"), indent=1, default=str)
    print(json.dumps(out["lists"], indent=1))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        json.dump(dict(error=traceback.format_exc()[-3000:]), open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
        raise
