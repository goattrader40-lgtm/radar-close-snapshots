#!/usr/bin/env python3
"""The parabolic short study on the WHOLE US market (the user, Nov 28 2026: CAR Apr 22 2026, NMAX Apr 1 2025, BYND Oct 2025 —
"check" them: small caps and stocks the scanner does not hold). A test tool only: nothing live reads it.

  python3 radar/probe_para.py cases /tmp/para_all_cases.json [2020-12-01]
  python3 radar/probe_para.py raw /tmp/raw_para_all.json.gz /tmp/para_all_cases.json

1. Alpaca's asset list (active AND inactive, so stocks that later collapsed or delisted are in), common stocks on NASDAQ / NYSE / AMEX.
2. Their daily bars (SIP, split-adjusted) since the start date.
3. The trade days: 3+ up closes in a row that added 30%+ (the close 3 sessions ago -> yesterday's close), yesterday's dollar volume $20M+,
   and today the stock gaps up (open 1%+ over yesterday's close), open $1+.
4. The 1-minute bars of those days.
Saved: the cases (with the day's and the next session's daily bar) and {"date SYMBOL": [[minute, o, h, l, c, v], ...]}."""
import collections, datetime, gzip, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
import probe_orh

HDR = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
BAD = re.compile(r"\b(ETF|ETN|FUND|TRUST|WARRANT|WARRANTS|UNIT|UNITS|RIGHT|RIGHTS|PREFERRED|NOTES|DEPOSITARY SHARES? EACH|%|BULL|BEAR|2X|3X|SHARES ETF|PROSHARES|DIREXION)\b", re.I)


def get(url):
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(5 * (attempt + 1))
                continue
            raise
        except Exception:
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("alpaca kept failing: " + url[:120])


def assets(log):
    out = {}
    for host in ("https://api.alpaca.markets", "https://paper-api.alpaca.markets"):
        for status in ("active", "inactive"):
            try:
                rows = get(f"{host}/v2/assets?asset_class=us_equity&status={status}")
            except Exception as e:
                log.append(f"assets {host} {status}: {e}")
                continue
            for a in rows:
                s = a.get("symbol") or ""
                if a.get("exchange") not in ("NASDAQ", "NYSE", "AMEX") or not re.fullmatch(r"[A-Z]{1,5}", s) or BAD.search(a.get("name") or ""):
                    continue
                out.setdefault(s, {"name": (a.get("name") or "")[:60], "exchange": a.get("exchange"), "status": status})
            log.append(f"assets {host} {status}: {len(rows)} rows")
        if out:
            break
    return out


def daily(syms, start, on_symbol, log):
    """every symbol's daily bars, 200 symbols a request; on_symbol(sym, bars) once a symbol is complete"""
    n_req = 0
    for k in range(0, len(syms), 200):
        chunk = syms[k:k + 200]
        got, token = collections.defaultdict(list), None
        while True:
            q = {"symbols": ",".join(chunk), "timeframe": "1Day", "feed": "sip", "adjustment": "split", "limit": 10000, "start": start + "T00:00:00Z"}
            if token:
                q["page_token"] = token
            try:
                res = get("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q))
            except Exception as e:
                log.append(f"daily chunk {k}: {e}")
                break
            n_req += 1
            for s, bs in (res.get("bars") or {}).items():
                got[s].extend((b["t"][:10], b["o"], b["h"], b["l"], b["c"], b["v"]) for b in bs)
            token = res.get("next_page_token")
            time.sleep(0.32)
            if not token:
                break
        for s, bs in got.items():
            on_symbol(s, sorted(bs))
        if k % 2000 == 0:
            print("daily", k, len(syms), n_req, flush=True)
    return n_req


def find_cases(sym, b, meta, cases):
    o = [x[1] for x in b]; h = [x[2] for x in b]; l = [x[3] for x in b]; c = [x[4] for x in b]; v = [x[5] for x in b]
    for i in range(4, len(b) - 1):
        if not (c[i - 1] and c[i - 4] and o[i]) or o[i] < 1:
            continue
        gap = (o[i] / c[i - 1] - 1) * 100
        if gap < 1:
            continue
        ups, j = 0, i - 1
        while j > 0 and c[j] > c[j - 1]:
            ups += 1; j -= 1
        if ups < 3:
            continue
        g3 = (c[i - 1] / c[i - 4] - 1) * 100
        if g3 < 30 or c[i - 1] * v[i - 1] < 20e6:
            continue
        lo10 = min(c[max(0, i - 10):i]); lo20 = min(c[max(0, i - 20):i])
        sma10 = sum(c[max(0, i - 10):i]) / len(c[max(0, i - 10):i])
        gaps, j = 0, i
        while j > 0 and o[j] > c[j - 1] * 1.01:
            gaps += 1; j -= 1
        prior = v[max(0, i - 21):i - 1]
        vol20 = sum(prior) / len(prior) if prior else 0
        cases.append(dict(sym=sym, date=b[i][0], g3=round(g3, 1), ups=ups, gap=round(gap, 2), gaps=gaps, run=round((o[i] / lo10 - 1) * 100, 1),
                          run20=round((o[i] / lo20 - 1) * 100, 1), ext10=round((o[i] / sma10 - 1) * 100, 1), y_chg=round((c[i - 1] / c[i - 2] - 1) * 100, 1),
                          y_dvol=round(c[i - 1] * v[i - 1] / 1e6, 1), y_vol=round(v[i - 1] / vol20, 2) if vol20 else 0,
                          y_pos=round((c[i - 1] - l[i - 1]) / (h[i - 1] - l[i - 1]), 2) if h[i - 1] > l[i - 1] else 0.5, hist=i,
                          pc=c[i - 1], o=o[i], h=h[i], l=l[i], c=c[i], v=v[i], no=o[i + 1], nh=h[i + 1], nl=l[i + 1], nc=c[i + 1],
                          status=meta["status"], exchange=meta["exchange"], name=meta["name"]))


def main():
    mode, out = sys.argv[1], sys.argv[2]
    if mode == "cases":
        start = sys.argv[3] if len(sys.argv) > 3 else "2020-12-01"
        log, cases = [], []
        A = assets(log)
        print(log, len(A), flush=True)
        n_req = daily(sorted(A), start, lambda s, b: find_cases(s, b, A[s], cases), log)
        log.append(f"daily requests {n_req}, cases {len(cases)}")
        print(log[-1], flush=True)
        with open(out, "w") as f:
            json.dump({"saved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "symbols": len(A), "log": log[:60], "cases": cases}, f, separators=(",", ":"))
        return
    cases = json.load(open(sys.argv[3]))["cases"]          # mode "raw": the 1-minute bars of the cases
    req = collections.defaultdict(list)
    for x in cases:
        req[x["date"]].append(x["sym"])
    raw, errors = {}, []
    for date, syms in sorted(req.items()):
        for k in range(0, len(syms), 50):
            try:
                B = probe_orh.bars(date, syms[k:k + 50])
            except Exception as e:
                errors.append(f"{date}: {e}")
                continue
            for s, bs in B.items():
                raw[f"{date} {s}"] = [list(b) for b in sorted(bs)]
    with gzip.open(out, "wt") as f:
        json.dump({"requested": len(cases), "found": len(raw), "errors": errors[:50], "bars": raw}, f, separators=(",", ":"))
    print("raw", len(raw), "of", len(cases), flush=True)


if __name__ == "__main__":
    main()
