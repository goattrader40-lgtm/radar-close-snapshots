#!/usr/bin/env python3
"""The link finder (a test tool, nothing live reads it): a bellwether's direct links, from the companies' own annual reports.

  python3 radar/probe_links.py <stocks.json> <out probe_links.json> [minutes]

The user, Nov 17-18 2026: "big bellwethers maps, for their suppliers and connectivity vendors ... kind of algorithmic ...
direct connection automatically built ... im only interested in 1st direct impact ones"; "you can increase that meta
microsoft apple and so on".
Every tradable stock of stocks.json (market cap $700M+, $20M+ a day) is read once: its newest annual report at the SEC
(10-K, 20-F or 40-F). Every sentence that names a bellwether (NAMES below) is sorted by what it says:
  customer %   the bellwether is named with a share of the stock's revenue or receivables (the 10% customer note)
  store %      the same through its store, app store or ads (a retailer's sales on Amazon, an app's on Google Play): no link
  stake        the bellwether bought, holds or may buy the stock's shares or warrants
  sells to it  the bellwether is named as a customer
  buys from it the bellwether is named as its supplier
  agreement    a named agreement, contract, lease or partnership with it
  rival        named as a competitor
  platform     a tool everyone uses (app stores, ads, cloud hosting, Windows ...): no link
  mention      anything else: no link
The file keeps the sentences, so each proposed link can be checked against the company's own words. It proposes; the map
(radar/bellwethers.json) is written from it by review: the finder's label alone is not the link.
(The first version, Nov 17, used the SEC's full-text search and missed MU, DELL, TSM, ALAB, MRVL for NVIDIA.)
"""
import concurrent.futures as cf, datetime, json, os, re, sys, threading, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import earnings as E  # noqa: E402
import event as V     # noqa: E402

NAMES = {"NVDA": ["NVIDIA", "Nvidia"], "MSFT": ["Microsoft", "Azure"], "GOOGL": ["Google", "Alphabet"], "AMZN": ["Amazon", "AWS"],
         "META": ["Meta Platforms", "Meta"], "AAPL": ["Apple"], "AVGO": ["Broadcom"], "TSM": ["TSMC", "Taiwan Semiconductor"],
         "MU": ["Micron"], "SPCX": ["SpaceX", "Space Exploration Technologies", "Starlink"], "ORCL": ["Oracle"],
         "AMD": ["AMD", "Advanced Micro Devices"], "ASML": ["ASML"], "TSLA": ["Tesla"], "PLTR": ["Palantir"],
         "UNH": ["UnitedHealth", "UnitedHealthcare", "Optum"], "LLY": ["Eli Lilly", "Lilly"], "OPENAI": ["OpenAI"]}
KINDS = ["customer %", "stake", "sells to it", "buys from it", "agreement", "rival", "store %", "platform", "mention"]
KEEP = KINDS[:6]
PLATFORM = re.compile(r"app stores?|google play|play store|app store|\bios\b|android|search engines?|social media|advertis|facebook|instagram|whatsapp|"
                      r"youtube|windows|office 365|microsoft 365|\bteams\b|browser|operating systems?|mobile (devices?|platforms?)|marketplaces?|"
                      r"kindle|alexa|prime video|iphone|ipad|smartphones?|"
                      r"(host(ed|ing|s)?|runs?|rel(y|ies|iance)|depend(s|ent|ence)?|operat\w+|deploy\w*|migrat\w+|built)[^.]{0,120}(aws|amazon web services|azure|google cloud|gcp)|"
                      r"third[- ]party (cloud|hosting) (service|provider|infrastructure|platform)|our (cloud|hosting) (service )?providers?", re.I)
STORE = re.compile(r"app stores?|google play|play store|app store|advertis|search engines?|marketplaces?|e-?commerce|retail(er)?s?|wholesale|consumer", re.I)
LOCK = threading.Lock()


