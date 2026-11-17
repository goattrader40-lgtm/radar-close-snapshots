#!/usr/bin/env python3
"""A probe (test only, nothing live reads it): can the direct links of a bellwether be built by code, from SEC filings?

  python3 radar/probe_links.py <stocks.json> <out probe_links.json> SYM [SYM ...]

The user, Nov 17 2026: "big bellwethers maps, for their suppliers and connectivity vendors ... kind of algorithmic ...
direct connection automatically built ... 1st direct impact and 2nd impact, im only interested in 1st direct impact".
For each bellwether: 1. the SEC's full-text search for its name in the annual reports (10-K / 20-F) of the last 15 months;
2. of the filers, the tradable stocks of stocks.json (market cap $700M+, $20M+ a day), the largest first; 3. each one's
report is read and every sentence that names the bellwether is sorted by what it says: customer with a % of revenue, the
bellwether owns a stake, supplier, customer, agreement, rival, a platform it merely uses (Google Play, Google Cloud as a
tool ...: no link), or a plain mention. A stock is a 1st-impact link when its own report states one of the first five.
The file keeps the sentences, so every link can be checked against the company's own words.
"""
import concurrent.futures as cf, datetime, json, os, re, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import earnings as E  # noqa: E402
import event as V     # noqa: E402

NAMES = {"NVDA": ["NVIDIA"], "GOOGL": ["Google", "Alphabet"], "SPCX": ["SpaceX", "Space Exploration Technologies", "Starlink"],
         "MSFT": ["Microsoft"], "AMZN": ["Amazon", "AWS"], "META": ["Meta Platforms", "Meta"], "AAPL": ["Apple"], "TSLA": ["Tesla"],
         "AVGO": ["Broadcom"], "TSM": ["TSMC", "Taiwan Semiconductor"], "ORCL": ["Oracle"], "MU": ["Micron"], "AMD": ["AMD", "Advanced Micro Devices"]}
MAX_DOCS = 320
PLATFORM = re.compile(r"google (play|ads?|analytics|search|maps|workspace|chrome|pay)|app stores?|android|chrome|search engines?|"
                      r"apple app store|play store|windows|office 365|microsoft (office|teams|azure active)|social media", re.I)
KINDS = ["customer %", "stake", "supplier", "customer", "agreement", "rival", "platform", "mention"]
FIRST = {"customer %", "stake", "supplier", "customer", "agreement"}


def fts(name, d0, d1, errors):
    """{cik: [(file_date, form, adsh, file name)]} of the annual reports that contain the name"""
    out, frm, total = {}, 0, None
    while frm < 6000:
        q = urllib.parse.urlencode({"q": f'"{name}"', "forms": "10-K,20-F", "dateRange": "custom", "startdt": d0, "enddt": d1, "from": frm})
        try:
            j = json.loads(E.retry(lambda: E.http("https://efts.sec.gov/LATEST/search-index?" + q, E.SEC_UA)))
        except Exception as e:
            errors.append(f"search {name} from {frm}: {e!r}"[:200])
            break
        hits = (j.get("hits") or {}).get("hits") or []
        total = ((j.get("hits") or {}).get("total") or {}).get("value")
        for h in hits:
            s = h.get("_source") or {}
            fn = str(h.get("_id") or "").split(":")[-1]
            form = s.get("form") or s.get("file_type") or ""
            for c in s.get("ciks") or []:
                out.setdefault(int(c), []).append((s.get("file_date") or "", form, s.get("adsh") or "", fn))
        if len(hits) < 100:
            break
        frm += 100
        time.sleep(0.15)
    return out, total


def kind_of(s, pat):
    low = s.lower()
    money = re.search(r"\d{1,2}(\.\d+)?\s?%", s) and re.search(r"revenue|net sales|sales|receivable", low)
    if money and re.search(r"customer|accounted for|represented|comprised|sales to", low):
        return "customer %"
    if re.search(r"\b(invest(ed|ment|or)|stake|warrants?|beneficial(ly)? own|shares? (of|issued|sold|held)|equity (interest|investment)|purchased? .{0,40}(shares|stock))", low) \
            and re.search(pat.pattern + r".{0,160}(invest|purchas|acquir|own|hold|stake|shares|warrant)|(invest\w*|shares|stake|warrants?) .{0,80}(by|from|to|with|of) .{0,30}" + pat.pattern, s, re.I):
        return "stake"
    if PLATFORM.search(s):
        return "platform"
    if re.search(r"supplier|supplied by|purchases? from|we (purchase|buy|source|procure)|rel(y|ies|iance) on|depend(s|ent|ence)? (up)?on|sole[- ]source|"
                 r"single[- ]source|manufactured by|foundr(y|ies)|supply agreement", low):
        return "supplier"
    if re.search(r"customers?|sales to|sold to|purchases? by|end[- ]users?|design wins?|hyperscal", low):
        return "customer"
    if re.search(r"agreement|partnership|partner(ed|s)? with|collaborat|contract|lease|joint|alliance|memorandum", low):
        return "agreement"
    if re.search(r"compet", low):
        return "rival"
    return "mention"


