"""Exit plans to compare (Nov 2 2026, the user: "test the exits"). Same order rules as scanner/mgmt.py: a bar that touches
the stop and a target counts the stop first; on the buy day only the bars after the buy count (none for a close buy)."""

# name: (targets [(unit 'R' | 'ADR', distance, fraction)], breakeven ('first' = after the first target, ('R', x) = when the
#        high reaches +xR, None), runner exit ('ema10' | 'ema21' | 'prevlow' | None), extras)
SPECS = {
    "E0 now: 1/3 +2ADR, 1/3 +5ADR, BE, 21EMA": ([("ADR", 2, 1 / 3), ("ADR", 5, 1 / 3)], "first", "ema21", {}),
    "E1: 1/2 +1R, BE, rest 10EMA": ([("R", 1, 0.5)], "first", "ema10", {}),
    "E2: all out at +2R (20 days max)": ([("R", 2, 1.0)], None, None, {"max_days": 20}),
    "E3: all out at +3R (20 days max)": ([("R", 3, 1.0)], None, None, {"max_days": 20}),
    "E4: 1/2 +2R, BE, rest 10EMA": ([("R", 2, 0.5)], "first", "ema10", {}),
    "E5: trail under the prior day's low": ([], None, "prevlow", {}),
    "E6: 10EMA close only": ([], None, "ema10", {}),
    "E7: 1/3 +1ADR, 1/3 +3ADR, BE, 10EMA": ([("ADR", 1, 1 / 3), ("ADR", 3, 1 / 3)], "first", "ema10", {}),
    "E8: now + out at day-3 close if under +1R": ([("ADR", 2, 1 / 3), ("ADR", 5, 1 / 3)], "first", "ema21", {"time": (3, 1.0)}),
    "E9: now + out at day-1 close if under the buy": ([("ADR", 2, 1 / 3), ("ADR", 5, 1 / 3)], "first", "ema21", {"fail_d1": True}),
    "E10: BE at +1R, 1/2 +2R, rest 21EMA": ([("R", 2, 0.5)], ("R", 1.0), "ema21", {}),
    "E11: 1/2 +1R, rest trails the prior day's low": ([("R", 1, 0.5)], "first", "prevlow", {}),
    "E12: out at the day-5 close": ([], None, None, {"max_days": 5}),
    "E13: 1/3 +1R, 1/3 +2R, BE, rest 10EMA": ([("R", 1, 1 / 3), ("R", 2, 1 / 3)], "first", "ema10", {}),
}


def run_x(a, k, buy, stop, spec, bars=None):
    st = a.st
    c, o, h, l = st.c, st.o, st.h, st.l
    targets, be, runner, ex = spec
    adr = float(st.adr[k - 1])
    R = buy - stop
    if R <= 0:
        return None
    lvl = lambda u, v: buy + v * R if u == "R" else buy * (1 + v * adr / 100)
    tg = sorted((lvl(u, v), f) for u, v, f in targets)
    hit = [False] * len(tg)
    be_lv = lvl(*be) if isinstance(be, tuple) else None
    ema = a.e10 if runner == "ema10" else a.e21 if runner == "ema21" else None
    S = dict(stop=stop, left=1.0, got=0.0)

    def out(px):
        S["got"] += S["left"] * px
        S["left"] = 0.0
        return True

    def step(bo, bh, bl):
        if bl <= S["stop"]:
            return out(min(S["stop"], bo))
        for i, (p, f) in enumerate(tg):
            if not hit[i] and bh >= p:
                hit[i] = True
                take = min(f, S["left"])
                S["got"] += take * max(p, bo)
                S["left"] -= take
        if S["left"] <= 1e-9:
            return True
        if (be == "first" and any(hit)) or (be_lv is not None and bh >= be_lv):
            S["stop"] = max(S["stop"], buy)
        return False

    done = False
    if bars:
        for n, x in enumerate(bars):
            if step(buy if n == 0 else x["o"], x["h"], x["l"]):
                done = True
                break
    if not done and ema is not None and c[k] < ema[k]:
        done = out(c[k])
    j = k + 1
    while not done and j < c.size:
        if runner == "prevlow":
            S["stop"] = max(S["stop"], l[j - 1])
        if step(o[j], h[j], l[j]):
            break
        d = j - k
        if ex.get("fail_d1") and d == 1 and c[j] < buy:
            done = out(c[j])
        elif "time" in ex and d == ex["time"][0] and c[j] < buy + ex["time"][1] * R:
            done = out(c[j])
        elif ema is not None and c[j] < ema[j]:
            done = out(c[j])
        elif ex.get("max_days") and d >= ex["max_days"]:
            done = out(c[j])
        j += 1
    if S["left"] > 1e-9:
        out(c[min(j, c.size - 1)])
    ret = 100 * (S["got"] / buy - 1)
    return round(ret, 2), round(100 * R / buy, 2)


def cols(a, k, buy, stop, pre, bars=None):
    """{pre + 'x<n>_ret': result %, pre + 'x_risk': risk %} for every exit plan"""
    out = {}
    for n, (nm, spec) in enumerate(SPECS.items()):
        r = run_x(a, k, buy, stop, spec, bars)
        if r is None:
            return {}
        out[f"{pre}x{n}_ret"] = r[0]
        out[f"{pre}x_risk"] = r[1]
    return out
