#!/usr/bin/env python3
"""Event links: when a bellwether reports, which stocks are tied to it, why, and what the bellwether itself said about them.

  python3 radar/event.py build  <bellwethers.json> <earnings.json> <stocks.json> <out events.json> [previous events.json]
  python3 radar/event.py replay <bellwethers.json> <stocks.json> <out> SYM YYYY-MM-DD|prev   (a past report, read again)

The user, Nov 17 2026 (NVDA's report): "it has major implications for all companies depend on nvda ... our code should be
able to connect dots"; "logic and rationale should be accurate linking"; "reason of alert has to be clear explanation ...
price and volume makes me decide, new direct link, fundamental news helps conviction". By code, no Claude:
  the links   radar/bellwethers.json: every linked stock written out with its tier (direct tie / one step away / rival / same
              spending) and the reason. A stock without an entry has no link and gets no reason.
  the event   the bellwether is on the Earnings tab (earnings.json): the event runs from the morning of its report to 8 PM ET
              of the reaction session (a report after the close: the next session).
  what it     its own words, quoted: the results filing at the SEC (8-K item 2.02): every exhibit, so NVIDIA's press release
  said        AND its CFO commentary. Each topic of the map (networking, the AI clouds, supply, power ...) keeps the 2
              sentences that say most about it (the topic's words, a number, a change). No sentence = "nothing in the
              release". The earnings call itself is not on the SEC and no free source carries it: the news feed's headlines
              about the bellwether since the report (Alpaca / Benzinga, which carry the call's main remarks) are matched to
              the same topics and shown as "heard", marked as a headline, not a quote.
  the moves   Yahoo quotes of every linked stock (after hours on the evening, pre-market, live); the page refreshes them
              from its own pre-market / live files.
  the reason  for each linked stock one line: the event and its result, the stock's tie, the bellwether's sentence about that
              tie. radar/alerts.py puts it on that stock's alerts during the reaction session ("why:"); the Pre-market
              tab's Event card shows all of it.
"""
import concurrent.futures as cf, datetime, html, json, os, re, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import earnings as E  # noqa: E402

NY = E.NY
GV = 2                       # the reader's version: a change re-reads the filing
TIERS = ["direct", "rival", "step", "spend"]
TIER_WORDS = {"direct": "direct tie", "step": "one step away", "rival": "rival", "spend": "same spending, no tie"}
BOILER = re.compile(r"forward-looking|risks and uncertainties|non-gaap (financial )?measures?|conference call|webcast|safe harbor|"
                    r"trademarks?|copyright|reconciliation|investor relations|for (more|further) information|press releases?|"
                    r"undue reliance|no obligation to update|form 10-[kq]|\bsec\b filings", re.I)
CUT = re.compile(r"CONDENSED CONSOLIDATED|About NVIDIA|Certain statements in this|Non-GAAP Measures|Safe Harbor", re.I)
CHANGE = re.compile(r"\b(record|grew|growth|up \d|down \d|increase[ds]?|decrease[ds]?|declined?|driven by|ramp|doubl|tripl|"
                    r"expect(s|ed)?|strong|surpass|exceed|accelerat|sold out|constrain|commitments (increased|were|of)|arriving|in (full )?production|"
                    r"announced|revealed|launched|unveiled|expanded|partner)", re.I)
MIN_SCORE = 3                # a sentence needs one of the topic's strong words (or three weak ones) to be quoted
CALLISH = re.compile(r"\b(says?|said|sees?|expects?|ceo|cfo|call|guid|outlook|forecast|demand|orders?|backlog)\b", re.I)


def money(v):
    if v is None:
        return "?"
    return f"${v / 1e9:.1f}B" if abs(v) >= 1e9 else f"${v / 1e6:.0f}M"


def next_session(d):
    d = datetime.date.fromisoformat(d) if isinstance(d, str) else d
    while True:
        d += datetime.timedelta(days=1)
        if E.trading(d):
            return d.isoformat()


