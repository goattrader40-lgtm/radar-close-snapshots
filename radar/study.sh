#!/usr/bin/env bash
# Test-only study commands of radar-tools, kept out of the workflow file (its run script has a 21,000-character limit).
#   bars6y        daily bars of the scanner's universe since Dec 2020 -> the scratch branch radar-study, bars_6y.json.gz
#   orh [NAME]    the opening-range / level study on 1-minute bars: history/NAME.json (default orh_request) and
#                 history/NAME_levels.json -> radar-data probe_orh.json
#   paraall       the parabolic short study on the whole US market (radar/probe_para.py) -> radar-study para_all_cases.json, raw_para_all.json.gz
#   raw NAME      the 1-minute bars of the stock-days in history/NAME.json -> the scratch branch radar-study, raw_NAME.json.gz
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
  paraall)
    python3 radar/probe_para.py cases /tmp/para_all_cases.json
    python3 radar/publish.py --branch radar-study "parabolic short study: whole-market trade days" /tmp/para_all_cases.json
    python3 radar/probe_para.py raw /tmp/raw_para_all.json.gz /tmp/para_all_cases.json
    python3 radar/publish.py --branch radar-study "parabolic short study: whole-market 1-minute bars" /tmp/raw_para_all.json.gz;;
esac
