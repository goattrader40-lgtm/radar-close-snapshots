#!/usr/bin/env python3
"""Today's runners vs their 21-day closing high (test/codegrade, Nov 4 2026): which opened right under it and ripped?

  python3 scanner/probe_runners.py <stocks.json> <out.json> [min_chg]

For every liquid stock up min_chg% (default 8) on the day (stocks.json chg_1d), Yahoo's daily bars: today's open, high,
close, the highest close of the 21 sessions before today, and where the open sat against it.
"""
import json, os, sys, datetime, zoneinfo
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "radar"))
from earnings import Y  # noqa: E402

NY = zoneinfo.ZoneInfo("America/New_York")


def main():
    S = json.load(open(sys.argv[1]))
    mn = float(sys.argv[3]) if len(sys.argv) > 3 else 8
    syms = [s for s in S if (s.get("chg_1d") or 0) >= mn and (s.get("dvol_20_m") or 0) >= 20 and (s.get("price") or 0) >= 10]
    y, out = Y(), []
    today = datetime.datetime.now(NY).date().isoformat()
    for s in sorted(syms, key=lambda s: -s["chg_1d"]):
        try:
            j = y.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{s['symbol'].replace('.', '-')}?range=3mo&interval=1d")
            r = j["chart"]["result"][0]
            q = r["indicators"]["quote"][0]
            bars = [(datetime.datetime.fromtimestamp(t, NY).date().isoformat(), o, h, c) for t, o, h, c in zip(r["timestamp"], q["open"], q["high"], q["close"]) if c]
            if bars[-1][0] != today:
                continue
            d, o, h, c = bars[-1]
            prev = bars[-22:-1]
            hc = max(x[3] for x in prev)
            hw = max(x[2] for x in prev)
            out.append(dict(sym=s["symbol"], chg=s["chg_1d"], prev_close=prev[-1][3], open=round(o, 2), close=round(c, 2), high=round(h, 2),
                            gap=round(100 * (o / prev[-1][3] - 1), 1), hi21_close=round(hc, 2), hi21_high=round(hw, 2),
                            open_vs_hi21_close=round(100 * (o / hc - 1), 1), close_vs_hi21_close=round(100 * (c / hc - 1), 1),
                            adr=s.get("adr_20"), avgvol=s.get("avg_vol_20"), mcap_b=s.get("mcap_b")))
        except Exception as e:
            print(s["symbol"], repr(e)[:100])
    json.dump({"date": today, "rows": out}, open(sys.argv[2], "w"), indent=0)
    for r in out:
        print(f"{r['sym']:6} {r['chg']:+6.1f}%  gap {r['gap']:+5.1f}%  open {r['open']:>8}  21d closing high {r['hi21_close']:>8} ({r['open_vs_hi21_close']:+5.1f}%)  close {r['close']}")


if __name__ == "__main__":
    main()
