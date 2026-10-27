#!/usr/bin/env python3
"""Keeps the live quote volume honest against the consolidated tape, for relative volume at time.

Yahoo's live volume runs ahead of the exact volume during the session (Oct 27 2026, 10:53 ET: a median +11%
over Alpaca SIP, +2% to +46%), by an amount that holds steady for a while: between two snapshots 18 minutes
apart Yahoo's increase matched SIP's within 1-3%. By the close it is gone (the day's volume matches SIP within
about 1%). Alpaca's free plan serves SIP minute bars 15 minutes late, so on each live update (radar/live.py):
  1. today's Yahoo volumes are kept (a state file in the job's work folder),
  2. once a kept snapshot is 16+ minutes old, SIP volume from 9:30 to each stock's quote time in it is added up
     from 1-minute bars (only the minutes since the last check are downloaded),
  3. offset = Yahoo volume then - SIP volume then, and the live volume = Yahoo volume now - offset
     (never less than the SIP volume then).
Snapshots before 9:34 aren't used (the opening auction prints in the first second of the 9:30 bar). So the
first correction lands around 9:55; before that, and from 4:00 on, the raw Yahoo volume is used.
Needs ALPACA_KEY_ID / ALPACA_SECRET; without them, or if Alpaca fails, nothing is corrected.
"""
import concurrent.futures as cf, datetime, json, os, sys, threading, time, urllib.error, urllib.parse, urllib.request, zoneinfo

NY = zoneinfo.ZoneInfo("America/New_York")
UTC = datetime.timezone.utc
ALPACA = "https://data.alpaca.markets/v2/stocks/bars"
DELAY = 16.5 * 60              # the free plan's 15 minutes, plus margin
KEEP = 6                       # snapshots waiting for their SIP minutes (5 minutes apart)


def mins(ts, day):
    """minutes from 9:30 on day to the epoch time ts (fractional)"""
    t0 = datetime.datetime(day.year, day.month, day.day, 9, 30, tzinfo=NY).timestamp()
    return (ts - t0) / 60


class Alpaca:
    def __init__(self, key, sec):
        self.hdr = {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": sec, "Accept": "application/json"}
        self.lock, self.clock, self.calls = threading.Lock(), 0.0, 0

    def call(self, q):
        url = ALPACA + "?" + urllib.parse.urlencode(q)
        for attempt in range(5):
            with self.lock:                                  # stay under 200 calls a minute across threads
                wait = self.clock + 0.32 - time.time()
                if wait > 0:
                    time.sleep(wait)
                self.clock = time.time()
                self.calls += 1
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=self.hdr), timeout=40) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    raise RuntimeError(f"alpaca refused ({e.code}): {e.read().decode(errors='replace')[:200]}")
                time.sleep(5 * (attempt + 1) if e.code == 429 else 2 * (attempt + 1))
            except Exception:
                time.sleep(2 * (attempt + 1))
        raise RuntimeError("alpaca: too many failures")

    def minutes(self, syms, day, k0, k1):
        """{alpaca sym: {minute index: volume}} for minutes k0..k1 (inclusive) after 9:30"""
        t0 = datetime.datetime(day.year, day.month, day.day, 9, 30, tzinfo=NY)
        z = lambda t: t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

        def job(chunk):
            q = {"symbols": ",".join(chunk), "timeframe": "1Min", "feed": "sip", "adjustment": "raw", "limit": 10000,
                 "start": z(t0 + datetime.timedelta(minutes=k0)), "end": z(t0 + datetime.timedelta(minutes=k1, seconds=30))}
            got = {}
            while True:
                res = self.call(q)
                for s, rows in (res.get("bars") or {}).items():
                    d = got.setdefault(s, {})
                    for b in rows:
                        k = int(round(mins(datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).timestamp(), day)))
                        if k0 <= k <= k1:
                            d[k] = d.get(k, 0) + (b.get("v") or 0)
                if not res.get("next_page_token"):
                    return got
                q["page_token"] = res["next_page_token"]

        out = {}
        with cf.ThreadPoolExecutor(4) as pool:
            for got in pool.map(job, [syms[i:i + 200] for i in range(0, len(syms), 200)]):
                out.update(got)
        return out


def offsets(rows, state_p, syms, now=None):
    """{sym: (offset, SIP volume at the calibration)} for the live rows {sym: [price, chg, volume, quote time, ...]},
    from the newest snapshot at least 16.5 minutes old. Saves this run's snapshot to state_p."""
    now = now or datetime.datetime.now(NY)
    day = now.date()
    try:
        st = json.load(open(state_p))
    except Exception:
        st = {}
    if st.get("date") != day.isoformat():
        st = {"date": day.isoformat(), "snaps": [], "k": 0, "cum": {}, "off": {}}
    if mins(now.timestamp(), day) >= 4:
        st["snaps"].append({"t": now.timestamp(), "v": {s: [v[2], v[3]] for s, v in rows.items()
                                                       if s in syms and v[2] and v[3] and mins(v[3], day) >= 0}})
    ready = [x for x in st["snaps"] if x["t"] + DELAY <= now.timestamp()]
    key, sec = os.environ.get("ALPACA_KEY_ID"), os.environ.get("ALPACA_SECRET")
    if ready and key and sec:
        snap = ready[-1]
        ks = int(mins(snap["t"], day))                       # the minute the snapshot was taken in
        k = st["k"]
        al = {s.replace("/", "."): s for s in snap["v"]}
        try:
            api = Alpaca(key, sec)
            got = api.minutes(sorted(al), day, k, ks)
            print(f"sipcal: SIP minutes {k}-{ks} for {len(got)} stocks, {api.calls} calls", file=sys.stderr)
        except Exception as e:
            print(f"sipcal: {e}", file=sys.stderr)
            got = None
        if got is not None:
            for a, s in al.items():
                pm = got.get(a, {})
                vol, qt = snap["v"][s]
                x = min(mins(qt, day), ks + 0.999)
                j = int(x)
                sip = st["cum"].get(s, 0) + sum(pm.get(m, 0) for m in range(k, j)) + (pm.get(j, 0) * (x - j) if j >= k else 0)
                if sip > 0:
                    st["off"][s] = [round(vol - sip), round(sip)]
                st["cum"][s] = st["cum"].get(s, 0) + sum(pm.get(m, 0) for m in range(k, ks))
            st["k"] = ks                                     # minute ks is fetched again next time
            st["snaps"] = [x for x in st["snaps"] if x["t"] > snap["t"]]
    st["snaps"] = st["snaps"][-KEEP:]
    json.dump(st, open(state_p, "w"), separators=(",", ":"))
    return {s: tuple(v) for s, v in st["off"].items()}
