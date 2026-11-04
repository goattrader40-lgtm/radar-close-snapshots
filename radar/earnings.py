#!/usr/bin/env python3
"""The Earnings tab: this week's reports for the stocks that pass your rules, their results, guidance and the read.

  python3 radar/earnings.py <stocks.json> <previous earnings.json or ""> <out earnings.json>

No Claude: every number comes from free sources, every read from fixed rules.
  calendar   Nasdaq's earnings calendar, Monday to Friday of this week (Saturday / Sunday: next week)
  who        stocks.json (the last close) with your Earnings rules (scanner/settings.json "earnings"): market cap
             $700M+, 20-day average $ volume $30M+ and 600K+ shares, price $10+, ADR 3.5%+, 30%+ over the 52-week low.
             Once on this week's list a stock stays for the week. Not filtered on the 50 EMA: the table shows it.
  estimates  Yahoo (earningsTrend) for the quarter being reported, the next quarter and the year, saved before the
             report: after a report Yahoo moves on to the next quarter, so they are frozen once the report is in
  results    the company's press release (SEC 8-K item 2.02, exhibit 99) filed at release time: revenue, and the
             guidance read from its outlook text; EPS from Yahoo (earningsHistory) or Nasdaq (adjusted, like the
             estimate); Yahoo's quarterly revenue as the backup
  prices     Yahoo quotes: the pre-market price (after hours on the evening of an after-close report, the live
             price during the session); vs 200D / vs 50 EMA against stocks.json (the last close); vs 20D high against
             the highest high of the previous 20 sessions (Yahoo daily bars); over the 52-week low.
  read       Strong bullish / Bullish / Mixed / Somewhat bearish / Bearish, from points (see score()).
The SEC wants a contact in the User-Agent: the SEC_UA secret.
"""
import concurrent.futures as cf, datetime, html, json, os, re, sys, time, urllib.parse, urllib.request, zoneinfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live import Yahoo, UA, HOLIDAYS  # noqa: E402

NY = zoneinfo.ZoneInfo("America/New_York")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = json.load(open(os.path.join(ROOT, "scanner", "settings.json")))["earnings"]
SEC_UA = (os.environ.get("SEC_UA") or "").strip() or "radar-close-snapshots research"
GV = 7          # the press-release reader's version: a change re-reads every release of the week
MON = {m: i for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}


def http(url, ua=UA, timeout=25):
    rq = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "application/json, text/html, */*",
                                              "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(rq, timeout=timeout) as r:
        return r.read()


def retry(fn, n=3, wait=1.5):
    for i in range(n):
        try:
            return fn()
        except Exception:
            if i == n - 1:
                raise
            time.sleep(wait * (i + 1))


def num(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).replace("$", "").replace(",", "").strip()
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg else v


def pct(a, b):
    """a vs b in %, None when either is missing; growth off a negative or zero base is not a percentage"""
    if a is None or b is None or b <= 0:
        return None
    return round((a / b - 1) * 100, 1)


# ───────── who: your rules on the last close ─────────
def passes(s):
    p, lo = s.get("price") or 0, s.get("low_52w")
    return ((s.get("mcap_b") or 0) * 1e9 >= RULES["min_mcap"] and (s.get("avg_vol_20") or 0) >= RULES["min_avg_vol_20d"]
            and (s.get("dvol_20_m") or 0) >= RULES["min_dollar_vol_20d_millions"] and p >= RULES["min_price"]
            and (s.get("adr_20") or 0) >= RULES["min_adr"] and (s.get("mcap_b") or 0) * 1e9 <= RULES.get("max_mcap", 9e99)
            and (not lo or p >= lo * (1 + RULES["min_pct_above_52w_low"] / 100)))


# ───────── calendar: Nasdaq, the week's days ─────────
def week_days(now):
    d = now.date()
    mon = d + datetime.timedelta(days=(7 - d.weekday()) if d.weekday() >= 5 else -d.weekday())
    return [(mon + datetime.timedelta(days=i)).isoformat() for i in range(5)]


def trading(d):
    return d.weekday() < 5 and d.isoformat() not in HOLIDAYS


def back(d, n=1):
    """n trading days before d"""
    while n:
        d -= datetime.timedelta(days=1)
        if trading(d):
            n -= 1
    return d


def reaction_days(now):
    """t0 = today (the last trading day on a weekend or holiday), p1 / p2 = the 1 / 2 trading days before it.
    Today's reactions = t0 before the open + p1 after the close; Day 2 = p1 before the open + p2 after the close."""
    t0 = now.date() if trading(now.date()) else back(now.date())
    return t0.isoformat(), back(t0).isoformat(), back(t0, 2).isoformat()


def nasdaq(day):
    j = json.loads(retry(lambda: http(f"https://api.nasdaq.com/api/calendar/earnings?date={day}")))
    return ((j.get("data") or {}).get("rows")) or []


def q_end(fq):
    """Nasdaq's 'Sep/2026' -> (2026, 9)"""
    m = re.match(r"([A-Za-z]{3})/(\d{4})", fq or "")
    return (int(m.group(2)), MON.get(m.group(1).title())) if m else None


