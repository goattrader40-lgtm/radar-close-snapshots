#!/usr/bin/env python3
"""Umbrella and industry ETFs for Theme & Group Radar.

  python3 radar/etfs.py <themes.json> <out etfs.json>

Each area of themes has a main ETF that moves the whole area (SMH for AI & semis, IGV for software, ...),
and each broad industry has its main ETF. This saves, for those ETFs plus every theme ETF, the latest close and
the 1D / 1W / 1M / 3M change from Yahoo daily bars, with the reference closes the 5-minute live job uses
(same conventions as stocks.json: 1W = 5 sessions, 1M = 21, 3M = 63), plus the 200-day SMA and the 50-day EMA
at the last close (the portal shows the ETF's price vs each; none for an ETF too young to have them).
Output: {"built_at", "areas": {area: ETF}, "industries": {industry: ETF}, "rows": {ETF: {...}}}
"""
import concurrent.futures as cf, datetime, json, sys, time, urllib.error, urllib.request, zoneinfo

NY = zoneinfo.ZoneInfo("America/New_York")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# main ETF per area (the "umbrella": when it moves, most themes under it move)
AREAS = {
    "AI & Semis": "SMH", "AI Infrastructure": "GRID", "Software": "IGV", "Internet": "FDN", "Financials": "XLF",
    "Industrial Frontier": "XLI", "Energy": "XLE", "Metals & Mining": "XME", "Materials": "XLB", "Clean Energy": "ICLN",
    "Healthcare": "XLV", "Consumer": "XLY", "Transports": "IYT", "Auto groups": "SPY",
}
# main ETF per broad industry (FinanceDatabase industry names)
INDUSTRIES = {
    "Semiconductors & Chip Equipment": "SMH", "Software": "IGV", "IT Services": "IGV", "Biotechnology": "XBI",
    "Pharmaceuticals": "XPH", "Medical Devices & Supplies": "IHI", "Health Care Providers": "IHF",
    "Health Care Technology": "XLV", "Life Science Tools": "XLV", "Banks": "KBE", "Capital Markets": "IAI",
    "Insurance": "KIE", "Consumer Lending": "XLF", "Mortgage Finance": "XLF", "Payments & Specialty Finance": "IPAY",
    "Mining & Metals": "XME", "Oil, Gas & Fuels": "XLE", "Oilfield Services & Equipment": "OIH", "Chemicals": "XLB",
    "Packaging": "XLB", "Building Materials": "XLB", "Paper & Wood Products": "XLB", "Aerospace & Defense": "ITA",
    "Machinery": "XLI", "Electrical Equipment": "XLI", "Professional Services": "XLI", "Commercial Services": "XLI",
    "Industrial Distribution & Rental": "XLI", "Conglomerates": "XLI", "Wholesale Distributors": "XLI",
    "Construction & Engineering": "PAVE", "Building Products": "XHB", "Household Durables": "ITB",
    "Electronic Components & Instruments": "XLK", "Networking & Communications Equipment": "XLK",
    "Computers & Hardware": "XLK", "Internet Media & Services": "FDN", "Entertainment": "XLC", "Media": "XLC",
    "Fixed & Integrated Telecom": "IYZ", "Wireless Telecom": "IYZ", "Hospitality & Leisure": "PEJ",
    "Specialty Retail": "XRT", "General & Online Retail": "XRT", "Apparel & Luxury Goods": "XLY",
    "Auto Parts": "XLY", "Automobiles": "XLY", "Consumer Services": "XLY", "Leisure Products": "XLY",
    "Grocery & Drug Retail": "XLP", "Food Products": "XLP", "Beverages": "XLP", "Household Products": "XLP",
    "Personal Care": "XLP", "Tobacco": "XLP", "Electric Utilities": "XLU", "Multi-Utilities": "XLU",
    "Water Utilities": "XLU", "Gas Utilities": "XLU", "Power Producers & Renewables": "XLU",
    "Rail & Road Transport": "IYT", "Freight & Logistics": "IYT", "Transport Infrastructure": "IYT",
    "Airlines": "JETS", "Shipping": "BWET", "Mortgage REITs": "REM", "Diversified REITs": "XLRE",
    "Retail REITs": "XLRE", "Specialty REITs": "XLRE", "Health Care REITs": "XLRE", "Residential REITs": "XLRE",
    "Industrial REITs": "XLRE", "Hotel REITs": "XLRE", "Office REITs": "XLRE", "Real Estate Development & Services": "XLRE",
}


def bars(sym):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=1y&interval=1d"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=25) as r:
                res = json.load(r)["chart"]["result"][0]
            q = res["indicators"]["quote"][0]
            adj = (res["indicators"].get("adjclose") or [{}])[0].get("adjclose") or q["close"]
            pts = [(datetime.datetime.fromtimestamp(t, NY).date(), c) for t, c in zip(res["timestamp"], adj) if c]
            name = (res.get("meta") or {}).get("longName") or (res.get("meta") or {}).get("shortName") or sym
            return sym, name, pts
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return sym, None, []
            time.sleep(2 * (attempt + 1))
        except Exception:
            time.sleep(2 * (attempt + 1))
    return sym, None, []


def ema_last(c, n=50):
    """n-day EMA at the last close, seeded with the first n-day SMA (needs 2n closes)"""
    if len(c) < 2 * n:
        return None
    e, k = sum(c[:n]) / n, 2 / (n + 1)
    for x in c[n:]:
        e += k * (x - e)
    return e


def main():
    themes_p, out_p = sys.argv[1], sys.argv[2]
    themes = json.load(open(themes_p))
    syms = set(AREAS.values()) | set(INDUSTRIES.values()) | {e for t in themes for e in (t.get("etfs") or "").split()}
    now = datetime.datetime.now(NY)
    unfinished = now.date() if now.weekday() < 5 and (9, 30) <= (now.hour, now.minute) < (16, 5) else None
    rows = {}
    with cf.ThreadPoolExecutor(8) as pool:
        for sym, name, pts in pool.map(bars, sorted(syms)):
            pts = [p for p in pts if p[0] != unfinished]       # only complete sessions
            if len(pts) < 70:
                continue
            c = [p[1] for p in pts]
            pct = lambda n: round((c[-1] / c[-1 - n] - 1) * 100, 2)
            rows[sym] = {"name": name, "asof": str(pts[-1][0]), "price": round(c[-1], 4), "chg_1d": pct(1), "chg_1w": pct(5),
                         "chg_1m": pct(21), "chg_3m": pct(63), "ref_1w": round(c[-5], 4), "ref_1m": round(c[-21], 4),
                         "ref_3m": round(c[-63], 4),
                         "sma200": round(sum(c[-200:]) / 200, 4) if len(c) >= 200 else None,
                         "ema50": round(ema_last(c), 4) if ema_last(c) else None}
    if len(rows) < 0.7 * len(syms):
        sys.exit(f"only {len(rows)} of {len(syms)} ETFs came back, not saving")
    json.dump({"built_at": now.isoformat(timespec="seconds"), "areas": AREAS, "industries": INDUSTRIES, "rows": rows},
              open(out_p, "w"), separators=(",", ":"))
    print(json.dumps({"etfs": len(rows), "of": len(syms), "missing": sorted(syms - set(rows))}))


if __name__ == "__main__":
    main()
