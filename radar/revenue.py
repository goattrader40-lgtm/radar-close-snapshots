#!/usr/bin/env python3
"""Revenue for every theme member (Yahoo financial data), so the portal can show which names have a real business.

  python3 radar/revenue.py <themes.json> <out revenue.json>

Writes {"built_at", "rows": {SYM: {"q_rev_m": latest quarter's revenue $M, "q": that quarter (e.g. "3Q2026"),
"growth": that quarter's revenue vs the same quarter a year earlier %, "rev_m": trailing-12-month revenue $M,
"margin": profit margin %, "next_q_growth": analysts' average revenue estimate for the quarter now under way vs the
same quarter a year earlier %, "next_q_est_m": that estimate $M, "next_q_end": the quarter's end date}}}.
Company guidance itself isn't in any free data feed; the analysts' consensus usually sits close to it after a report.
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
               f"?modules=financialData,earnings,earningsTrend&crumb={urllib.parse.quote(y.crumb)}")
        for attempt in range(3):
            try:
                res = json.loads(y.get(url))["quoteSummary"]["result"][0]
                fd = res.get("financialData") or {}
                g = lambda k: (fd.get(k) or {}).get("raw")
                rev = g("totalRevenue")
                qs = (((res.get("earnings") or {}).get("financialsChart") or {}).get("quarterly") or [])
                last = qs[-1] if qs else {}
                qrev = (last.get("revenue") or {}).get("raw")
                tr = {t.get("period"): t for t in ((res.get("earningsTrend") or {}).get("trend") or [])}
                nq = tr.get("0q") or {}
                re_ = nq.get("revenueEstimate") or {}
                eg = (re_.get("growth") or {}).get("raw")
                ea = (re_.get("avg") or {}).get("raw")
                return s, {"q_rev_m": None if qrev is None else round(qrev / 1e6, 1), "q": last.get("date"),
                           "next_q_end": nq.get("endDate"), "next_q_est_m": None if ea is None else round(ea / 1e6, 1),
                           "next_q_growth": None if eg is None else round(eg * 100, 1), "next_q_analysts": (re_.get("numberOfAnalysts") or {}).get("raw"),
                           "rev_m": None if rev is None else round(rev / 1e6, 1),
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