def window(row):
    """(start, end, reaction day): from the morning of the report to 8 PM ET of the session that reacts to it"""
    react = row["date"] if row.get("when") == "bmo" else next_session(row["date"])
    return row["date"] + "T00:00", react + "T20:00", react


def when_words(row):
    d = datetime.date.fromisoformat(row["date"])
    w = {"bmo": "before the open", "amc": "after the close"}.get(row.get("when"), "")
    return f"{d:%a %b} {d.day}" + (" " + w if w else "")


# ───────── the filing: every exhibit of the results 8-K ─────────
def clean(raw):
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    t = re.sub(r"(?i)</(p|li|div|tr|h[1-6]|table)>|<br\s*/?>", " ¶ ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"[ \t\r\n\xa0]+", " ", html.unescape(t)).strip()


def filing_docs(sec, sym, day_from, day_to):
    """the results filing (8-K item 2.02, or a 6-K) accepted between the two days (ISO): {filed, docs: [{url, kind, text}]}"""
    c = sec.cik.get(sym.upper())
    if not c:
        return None
    sub = json.loads(E.retry(lambda: E.http(f"https://data.sec.gov/submissions/CIK{c:010d}.json", E.SEC_UA)))
    f = sub["filings"]["recent"]
    for i, form in enumerate(f["form"]):
        if form not in ("8-K", "6-K") or (form == "8-K" and "2.02" not in (f["items"][i] or "")):
            continue
        acc_t = datetime.datetime.fromisoformat(f["acceptanceDateTime"][i].replace("Z", "+00:00")).astimezone(NY)
        d = acc_t.date().isoformat()
        if d > day_to:
            continue
        if d < day_from:
            return None
        base = f"https://www.sec.gov/Archives/edgar/data/{c}/{f['accessionNumber'][i].replace('-', '')}/"
        names = [x["name"] for x in json.loads(E.retry(lambda: E.http(base + "index.json", E.SEC_UA)))["directory"]["item"]]
        htm = [n for n in names if n.lower().endswith((".htm", ".html")) and "index" not in n.lower() and n != f["primaryDocument"][i]
               and not re.match(r"R\d+\.htm", n)]                 # R1.htm ...: the filing's data pages, not a document
        docs = []
        for n in htm[:6]:
            time.sleep(0.2)
            try:
                txt = clean(E.http(base + n, E.SEC_UA).decode("utf-8", "replace"))
            except Exception:
                continue
            if len(txt) < 1500:
                continue
            kind = ("supplemental data" if "supplement" in n.lower() else "CFO commentary" if re.search(r"CFO Commentary", txt[:800], re.I)
                    else "press release")
            docs.append({"url": base + n, "kind": kind, "text": txt})
        return {"filed": acc_t.isoformat(timespec="minutes"), "docs": docs}
    return None


def sentences(text):
    m = CUT.search(text, 1500)
    body = text[:m.start()] if m else text
    out = []
    for part in re.split(r"\s*¶\s*", body):
        for s in re.split(r"(?<=[a-z0-9%\)”\"])[.!?]\s+(?=[A-Z“\"$])", part):
            s = s.strip(" ·•-–—")
            if not (50 <= len(s) <= 460) or BOILER.search(s):
                continue
            if sum(ch.isalpha() or ch == " " for ch in s) < 0.72 * len(s):       # a table row, not a sentence
                continue
            out.append(s if s[-1] in ".!?" else s + ".")
    return out


def short(s, n=300):
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0].rstrip(",;:") + " …"


