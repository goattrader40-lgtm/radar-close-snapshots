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
  STAGE (the last close; "rising" = higher than 5 sessions ago): 2 uptrend = 21 EMA > 50 EMA > 200 SMA, the 21 and
        the 50 rising; 3 pullback / chop = over the 200, the 50 over it, not 2; 1 basing / turning = over the 200 with the
        50 still under it, or under the 200 without 4; 4 downtrend = under the 200, the 21 under the 50, both falling
  ELIGIBLE (gap-ups at the pre-market price): 30%+ over the 52-week low, ADR 3.5%+, over the 50 EMA, at most 20% under
        the 200 SMA, over the highest close of the last 21 sessions (else it gaps into chop); else "—". No cap over the
        200; extension = the ATR multiple from the 50 SMA: 10x+ flagged "extended", 15x+ at most C. A 5-8% gap one grade lower;
        A+ only in a leading or turning-up group. The reversal is shown as "⤴ reversal" (not the ★ stars, not the
        Trend column's "Turn up").
  NEWS ONLY (the user, Nov 6 2026): every other 5%+ gapper (prepare's gappers.json: the list's rules dropped it) gets
        the same news lookup, no grade, under "news" in the output (with the rule that dropped it); a gap with no filing
        while 3+ of its theme / industry gap 5%+ the same way reads "Sector move: <group>" (graded rows too).
        Earnings reported before the last close (a report the morning before: VCEL Nov 5 2026) are not today's news:
        with no new filing the gap reads "After earnings (<date>)", news C.
  GRADE (gap-ups) stage 2 / 3: A / B news -> A / B; stage 1 / 4 now over the 200 (★ turn-up, shorts caught off guard):
        A news A+, B news A; stage 1 / 4 still under the 200: W (laggard watch) on A / B news or an earnings report, else
        "—"; C and F as they are. Gap-downs: the news grade, B -> A when a stage-2 stock gaps under its 50 and 200.
"""
import datetime, html, json, os, re, sys, time, urllib.parse, urllib.request, zoneinfo
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
FILINGS_SINCE = "9999"      # the live grader never needs older pages; the backtest sets its first date
ROUTINE = {"5.07", "5.03", "5.08", "9.01", "3.03"}   # votes, bylaws, exhibits only: no news in them


def worth_reading(f):
    if f["form"] == "6-K":
        return True
    items = {x.strip() for x in (f.get("items") or "").split(",") if x.strip()}
    return f["form"] in ("8-K", "8-K/A") and bool(items - ROUTINE)


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
        for extra in sub["filings"].get("files", []):          # older pages, only as far back as the backtest needs
            if extra.get("filingTo", "9999") >= FILINGS_SINCE:
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


def tidy(t):
    """a release's text without the SEC exhibit header ("EX-99.1 2 lrcx_ex991.htm EX-99.1 Document FOR IMMEDIATE
    RELEASE"), so a reason starts with its words"""
    t = re.sub(r"\bEX-\d+(?:\.\d+)?\s+\d+\s+\S+\.(?:htm|html|txt)\b\s*", " ", t[:1500], flags=re.I)
    t = re.sub(r"\b(?:EX-\d+(?:\.\d+)?\s+Document|EXHIBIT\s+\d+(?:\.\d+)?|FOR IMMEDIATE RELEASE)\b:?\s*", " ", t, flags=re.I)
    return re.sub(r"\s+", " ", t).strip()


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
    lead = " ".join(tidy(t[1])[:700] for t in texts.values())      # the same, for the reason shown (no exhibit header)
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
        out.update(news="C" if direction == "up" else "B", catalyst="Buying a company", reason="The company is the acquirer: " + lead[:160])
    elif re.search(r"FDA (?:has )?(?:approv|grants? (?:accelerated )?approval)|approval (?:of|for) .{0,60}by the (?:U\.S\. )?(?:FDA|Food and Drug)", head, re.I):
        out.update(news="A" if direction == "up" else "C", catalyst="FDA approval", reason=lead[:200], inflection="New business", inflection_score=7)
    elif re.search(r"complete response letter|\bCRL\b", head, re.I):
        out.update(news="A" if direction == "down" else "C", catalyst="FDA rejection (CRL)", reason=lead[:200])
    elif re.search(r"did not (?:meet|achieve)|failed to (?:meet|achieve)|missed (?:its|the) primary endpoint", head, re.I):
        out.update(news="A" if direction == "down" else "C", catalyst="Failed trial", reason=lead[:200])
    elif re.search(r"positive (?:topline|top-line|phase)|met (?:its|the) primary endpoint|statistically significant", head, re.I):
        out.update(news="B" if direction == "up" else "C", catalyst="Positive trial data", reason=lead[:200], inflection="New business", inflection_score=5)
    elif re.search(r"\b(?:contract|award(?:ed)?|order|agreement|lease|partnership|collaboration)\b", head, re.I) and money_max(head) > 0:
        v = money_max(head)
        share = v / (mcap * 1e9) if mcap else 0
        g = "A" if share >= 0.25 else "B" if share >= 0.05 else "C"
        out.update(news=g if direction == "up" else "C", catalyst="Contract / agreement",
                   reason=f"{lead[:160]} ... (${v / 1e6:,.0f}M = {share * 100:.0f}% of the market cap)",
                   inflection="New business" if g == "A" else "None", inflection_score=7 if g == "A" else 0)
    elif re.search(r"(?:chief executive|ceo|chief financial|cfo)\b.{0,80}\b(?:resign|depart|step(?:s|ping)? down|terminat|leave)", head, re.I) or \
            any(f["form"] == "8-K" and "5.02" in items(f) and re.search(r"resign|depart|step(?:s|ping)? down|terminat", texts.get(f["acc"], ("", ""))[1][:3000], re.I) for f in fs):
        imm = re.search(r"effective immediately", alltxt, re.I)
        out.update(news=("A" if imm else "B") if direction == "down" else "C", catalyst="Executive change", reason=lead[:200])
    elif fs:
        kinds = ", ".join(sorted({f["form"] + (" " + items(f) if items(f) else "") for f in fs}))[:120]
        out.update(news="C", catalyst="Filing, not classified", reason=f"Filed since the close: {kinds}. " + lead[:140])
    if direction == "down" and flags and out["news"] == "C":
        out.update(news="B", catalyst="Offering / dilution")
    return out


# ───────── the chart ─────────
SLOPE = 5          # "rising" = higher than 5 sessions ago (an EMA's one-day change only repeats the price test: NVDA
                   # May 5 2026 closed under its 21 EMA in an uptrend and would flip to chop for a day)
LAUNCH = dict(min_adr=3.5)   # the launch list's ADR (scanner/settings.json)
MAX_EXT200 = None  # no cap over the 200 SMA: leaders run 200-300% over it (the user, Nov 4 2026); extension is the ATR
                   # multiple from the 50 SMA instead (the user's own setting)
EXTENDED = 10      # pre-market price 10+ ATRs over the 50 SMA: flagged "extended" (the user's setting)
TOO_EXTENDED = 15  # 15+ ATRs: at most C (backtest, 8%+ gaps: trade -6.7%, broke the low 68%)
MIN_GAP_AB = 8     # A+ / A / B only on gaps of 8%+ (backtest: 5-8% gaps with A / B news ran 20%+ only 9-14% of the time)
MAX_UNDER200 = 20  # a laggard at most 20% under the 200 at the pre-market price (backtest: 10-20% under crossed the 200
                   # within 60 sessions 78%, 20-30% 50%, 30%+ 8%; the user had 25-30% in mind)
LOW52_MIN = 30     # 30%+ over the 52-week low, like every list (the user, Nov 4 2026)


def stage(c, e21, e50, s200, e21_ago, e50_ago, both=True):
    """the trend stage at the last close (the user, Nov 4 2026): 2 uptrend = 21 > 50 > 200 with the 21 and the 50 rising
    (both, so no chop); 3 pullback / chop = over the 200 with the 50 over it, not 2; 1 basing / turning = over the 200
    with the 50 still under it, or under the 200 without 4; 4 downtrend = under the 200, the 21 under the 50, both
    falling (ALAB Nov 4 2026: a breakdown, not a pullback, though its 50 is still over its 200)"""
    r21, r50 = e21 > e21_ago, e50 > e50_ago
    if c < s200:
        return 4 if (e21 < e50 and not r21 and not r50) else 1
    if e50 < s200:
        return 1
    if e21 > e50 > s200 and r21 and (r50 or not both):
        return 2
    return 3


def eligible(px, prev_c, e50, s200, hi, adr, gap, over_low52, max_ext=MAX_EXT200, max_under=MAX_UNDER200):
    """a gap-up eligible at the pre-market price: (True, "") or (False, why). hi = the 21-day high by the closes (the user,
    Nov 4 2026: the pre-market / opening price over the highest close of the last 21 sessions)"""
    if over_low52 is not None and over_low52 < LOW52_MIN:
        return False, f"only {over_low52:.0f}% over the 52-week low (30%+)"
    if adr is not None and adr < LAUNCH["min_adr"]:
        return False, f"ADR {adr:.2f}% (3.5%+)"
    ext = 100 * (prev_c / s200 - 1) if s200 else None
    if ext is not None and max_ext is not None and ext > max_ext:
        return False, f"{ext:.0f}% over the 200 SMA yesterday (at most {max_ext}%: parabolic)"
    if px < e50:
        return False, "under the 50 EMA"
    if s200 and px < s200 and max_under is not None and px < s200 * (1 - max_under / 100):
        return False, f"{100 * (1 - px / s200):.0f}% under the 200 SMA (a laggard at most {max_under}%)"
    if hi is not None and px <= hi:
        return False, "under the 21-day high close (gapping into last month's range = chop)"
    return True, ""


def atr_mult(px, sma50, atr, prev_c):
    """the ATR multiple from the 50 SMA: (% over the 50 SMA) / (ATR %)"""
    if not (px and sma50 and atr and prev_c):
        return None
    return round((px / sma50 - 1) / (atr / prev_c), 1)


def event(stg, px, s200):
    """what the gap does: 'trend' (stage 2 / 3 over the 21-day high: the trend goes on, chop cleared), 'turnup' (stage 1 / 4
    now over the 200: shorts caught off guard), 'laggard' (stage 1 / 4 still under the 200)"""
    if stg in (2, 3):
        return "trend"
    return "turnup" if px > s200 else "laggard"


LOWER = {"A+": "A", "A": "B", "B": "C"}


def combine(news, ev, direction, ok=True, earn=False, broke_trend=False, gap=None, mult=None, group=None):
    """the final grade (the user's choices, Nov 4 2026): 15+ ATRs over the 50 SMA at most C; a 5-8% gap one grade lower
    (YOU Nov 4: an A+ reversal on a 6.3% gap closed +23.8%); A+ only in a leading or turning-up group (backtest:
    reversals in a leading group r20 +16%, in a group that isn't trending -3.5%)"""
    g = _combine(news, ev, direction, ok, earn, broke_trend)
    if direction == "up" and g in ("A+", "A", "B"):
        if mult is not None and mult >= TOO_EXTENDED:
            g = "C"
        elif gap is not None and gap < MIN_GAP_AB:
            g = LOWER[g]
        if g == "A+" and group is not None and group < 1:
            g = "A"
    return g


def stars(stocks, trend, launch_doc):
    """{symbol: (star, trend label, group tier)} as the portal's Stars column shows them (docs/index.html launchStars, the
    conviction stars, live Nov 4 2026), from the last close: ★★ = its best group ★ Top / Strong (not a loose group) and
    Trend Negative (under the 21 EMA: a launch out of a pullback); ★ = Trend Up; ⚠ = no Trend label; "" = the rest.
    Logged next to the code grade, so the two can be compared (the user, Nov 4 2026)"""
    gr = (launch_doc or {}).get("group_rank") or {}
    by = {(g["kind"], g["group"]): g for g in gr.get("rows", [])}
    ug = any(r.get("group") for r in stocks)
    tr = (trend or {}).get("rows", trend or {})
    out = {}
    for r in stocks:
        ind = (r["group"] if r.get("group") else (r.get("industry") or "Other") + " · other") if ug else r.get("industry")
        c = [by.get(("theme", t)) for t in (r.get("themes") or "").split(" | ") if t] + [by.get(("ind", ind))]
        c = [x for x in c if x]
        b = max(c, key=lambda x: (min(x["pct"], 89.9) if x.get("loose") else x["pct"], -x["rank"])) if c else None
        tier = b["tier"] if b and not b.get("loose") else None
        t = tr.get(r["symbol"])
        lab = t[0] if t else None
        if lab is None:
            continue
        star = "★★" if tier in ("Top", "Strong") and lab == "Negative" else "★" if lab == "Up" else "⚠" if lab == "" else ""
        out[r["symbol"]] = (star, lab, tier)
    return out


def group_status(stocks, themes, trend):
    """{symbol: 2 leading / 1 turning up / 0} at the last close, the backtest's rule (scanner/launch.py group_status): a
    group of 3+ stocks is leading when 60%+ are over their 50 EMA and the median 1-month move is 8%+, turning up when
    half are over their 21 EMA and the median 1-week move is up; a stock takes its best group (themes, else industry,
    and their areas)"""
    import statistics
    area = {t["theme"]: t.get("category") for t in themes if t.get("category") != "Auto groups"}
    tr = (trend or {}).get("rows", trend or {})
    members = {}
    for r in stocks:
        th = [t for t in (r.get("themes") or "").split(" | ") if t]
        gs = th or ([r["industry"]] if r.get("industry") else [])
        ars = sorted({area[t] for t in th if t in area}) if th else ([r["sector"]] if r.get("sector") else [])
        for g in gs + ["area:" + a for a in ars]:
            members.setdefault(g, []).append(r)
    st = {}
    for g, ms in members.items():
        if len(ms) < 3:
            continue
        o50 = [(m.get("vs_50e") or 0) > 0 for m in ms if m.get("vs_50e") is not None]
        o21 = []
        for m in ms:
            t = tr.get(m["symbol"])
            if t and len(t) > 2 and t[2] and len(t[2]) >= 6:
                o21.append(t[2][5] > t[2][2])           # the price over the 21 EMA
        m1 = [m["chg_1m"] for m in ms if m.get("chg_1m") is not None]
        m5 = [m["chg_1w"] for m in ms if m.get("chg_1w") is not None]
        sh50 = sum(o50) / len(o50) if o50 else 0
        sh21 = sum(o21) / len(o21) if o21 else 0
        if sh50 >= 0.6 and m1 and statistics.median(m1) >= 8:
            st[g] = 2
        elif sh21 >= 0.5 and m5 and statistics.median(m5) > 0:
            st[g] = 1
        else:
            st[g] = 0
    out = {}
    for g, ms in members.items():
        for m in ms:
            out[m["symbol"]] = max(out.get(m["symbol"], 0), st.get(g, 0))
    return out


def _combine(news, ev, direction, ok=True, earn=False, broke_trend=False):
    """the grade: gap-ups eligible only by the launch rules; over the 200 A / B news -> A / B (turn-up A+ / A); under the
    200 only W (laggard watch: A / B news or an earnings report, the Launch laggards rule); C and F as they are; the rest
    "—". Gap-downs: the news grade, B -> A when a stage-2 stock gaps under its 50 and 200."""
    if direction == "down":
        return "A" if news == "B" and broke_trend else news
    if not ok:
        return "—"
    if ev == "laggard":
        return "W" if news in ("A", "B") or (earn and news != "F") else "—"
    if news == "A":
        return "A+" if ev == "turnup" else "A"
    if news == "B":
        return "A" if ev == "turnup" else "B"
    return news


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
    rows = [(datetime.datetime.fromtimestamp(t, NY).date().isoformat(), c, h, lo) for t, c, h, lo in zip(r["timestamp"], q["close"], q["high"], q["low"]) if c and h and lo]
    rows = [x for x in rows if x[0] < before]
    return [x[1] for x in rows], [x[2] for x in rows], [x[3] for x in rows]


def ema_series(xs, n):
    a, out = 2 / (n + 1), [xs[0]]
    for x in xs[1:]:
        out.append(a * x + (1 - a) * out[-1])
    return out


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


def live(pm_path, stocks_path, earn_path, out_path, asof=None, grade=True):
    """grade=False (the 8:05 / 8:35 news runs, the user Nov 6 2026: news from 8:05): no grades, every 5%+ gapper's news
    only, written to its own file (pmnews.json) so codegrade.json and its 8:45-9:25 pop-ups stay as they were"""
    rows = [r for r in json.load(open(pm_path)) if not r.get("placeholder") and r.get("direction") in ("up", "down")]
    if not grade:
        rows = []
    try:                                                # Claude's grade for the same stock, when it's posted
        cl = {x["symbol"]: x.get("grade") for x in json.load(open(os.path.join(os.path.dirname(pm_path), "claude_premarket.json")))
              if x.get("scan_date") == (rows[0].get("scan_date") if rows else None)}
        for r in rows:
            if not r.get("grade"):                      # the list's rows carry an empty grade
                r["grade"] = cl.get(r["symbol"])
    except Exception:
        pass
    # every gapper on the list (rows.json: all that pass the list's rules), not only the top 12 Claude researches
    SL = json.load(open(stocks_path))
    S = {s["symbol"]: s for s in SL}
    try:
        d0 = os.path.dirname(stocks_path)
        GRP = group_status(SL, json.load(open(os.path.join(d0, "themes.json"))), json.load(open(os.path.join(d0, "trend.json"))))
    except Exception as ex:
        GRP = {}
        print("group status:", repr(ex)[:120])
    try:                                                # the ★ stars of the Stars column, for the comparison
        STR = stars(SL, json.load(open(os.path.join(os.path.dirname(stocks_path), "trend.json"))),
                    json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "setups", "launch.json"))))
    except Exception as ex:
        STR = {}
        print("stars:", repr(ex)[:120])
    E = {}
    try:
        ej = json.load(open(earn_path))
        E = {r["sym"]: r for r in ej.get("rows", []) if r.get("reported")}
    except Exception:
        pass
    day = rows[0].get("scan_date") if rows else gappers_day(pm_path) or datetime.datetime.now(NY).date().isoformat()
    t_to = datetime.datetime.fromisoformat(asof).replace(tzinfo=NY) if asof else datetime.datetime.now(NY)
    t_from = last_close_time(day)
    out = {}
    for r in rows:
        sym, d = r["symbol"], r["direction"]
        st = S.get(sym, {})
        mcap = st.get("mcap_b") or r.get("mcap_b")
        nw, er = news_of(sym, d, mcap, E, t_from, t_to, day)
        # the chart: the stage at the last close, then the gap at the pre-market price
        px, lo52 = r.get("pm_last"), st.get("low_52w")
        ol = round((px / lo52 - 1) * 100, 1) if lo52 and px else None
        try:
            cl, hi, lo = yahoo_bars(sym, day)
            E21, E50 = ema_series(cl, 21), ema_series(cl, 50)
            e21, e50 = E21[-1], E50[-1]
            s200 = sum(cl[-200:]) / 200 if len(cl) >= 200 else st.get("sma200")
            hi21 = max(cl[-21:]) if len(cl) >= 21 else None          # the highest close of the last 21 sessions
            stg = stage(cl[-1], e21, e50, s200, E21[-1 - SLOPE], E50[-1 - SLOPE])
            ok, why = eligible(px, cl[-1], e50, s200, hi21, st.get("adr_20"), r.get("gap_pct") or 0, ol) if d == "up" else (True, "")
            ev = event(stg, px, s200) if d == "up" else None      # the events are a gap-up idea
            sma50 = sum(cl[-50:]) / 50 if len(cl) >= 50 else None
            tr = [max(hi[k] - lo[k], abs(hi[k] - cl[k - 1]), abs(lo[k] - cl[k - 1])) for k in range(len(cl) - 14, len(cl))] if len(cl) > 15 else []
            mult = atr_mult(px, sma50, sum(tr) / len(tr) if tr else None, cl[-1])
            broke = bool(d == "down" and stg == 2 and px < e50 and px < s200)
            lv = dict(e21=round(e21, 2), e50=round(e50, 2), s200=round(s200, 2) if s200 else None, hi21=round(hi21, 2) if hi21 else None,
                      e21_rising=E21[-1] > E21[-1 - SLOPE], e50_rising=E50[-1] > E50[-1 - SLOPE], ext200=round(100 * (cl[-1] / s200 - 1), 1) if s200 else None,
                      sma50=round(sma50, 2) if sma50 else None, atr_mult=mult)
        except Exception as ex:
            stg, ok, why, ev, broke, lv, mult = None, False, "no daily bars", None, False, {}, None
            print("bars", sym, repr(ex)[:120])
        earn = bool(er or E.get(sym))
        grp = GRP.get(sym) if GRP else None
        fin = combine(nw["news"], ev, d, ok, earn, broke, r.get("gap_pct"), mult, grp)
        if d == "up" and mult is not None and mult >= EXTENDED:
            nw["flags"] = "; ".join(x for x in (nw["flags"], f"extended: {mult:.0f}x ATR over the 50 SMA" + (" (15x+: at most C)" if mult >= TOO_EXTENDED else "")) if x)
        if d == "up" and ok and nw["news"] in ("A", "B") and (r.get("gap_pct") or 0) < MIN_GAP_AB:
            nw["flags"] = "; ".join(x for x in (nw["flags"], f"gap {r.get('gap_pct'):.1f}% (under 8%): one grade lower") if x)
        if d == "up" and ok and ev == "turnup" and nw["news"] == "A" and grp == 0:
            nw["flags"] = "; ".join(x for x in (nw["flags"], "its group isn't trending: A, not A+") if x)
        ch = {2: "uptrend", 3: "pullback", 1: "basing", 4: "downtrend"}.get(stg, "unknown")
        sx = STR.get(sym) or ("", None, None)
        out[sym] = dict(nw, direction=d, stage=stg, chart=ch, event=ev if ok else None, eligible=ok, not_eligible=why, grade=fin, group=grp,
                        star=sx[0], trend=sx[1], group_tier=sx[2],
                        levels=lv, claude=r.get("grade"), pm_last=px, over_low52=ol)
        print(f"{sym:6} {d:4} stage {stg} {('event ' + str(ev)) if ok else 'not eligible: ' + why:40} news {nw['news']} -> {fin:2} | Claude {r.get('grade')} | {nw['catalyst']}")
    # every other 5%+ gapper (gappers.json from prepare: the ones the list's rules dropped, e.g. under the 50 EMA or the
    # 30% over the 52-week low): its news only, no grade (the user, Nov 6 2026: "any gappers above 5%, their news"; FLY)
    news, every = {}, []
    gp = os.path.join(os.path.dirname(pm_path), "gappers.json")
    if os.path.exists(gp):
        try:
            every = [g for g in json.load(open(gp)) if g.get("direction") in ("up", "down")]
        except Exception as ex:
            print("gappers:", repr(ex)[:120])
    t0 = time.time()
    for g in every:                                     # biggest gaps first (prepare sorts them)
        sym, d = g["symbol"], g["direction"]
        if sym in out:
            continue
        if time.time() - t0 > NEWS_BUDGET:
            print(f"news: out of time after {len(news)} stocks, the rest have none this run")
            break
        nw, _ = news_of(sym, d, (S.get(sym) or {}).get("mcap_b") or g.get("mcap_b"), E, t_from, t_to, day)
        news[sym] = dict(nw, direction=d, gap_pct=g.get("gap_pct"), pm_last=g.get("pm_last"), dropped=g.get("dropped") or "")
        print(f"{sym:6} {d:4} news only ({g.get('dropped') or 'not on the list'}): {nw['news']} | {nw['catalyst']}")
    try:                                                # a stock's own headline when the SEC has nothing (FLY Nov 6: the AST
        H = headlines(list(out) + list(news), t_from, t_to)   # deal was a 7:31 AM press release, no 8-K yet)
    except Exception as ex:
        H = {}
        print("headlines:", repr(ex)[:160])
    use_headlines({**news, **out}, H, S)
    sector_moves(out, news, every, S)
    if not grade:                                       # the early news runs: pmnews.json, no rows
        json.dump({"built_at": datetime.datetime.now(NY).isoformat(timespec="seconds"), "day": day,
                   "window": [t_from.isoformat(), t_to.isoformat()], "news": news}, open(out_path, "w"), indent=0)
        return
    json.dump({"built_at": datetime.datetime.now(NY).isoformat(timespec="seconds"), "day": day,
               "window": [t_from.isoformat(), t_to.isoformat()], "rows": out, "news": news}, open(out_path, "w"), indent=0)


