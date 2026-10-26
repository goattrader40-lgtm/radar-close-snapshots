#!/usr/bin/env python3
"""Trailing-12-month revenue for every theme member (Yahoo financial data), to spot speculative names.

  python3 radar/revenue.py <themes.json> <out revenue.json>

Writes {"built_at", "rows": {SYM: {"rev_m": TTM revenue $M, "growth": revenue growth %, "margin": profit margin %}}}.
"""
import concurrent.futures as cf, datetime, json, sys, time, urllib.parse, zoneinfo
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from live import Yahoo

NY = zoneinfo.ZoneInfo("America/New_York")


def main():
    themes = json.load(open(sys.argv[1]))
    syms = sorted({x for t in themes for x in ((t.get("members") or "") + " " + (t.get("ext") or "")).split()})
    y = Yahoo()
    if not y.login():
        sys.exit("could not get a Yahoo crumb")

    def one(s):
        url = (f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{urllib.parse.quote(s.replace('/', '-'))}"
               f"?modules=financialData&crumb={urllib.parse.quote(y.crumb)}")
        for attempt in range(3):
            try:
                fd = json.loads(y.get(url))["quoteSummary"]["result"][0]["financialData"]
                g = lambda k: (fd.get(k) or {}).get("raw")
                rev = g("totalRevenue")
                return s, {"rev_m": None if rev is None else round(rev / 1e6, 1),
                           "growth": None if g("revenueGrowth") is None else round(g("revenueGrowth") * 100, 1),
                           "margin": None if g("profitMargins") is None else round(g("profitMargins") * 100, 1)}
            except Exception:
                time.sleep(2 * (attempt + 1))
        return s, None

    with cf.ThreadPoolExecutor(6) as pool:
        rows = {s: v for s, v in pool.map(one, syms) if v}
    json.dump({"built_at": datetime.datetime.now(NY).isoformat(timespec="seconds"), "rows": rows},
              open(sys.argv[2], "w"), separators=(",", ":"))
    print(json.dumps({"symbols": len(syms), "with_data": len(rows)}))


if __name__ == "__main__":
    main()
