#!/usr/bin/env python3
"""The earnings breakdown alert (the 🔻 short box: radar/alerts.py ebd_*) on the days kept in ebd_cases.json, replayed
minute by minute as the live job sees them (sim_ebd.replay_day). No network, no study files.

  python3 tools/gapdown/test_ebd.py          every case must do what its "expect" says; exits 1 on a difference"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sim_ebd as M  # noqa: E402
A = M.A


def run_case(c):
    r = M.replay_day(c["date"], c["sym"], c["stock"], [tuple(b) for b in c["bars"]], c["earnings"], c["last_day"])
    a = r["alert"]
    return r, {"alert": a["t"] if a else None, "price": a["price"] if a else None, "tight": ("TIGHT STOP" in a["title"]) if a else None,
               "orl": a["lv"]["orl"] if a else None, "orh": a["lv"]["orh"] if a else None, "start": a["lv"]["start"] if a else None,
               "back": r.get("back") or [], "stopped": r["stopped"]["at"] if r["stopped"] else None, "lost": r["lost"]["why"] if r["lost"] else None,
               "skip": bool(r["skip"])}


def main():
    bad = 0
    for c in json.load(open(os.path.join(HERE, "ebd_cases.json")))["cases"]:
        r, got = run_case(c)
        ok = got == c["expect"]
        bad += not ok
        a = r["alert"]
        print(("ok   " if ok else "FAIL ") + f"{c['date']} {c['sym']:<5} {c['note']}")
        print("       " + (f"alert {a['t']} at ${a['price']:.2f}, short under ${a['lv']['orl']:.2f}, stop ${a['lv']['orh']:.2f}" + (", TIGHT" if got["tight"] else ", wide")
                           + (f", BACK ON {', '.join(got['back'])}" if got["back"] else "") + (f", stopped {got['stopped']}" if got["stopped"] else "")
                           + (f", as a trade from the alert's price {a['r']:+.2f}R" if a.get("r") is not None else "") if a else "no alert" + (f" ({r['skip']})" if r["skip"] else "")))
        if not ok:
            print("       expected", c["expect"], "\n       got     ", got)
    # the pieces on their own
    st = {"price": 100.0, "ema50": 95.0, "sma200": 90.0, "adr_20": 4.0, "mcap_b": 5.0, "avg_vol_20": 2e6, "dvol_20_m": 200.0}
    checks = [
        ("strong yesterday: the close over the 50 EMA and the 200 SMA", A.ebd_strong(st) is True and A.ebd_strong(dict(st, sma200=110.0)) is False and A.ebd_strong(dict(st, ema50=None)) is None),
        ("the Earnings tab's row reacts today: its reaction day", A.ebd_reacts({"react_day": "2026-11-30"}, "2026-11-30", "2026-11-27") and not A.ebd_reacts({"react_day": "2026-11-27"}, "2026-11-30", "2026-11-27")),
        ("... a report before today's open, not graded yet", A.ebd_reacts({"when": "bmo", "date": "2026-11-30"}, "2026-11-30", "2026-11-27") and not A.ebd_reacts({"when": "bmo", "date": "2026-11-27"}, "2026-11-30", "2026-11-27")),
        ("... a report after the last close", A.ebd_reacts({"when": "amc", "date": "2026-11-27"}, "2026-11-30", "2026-11-27") and not A.ebd_reacts({"when": "amc", "date": "2026-11-30"}, "2026-11-30", "2026-11-27")),
        ("the alert shows the Earnings tab's grade and reason", A.ebd_earnings("X", [0] * 8, {"X": {"react_day": "d", "read": "Bearish", "why": "revenue miss -3.8%, EPS miss -11.0%, pre-market -9%"}}, "d", "p", 0, 0)
         == "Bearish: revenue miss -3.8%, EPS miss -11.0%"),
        ("... 'reports today' before the tab graded it", A.ebd_earnings("X", [0] * 8, {"X": {"when": "bmo", "date": "d"}}, "d", "p", 0, 0) == "reports today, not graded yet"),
        ("... Yahoo's earnings time for a stock the tab doesn't list", A.ebd_earnings("X", [0, 0, 0, 0, 0, 0, 500, 0], {}, "d", "p", 100, 1000) == "reported since the last close"
         and A.ebd_earnings("X", [0, 0, 0, 0, 0, 0, 50, 0], {}, "d", "p", 100, 1000) is None),
        ("a stock under $700M, 700K shares or $20M a day is left out", A.morning_static(st, A.EBD_LIQ) and not A.morning_static(dict(st, mcap_b=0.5), A.EBD_LIQ)
         and not A.morning_static(dict(st, avg_vol_20=5e5), A.EBD_LIQ) and not A.morning_static(dict(st, dvol_20_m=15.0), A.EBD_LIQ)),
        ("a short alert is a trigger; its BACK ON stays on the portal", A.is_trigger("X:ebd", "") and A.is_trigger("X:ebdback0940", "") and "ebdback0940".startswith(A.PAGE_ONLY) and not "ebd".startswith(A.PAGE_ONLY)),
    ]
    for name, ok in checks:
        bad += not ok
        print(("ok   " if ok else "FAIL ") + name)
    print("all passed" if not bad else f"{bad} FAILED")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
