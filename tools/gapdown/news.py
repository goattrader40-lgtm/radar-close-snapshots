#!/usr/bin/env python3
"""Why each gap-down happened, from radar/probe_gapnews.py's file: earnings day or not, and what the headlines say.

  python3 news.py gapdown_news.json.gz gapdown_news_request.json reasons.json

Per stock-day:
  earn      1 = an earnings day: an 8-K with item 2.02 (results of operations) accepted between the close of the
            session before and the end of the gap day; 0 = none; None = a company that files no 8-Ks (foreign: 6-Ks).
            The headlines (Alpaca / Benzinga) only reach back to Apr 2026: hl_earn and the rest are a cross-check there
  sec202    the 8-K's acceptance time; pre = 1 when it came before the open
  eps / sales   "miss" / "beat" from the headline ("EPS $0.52 Misses $0.60 Estimate")
  guide     "cut" / "raise" / "given" from the headlines (lowers, cuts, below ... guidance / outlook / forecast)
  kinds     other reasons in the headlines: downgrade, offering, fda, deal, exec, legal / probe, short report
  n_news    headlines in the window"""
import datetime, gzip, json, re, sys

PREVIEW = re.compile(r"earnings preview|ahead of|what to expect|scheduled|to report|reports? (?:on|after|before)|preview:|stocks? (?:moving|to watch)|movers|"
                     r"earnings (?:call|date|whispers?)|set to (?:report|announce)|will (?:report|release|announce)|announces? (?:date|timing)|conference call", re.I)
RESULTS = re.compile(r"\bQ[1-4]\b|\b(?:first|second|third|fourth)[- ](?:quarter)\b|\b[1-4]Q\b|\bquarterly (?:results|earnings|profit|loss|revenue|sales)\b|"
                     r"\b(?:full[- ]year|fiscal|FY ?'?\d{2,4}|H[12])\b.{0,40}\b(?:results|EPS|sales|revenue|earnings|profit)\b|"
                     r"\bEPS\b|\b(?:reports?|posts?|announces?|delivers?)\b.{0,40}\b(?:results|earnings|profit|loss)\b|\bearnings (?:miss|beat|fall|drop|disappoint)", re.I)
EPS = re.compile(r"EPS.{0,60}?\b(beats?|miss(?:es)?|in[- ]line|inline)\b", re.I)
SALES = re.compile(r"(?:sales|revenue)s?.{0,60}?\b(beats?|miss(?:es)?|in[- ]line|inline)\b", re.I)
GUIDE = re.compile(r"guidance|outlook|forecast|\bsees\b|\bguides?\b|\bexpects? (?:FY|Q[1-4]|fiscal|full)", re.I)
CUT = re.compile(r"\b(?:cuts?|lowers?|lowered|reduces?|slash(?:es)?|trims?|withdraws?|suspends?|pulls?|below|weak|soft|disappoint\w*|misses|light|warns?|warning)\b", re.I)
RAISE = re.compile(r"\b(?:raises?|raised|boosts?|lifts?|hikes?|above|strong|increases?)\b", re.I)
VS_EST = re.compile(r"\bsees\b[^;]*?\$?(-?[\d.]+)([BMK]?)(?:\s*(?:-|to)\s*\$?(-?[\d.]+)([BMK]?))?\s*vs\.?\s*\$?(-?[\d.]+)([BMK]?)\s*est", re.I)
UNIT = {"": 1, "K": 1e3, "M": 1e6, "B": 1e9}


def vs_est(h):
    """Benzinga's "Sees Q3 Revenue $12.5B-$13.5B vs $14.35B Est": -1 below the estimate, +1 above, 0 in line, None no numbers"""
    m = VS_EST.search(h)
    if not m:
        return None
    try:
        lo = float(m.group(1)) * UNIT[m.group(2).upper()]
        hi = float(m.group(3)) * UNIT[(m.group(4) or m.group(2)).upper()] if m.group(3) else lo
        if m.group(3) and not m.group(2):                 # "$1.10-$1.20B": the unit written once, at the end
            lo = float(m.group(1)) * UNIT[(m.group(4) or "").upper()]
        est = float(m.group(5)) * UNIT[m.group(6).upper()]
    except (ValueError, KeyError):
        return None
    mid = (lo + hi) / 2
    if est == 0:
        return None
    d = (mid - est) / abs(est)
    return -1 if d < -0.005 else 1 if d > 0.005 else 0


