#!/usr/bin/env python3
"""The code grader for pre-market gappers (no Claude): the news from the SEC, the chart from the averages.

  python3 radar/codegrade.py live <premarket.json> <stocks.json> <earnings.json> <out.json> [--asof=YYYY-MM-DDTHH:MM]

Built Nov 4 2026 with the user, as a second grade next to Claude's for 1-2 weeks (Claude's stays the official one).
Two layers, then one combined grade:

  NEWS  (the user's A / B / C / F definitions, made measurable; filings accepted since the last close at 4 PM ET up
        to the grading time, so nothing after the open counts)
        gap-ups   F  an offering / ATM / shelf takedown (424B, S-1, S-3, F-1, F-3, 8-K 3.02), a delisting notice (3.01),
                     a reverse split, going concern
                  A  earnings: beat (or no estimate) + guidance raised or above the street + revenue growth 20%+ or
                     3+ points faster than last quarter; a signed takeover of the company; an FDA approval;
                     a signed contract worth 25%+ of the market cap
                  B  earnings: a modest beat-and-raise, a turnaround (last quarter shrinking, this one growing),
                     growth 15%+ with a beat; positive trial data; a contract worth 5-25%
                  C  no filing since the close (sector / macro / analyst / sympathy), mixed earnings, anything the code
                     can't classify, buying a company (the acquirer)
        gap-downs A  guidance cut / withdrawn, a big miss with a weak guide, a failed trial, a CRL, a CEO / CFO out
                     effective immediately
                  B  a modest miss, a guide under the street, shrinking revenue, an offering
                  C  no filing, a good report sold off
  CHART (the user, Nov 4 2026: "we are market players": a stock under its 200 SMA gets shorted; the gap that matters
        takes the pre-market price over the 50 and the 200 and over the 21-day high: shorts caught off guard)
        turnup    was under the 50 EMA or the 200 SMA at the last close, the pre-market price over both and over the
                  21-day high
        trending  21 EMA > 50 EMA > 200 SMA at the last close and the price over all three
        mixed     over the 200, not stacked or under the 50
        laggard   over the 50 EMA, under the 200 SMA, over the 21-day high (the Launch laggards case: all but the 200)
        downtrend over the 50 EMA, under the 200 SMA and the 21-day high
        under50_200  under both the 50 EMA and the 200 SMA: a gap-up qualifies for nothing ("—"; the user, Nov 4 2026)
  GRADE (gap-ups) over the 200: news A: turnup A+, trending A, mixed B; news B: turnup A, trending B, mixed C;
        news C stays C; F stays F. Under the 200 the trend isn't confirmed (the user, Nov 4 2026): only W (laggard watch:
        A / B news, over the 50 and the 21-day high), everything else "—", not qualified. (a turnup without news is
        flagged); F stays F; under 30% over the 52-week low (pre-market price) qualifies for nothing ("—"; the pre-market
        list drops these before grading). Gap-downs: the news grade, one
        grade more serious (B -> A) when a trending stock gaps under its 50 and 200.
"""
import datetime, html, json, os, re, sys, time, urllib.request, zoneinfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

NY = zoneinfo.ZoneInfo("America/New_York")
SEC_UA = (os.environ.get("SEC_UA") or "").strip() or "radar-close-snapshots research"
OFFER_FORMS = ("424B1", "424B2", "424B3", "424B4", "424B5", "424B7", "S-1", "S-3", "F-1", "F-3", "S-1MEF", "S-3MEF")


# ───────── SEC ─────────
_last = [0.0]


def sec_get(url, raw=False):
    """the SEC asks for at most 10 requests a second and a contact in the User-Agent"""
    wait = 0.12 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    for k in range(3):
        try:
            _last[0] = time.time()
            rq = urllib.request.Request(url, headers={"User-Agent": SEC_UA, "Accept": "application/json, text/html, */*"})
            with urllib.request.urlopen(rq, timeout=30) as r:
                b = r.read()
            return b if raw else json.loads(b)
        except Exception:
            if k == 2:
                raise
            time.sleep(1.5 * (k + 1))


_cik = {}


