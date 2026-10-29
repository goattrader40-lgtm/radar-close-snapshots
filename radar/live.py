#!/usr/bin/env python3
"""5-minute live prices for Theme & Group Radar.

  python3 radar/live.py <stocks.json> <themes.json> <out live.json> [--force]

Pulls Yahoo quotes for every stock in stocks.json plus the theme ETFs, in batches, and writes
live.json: {"saved_at", "date", "session", "n", "source",
            "rows": {SYM: [price, chg_1d %, volume, quote time, relative volume at time, today's open, earnings time, today's high]}}.
Today's high lets the alerts see a stock that traded over its buy point between two updates and fell back.
Relative volume at time = today's volume from 9:30 to the quote time / the 20-session average volume from
9:30 to the same minute (from volprofile.json, --profile <path>); null without a curve or before 9:31.
From 4:00 on it is the full day / the previous 20 sessions' full-day average (avg_vol_20 in stocks.json).
With --sipcal <state file> the volume is first corrected against the consolidated tape (radar/sipcal.py:
Yahoo's live volume runs ahead of it during the session, a median +11% on Oct 27 2026).
Runs only from 9:30 AM to 4:10 PM ET on trading days unless --force is given (exits 3 = nothing to do).
"""
import concurrent.futures as cf, datetime, http.cookiejar, json, os, sys, time, urllib.error, urllib.parse, urllib.request, zoneinfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sipcal  # noqa: E402

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
        """v7 quote endpoint, BATCH symbols per call. Returns {yahoo_sym: [price, chg%, volume, time, open, earnings, day high]}."""
        out = {}
        for i in range(0, len(syms), BATCH):
            chunk = syms[i:i + BATCH]
            q = urllib.parse.urlencode({"symbols": ",".join(chunk), "crumb": self.crumb,
                                        "fields": "regularMarketPrice,regularMarketChangePercent,regularMarketVolume,regularMarketTime,regularMarketOpen,earningsTimestamp,regularMarketDayHigh"})
            for attempt in range(3):
                try:
                    res = json.loads(self.get("https://query2.finance.yahoo.com/v7/finance/quote?" + q))["quoteResponse"]["result"]
                    for r in res:
                        p = r.get("regularMarketPrice")
                        if p:
                            op, hi = r.get("regularMarketOpen"), r.get("regularMarketDayHigh")
                            out[r["symbol"]] = [round(p, 4), round(r.get("regularMarketChangePercent") or 0, 3),
                                                r.get("regularMarketVolume"), r.get("regularMarketTime"), round(op, 4) if op else None,
                                                r.get("earningsTimestamp"), round(hi, 4) if hi else None]
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
                    hi = m.get("regularMarketDayHigh")
                    return [round(p, 4), round((p / pc - 1) * 100, 3), m.get("regularMarketVolume"), m.get("regularMarketTime"), None, None,
                            round(hi, 4) if hi else None]
                return None
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return None
                time.sleep(2 * (attempt + 1))
            except Exception:
                time.sleep(2 * (attempt + 1))
        return None


def fill_opens(y, got, now, limit=80, cache_p="/tmp/radar/out/opens.json"):
    """Yahoo's quote leaves an NYSE stock's open empty for its first ~10 minutes (Oct 28 2026: STNG and EAT met their
    alert rules at 9:35 / 9:37 and alerted at 9:45, while Nasdaq's ICLR and AXGN alerted at 9:35), and even with an open
    in it the alerts can wait (GKOS Oct 29: its 9:31 heads-up and 9:35 power day came at 9:46). So until 9:50 every stock
    moving 3%+ takes its open from Yahoo's 1-minute chart (the first bar from 9:30), once, kept for the day (cache_p);
    after that only those still without one. got: {yahoo sym: [price, chg, vol, time, open, earnings]}, filled in place.
    Returns [(symbol, the quote's open, the chart's)] for the ones taken from the chart this time."""
    if not ((now.hour, now.minute) >= (9, 30) and now.hour < 16):
        return []
    try:
        cache = json.load(open(cache_p))
        cache = cache["opens"] if cache.get("date") == now.date().isoformat() else {}
    except Exception:
        cache = {}
    for k, v in got.items():
        if k in cache:
            v[4] = cache[k]
    early = (now.hour, now.minute) < (9, 50)
    todo = [k for k, v in got.items() if k not in cache and abs(v[1] or 0) >= 3 and (v[4] is None or early)][:limit]

    def first_open(ysym):
        try:
            r = json.loads(y.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ysym)}?range=1d&interval=1m", 15))["chart"]["result"][0]
            for t, o in zip(r.get("timestamp") or [], r["indicators"]["quote"][0].get("open") or []):
                ts = datetime.datetime.fromtimestamp(t, NY)
                if o and ts.date() == now.date() and (ts.hour, ts.minute) >= (9, 30):
                    return round(o, 4)
        except Exception:
            pass
        return None
    done = []
    with cf.ThreadPoolExecutor(8) as pool:
        for k, o in zip(todo, pool.map(first_open, todo)):
            if o:
                done.append((k, got[k][4], o))
                got[k][4] = cache[k] = o
    if done:
        try:
            os.makedirs(os.path.dirname(cache_p), exist_ok=True)
            json.dump({"date": now.date().isoformat(), "opens": cache}, open(cache_p, "w"))
        except Exception:
            pass
    return done


