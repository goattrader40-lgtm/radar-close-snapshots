#!/usr/bin/env python3
"""A real run of the movers' 1-minute read (radar/movers.py + radar/levels.py) on a copy of the live files, nothing
published live: how many stocks, how long each step takes, and how the rows moved since the full update.

  python3 radar/probe_movers.py <dir with live.json levels.json volprofile.json stocks.json> <out.json> [rounds]
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    d, out_p = sys.argv[1], sys.argv[2]
    rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    f = lambda n: os.path.join(d, n)
    live = json.load(open(f("live.json")))
    lev0 = len((json.load(open(f("levels.json"))).get("rows") or {})) if os.path.exists(f("levels.json")) else 0
    res = {"full_update": live.get("saved_at"), "levels_before": lev0, "rounds": []}
    for i in range(rounds):
        t0 = time.time()
        r = subprocess.run([sys.executable, os.path.join(HERE, "movers.py"), f("live.json"), f("nofast.json"), f("levels.json"),
                            f("volprofile.json"), f("nocal.json"), f("stocks.json"), f("merged.json")], capture_output=True, text=True)
        t1 = time.time()
        r2 = subprocess.run([sys.executable, os.path.join(HERE, "levels.py"), f("merged.json"), f("levels.json")], capture_output=True, text=True)
        t2 = time.time()
        row = {"movers_s": round(t1 - t0, 1), "levels_s": round(t2 - t1, 1), "movers": (r.stdout or r.stderr).strip()[-200:],
               "levels": (r2.stdout or r2.stderr).strip()[-200:]}
        if r.returncode == 0:
            m = json.load(open(f("merged.json")))
            ch = [(s, live["rows"][s][0], q[0], live["rows"][s][1], q[1]) for s, q in m["rows"].items() if q != live["rows"].get(s)]
            ch.sort(key=lambda x: -abs(x[4] - x[3]))
            row.update(fast_at=m.get("fast_at"), fast_n=m.get("fast_n"), changed=len(ch),
                       biggest=[{"sym": s, "price_full": a, "price_now": b, "chg_full": c, "chg_now": e} for s, a, b, c, e in ch[:12]])
        res["rounds"].append(row)
        if i < rounds - 1:
            time.sleep(max(0, 60 - (time.time() - t0)))
    json.dump(res, open(out_p, "w"), indent=1)
    print(json.dumps(res)[:1500])


if __name__ == "__main__":
    main()
