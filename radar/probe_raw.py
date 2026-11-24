#!/usr/bin/env python3
"""The 1-minute bars (regular hours, SIP) of a list of stock-days, for the EP study's intraday entries on days that are
not gap days (the user, Nov 22 2026: the first touch of the 10 / 21 EMA after an EP day, bought intraday when the price
recovers). A test tool only: nothing live reads it.

  python3 radar/probe_raw.py history/orh_touch.json /tmp/raw_orh_touch.json.gz

The request is {date: [symbols]}. Saved: {"date SYMBOL": [[minute after 9:30, open, high, low, close, volume], ...]}."""
import gzip, json, sys
import probe_orh


def main():
    req = json.load(open(sys.argv[1]))
    out, errors = {}, []
    for date, syms in sorted(req.items()):
        for k in range(0, len(syms), 50):
            try:
                B = probe_orh.bars(date, syms[k:k + 50])
            except Exception as e:
                errors.append(f"{date}: {e}")
                continue
            for s, bs in B.items():
                out[f"{date} {s}"] = [list(b) for b in sorted(bs)]
        print(date, len(out), flush=True)
    with gzip.open(sys.argv[2], "wt") as f:
        json.dump({"requested": sum(len(v) for v in req.values()), "found": len(out), "errors": errors[:50], "bars": out}, f, separators=(",", ":"))


if __name__ == "__main__":
    main()
