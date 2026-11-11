#!/usr/bin/env python3
"""The user's 51 chart buy days (tools/chart_examples.txt) against the Launches engine: for each day, was the stock on
the list (a launch followed by the list rules) and did the engine name the day?

  python3 tools/chart_check.py            MATCH = named and on the list · OFF = named, the stock was off the list ·
                                          MISS = not named; with the status the file recorded (Nov 10 2026) for comparison
Data: radar-data long_bars.json (as tools/replay.py). The $10 price floor is off: the old charts are split-adjusted.
"""
import os, re, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replay, launch  # noqa: E402
L = launch.L
SIG = replay.SIGNALS + ("falling range",)
QUIET = ("In the base", "Below the 21 EMA", "Closed under", "Running", "Consolidation", "Off the list")


def read(A, GS, cal, sym, day):
    a = A.get(sym)
    if a is None or day not in a.st.dates:
        return "?", "no bars"
    st, i = a.st, a.st.dates.index(day)
    ev = [e[1] for e in launch.detect({sym: a}, {}, GS, cal, None) if e[1] <= i]
    if not ev:
        return "MISS", "no launch before it" + ("" if a.liquid[i] else f" (ADR {st.adr[i]:.1f}% or liquidity under the minimum)")
    best = None
    for i0 in reversed(ev[-4:]):                       # the newest launch that is still on the list, else the newest
        f = launch.follow(a, i0, i)
        named = i == i0 or (any(w in f["stage"] for w in SIG) and not f["stage"].startswith(QUIET))
        if i == i0 and f.get("launch_attempt"):
            named = True
        why = None
        if i > i0:
            if launch.stale(a, i0, i):
                why = "62 sessions without a new high"
            elif st.adr[i] < L["off_adr"]:
                why = f"ADR {st.adr[i]:.1f}% under 3.2%"
            elif launch.under200(a, max(i0, i - L["off_200"]), i):
                why = "2 closes under the 200 SMA"
            elif f["off_now"]:
                why = f"off since {f['off_since']}: {f['off_why']}"
        res = ("MATCH" if named and not why else "OFF" if named else "MISS", f["stage"][:150] + (f" [{why}]" if why else ""), i0)
        if best is None or (res[0] == "MATCH" and best[0] != "MATCH"):
            best = res
        if res[0] == "MATCH":
            break
    return best[0], best[1] + f" (launch {st.dates[best[2]]})"


def main():
    class NoFloor(dict):                               # settings.json puts the $10 floor back at load: keep it off
        def update(self, d=(), **k):
            super().update({x: y for x, y in dict(d, **k).items() if x != "min_price"})
    launch.LIQ = NoFloor(launch.LIQ, min_price=0)
    A = replay.load_all()
    cal = sorted({d for a in A.values() for d in a.st.dates})
    GS = {}
    tot, was = {}, {}
    for row in open(os.path.join(replay.ROOT, "tools", "chart_examples.txt")):
        m = re.match(r"^([A-Z]+)\s+(\d{4}-\d\d-\d\d)\s+(.*?)\|\s+(MATCH|OFF|MISS)", row)
        if not m:
            continue
        sym, day, what, old = m.group(1), m.group(2), m.group(3).strip(), m.group(4)
        new, txt = read(A, GS, cal, sym, day)
        tot[new] = tot.get(new, 0) + 1
        was[old] = was.get(old, 0) + 1
        print(f"{sym:5} {day} {old:5} -> {new:5}{' *' if new != old else '  '} {what[:58]:58} | {txt}")
    print("\nrecorded Nov 10:", was, "\nnow:            ", tot)


if __name__ == "__main__":
    main()
