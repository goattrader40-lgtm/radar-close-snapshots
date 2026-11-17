"""Daily scanner — steps 1 to 3 of your workflow, run after the close.

  Step 1  EP-GAPUP-BREAKOUT → 1-EP/GAP · HOTTEST STOCKS → 1-UPDAY        (daily, a section per date)
  Step 2  50 EMA FIRST CLOSE → 2-POOL › 50 EMA reclaim                    (daily)
          MOMENTUM-1W/1M/3M/6M → 2-POOL › Momentum                         (weekly refresh)
  Step 3  3-SETUPS: built right after this by scanner/launch.py --watchlist, the Launches engine's buy points and
          triggers on 1-EP/GAP + 1-UPDAY + 2-POOL (Triggered today / Ready / Setting up; your Nov 1 2026 design)
  Deletes: 2 closes in a row below the 50 EMA (any list) · 1-lists: close below the gap / up-day low, or 15
  trading days with no setup · 2-POOL weekly: below 200 SMA, illiquid, up 300%+ · 3-SETUPS: below 200 SMA,
  weekly trim to the best 30.

Usage:
  python scanner/run.py --bars BARS.json.gz              # process every new trading day since the last run
  python scanner/run.py --bars BARS.json.gz --backfill 15 # rebuild the lists from scratch over the last 15 days
"""
import argparse
import datetime
import gzip
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import msf  # noqa: E402
import screens  # noqa: E402

ROOT = os.path.dirname(HERE)
STATE = os.path.join(HERE, "state.json")
OUT = os.path.join(ROOT, "setups")
LISTS = ["1-EP/GAP", "1-UPDAY", "2-POOL", "3-SETUPS"]
SETUP_SCREENS = {"DAILY TIGHTNESS": "Tight", "PULLBACK TO 21EMA-MAIN": "PB 21", "PULLBACK TO 50EMA": "PB 50"}
GRADE = {0: "", 1: "A+", 2: "A", 3: "B"}
PBE_DAYS = 4   # MSF v29.1 'Today is at least the Nth day since the 20-day high' (21 / 50 EMA pullback triggers)
PBE_HH_LEN, PBE_HH_REF, PBE_HH_TOL = 30, 33, 0.0   # MSF v29.13: higher high = the last 30 days' peak >= the peak of the 33 days before (x (1 - tol%))


def higher_high(H, i):
    """momentum only: a new 3-month high made in the last 30 days (the 21 / 50 EMA triggers need it)"""
    if i < PBE_HH_LEN + PBE_HH_REF - 1:
        return False
    return H[i - PBE_HH_LEN + 1:i + 1].max() >= H[i - PBE_HH_LEN - PBE_HH_REF + 1:i - PBE_HH_LEN + 1].max() * (1 - PBE_HH_TOL / 100)


PBE_MAX_TOUCHES_50 = 1   # MSF v29.12: 50 EMA trigger — at most 1 earlier day whose low reached the 50 EMA since the 20-day high
PBE_MAX_TOUCHES_21 = 1   # MSF v29.11: 21 EMA trigger — at most 1 earlier day whose low reached the 21 EMA since the 20-day high


def structure_hhhl(st, P):
    """'structure' version of higher high + higher low: turns on when price takes out the last swing high after
    a higher low, stays on until price undercuts that higher low (same swing size as the MSF grade)."""
    H, L, adr = st.h, st.l, st.adr
    on = np.zeros(H.size, bool)
    d = 1; zh = zl = sh1 = sl1 = sl2 = key = math.nan; s = False
    for i in range(H.size):
        th = max(P["swMinPct"], min(P["swMaxPct"], P["swAdrX"] * adr[i])) if adr[i] == adr[i] else P["swMinPct"]
        if d == 1:
            if zh != zh or H[i] > zh:
                zh = H[i]
            elif L[i] <= zh * (1 - th / 100):
                sh1 = zh; d = -1; zl = L[i]
        else:
            if L[i] < zl:
                zl = L[i]
            elif H[i] >= zl * (1 + th / 100):
                sl2 = sl1; sl1 = zl; d = 1; zh = H[i]
        if s and L[i] < key:
            s = False
        if sh1 == sh1 and H[i] > sh1 and sl1 == sl1 and sl2 == sl2 and sl1 > sl2 and (not s or sl1 > key):
            s = True; key = sl1
        on[i] = s
    return on