def gappers_day(pm_path):
    """the scan date of prepare's gappers.json (the day when no stock passed the list's rules)"""
    try:
        g = json.load(open(os.path.join(os.path.dirname(pm_path), "gappers.json")))
        return g[0].get("scan_date") if g else None
    except Exception:
        return None


NEWS_BUDGET = 480      # seconds for the news-only gappers (the job has 15 minutes; ~230 stocks on Nov 6 2026)
NO_NEWS = ("No company news", "Filing, not classified", "Not at the SEC")
ROUTINE_FORMS = {"3", "4", "5", "3/A", "4/A", "5/A", "144", "144/A", "SC 13G", "SC 13G/A", "SCHEDULE 13G", "SCHEDULE 13G/A", "13F-HR",
                 "S-8", "S-8 POS", "10-Q", "10-K", "DEF 14A", "DEFA14A", "ARS", "SD", "11-K", "CORRESP", "UPLOAD"}   # no news in them


def news_of(sym, d, mcap, E, t_from, t_to, day):
    """the news behind one gap: the SEC filings accepted since the last close, their releases and the Earnings tab's
    numbers -> (classify()'s dict, the earnings filings)"""
    try:
        fs = filings(sym, t_from, t_to)
    except Exception as ex:
        fs = None
        print("sec", sym, repr(ex)[:120])
    texts = {}
    for f in [f for f in (fs or []) if worth_reading(f)][:6]:
        texts[f["acc"]] = release_text(f)
    e = old = E.get(sym)
    last = t_from.date().isoformat()
    if e and (e.get("date") < last or (e.get("date") == last and e.get("when") == "bmo")):
        e = None                                        # reported before the last close, already in that close's price
    else:                                               # (VCEL Nov 5 7 AM, +13.9% that day: Nov 6 is day 2, not news)
        old = None
    er = [f for f in (fs or []) if f["form"] in ("8-K", "6-K") and ("2.02" in (f.get("items") or "") or f["form"] == "6-K")]
    if er and not e:
        try:
            e = earn_fields(sym, texts.get(er[0]["acc"], ("", ""))[1], day)
        except Exception as ex:
            print("earnings", sym, repr(ex)[:120])
    nw = classify(fs, texts, d, mcap, e)
    routine = bool(fs) and all(f["form"] in ROUTINE_FORMS or (f["form"] in ("8-K", "8-K/A") and not worth_reading(f)) for f in fs)
    if old and (nw["catalyst"] == "No company news" or (nw["catalyst"] == "Filing, not classified" and routine)):
        dt = datetime.date.fromisoformat(old["date"])    # say so instead of "no news" (Claude's U Nov 6: "Day-2 after Q3 beat")
        when = {"bmo": " before the open", "amc": " after the close"}.get(old.get("when"), "")
        nw.update(catalyst=f"After earnings ({dt:%b} {dt.day})",
                  reason=f"Reported {dt:%a %b} {dt.day}{when}: {old.get('why') or old.get('read') or 'see the Earnings tab'}; " +
                         (f"only routine filings since the last close ({', '.join(sorted({f['form'] for f in fs}))})" if fs else
                          "no new filing since the last close"))
    elif routine and nw["catalyst"] == "Filing, not classified":   # a Form 4 / 144 / 10-Q isn't news (BE Nov 6: a Form 4)
        nw.update(catalyst="No company news", reason=f"No news since the last close, only routine filings ({', '.join(sorted({f['form'] for f in fs}))})")
    return nw, er