def said_for(docs, topics):
    """{topic: [{text, src, url}]}: the bellwether's own sentences that say most about each topic, at most 2"""
    pool = []
    for d in docs:
        for k, s in enumerate(sentences(d["text"])):
            pool.append((s, d["kind"], d["url"], k))
    out = {}
    for t, spec in topics.items():
        pats = [(re.compile(p, re.I), 3) for p in spec["find"]] + [(re.compile(p, re.I), 1) for p in spec.get("also") or []]
        cand = []
        for s, kind, url, k in pool:
            hits = [w for p, w in pats if p.search(s)]
            if sum(hits) < MIN_SCORE:
                continue
            sc = sum(hits) + (2 if re.search(r"\$\s?\d|\d\s?%|\d (billion|million)", s) else 0) \
                + (1 if CHANGE.search(s) else 0) + (0.5 if kind == "CFO commentary" else 0) - (2 if len(s) > 320 else 0) - k / 2000
            cand.append((sc, s, kind, url))
        cand.sort(key=lambda x: -x[0])
        keep, seen = [], set()
        for sc, s, kind, url in cand:
            key = re.sub(r"\W+", "", s.lower())[:50]
            if key in seen:
                continue
            seen.add(key)
            keep.append({"text": short(s), "src": kind, "url": url})
            if len(keep) == 2:
                break
        if keep:
            out[t] = keep
    return out


def named_for(docs, names, relevant=None):
    """{sym: {text, src, url}}: the report's sentence that names the linked company itself (the strongest reason); only a
    sentence about the business the link is about (the map's 'relevant' words: a line on laptops is no reason for Dell's
    AI servers)"""
    out = {}
    rel = re.compile(relevant, re.I) if relevant else None
    pool = [(s, d["kind"], d["url"]) for d in docs for s in sentences(d["text"]) if not rel or rel.search(s)]
    for sym, pat in (names or {}).items():
        p = re.compile(r"(?<![A-Za-z])(" + pat + r")(?![A-Za-z])")
        cand = [(2 * bool(re.search(r"\$\s?\d|\d\s?%|\d (billion|million)", s)) + bool(CHANGE.search(s)) - len(s) / 400, s, kind, url)
                for s, kind, url in pool if p.search(s)]
        if cand:
            _, s, kind, url = max(cand)
            out[sym] = {"text": short(s, 380), "src": kind, "url": url, "topic": "named"}
    return out


def heard_for(arts, topics, since):
    """{topic: [{text, src, url}]} from the news feed's headlines about the bellwether since the report, at most 2 a topic"""
    out = {}
    ts = lambda n: datetime.datetime.fromisoformat(str(n.get("created_at") or "1970-01-01T00:00:00Z").replace("Z", "+00:00")).astimezone(NY)
    A = [n for n in arts if ts(n).isoformat() >= since and len(n.get("symbols") or []) <= 4 and n.get("headline")]
    for t, spec in topics.items():
        pats = [re.compile(p, re.I) for p in spec["find"] + (spec.get("also") or [])]
        cand = []
        for n in A:
            hl = html.unescape(n["headline"])
            hits = sum(1 for p in pats if p.search(hl))
            if hits:
                cand.append((hits + (2 if CALLISH.search(hl) else 0), ts(n), hl, n))
        cand.sort(key=lambda x: (-x[0], x[1]))
        keep, seen = [], set()
        for _, tm, hl, n in cand:
            key = re.sub(r"\W+", "", hl.lower())[:40]
            if key in seen:
                continue
            seen.add(key)
            keep.append({"text": short(hl, 220), "src": f"{n.get('source') or 'news'} {tm:%b} {tm.day} {tm:%H:%M} ET", "url": n.get("url") or ""})
            if len(keep) == 2:
                break
        if keep:
            out[t] = keep
    return out


# ───────── the result, the moves ─────────
def result_line(r):
    p = []
    if r.get("rev_act"):
        s = "revenue " + money(r["rev_act"])
        if r.get("rev_est"):
            s += f" vs {money(r['rev_est'])} est"
            if r.get("rev_surprise") is not None:
                s += f" ({r['rev_surprise']:+.1f}%)"
        if r.get("rev_growth") is not None:
            s += f", {r['rev_growth']:+.0f}% y/y"
        p.append(s)
    if r.get("eps_act") is not None:
        p.append(f"EPS {r['eps_act']:.2f}" + (f" vs {r['eps_est']:.2f} est" if r.get("eps_est") is not None else ""))
    g = r.get("guide") or {}
    if g.get("mid"):
        p.append(("next quarter's" if g.get("kind") == "q" else "the year's") + " revenue guide " + money(g["mid"])
                 + (f" ({g['vs_street']:+.1f}% vs the street)" if g.get("vs_street") is not None else ""))
    elif g.get("dir") in ("raised", "lowered", "reaffirmed"):
        p.append("guidance " + g["dir"])
    return "; ".join(p)


