#!/usr/bin/env python3
"""Pre-market gappers for Theme & Group Radar.

  prepare <premarket/latest.json> <stocks.json> <out_dir> [n_grade_up] [n_grade_down] [--live=premarket_live.json]
      Keeps gaps of 5%+ up or down that pass your rules: premarket/rules.json, which the portal's boxes on the Graded
      gappers list save (the user, Nov 7 2026); without it the defaults: market cap $700M+, 20-day average volume 700K+
      shares, 20-day average $ volume $20M+, ADR% 3+, 30%+ over the 52-week low at the pre-market price, gap-ups also over
      the 50 EMA. Claude's 8:45 grading and the code grader both run this, so they always use the same rules. It adds
      ADR%, theme, the pre-market price vs the 200-day SMA
      and the 50-day EMA (both as of the last close), an EP badge, and writes
      <out_dir>/rows.json plus <out_dir>/to_grade.json (by pre-market $ volume: top 20 gap-ups and top 8 gap-downs),
      and <out_dir>/gappers.json: every 5%+ gapper before those rules, with the rule that dropped it ("dropped"), so the
      code grader can give each one its news (the user, Nov 6 2026: "any gappers above 5%, their news"; FLY).
      and <out_dir>/theme_event.json: the theme events of the live scan (radar/theme_event.py: many stocks of one area
      gapping 5%+ together, Nov 11 2026: 93 semis / AI stocks), each with a plain "line"; [] on a normal day.
  finish <out_dir> [grades.json] [event_news.json]
      Merges the grades into <out_dir>/premarket.json (the dashboard's dataset file). With event_news.json
      ({"why": "one or two plain sentences: the market / sector news behind the theme event", "sources": ["url", ...]})
      it writes <out_dir>/pm_event.json for the portal's theme event line.

grades.json: {"SYM": {"grade": "A|B|C|F", "catalyst": "...", "reason": "...", "flags": "...",
                       "inflection": "Turnaround|Acceleration|New business|Margin|Deterioration|None", "inflection_score": 0-10,
                       "sources": ["url", ...]}}
"""
import datetime, json, os, re, subprocess, sys, urllib.parse

GAP_MIN, MCAP_MIN, AVGVOL_MIN, DVOL_MIN, ADR_MIN = 5.0, 0.7, 700_000, 20.0, 3.0
LOW52_MIN = 30.0       # the pre-market price at least 30% over the 52-week low (the user, Nov 4 2026)
# your rules for the graded list (the user, Nov 7 2026: "I want to adjust them myself"): the portal saves them to
# premarket/rules.json on main; each value is checked against the same range the portal allows, and one that is missing
# or out of range falls back to its default, so a typo can't empty the list. [default, lowest, highest]
RULES = {"mcap_min_b": [MCAP_MIN, 0.1, 50], "avgvol_min_k": [AVGVOL_MIN / 1000, 50, 10000], "dvol_min_m": [DVOL_MIN, 1, 1000],
         "adr_min": [ADR_MIN, 0, 20], "low52_min": [LOW52_MIN, 0, 200]}
RULES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "premarket", "rules.json")


def load_rules(path=RULES_FILE):
    """your saved rules, checked: {mcap_min_b, avgvol_min_k, dvol_min_m, adr_min, low52_min, gapup_above_ema50, saved_at,
    ignored (the values that were out of range or unreadable, with the default used instead)}"""
    try:
        doc = json.load(open(path))
    except Exception:
        doc = {}
    out, bad = {}, []
    for k, (d, lo, hi) in RULES.items():
        v = num(doc.get(k)) if k in doc else d
        if v is None or not (lo <= v <= hi):
            bad.append(f"{k}={doc.get(k)!r}")
            v = d
        out[k] = v
    e50 = doc.get("gapup_above_ema50", True)
    out["gapup_above_ema50"] = e50 if isinstance(e50, bool) else True
    out["saved_at"], out["ignored"] = doc.get("saved_at", ""), bad
    return out


def fmt(v):
    """3.0 -> '3', 0.7 -> '0.7' (for the dropped reasons)"""
    return f"{v:g}"
EP_GAP = 10.0          # Qullamaggie: an episodic pivot gaps 10%+ on huge volume
EP_PM_SHARE = 0.25     # proxy: pre-market volume already 25%+ of a normal full day


def num(x):
    try:
        return None if x is None or x == "" else float(x)
    except (TypeError, ValueError):
        return None