def weak_news(r):
    """no news of its own today: none, routine filings, earnings before the last close, a board change (news C)"""
    return r.get("news") == "C" and (r.get("catalyst") in NO_NEWS or r["catalyst"].startswith("After earnings") or r["catalyst"] == "Executive change")


# ───────── headlines: Alpaca's news API (Benzinga: company press releases, Reuters / Dow Jones items, explainers) ─────────
LIST_ART = re.compile(r"stocks? (?:moving|to watch|making)|stock market today|here are \d+|\b\d+ (?:\w+ )?stocks\b|movers|top (?:gainers|losers)|"
                      r"futures|pre-?market session|earnings (?:scheduled|preview)|biggest moves|market (?:wrap|recap)", re.I)
KINDS = [("Analyst upgrade", r"\bupgrad"), ("Analyst downgrade", r"\bdowngrad"),
         ("Analyst note", r"\banalysts?\b|price target|\bmaintains\b|\breiterates\b|\binitiates\b"),
         ("Takeover / sale talk", r"\b(?:acquir\w*|buyout|takeover|take-private|explor\w* (?:a )?sale|strategic alternatives|to be acquired|merger|bid for|suitors?)\b"),
         ("Offering", r"\b(?:public offering|private placement|prices? .{0,30}offering|convertible notes|at-the-market)\b"),
         ("FDA / trial", r"\b(?:FDA|approval|approved|clearance|phase [123i]+|trial|topline|data readout)\b"),
         ("Buyback", r"\b(?:buyback|repurchase)\b"),
         ("Deal / contract", r"\b(?:agreement|deal|contract|orders?|award\w*|partnership|partners? with|collaborat\w*|selected|inks?|signs?|wins?|role in|supply)\b"),
         ("Earnings", r"\b(?:results|earnings|Q[1-4]|quarter|guidance|outlook)\b")]