def load_bars(path):
    with gzip.open(path, "rt") as f:
        return json.load(f)


def build(D, cfg):
    P = dict(msf.DEFAULTS, **{k: v for k, v in cfg["msf"].items() if not k.startswith("_")})
    p = msf.params(base=P)
    bench = {b[0]: b[4] for b in D["bars"]["SPY"]}
    S = cfg["standard"]
    screens.REL_VOL_DAYS = int(cfg["screeners"].get("rel_vol_days", 20))
    stocks = {}
    for sym, bars in D["bars"].items():
        mc = D["market_cap"].get(sym, 0)
        if sym == "SPY" or not (S["min_mcap"] <= mc <= S["max_mcap"]) or len(bars) < 60:
            continue
        st = screens.Stock(sym, bars, bench, p, mc, D.get("exchange", {}).get(sym))
        st.hhhl_struct = structure_hhhl(st, P)
        stocks[sym] = st
    return stocks, P


def hhhl_ok(st, i, mode):
    if mode == "off":
        return True
    if mode == "structure":
        return bool(st.hhhl_struct[i])
    return bool(st.df.hhhl.values[i] == 1)


def tdays_between(dates, a, b):
    """trading days from date a to date b (b later)"""
    try:
        return dates.index(b) - dates.index(a)
    except ValueError:
        return 0