def prepare(pm_path, stocks_path, out, n_grade=20, n_down=8, live_path=None):
    pm = json.load(open(pm_path))
    stocks = {r["symbol"]: r for r in json.load(open(stocks_path))}
    # The live scanner file (every 5 minutes) is newer than the 8:25 scan: take its latest pre-market price, so the gap
    # and the moving-average columns are as of grading time (about 8:47), and its volume (Alpaca's consolidated tape;
    # Yahoo's pre-market bars carry none). Stocks only in the live file are added; ones only in the scan keep its numbers.
    if live_path and os.path.exists(live_path):
        lv = json.load(open(live_path))
        if lv.get("date") and lv["date"] > (pm.get("date") or ""):   # before the 8:25 scan (the 8:05 / 8:35 news runs, the
            pm = {"date": lv["date"], "saved_at": lv.get("saved_at", ""), "rows": []}   # user Nov 6 2026): the live scan alone
        if lv.get("date") == pm.get("date"):
            by = {g["symbol"]: g for g in pm.get("rows", [])}
            for sym, q in (lv.get("rows") or {}).items():
                prev = num((stocks.get(sym) or {}).get("price"))
                if not prev:
                    continue
                g = by.setdefault(sym, {"symbol": sym, "prev_close": prev})
                g["pm_last"], g["gap_pct"], g["pm_volume"], g["pm_dvol"] = q[0], q[1], q[3], q[4]
            pm["rows"] = list(by.values())
            pm["saved_at"] = lv.get("saved_at") or pm.get("saved_at", "")
    events = []                                   # the theme events of the live scan (the user, Nov 11 2026)
    if live_path and os.path.exists(live_path):
        try:
            lv = json.load(open(live_path))
            if lv.get("date") == pm.get("date"):
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                import theme_event
                events = [dict(e, line=theme_event.line(e, lv.get("rows") or {})) for e in lv.get("events") or []]
        except Exception as e:
            print(f"theme events: {e}", file=sys.stderr)
    os.makedirs(out, exist_ok=True)
    json.dump(events, open(os.path.join(out, "theme_event.json"), "w"), indent=1)
    R = load_rules()
    mcap_min, avgvol_min, dvol_min, adr_min, low52_min = R["mcap_min_b"], R["avgvol_min_k"] * 1000, R["dvol_min_m"], R["adr_min"], R["low52_min"]
    rows, every = [], []                          # every = all 5%+ gappers, for the news of each (the user, Nov 6 2026)
    for g in pm.get("rows", []):
        s = stocks.get(g["symbol"])
        if not s or abs(g["gap_pct"]) < GAP_MIN:
            continue
        mcap, avgv, dv = num(s.get("mcap_b")), num(s.get("avg_vol_20") or s.get("avg_vol_30d")), num(s.get("dvol_20_m"))   # 20-day (your rule, Nov 2 2026)
        adr = num(s.get("adr_20"))
        lo52, px = num(s.get("low_52w")), num(g.get("pm_last"))
        e50x = num(s.get("ema50"))
        if not (mcap and mcap >= mcap_min):
            why = f"market cap under ${fmt(mcap_min)}B"
        elif not (avgv and avgv >= avgvol_min):
            why = f"20-day average volume under {fmt(avgvol_min / 1000)}K"
        elif not (dv and dv >= dvol_min):
            why = f"20-day average $ volume under ${fmt(dvol_min)}M"
        elif adr is not None and adr < adr_min:   # ADR% 3+ (a stock with no ADR yet isn't dropped)
            why = f"ADR under {fmt(adr_min)}%"
        elif lo52 and px and px < lo52 * (1 + low52_min / 100):
            why = f"under {fmt(low52_min)}% over the 52-week low"   # the user, Nov 4 2026: under 30% over the 52-week low
                                                  # (pre-market price) qualifies for nothing (no 52-week low yet isn't dropped)
        elif R["gapup_above_ema50"] and g["gap_pct"] > 0 and e50x and px and px < e50x:
            why = "gap-up under the 50 EMA"       # a gap-up under its 50 EMA in pre-market isn't eligible (the user, Nov 4 2026)
        else:
            why = ""
        every.append({"symbol": g["symbol"], "direction": "up" if g["gap_pct"] > 0 else "down", "gap_pct": g["gap_pct"],
                      "pm_last": g.get("pm_last"), "mcap_b": mcap, "scan_date": pm.get("date", ""), "dropped": why})
        if why:
            continue
        share = g["pm_volume"] / avgv
        sma, e50, last = num(s.get("sma200")), num(s.get("ema50")), num(g.get("pm_last"))
        vs = lambda m: round((last / m - 1) * 100, 1) if m and last else None   # the pre-market price at scan time
        rows.append({
            "symbol": g["symbol"], "name": s.get("name"), "tv_symbol": s.get("tv_symbol"),
            "gap_pct": g["gap_pct"], "pm_last": g["pm_last"], "prev_close": g["prev_close"],
            "pm_volume": g["pm_volume"], "pm_dvol_m": round(g["pm_dvol"] / 1e6, 2),
            "pm_vol_pct_adv": round(share * 100, 1),
            "gap_x_adr": round(g["gap_pct"] / adr, 2) if adr else None,
            "direction": "up" if g["gap_pct"] > 0 else "down",
            "ep": bool(g["gap_pct"] >= EP_GAP and share >= EP_PM_SHARE),
            "mcap_b": mcap, "avg_vol_30d": int(avgv), "dvol_20_m": dv, "adr_20": adr,
            "sma200": sma, "ema50": e50, "above_200": (last > sma) if sma and last else s.get("above_200"),
            "vs_200": vs(sma) if sma and last else s.get("vs_200"), "vs_50e": vs(e50), "chg_1m": s.get("chg_1m"), "chg_3m": s.get("chg_3m"),
            "themes": s.get("themes") or "", "industry": s.get("industry"),
            "grade": "", "catalyst": "", "reason": "", "flags": "", "inflection": "", "inflection_score": None,
            "sources": "", "graded": False,
            "scan_time": pm.get("saved_at", "")[11:16], "scan_date": pm.get("date", ""),
        })
    rows.sort(key=lambda r: -r["pm_dvol_m"])
    os.makedirs(out, exist_ok=True)
    json.dump({"scan_date": pm.get("date", ""), "scan_time": pm.get("saved_at", "")[11:16]}, open(os.path.join(out, "meta.json"), "w"))
    json.dump(rows, open(os.path.join(out, "rows.json"), "w"), indent=1)
    every.sort(key=lambda r: -abs(r["gap_pct"]))
    json.dump(every, open(os.path.join(out, "gappers.json"), "w"), indent=0)   # the code grader's news for each (codegrade.py)
    pick = [r for r in rows if r["direction"] == "up"][:n_grade] + [r for r in rows if r["direction"] == "down"][:n_down]
    todo = [{k: r[k] for k in ("symbol", "name", "direction", "gap_pct", "pm_volume", "pm_dvol_m", "pm_vol_pct_adv", "gap_x_adr",
                                "mcap_b", "industry", "themes")} for r in pick]
    json.dump(todo, open(os.path.join(out, "to_grade.json"), "w"), indent=1)
    print(json.dumps({"scan_date": pm.get("date"), "scan_time": pm.get("saved_at"), "in_file": len(pm.get("rows", [])),
                      "gapping_5": len(every), "pass_rules": len(rows), "to_grade": len(todo),
                      "theme_events": [e["line"] for e in events],
                      "rules": {k: R[k] for k in list(RULES) + ["gapup_above_ema50", "saved_at"]},
                      **({"rules_ignored": R["ignored"]} if R["ignored"] else {})}))


