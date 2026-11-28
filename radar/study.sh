#!/usr/bin/env bash
# Test-only study commands of radar-tools, kept out of the workflow file (its run script has a 21,000-character limit).
#   bars6y        daily bars of the scanner's universe since Dec 2020 -> the scratch branch radar-study, bars_6y.json.gz
#   orh [NAME]    the opening-range / level study on 1-minute bars: history/NAME.json (default orh_request) and
#                 history/NAME_levels.json -> radar-data probe_orh.json
#   paraall       the parabolic short study on the whole US market (radar/probe_para.py) -> radar-study para_all_cases.json, raw_para_all.json.gz
#   raw NAME      the 1-minute bars of the stock-days in history/NAME.json -> the scratch branch radar-study, raw_NAME.json.gz
#   gapdown       the gap-down short study's 1-minute bars (the user, Nov 23 2026): history/gapdown_2023 ... 2026.json (every
#                 5%+ gap-down day since Jan 2023 in the liquid universe) -> radar-study, raw_gapdown_YEAR.json.gz, a year at a time
#   gapticks      the trades of the minutes where an entry's own bar also touched the stop (history/gapdown_ticks.json):
#                 which came first -> radar-study, gapdown_ticks_out.json
#   gapnews       why each gap-down happened: the SEC's 8-Ks (item 2.02 = earnings) and the morning's headlines
#                 (history/gapdown_news_request.json) -> radar-study, gapdown_news.json.gz
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
  gapticks)
    python3 radar/probe_ticks.py history/gapdown_ticks.json /tmp/gapdown_ticks_out.json
    python3 radar/publish.py --branch radar-study "trades inside the entry minute: gap-down days (study check)" /tmp/gapdown_ticks_out.json;;
  gapnews)
    python3 radar/probe_gapnews.py history/gapdown_news_request.json /tmp/gapdown_news.json.gz
    python3 radar/publish.py --branch radar-study "the news behind the gap-down days (study)" /tmp/gapdown_news.json.gz;;
  gapdaily)
    python3 radar/probe_daily.py /tmp/gapdown_daily.json.gz history/gapdown_2023.json history/gapdown_2024.json history/gapdown_2025.json history/gapdown_2026.json
    python3 radar/publish.py --branch radar-study "daily bars from Alpaca: gap-down days (study check)" /tmp/gapdown_daily.json.gz;;
  paraall)
    python3 radar/probe_para.py cases /tmp/para_all_cases.json
    python3 radar/publish.py --branch radar-study "parabolic short study: whole-market trade days" /tmp/para_all_cases.json
    python3 radar/probe_para.py raw /tmp/raw_para_all.json.gz /tmp/para_all_cases.json
    python3 radar/publish.py --branch radar-study "parabolic short study: whole-market 1-minute bars" /tmp/raw_para_all.json.gz;;
esac
