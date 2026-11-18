#!/usr/bin/env bash
# radar-tools commands of the event links (called by .github/workflows/radar-tools.yml with $CMD; test builds, the portal reads none)
set -e
rd() { git fetch -q --depth 1 origin +refs/heads/radar-data:refs/remotes/origin/radar-data; mkdir -p /tmp/rd; for f in "$@"; do git show origin/radar-data:$f > /tmp/rd/$f; done; }
case "$CMD" in
  eventtest|eventtest\ *)   # ("eventtest NVDA": that one read without the tab's row, the path of a bellwether your Earnings rules leave out)
                    # the bellwether event from the live Earnings tab -> radar-data events_test.json
    rd stocks.json earnings.json
    git show origin/radar-data:events_test.json > /tmp/rd/events_prev.json 2>/dev/null || echo '{}' > /tmp/rd/events_prev.json
    A=${CMD#eventtest}; A=${A# }
    python3 radar/event.py build radar/bellwethers.json /tmp/rd/earnings.json /tmp/rd/stocks.json /tmp/events_test.json /tmp/rd/events_prev.json ${A:+--own=$A}
    python3 radar/publish.py "event test build" /tmp/events_test.json;;
  eventreplay\ *)   # a past report read again ("eventreplay NVDA 2026-08-26", "eventreplay MSFT prev GOOGL prev") -> radar-data events_replay.json
    rd stocks.json
    python3 radar/event.py replay radar/bellwethers.json /tmp/rd/stocks.json /tmp/events_replay.json ${CMD#eventreplay }
    python3 radar/publish.py "event replay" /tmp/events_replay.json;;
  links|links\ *)    # the link finder: every tradable stock's annual report read for the bellwethers' names ("links" or "links 30" minutes) -> radar-data probe_links.json
    rd stocks.json
    A=${CMD#links}; python3 radar/probe_links.py /tmp/rd/stocks.json /tmp/probe_links.json ${A# }
    python3 radar/publish.py "links probe" /tmp/probe_links.json;;
esac