# ───────── the safety lock on A / B grades (the user, Nov 4 2026: DUOL got an A while its reason said "exact revenue
# and guidance figures were not confirmed", and the grader never opened the release) ─────────
HEDGE = re.compile(r"not (?:been |yet )?confirmed|unconfirmed|could ?n[o']t (?:be )?(?:confirm|verif|find|open|read|access)|"
                   r"not (?:be )?verified|unverified|unable to (?:confirm|verify|open|access)|not available|no (?:primary|official) source",
                   re.I)
NEWSWIRES = ("sec.gov", "globenewswire.com", "businesswire.com", "prnewswire.com", "accessnewswire.com", "newsfilecorp.com",
             "accesswire.com", "newswire.ca")


def primary(url, name, sym):
    """an SEC filing, a newswire carrying the company's own release, or the company's own site"""
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    if any(host == d or host.endswith("." + d) for d in NEWSWIRES):
        return True
    label = host.split(".")[-2] if host.count(".") >= 1 else host           # riotplatforms.com -> riotplatforms
    words = [w for w in re.findall(r"[a-z0-9]+", (name or "").lower()) if len(w) >= 4 and w not in ("inc", "corp", "holdings", "group", "company", "technologies", "therapeutics")]
    return bool(label and (label.startswith(sym.lower()) or any(label.startswith(w[:6]) or w[:6] in label for w in words)))


def earnings_reads():
    """the Earnings tab's reads (radar-data earnings.json): SEC release numbers, no Claude"""
    try:
        j = json.loads(subprocess.run(["git", "show", "origin/radar-data:earnings.json"], capture_output=True, text=True, check=True).stdout)
    except Exception:
        return {}
    react = j.get("react") or {}
    t0, p1 = react.get("t0"), react.get("p1")
    out = {}
    for r in j.get("rows", []):
        if r.get("reported") and r.get("read") and ((r.get("date") == t0 and r.get("when") in ("bmo", "dmh", "tns")) or
                                                     (r.get("date") == p1 and r.get("when") in ("amc", "dmh", "tns")) or r.get("date") == t0):
            out[r["sym"]] = r
    return out