RANK = ["Takeover / sale talk", "FDA / trial", "Offering", "Deal / contract", "Buyback", "Earnings", "Analyst upgrade",
        "Analyst downgrade", "In the news", "Analyst note"]
WHY = re.compile(r"what'?s (?:going on|happening)|why is|here'?s why|trading (?:higher|lower)|shares (?:rise|jump|surge|soar|climb|rebound|fall|drop|slide|sink|tumble)|"
                 r"stock is (?:surging|soaring|rising|gaining|falling|sliding)|(?:rebounds?|rall(?:y|ies)|jumps?|surges?|soars?) (?:\d|after|on)", re.I)
NOISE = re.compile(r"inducement|equity awards? to|announces? (?:the )?(?:date|dates|timing)\b|release date|(?:conference|earnings) call\b|webcast|"
                   r"to (?:participate|host|ring)\b|investor (?:conference|day)|annual (?:general )?meeting|declares? (?:a |its )?(?:quarterly |regular )?dividend",
                   re.I)                                # notices, not news (OCUL Nov 6: inducement awards; ACCV / KOPN: a results date)
OPINION = re.compile(r"ahead of (?:its |the )?(?:q\d )?earnings|into earnings|before earnings|earnings preview|is it a buy|should you buy|"
                     r"buy the dip|stocks? to buy|worth buying|time to buy", re.I)   # a view, not an event (NVDA Nov 6: "Ahead of Earnings: Is It a Buy?")
