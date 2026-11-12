#!/usr/bin/env python3
"""Theme event: many stocks of one area gapping together before the open (the user, Nov 11 2026: "the pre-market graders
have a flaw: the most important thing happened [in] semis and it hasn't done anything related to it").

Nov 11 2026, the 9:25 scan: 115 tradable stocks up 5%+, 63 of the 83 in AI & Semis and 30 of the 62 in AI Infrastructure
(Optics & CPO 14 of 15, Neoclouds 13 of 15, Semi Test & Packaging 12 of 14 ...). The graders read each one C ("sector
sympathy") and never said the area itself was the news; the biggest (CRWV, NBIS, MRVL, SNDK, MU, DELL) were not even on
the graded list: still under their 50 EMA.

An AREA is a theme category of themes.json (AI & Semis, AI Infrastructure, Software, Energy ...; a stock with no theme
counts in its sector). An area has an event when, among its tradable stocks (market cap $700M+, 700K+ shares and $20M+ a
day, ADR 3%+: the graded list's liquidity rules, without its 50 EMA and 52-week-low rules, so the beaten-down leaders
count), AREA_MIN (8) or more gap GAP (5%)+ the same way and they are AREA_SHARE (30%)+ of the area. The areas of one
direction make one event (Nov 11: "AI & Semis and AI Infrastructure").

  find(stocks, live_rows, themes) -> [event, ...]   (one per direction, at most)
  event = {"dir": "up", "n": 93, "areas": [{"name", "n", "of"}], "themes": [{"name", "n", "of"}], "leaders": [sym, ...],
           "symbols": [sym, ...]}

radar/pmlive.py puts the events into premarket_live.json every 5 minutes; the portal draws the event line and the theme
bounce list from them (each gapper's distance to its 21 and 50 EMA: the first to reclaim both is the user's "go sign",
AMD Sep 4-8 2026, MRVL Mar 6 2026). The 8:45 grading reads them (premarket_build.py prepare -> theme_event.json),
searches once for the market / sector news behind the move and saves it (finish -> pm_event.json).
"""
import json, sys

GAP = 5.0            # a gapper: the pre-market change, %
AREA_MIN = 8         # stocks of one area gapping the same way
AREA_SHARE = 0.30    # ... and this share of the area's tradable stocks
THEME_MIN = 3        # a theme is named with 3+ gappers
MCAP_MIN, AVGVOL_MIN, DVOL_MIN, ADR_MIN = 0.7, 700_000, 20.0, 3.0


def num(x):
    try:
        return None if x is None or x == "" else float(x)
    except (TypeError, ValueError):
        return None


def tradable(s):
    adr = num(s.get("adr_20"))
    return ((num(s.get("mcap_b")) or 0) >= MCAP_MIN and (num(s.get("avg_vol_20") or s.get("avg_vol_30d")) or 0) >= AVGVOL_MIN
            and (num(s.get("dvol_20_m")) or 0) >= DVOL_MIN and (adr is None or adr >= ADR_MIN))


def themes_of(s):
    return [t for t in str(s.get("themes") or "").split(" | ") if t]


def areas_of(s, cat):
    """the theme categories of the stock's themes; an auto group or no theme: its sector"""
    a = {cat[t] for t in themes_of(s) if cat.get(t) and cat[t] != "Auto groups"}
    return a or ({str(s["sector"])} if s.get("sector") else set())


def find(stocks, live, themes):
    cat = {t["theme"]: t.get("category") or "" for t in themes or []}
    pool = [s for s in stocks if tradable(s)]
    out = []
    for d, sign in (("up", 1), ("down", -1)):
        gap = {s["symbol"] for s in pool if s["symbol"] in live and (num(live[s["symbol"]][1]) or 0) * sign >= GAP}
        tot, got, ttot, tgot = {}, {}, {}, {}
        for s in pool:
            g = s["symbol"] in gap
            for a in areas_of(s, cat):
                tot[a] = tot.get(a, 0) + 1
                if g:
                    got.setdefault(a, []).append(s["symbol"])
            for t in themes_of(s):
                ttot[t] = ttot.get(t, 0) + 1
                if g:
                    tgot.setdefault(t, []).append(s["symbol"])
        hot = sorted([a for a, m in got.items() if len(m) >= AREA_MIN and len(m) >= AREA_SHARE * tot[a]], key=lambda a: -len(got[a]))
        if not hot:
            continue
        syms = sorted({x for a in hot for x in got[a]})
        inset = set(syms)
        by = {s["symbol"]: s for s in pool}
        dvol = lambda x: num(live[x][4]) or 0                      # pre-market $ volume: where the money is
        th = [{"name": t, "n": len(m), "of": ttot[t]} for t, m in tgot.items()
              if len([x for x in m if x in inset]) >= THEME_MIN and cat.get(t) in hot]
        th.sort(key=lambda r: (-r["n"], r["name"]))
        out.append({"dir": d, "n": len(syms), "areas": [{"name": a, "n": len(got[a]), "of": tot[a]} for a in hot],
                    "themes": th[:10], "leaders": sorted(syms, key=lambda x: -dvol(x))[:8],
                    "symbols": sorted(syms, key=lambda x: -(num(by[x].get("mcap_b")) or 0))})
    return out


def line(ev, live=None):
    """one plain line for the logs and the 8:45 grading"""
    areas = " and ".join(f"{a['name']} ({a['n']} of {a['of']})" for a in ev["areas"])
    th = ", ".join(f"{t['name']} {t['n']}/{t['of']}" for t in ev["themes"][:6])
    lead = ", ".join(f"{x} {live[x][1]:+.1f}%" if live and x in live else x for x in ev["leaders"])
    return f"THEME EVENT: {ev['n']} stocks gapping {ev['dir']} {GAP:g}%+ in {areas}" + (f" · {th}" if th else "") + f" · leaders by pre-market $ volume: {lead}"


if __name__ == "__main__":      # python3 radar/theme_event.py stocks.json premarket_live.json themes.json
    stocks, lv, th = (json.load(open(p)) for p in sys.argv[1:4])
    evs = find(stocks, lv.get("rows") or {}, th)
    for e in evs:
        print(line(e, lv.get("rows")))
    if not evs:
        print("no theme event")
