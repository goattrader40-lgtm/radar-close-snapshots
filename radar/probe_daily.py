#!/usr/bin/env python3
"""A check of the gap-down study's daily bars (Yahoo) against Alpaca's (the user, Nov 22 2026: "you need to analyze and
check your datas"). A test tool only: nothing live reads it.

  python3 radar/probe_daily.py /tmp/gapdown_daily.json.gz history/gapdown_2023.json [history/gapdown_2024.json ...]

The requests are {date: [symbols]}. For each stock-day it saves Alpaca's daily bar of that day and the close of the
session before, twice: adjusted for splits only ("s", what the study uses) and for splits, dividends and spin-offs
("a"): a gap that is there in "s" and gone in "a" is a payout, not a gap.
Saved: {"date SYMBOL": {"s": [close before, open, high, low, close, volume], "a": [close before, open]}}."""
import gzip, json, sys, time, urllib.error, urllib.parse, urllib.request
import probe_orh

START, END = "2022-12-01T00:00:00Z", "2026-11-21T00:00:00Z"


def daily(syms, adjustment):
    out, token = {}, None
    while True:
        q = {"symbols": ",".join(syms), "timeframe": "1Day", "feed": "sip", "adjustment": adjustment, "limit": 10000,
             "start": START, "end": END}
        if token:
            q["page_token"] = token
        for attempt in range(5):
            try:
                with urllib.request.urlopen(urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q), headers=probe_orh.HDR), timeout=60) as r:
                    res = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 or e.code >= 500:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise
        else:
            raise RuntimeError("alpaca kept failing")
        for s, bs in (res.get("bars") or {}).items():
            out.setdefault(s, []).extend((b["t"][:10], b["o"], b["h"], b["l"], b["c"], b.get("v", 0)) for b in bs)
        token = res.get("next_page_token")
        time.sleep(0.35)
        if not token:
            return out


def main():
    want = {}
    for path in sys.argv[2:]:
        for date, syms in json.load(open(path)).items():
            for s in syms:
                want.setdefault(s, set()).add(date)
    syms = sorted(want)
    out, errors = {}, []
    for k in range(0, len(syms), 100):
        part = syms[k:k + 100]
        try:
            S, A = daily(part, "split"), daily(part, "all")
        except Exception as e:
            errors.append(f"{part[0]}-{part[-1]}: {e}")
            continue
        for s in part:
            bs, ba = sorted(S.get(s, [])), {b[0]: b for b in A.get(s, [])}
            for i, b in enumerate(bs):
                if b[0] in want[s] and i:
                    p = bs[i - 1]
                    out[f"{b[0]} {s}"] = {"s": [p[4], b[1], b[2], b[3], b[4], b[5]],
                                          "a": [ba[p[0]][4], ba[b[0]][1]] if p[0] in ba and b[0] in ba else None}
        print(k, len(out), flush=True)
    with gzip.open(sys.argv[1], "wt") as f:
        json.dump({"requested": sum(len(v) for v in want.values()), "found": len(out), "errors": errors[:50], "rows": out}, f, separators=(",", ":"))


if __name__ == "__main__":
    main()