def kind_of(s, n, ctx):
    """n = the bellwether's names as one regex group; ctx = the text just before the sentence"""
    low = s.lower()
    if re.search(r"\d{1,2}(\.\d+)?\s?%", s) and re.search(r"revenue|net sales|\bsales\b|receivable", low) \
            and re.search(r"customer|accounted for|represented|comprised|sales to|distributor|partner", low):
        return "store %" if STORE.search(s) else "customer %"
    G = r"(?:[^.;]|\.(?=\d))"
    SH = r"(?i:shares|stock|warrants?|equity|notes)"
    if re.search(n + G + r"{0,90}\b(?i:invested|purchased|acquired|holds?|owns?|agreed to (?:purchase|invest)|right to (?:purchase|acquire)|subscribed)\b" + G + r"{0,90}(?:" + SH + r"|\$)", s) \
            or re.search(r"(?i:issu(?:ed|ance)|sold|sale|grant(?:ed)?)" + G + r"{0,140}" + SH + G + r"{0,140}\bto " + n, s) \
            or re.search(r"(?i:investment|invested)" + G + r"{0,40}\b(?:by|from) " + n, s) or re.search(n + r"(?:'s)? (?:Warrants?|Investment|Shares)\b", s) \
            or re.search(r"(?i:warrants?|right)" + G + r"{0,80}\bto " + n + G + r"{0,80}(?i:purchase|acquire)", s):
        return "stake"
    if re.search(r"compet", low) or re.search(r"compet", ctx[-350:].lower()):
        return "rival"
    if PLATFORM.search(s):
        return "platform"
    if re.search(r"(customers?|clients?)(?:[^.]|\.(?=\d)){0,140}(includ\w+|such as|like|:|are|were)(?:[^.]|\.(?=\d)){0,220}" + n, s, re.I) \
            or re.search(n + r"(?:[^.]|\.(?=\d)){0,90}\b(is|are|was|were|as|remain(s|ed)?)\b(?:[^.]|\.(?=\d)){0,40}(customers?|clients?)", s) \
            or re.search(r"(sales|sold|shipments?|deliver\w+|revenue)(?:[^.]|\.(?=\d)){0,30}\b(to|from) (?:[^.]|\.(?=\d)){0,40}" + n, s):
        return "sells to it"
    if re.search(r"(suppliers?|vendors?|foundr(y|ies)|manufacturers?)(?:[^.]|\.(?=\d)){0,140}(includ\w+|such as|like|:|are|is)(?:[^.]|\.(?=\d)){0,220}" + n, s, re.I) \
            or re.search(n + r"(?:[^.]|\.(?=\d)){0,80}\b(is|are|as)\b(?:[^.]|\.(?=\d)){0,40}(sole|primary|principal|key|major|only|single|significant)(?:[^.]|\.(?=\d)){0,30}(supplier|source|provider|vendor|foundry)", s) \
            or re.search(r"(purchas\w+|buy|source[ds]?|procure\w*|obtain\w*|licens\w+)(?:[^.]|\.(?=\d)){0,100}\bfrom (?:[^.]|\.(?=\d)){0,40}" + n, s) \
            or re.search(r"(rel(y|ies|iance)|depend(s|ent|ence)?) (up)?on (?:[^.]|\.(?=\d)){0,80}" + n, s):
        return "buys from it"
    if re.search(r"(agreements?|contracts?|leases?|partnerships?|collaborations?|memorandum|orders?|arrangements?|alliances?)(?:[^.]|\.(?=\d)){0,90}\b(with|by|from|to) (?:[^.]|\.(?=\d)){0,60}" + n, s, re.I) \
            or re.search(n + r"(?:[^.]|\.(?=\d)){0,70}(agreement|contract|lease|partnership|collaboration)", s) \
            or re.search(r"(partner(ed|ing|s)?|collaborat\w+|teamed) with (?:[^.]|\.(?=\d)){0,50}" + n, s, re.I):
        return "agreement"
    return "mention"


def annual(sec_cik):
    """(filed, form, url) of the filer's newest annual report"""
    sub = json.loads(E.retry(lambda: E.http(f"https://data.sec.gov/submissions/CIK{sec_cik:010d}.json", E.SEC_UA, 40)))
    f = sub["filings"]["recent"]
    for i, form in enumerate(f["form"]):
        if form in ("10-K", "20-F", "40-F") and f["primaryDocument"][i]:
            return f["filingDate"][i], form, f"https://www.sec.gov/Archives/edgar/data/{sec_cik}/{f['accessionNumber'][i].replace('-', '')}/{f['primaryDocument'][i]}"
    return None