OUTLOOK = [re.compile(r"expected to be (?:between |in the range of )?\$\s?(\d[\d,.]*)\s*(billion|million)?\s*(?:and|to|-|–)\s*\$?\s?(\d[\d,.]*)\s*(billion|million)", re.I),
           re.compile(r"(?:revenue|net sales)[^.]{0,60}in the range of \$\s?(\d[\d,.]*)\s*(billion|million)?\s*(?:and|to|-|–)\s*\$?\s?(\d[\d,.]*)\s*(billion|million)", re.I),
           re.compile(r"expected to be \$\s?(\d[\d,.]*)\s*(billion|million)", re.I)]


def outlook_mid(text):
    """the midpoint, in dollars, of a revenue outlook sentence ('$130.0 billion, plus or minus 3%', 'between $206.0 billion
    and $213.0 billion', 'in the range of $56-59 billion')"""
    u = lambda x: 1e9 if (x or "").lower() == "billion" else 1e6
    for k, p in enumerate(OUTLOOK):
        g = p.search(text or "")
        if not g:
            continue
        if k == 2:
            return float(g.group(1).replace(",", "")) * u(g.group(2))
        a, b = float(g.group(1).replace(",", "")), float(g.group(3).replace(",", ""))
        return (a * u(g.group(2) or g.group(4)) + b * u(g.group(4))) / 2
    return None


def own_words(said, row, lead=("datacenter", "outlook"), n=2):
    """the result in the bellwether's own sentences: the first sentence of each of its lead topics (the map's "lead": NVIDIA
    Data Center revenue and the outlook; a cloud giant its capital spending and its cloud), the outlook's $ figure
    against the saved estimate"""
    p = []
    for t in lead:
        if said.get(t) and len(p) < n:
            x = short(said[t][0]["text"], 200).rstrip(".")
            if t == "outlook":
                v, est = outlook_mid(said[t][0]["text"]), (row.get("nq") or {}).get("rev")
                if v and est and 0.5 < v / est < 2:
                    x += f" ({(v / est - 1) * 100:+.1f}% vs the {money(est)} estimate)"
            if x not in p:
                p.append(x)
    return "; ".join(p)


def lead_words(m, said, row):
    """the Earnings tab's reading (revenue, EPS, guide vs the estimates) with the bellwether's key sentence; before the tab
    has read the report, its own sentences alone"""
    lead = tuple(m.get("lead") or ("datacenter", "outlook"))
    res = result_line(row)
    if not res:
        return own_words(said, row, lead)
    key = own_words(said, row, lead[:1], 1)
    return res + ("; " + key if key else "")


def quote_move(q, now):
    """(move %, kind, price) the way the Earnings tab reads a quote: pre-market, live, after hours, else the close"""
    st = q.get("marketState") or ""
    reg, prv = q.get("regularMarketPrice"), q.get("regularMarketPreviousClose")
    pre, post = q.get("preMarketPrice"), q.get("postMarketPrice")
    pre_t, post_t, reg_t = q.get("preMarketTime") or 0, q.get("postMarketTime") or 0, q.get("regularMarketTime") or 0
    if st == "PRE" or (st in ("PREPRE", "CLOSED") and pre and pre_t > reg_t and now.hour < 10):
        px, kind, ref = pre, "pre-market", reg
    elif st == "REGULAR":
        px, kind, ref = reg, "live", prv
    elif post and post_t > reg_t:
        px, kind, ref = post, "after hours", reg
    else:
        px, kind, ref = reg, "close", prv
    if not (px and ref):
        return None
    return [round((px / ref - 1) * 100, 2), kind, round(px, 4)]