def step(state, d, stocks, cfg, cal, log):
    L = cfg["lists"]
    lists = state["lists"]
    weekly = state.get("pool_refresh") is None or datetime.date.fromisoformat(d).weekday() == L["pool_refresh_weekday"] \
        or (datetime.date.fromisoformat(d) - datetime.date.fromisoformat(state["pool_refresh"])).days >= 7
    today = {s: st for s, st in stocks.items() if d in st.pos}
    hits = {s: st.screens(st.pos[d], cfg) for s, st in today.items()}

    def chased(st, i):   # no-chase rule (off when the setting is empty or 0)
        return bool(L.get("no_chase_1y_pct")) and st.perf(i, 252) >= L["no_chase_1y_pct"]

    def remove(name, sym, why):
        lists[name].pop(sym, None)
        log.append(dict(date=d, list=name, sym=sym, action="removed", why=why))

    # 1-UPDAY rows from before Nov 14 2026 carry the low of their LATEST up day: once, put back the low of the day they
    # came on the list (the last "added" in the log; rows without one, or without that bar, keep what they have)
    came = {}
    for x in log:
        if x["list"] == "1-UPDAY":
            came[x["sym"]] = x["date"] if x["action"] == "added" else None
    for sym, e in lists["1-UPDAY"].items():
        st = today.get(sym)
        if "first_day" not in e and st is not None:
            d0 = came.get(sym) if came.get(sym) in st.pos else None
            e["first_day"] = d0 or e.get("added")
            if d0:
                e["low"] = round(float(st.l[st.pos[d0]]), 4)

    # 1-EP/GAP rows from before Nov 14 2026 have no pre-gap close: once, take the close before the day they came on
    for sym, e in lists["1-EP/GAP"].items():
        st = today.get(sym)
        if "pre_close" not in e and st is not None:
            k = st.pos.get(e.get("added"))
            e["pre_close"] = round(float(st.c[k - 1]), 4) if k else None

    # your x on 1-EP/GAP and 1-UPDAY (the user, Nov 14 2026: "add x button next to tickers for ep/gap and upday so if i see
    # some wrong i can delete it myself"): setups/picks.json "removed_lists" {list: {symbol: {added}}}: the row you saw
    # (its added day) leaves; a new gap / up day on a later day puts the stock back
    for name, gone in (state.get("_removed_lists") or {}).items():
        for sym, g in (gone or {}).items():
            e = lists.get(name, {}).get(sym) if name in ("1-EP/GAP", "1-UPDAY") else None
            if e and (e.get("added") or "") <= ((g or {}).get("added") or ""):
                remove(name, sym, "removed by you (the x on the Watchlist)")

    # 1) deletes
    nb = L["delete_after_closes_below_ema50"]
    for name in LISTS:
        for sym in list(lists[name]):
            st = today.get(sym)
            if st is None:
                continue
            i = st.pos[d]
            e = lists[name][sym]
            if st.below50(i, nb):
                remove(name, sym, f"{nb} closes in a row below the 50 EMA")
            elif name == "1-EP/GAP" and L.get("delete_below_pre_gap_close") and e.get("pre_close") and st.c[i] < e["pre_close"]:
                remove(name, sym, f"closed below the pre-gap close {e['pre_close']} (the gap is given back)")
            elif ((name == "1-EP/GAP" and L["delete_below_gap_low"]) or (name == "1-UPDAY" and L["delete_below_upday_low"])) and st.c[i] < e["low"]:
                remove(name, sym, "closed below the " + ("gap" if name == "1-EP/GAP" else "up-day") + f" low {e['low']}")
            # the 15 days without a setup: 1-UPDAY only (the user, Nov 14 2026, on 1-EP/GAP: "lets take that 15 day clock,
            # we dont need it there": an EP gap stays until it closes 2 days under the 50 EMA)
            elif name == "1-UPDAY" and not e.get("promoted") and tdays_between(cal, e["added"], d) >= L["new_mover_days_without_setup"]:
                remove(name, sym, f"{L['new_mover_days_without_setup']} trading days with no setup")
            elif name == "3-SETUPS" and L["setups_need_above_sma200"] and not st.c[i] > st.sma200[i]:
                remove(name, sym, "closed below the 200 SMA")
            elif name == "2-POOL" and weekly:
                S = cfg["standard"]
                if not st.c[i] > st.sma200[i]:
                    remove(name, sym, "below the 200 SMA (weekly refresh)")
                elif not (st.c[i] >= S["min_price"] and st.avgv20[i] >= S["min_avg_vol_20d"] and st.dv20[i] >= S["min_dollar_vol_20d_millions"]):
                    remove(name, sym, "no longer liquid (weekly refresh)")
                elif chased(st, i):
                    remove(name, sym, f"up {L['no_chase_1y_pct']}%+ in a year (weekly refresh)")

    def add(name, sym, entry):
        new = sym not in lists[name]
        old = lists[name].get(sym, {})
        entry = dict(old, **entry)
        if new:
            entry["added"] = d
            log.append(dict(date=d, list=name, sym=sym, action="added", why=entry.get("why", "")))
        lists[name][sym] = entry

    # 2) step 1 and 2 additions
    for sym, h in hits.items():
        st = today[sym]; i = st.pos[d]
        if "EP-GAPUP-BREAKOUT" in h:
            gap = round(100 * (st.o[i] / st.c[i - 1] - 1), 1)
            # pre_close: the close before the gap, the line an EP has to hold (the first gap's while it is on the list)
            add("1-EP/GAP", sym, dict(section=d, low=round(float(st.l[i]), 4), why=f"gap +{gap}%, rel vol {st.relvol[i]:.1f}",
                                      **({} if lists["1-EP/GAP"].get(sym, {}).get("pre_close") else dict(pre_close=round(float(st.c[i - 1]), 4)))))
            lists["1-EP/GAP"][sym].update(added=d, promoted=False)   # a repeat gap moves it to today's section
        elif "HOTTEST STOCKS" in h:
            chg = round(100 * (st.c[i] / st.c[i - 1] - 1), 1)
            # the line it must hold = the low of the FIRST day it came on the list: a later up day moves it to today's
            # section and restarts the 15 days, but no longer raises the line (the user, Nov 14 2026: "it should have
            # counted the low of 1st day it got into our table"; before: up 6%, up 5%, then a close under the 2nd day's
            # low took it off)
            first = sym not in lists["1-UPDAY"]
            add("1-UPDAY", sym, dict(section=d, why=f"+{chg}%, rel vol {st.relvol[i]:.1f}", **(dict(low=round(float(st.l[i]), 4), first_day=d) if first else {})))
            lists["1-UPDAY"][sym].update(added=d, promoted=False)
        if "50 EMA FIRST CLOSE" in h and not chased(st, i) and sym not in lists["2-POOL"]:
            add("2-POOL", sym, dict(section="50 EMA reclaim", why="first close back above the 50 EMA"))
        if weekly:
            mom = [n.replace("MOMENTUM-", "") for n in h if n.startswith("MOMENTUM-")]
            if mom and not chased(st, i):
                add("2-POOL", sym, dict(section="Momentum", why="momentum " + "/".join(mom)))
    if weekly:
        state["pool_refresh"] = d

    # 3) step 3: 3-SETUPS is built after this by scanner/launch.py --watchlist (your Nov 1 2026 design: the Launches
    # engine's buy points and triggers on these three lists; the Tight / PB 21 / PB 50 screens are gone). A stock it
    # took last night is "promoted": it is not deleted for 15 days without a setup
    for name in ("1-EP/GAP", "1-UPDAY", "2-POOL"):
        for sym in lists[name]:
            if sym in state.get("_prev3", ()):
                lists[name][sym]["promoted"] = True
    lists["3-SETUPS"] = {}
    state["asof"] = d