def qshift(q, n):
    """(2026, 9) shifted by n quarters: qshift((2026, 9), -1) = (2026, 6)"""
    k = q[0] * 12 + (q[1] - 1) + 3 * n
    return (k // 12, k % 12 + 1)


def ym(iso):
    return (int(iso[:4]), int(iso[5:7])) if iso and len(iso) >= 7 else None


def near(a, b):
    """the same fiscal quarter, a month apart allowed (Nasdaq says Aug, Yahoo the 31st or the next month's end)"""
    return bool(a and b and abs((a[0] * 12 + a[1]) - (b[0] * 12 + b[1])) <= 1)


def pick(d, k):
    return next((v for kk, v in d.items() if near(kk, k)), None) if k else None


# ───────── Yahoo: report time, estimates, EPS, quotes, daily bars ─────────
class Y:
    def __init__(self):
        self.y = Yahoo()
        if not self.y.login():
            raise SystemExit("could not get a Yahoo crumb")

    def get(self, url):
        return json.loads(retry(lambda: self.y.get(url + ("&" if "?" in url else "?") + "crumb=" + urllib.parse.quote(self.y.crumb))))

    def summary(self, s):
        res = self.get(f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{urllib.parse.quote(s)}"
                       f"?modules=earningsHistory,earningsTrend")["quoteSummary"]["result"][0]
        hist = {}
        for h in (res.get("earningsHistory") or {}).get("history") or []:
            q = (h.get("quarter") or {}).get("fmt")
            if q:
                hist[ym(q)] = {"act": (h.get("epsActual") or {}).get("raw"), "est": (h.get("epsEstimate") or {}).get("raw")}
        trend = {}
        for t in (res.get("earningsTrend") or {}).get("trend") or []:
            e, r = t.get("earningsEstimate") or {}, t.get("revenueEstimate") or {}
            trend[t.get("period")] = {"end": t.get("endDate"), "eps": (e.get("avg") or {}).get("raw"),
                                      "eps_yago": (e.get("yearAgoEps") or {}).get("raw"),
                                      "rev": (r.get("avg") or {}).get("raw"), "rev_yago": (r.get("yearAgoRevenue") or {}).get("raw")}
        return hist, trend

    def revenue_ts(self, s):
        now = int(time.time())
        res = self.get(f"https://query1.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{urllib.parse.quote(s)}"
                       f"?type=quarterlyTotalRevenue&period1={now - 86400 * 800}&period2={now}")["timeseries"]["result"]
        out = {}
        for t in res:
            for v in t.get("quarterlyTotalRevenue") or []:
                if v and v.get("asOfDate"):
                    out[ym(v["asOfDate"])] = (v.get("reportedValue") or {}).get("raw")
        return out

    def quotes(self, syms):
        out = {}
        for i in range(0, len(syms), 100):
            q = urllib.parse.urlencode({"symbols": ",".join(syms[i:i + 100]),
                                        "fields": "regularMarketPrice,regularMarketPreviousClose,regularMarketTime,preMarketPrice,"
                                                  "preMarketTime,postMarketPrice,postMarketTime,marketState,earningsTimestamp,"
                                                  "isEarningsDateEstimate"})
            for r in self.get("https://query2.finance.yahoo.com/v7/finance/quote?" + q)["quoteResponse"]["result"]:
                out[r["symbol"]] = r
        return out

    def high20(self, s, today):
        """the highest high of the previous 20 sessions (today's bar left out)"""
        j = self.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(s)}?range=3mo&interval=1d")
        r = j["chart"]["result"][0]
        ts, hi = r.get("timestamp") or [], ((r.get("indicators") or {}).get("quote") or [{}])[0].get("high") or []
        bars = [(datetime.datetime.fromtimestamp(t, NY).date().isoformat(), h) for t, h in zip(ts, hi) if h]
        bars = [b for b in bars if b[0] < today][-20:]
        return round(max(h for _, h in bars), 4) if len(bars) >= 10 else None


# ───────── SEC: the results press release ─────────
class SEC:
    def __init__(self):
        self.cik = {}
        try:
            t = json.loads(retry(lambda: http("https://www.sec.gov/files/company_tickers.json", SEC_UA)))
            self.cik = {v["ticker"].upper(): int(v["cik_str"]) for v in t.values()}
        except Exception as e:
            print("SEC tickers:", repr(e)[:200])

    def release(self, sym, since):
        """the newest 8-K with item 2.02 accepted on or after `since` (ISO date): (filed ET, url, plain text)"""
        c = self.cik.get(sym.upper().replace("-", ".")) or self.cik.get(sym.upper().replace(".", "-")) or self.cik.get(sym.upper())
        if not c:
            return None
        sub = json.loads(retry(lambda: http(f"https://data.sec.gov/submissions/CIK{c:010d}.json", SEC_UA)))
        f = sub["filings"]["recent"]
        for i, form in enumerate(f["form"]):
            if form not in ("8-K", "6-K") or (form == "8-K" and "2.02" not in (f["items"][i] or "")):
                continue
            acc_t = datetime.datetime.fromisoformat(f["acceptanceDateTime"][i].replace("Z", "+00:00")).astimezone(NY)
            if acc_t.date().isoformat() < since:
                return None                                     # the newest results filing is older: not out yet
            acc = f["accessionNumber"][i]
            base = f"https://www.sec.gov/Archives/edgar/data/{c}/{acc.replace('-', '')}/"
            docs = [d["name"] for d in json.loads(retry(lambda: http(base + "index.json", SEC_UA)))["directory"]["item"]]
            htm = [d for d in docs if d.lower().endswith((".htm", ".html")) and "index" not in d.lower()]
            ex = [d for d in htm if re.search(r"ex[-_]?99|exh?99|exhibit[-_]?99|ex-?99|991|pressrelease|press", d, re.I)]
            pick = (ex or [d for d in htm if d != f["primaryDocument"][i]] or htm or [None])[0]
            if not pick:
                return None
            raw = http(base + pick, SEC_UA).decode("utf-8", "replace")
            txt = re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style).*?</\1>", " ", raw))
            txt = re.sub(r"\s+", " ", html.unescape(txt)).strip()
            return {"filed": acc_t.isoformat(timespec="minutes"), "url": base + pick, "text": txt}
        return None


UNIT = {"million": 1e6, "billion": 1e9, "m": 1e6, "b": 1e9, "mm": 1e6, "bn": 1e9, "thousand": 1e3}
MONEY = r"\$\s?(\d[\d,]*(?:\.\d+)?)\s*(million|billion|bn|mm|m|b)?\b"
RANGE2 = r"(?:\s*(?:to|-|–|—|−|and)\s*\$?\s?(\d[\d,]*(?:\.\d+)?)\s*(million|billion|bn|mm|m|b)?\b)?"   # '$375.0 − 415.0' (ADEA)


NEXT = re.compile(r"\s*(?:\(\d\)\s*)?(?:to\s+)?\$\s?(\d[\d,]*(?:\.\d+)?)\s*(million|billion|bn|mm|m|b)?\b", re.I)
ROWNUM = re.compile(r"\s*(?:\(\d\)\s*)?\$?\s?(\d[\d,]*(?:\.\d+)?)\s*(million|billion|bn|mm|m|b)?\b(?!\s*%)", re.I)
YEARS = re.compile(r"\b(?:Q[1-4]|fiscal|FY|(?:three|six|nine|twelve) months ended[^0-9]{0,30}\d{1,2},?)?\s*(20\d\d)\b[^$%]{0,40}?\b(20\d\d)\b", re.I)


def scaled(v, u, ref):
    """a $ figure in dollars: its own unit, else the table scale that fits the reference (thousands / millions)"""
    if u:
        return v * UNIT.get(u.lower(), 1)
    for sc in (1, 1e3, 1e6, 1e9):
        if 0.6 <= v * sc / ref <= 1.7:
            return v * sc
    return v


