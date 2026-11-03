#!/usr/bin/env python3
"""Source check for the Earnings tab (test/earnings): can a GitHub job reach each free source, and what does it give?

  python3 radar/probe_earnings.py <out.json> SYM [SYM ...]

Checks, each on its own so one failure doesn't hide the others:
  nasdaq   the week's earnings calendar (api.nasdaq.com), Mon-Fri of this week: symbol, before open / after close,
           EPS forecast
  yahoo    per symbol: quoteSummary earningsHistory / earningsTrend / calendarEvents / earnings, and the
           fundamentals timeseries (quarterly revenue and diluted EPS)
  sec      per symbol: the newest 8-K with item 2.02 (results), its press release exhibit (99.1) and the text around
           its outlook / guidance words. The SEC wants a contact in the User-Agent: SEC_UA (a secret) if set.
"""
import datetime, json, os, re, sys, time, urllib.parse, urllib.request, zoneinfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live import Yahoo, UA  # noqa: E402

NY = zoneinfo.ZoneInfo("America/New_York")
SEC_UA = (os.environ.get("SEC_UA") or "").strip() or "radar-close-snapshots research"


def http(url, ua, timeout=25):
    rq = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "application/json, text/html, */*",
                                              "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(rq, timeout=timeout) as r:
        return r.read()


def nasdaq_week():
    today = datetime.datetime.now(NY).date()
    mon = today - datetime.timedelta(days=today.weekday())
    out = {}
    for i in range(5):
        d = (mon + datetime.timedelta(days=i)).isoformat()
        try:
            j = json.loads(http(f"https://api.nasdaq.com/api/calendar/earnings?date={d}", UA))
            rows = ((j.get("data") or {}).get("rows")) or []
            out[d] = {"n": len(rows), "sample": rows[:3]}
        except Exception as e:
            out[d] = {"error": repr(e)[:200]}
        time.sleep(0.5)
    return out


def yahoo(syms):
    y = Yahoo()
    if not y.login():
        return {"error": "no crumb"}
    out = {}
    now = int(time.time())
    for s in syms:
        r = {}
        try:
            url = (f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{urllib.parse.quote(s)}"
                   f"?modules=earningsHistory,earningsTrend,calendarEvents,earnings&crumb={urllib.parse.quote(y.crumb)}")
            res = json.loads(y.get(url))["quoteSummary"]["result"][0]
            eh = (res.get("earningsHistory") or {}).get("history") or []
            r["eps_history"] = [{k: (h.get(k) or {}).get("fmt") if isinstance(h.get(k), dict) else h.get(k)
                                 for k in ("quarter", "period", "epsActual", "epsEstimate", "surprisePercent")} for h in eh]
            tr = (res.get("earningsTrend") or {}).get("trend") or []
            r["trend"] = [{"period": t.get("period"), "end": t.get("endDate"),
                           "eps_avg": ((t.get("earningsEstimate") or {}).get("avg") or {}).get("raw"),
                           "eps_yago": ((t.get("earningsEstimate") or {}).get("yearAgoEps") or {}).get("raw"),
                           "rev_avg": ((t.get("revenueEstimate") or {}).get("avg") or {}).get("raw"),
                           "rev_yago": ((t.get("revenueEstimate") or {}).get("yearAgoRevenue") or {}).get("raw"),
                           "eps_7d_ago": ((t.get("epsTrend") or {}).get("7daysAgo") or {}).get("raw")} for t in tr]
            ce = (res.get("calendarEvents") or {}).get("earnings") or {}
            r["calendar"] = {"dates": [d.get("fmt") for d in ce.get("earningsDate") or []],
                             "eps_avg": (ce.get("earningsAverage") or {}).get("raw"),
                             "rev_avg": (ce.get("revenueAverage") or {}).get("raw"),
                             "call": [d.get("fmt") for d in ce.get("earningsCallDate") or []] if ce.get("earningsCallDate") else None}
            q = (((res.get("earnings") or {}).get("financialsChart") or {}).get("quarterly")) or []
            r["fin_chart"] = [{"q": x.get("date"), "rev": (x.get("revenue") or {}).get("raw")} for x in q]
        except Exception as e:
            r["qs_error"] = repr(e)[:200]
        try:
            ts = (f"https://query1.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{urllib.parse.quote(s)}"
                  f"?type=quarterlyTotalRevenue,quarterlyDilutedEPS&period1={now - 86400 * 800}&period2={now}"
                  f"&crumb={urllib.parse.quote(y.crumb)}")
            res = json.loads(y.get(ts))["timeseries"]["result"]
            for t in res:
                k = (t.get("meta") or {}).get("type", ["?"])[0]
                r[k] = [(v.get("asOfDate"), (v.get("reportedValue") or {}).get("raw")) for v in (t.get(k) or []) if v]
        except Exception as e:
            r["ts_error"] = repr(e)[:200]
        try:
            q = json.loads(y.get("https://query2.finance.yahoo.com/v7/finance/quote?" + urllib.parse.urlencode(
                {"symbols": s, "crumb": y.crumb,
                 "fields": "earningsTimestamp,earningsTimestampStart,earningsTimestampEnd,isEarningsDateEstimate,"
                           "earningsCallTimestampStart,preMarketPrice,preMarketTime,marketCap"})))["quoteResponse"]["result"][0]
            r["quote"] = {k: q.get(k) for k in ("earningsTimestamp", "earningsTimestampStart", "isEarningsDateEstimate",
                                                "earningsCallTimestampStart", "preMarketPrice", "preMarketTime", "marketCap")}
        except Exception as e:
            r["quote_error"] = repr(e)[:200]
        out[s] = r
        time.sleep(0.3)
    return out


