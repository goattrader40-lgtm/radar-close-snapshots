#!/usr/bin/env bash
# The gap-down short study, start to end (research only; the user, Nov 23 2026). Run from the repo root.
# The data comes from the radar-tools job on this branch (the container can't reach Alpaca or Yahoo):
#   radar-tools "bars6y"    daily bars since Dec 2020            -> radar-study bars_6y.json.gz
#   radar-tools "gapdown"   1-minute bars of every gap-down day  -> radar-study raw_gapdown_2023..2026.json.gz
#   radar-tools "gapdaily"  the same days' daily bars, Alpaca    -> radar-study gapdown_daily.json.gz
#   radar-tools "gapticks"  trades inside the doubtful minutes   -> radar-study gapdown_ticks_out.json   (history/gapdown_ticks.json)
set -e
D=${1:-/tmp/gapdown}; mkdir -p "$D"
git fetch -q origin +refs/heads/radar-study:refs/remotes/origin/radar-study
for f in bars_6y.json.gz raw_gapdown_2023.json.gz raw_gapdown_2024.json.gz raw_gapdown_2025.json.gz raw_gapdown_2026.json.gz gapdown_daily.json.gz gapdown_ticks_out.json; do
  git show origin/radar-study:$f > "$D/$f"
done
python3 tools/gapdown/find_gaps.py "$D/bars_6y.json.gz" "$D"                                   # the gap list (+ the request files in history/)
python3 tools/gapdown/clean_gaps.py "$D/gaps.json" "$D/gapdown_daily.json.gz" "$D/gaps_clean.json"   # payouts and price-basis days out
python3 tools/gapdown/trades.py "$D/gaps_clean.json" history/gapdown_share5.json "$D/gapdown_ticks_out.json" "$D/trades.json" "$D"/raw_gapdown_20*.json.gz
python3 tools/gapdown/report.py "$D/trades.json" > "$D/results.txt"
(cd tools/gapdown && python3 make_xlsx.py "$D/trades.json" "$D/gapdown_short_study.xlsx")
# part 2 (Nov 24 2026): the gap-up rules mirrored (yesterday vs the 50 EMA / 200 SMA, the open vs the 1- / 3-month lows ...)
python3 tools/gapdown/features.py "$D/bars_6y.json.gz" "$D/gaps_clean.json" "$D/features.json"
(cd tools/gapdown && python3 mirror.py "$D/trades.json" "$D/features.json" "$D/gaps_clean.json" > "$D/results_mirrored.txt" \
  && python3 make_xlsx_mirror.py "$D/trades.json" "$D/features.json" "$D/gaps_clean.json" "$D/gapdown_short_study_mirrored_rules.xlsx")
echo "results: $D/results.txt, $D/gapdown_short_study.xlsx, $D/results_mirrored.txt, $D/gapdown_short_study_mirrored_rules.xlsx"
