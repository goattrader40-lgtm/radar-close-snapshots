#!/usr/bin/env bash
# Test-only study commands of radar-tools, kept out of the workflow file (its run script has a 21,000-character limit).
#   bars6y        daily bars of the scanner's universe since Dec 2020 -> the scratch branch radar-study, bars_6y.json.gz
#   orh [NAME]    the opening-range / level study on 1-minute bars: history/NAME.json (default orh_request) and
#                 history/NAME_levels.json -> radar-data probe_orh.json
#   raw NAME      the 1-minute bars of the stock-days in history/NAME.json -> the scratch branch radar-study, raw_NAME.json.gz
#   gapdown       the gap-down short study's 1-minute bars (the user, Nov 23 2026): history/gapdown_2023 ... 2026.json (every
#                 5%+ gap-down day since Jan 2023 in the liquid universe) -> radar-study, raw_gapdown_YEAR.json.gz, a year at a time
#   gapdaily      the same stock-days' daily bars from Alpaca, to check Yahoo's (the gap, the close before) -> radar-study, gapdown_daily.json.gz
set -e
CMD="$1"
case "$CMD" in
  bars6y)
    python3 radar/probe_bars.py /tmp/bars_6y.json.gz 2020-12-01
    python3 radar/publish.py --branch radar-study "daily bars since Dec 2020 (study)" /tmp/bars_6y.json.gz;;
  orh|orh\ *)
    R="${CMD#orh}"; R="${R# }"; R="${R:-orh_request}"
    python3 radar/probe_orh.py "history/$R.json" /tmp/probe_orh.json "history/${R}_levels.json" history/orh_raw.json
    python3 radar/publish.py "orh probe" /tmp/probe_orh.json;;
  raw\ *)
    R="${CMD#raw }"
    python3 radar/probe_raw.py "history/$R.json" "/tmp/raw_$R.json.gz"
    python3 radar/publish.py --branch radar-study "1-minute bars: $R (study)" "/tmp/raw_$R.json.gz";;
  gapdown)
    for Y in 2023 2024 2025 2026; do
      python3 radar/probe_raw.py "history/gapdown_$Y.json" "/tmp/raw_gapdown_$Y.json.gz"
      python3 radar/publish.py --branch radar-study "1-minute bars: gap-down days $Y (study)" "/tmp/raw_gapdown_$Y.json.gz"
    done;;
  gapdaily)
    python3 radar/probe_daily.py /tmp/gapdown_daily.json.gz history/gapdown_2023.json history/gapdown_2024.json history/gapdown_2025.json history/gapdown_2026.json
    python3 radar/publish.py --branch radar-study "daily bars from Alpaca: gap-down days (study check)" /tmp/gapdown_daily.json.gz;;
esac
