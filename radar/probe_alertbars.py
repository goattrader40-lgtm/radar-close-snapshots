#!/usr/bin/env python3
"""Today's 1-minute SIP bars of every stock that had an alert today, to score the alerts after the close (a check tool).

  python3 radar/probe_alertbars.py <out.json.gz>     (needs ALPACA_KEY_ID / ALPACA_SECRET; after 4:16 PM ET for the whole session)

Reads radar-data alerts.json (today's alerts), takes each stock named in an alert key and writes
{day, bars_to, rows: {SYM: [[minute after 9:30, open, high, low, close, volume], ...]}, errors}. Nothing is alerted or changed."""
import datetime, gzip, json, os, subprocess, sys, urllib.parse, urllib.request, zoneinfo

NY = zoneinfo.ZoneInfo("America/New_York")
UTC = datetime.timezone.utc
z = lambda t: t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(out):
    hdr = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET"]}
    subprocess.run(["git", "fetch", "-q", "--depth", "1", "origin", "+refs/heads/radar-data:refs/remotes/origin/radar-data"])
    al = json.loads(subprocess.run(["git", "show", "origin/radar-data:alerts.json"], capture_output=True, text=True).stdout)
    syms = sorted({it["key"].split(":")[0] for it in al.get("items") or []
                   if ":" in it.get("key", "") and not it["key"].startswith(("grp:", "thm:", "summary:", "mbatch"))} | set(sys.argv[2:]))
    now = datetime.datetime.now(NY)
    day = datetime.date.fromisoformat(al["date"])
    t0 = datetime.datetime(day.year, day.month, day.day, 9, 30, tzinfo=NY)
    end = min(now - datetime.timedelta(minutes=16), t0 + datetime.timedelta(minutes=390))
    out.update(day=str(day), bars_to=end.strftime("%H:%M"), n_syms=len(syms))
    rows = {}
    for k in range(0, len(syms), 100):
        q = {"symbols": ",".join(syms[k:k + 100]), "timeframe": "1Min", "feed": "sip", "adjustment": "raw", "limit": 10000,
             "start": z(t0), "end": z(end)}
        try:
            while True:
                req = urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q), headers=hdr)
                with urllib.request.urlopen(req, timeout=60) as r:
                    res = json.load(r)
                for s, bs in (res.get("bars") or {}).items():
                    for b in bs:
                        d = datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(NY)
                        m = d.hour * 60 + d.minute - 570
                        if d.date() == day and 0 <= m < 390:
                            rows.setdefault(s, []).append([m, b["o"], b["h"], b["l"], b["c"], b["v"]])
                if not res.get("next_page_token"):
                    break
                q["page_token"] = res["next_page_token"]
        except Exception as e:
            out["errors"].append(f"{syms[k]}..: {e!r}")
    out["rows"] = rows
    out["missing"] = [s for s in syms if s not in rows]


if __name__ == "__main__":
    o = {"errors": []}
    try:
        main(o)
    except Exception as e:                       # the job's log can't be read from a session: the error goes into the file
        import traceback
        o["errors"] += [repr(e), traceback.format_exc()[-1500:]]
    with gzip.open(sys.argv[1], "wt") as f:
        json.dump(o, f, separators=(",", ":"))
    print("alert bars:", len(o.get("rows") or {}), "stocks; errors:", o["errors"][:3])