def same(v, raw, u, b):
    """v (read from the printed figure raw, e.g. '271.7') is last year's b, to the figure's own rounding
    ('$271.7M' = 271,713,000; but '$594 million' is not 595,700,000: VAL Nov 2 2026 was flat y/y)"""
    if not (v and b and raw and num(raw)):
        return False
    dec = len(raw.split(".")[1]) if "." in raw else 0
    half = 0.5 * 10 ** -dec * (v / num(raw)) + 1
    return half <= v * 0.002 and abs(v - b) <= half     # too rounded to tell ('$1.5 billion', IT / KD): not last year's


def rev_from(text, est, yago):
    """the quarter's revenue from the release's first part (before the outlook); checked against the estimate.
    Two figures in a row (a table: 'Revenues $271.7M $309.0M', or 'from $271.7 million to $309.0 million') = last
    year's and this year's: the one that is not last year's quarter (Yahoo's year-ago revenue), else the column of the
    later year in the table's header (DUOL Nov 3 2026: Q3 2025 $271.7M | Q3 2026 $309.0M; the reader took $271.7M)."""
    head = text[:12000]
    cut = re.search(r"\b(outlook|guidance)\b", head[1500:], re.I)
    if cut:
        head = head[:1500 + cut.start()]
    ref = est or yago
    gap = r"(?:[^$.;]|\.(?=\d)){0,70}?"              # '... increased 6.2% to $727.0 million' (SKY / SN)
    total = r"\btotal (?:net |operating )?(?:revenues?|sales)\b" + gap + MONEY
    anyrev = (r"\b(?:total |net |quarterly |record |third[- ]quarter |fourth[- ]quarter |first[- ]quarter |second[- ]quarter |q[1-4] )*"
              r"(?:revenues?|sales)\b(?: and other income)?" + gap + MONEY)
    # positions are in `text` (head is its start): the head's figures first, then 'Total revenue' in the tables further
    # down (TVTX Nov 2 2026: the table's Total revenue $224.6M; the text only had product sales)
    tbl = (r"\btotal (?:net |operating )?revenues?(?: and other income)?\s*(?:\(\d\)\s*)?:?\s*\$?\s?(\d[\d,]*(?:\.\d+)?)"   # a table row:
           r"\s*(million|billion)?\b(?!\s*%)")      # 'Total revenue 224,563 164,859' (not 'total revenue, grew 214%': DOCN)
    row1 = r"\b(?:reported )?(?:net )?(?:revenues?|sales)\s*(?:\(\d\)\s*)?:?\s*\$\s?(\d[\d,]*(?:\.\d+)?)\s*(million|billion)?\b(?!\s*%)"
    ms = [*re.compile(total, re.I).finditer(text, 0, len(head)), *re.compile(tbl, re.I).finditer(text, len(head), 40000),
          *re.compile(anyrev, re.I).finditer(text, 0, len(head)),
          *re.compile(row1, re.I).finditer(text, len(head), 40000)]   # 'Net Sales $ 3,715 $ 3,481' further down (EL, PRGO, CVI, ERO)
    for m in ms:
        if re.search(r"\b(?:for|of)\s+(?!the\b|our\b|its\b|\$|Q[1-4]\b|(?:Fiscal|First|Second|Third|Fourth|Quarter|Full|Year|"
                     r"Three|Six|Nine|Twelve|Total|Net|Fiscal|The|Our)\b)[A-Z][A-Za-z0-9]+|[®™]", m.group(0)):
            continue                                    # one product's sales ('sales of FILSPARI®', 'revenue for Lumvoa')
        if re.search(r"\b(?!GAAP\b|NYSE\b|EBITDA\b)[A-Z]{4,}[®™]?\s+(?:net\s+)?(?:product\s+)?$", text[max(0, m.start() - 40): m.start()]):
            continue                                    # 'FILSPARI net product sales of $200 million' (TVTX)
        # the company's 'Total revenue' first: the first revenue figure can be one product's (URGN Nov 4 2026:
        # 'ZUSDURI net product revenue of $68.0 million'; total revenue $89.0 million)
        pre = text[max(0, m.start() - 80): m.start()].lower()
        if re.search(r"expect|outlook|guidance|between|range|forecast", pre + m.group(0)[:60].lower()) \
                and not re.search(r"\bq[1-4] 20\d\d\s*$", pre):   # 'Q3 2026 Revenue of $321 million' after an outlook line (DOCN)
            continue
        if re.search(r"\b(?:nine|six|twelve) months\b|year[- ]to[- ]date|\bytd\b|for the (?:full )?(?:fiscal )?year\b|full[- ]year|trailing",
                     pre[-40:] + m.group(0).lower()):
            continue                                    # not the quarter ('Third Quarter Fiscal Year 2026' is: LIFE / LITE)
        if not ref:
            continue
        v = scaled(num(m.group(1)), m.group(2), ref)
        old1 = same(v, m.group(1), m.group(2), yago)
        n2 = NEXT.match(text, m.end())
        v2 = scaled(num(n2.group(1)), n2.group(2) or m.group(2), ref) if n2 else None
        row, p = [], m.end()                            # the row's next figures ('$ 13,377 $ 11,536 $ 9,246 $ 35,166')
        for _ in range(4):
            nx = ROWNUM.match(text, p)
            if not nx:
                break
            row.append(nx); p = nx.end()
        later_old = any(same(scaled(num(x.group(1)), x.group(2) or m.group(2), ref), x.group(1), x.group(2) or m.group(2), yago)
                        for x in row)
        if v2 is not None and 0.6 <= v2 / ref <= (1.7 if est else 4):
            old2 = same(v2, n2.group(1), n2.group(2) or m.group(2), yago)
            if old1 and not old2:
                v = v2                                  # the first figure is last year's quarter
            elif not old1 and later_old:
                pass                                    # last year's is further along the row: the first is this quarter
                                                        # (AMD: Q3'26 $13,377 | Q2'26 $11,536 | Q3'25 $9,246)
            elif not old1 and not old2:
                hd = [y for y in YEARS.finditer(text[max(0, m.start() - 1500): m.start()])]
                if hd and int(hd[-1].group(2)) > int(hd[-1].group(1)):
                    v = v2                              # the header puts last year first
        elif old1:
            continue                                    # last year's figure alone ('compared to $271.7 million')
        if 0.6 <= v / ref <= (1.7 if est else 4):
            return v
    return None


