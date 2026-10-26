#!/usr/bin/env python3
"""Pre-market gappers for Theme & Group Radar.

  prepare <premarket/latest.json> <stocks.json> <out_dir> [n_grade_up] [n_grade_down] [--live=premarket_live.json]
      Keeps gaps of 5%+ up or down that pass the liquidity rules (market cap $700M+, 30-day average volume 700K+ shares,
      20-day average $ volume $20M+, ADR% 3+), adds ADR%, theme, 200-day SMA and an EP badge, and writes
      <out_dir>/rows.json plus <out_dir>/to_grade.json (by pre-market $ volume: top 20 gap-ups and top 8 gap-downs).
  finish <out_dir> [grades.json]
      Merges the grades into <out_dir>/premarket.json (the dashboard's dataset file).

grades.json: {"SYM": {"grade": "A|B|C|F", "catalyst": "...", "reason": "...", "flags": "...",
                       "inflection": "Turnaround|Acceleration|New business|Margin|Deterioration|None", "inflection_score": 0-10,
                       "sources": ["url", ...]}}
"""
import datetime, json, os, sys

GAP_MIN, MCAP_MIN, AVGVOL_MIN, DVOL_MIN, ADR_MIN = 5.0, 0.7, 700_000, 20.0, 3.0
EP_GAP = 10.0          # Qullamaggie: an episodic pivot gaps 10%+ on huge volume
EP_PM_SHARE = 0.25     # proxy: pre-market volume already 25%+ of a normal full day


def num(x):
    try:
        return None if x is None or x == "" else float(x)
    except (TypeError, ValueError):
        return None


def prepare(pm_path, stocks_path, out, n_grade=20, n_down=8, live_path=None):
    pm = json.load(open(pm_path))
    # Yahoo's pre-market bars carry no volume; the live scanner file has it from Alpaca (consolidated tape)
    if live_path and os.path.exists(live_path):
        lv = json.load(open(live_path))
        if lv.get("date") == pm.get("date"):
            for g in pm.get("rows", []):
                q = (lv.get("rows") or {}).get(g["symbol"])
                if q:
                    g["pm_volume"], g["pm_dvol"] = q[3], q[4]
    stocks = {r["symbol"]: r for r in json.load(open(stocks_path))}
    rows = []
    for g in pm.get("rows", []):
        s = stocks.get(g["symbol"])
        if not s or abs(g["gap_pct"]) < GAP_MIN:
            continue
        mcap, avgv, dv = num(s.get("mcap_b")), num(s.get("avg_vol_30d")), num(s.get("dvol_20_m"))
        if not (mcap and mcap >= MCAP_MIN and avgv and avgv >= AVGVOL_MIN and dv and dv >= DVOL_MIN):
            continue
        adr = num(s.get("adr_20"))
        if adr is not None and adr < ADR_MIN:     # ADR% 3+ (a stock with no ADR yet isn't dropped)
            continue
        share = g["pm_volume"] / avgv
        rows.append({
            "symbol": g["symbol"], "name": s.get("name"), "tv_symbol": s.get("tv_symbol"),
            "gap_pct": g["gap_pct"], "pm_last": g["pm_last"], "prev_close": g["prev_close"],
            "pm_volume": g["pm_volume"], "pm_dvol_m": round(g["pm_dvol"] / 1e6, 2),
            "pm_vol_pct_adv": round(share * 100, 1),
            "gap_x_adr": round(g["gap_pct"] / adr, 2) if adr else None,
            "direction": "up" if g["gap_pct"] > 0 else "down",
            "ep": bool(g["gap_pct"] >= EP_GAP and share >= EP_PM_SHARE),
            "mcap_b": mcap, "avg_vol_30d": int(avgv), "dvol_20_m": dv, "adr_20": adr,
            "above_200": s.get("above_200"), "vs_200": s.get("vs_200"), "chg_1m": s.get("chg_1m"), "chg_3m": s.get("chg_3m"),
            "themes": s.get("themes") or "", "industry": s.get("industry"),
            "grade": "", "catalyst": "", "reason": "", "flags": "", "inflection": "", "inflection_score": None,
            "sources": "", "graded": False,
            "scan_time": pm.get("saved_at", "")[11:16], "scan_date": pm.get("date", ""),
        })
    rows.sort(key=lambda r: -r["pm_dvol_m"])
    os.makedirs(out, exist_ok=True)
    json.dump({"scan_date": pm.get("date", ""), "scan_time": pm.get("saved_at", "")[11:16]}, open(os.path.join(out, "meta.json"), "w"))
    json.dump(rows, open(os.path.join(out, "rows.json"), "w"), indent=1)
    pick = [r for r in rows if r["direction"] == "up"][:n_grade] + [r for r in rows if r["direction"] == "down"][:n_down]
    todo = [{k: r[k] for k in ("symbol", "name", "direction", "gap_pct", "pm_volume", "pm_dvol_m", "pm_vol_pct_adv", "gap_x_adr",
                                "mcap_b", "industry", "themes")} for r in pick]
    json.dump(todo, open(os.path.join(out, "to_grade.json"), "w"), indent=1)
    print(json.dumps({"scan_date": pm.get("date"), "scan_time": pm.get("saved_at"), "in_file": len(pm.get("rows", [])),
                      "pass_rules": len(rows), "to_grade": len(todo)}))


def finish(out, grades_path=None):
    rows = json.load(open(os.path.join(out, "rows.json")))
    grades = json.load(open(grades_path)) if grades_path and os.path.exists(grades_path) else {}
    for r in rows:
        g = grades.get(r["symbol"])
        if g:
            r.update(grade=str(g.get("grade", "")).upper()[:1], catalyst=g.get("catalyst", ""), reason=g.get("reason", ""),
                     flags=g.get("flags", ""), inflection=g.get("inflection", "") if g.get("inflection") != "None" else "",
                     inflection_score=g.get("inflection_score"), sources=" ".join(g.get("sources", [])[:3]), graded=True)
    order = {"A": 0, "B": 1, "C": 2, "F": 3}
    rows.sort(key=lambda r: (r["direction"] != "up", order.get(r["grade"], 4), -r["pm_dvol_m"]))
    if not rows:   # keep one placeholder row so the dashboard can still show the scan time
        meta = json.load(open(os.path.join(out, "meta.json"))) if os.path.exists(os.path.join(out, "meta.json")) else {}
        rows = [{"symbol": "(none)", "placeholder": True, "direction": "none", "scan_date": meta.get("scan_date", ""),
                 "scan_time": meta.get("scan_time", ""), "graded": False, "grade": "", "pm_dvol_m": 0}]
    json.dump(rows, open(os.path.join(out, "premarket.json"), "w"), separators=(",", ":"))
    print(json.dumps({"rows": len(rows), "graded": sum(r["graded"] for r in rows),
                      "by_grade": {k: sum(r["grade"] == k for r in rows) for k in "ABCF"}}))


if __name__ == "__main__":
    if sys.argv[1] == "prepare":
        a = [x for x in sys.argv[2:] if not x.startswith("--live=")]
        live = next((x.split("=", 1)[1] for x in sys.argv if x.startswith("--live=")), None)
        prepare(a[0], a[1], a[2], int(a[3]) if len(a) > 3 else 20, int(a[4]) if len(a) > 4 else 8, live)
    else:
        finish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