MINOR = ("In the news", "Analyst note")                 # the stock's own, but no event: a sector move stays the label
SUFFIX = re.compile(r"\b(?:inc|incorporated|corp|corporation|co|company|ltd|limited|plc|holdings?|group|n\.?v|s\.?a|se|ag|the|class [a-c])\b\.?", re.I)
GENERIC = {"american", "first", "general", "united", "national", "global", "international", "applied", "advanced", "new", "digital",
           "energy", "data", "power", "western", "eastern", "pacific", "atlantic", "standard", "universal", "community", "capital",
           "financial", "north", "south", "great", "royal", "health", "home", "bank", "life", "american", "us", "china", "world"}


def headlines(syms, t_from, t_to):
    """{SYM: [articles tagged with it]} from Alpaca's news API, accepted in (t_from, t_to]; {} without the keys"""
    key, sec = os.environ.get("ALPACA_KEY_ID"), os.environ.get("ALPACA_SECRET")
    if not (key and sec) or not syms:
        return {}
    hdr = {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": sec}
    z = lambda t: t.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out, syms = {}, sorted(set(syms))
    for i in range(0, len(syms), 100):
        chunk, tok = set(syms[i:i + 100]), None
        for _ in range(40):
            q = {"symbols": ",".join(sorted(chunk)), "start": z(t_from), "end": z(t_to), "limit": 50, "sort": "asc"}
            if tok:
                q["page_token"] = tok
            rq = urllib.request.Request("https://data.alpaca.markets/v1beta1/news?" + urllib.parse.urlencode(q), headers=hdr)
            with urllib.request.urlopen(rq, timeout=30) as r:
                d = json.load(r)
            for n in d.get("news", []):
                for s in set(n.get("symbols") or []) & chunk:
                    out.setdefault(s, []).append(n)
            tok = d.get("next_page_token")
            if not tok:
                break
    print("headlines:", sum(len(v) for v in out.values()), "for", len(out), "of", len(syms), "stocks")
    return out


def mentions(title, sym, name):
    """the headline is about this company: its ticker (2+ letters, as written) or its name's first words"""
    if len(sym) >= 2 and re.search(rf"(?<![A-Za-z]){re.escape(sym)}(?![A-Za-z])", title):
        return True
    w = SUFFIX.sub(" ", re.sub(r"[,.()]", " ", name or "")).split()
    keys = ([" ".join(w[:2])] if len(w) >= 2 else []) + ([w[0]] if w and len(w[0]) >= 4 and w[0].lower() not in GENERIC else [])
    return any(re.search(rf"(?<![A-Za-z]){re.escape(k)}(?![A-Za-z])", title, re.I) for k in keys)


def best_headline(sym, name, arts):
    """its own headline (not a list of movers), the biggest kind of event first, the earliest of that kind (the release
    before the "why is it moving" pieces) -> {kind, title, source, at, url} or None"""
    got = []
    for n in arts:
        t = (n.get("headline") or "").strip()
        if not t or LIST_ART.search(t) or NOISE.search(t) or not mentions(t, sym, name):
            continue
        kind = "In the news" if OPINION.search(t) else next((k for k, rx in KINDS if re.search(rx, t, re.I)), "In the news")
        got.append((RANK.index(kind), n.get("created_at") or "", kind, t, n))
    if not got:
        return None
    # an event: the earliest (the release, not the follow-ups); a minor item: a "why is it moving" piece first, the newest
    # (AMD Nov 6: "AMD Shares Rebound 7% Premarket After 17% Rout", not last night's "CEO addresses AI concerns")
    key = lambda x: (x[0], x[1]) if x[2] not in MINOR else (x[0], not WHY.search(x[3]), -datetime.datetime.fromisoformat(x[1].replace("Z", "+00:00")).timestamp())
    _, at, kind, t, n = min(got, key=key)
    when = datetime.datetime.fromisoformat(at.replace("Z", "+00:00")).astimezone(NY)
    return {"kind": kind, "title": t, "source": (n.get("source") or "news").capitalize(), "url": n.get("url") or "",
            "at": when.strftime("%-I:%M %p").replace("AM", "AM ET").replace("PM", "PM ET") if when.date() == datetime.datetime.now(NY).date()
            else when.strftime("%b %-d %-I:%M %p ET")}


def use_headlines(allr, H, S):
    """each gapper's own headline goes on its row ("headline"); when the SEC had nothing of its own (weak news) and the
    headline is an event (a deal, a sale, an FDA item, a buyback, an offering, earnings, an analyst up/downgrade), the
    headline is the catalyst; the news grade stays C (no primary source in the filing yet: the safety lock's rule)"""
    n = 0
    for sym, r in allr.items():
        hl = best_headline(sym, (S.get(sym) or {}).get("name"), H.get(sym) or [])
        if not hl:
            continue
        r["headline"] = hl
        if weak_news(r) and hl["kind"] not in MINOR:
            sec = "" if r["catalyst"] == "No company news" else f"; SEC: {r['catalyst']}: {r['reason'][:100]}"
            r.update(catalyst=hl["kind"] + " (headline)", reason=f"{hl['title']} ({hl['source']} {hl['at']})" + sec,
                     sources=[hl["url"]] + (r.get("sources") or [])[:2],
                     flags="; ".join(x for x in (r.get("flags"), "headline only: no SEC filing on it yet") if x))
            n += 1
    print("headlines used as the catalyst:", n)


def sector_moves(out, news, every, S):
    """a gap with no news of its own today (none, a routine filing, earnings before the last close, a board change: news
    C), while 3+ stocks of its theme (with nothing at all: or of its industry), itself included, gap 5%+ the same way:
    "Sector move: <group>", the biggest peers named, those with their own news, then its own item (the user, Nov 6 2026:
    ~60 chip and AI-hardware names up 5-20%). Only the catalyst and the reason change, the news grade stays C."""
    allr = {**news, **out}                              # the same dicts: the changes land in both
    side = {g["symbol"]: g["direction"] for g in every}
    for sym, r in out.items():
        side.setdefault(sym, r["direction"])
    themes = lambda sym: [t.strip() for t in str((S.get(sym) or {}).get("themes") or "").split(" | ") if t.strip()]
    inds = lambda sym: [S[sym]["industry"]] if (S.get(sym) or {}).get("industry") else []
    members = {}
    for sym, d in side.items():
        for t in themes(sym) + inds(sym):
            members.setdefault((t, d), []).append(sym)
    weak = weak_news
    own = {s: r["catalyst"] for s, r in allr.items() if not weak(r)}
    for sym, r in allr.items():
        if not weak(r):
            continue
        nothing = r["catalyst"] in ("No company news", "Not at the SEC")
        best = None                                     # its theme with the most such gappers (the portal's groups: CRWV
        for cands in (themes(sym), inds(sym) if nothing else []):   # Neoclouds, not Software); its industry only when
            m = max(((t, members.get((t, r["direction"]), [])) for t in cands), key=lambda x: len(x[1]), default=None)   # it has
            if m and len(m[1]) >= 3:                    # nothing of its own (VCEL: "After earnings", not "Biotechnology")
                best = m
                break
        if not best:
            continue
        t, mem = best
        peers = sorted((s for s in mem if s != sym), key=lambda s: -((S.get(s) or {}).get("mcap_b") or 0))   # the best-known first
        newsy = [s for s in peers if s in own]
        mine = ("; " + r["reason"][:1].lower() + r["reason"][1:] if r["catalyst"] == "No company news" else
                "; not at the SEC (no filings to check)" if r["catalyst"] == "Not at the SEC" else
                f"; its own: {r['catalyst']}: {r['reason'][:140]}")      # AMD Nov 6: its Nov 3 report, MU a board retirement
        hl = r.get("headline")
        r["catalyst"] = "Sector move: " + t
        r["reason"] = (f"{len(mem)} {t} stocks gapping {r['direction']} 5%+ ({', '.join(peers[:6])}{', ...' if len(peers) > 6 else ''})" +
                       (f"; with their own news: {', '.join(f'{s} ({own[s]})' for s in newsy[:3])}" if newsy else "") +
                       (f"; headline: {hl['title']} ({hl['source']} {hl['at']})" if hl else "") + mine)
        if hl:
            r["sources"] = [hl["url"]] + [u for u in r.get("sources") or [] if u != hl["url"]][:2]
    for r in allr.values():                             # no group either: its headline, minor as it is (AMD-type explainers)
        hl = r.get("headline")
        if hl and weak(r) and r["catalyst"] in ("No company news", "Not at the SEC"):
            r.update(catalyst=hl["kind"] + " (headline)", reason=f"{hl['title']} ({hl['source']} {hl['at']}); " + r["reason"][:1].lower() + r["reason"][1:],
                     sources=[hl["url"]] + (r.get("sources") or [])[:2])


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
                   "chart": r["chart"], "catalyst": r["catalyst"], "pm_last": r.get("pm_last"), "claude": r.get("claude"), "built_at": cg["built_at"],
                   "star": r.get("star"), "trend": r.get("trend"), "group_tier": r.get("group_tier"), "stage": r.get("stage"),
                   "event": r.get("event"), "eligible": r.get("eligible")}
    json.dump(sorted(keep.values(), key=lambda e: e["key"]), open(log_path, "w"), separators=(",", ":"))
    print(len(keep), "log entries")


if __name__ == "__main__":
    if sys.argv[1] == "log":
        log(sys.argv[2], sys.argv[3])
    elif sys.argv[1] in ("live", "news"):              # news = the early runs: no grades, pmnews.json
        a = [x for x in sys.argv[2:] if not x.startswith("--asof=")]
        asof = next((x.split("=", 1)[1] for x in sys.argv if x.startswith("--asof=")), None)
        live(a[0], a[1], a[2], a[3], asof, grade=sys.argv[1] == "live")