def assemble(B, m, row, S, said, heard, mv, status, named=None, first=("direct", "rival")):
    """the event: its links (theme by theme, each stock with tier, reason and move), and the one-line reasons"""
    res = lead_words(m, said, row) if status == "out" else ""
    bm = mv.get(B)
    head = f"{B} earnings ({when_words(row)})"
    lead = head + (": " + res if res else " are out" if status != "due" else "")
    if bm and status != "due":
        lead += f"; {B} {bm[0]:+.1f}% {bm[1]}"
    links, best, themes = [], {}, {}
    for L in m["links"]:
        qs = [dict(x, topic=m["topics"][t]["label"]) for t in L["topics"] for x in (said.get(t) or [])[:1]][:2]
        hs = [dict(x, topic=m["topics"][t]["label"]) for t in L["topics"] for x in (heard.get(t) or [])[:1]][:2]
        st = []
        for sym, v in L["stocks"].items():
            tier, why = v[0], v[1]
            if sym not in S or tier not in first:              # the 1st impact only (the user, Nov 17 2026)
                continue
            tp = v[2] if len(v) > 2 else L["topics"]           # the stock's own topics, else the theme's
            q1 = [dict(x, topic=m["topics"][t]["label"]) for t in tp for x in (said.get(t) or [])[:1]][:1] if len(v) > 2 else qs
            h1 = [dict(x, topic=m["topics"][t]["label"]) for t in tp for x in (heard.get(t) or [])[:1]][:1] if len(v) > 2 else hs
            st.append({"sym": sym, "tier": tier, "why": why, "mv": mv.get(sym), "named": (named or {}).get(sym),
                       "said": q1[:1] if len(v) > 2 else None})
            if sym not in best or TIERS.index(tier) < TIERS.index(best[sym][0]):
                best[sym] = (tier, why, {"topics": tp}, q1, h1)
        st.sort(key=lambda x: TIERS.index(x["tier"]))
        if not st:
            continue
        links.append({"theme": L["theme"], "why": L["why"], "topics": [m["topics"][t]["label"] for t in L["topics"]],
                      "said": qs, "heard": hs, "stocks": st})
        if status != "due":
            themes[L["theme"]] = lead + ". " + L["why"] + said_words(m["name"], qs, hs, m["topics"][L["topics"][0]]["label"])
    alerts = {}
    if status != "due":
        for sym, (tier, why, L, qs, hs) in best.items():
            nm = (named or {}).get(sym)
            alerts[sym] = f"{lead}. {sym}, {TIER_WORDS[tier]}: {why}" + (
                f" {m['name']} named it in its report: “{short(nm['text'], 260)}” ({nm['src']})" if nm
                else said_words(m["name"], qs, hs, m["topics"][L["topics"][0]]["label"]))
    return links, alerts, themes, lead


def said_words(name, qs, hs, label):
    if qs:
        q = qs[0]
        return f" {name} on {q['topic']}: “{short(q['text'], 240)}” ({q['src']})"
    if hs:
        return f" Heard on {hs[0]['topic']}: {hs[0]['text']} ({hs[0]['src']}, a headline)"
    return f" {name}'s release says nothing on {label}."


def yahoo_moves(syms, now, errors):
    try:
        y = E.Y()
        Q = y.quotes([s.replace(".", "-") for s in syms])
    except (Exception, SystemExit) as e:
        errors.append(f"quotes: {e!r}"[:160])
        return {}
    out = {}
    for s in syms:
        q = Q.get(s.replace(".", "-"))
        mv = quote_move(q, now) if q else None
        if mv:
            out[s] = mv
    return out