def rev_growth_from(text):
    """'revenue grew 32% year-over-year' in the release's first part (before the outlook): the quarter's growth"""
    head = text[:8000]
    cut = re.search(r"\b(outlook|guidance)\b", head[1500:], re.I)
    if cut:
        head = head[:1500 + cut.start()]
    m = re.search(r"\b(?:total )?revenues?\b[^.;$]{0,40}?\b(?:grew|increased|rose|was up|up)\b\s*(?:by\s*)?(\d+(?:\.\d+)?)\s*%", head, re.I)
    return float(m.group(1)) if m else None


def eps_from(text, est):
    """the adjusted (non-GAAP) EPS in the release, checked against the estimate"""
    head = text[:15000]
    for m in re.finditer(r"(?:non-gaap|adjusted)(?:[^.;]|\.(?=\d)){0,140}?(?:\$\s?(\(?-?\d+\.\d{2}\)?)\s+per (?:diluted )?share|(?:eps|earnings per (?:diluted )?share|net income per (?:diluted )?share)\b[^.;$]{0,40}?\(?\$\s?(\(?-?\d+\.\d{2}\)?))", head, re.I):
        v = num(m.group(1) or m.group(2))
        if v is None:
            continue
        if est is None or abs(v - est) <= max(abs(est) * 1.5, 0.3):
            return v
    return None


WORDS = {"single-digit": 5, "single digit": 5, "teens": 15, "twenties": 25, "thirties": 35, "forties": 45, "fifties": 55,
         "sixties": 65, "seventies": 75}
LEVEL = {"low": -3, "mid": 0, "high": 3}