GUIDE = re.compile(r"(outlook|guidance|expects?|anticipates?|raises?|raised|reaffirm\w*|lower\w*|full[- ]year|fourth quarter|next quarter)", re.I)


def sec(syms):
    out = {"ua_from_secret": bool(os.environ.get("SEC_UA"))}
    try:
        tick = json.loads(http("https://www.sec.gov/files/company_tickers.json", SEC_UA))
        cik = {v["ticker"]: int(v["cik_str"]) for v in tick.values()}
    except Exception as e:
        out["error"] = "company_tickers: " + repr(e)[:200]
        return out
    for s in syms:
        r = {}
        try:
            c = cik.get(s)
            sub = json.loads(http(f"https://data.sec.gov/submissions/CIK{c:010d}.json", SEC_UA))
            f = sub["filings"]["recent"]
            for i, form in enumerate(f["form"]):
                if form == "8-K" and "2.02" in (f["items"][i] or ""):
                    acc = f["accessionNumber"][i]
                    r.update(filed=f["acceptanceDateTime"][i], acc=acc)
                    base = f"https://www.sec.gov/Archives/edgar/data/{c}/{acc.replace('-', '')}/"
                    idx = json.loads(http(base + "index.json", SEC_UA))
                    docs = [d["name"] for d in idx["directory"]["item"]]
                    ex = [d for d in docs if re.search(r"(ex|exh|exhibit)[-_]?99", d, re.I) and d.lower().endswith((".htm", ".html"))]
                    r["docs"] = docs[:12]
                    if ex:
                        html = http(base + ex[0], SEC_UA).decode("utf-8", "replace")
                        txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"&nbsp;|&#160;", " ", html)))
                        r["chars"] = len(txt)
                        hits = []
                        for m in GUIDE.finditer(txt):
                            if len(hits) >= 6:
                                break
                            if not hits or m.start() - hits[-1][0] > 400:
                                hits.append((m.start(), txt[max(0, m.start() - 120): m.start() + 380]))
                        r["guidance_snippets"] = [h[1] for h in hits]
                    break
        except Exception as e:
            r["error"] = repr(e)[:200]
        out[s] = r
        time.sleep(0.25)
    return out


def main():
    path, syms = sys.argv[1], sys.argv[2:]
    res = {"built_at": datetime.datetime.now(NY).isoformat(timespec="seconds")}
    for name, fn in (("nasdaq", nasdaq_week), ("yahoo", lambda: yahoo(syms)), ("sec", lambda: sec(syms))):
        t = time.time()
        try:
            res[name] = fn()
        except Exception as e:
            res[name] = {"error": repr(e)[:300]}
        res[name + "_secs"] = round(time.time() - t, 1)
    json.dump(res, open(path, "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