def rank_key(sym, e, today, d, cal):
    st = today.get(sym)
    if st is None:
        return (9, 9, 0, 99)
    i = st.pos[d]
    r = st.df.iloc[i]
    g = int(r.grade)
    age = tdays_between(cal, e.get("last_hit", e["added"]), d)
    # your MSF score, plus 10 when the 21 EMA is over the 50 EMA (the user's rule, Oct 31 2026; the MSF engine itself
    # is left as in TradingView)
    score = int(r.score) + (10 if st.ema21[i] > st.ema50[i] else 0)
    return (0 if age <= 5 else 1, {1: 0, 2: 1, 3: 2}.get(g, 3), -score, age)


def fnum(x, nd=2):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), nd)


def our_flag(st, i):
    """a bull flag for the Watchlist when your MSF engine names no pattern yet: the Launches tab's flag
    (scanner/launch.py), the same rule. The top at least a 1-month high, after a run of 4+ ADRs made by the trend; the
    high and 4+ pullback days, 1.25-4 ADRs deep, 3+ lower highs, closes holding the 21 EMA, 3+ days within an ADR of the
    10 or the 21 EMA, no violent drop (a gap down of 0.7+ ADR closing 1+ ADR down on 1.3x+ volume), under a falling
    line across the highs (a failed try doesn't redraw it); a bull flag's channel or a pennant, the volume drying up.
    Returns (the line tomorrow, the top, "bull flag" / "pennant") or None. LIFE Oct 2026:
    +44% to 44.99, 10% back, riding its 10 EMA as the volume dried up, the line from 44.99"""
    import types
    import launch                                 # here: launch imports this module
    prev = np.concatenate(([np.nan], st.c[:-1]))
    avg20 = np.concatenate(([np.nan], launch.roll_mean(st.v, 20)[:-1]))
    a = types.SimpleNamespace(st=st, e10=launch.ema(st.c, 10), e21=st.ema21, e50=st.ema50,
                              chg=100 * (st.c / prev - 1), rv=st.v / avg20)        # for the flag's no-violent-drop test
    try:
        f = launch.flag_at(a, i)
        if not f or not launch.flag_run(a, f[0]) or launch.lower_highs(a, f[0], i) < launch.L["flag_down_days"] \
                or launch.surfing(a, f[0], i) < launch.L["flag_surf"] or st.c[i] > f[2] * (1 + launch.L["caution_pct"] / 100):
            return None             # closed over its line today: the flag broke (within 0.5% the line stays the next trigger)
    except (IndexError, ValueError):
        return None
    return float(f[3]), float(st.h[f[0]]), f[4] if len(f) > 4 else "bull flag"     # the line tomorrow, the top, the shape


