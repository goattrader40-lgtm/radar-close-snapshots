#!/usr/bin/env python3
"""The pop to VWAP that fails, on 1- / 2- / 3- / 5- / 10- / 15-minute candles (the user, Nov 27 2026: "why you go based on
5 min chart vs 3 min chart for vwap pop short ... why not 3 mins?").

  python3 vwap_tf.py trades_out.json OUT.json raw_gapdown_2023.json.gz [...]

Saved {stock-day: {"3": trade, "5": trade, "3w4": the 3-minute candle with 4 candles of patience (12 minutes, near the
5-minute rule's 15) ...}}."""
import gzip, json, sys
import scenarios as S

SIZES = (1, 2, 3, 5, 10, 15)


def main():
    rows = json.load(open(sys.argv[1]))["rows"]
    out = {}
    for path in sys.argv[3:]:
        d = json.load(gzip.open(path, "rt"))
        for key, bs in d["bars"].items():
            date, sym = key.split()
            key = f"{date} {sym.replace('.', '/')}"
            if key not in rows:
                continue
            bs = sorted(b for b in bs if b[0] < (210 if date in S.HALF_DAYS else 390))
            r = {str(n): S.vwap_fail(bs, n) for n in SIZES}
            r["3w4"] = S.vwap_fail(bs, 3, 4)
            r["1w14"] = S.vwap_fail(bs, 1, 14)
            r = {k: v for k, v in r.items() if v}
            if r:
                out[key] = r
    json.dump(out, open(sys.argv[2], "w"), separators=(",", ":"))
    print("stock-days", len(rows), "| signals:", {k: sum(1 for v in out.values() if k in v) for k in [str(n) for n in SIZES] + ["3w4", "1w14"]})


if __name__ == "__main__":
    main()