def cik_of(sym):
    if not _cik:
        t = sec_get("https://www.sec.gov/files/company_tickers.json")
        _cik.update({v["ticker"].upper(): int(v["cik_str"]) for v in t.values()})
    s = sym.upper()
    return _cik.get(s) or _cik.get(s.replace(".", "-")) or _cik.get(s.replace("-", "."))


_subs = {}


def filings(sym, t_from, t_to):
    """the company's filings accepted in (t_from, t_to] (aware datetimes): [{form, items, at, base, primary}]"""
    c = cik_of(sym)
    if not c:
        return None
    if c not in _subs:
        sub = sec_get(f"https://data.sec.gov/submissions/CIK{c:010d}.json")
        rows = []

        def add(f):
            for i, form in enumerate(f["form"]):
                rows.append({"form": form, "items": f.get("items", [""] * len(f["form"]))[i] or "",
                             "at": f["acceptanceDateTime"][i], "acc": f["accessionNumber"][i], "primary": f["primaryDocument"][i]})
        add(sub["filings"]["recent"])
        for extra in sub["filings"].get("files", []):          # older pages, for the backtest's early months
            if extra.get("filingTo", "9999") >= "2024-06-01":
                try:
                    add(sec_get("https://data.sec.gov/submissions/" + extra["name"]))
                except Exception:
                    pass
        _subs[c] = rows
    out = []
    for f in _subs[c]:
        try:
            at = datetime.datetime.fromisoformat(f["at"].replace("Z", "+00:00")).astimezone(NY)
        except ValueError:
            continue
        if t_from < at <= t_to:
            out.append(dict(f, at=at, base=f"https://www.sec.gov/Archives/edgar/data/{c}/{f['acc'].replace('-', '')}/"))
    return sorted(out, key=lambda f: f["at"])


def clean(raw):
    txt = re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style).*?</\1>", " ", raw))
    return re.sub(r"\s+", " ", html.unescape(txt)).strip()


def release_text(f):
    """an 8-K / 6-K's press release (exhibit 99), else its main document: (url, text)"""
    try:
        docs = [d["name"] for d in sec_get(f["base"] + "index.json")["directory"]["item"]]
    except Exception:
        docs = [f["primary"]]
    htm = [d for d in docs if d.lower().endswith((".htm", ".html", ".txt")) and "index" not in d.lower()]
    ex = [d for d in htm if re.search(r"ex[-_]?99|exh?99|exhibit[-_]?99|991|press", d, re.I)]
    pick = (ex or [f["primary"]] or htm)[0]
    try:
        return f["base"] + pick, clean(sec_get(f["base"] + pick, raw=True).decode("utf-8", "replace"))[:60000]
    except Exception:
        return f["base"] + pick, ""


_ok = {}


def offer_kind(f):
    """a prospectus / registration: 'equity' (shares, ATM, convertible = dilution), 'debt' (notes), or 'shelf' (S-3 / F-3
    with no takedown); HCA Nov 4 2026: a 424B5 for senior notes is not dilution"""
    if f["acc"] in _ok:
        return _ok[f["acc"]]
    try:
        t = clean(sec_get(f["base"] + f["primary"], raw=True)[:60000].decode("utf-8", "replace"))[:8000].lower()
    except Exception:
        t = ""
    if re.search(r"convertible|common stock|ordinary shares|american depositary|pre-funded warrants|at[- ]the[- ]market|units consisting", t[:5000]):
        k = "equity"
    elif re.search(r"\bnotes? due\b|senior notes|debentures|% notes|bonds due", t[:5000]):
        k = "debt"
    else:
        k = "equity"
    if f["form"] in ("S-3", "F-3") and k == "equity" and not re.search(r"at[- ]the[- ]market|sales agreement|underwrit", t):
        k = "shelf"
    _ok[f["acc"]] = k
    return k


# ───────── the news ─────────
MONEY = r"\$\s?(\d[\d,]*(?:\.\d+)?)\s*(million|billion|thousand|[mbk])\b"
UNIT = {"million": 1e6, "billion": 1e9, "thousand": 1e3, "m": 1e6, "b": 1e9, "k": 1e3}