def own_rows(bw, rows, prev, now, errors, force=()):
    """a row like the Earnings tab's for each bellwether the tab doesn't carry (your Earnings rules leave MSFT and GOOGL out:
    ADR under 3%): the report day and time from Yahoo, the estimates saved before the report (Yahoo moves on after it), then
    the release read with the tab's own reader (revenue, EPS, guidance). Kept in events.json ("own_rows") from 10 days before
    the report to the end of its reaction session. A results filing accepted today sets the day whatever Yahoo's date says"""
    need = [b for b in bw["bellwethers"] if b not in rows or b in force]
    old = {k: v for k, v in ((prev or {}).get("own_rows") or {}).items() if k in need and now.isoformat()[:16] <= window(v)[1]}
    if not need:
        return {}
    out, today, sec = dict(old), now.date().isoformat(), None
    try:
        y = E.Y()
        Q = y.quotes([b.replace(".", "-") for b in need])
    except (Exception, SystemExit) as e:
        errors.append(f"own rows, quotes: {e!r}"[:160])
        return out
    for b in need:
        r = out.get(b)
        if not r and b in force and b in rows:                 # the test: the tab's day and time, none of its reading
            r = out[b] = dict({k: rows[b].get(k) for k in ("sym", "date", "when", "time", "report_at", "nq", "rev_est", "eps_est", "rev_yago")}, own=True)
        if not r:
            ts = (Q.get(b.replace(".", "-")) or {}).get("earningsTimestamp")
            if not ts:
                continue
            t = datetime.datetime.fromtimestamp(ts, NY)
            if not (-1 <= (t.date() - now.date()).days <= 10):
                continue
            w = "bmo" if t.hour < 12 else "amc" if t.hour >= 15 else "dmh"
            r = out[b] = {"sym": b, "own": True, "date": t.date().isoformat(), "when": w, "time": t.strftime("%H:%M"),
                          "report_at": t.date().isoformat() + ("T07:00" if w == "bmo" else "T16:00" if w == "amc" else "T12:00")}
        try:
            if not r.get("est_frozen") and now.isoformat() < r["report_at"]:
                hist, trend = y.summary(b.replace(".", "-"))
                t0 = trend.get("0q") or {}
                r.update(eps_est=t0.get("eps"), eps_yago=t0.get("eps_yago"), rev_est=t0.get("rev"), rev_yago=t0.get("rev_yago"),
                         nq=trend.get("+1q"), fy=trend.get("0y"), est_at=now.isoformat(timespec="minutes"))
            if not r.get("rel_url") and r["date"] >= today or (not r.get("rel_url") and now.isoformat() >= r["report_at"]):
                sec = sec or E.SEC()
                rel = sec.release(b, today if r["date"] > today else r["date"])
                time.sleep(0.2)
                if rel:
                    ft = datetime.datetime.fromisoformat(rel["filed"])
                    if ft.date().isoformat() != r["date"]:                  # out on another day than Yahoo's date
                        w = "bmo" if ft.hour < 12 else "amc" if ft.hour >= 15 else "dmh"
                        r.update(date=ft.date().isoformat(), when=w, report_at=rel["filed"][:16])
                    E.use_release(r, rel)
                    if r.get("rel_eps") is not None:
                        r["eps_act"] = r["rel_eps"]
                    r["rev_surprise"], r["rev_growth"] = E.pct(r.get("rev_act"), r.get("rev_est")), E.pct(r.get("rev_act"), r.get("rev_yago"))
                    r.pop("headline", None)
        except (Exception, SystemExit) as e:
            errors.append(f"own row {b}: {e!r}"[:160])
    return out