KINDS = [("downgrade", r"\bdowngrad"), ("offering", r"\b(?:public offering|private placement|prices? .{0,30}offering|convertible|at-the-market|secondary offering|share sale)\b"),
         ("fda / trial", r"\b(?:FDA|topline|top-line|clinical|trial|phase [123i]+|endpoint|CRL|complete response)\b"),
         ("exec change", r"\b(?:CEO|CFO|chief executive|chief financial)\b.{0,60}\b(?:resign|depart|step|leave|retire|out|replac|terminat|transition)"),
         ("legal / probe", r"\b(?:investigation|probe|subpoena|lawsuit|sues?|DOJ|SEC charges|fraud|accounting|restat)\w*"),
         ("short report", r"\b(?:short[- ]seller|short report|Hindenburg|Muddy Waters|Citron|Spruce Point|Grizzly|Culper|Kerrisdale)\b"),
         ("deal", r"\b(?:to acquire|acquisition of|merger|to buy|takeover)\b"),
         ("price target cut", r"\b(?:lowers?|cuts?) (?:price )?target|price target (?:to|cut|lowered)")]
NY_OFF = None


def ny(dt_str):
    import zoneinfo
    return datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00")).astimezone(zoneinfo.ZoneInfo("America/New_York"))


def main():
    d = json.load(gzip.open(sys.argv[1], "rt"))
    req = json.load(open(sys.argv[2]))
    sec, news = d["sec"], d["news"]
    out = {}
    for date, v in req.items():
        t0, t_open, t_end = f"{v['prev']}T16:00", f"{date}T09:30", f"{date}T23:59"
        for s in v["syms"]:
            key = f"{date} {s}"
            fs = sec.get(s)
            r = {"filer": "unknown" if fs is None else "8-K" if any(f[1].startswith("8-K") for f in fs) else "6-K" if fs else "none"}
            e202 = [f for f in (fs or []) if f[1].startswith("8-K") and "2.02" in f[2] and t0 < f[0] <= t_end]
            if e202:
                r["sec202"], r["pre"] = e202[0][0], 1 if e202[0][0] <= t_open else 0
            items = sorted({x.strip() for f in (fs or []) if f[1].startswith("8-K") and t0 < f[0] <= t_open for x in f[2].split(",") if x.strip()})
            if items:
                r["items"] = ",".join(items)
            hs = [h for t, h in news.get(key, []) if h]
            r["n_news"] = len(hs)
            res = [h for h in hs if RESULTS.search(h) and not PREVIEW.search(h)]
            r["hl_earn"] = 1 if res else 0
            # the headline archive only reaches back to Apr 2026, so the earnings day is the SEC's alone: 1 / 0 for a company
            # that files 8-Ks, None for the others (foreign companies file 6-Ks, which carry no item numbers)
            r["earn"] = (1 if e202 else 0) if r["filer"] == "8-K" else None
            for nm, rx in (("eps", EPS), ("sales", SALES)):
                got = [m.group(1).lower() for h in hs for m in [rx.search(h)] if m]
                if got:
                    r[nm] = "miss" if any(g.startswith("miss") for g in got) else "beat" if any(g.startswith("beat") for g in got) else "inline"
            gh = [h for h in hs if GUIDE.search(h) and not PREVIEW.search(h)]
            if gh:
                num = [x for x in (vs_est(h) for h in gh) if x is not None]
                r["guide"] = ("cut" if any(x < 0 for x in num) or any(CUT.search(h) for h in gh if vs_est(h) is None)
                              else "raise" if any(x > 0 for x in num) or any(RAISE.search(h) for h in gh if vs_est(h) is None) else "given")
            kinds = [nm for nm, rx in KINDS if any(re.search(rx, h, re.I) for h in hs)]
            if kinds:
                r["kinds"] = kinds
            if res:
                r["hl"] = res[0][:160]
            elif hs:
                r["hl"] = hs[0][:160]
            out[key] = r
    json.dump(out, open(sys.argv[3], "w"), separators=(",", ":"))
    n = len(out)
    print("stock-days", n, "| earnings day", sum(1 for r in out.values() if r["earn"]), "| not an earnings day", sum(1 for r in out.values() if r["earn"] == 0),
          "| unknown (no 8-Ks: foreign filers)", sum(1 for r in out.values() if r["earn"] is None), "| the 8-K before the open", sum(1 for r in out.values() if r.get("pre")),
          "| with headlines", sum(1 for r in out.values() if r["n_news"]), "| filer", {k: sum(1 for r in out.values() if r["filer"] == k) for k in ("8-K", "6-K", "none", "unknown")})


if __name__ == "__main__":
    main()
