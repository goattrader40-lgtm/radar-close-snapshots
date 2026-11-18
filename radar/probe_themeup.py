#!/usr/bin/env python3
"""Replay the THEME MOVING UP alert (radar/alerts.py theme_moves; the user, Nov 18 2026) on the last month's 5-minute charts.

  python3 radar/probe_themeup.py <stocks.json> <themes.json> <launch.json> <out.json>

Every tight member of a theme or a tight industry group (today's membership) gets its 5-minute chart of the last month
from Yahoo. Each session, at every 5-minute mark from 9:35 to 4:00, the alert's own code runs on what was known then (the
price = the last finished bar's close, the change vs the session before's last bar), once per setting: 3 / 4 / 5 stocks
up 3% / 4% / 5%. Writes, per setting, how many alerts a day (themes and industry groups apart), when they came, and how the
named stocks did from the alert to the close; and every alert of the live setting, day by day (-> radar-data
probe_themeup.json). No rel vol (the 5-minute bars carry no pace).
"""
import concurrent.futures, datetime, json, os, statistics, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from alerts import NY, THEME_UP, theme_members, theme_moves  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def bars(sym):
    """{date: [(minutes since midnight at the bar's end, close)]} regular hours of the last month, 5-minute bars"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym.replace('/', '-').replace('.', '-'))}?range=1mo&interval=5m"
    for _ in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
                res = json.load(r)["chart"]["result"][0]
            out = {}
            for t, c in zip(res.get("timestamp") or [], res["indicators"]["quote"][0]["close"]):
                d = datetime.datetime.fromtimestamp(t, NY)
                if c and (9, 30) <= (d.hour, d.minute) < (16, 0):
                    out.setdefault(d.date().isoformat(), []).append((d.hour * 60 + d.minute + 5, c))
            return out
        except Exception:
            pass
    return None


def main():
    stocks_p, themes_p, launch_p, out_p = sys.argv[1:5]
    stocks, themes = json.load(open(stocks_p)), json.load(open(themes_p))
    try:
        doc = json.load(open(launch_p))
    except Exception:
        doc = {}
    mem = theme_members(themes, stocks, THEME_UP["fit"])
    syms = sorted({s for v in mem.values() for s in v} | {"SPY"})
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        B = dict(zip(syms, ex.map(bars, syms)))
    missing = [s for s in syms if not B.get(s)]
    days = sorted({d for b in B.values() if b for d in b})
    # the close of the session before, per stock and day
    prev = {s: {d: (b[days[i - 1]][-1][1] if i and days[i - 1] in b else None) for i, d in enumerate(days)} for s, b in B.items() if b}
    variants = [(n, c) for c in (3.0, 4.0, 5.0) for n in (3, 4, 5)]
    res = {f"{n} stocks up {c:g}%+": {"days": [], "alerts": []} for n, c in variants}
    for d in days[1:]:
        y, m, dd = map(int, d.split("-"))
        last = {s: b[d][-1][1] for s, b in B.items() if b and d in b}
        spy = (100 * (last["SPY"] / prev["SPY"][d] - 1)) if last.get("SPY") and prev.get("SPY", {}).get(d) else None
        states = {k: {"sent": []} for k in res}
        idx = {s: 0 for s in B}
        px = {}
        for mark in range(9 * 60 + 35, 16 * 60 + 1, 5):
            for s, b in B.items():
                if not b or d not in b:
                    continue
                bs = b[d]
                while idx[s] < len(bs) and bs[idx[s]][0] <= mark:
                    px[s] = bs[idx[s]][1]
                    idx[s] += 1
            rows = {s: [p, 100 * (p / prev[s][d] - 1), None, None, None] for s, p in px.items() if prev[s].get(d)}
            now = datetime.datetime(y, m, dd, mark // 60, mark % 60, tzinfo=NY)
            for (n, c), k in zip(variants, res):
                st = states[k]
                for key, title, msg, _, _ in theme_moves({"rows": rows}, mem, st, now, dict(THEME_UP, min_n=n, min_chg=c), doc):
                    st["sent"].append(key)
                    names = [x.split(" +")[0] for x in msg.split(" · ") if " +" in x and not x.startswith(("all ", "and ", "first "))]
                    after = [100 * (last[s] / rows[s][0] - 1) for s in names if s in last and s in rows]
                    res[k]["alerts"].append({"day": d, "time": f"{now:%H:%M}", "title": title, "stocks": names, "more": key.endswith(":more"),
                                             "to_close": round(sum(after) / len(after), 2) if after else None})
        for k in res:
            a = [x for x in res[k]["alerts"] if x["day"] == d]
            res[k]["days"].append({"day": d, "spy": None if spy is None else round(spy, 2), "first": len([x for x in a if not x["more"]]),
                                   "more": len([x for x in a if x["more"]]),
                                   "themes": len([x for x in a if not x["more"] and x["title"].startswith("THEME")]),
                                   "by_10": len([x for x in a if not x["more"] and x["time"] < "10:00"])})
    out = {"built": datetime.datetime.now(NY).isoformat(timespec="minutes"), "sessions": days[1:], "stocks": len(syms), "missing": missing[:40],
           "n_missing": len(missing), "names": {"themes": len([k for k in mem if k[0] == "theme"]), "groups": len([k for k in mem if k[0] == "group"])},
           "settings": {}}
    for k, v in res.items():
        f = [x["first"] for x in v["days"]]
        tc = [x["to_close"] for x in v["alerts"] if not x["more"] and x["to_close"] is not None]
        out["settings"][k] = {"a_day_avg": round(sum(f) / len(f), 1) if f else None, "a_day_median": statistics.median(f) if f else None,
                              "a_day_max": max(f) if f else None, "quiet_days": len([x for x in f if x == 0]),
                              "themes_a_day": round(sum(x["themes"] for x in v["days"]) / len(f), 1) if f else None,
                              "by_10_a_day": round(sum(x["by_10"] for x in v["days"]) / len(f), 1) if f else None,
                              "second_alerts_a_day": round(sum(x["more"] for x in v["days"]) / len(f), 1) if f else None,
                              "to_close_avg": round(sum(tc) / len(tc), 2) if tc else None,
                              "to_close_up_share": round(100 * len([x for x in tc if x > 0]) / len(tc)) if tc else None,
                              "days": v["days"]}
    live = f"{THEME_UP['min_n']} stocks up {THEME_UP['min_chg']:g}%+"
    out["live_setting"] = live
    out["alerts"] = {k: res[k]["alerts"] for k in (live, "3 stocks up 5%+")}
    json.dump(out, open(out_p, "w"), indent=1)
    print(f"theme replay: {len(days) - 1} sessions, {len(syms)} stocks ({len(missing)} without bars); "
          + "; ".join(f"{k}: {v['a_day_avg']} a day" for k, v in out["settings"].items()))


if __name__ == "__main__":
    main()