def build(bw, earn, S, prev, now, force=()):
    rows = {r["sym"]: r for r in earn.get("rows", [])}
    pv = {e["id"]: e for e in (prev or {}).get("events", [])}
    errors, events, sec = [], [], None
    own = own_rows(bw, rows, prev, now, errors, force)
    rows.update(own)
    for B, m in bw["bellwethers"].items():
        row = rows.get(B)
        if not row or not row.get("report_at"):
            continue
        start, end, react = window(row)
        if not (start <= now.isoformat()[:16] <= end):
            continue
        eid = f"{B}:{row['date']}"
        status = "due" if now.isoformat() < row["report_at"] else "out" if (row.get("reported") or row.get("rel_url")) else "waiting"
        said, heard, docs, filed, named, feed_n = {}, {}, [], None, {}, None
        old = pv.get(eid) or {}
        if status != "due":
            if old.get("gv") == GV and len(old.get("docs") or []) >= 2:
                said, docs, filed, named = old.get("said_all") or {}, old["docs"], old.get("filed"), old.get("named") or {}
            else:
                try:
                    sec = sec or E.SEC()
                    fd = filing_docs(sec, B, row["date"], next_session(row["date"]))
                    if fd and fd["docs"]:
                        said, named = said_for(fd["docs"], m["topics"]), named_for(fd["docs"], m.get("names"), m.get("relevant"))
                        docs, filed = [{"url": d["url"], "kind": d["kind"]} for d in fd["docs"]], fd["filed"]
                except Exception as e:
                    errors.append(f"sec {B}: {e!r}"[:160])
                    said, docs, filed, named = old.get("said_all") or {}, old.get("docs") or [], old.get("filed"), old.get("named") or {}
            try:
                arts = E.feed([B], datetime.datetime.fromisoformat(row["report_at"]).replace(tzinfo=NY), now).get(B, [])
                heard = heard_for(arts, m["topics"], datetime.datetime.fromisoformat(row["report_at"]).replace(tzinfo=NY).isoformat())
                feed_n = len(arts)
            except Exception as e:
                errors.append(f"news feed {B}: {e!r}"[:160])
                heard = old.get("heard_all") or {}
            if docs and status == "waiting":
                status = "out"
        first = tuple(bw.get("first") or ("direct", "rival"))
        linked = sorted({s for L in m["links"] for s, v in L["stocks"].items() if s in S and v[0] in first})
        mv = yahoo_moves([B] + linked, now, errors)
        if not mv and old.get("moves"):
            mv = old["moves"]
        links, alerts, themes, lead = assemble(B, m, row, S, said, heard, mv, status, named, first)
        events.append({"id": eid, "gv": GV, "sym": B, "name": m["name"], "kind": "earnings", "date": row["date"], "when": row.get("when"),
                       "when_words": when_words(row), "react_day": react, "status": status, "what": m["what"], "lead": lead,
                       "result": lead_words(m, said, row) if status == "out" else "", "read": row.get("read") if status == "out" else None,
                       "filed": filed, "docs": docs, "said_all": said, "named": named, "heard_all": heard, "feed_n": feed_n, "own_row": bool(row.get("own")),
                       "moves": mv, "moves_at": now.isoformat(timespec="minutes"),
                       "links": links, "alerts": alerts, "themes": themes})
    return {"built_at": now.isoformat(timespec="seconds"), "tiers": bw.get("tiers") or {}, "events": events, "own_rows": own, "errors": errors[:20]}


# ───────── a past report read again (the test of the reader and of the links) ─────────
def daily(y, sym, d0, d1):
    p1 = int(datetime.datetime.combine(d0, datetime.time(), NY).timestamp())
    p2 = int(datetime.datetime.combine(d1, datetime.time(), NY).timestamp())
    j = y.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym.replace('.', '-'))}?period1={p1}&period2={p2}&interval=1d")
    r = j["chart"]["result"][0]
    q = ((r.get("indicators") or {}).get("quote") or [{}])[0]
    return [(datetime.datetime.fromtimestamp(t, NY).date().isoformat(), o, c) for t, o, c in
            zip(r.get("timestamp") or [], q.get("open") or [], q.get("close") or []) if o and c]


