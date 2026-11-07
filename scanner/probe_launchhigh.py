#!/usr/bin/env python3
"""A check, not a rule (the user, Nov 7 2026, LION): "none of these days closed above the high of the launch day,
meaning that day's high is the breakout level". For each launch on a Launches list, its launch day's high and the first
close above it since; while there is none, that high would be the breakout level. Compared with the buy point the
engine gave (one launch.json per session), and with that session's own high: where the alerts would have fired at a
different level.

  python3 scanner/probe_launchhigh.py BARS.json.gz OUT.json LABEL=launch.json [LABEL=launch.json ...]

Each launch.json is an evening read (its date = the close it was read at); its buy points are the next session's
triggers, so the next session's bar says whether each level traded that day."""
import gzip
import json
import sys


def main():
    bars_p, out_p, pairs = sys.argv[1], sys.argv[2], sys.argv[3:]
    with gzip.open(bars_p, "rt") as f:
        B = json.load(f)["bars"]
    out = {"note": __doc__.split("\n\n")[0], "reads": []}
    for pair in pairs:
        label, path = pair.split("=", 1)
        doc = json.load(open(path))
        day = doc["date"]
        rows = []
        for lst in ("launches", "laggards"):
            for r in doc.get(lst, []):
                sym = r["symbol"]
                if r.get("grade") == "You" or r.get("pick"):
                    continue                                    # your picks have no launch day
                bars = B.get(sym) or []
                dates = [b[0] for b in bars]
                if r["date"] not in dates or day not in dates:
                    continue
                i0, i = dates.index(r["date"]), dates.index(day)
                hl = bars[i0][2]                                # the launch day's high
                above = next((bars[k][0] for k in range(i0 + 1, i + 1) if bars[k][4] > hl), None)
                close = bars[i][4]
                bp = r.get("buy_point")
                nxt = bars[i + 1] if i + 1 < len(bars) else None    # the session these buy points were for
                row = {"sym": sym, "list": lst, "launch": r["date"], "grade": r.get("grade"), "launch_high": round(hl, 2),
                       "first_close_above": above, "close": round(close, 2), "buy_point": bp, "pattern": r.get("pattern"),
                       "stage": (r.get("stage") or "")[:110]}
                if above is None and close < hl:
                    row["rule_level"] = round(hl, 2)
                    row["changes"] = bp is None or abs(bp - hl) > 0.005
                else:
                    row["rule_level"], row["changes"] = None, False
                if nxt:
                    row["next_day"] = nxt[0]
                    row["next_high"], row["next_close"] = round(nxt[2], 2), round(nxt[4], 2)
                    row["old_traded"] = bool(bp and nxt[2] > bp)
                    row["rule_traded"] = bool(row["rule_level"] and nxt[2] > row["rule_level"])
                rows.append(row)
        ch = [x for x in rows if x["changes"]]
        out["reads"].append({"label": label, "read_of": day, "launches": len(rows), "rule_active": sum(1 for x in rows if x["rule_level"]),
                             "level_changes": len(ch), "rows": sorted(rows, key=lambda x: (not x["changes"], x["sym"]))})
    json.dump(out, open(out_p, "w"), indent=1)
    for rd in out["reads"]:
        print(f"{rd['label']} (read of {rd['read_of']}): {rd['launches']} launches, rule active on {rd['rule_active']}, level changes on {rd['level_changes']}")


if __name__ == "__main__":
    main()