def read(sym, cik, pats, own):
    """{bellwether: {kind: [sentences]}} and the mention counts, from the stock's annual report"""
    a = annual(cik)
    if not a:
        return None
    filed, form, url = a
    txt = V.clean(E.retry(lambda: E.http(url, E.SEC_UA, 120)).decode("utf-8", "replace"))
    out = {}
    hot = {b: p for b, (p, n) in pats.items() if b != own and p.search(txt)}
    if not hot:
        return {"filed": filed, "form": form, "url": url, "chars": len(txt), "links": {}}
    ctx = ""
    for part in re.split(r"\s*¶\s*", txt):
        hit = [b for b, p in hot.items() if p.search(part)]
        if hit:
            # a table row: the name with a share next to it, under a note about customers (the 10% customer table)
            if len(part) <= 170 and re.search(r"\d{1,2}(\.\d+)?\s?%", part) and re.search(r"customer|accounts? receivable|net sales|revenue", ctx[-900:], re.I) \
                    and re.search(r"10\s?%|ten percent|concentration|significant customers?|major customers?|accounted for", ctx[-900:], re.I):
                for b in hit:
                    o = out.setdefault(b, {"n": 0, "by": {}})
                    o["n"] += 1
                    o["by"].setdefault("customer %", [])
                    if len(o["by"]["customer %"]) < 3:
                        o["by"]["customer %"].append(V.short("[table] … " + ctx[-260:].strip() + " | " + part.strip(), 520))
            else:
                for s in re.split(r"(?<=[a-z0-9%\)”\"])[.!?]\s+(?=[A-Z“\"$•])", part):
                    if not (40 <= len(s) <= 900):
                        continue
                    for b in hit:
                        if not hot[b].search(s):
                            continue
                        k = kind_of(s, pats[b][1], ctx)
                        o = out.setdefault(b, {"n": 0, "by": {}})
                        o["n"] += 1
                        o["by"].setdefault(k, [])
                        if len(o["by"][k]) < 3:
                            o["by"][k].append(V.short(s.strip(), 420))
        ctx = (ctx + " " + part)[-1200:]
    return {"filed": filed, "form": form, "url": url, "chars": len(txt), "links": out}


def main():
    stocks_p, out_p = sys.argv[1], sys.argv[2]
    minutes = float(sys.argv[3]) if len(sys.argv) > 3 else 42
    S = json.load(open(stocks_p))
    trad = sorted((s for s in S if (s.get("mcap_b") or 0) >= 0.7 and (s.get("dvol_20_m") or 0) >= 20), key=lambda s: -(s.get("mcap_b") or 0))
    sec = E.SEC()
    cik_of = lambda t: sec.cik.get(t) or sec.cik.get(t.replace("/", "-")) or sec.cik.get(t.replace("/", "."))
    pats = {}
    for b, names in NAMES.items():
        g = "(?:" + "|".join(re.escape(x) for x in names) + ")"
        pats[b] = (re.compile(r"(?<![A-Za-z])" + g + r"(?![A-Za-z])"), r"(?<![A-Za-z])" + g + r"(?![A-Za-z])")
    t0, res, errors, stats = time.time(), {b: [] for b in NAMES}, [], {"read": 0, "no_cik": 0, "no_report": 0, "errors": 0, "skipped_time": 0}

    def one(st):
        sym = st["symbol"]
        if time.time() - t0 > minutes * 60:
            with LOCK:
                stats["skipped_time"] += 1
            return
        c = cik_of(sym)
        if not c:
            with LOCK:
                stats["no_cik"] += 1
            return
        time.sleep(0.25)
        try:
            r = read(sym, c, pats, sym if sym in NAMES else {"GOOG": "GOOGL"}.get(sym))
        except Exception as e:
            with LOCK:
                stats["errors"] += 1
                if len(errors) < 25:
                    errors.append(f"{sym}: {e!r}"[:140])
            return
        with LOCK:
            if not r:
                stats["no_report"] += 1
                return
            stats["read"] += 1
            for b, o in r["links"].items():
                best = next((k for k in KINDS if o["by"].get(k)), None)
                row = {"sym": sym, "name": st.get("name"), "mcap_b": st.get("mcap_b"), "themes": st.get("themes") or "", "adr": st.get("adr_20"),
                       "filed": r["filed"], "form": r["form"], "url": r["url"], "mentions": o["n"], "kind": best,
                       "kinds": {k: len(v) for k, v in o["by"].items()}}
                if best in KEEP:
                    row["by_kind"] = {k: v for k, v in o["by"].items() if k in KEEP}
                elif st.get("themes") and o["n"] >= 2:
                    row["seen"] = o["by"][best][0][:300]
                res[b].append(row)
    with cf.ThreadPoolExecutor(5) as ex:
        list(ex.map(one, trad))
    out = {"built_at": datetime.datetime.now(E.NY).isoformat(timespec="seconds"), "tradable": len(trad), "stats": stats, "seconds": round(time.time() - t0),
           "errors": errors, "names": NAMES, "bellwethers": {}}
    for b, rows in res.items():
        rows.sort(key=lambda r: (KINDS.index(r["kind"]), -(r.get("mentions") or 0)))
        out["bellwethers"][b] = {"count_by_kind": {k: sum(1 for r in rows if r["kind"] == k) for k in KINDS},
                                 "rows": [r for r in rows if r["kind"] in KEEP],
                                 "other": [[r["sym"], r["kind"], r["mentions"], r.get("seen", "")] for r in rows if r["kind"] not in KEEP and (r["mentions"] >= 5 or r.get("seen"))][:160]}
        print(b, out["bellwethers"][b]["count_by_kind"])
    json.dump(out, open(out_p, "w"), separators=(",", ":"))
    print(stats, round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