def money_max(s):
    best = 0.0
    for m in re.finditer(MONEY, s, re.I):
        try:
            best = max(best, float(m.group(1).replace(",", "")) * UNIT[m.group(2).lower()])
        except ValueError:
            pass
    return best


def earnings_news(e, direction):
    """the Earnings tab's numbers (or the same fields worked out for the backtest) -> (grade, catalyst, reason, inflection, score)"""
    rs, gr, pg = e.get("rev_surprise"), e.get("rev_growth"), e.get("rev_prev_growth")
    g = e.get("guide") or {}
    d, vs = g.get("dir"), g.get("vs_street")
    prod = g.get("kind") == "product"                 # one product's guide (URGN: JELMYTO) counts as weak / modest only
    if prod:
        vs = None
    acc = gr - pg if gr is not None and pg is not None else None
    raised = (d == "raised" and not prod) or (vs is not None and vs >= 1)
    weak_guide = d == "lowered" or (vs is not None and vs <= -1)
    turn = pg is not None and gr is not None and pg < 0 <= gr
    bits = []
    if rs is not None:
        bits.append(f"revenue {'beat' if rs > 0 else 'miss'} {rs:+.1f}%")
    if gr is not None:
        bits.append(f"revenue {gr:+.0f}% y/y" + (f" (last q {pg:+.0f}%: {'faster' if acc >= 1 else 'slower' if acc <= -1 else 'same'})" if acc is not None else ""))
    if d and d not in ("none", "given"):
        bits.append(f"guidance {d}" + (f" ({g.get('product')} only)" if g.get("kind") == "product" else ""))
    if vs is not None:
        bits.append(f"guide {vs:+.1f}% vs street")
    infl, sc = "None", 0
    if acc is not None and acc >= 3:
        infl, sc = "Acceleration", min(10, 4 + int(acc // 3) + (2 if raised else 0))
    elif turn:
        infl, sc = "Turnaround", 5 + (2 if raised else 0)
    elif (acc is not None and (acc <= -10 or (acc <= -5 and gr < 15))) or (d == "lowered" and not prod):
        infl, sc = "Deterioration", 5 + (2 if d == "lowered" else 0)
    if direction == "up":
        if weak_guide:
            gd = "C"
        elif raised and (rs is None or rs > 0) and ((gr is not None and gr >= 20) or (acc is not None and acc >= 3)):
            gd = "A"
        elif raised or turn or (gr is not None and gr >= 15 and (rs is None or rs >= 0)) or (rs is not None and rs >= 2 and (gr or 0) >= 0):
            gd = "B"
        else:
            gd = "C"
    else:
        if (d == "lowered" and not prod) or (rs is not None and rs <= -2 and weak_guide):
            gd = "A"
        elif (rs is not None and rs < 0) or weak_guide or (gr is not None and gr < 0):
            gd = "B"
        else:
            gd = "C"
    cat = "Earnings" + (" beat" if rs and rs > 0 else " miss" if rs and rs < 0 else "") + (" + raise" if raised else
                                                                                         " + product guide cut" if d == "lowered" and prod else " + guide cut" if d == "lowered" else "")
    return gd, cat, "; ".join(bits) or "earnings release (numbers not read)", infl, sc


def classify(fs, texts, direction, mcap, e=None):
    """filings in the window + their release texts -> {news, catalyst, reason, flags, sources, inflection, inflection_score}"""
    out = dict(news="C", catalyst="No company news", reason="No SEC filing or company release since the last close",
               flags="", sources=[], inflection="None", inflection_score=0)
    if fs is None:
        out.update(reason="Not found at the SEC (no CIK): grade by hand", catalyst="Not at the SEC")
        return out
    items = lambda f: f.get("items") or ""
    flags = []
    offer = [f for f in fs if (f["form"] in OFFER_FORMS and offer_kind(f) == "equity") or (f["form"] in ("8-K", "6-K") and "3.02" in items(f))]
    shelf = [f for f in fs if f["form"] in OFFER_FORMS and offer_kind(f) == "shelf"]
    deli = [f for f in fs if f["form"] == "8-K" and "3.01" in items(f)]
    erel = [f for f in fs if (f["form"] == "8-K" and "2.02" in items(f)) or (f["form"] == "6-K" and re.search(r"results|earnings|quarter", texts.get(f["acc"], ("", ""))[1][:600], re.I))]
    alltxt = " ".join(t[1][:4000] for t in texts.values())
    head = " ".join(t[1][:700] for t in texts.values())
    srcs = [texts[f["acc"]][0] for f in fs if f["acc"] in texts and texts[f["acc"]][0]] or [f["base"] for f in fs][:3]
    out["sources"] = srcs[:3]
    if offer or re.search(r"pricing of (?:its |an? |the )?(?:upsized )?(?:underwritten |public |registered direct |private )?offering|"
                          r"at[- ]the[- ]market (?:equity )?(?:offering|program)|convertible (?:senior )?notes offering", head, re.I):
        flags.append("dilution: " + ", ".join(sorted({f["form"] for f in offer})) if offer else "dilution: an offering in the release")
    if re.search(r"reverse (?:stock )?split", head, re.I):
        flags.append("reverse split")
    if re.search(r"substantial doubt|going concern", alltxt, re.I):
        flags.append("going concern")
    if deli:
        flags.append("delisting notice (8-K 3.01)")
    debt = [f for f in fs if f["form"] in OFFER_FORMS and offer_kind(f) == "debt"]
    note = ([f"debt offering ({', '.join(sorted({f['form'] for f in debt}))}: not dilution)"] if debt else []) + \
           ([f"new shelf registration ({', '.join(sorted({f['form'] for f in shelf}))}): possible future dilution"] if shelf else [])
    out["flags"] = "; ".join(flags + note)
    if flags and direction == "up":
        out.update(news="F", catalyst="Dilution / warning", reason="F by rule: " + out["flags"])
        return out
    # earnings
    if erel or e:
        gd, cat, why, infl, sc = earnings_news(e or {}, direction)
        out.update(news=gd, catalyst=cat, reason=why, inflection=infl, inflection_score=sc)
        if direction == "down" and flags:
            out["news"] = "A" if gd == "A" else "B"
        return out
    # takeover, FDA, trials, contracts, executives (the release headline and the 8-K items)
    if re.search(r"(?:definitive|merger) agreement", head, re.I) and re.search(r"to be acquired by|will acquire all|acquired by .{0,60}for \$|per share in cash|"
                                                                                r"take(?:s)? .{0,20}private|all-cash transaction", head, re.I) and not re.search(r"\bto acquire\b|\bacquisition of\b", head[:200], re.I):
        out.update(news="A" if direction == "up" else "C", catalyst="Signed takeover", reason="A signed agreement to be acquired (8-K / release)")
    elif re.search(r"\b(?:to acquire|acquisition of|agreed to acquire|will acquire)\b", head, re.I):
        out.update(news="C" if direction == "up" else "B", catalyst="Buying a company", reason="The company is the acquirer: " + head[:160])
    elif re.search(r"FDA (?:has )?(?:approv|grants? (?:accelerated )?approval)|approval (?:of|for) .{0,60}by the (?:U\.S\. )?(?:FDA|Food and Drug)", head, re.I):
        out.update(news="A" if direction == "up" else "C", catalyst="FDA approval", reason=head[:200], inflection="New business", inflection_score=7)
    elif re.search(r"complete response letter|\bCRL\b", head, re.I):
        out.update(news="A" if direction == "down" else "C", catalyst="FDA rejection (CRL)", reason=head[:200])
    elif re.search(r"did not (?:meet|achieve)|failed to (?:meet|achieve)|missed (?:its|the) primary endpoint", head, re.I):
        out.update(news="A" if direction == "down" else "C", catalyst="Failed trial", reason=head[:200])
    elif re.search(r"positive (?:topline|top-line|phase)|met (?:its|the) primary endpoint|statistically significant", head, re.I):
        out.update(news="B" if direction == "up" else "C", catalyst="Positive trial data", reason=head[:200], inflection="New business", inflection_score=5)
    elif re.search(r"\b(?:contract|award(?:ed)?|order|agreement|lease|partnership|collaboration)\b", head, re.I) and money_max(head) > 0:
        v = money_max(head)
        share = v / (mcap * 1e9) if mcap else 0
        g = "A" if share >= 0.25 else "B" if share >= 0.05 else "C"
        out.update(news=g if direction == "up" else "C", catalyst="Contract / agreement",
                   reason=f"{head[:160]} ... (${v / 1e6:,.0f}M = {share * 100:.0f}% of the market cap)",
                   inflection="New business" if g == "A" else "None", inflection_score=7 if g == "A" else 0)
    elif re.search(r"(?:chief executive|ceo|chief financial|cfo)\b.{0,80}\b(?:resign|depart|step(?:s|ping)? down|terminat|leave)", head, re.I) or \
            any(f["form"] == "8-K" and "5.02" in items(f) and re.search(r"resign|depart|step(?:s|ping)? down|terminat", texts.get(f["acc"], ("", ""))[1][:3000], re.I) for f in fs):
        imm = re.search(r"effective immediately", alltxt, re.I)
        out.update(news=("A" if imm else "B") if direction == "down" else "C", catalyst="Executive change", reason=head[:200])
    elif fs:
        kinds = ", ".join(sorted({f["form"] + (" " + items(f) if items(f) else "") for f in fs}))[:120]
        out.update(news="C", catalyst="Filing, not classified", reason=f"Filed since the close: {kinds}. " + head[:140])
    if direction == "down" and flags and out["news"] == "C":
        out.update(news="B", catalyst="Offering / dilution")
    return out


# ───────── the chart ─────────
def chart_state(px, prev_c, e21, e50, s200, hi21):
    """where the pre-market price puts the stock vs the last close's averages (the user's turn-up idea)"""
    if None in (px, s200) or s200 != s200:
        return "unknown"
    if px < s200 and px < e50:                      # under both the 50 and the 200: qualifies for nothing (the user,
        return "under50_200"                        # Nov 4 2026: NVTS $9.60 under its 50 EMA 10.65 and 200 SMA 13.30)
    if px < s200:                                   # over the 50, under the 200: a laggard only if it clears the 21-day
        return "laggard" if hi21 is not None and px > hi21 else "downtrend"   # high (every Launch laggards rule but the 200)
    if (prev_c < e50 or prev_c < s200) and px > e50 and hi21 is not None and px > hi21:
        return "turnup"
    if e21 > e50 > s200 and px > e21:
        return "trending"
    return "mixed"


# W = laggard watch (the user, Nov 4 2026): real news, over the 21-day high, but still under the 200 SMA after the gap
# (every Launch laggards rule but the 200), so shorts are in control; lower importance, but it isn't dropped: the news grade (A / B) still feeds the Launch laggards rule, and the
# day it gets over its 50 and 200 it is a turn-up
COMBINE = {"A": {"turnup": "A+", "trending": "A", "mixed": "B", "laggard": "W"},
           "B": {"turnup": "A", "trending": "B", "mixed": "C", "laggard": "W"}}
LOW52_MIN = 30                                      # the user's main rule: 30%+ over the 52-week low (pre-market price)


def combine(news, chart, direction, broke_trend=False, over_low52=None):
    if direction == "down":
        return "A" if news == "B" and broke_trend else news
    if chart in ("under50_200", "downtrend") or (chart == "laggard" and news not in ("A", "B")):
        return "—"                                  # under the 200 the trend isn't confirmed: no grade at all (the user,
                                                    # Nov 4 2026), except W: A / B news + every laggard rule but the 200
    g = COMBINE[news].get(chart, news) if news in COMBINE else news
    if over_low52 is not None and over_low52 < LOW52_MIN:
        g = "—"                                     # under 30% over the 52-week low qualifies for nothing (the user, Nov 4 2026;
    return g                                        # the pre-market list drops these before grading)


# ───────── live: the pre-market list ─────────
_y = []


def yahoo_bars(sym, before):
    """daily bars before the given date (Yahoo, 1 year): closes, highs"""
    if not _y:
        from earnings import Y
        _y.append(Y())
    j = _y[0].get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym.replace('.', '-')}?range=1y&interval=1d")
    r = j["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    rows = [(datetime.datetime.fromtimestamp(t, NY).date().isoformat(), c, h) for t, c, h in zip(r["timestamp"], q["close"], q["high"]) if c and h]
    rows = [x for x in rows if x[0] < before]
    return [x[1] for x in rows], [x[2] for x in rows]


def ema_last(xs, n):
    a, e = 2 / (n + 1), xs[0]
    for x in xs[1:]:
        e = a * x + (1 - a) * e
    return e


def earn_fields(sym, text, day):
    """a release the Earnings tab didn't cover (outside its filters): its revenue, growth, last quarter's growth and the
    guidance, read the same way (radar/earnings.py), with Yahoo's history; no saved estimate, so no beat / miss"""
    from earnings import Y, rev_from, rev_growth_from, guidance, pick, ym
    if not _y:
        _y.append(Y())
    y = _y[0]
    hist, trend = y.summary(sym.replace(".", "-"))
    qs = sorted((q for q, h in hist.items() if h.get("act") is not None), reverse=True)
    if not qs:
        return {"guide": guidance(text, None, None)}
    qe = qs[0]
    sh = lambda q, n: (lambda k: (k // 12, k % 12 + 1))(q[0] * 12 + q[1] - 1 + 3 * n)
    ts = y.revenue_ts(sym.replace(".", "-"))
    yago, prev, prev_yago = pick(ts, sh(qe, -4)), pick(ts, sh(qe, -1)), pick(ts, sh(qe, -5))
    act = rev_from(text, None, yago) or pick(ts, qe)
    if act is None and yago:
        gr0 = rev_growth_from(text)
        act = yago * (1 + gr0 / 100) if gr0 is not None else None
    pct = lambda a, b: round((a / b - 1) * 100, 1) if a and b and b > 0 else None
    return {"rev_act": act, "rev_growth": pct(act, yago), "rev_prev_growth": pct(prev, prev_yago),
            "guide": guidance(text, trend.get("0q"), trend.get("0y")), "rev_surprise": None}


def last_close_time(day):
    """the last session's close (4 PM ET) before `day` (ISO)"""
    from earnings import back, HOLIDAYS  # noqa
    d = datetime.date.fromisoformat(day)
    p = back(d)
    return datetime.datetime(p.year, p.month, p.day, 16, 0, tzinfo=NY)


def live(pm_path, stocks_path, earn_path, out_path, asof=None):
    rows = [r for r in json.load(open(pm_path)) if not r.get("placeholder") and r.get("direction") in ("up", "down")]
    try:                                                # Claude's grade for the same stock, when it's posted
        cl = {x["symbol"]: x.get("grade") for x in json.load(open(os.path.join(os.path.dirname(pm_path), "claude_premarket.json")))
              if x.get("scan_date") == (rows[0].get("scan_date") if rows else None)}
        for r in rows:
            r.setdefault("grade", cl.get(r["symbol"]))
    except Exception:
        pass
    rows = [r for r in rows if r.get("graded")] or rows[:16]
    S = {s["symbol"]: s for s in json.load(open(stocks_path))}
    E = {}
    try:
        ej = json.load(open(earn_path))
        E = {r["sym"]: r for r in ej.get("rows", []) if r.get("reported")}
    except Exception:
        pass
    day = rows[0].get("scan_date") if rows else datetime.datetime.now(NY).date().isoformat()
    t_to = datetime.datetime.fromisoformat(asof).replace(tzinfo=NY) if asof else datetime.datetime.now(NY)
    t_from = last_close_time(day)
    out = {}
    for r in rows:
        sym, d = r["symbol"], r["direction"]
        st = S.get(sym, {})
        mcap = st.get("mcap_b") or r.get("mcap_b")
        try:
            fs = filings(sym, t_from, t_to)
        except Exception as ex:
            fs = None
            print("sec", sym, repr(ex)[:120])
        texts = {}
        for f in (fs or [])[:8]:
            if f["form"] in ("8-K", "6-K", "8-K/A"):
                texts[f["acc"]] = release_text(f)
        e = E.get(sym)
        if e and not (e.get("date") >= t_from.date().isoformat()):
            e = None
        er = [f for f in (fs or []) if f["form"] in ("8-K", "6-K") and ("2.02" in (f.get("items") or "") or f["form"] == "6-K")]
        if er and not e:
            try:
                e = earn_fields(sym, texts.get(er[0]["acc"], ("", ""))[1], day)
            except Exception as ex:
                print("earnings", sym, repr(ex)[:120])
        nw = classify(fs, texts, d, mcap, e)
        # the chart at the pre-market price
        try:
            cl, hi = yahoo_bars(sym, day)
            e21, e50 = ema_last(cl[-120:], 21), ema_last(cl[-200:], 50)
            s200 = sum(cl[-200:]) / 200 if len(cl) >= 200 else st.get("sma200")
            hi21 = max(hi[-21:]) if len(hi) >= 21 else None
            px = r.get("pm_last")
            ch = chart_state(px, cl[-1], e21, e50, s200, hi21)
            broke = bool(d == "down" and e21 > e50 > s200 and px < e50 and px < s200)
            lv = dict(e21=round(e21, 2), e50=round(e50, 2), s200=round(s200, 2) if s200 else None, hi21=round(hi21, 2) if hi21 else None)
        except Exception as ex:
            ch, broke, lv = "unknown", False, {}
            print("bars", sym, repr(ex)[:120])
        lo52 = st.get("low_52w")
        ol = round((r.get("pm_last") / lo52 - 1) * 100, 1) if lo52 and r.get("pm_last") else None
        fin = combine(nw["news"], ch, d, broke, ol)
        if ol is not None and ol < LOW52_MIN and d == "up":
            nw["flags"] = "; ".join(x for x in (nw["flags"], f"only {ol:.0f}% over the 52-week low (rule: 30%+)") if x)
        if d == "up" and nw["news"] == "C" and ch == "turnup":
            nw["flags"] = "; ".join(x for x in (nw["flags"], "chart turn-up without company news") if x)
        out[sym] = dict(nw, direction=d, chart=ch, grade=fin, levels=lv, claude=r.get("grade"), pm_last=r.get("pm_last"), over_low52=ol)
        print(f"{sym:6} {d:4} news {nw['news']} chart {ch:9} -> {fin:2} | Claude {r.get('grade')} | {nw['catalyst']}: {nw['reason'][:90]}")
    json.dump({"built_at": datetime.datetime.now(NY).isoformat(timespec="seconds"), "day": day,
               "window": [t_from.isoformat(), t_to.isoformat()], "rows": out}, open(out_path, "w"), indent=0)


def log(cg_path, log_path):
    """the day's code grades into codegrade_log.json (one entry per day and stock, the last run of the morning wins),
    for the 1-2 week comparison with Claude's grades (outcomes come from the bars when it's evaluated)"""
    cg = json.load(open(cg_path))
    try:
        lg = json.load(open(log_path))
    except Exception:
        lg = []
    keep = {e["key"]: e for e in lg if isinstance(e, dict) and e.get("key")}
    for sym, r in cg.get("rows", {}).items():
        k = f"{cg['day']} {sym}"
        keep[k] = {"key": k, "date": cg["day"], "symbol": sym, "direction": r["direction"], "grade": r["grade"], "news": r["news"],
                   "chart": r["chart"], "catalyst": r["catalyst"], "pm_last": r.get("pm_last"), "claude": r.get("claude"), "built_at": cg["built_at"]}
    json.dump(sorted(keep.values(), key=lambda e: e["key"]), open(log_path, "w"), separators=(",", ":"))
    print(len(keep), "log entries")


if __name__ == "__main__":
    if sys.argv[1] == "log":
        log(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "live":
        a = [x for x in sys.argv[2:] if not x.startswith("--asof=")]
        asof = next((x.split("=", 1)[1] for x in sys.argv if x.startswith("--asof=")), None)
        live(a[0], a[1], a[2], a[3], asof)