def guidance(text, nq, fy):
    """the outlook: direction (raised / lowered / reaffirmed / given / none) and, when a revenue number is there, its
    midpoint vs the street and vs the same period a year ago. nq / fy = the saved estimates {rev, rev_yago, end}."""
    head = text[:2500]
    # the outlook section: the first 'outlook' / 'guidance' (or 'we expect') with an expectation about revenue right after it
    anchors = []
    for m in re.finditer(r"\b(business outlook|financial outlook|outlook|guidance|we expect|the company expects|company expects|"
                         r"estimates the following|for the (?:fourth|first|second|third) quarter of 20\d\d)\b", text[1500:], re.I):
        nxt = text[1500 + m.start(): 1500 + m.start() + 900]
        if re.search(r"\bexpect|\banticipat|\bguid|\bproject|\bforecast|\bestimat|\boutlook", nxt, re.I) and re.search(r"revenue|sales", nxt, re.I):
            if not anchors or m.start() - anchors[-1].start() > 600:
                anchors.append(m)
        if len(anchors) >= 6:
            break
    m0 = None                                       # the words (raised / lowered ...): the first outlook section, as before
    for m in re.finditer(r"\b(business outlook|financial outlook|outlook|guidance|we expect|the company expects|company expects)\b", text[1500:], re.I):
        nxt = text[1500 + m.start(): 1500 + m.start() + 900]
        if re.search(r"\bexpect|\banticipat|\bguid|\bproject|\bforecast", nxt, re.I) and re.search(r"revenue|sales", nxt, re.I):
            m0 = m
            break
    body = text[1500 + m0.start(): 1500 + m0.start() + 3500] if m0 else ""
    # the number: that section first, then the later ones (ALAB / RAL Nov 2026: '$730 million to $750 million' further down)
    bodies = ([body] if body else []) + [text[1500 + a.start(): 1500 + a.start() + 3500] for a in anchors
                                         if not m0 or abs(a.start() - m0.start()) > 600]
    scan = head + " " + body
    g = {"dir": "none"}
    up = re.search(r"\b(rais(?:e|es|ed|ing)|increas(?:e|es|ed|ing)|boost(?:s|ed)?|lift(?:s|ed)?|upgrad\w*)\b[^.;]{0,90}?\b(guidance|outlook|forecast|expectations)\b"
                   r"|\b(guidance|outlook)\b[^.;]{0,25}\b(raised|increased)\b", scan, re.I)
    dn = re.search(r"\b(lower(?:s|ed|ing)?|reduc(?:e|es|ed|ing)|cut(?:s|ting)?|downgrad\w*|withdr[ae]w\w*)\b[^.;]{0,90}?\b(guidance|outlook|forecast)\b"
                   r"|\b(guidance|outlook)\b[^.;]{0,25}\b(lowered|reduced|cut|withdrawn)\b", scan, re.I)
    keep = re.search(r"\b(reaffirm\w*|reiterat\w*|maintain\w*|confirm\w*)\b[^.;]{0,90}?\b(guidance|outlook|forecast)\b", scan, re.I)
    if up and dn:
        g["dir"] = "mixed"
    elif up:
        g["dir"] = "raised"
    elif dn:
        g["dir"] = "lowered"
    elif keep:
        g["dir"] = "reaffirmed"
    elif m0 and re.search(r"\bexpect\w*\b", body, re.I) and re.search(r"revenue|sales", body, re.I):
        g["dir"] = "given"
    hit = up or dn or keep
    if hit:
        s = scan[max(0, hit.start() - 60): hit.end() + 140]
        g["text"] = s.strip()
    # a revenue number in the outlook: a $ range, a single $ figure, or a growth rate
    best = best_prod = None
    # a $ figure in any outlook section first, then a growth rate (ALAB: the $730-750 million is in the second section)
    for phase, body in [("$", b) for b in bodies] + [("%", b) for b in bodies]:
        for unitless in ((False, True) if phase == "$" else ()):   # sentences with units first; then tables under '(in millions)'
            for m in re.finditer(r"\b(?:revenues?|sales|net sales)\b[^.;$%]{0,80}?" + MONEY + RANGE2, body, re.I):
                a = num(m.group(1))
                ua = (m.group(2) or m.group(4) or "").lower()
                b = num(m.group(3)) if m.group(3) else None
                ub = (m.group(4) or ua).lower()
                if a is None or bool(ua or ub) == unitless:
                    continue
                hdr = body[max(0, m.start() - 300): m.start()]
                p_old = re.search(r"\b(previous|prior)\b", hdr, re.I)
                p_new = re.search(r"\b(raised|updated|revised|new|current|lowered|reduced)\b", hdr, re.I)
                if p_old and p_new and p_old.start() < p_new.start():
                    n2 = re.compile(r"\s*\$\s?(\d[\d,]*(?:\.\d+)?)" + RANGE2).match(body, m.end())
                    if not n2:                          # 'Previous | Raised' columns: the second one (SOLS Nov 4 2026)
                        continue
                    a, b = num(n2.group(1)), num(n2.group(2)) if n2.group(2) else None
                if b is not None and not (a and 0.5 <= b / a <= 2):
                    b = None                            # not a range ('$300 million to 2027')
                if unitless:                            # a table without units: its '(in millions)' marker (DUOL Nov 3 2026)
                    mk = list(re.finditer(r"\bin (thousands|millions|billions)\b", body[:m.start()], re.I))
                    if not mk or m.start() - mk[-1].end() > 600:
                        continue
                    ua = ub = {"thousands": "thousand", "millions": "million", "billions": "billion"}[mk[-1].group(1).lower()]
                ctx = body[max(0, m.start() - 160): m.end()].lower()
                if re.search(r"\b(was|were|totaled|grew|increased|decreased|declined|reported|achieved)\b",
                             m.group(0).lower().replace("(reported)", "")) \
                        or not re.search(r"expect|anticipat|guid|outlook|forecast|project|to be|will be|range|between|approximately", ctx):
                    continue                              # a result or a company profile, not a forecast
                if not b and re.match(r"\s*\$?\s?\d[\d,]*(?:\.\d+)?\s*\(?-?\d+(?:\.\d+)?\s*\)?\s*%", body[m.end():m.end() + 30]):
                    continue                              # a results row: this year, last year, change % (EL Nov 2026)
                lo, hi = a * UNIT.get(ua or ub, 1), (b * UNIT.get(ub, 1) if b else a * UNIT.get(ua or ub, 1))
                mid = (lo + hi) / 2
                near = []
                for kind, e in (("q", nq), ("fy", fy)):
                    if e and e.get("rev") and 0.7 <= mid / e["rev"] <= 1.45:
                        near.append((abs(mid / e["rev"] - 1), kind, e))
                prior = prior_mid(body, m, a, b, ua or ub, prev_first=bool(p_old and p_new and p_old.start() < p_new.start()))
                prod = product_of(body[max(0, m.start() - 120): m.end() + 20])
                if prod:                                # one product's guide (URGN: JELMYTO ~$90M): shown, not vs the street
                    if not best_prod:
                        best_prod = {"kind": "product", "product": prod, "lo": lo, "hi": hi, "mid": mid, "prior_mid": prior,
                                     "said": body[max(0, m.start() - 40): m.end() + 10].strip()}
                    continue
                if near:
                    _, kind, e = min(near)
                    best = {"kind": kind, "lo": lo, "hi": hi, "mid": mid, "vs_street": pct(mid, e["rev"]),
                            "growth": pct(mid, e.get("rev_yago")), "period_end": e.get("end"), "prior_mid": prior,
                            "said": body[max(0, m.start() - 40): m.end() + 10].strip(),
                            "near_words": body[max(0, m.start() - 200): m.start() + 20]}
                    break
            if best:
                break
        if phase == "%" and not best:
            best = best_prod
        if not best and phase == "%":
            m = None
            for mm in re.finditer(r"\b(?:total )?(?:revenues?|sales)\b[^.;]{0,30}?\b(?:to )?grow\w*\b[^.;]{0,50}?(?:(\d+(?:\.\d+)?)\s*%(?:\s*(?:to|-|–)\s*(\d+(?:\.\d+)?)\s*%)?"
                                  r"|\b(low|mid|high)[- ](single[- ]digit|teens|twenties|thirties|forties|fifties|sixties|seventies)\b)", body, re.I):
                pre = body[max(0, mm.start() - 200): mm.start()].lower()
                if re.search(r"from (new )?products|segment|new product", body[mm.start(): mm.start() + 40].lower()):
                    continue                              # a product line's growth, not the company's
                if re.search(r"expect|anticipat|guid|outlook|forecast|project", pre + mm.group(0).lower()) and not re.search(r"\bgrew\b", mm.group(0).lower()):
                    m = mm
                    break
            if m:
                if m.group(1):
                    gr = (float(m.group(1)) + float(m.group(2) or m.group(1))) / 2
                else:
                    gr = WORDS[m.group(4).lower().replace(" ", "-")] + LEVEL[m.group(3).lower()]
                ctx = body[max(0, m.start() - 300): m.start()].lower()
                kind = "fy" if re.search(r"full[- ]year|fiscal (year )?20\d\d|for (the )?(year|20\d\d)\b|annual", ctx) and not re.search(r"quarter", ctx[-120:]) else "q"
                e = nq if kind == "q" else fy
                mid = e["rev_yago"] * (1 + gr / 100) if e and e.get("rev_yago") else None
                best = {"kind": kind, "growth": round(gr, 1), "mid": mid, "vs_street": pct(mid, e.get("rev")) if e and mid else None,
                        "period_end": e.get("end") if e else None, "said": body[max(0, m.start() - 40): m.end() + 10].strip()}
        if best:
            break
    if best:
        nw = best.pop("near_words", "") if isinstance(best, dict) else ""
        g.update(best)
        if g["dir"] in ("none", "given") and nw:
            if re.search(r"\b(rais(?:e|es|ed|ing)|increas(?:e|es|ed|ing))\b[^.;]{0,60}?\b(guidance|outlook)\b", nw, re.I):
                g["dir"] = "raised"
            elif re.search(r"\b(lower(?:s|ed|ing)?|reduc(?:e|es|ed|ing)|cut(?:s)?)\b[^.;]{0,60}?\b(guidance|outlook)\b", nw, re.I):
                g["dir"] = "lowered"
        if g["dir"] == "none":
            g["dir"] = "given"
        pm = best.get("prior_mid")
        if pm and best.get("mid"):
            by = "raised" if best["mid"] > pm * 1.002 else "lowered" if best["mid"] < pm * 0.998 else "reaffirmed"
            g["by_numbers"] = by            # the new vs the prior range beats the words (ADEA Nov 2 2026: $375-415M
            words = g["dir"]                # vs $395-435M read 'reaffirmed' from 'reiterate ... long-term outlook')
            if best.get("product") or words in ("given", "reaffirmed", "none") or words == by:
                g["dir"] = by
            elif by != "reaffirmed":        # the words say raised and the revenue numbers lowered, or the reverse
                g["dir"] = "mixed"
    return g


