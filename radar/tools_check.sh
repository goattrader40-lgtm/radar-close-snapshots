#!/bin/bash
# Check tools of a session (radar-tools.yml runs this with CMD set; the workflow's own run block is at GitHub's size limit).
#   eppcheck    the EP pullback alerts replayed on today's exact minute bars, and the plan audited (after 4:16 PM ET) -> radar-data probe_epp.json
#   alertbars   today's 1-minute bars of every alerted stock, to score the alerts after the close -> radar-data probe_alertbars.json.gz
if [ "$CMD" = "eppcheck" ]; then
  python3 radar/probe_epp.py setups/ep_pullback.json /tmp/probe_epp.json; python3 radar/publish.py "EP pullback check" /tmp/probe_epp.json
fi
if [ "$CMD" = "alertbars" ]; then
  python3 radar/probe_alertbars.py /tmp/probe_alertbars.json.gz; python3 radar/publish.py "alert bars" /tmp/probe_alertbars.json.gz
fi
exit 0
