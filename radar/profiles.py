#!/usr/bin/env python3
"""Each stock's Yahoo profile: its finer industry (e.g. "Banks - Regional", "Software - Infrastructure") and the start of
its business description, for building sub-groups by what the companies do (the user, Nov 3 2026).

  python3 radar/profiles.py <stocks.json> <out profiles.json>
"""
import concurrent.futures as cf, datetime, json, sys, time, urllib.parse, zoneinfo
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from live import Yahoo

NY = zoneinfo.ZoneInfo("America/New_York")


def main():
    syms = sorted({r["symbol"] for r in json.load(open(sys.argv[1]))})
    y = Yahoo()
    if not y.login():
        sys.exit("could not get a Yahoo crumb")

    def one(s):
        url = (f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{urllib.parse.quote(s.replace('/', '-'))}"
               f"?modules=assetProfile&crumb={urllib.parse.quote(y.crumb)}")
        for attempt in range(3):
            try:
                p = json.loads(y.get(url))["quoteSummary"]["result"][0].get("assetProfile") or {}
                return s, {"industry": p.get("industry"), "sector": p.get("sector"), "about": (p.get("longBusinessSummary") or "")[:700]}
            except Exception:
                time.sleep(2 * (attempt + 1))
        return s, None

    with cf.ThreadPoolExecutor(6) as pool:
        rows = {s: v for s, v in pool.map(one, syms) if v}
    json.dump({"built_at": datetime.datetime.now(NY).isoformat(timespec="seconds"), "rows": rows}, open(sys.argv[2], "w"), separators=(",", ":"))
    print(json.dumps({"symbols": len(syms), "with_profile": len(rows), "with_industry": sum(1 for v in rows.values() if v["industry"])}))


if __name__ == "__main__":
    main()
