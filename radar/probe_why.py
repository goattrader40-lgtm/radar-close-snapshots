#!/usr/bin/env python3
"""What the reason on the after-the-open alerts would have said (the user, Nov 17 2026: "show me what the MOH and CNC
alerts of Nov 16 would have said"). A replay, nothing live reads it.

  python3 radar/probe_why.py <out.json> <stocks.json> <alerts.json of that day> [SYM ...]

Every morning breakout and GROUP MOVE alert of the day in alerts.json (or only those of the named stocks) gets its news
line again from the live code (codegrade.stock_news with Yahoo, alerts.group_reasons) as of the minute it fired: the
headline sources answer with their publish times, so only what was out by then counts. Then the follow-up check
(alerts.news_followups) runs every 5 minutes to the close, as the day job would.
"""
import datetime, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alerts, codegrade  # noqa: E402

out_p, stocks_p, alerts_p, only = sys.argv[1], sys.argv[2], sys.argv[3], {s.upper() for s in sys.argv[4:]}
S = {s["symbol"]: s for s in json.load(open(stocks_p))}
A = json.load(open(alerts_p))
day = datetime.date.fromisoformat(A["date"])
T = lambda hm: datetime.datetime(day.year, day.month, day.day, int(hm[:2]), int(hm[3:]), tzinfo=codegrade.NY)
res = {"day": A["date"], "alerts": [], "followups": [], "headlines": {}}
state = {"items": [it for it in A.get("items", [])], "sent": []}
ev = []
for it in A.get("items", []):
    k = it["key"]
    if k.endswith(":mbo") and not k.startswith("mbatch") and (not only or k.split(":")[0] in only):
        ev.append((it["time"], "mbo", k.split(":")[0], it))
    elif k.startswith("grp:") and not k.startswith("grp:news:"):
        syms = [x.strip() for x in it["title"].rsplit(": ", 1)[-1].split(",")]
        if not only or only & set(syms):
            ev.append((it["time"], "grp", k[4:], dict(it, syms=syms)))
for hm, kind, name, it in sorted(ev, key=lambda e: e[0]):
    now = T(hm)
    try:
        if kind == "mbo":
            N = codegrade.stock_news([name], S, {}, now, yahoo=True)
            words = alerts.news_words(N.get(name))
            if (N.get(name) or {}).get("checked") and not N[name].get("today"):
                state.setdefault("why", {})[name] = {"t": hm, "syms": [name], "what": f"{name} morning breakout {hm}", "push": False}
        else:
            words = alerts.group_reasons({name: [(s, "", hm) for s in it["syms"]]}, state, S, now).get(name, "")
    except Exception as e:
        words = f" · ERROR {e!r}"
    old = it["msg"]
    res["alerts"].append({"time": hm, "key": it["key"], "title": it["title"], "was": old[old.find(" · news:"):] if " · news:" in old else "(no news line)",
                          "now": words})
syms = sorted({x for w in (state.get("why") or {}).values() for x in w["syms"]} | {e[2] for e in ev if e[1] == "mbo"})
try:
    H = codegrade.all_headlines(syms, codegrade.last_close_time(A["date"]), T("16:00"))
    for s, arts in H.items():
        res["headlines"][s] = [{"at": codegrade.when_words(codegrade.art_time(n), T("16:00")), "source": n.get("source"), "via": n.get("via") or "alpaca",
                                "title": n.get("headline"), "tags": (n.get("symbols") or [])[:10], "story": codegrade.story_ok(n)} for n in arts]
except Exception as e:
    res["headlines_error"] = repr(e)[:200]
res["waiting_after_alerts"] = sorted(state.get("why") or {})
t = T("09:40")
while t <= T("16:00"):
    try:
        for a in alerts.news_followups(state, S, t):
            res["followups"].append({"time": f"{t:%H:%M}", "key": a[0], "title": a[1], "msg": a[2], "phone": a[0] not in alerts._NO_PUSH})
    except Exception as e:
        res["followups"].append({"time": f"{t:%H:%M}", "error": repr(e)[:200]})
    t += datetime.timedelta(minutes=5)
res["never_found"] = sorted(state.get("why") or {})
json.dump(res, open(out_p, "w"), indent=1)
print(json.dumps({k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in res.items()}))
