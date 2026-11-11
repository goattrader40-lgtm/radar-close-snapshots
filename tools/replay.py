#!/usr/bin/env python3
"""Replay stocks day by day through the Launches follow (scanner/launch.py), to check a read against your chart.

Data: daily bars from the radar-data branch's long_bars.json (fetch them first; SPY comes with every fetch):
  gh workflow run radar-tools.yml --ref main -f cmd="long ARM TTAN"      (about 2 minutes)
  git fetch -q origin radar-data

  python3 tools/replay.py ARM 2026-03-25 2026-05-29 --pick    one stock: the days with a signal (--all: every day)
  python3 tools/replay.py --regress                            every agreed example (tools/examples.txt), compared with
                                                               tools/expected_reads.txt; prints the differences
  python3 tools/replay.py --regress --write                    rewrite tools/expected_reads.txt (only after the user
                                                               agreed the new reads)
--pick follows the stock as the user's pick (the Follow button) from that day's close; without it, as a launch on
that day. Each line: the date, the close, the leg, the status after the close, and the next buy point.
"""
import argparse, difflib, gzip, json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scanner"))
import launch  # noqa: E402

SIGNALS = ("Launch day", "breakout", "Breakout", "Retest", "Tight", "Pop", "Flag", "Bull flag", "Bull pennant", "Pennant", "Push", "21 EMA retest", "21 EMA undercut", "50 EMA undercut", "try of", "Launch attempt", "BACK ON", "FAILED", "confirms the launch")
EXAMPLES = os.path.join(ROOT, "tools", "examples.txt")
EXPECTED = os.path.join(ROOT, "tools", "expected_reads.txt")


def radar_data(name):
    return subprocess.run(["git", "show", f"origin/radar-data:{name}"], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def load_all():
    """the stocks in long_bars.json, loaded the way the nightly scan loads them"""
    bars, stocks = json.loads(radar_data("long_bars.json")), radar_data("stocks.json")
    meta = {r["symbol"]: r for r in json.loads(stocks)}
    tmp = tempfile.mkdtemp()
    bp, sp = os.path.join(tmp, "bars.json.gz"), os.path.join(tmp, "stocks.json")
    with gzip.open(bp, "wt") as f:
        json.dump({"market_cap": {s: (meta.get(s, {}).get("mcap_b") or 10) * 1e9 for s in bars},
                   "exchange": {s: meta.get(s, {}).get("exchange", "NASDAQ") for s in bars}, "bars": bars}, f)
    open(sp, "w").write(stocks)
    return launch.load(bp, sp)[0]


def walk(A, sym, d0, d1, pick, every=False):
    a = A[sym]
    st = a.st
    i0 = st.dates.index(d0)
    i1 = st.dates.index(d1) if d1 in st.dates else len(st.dates) - 1
    out = [f"{sym} from {d0}" + (" (pick)" if pick else " (launch)")]
    for j in range(i0, i1 + 1):
        f = launch.follow(a, i0, j, pick=pick)
        if every or j == i0 or any(w in f["stage"] for w in SIGNALS) or (f.get("off_since") == st.dates[j]):
            out.append(f"  {st.dates[j]} c {st.c[j]:.2f} | leg {f['leg']} | {f['stage']} | next buy point {f['buy_point']} {f['pattern']}")
    return out


def regress(A):
    lines = []
    for row in open(EXAMPLES):
        row = row.split("#")[0].split()
        if not row:
            continue
        sym, d0, d1, kind = row[0], row[1], row[2], row[3] if len(row) > 3 else "launch"
        if sym not in A:
            lines.append(f"{sym}: no bars (fetch it with the long command)")
            continue
        lines += walk(A, sym, d0, d1, kind == "pick")
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sym", nargs="?")
    ap.add_argument("start", nargs="?")
    ap.add_argument("end", nargs="?", default="2099-01-01")
    ap.add_argument("--pick", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--regress", action="store_true")
    ap.add_argument("--write", action="store_true")
    a_ = ap.parse_args()
    A = load_all()
    if a_.regress:
        got = regress(A)
        if a_.write:
            open(EXPECTED, "w").write("\n".join(got) + "\n")
            print(f"wrote {EXPECTED}: {len(got)} lines")
            return
        want = open(EXPECTED).read().splitlines()
        diff = list(difflib.unified_diff(want, got, "agreed", "now", lineterm="", n=0))
        print("\n".join(diff) if diff else "every agreed example reads the same")
        return
    print("\n".join(walk(A, a_.sym, a_.start, a_.end, a_.pick, a_.all)))


if __name__ == "__main__":
    main()