def replay(bw, S, B, day):
    m = bw["bellwethers"][B]
    errors = []
    sec = E.SEC()
    if day == "prev":                      # the newest results filing more than a week old: the report before this one
        fd = filing_docs(sec, B, "1900-01-01", (datetime.datetime.now(NY).date() - datetime.timedelta(days=7)).isoformat())
    else:
        fd = filing_docs(sec, B, day, next_session(day))
    if not fd:
        return {"built_at": datetime.datetime.now(NY).isoformat(timespec="seconds"), "events": [], "errors": [f"no results filing of {B} on {day}"]}
    filed = datetime.datetime.fromisoformat(fd["filed"])
    amc = filed.hour >= 15
    row = {"date": filed.date().isoformat(), "when": "amc" if amc else "bmo", "report_at": fd["filed"][:16]}
    react = window(row)[2]
    said, named = said_for(fd["docs"], m["topics"]), named_for(fd["docs"], m.get("names"), m.get("relevant"))
    first = tuple(bw.get("first") or ("direct", "rival"))
    linked = sorted({s for L in m["links"] for s, v in L["stocks"].items() if s in S and v[0] in first})
    mv = {}
    try:
        y = E.Y()
        rd = datetime.date.fromisoformat(react)

        def one(s):
            try:
                bars = daily(y, s, rd - datetime.timedelta(days=8), rd + datetime.timedelta(days=1))
                i = next(k for k, b in enumerate(bars) if b[0] == react)
                pc = bars[i - 1][2]
                return s, [round((bars[i][2] / pc - 1) * 100, 2), "that session, close to close", round(bars[i][2], 4), round((bars[i][1] / pc - 1) * 100, 2)]
            except Exception:
                return s, None
        with cf.ThreadPoolExecutor(6) as ex:
            mv = {s: v for s, v in ex.map(one, [B] + linked) if v}
    except (Exception, SystemExit) as e:
        errors.append(f"bars: {e!r}"[:160])
    links, alerts, themes, lead = assemble(B, m, row, S, said, {}, mv, "out", named, first)
    head = next((d["text"][:500] for d in fd["docs"] if d["kind"] == "press release"), "")
    ev = {"id": f"{B}:{row['date']}", "gv": GV, "sym": B, "name": m["name"], "kind": "earnings", "date": row["date"], "when": row["when"],
          "when_words": when_words(row), "react_day": react, "status": "out", "replay": True, "what": m["what"], "lead": lead, "result": lead_words(m, said, row),
          "headline": head, "filed": fd["filed"], "docs": [{"url": d["url"], "kind": d["kind"], "chars": len(d["text"]), "sentences": len(sentences(d["text"]))} for d in fd["docs"]],
          "said_all": said, "named": named, "heard_all": {}, "moves": mv, "links": links, "alerts": alerts, "themes": themes}
    return {"built_at": datetime.datetime.now(NY).isoformat(timespec="seconds"), "tiers": bw.get("tiers") or {}, "events": [ev], "errors": errors}


def main():
    mode = sys.argv[1]
    bw = json.load(open(sys.argv[2]))
    if mode == "build":
        earn, S = json.load(open(sys.argv[3])), {s["symbol"]: s for s in json.load(open(sys.argv[4]))}
        prev = None
        rest = [a for a in sys.argv[6:] if not a.startswith("--")]
        if rest:
            try:
                prev = json.load(open(rest[0]))
            except Exception:
                prev = None
        force = tuple(a[6:].upper() for a in sys.argv if a.startswith("--own="))     # a test: read this one without the Earnings tab's row
        out = build(bw, earn, S, prev, datetime.datetime.now(NY), force)
        json.dump(out, open(sys.argv[5], "w"), separators=(",", ":"))
    else:                                    # replay <map> <stocks> <out> SYM DAY|prev [SYM DAY|prev ...]
        S = {s["symbol"]: s for s in json.load(open(sys.argv[3]))}
        out = {"built_at": datetime.datetime.now(NY).isoformat(timespec="seconds"), "tiers": bw.get("tiers") or {}, "events": [], "errors": []}
        a = sys.argv[5:]
        for k in range(0, len(a) - 1, 2):
            try:
                o = replay(bw, S, a[k].upper(), a[k + 1])
                out["events"] += o["events"]; out["errors"] += o["errors"]
            except (Exception, SystemExit) as e:
                out["errors"].append(f"{a[k]}: {e!r}"[:200])
        json.dump(out, open(sys.argv[4], "w"), separators=(",", ":"))
    for e in out["events"]:
        print(e["id"], e["status"], "| docs", len(e["docs"]), "| topics said", sorted(e["said_all"]), "| heard", sorted(e["heard_all"]),
              "| linked stocks", len(e["alerts"]) or sum(len(L["stocks"]) for L in e["links"]), "| moves", len(e["moves"]))
    if not out["events"]:
        print("no event now")
    for x in out["errors"]:
        print("error:", x)


if __name__ == "__main__":
    main()