def details(sym, st, d, entry, P):
    i = st.pos[d]
    r = st.df.iloc[i]
    code = int(r.code)
    H = st.h
    ins = msf.inside_days(st.h, st.l, i) if r.early != r.early and st.c[i] > st.sma200[i] else (None, None, None)   # no coil, over the 200 SMA
    hb20 = int(19 - np.where(H[i - 19:i + 1] == H[i - 19:i + 1].max())[0][-1]) if i >= 19 else None
    hi20 = float(H[i - 19:i + 1].max()) if i >= 19 else None
    out = dict(
        symbol=sym, tv=tv_symbol(sym, st.exchange), close=fnum(st.c[i]), chg_pct=fnum(100 * (st.c[i] / st.c[i - 1] - 1), 1),
        grade=GRADE.get(int(r.grade), ""), higher_high_low=bool(r.hhhl == 1), pullback_from_20d_high_pct=fnum(r.pb20, 1),
        pattern=msf.NAMES[code] if code else "", buy_point=fnum(r.pivot) if code else None,
        to_buy_point_pct=fnum(r.dist, 1) if code else None, base_bars=fnum(r.cN, 0), base_depth_pct=fnum(r.cDep, 1),
        msf_score=int(r.score), adr_pct=fnum(r.adr, 1), rel_vol=fnum(st.relvol[i], 1), dollar_vol_30d_m=fnum(st.dv30[i], 0),
        perf_1m_pct=fnum(st.perf(i, 21), 0), perf_3m_pct=fnum(st.perf(i, 63), 0), off_52w_high_pct=fnum(100 * (1 - st.c[i] / st.high52[i]), 1),
        ema21=fnum(st.ema21[i]), ema50=fnum(st.ema50[i]), sma200=fnum(st.sma200[i]),
        entries={k: v for k, v in dict(
            breakout=fnum(r.pivot) if msf.is_pat(code) else None,
            flag_trendline=fnum(r.tlLive),
            coil=fnum(r.early), coil_stop=fnum(r.earlyStop),
            # "inside day": 2+ days inside a mother day whatever their bodies, over the 200 SMA; only when there is no coil
            # (the coil is the stronger read and wins: the user, Nov 14 2026)
            inside_day=fnum(ins[0]), inside_day_stop=fnum(ins[1]),
            inside_day_triggered=fnum(ins[2]),      # today's high took out the inside-day buy: the entry is used up
            pullback_tight_day=fnum(r.hlTrig) if not r.hlDone else None, pullback_stop=fnum(r.hlStop) if not r.hlDone and r.hlTrig == r.hlTrig else None,
            level=fnum(r.cLvTrig), bigger_base=fnum(r.cBigBuy), flat_top=fnum(r.cFTBuy)).items() if v is not None},
        ema_triggers_tomorrow=[] if not higher_high(H, i) else [t for t, ok in (
            ("21 EMA", hb20 is not None and hb20 + 1 >= PBE_DAYS and r.ema10 > r.ema21 > r.ema50 > r.sma200 and r.liquid == 1 and r.above200 == 1
             and st.avgv30[i] >= 700000 and st.c[i] > r.ema50
             and r.ema21 < st.c[i] <= r.ema21 * (1 + r.adr / 100)
             and sum(st.l[k] <= st.ema21[k] for k in range(i - hb20 + 1, i + 1)) <= PBE_MAX_TOUCHES_21),
            ("50 EMA", hb20 is not None and hb20 + 1 >= PBE_DAYS and r.ema21 > r.ema50 > r.sma200 and r.liquid == 1 and r.above200 == 1
             and st.avgv30[i] >= 700000 and st.c[i] > r.ema50
             and r.ema50 < st.c[i] <= r.ema50 * (1 + r.adr / 100)
             and sum(st.l[k] <= st.ema50[k] for k in range(i - hb20 + 1, i + 1)) <= PBE_MAX_TOUCHES_50)) if ok],
        twenty_day_high=fnum(hi20), days_since_20d_high=hb20,
    )
    # MSF names no pattern yet: the flag rule from the Launches tab may (LIFE Oct 30 2026)
    if code == 10:
        fl = our_flag(st, i)
        if fl:
            out.update(pattern=("Bull pennant" if fl[2] == "pennant" else "Bull flag") + " (falling line)", buy_point=fnum(fl[0]), to_buy_point_pct=fnum(100 * (fl[0] / st.c[i] - 1), 1),
                       flag_top=fnum(fl[1]))
            out["entries"]["flag_line"] = fnum(fl[0])
    out.update({k: v for k, v in entry.items() if k not in ("low",)})
    if "low" in entry:
        out["support_low"] = entry["low"]
    if entry.get("pre_close"):
        out["pre_gap_close"] = entry["pre_close"]
    return out