def lock(r, er):
    """A / B only with a primary source the reason doesn't hedge on; earnings gappers carry the Earnings tab's read"""
    notes = []
    e = er.get(r["symbol"])
    if e:
        notes.append(f"Earnings tab (SEC release): {e['read']}" + (f" ({e['why']})" if e.get("why") else ""))
    g0 = r.get("grade")
    if g0 in ("A", "B"):
        srcs = (r.get("sources") or "").split()
        why = None
        if HEDGE.search((r.get("reason") or "") + " " + (r.get("flags") or "")):
            why = "the grader could not confirm the facts"
        elif not any(primary(u, r.get("name"), r["symbol"]) for u in srcs):
            why = "no primary source (company release, SEC filing or newswire)"
        elif e and r.get("direction") == "up" and e["read"] in ("Bearish", "Somewhat bearish"):
            why = f"the Earnings tab reads the release {e['read']}"
        elif e and r.get("direction") == "down" and e["read"] in ("Bullish", "Strong bullish"):
            why = f"the Earnings tab reads the release {e['read']}"
        if why:
            r["grade"] = "C" if why.startswith(("the grader", "no primary")) else {"A": "B", "B": "C"}[g0]
            r["locked"] = f"{g0} -> {r['grade']}: {why}"
            r["reason"] = f"⚠ Lowered from {g0}: {why}. " + (r.get("reason") or "")
    if notes:
        r["flags"] = "; ".join([x for x in [r.get("flags") or ""] if x] + notes)


def event_news(out, news_path):
    """the news behind today's theme event (the 8:45 grading searched it once) -> <out>/pm_event.json for the portal"""
    try:
        evs = json.load(open(os.path.join(out, "theme_event.json")))
        meta = json.load(open(os.path.join(out, "meta.json")))
        n = json.load(open(news_path))
    except Exception:
        return False
    why = str(n.get("why") or "").strip()
    if not evs or not why:
        return False
    src = [u for u in (n.get("sources") or []) if isinstance(u, str) and u.startswith("https://")][:3]
    json.dump({"day": meta.get("scan_date", ""), "time": meta.get("scan_time", ""), "why": why[:600], "sources": src,
               "areas": [a["name"] for e in evs for a in e.get("areas", [])]},
              open(os.path.join(out, "pm_event.json"), "w"), separators=(",", ":"))
    return True


def finish(out, grades_path=None, news_path=None):
    if news_path:
        print(json.dumps({"theme_event_news": event_news(out, news_path)}))
    rows = json.load(open(os.path.join(out, "rows.json")))
    grades = json.load(open(grades_path)) if grades_path and os.path.exists(grades_path) else {}
    er = earnings_reads()
    for r in rows:
        g = grades.get(r["symbol"])
        if g:
            r.update(grade=str(g.get("grade", "")).upper()[:1], catalyst=g.get("catalyst", ""), reason=g.get("reason", ""),
                     flags=g.get("flags", ""), inflection=g.get("inflection", "") if g.get("inflection") != "None" else "",
                     inflection_score=g.get("inflection_score"), sources=" ".join(g.get("sources", [])[:3]), graded=True)
            lock(r, er)
    order = {"A": 0, "B": 1, "C": 2, "F": 3}
    rows.sort(key=lambda r: (r["direction"] != "up", order.get(r["grade"], 4), -r["pm_dvol_m"]))
    if not rows:   # keep one placeholder row so the dashboard can still show the scan time
        meta = json.load(open(os.path.join(out, "meta.json"))) if os.path.exists(os.path.join(out, "meta.json")) else {}
        rows = [{"symbol": "(none)", "placeholder": True, "direction": "none", "scan_date": meta.get("scan_date", ""),
                 "scan_time": meta.get("scan_time", ""), "graded": False, "grade": "", "pm_dvol_m": 0}]
    json.dump(rows, open(os.path.join(out, "premarket.json"), "w"), separators=(",", ":"))
    print(json.dumps({"rows": len(rows), "graded": sum(r["graded"] for r in rows),
                      "by_grade": {k: sum(r["grade"] == k for r in rows) for k in "ABCF"},
                      "locked": [f"{r['symbol']} {r['locked']}" for r in rows if r.get("locked")]}))


if __name__ == "__main__":
    if sys.argv[1] == "prepare":
        a = [x for x in sys.argv[2:] if not x.startswith("--live=")]
        live = next((x.split("=", 1)[1] for x in sys.argv if x.startswith("--live=")), None)
        prepare(a[0], a[1], a[2], int(a[3]) if len(a) > 3 else 20, int(a[4]) if len(a) > 4 else 8, live)
    else:
        finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None, sys.argv[4] if len(sys.argv) > 4 else None)