def prior_mid(body, m, a, b, unit, prev_first=False):
    """the prior guidance for the same line, when the release shows it: the other column of an 'Updated | Prior'
    table (ADEA), the first column of a 'Previous | Raised' table (SOLS), or '... compared with its prior guidance
    (range) of $97 million to $101 million' (URGN)"""
    sc = UNIT.get(unit, 1)
    fig = r"\$?\s?(\d[\d,]*(?:\.\d+)?)\s*(?:million|billion|bn|mm|m|b)?\b"
    rng = fig + r"(?:\s*(?:to|-|–|—|−)\s*" + fig + ")?"
    if prev_first:                                  # the first figure of the row is the previous guide
        m1 = re.compile(r"\$\s?(\d[\d,]*(?:\.\d+)?)" + RANGE2).search(body, m.start())
        if m1:
            x, y = num(m1.group(1)), num(m1.group(2)) if m1.group(2) else None
            return (x + (y or x)) / 2 * sc if x else None
        return None
    hdr = body[max(0, m.start() - 300): m.start()]
    if re.search(r"\b(updated|revised|new|current|raised|lowered)\b[^$]{0,60}\b(prior|previous)\b", hdr, re.I) \
            or re.search(r"\bas of \d{1,2}/\d{1,2}/\d{2,4}\s+as of \d{1,2}/\d{1,2}/\d{2,4}", hdr, re.I):   # 'As of 11/3 | As of 8/6' (QDEL)
        m2 = re.compile(r"\s*\$\s?" + rng).match(body, m.end())       # the next column of the row
        if m2:
            x, y = num(m2.group(1)), num(m2.group(2)) if m2.group(2) else None
            if x and 0.5 <= x / a <= 2:
                return (x + (y or x)) / 2 * sc
    m3 = re.compile(r"[^.;]{0,80}?\b(?:prior|previous|previously)\b[^$.;]{0,60}?\$\s?" + rng, re.I).match(body, m.end())
    if m3:
        x, y = num(m3.group(1)), num(m3.group(2)) if m3.group(2) else None
        u = re.search(r"\b(million|billion)\b", m3.group(0), re.I)
        s2 = UNIT.get(u.group(1).lower(), sc) if u else sc
        if x and 0.5 <= x * s2 / (a * sc) <= 2:
            return (x + (y or x)) / 2 * s2
    return None


NOT_PRODUCT = {"GAAP", "NYSE", "NASDAQ", "EBITDA", "FY", "USD", "ARR", "SAAS"}


def product_of(s):
    """'net product revenue guidance for JELMYTO' -> 'JELMYTO': a guide for one product (a brand in capitals)"""
    m = re.search(r"\b(?:revenues?|sales)\b[^.;$]{0,40}?\b(?:for|of)\s+([A-Z][A-Z0-9]{3,})\b", s)
    return m.group(1) if m and m.group(1) not in NOT_PRODUCT else None


# ───────── the read ─────────
READS = [(6, "Strong bullish"), (3, "Bullish"), (0, "Mixed"), (-3, "Somewhat bearish"), (-99, "Bearish")]


def score(r):
    """points: revenue surprise ±1/2, EPS surprise ±1/2, guidance (raised +2, above the street +1 more / +2 alone,
    lowered -3, below the street -2; one product's guide raised +1 / lowered -1), revenue growth 25%+ +1 / shrinking -1, the move after the report ±1/2.
    6+ Strong bullish, 3-5 Bullish, 0-2 Mixed, -1 to -3 Somewhat bearish, -4 or less Bearish."""
    pts, why = 0, []
    rs = r.get("rev_surprise")
    if rs is not None:
        p = 2 if rs >= 2 else 1 if rs > 0 else -2 if rs <= -2 else -1 if rs < 0 else 0
        pts += p; why.append(f"revenue {'beat' if rs > 0 else 'miss' if rs < 0 else 'in line'} {rs:+.1f}%")
    es = r.get("eps_surprise")
    if es is not None:
        p = 2 if es >= 10 else 1 if es > 0 else -2 if es <= -10 else -1 if es < 0 else 0
        pts += p; why.append(f"EPS {'beat' if es > 0 else 'miss' if es < 0 else 'in line'} {es:+.1f}%")
    g = r.get("guide") or {}
    d, vs = g.get("dir"), g.get("vs_street")
    if g.get("kind") == "product":               # one product's guide (URGN Nov 4 2026, JELMYTO): +1 / -1
        if d in ("raised", "lowered"):
            pts += 1 if d == "raised" else -1; why.append(f"{g.get('product')} guide {d}")
    elif d == "raised":
        pts += 2; why.append("guidance raised")
    elif d == "lowered":
        pts -= 3; why.append("guidance lowered")
    elif d == "mixed":
        why.append("guidance raised and lowered")
    elif d == "reaffirmed":
        why.append("guidance reaffirmed")
    if vs is not None:
        if vs >= 1:
            pts += 1 if d == "raised" else 2; why.append(f"guide {vs:+.1f}% vs street")
        elif vs <= -1:
            pts -= 2; why.append(f"guide {vs:+.1f}% vs street")
    gr = r.get("rev_growth")
    if gr is not None:
        if gr >= 25:
            pts += 1; why.append(f"revenue +{gr:.0f}% y/y")
        elif gr < 0:
            pts -= 1; why.append(f"revenue {gr:.0f}% y/y")
    mv = r.get("move") if r.get("move_after") else None
    if mv is not None:
        p = 2 if mv >= 5 else 1 if mv >= 2 else -2 if mv <= -5 else -1 if mv <= -2 else 0
        pts += p; why.append(f"{mv:+.1f}% {r.get('move_kind') or ''}".strip())
    if not why:
        return None, None, None
    return next(n for lim, n in READS if pts >= lim), pts, ", ".join(why)