def tv_symbol(sym, ex):
    s = sym.replace("/", ".")
    return f"{ex}:{s}" if ex else s


def write_outputs(state, stocks, cfg, P, log, d):
    os.makedirs(os.path.join(OUT, "tradingview"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "history"), exist_ok=True)
    lists = state["lists"]
    today = {s: st for s, st in stocks.items() if d in st.pos}
    cal = state["_cal"]
    full = {}
    for name in LISTS:
        rows = [details(s, today[s], d, e, P) for s, e in lists[name].items() if s in today]
        if name == "3-SETUPS":
            rows.sort(key=lambda r: rank_key(r["symbol"], lists[name][r["symbol"]], today, d, cal))
        else:
            rows.sort(key=lambda r: r["symbol"])
            rows.sort(key=lambda r: r.get("section", ""), reverse=name.startswith("1-"))
        full[name] = rows
    changes = [x for x in log if x["date"] == d]
    doc = dict(date=d, made_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
               counts={n: len(full[n]) for n in LISTS}, changes_today=changes, lists=full,
               # the rules behind each list, for the portal's "what puts a stock on this list" box
               settings=dict(standard=cfg["standard"], screeners=cfg["screeners"], lists=cfg["lists"],
                             higher_high_low=cfg["lists"]["setups_higher_high_low"], msf="v29.4" + (" + " + ", ".join(f"{k}={v}" for k, v in cfg["msf"].items() if not k.startswith("_")) if any(not k.startswith("_") for k in cfg["msf"]) else "")))
    with open(os.path.join(OUT, "latest.json"), "w") as f:
        json.dump(doc, f, indent=1)
    with open(os.path.join(OUT, "history", d + ".json"), "w") as f:   # the day's 3-SETUPS, list sizes and changes
        json.dump({k: v for k, v in doc.items() if k != "lists"} | {"setups": full["3-SETUPS"],
                  "lists": {n: [r["symbol"] for r in full[n]] for n in LISTS}}, f, separators=(",", ":"))
    # TradingView import files: one per list, a ### line per section
    for name in LISTS:
        secs = {}
        for r in full[name]:
            secs.setdefault(r.get("section", ""), []).append(r["tv"])
        order = sorted(secs, reverse=True) if name.startswith("1-") else (["Tight", "PB 21", "PB 50"] if name == "3-SETUPS" else ["Momentum", "50 EMA reclaim", "Growth"])
        lines = []
        for s in order + [s for s in secs if s not in order]:
            if s in secs:
                lines.append("###" + s)
                lines.extend(secs[s])
        with open(os.path.join(OUT, "tradingview", name.replace("/", "-") + ".txt"), "w") as f:
            f.write("\n".join(lines) + "\n")
    with open(os.path.join(OUT, "README.md"), "w") as f:
        f.write(summary_md(doc))


