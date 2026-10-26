#!/usr/bin/env python3
"""5-minute live prices for Theme & Group Radar.

  python3 radar/live.py <stocks.json> <themes.json> <out live.json> [--force]

Pulls Yahoo quotes for every stock in stocks.json plus the theme ETFs, in batches, and writes
live.json: {"saved_at", "date", "session", "n", "source",
            "rows": {SYM: [price, chg_1d %, volume, quote time, relative volume at time]}}.
Relative volume at time = today's volume from 9:30 to the quote time / the 20-session average volume from
9:30 to the same minute (from volprofile.json, --profile <path>); null without a curve or before 9:31.
Runs only from 9:30 AM to 4:10 PM ET on trading days unless --force is given (exits 3 = nothing to do).
"""
import concurrent.futures as cf, datetime, http.cookiejar, json, sys, time, urllib.error, urllib.parse, urllib.request, zoneinfo

NY = zoneinfo.ZoneInfo("America/New_York")
HOLIDAYS = set("2026-11-26 2026-12-25 2027-01-01 2027-01-18 2027-02-15 2027-03-26 2027-05-31 2027-06-18 "
               "2027-07-05 2027-09-06 2027-11-25 2027-12-24".split())
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BATCH = 150


def yahoo_sym(s):
    return s.replace("/", "-").replace(".", "-")


class Yahoo:
    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        self.op.addheaders = [("User-Agent", UA), ("Accept", "*/*"), ("Accept-Language", "en-US,en;q=0.9")]
        self.crumb = None

    def get(self, url, timeout=25):
        with self.op.open(url, timeout=timeout) as r:
            return r.read()

    def login(self):
        for url in ("https://fc.yahoo.com/", "https://finance.yahoo.com/"):
            try:
                self.get(url, 15)
            except urllib.error.HTTPError:
                pass          # fc.yahoo.com answers 404 but still sets the cookie
            except Exception:
                continue
            try:
                c = self.get("https://query2.finance.yahoo.com/v1/test/getcrumb", 15).decode().strip()
                if c and "<" not in c and len(c) < 40:
                    self.crumb = c
                    return True
            except Exception:
                pass
        return False

    def quotes(self, syms):
        """v7 quote endpoint, BATCH symbols per call. Returns {yahoo_sym: [price, chg%, volume, time]}."""
        out = {}
        for i in range(0, len(syms), BATCH):
            chunk = syms[i:i + BATCH]
            q = urllib.parse.urlencode({"symbols": ",".join(chunk), "crumb": self.crumb,
                                        "fields": "regularMarketPrice,regularMarketChangePercent,regularMarketVolume,regularMarketTime"})
            for attempt in range(3):
                try:
                    res = json.loads(self.get("https://query2.finance.yahoo.com/v7/finance/quote?" + q))["quoteResponse"]["result"]
                    for r in res:
                        p = r.get("regularMarketPrice")
                        if p:
                            out[r["symbol"]] = [round(p, 4), round(r.get("regularMarketChangePercent") or 0, 3),
                                                r.get("regularMarketVolume"), r.get("regularMarketTime")]
                    break
                except Exception as e:
                    if attempt == 2:
                        print(f"quote batch {i // BATCH} failed: {e}", file=sys.stderr)
                    time.sleep(2 * (attempt + 1))
        return out

    def chart(self, ysym):
        """fallback: one chart call per symbol (no crumb needed)."""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ysym)}?range=1d&interval=1d"
        for attempt in range(3):
            try:
                m = json.loads(self.get(url))["chart"]["result"][0]["meta"]
                p, pc = m.get("regularMarketPrice"), m.get("chartPreviousClose") or m.get("previousClose")
                if p and pc:
                    return [round(p, 4), round((p / pc - 1) * 100, 3), m.get("regularMarketVolume"), m.get("regularMarketTime")]
                return None
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return None
                time.sleep(2 * (attempt + 1))
            except Exception:
                time.sleep(2 * (attempt + 1))
        return None


def rvol_at(vol, qtime, curve):
    """today's volume so far / the average volume from 9:30 to the same minute"""
    if not vol or not qtime or not curve:
        return None
    t = datetime.datetime.fromtimestamp(qtime, NY)
    m = min(t.hour * 60 + t.minute + t.second / 60, 960) - 570       # minutes since 9:30, capped at 4:00
    if m < 1:
        return None
    pos = m / 5                                                       # curve[j] = average through 9:30 + 5(j+1) min
    j = int(pos)
    lo = curve[j - 1] if j >= 1 else 0
    hi = curve[min(j, len(curve) - 1)]
    exp = lo + (hi - lo) * (pos - j) if j < len(curve) else curve[-1]
    return round(vol / exp, 2) if exp > 0 else None


def main():
    stocks_p, themes_p, out_p = sys.argv[1:4]
    prof = {}
    if "--profile" in sys.argv:
        try:
            prof = json.load(open(sys.argv[sys.argv.index("--profile") + 1]))["rows"]
        except Exception as e:
            print(f"no volume curves: {e}", file=sys.stderr)
    force = "--force" in sys.argv
    now = datetime.datetime.now(NY)
    if not force and (now.weekday() >= 5 or now.date().isoformat() in HOLIDAYS
                      or not ((now.hour, now.minute) >= (9, 30) and (now.hour, now.minute) <= (16, 10))):
        print("outside market hours: nothing to do")
        sys.exit(3)
    stocks = json.load(open(stocks_p))
    themes = json.load(open(themes_p))
    syms = [r["symbol"] for r in stocks]
    syms += sorted({e for t in themes for e in (t.get("etfs") or "").split()} - set(syms))
    ymap = {yahoo_sym(s): s for s in syms}
    y = Yahoo()
    got, source = {}, ""
    if y.login():
        got = y.quotes(list(ymap))
        source = "yahoo quote"
    if len(got) < 0.5 * len(ymap):     # crumb refused or blocked: fall back to chart calls for the liquid names
        source = "yahoo chart"
        liquid = [yahoo_sym(r["symbol"]) for r in stocks
                  if (r.get("mcap_b") or 0) >= 0.7 and (r.get("avg_vol_30d") or 0) >= 300_000]
        liquid += [yahoo_sym(s) for s in syms[len(stocks):]]
        todo = [s for s in liquid if s not in got]
        with cf.ThreadPoolExecutor(12) as pool:
            for s, v in zip(todo, pool.map(y.chart, todo)):
                if v:
                    got[s] = v
    rows = {ymap[k]: v for k, v in got.items() if k in ymap}
    for s, v in rows.items():
        v.append(rvol_at(v[2], v[3], prof.get(s)))
    if len(rows) < 300:
        sys.exit(f"only {len(rows)} quotes came back, not saving")
    times = sorted(v[3] for v in rows.values() if v[3])
    session = datetime.datetime.fromtimestamp(times[len(times) // 2], NY).date().isoformat() if times else now.date().isoformat()
    json.dump({"saved_at": now.isoformat(timespec="seconds"), "date": now.date().isoformat(), "session": session,
               "n": len(rows), "source": source, "rows": rows}, open(out_p, "w"), separators=(",", ":"))
    print(json.dumps({"saved_at": now.isoformat(timespec="seconds"), "session": session, "quotes": len(rows),
                      "with_rvol": sum(1 for v in rows.values() if v[4] is not None),
                      "of": len(ymap), "source": source}))


if __name__ == "__main__":
    main()
