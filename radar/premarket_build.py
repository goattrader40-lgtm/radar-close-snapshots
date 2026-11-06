#!/usr/bin/env python3
"""Pre-market gappers for Theme & Group Radar.

  prepare <premarket/latest.json> <stocks.json> <out_dir> [n_grade_up] [n_grade_down] [--live=premarket_live.json]
      Keeps gaps of 5%+ up or down that pass the liquidity rules (market cap $700M+, 20-day average volume 700K+ shares,
      20-day average $ volume $20M+, ADR% 3+) and sit 30%+ over the 52-week low at the pre-market price (gap-ups also over
      the 50 EMA), adds ADR%, theme, the pre-market price vs the 200-day SMA
      and the 50-day EMA (both as of the last close), an EP badge, and writes
      <out_dir>/rows.json plus <out_dir>/to_grade.json (by pre-market $ volume: top 20 gap-ups and top 8 gap-downs),
      and <out_dir>/gappers.json: every 5%+ gapper before those rules, with the rule that dropped it ("dropped"), so the
      code grader can give each one its news (the user, Nov 6 2026: "any gappers above 5%, their news"; FLY).
  finish <out_dir> [grades.json]
      Merges the grades into <out_dir>/premarket.json (the dashboard's dataset file).

grades.json: {"SYM": {"grade": "A|B|C|F", "catalyst": "...", "reason": "...", "flags": "...",
                       "inflection": "Turnaround|Acceleration|New business|Margin|Deterioration|None", "inflection_score": 0-10,
                       "sources": ["url", ...]}}
"""
import datetime, json, os, re, subprocess, sys, urllib.parse

GAP_MIN, MCAP_MIN, AVGVOL_MIN, DVOL_MIN, ADR_MIN = 5.0, 0.7, 700_000, 20.0, 3.0
LOW52_MIN = 30.0       # the pre-market price at least 30% over the 52-week low (the user, Nov 4 2026)
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
    rows, every = [], []                          # every = all 5%+ gappers, for the news of each (the user, Nov 6 2026)
    for g in pm.get("rows", []):
        s = stocks.get(g["symbol"])
        if not s or abs(g["gap_pct"]) < GAP_MIN:
            continue
        mcap, avgv, dv = num(s.get("mcap_b")), num(s.get("avg_vol_20") or s.get("avg_vol_30d")), num(s.get("dvol_20_m"))   # 20-day (your rule, Nov 2 2026)
        adr = num(s.get("adr_20"))
        lo52, px = num(s.get("low_52w")), num(g.get("pm_last"))
        e50x = num(s.get("ema50"))
        if not (mcap and mcap >= MCAP_MIN):
            why = f"market cap under ${MCAP_MIN}B"
        elif not (avgv and avgv >= AVGVOL_MIN):
            why = f"20-day average volume under {AVGVOL_MIN // 1000}K"
        elif not (dv and dv >= DVOL_MIN):
            why = f"20-day average $ volume under ${DVOL_MIN:.0f}M"
        elif adr is not None and adr < ADR_MIN:   # ADR% 3+ (a stock with no ADR yet isn't dropped)
            why = f"ADR under {ADR_MIN:.0f}%"
        elif lo52 and px and px < lo52 * (1 + LOW52_MIN / 100):
            why = f"under {LOW52_MIN:.0f}% over the 52-week low"   # the user, Nov 4 2026: under 30% over the 52-week low
                                                  # (pre-market price) qualifies for nothing (no 52-week low yet isn't dropped)
        elif g["gap_pct"] > 0 and e50x and px and px < e50x:
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
                      "gapping_5": len(every), "pass_rules": len(rows), "to_grade": len(todo)}))


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


def finish(out, grades_path=None):
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
        finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