def read_one(cik, hits, pats):
    """the newest annual report of the filer: its sentences that name the bellwether, sorted by kind"""
    d, form, adsh, fn = sorted(hits, reverse=True)[0]
    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{fn}"
    raw = E.retry(lambda: E.http(url, E.SEC_UA, 60)).decode("utf-8", "replace")
    txt = V.clean(raw)
    found = {}
    n = 0
    for part in re.split(r"\s*¶\s*", txt):
        if not any(p.search(part) for p in pats):
            continue
        for s in re.split(r"(?<=[a-z0-9%\)”\"])[.!?]\s+(?=[A-Z“\"$])", part):
            p = next((p for p in pats if p.search(s)), None)
            if not p or not (40 <= len(s) <= 700):
                continue
            n += 1
            k = kind_of(s, p)
            found.setdefault(k, [])
            if len(found[k]) < 3:
                found[k].append(V.short(s.strip(), 420))
    return {"filed": d, "form": form, "url": url, "mentions": n, "by_kind": found}


def main():
    stocks_p, out_p, syms = sys.argv[1], sys.argv[2], [s.upper() for s in sys.argv[3:]]
    S = json.load(open(stocks_p))
    trad = {s["symbol"]: s for s in S if (s.get("mcap_b") or 0) >= 0.7 and (s.get("dvol_20_m") or 0) >= 20}
    sec = E.SEC()
    by_cik = {}
    for t, c in sec.cik.items():
        t2 = t.replace("-", "/")
        if t in trad or t2 in trad:
            by_cik.setdefault(c, t if t in trad else t2)
    now = datetime.datetime.now(E.NY).date()
    d0, d1 = (now - datetime.timedelta(days=460)).isoformat(), now.isoformat()
    res = {"built_at": datetime.datetime.now(E.NY).isoformat(timespec="seconds"), "window": [d0, d1], "tradable": len(trad), "bellwethers": {}}
    for B in syms:
        errors, t0 = [], time.time()
        names = NAMES.get(B) or [str((next((s for s in S if s["symbol"] == B), {}) or {}).get("name") or B).split()[0]]
        pats = [re.compile(r"\b" + re.escape(nm) + r"\b") for nm in names]
        hits, totals = {}, {}
        for nm in names:
            h, tot = fts(nm, d0, d1, errors)
            totals[nm] = tot
            for c, v in h.items():
                hits.setdefault(c, []).extend(v)
        own = sec.cik.get(B)
        cand = sorted(((by_cik[c], c) for c in hits if c in by_cik and c != own), key=lambda x: -(trad[x[0]].get("mcap_b") or 0))
        rows = []

        def one(x):
            sym, c = x
            time.sleep(0.12)
            try:
                r = read_one(c, hits[c], pats)
            except Exception as e:
                return {"sym": sym, "error": repr(e)[:120]}
            best = next((k for k in KINDS if r["by_kind"].get(k)), None)
            st = trad[sym]
            return dict(r, sym=sym, name=st.get("name"), mcap_b=st.get("mcap_b"), themes=st.get("themes") or "", kind=best, first=best in FIRST)
        with cf.ThreadPoolExecutor(4) as ex:
            rows = list(ex.map(one, cand[:MAX_DOCS]))
        ok = [r for r in rows if not r.get("error") and r.get("kind")]
        ok.sort(key=lambda r: (KINDS.index(r["kind"]), -(r.get("mentions") or 0)))
        res["bellwethers"][B] = {"names": names, "search_hits": totals, "filers": len(hits), "tradable_filers": len(cand), "read": len(rows),
                                 "read_errors": sum(1 for r in rows if r.get("error")), "seconds": round(time.time() - t0),
                                 "count_by_kind": {k: sum(1 for r in ok if r["kind"] == k) for k in KINDS},
                                 "rows": ok, "errors": errors[:10] + [f"{r['sym']}: {r['error']}" for r in rows if r.get("error")][:10]}
        print(B, names, "| search hits", totals, "| tradable filers", len(cand), "| read", len(rows), "|", res["bellwethers"][B]["count_by_kind"], "| errors", len(errors))
    json.dump(res, open(out_p, "w"), separators=(",", ":"))


if __name__ == "__main__":
    main()