def summary_md(doc):
    d = doc["date"]
    L = doc["lists"]
    out = [f"# Setups — {d}", "",
           " · ".join(f"**{n}** {doc['counts'][n]}" for n in LISTS), "",
           "TradingView import files are in [`tradingview/`](tradingview/) (Watchlist menu → Import list).", "",
           "## 3-SETUPS", "",
           "Triggered today / Ready (the trigger within 0.7 ADR) / Setting up, from the Launches engine (scanner/launch.py).", "",
           "| # | Symbol | Setup (last hit) | Grade | Pattern | Buy point | Away | Other entries | ADR | From |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for k, r in enumerate(L["3-SETUPS"], 1):
        ent = r.get("entries", {})
        other = ", ".join(f"{n.replace('_', ' ')} {v}" for n, v in ent.items() if n not in ("breakout",) and not n.endswith("stop"))
        if r.get("ema_triggers_tomorrow"):
            other = (other + ", " if other else "") + "armed: " + " + ".join(r["ema_triggers_tomorrow"]) + " pullback"
        away = f"{r['to_buy_point_pct']:+.1f}%" if r.get("to_buy_point_pct") is not None else ""
        hit = datetime.date.fromisoformat(r["last_hit"]).strftime("%b %d") if r.get("last_hit") else ""
        out.append(f"| {k} | {r['symbol']} | {r.get('section', '')}: {r.get('setup') or ' + '.join(r.get('setups') or [])}{f' ({hit})' if hit else ''} | {r.get('grade')} | {r.get('pattern')} | "
                   f"{r['buy_point'] or ''} | {away} | {other} | {r['adr_pct']}% | {r.get('source', '')} |")
    ch = doc["changes_today"]
    if ch:
        out += ["", "## Changes today", "", "| List | Symbol | | Why |", "|---|---|---|---|"]
        for x in sorted(ch, key=lambda x: (x["list"], x["action"], x["sym"])):
            out.append(f"| {x['list']} | {x['sym']} | {x['action']} | {x['why']} |")
    for n in ("1-EP/GAP", "1-UPDAY", "2-POOL"):
        out += ["", f"## {n}", ""]
        secs = {}
        for r in L[n]:
            secs.setdefault(r.get("section", ""), []).append(r["symbol"])
        for s in sorted(secs, reverse=True):
            out.append(f"- **{s}**: " + ", ".join(sorted(secs[s])))
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True)
    ap.add_argument("--backfill", type=int, default=0)
    ap.add_argument("--date")
    a = ap.parse_args()
    cfg = json.load(open(os.path.join(HERE, "settings.json")))
    D = load_bars(a.bars)
    cal = [b[0] for b in D["bars"]["SPY"]]
    stocks, P = build(D, cfg)
    print(len(stocks), "stocks in the market-cap range")
    last = a.date or cal[-1]
    if a.backfill or not os.path.exists(STATE):
        n = a.backfill or 15
        state = dict(lists={n_: {} for n_ in LISTS}, asof=None, pool_refresh=None, log=[])
        days = [x for x in cal if x <= last][-n:]
    else:
        state = json.load(open(STATE))
        days = [x for x in cal if state["asof"] < x <= last]
    log = state.setdefault("log", [])
    try:                                                # last night's 3-SETUPS (scanner/launch.py), for the promotion
        state["_prev3"] = {r["symbol"] for r in json.load(open(os.path.join(OUT, "latest.json")))["lists"].get("3-SETUPS", [])}
    except Exception:
        state["_prev3"] = set()
    try:                                                # your x on 1-EP/GAP / 1-UPDAY (the portal saves it in picks.json)
        state["_removed_lists"] = json.load(open(os.path.join(OUT, "picks.json"))).get("removed_lists") or {}
    except Exception:
        state["_removed_lists"] = {}
    for d in days:
        step(state, d, stocks, cfg, cal, log)
        print(d, {n_: len(state["lists"][n_]) for n_ in LISTS})
    if not days:
        print("nothing new to process (last processed", state["asof"], ")")
        return
    cutoff = (datetime.date.fromisoformat(last) - datetime.timedelta(days=45)).isoformat()
    state["log"] = [x for x in log if x["date"] >= cutoff]
    state["_cal"] = cal
    state.pop("_prev3", None)
    state.pop("_removed_lists", None)
    write_outputs(state, stocks, cfg, P, state["log"], last)
    state.pop("_cal")
    with open(STATE, "w") as f:
        json.dump(state, f, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