def rvol_at(vol, qtime, curve, avg20=None):
    """today's volume so far / the average volume from 9:30 to the same minute.
    From 4:00 the quote's volume includes the closing auction, which the curves (9:30-3:59) leave out, so it is
    the full day / the previous 20 sessions' full-day average instead, the same number the after-close rebuild shows."""
    if not vol or not qtime:
        return None
    t = datetime.datetime.fromtimestamp(qtime, NY)
    if (t.hour, t.minute) >= (16, 0):
        return round(vol / avg20, 2) if avg20 else None
    if not curve:
        return None
    m = t.hour * 60 + t.minute + t.second / 60 - 570                 # minutes since 9:30
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
    etf = {e for t in themes for e in (t.get("etfs") or "").split()}
    if "--etfs" in sys.argv:
        try:
            etf |= set(json.load(open(sys.argv[sys.argv.index("--etfs") + 1]))["rows"])
        except Exception as e:
            print(f"no etfs file: {e}", file=sys.stderr)
    syms += sorted(etf - set(syms))
    ymap = {yahoo_sym(s): s for s in syms}
    y = Yahoo()
    got, source = {}, ""
    if y.login():
        got = y.quotes(list(ymap))
        source = "yahoo quote"
    opened = fill_opens(y, got, now) if source == "yahoo quote" else []
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
    avg20 = {r["symbol"]: r.get("avg_vol_20") for r in stocks}
    off = {}
    if "--sipcal" in sys.argv:
        try:
            off = sipcal.offsets(rows, sys.argv[sys.argv.index("--sipcal") + 1], set(prof), now)
        except Exception as e:
            print(f"sipcal failed: {e}", file=sys.stderr)
    fixed = 0
    for s, v in rows.items():
        hi = v.pop(6) if len(v) > 6 else None
        ern = v.pop(5) if len(v) > 5 else None
        op = v.pop(4) if len(v) > 4 else None
        fv = sipcal.corrected(v[2], v[3], off.get(s)) if off else None
        if fv is not None:
            v[2] = fv                                              # Yahoo's surplus over the exact volume, measured 16+ min ago
            fixed += 1
        v.append(rvol_at(v[2], v[3], prof.get(s), avg20.get(s)))
        v.append(op)                                               # the open, for the launch trigger's gap
        v.append(ern)                                              # the last / next earnings time, for the earnings tag
        v.append(hi)                                               # today's high: a buy point touched between updates
    if len(rows) < 300:
        sys.exit(f"only {len(rows)} quotes came back, not saving")
    times = sorted(v[3] for v in rows.values() if v[3])
    session = datetime.datetime.fromtimestamp(times[len(times) // 2], NY).date().isoformat() if times else now.date().isoformat()
    json.dump({"saved_at": now.isoformat(timespec="seconds"), "date": now.date().isoformat(), "session": session,
               "n": len(rows), "source": source, "open_from_chart": sorted(ymap.get(k[0], k[0]) for k in opened), "rows": rows},
              open(out_p, "w"), separators=(",", ":"))
    print(json.dumps({"saved_at": now.isoformat(timespec="seconds"), "session": session, "quotes": len(rows),
                      "with_rvol": sum(1 for v in rows.values() if v[4] is not None), "volume_corrected": fixed,
                      "of": len(ymap), "source": source}))


if __name__ == "__main__":
    main()