# ───────── the build ─────────
def main():
    stocks_p, prev_p, out_p = sys.argv[1], sys.argv[2], sys.argv[3]
    now = datetime.datetime.now(NY)
    today = now.date().isoformat()
    days = week_days(now)
    t0, p1, p2 = reaction_days(now)
    extra = sorted({p1, p2} - set(days))            # last week's days the reaction views need (on a Monday / Tuesday)
    S = {s["symbol"]: s for s in json.load(open(stocks_p))}
    prev = {}
    if prev_p and os.path.exists(prev_p):
        try:
            pj = json.load(open(prev_p))
            if pj.get("days") == days:
                prev = {r["sym"]: r for r in pj.get("rows", [])}
        except Exception:
            prev = {}
    errors = []

    # 1. the week's calendar, your rules
    cal = {}
    for d in extra + days:
        try:
            for x in nasdaq(d):
                sym = (x.get("symbol") or "").upper()
                if sym:
                    cal[sym] = (d, x)
        except Exception as e:
            errors.append(f"nasdaq {d}: {e!r}"[:200])
        time.sleep(0.4)
    rows = {}
    for sym, (d, x) in cal.items():
        s = S.get(sym)
        if not s:
            continue
        if sym not in prev and not passes(s):
            continue
        r = dict(prev.get(sym) or {})
        r.update(sym=sym, name=s.get("name") or x.get("name"), date=d, fq=x.get("fiscalQuarterEnding"),
                 nasdaq_when={"time-pre-market": "bmo", "time-after-hours": "amc"}.get(x.get("time")),
                 nasdaq_eps_est=num(x.get("epsForecast")), nasdaq_eps=num(x.get("eps")), industry=s.get("industry"),
                 nasdaq_eps_yago=num(x.get("lastYearEPS")) if x.get("lastYearEPS") else (prev.get(sym) or {}).get("nasdaq_eps_yago"),
                 themes=s.get("themes") or "", mcap_b=s.get("mcap_b"), adr=s.get("adr_20"), dvol_20_m=s.get("dvol_20_m"),
                 avg_vol_20=s.get("avg_vol_20"), close=s.get("price"), sma200=s.get("sma200"), ema50=s.get("ema50"),
                 low_52w=s.get("low_52w"), high_52w=s.get("high_52w"))
        rows[sym] = r
    for sym, r in prev.items():                      # a date that moved out of the week drops the row
        if sym not in rows and r.get("reported"):
            rows[sym] = r                            # but a report already in stays for the week
    syms = sorted(rows)
    print(len(cal), "on the calendar,", len(syms), "pass your rules")

    y = Y()
    # 2. quotes: report time, prices
    try:
        Q = y.quotes([s.replace(".", "-") for s in syms])
    except Exception as e:
        Q = {}; errors.append(f"yahoo quotes: {e!r}"[:200])
    for sym in syms:
        r, q = rows[sym], Q.get(sym.replace(".", "-")) or {}
        ts = q.get("earningsTimestamp")
        if ts:
            t = datetime.datetime.fromtimestamp(ts, NY)
            if t.date().isoformat() == r["date"] and not (t.hour == 0 and t.minute == 0):
                r["when"] = "bmo" if t.hour < 12 else "amc" if t.hour >= 15 else "dmh"
                r["time"] = t.strftime("%H:%M")
        r["when"] = r.get("nasdaq_when") or r.get("when") or "tns"
        # the report's moment: before the open = that morning; after the close = that evening
        r["report_at"] = r["date"] + ("T07:00" if r["when"] == "bmo" else "T16:00" if r["when"] == "amc" else "T12:00")
        st = q.get("marketState") or ""
        reg, prv = q.get("regularMarketPrice"), q.get("regularMarketPreviousClose")
        pre, post = q.get("preMarketPrice"), q.get("postMarketPrice")
        pre_t, post_t = q.get("preMarketTime") or 0, q.get("postMarketTime") or 0
        reg_t = q.get("regularMarketTime") or 0
        px = kind = ref = None
        if st == "PRE" or (st in ("PREPRE", "CLOSED") and pre and pre_t > reg_t and now.hour < 10):
            px, kind, ref = pre, "pre-market", reg
        elif st == "REGULAR":
            px, kind, ref = reg, "live", prv
        elif post and post_t > reg_t:
            px, kind, ref = post, "after hours", reg
        else:
            px, kind, ref = reg, "close", prv
        if px:
            r.update(px=round(px, 4), px_kind=kind, px_time=datetime.datetime.fromtimestamp(
                {"pre-market": pre_t, "after hours": post_t}.get(kind, reg_t) or reg_t, NY).strftime("%H:%M"),
                move=pct(px, ref) if ref else None)
            r["vs200"] = pct(px, r["sma200"]) if r.get("sma200") else None
            r["vs50"] = pct(px, r["ema50"]) if r.get("ema50") else None
            r["over_low52"] = pct(px, r["low_52w"]) if r.get("low_52w") else None
        # is the move the reaction to the report? (after hours on its evening, the next pre-market / session)
        r["move_after"] = bool(px and now.isoformat() >= r["report_at"] and (
            (r["when"] == "bmo" and r["date"] == today) or
            (r["when"] == "amc" and ((r["date"] == today and kind == "after hours") or (r["date"] < today and r.get("react_day") in (None, today))))
            or (r["when"] in ("dmh", "tns") and r["date"] <= today and r.get("reported"))))
        if r["when"] == "amc" and r["date"] < today and not r.get("react_day"):
            r["react_day"] = today
        if r["move_after"]:
            r["react_move"], r["react_kind"] = r.get("move"), kind
        r["move_kind"] = kind

    # 3. the 20-day high, the estimates (frozen at the report), EPS actual
    def per(sym):
        r = rows[sym]
        ysym = sym.replace(".", "-")
        try:
            if r.get("high20_day") != today:
                r["high20"], r["high20_day"] = y.high20(ysym, today), today
        except Exception as e:
            errors.append(f"bars {sym}: {e!r}"[:160])
        if r.get("px") and r.get("high20"):
            r["vs20h"] = pct(r["px"], r["high20"])
        try:
            hist, trend = y.summary(ysym)
        except Exception as e:
            errors.append(f"summary {sym}: {e!r}"[:160]); return
        qe = q_end(r.get("fq"))
        t0 = trend.get("0q") or {}
        if not r.get("est_frozen"):
            if qe and near(ym(t0.get("end")), qe):           # Yahoo still on the quarter being reported
                r.update(eps_est=t0.get("eps"), eps_yago=t0.get("eps_yago"), rev_est=t0.get("rev"), rev_yago=t0.get("rev_yago"),
                         nq=trend.get("+1q"), fy=trend.get("0y"), est_from="before the report")
            elif qe:                                     # already moved on: the report is out, estimates from history
                h = pick(hist, qe) or {}
                r.update(eps_est=h.get("est") or r.get("nasdaq_eps_est"), nq=t0, fy=trend.get("0y"),
                         est_from="after the report (Yahoo had moved on)")
                yago = (qe[0] - 1, qe[1])
                hy = pick(hist, yago)
                r["eps_yago"] = hy.get("act") if hy else r.get("eps_yago")
                if r.get("rev_yago") is None:
                    try:
                        r["rev_yago"] = pick(y.revenue_ts(ysym), yago)
                    except Exception:
                        pass
        h = pick(hist, qe)
        if h and h.get("est") is not None and (r.get("eps_est_src") or "").startswith("Nasdaq"):
            r["eps_est"] = h["est"]; r.pop("eps_est_src", None)     # undo the old swap: Yahoo's estimate back
        # last quarter (q/q): Yahoo's EPS (the same basis as the actual) and revenue, and last quarter's own y/y
        pq = qshift(qe, -1) if qe else None
        hp = pick(hist, pq) if pq else None
        if hp and hp.get("act") is not None:
            r["eps_prev"] = hp["act"]
        if pq and r.get("rev_prev") is None:
            try:
                ts = y.revenue_ts(ysym)
                r["rev_prev"], r["rev_prev_yago"] = pick(ts, pq), pick(ts, qshift(qe, -5))
            except Exception as e:
                errors.append(f"revenue history {sym}: {e!r}"[:160])
        if h and h.get("act") is not None and now.isoformat() >= r["report_at"]:
            r["eps_act"], r["eps_src"] = h["act"], "Yahoo"
            if h.get("est") is not None and r.get("eps_est") is None:
                r["eps_est"] = h["est"]
        elif r.get("rel_eps") is not None:
            r["eps_act"], r["eps_src"] = r["rel_eps"], "press release"
        elif r.get("nasdaq_eps") is not None and now.isoformat() >= r["report_at"]:
            r["eps_act"], r["eps_src"] = r["nasdaq_eps"], "Nasdaq"
        if (r.get("reported") or r.get("eps_act") is not None) and r.get("rev_act") is None and qe:
            try:
                rv = pick(y.revenue_ts(ysym), qe)
                if rv:
                    r["rev_act"], r["rev_src"] = rv, "Yahoo"
            except Exception:
                pass
    with cf.ThreadPoolExecutor(6) as ex:
        list(ex.map(per, syms))

    # 4. the press release (results out?)
    sec = SEC()
    for sym in syms:
        r = rows[sym]
        if now.isoformat() < r["report_at"][:10] + "T00:00" or (r.get("rel_url") and r.get("gv") == GV):
            continue
        since = (datetime.date.fromisoformat(r["date"]) - datetime.timedelta(days=1)).isoformat()
        try:
            rel = sec.release(sym, since)
        except Exception as e:
            errors.append(f"sec {sym}: {e!r}"[:160]); rel = None
        time.sleep(0.15)
        if not rel:
            continue
        r.update(rel_url=rel["url"], rel_filed=rel["filed"], reported=True, est_frozen=True, gv=GV)
        rv = rev_from(rel["text"], r.get("rev_est"), r.get("rev_yago"))
        if rv:
            r["rev_act"], r["rev_src"] = rv, "press release"
        elif r.get("rev_yago") and r.get("rev_src") != "Yahoo":
            gr = rev_growth_from(rel["text"])
            if gr is not None:
                r["rev_act"], r["rev_src"] = r["rev_yago"] * (1 + gr / 100), f"press release (≈ from its {gr:g}% growth)"
        ep = eps_from(rel["text"], r.get("eps_est"))
        if ep is not None:
            r["rel_eps"] = ep
        if r.get("eps_src") != "Yahoo" and r.get("rel_eps") is not None:
            r["eps_act"], r["eps_src"] = r["rel_eps"], "press release"
        r["guide"] = guidance(rel["text"], r.get("nq"), r.get("fy"))
        r["headline"] = rel["text"][:400]
    for sym in syms:
        r = rows[sym]
        # Yahoo's estimate stays paired with Yahoo's actual (the same adjusted basis). The old swap to Nasdaq's estimate
        # when the two were 3x apart (MPC Nov 3 2026: Yahoo 26.00 vs Nasdaq 3.01; MPC reported 26.93: Yahoo was right)
        # set Nasdaq's estimate against Yahoo's actual: FRSH +1000%, PCOR +264%, LIFE +390% (Nov 2026).
        if r.get("eps_act") is not None and now.isoformat() >= r["report_at"]:
            r["reported"], r["est_frozen"] = True, True
        r["eps_surprise"] = (round((r["eps_act"] - r["eps_est"]) / abs(r["eps_est"]) * 100, 1)
                             if r.get("eps_act") is not None and r.get("eps_est") not in (None, 0) else None)
        if r["eps_surprise"] is not None and r["eps_act"] and (abs(r["eps_est"]) > 3 * abs(r["eps_act"]) or abs(r["eps_act"]) > 3 * abs(r["eps_est"])) \
                and abs(r["eps_act"] - r["eps_est"]) > 0.5:
            r["eps_surprise"], r["eps_est_odd"] = None, True      # 3x+ apart: a bad estimate or a one-off, no surprise scored (MPC)
        if r.get("eps_yago") is None and r.get("nasdaq_eps_yago") is not None:
            r["eps_yago"] = r["nasdaq_eps_yago"]
        r["eps_growth"] = pct(r.get("eps_act"), r.get("eps_yago")) if r.get("eps_act") is not None else None
        if r["eps_growth"] is not None and abs(r["eps_yago"]) < 0.05:
            r["eps_growth"], r["eps_nm"] = None, True        # a year-ago EPS under 5 cents: % is meaningless (AEHR 0.01 -> 0.28)
        r["eps_qoq"] = pct(r.get("eps_act"), r.get("eps_prev")) if r.get("eps_src") in ("Yahoo", "press release") else None
        if r["eps_qoq"] is not None and abs(r["eps_prev"]) < 0.05:
            r["eps_qoq"] = None
        r["rev_qoq"] = pct(r.get("rev_act"), r.get("rev_prev"))
        r["rev_prev_growth"] = pct(r.get("rev_prev"), r.get("rev_prev_yago"))   # last quarter's y/y: speeding up or slowing
        r["eps_turn"] = bool(r.get("eps_act") is not None and r.get("eps_yago") is not None and r["eps_yago"] <= 0 < r["eps_act"])
        r["rev_surprise"] = pct(r.get("rev_act"), r.get("rev_est"))
        r["rev_growth"] = pct(r.get("rev_act"), r.get("rev_yago"))
        rr = dict(r, move=r.get("react_move"), move_after=r.get("react_move") is not None, move_kind=r.get("react_kind"))
        r["read"], r["points"], r["why"] = score(rr) if r.get("reported") else (None, None, None)

    out = {"built_at": now.isoformat(timespec="seconds"), "days": days, "today": today, "rules": RULES,
           "react": {"t0": t0, "p1": p1, "p2": p2}, "extra_days": extra,
           "n_calendar": len(cal), "rows": [rows[s] for s in syms], "errors": errors[:40]}
    json.dump(out, open(out_p, "w"), separators=(",", ":"), default=str)
    print(len(syms), "rows,", sum(1 for s in syms if rows[s].get("reported")), "reported,", len(errors), "errors")


if __name__ == "__main__":
    main()
