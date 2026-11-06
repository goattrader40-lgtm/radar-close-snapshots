#!/usr/bin/env python3
"""Theme & Group Radar: one GitHub job runs the whole market day.

  python3 radar/day.py day      # the full day (default): pre-market scans, 5-minute live prices, then the close
  python3 radar/day.py daily    # only the after-close refresh (pipeline + track record), now
  python3 radar/day.py live     # one live update, now (works any time)

Timeline (ET, trading days):
  8:25, 8:40   start the "Pre-market scan" workflow (if today's scan isn't saved yet)
  8:45, 8:55, 9:00, 9:10, 9:20   start the "Code grader" workflow after that update's pre-market prices (in by 9:05)
  9:30-4:10    every 5 minutes: live prices -> live.json on the radar-data branch
  9:31-12:00, 3:00-4:00   every minute in between: the launch watch list and the followed launches (radar/fast.py),
               for the big gap-up alerts and the breakouts
               (catalyst gaps, power days, A+/A launches; 9:31-9:34 their early heads-ups, before the volume
               means anything); alerts.json is published when one is sent
  4:06         start the "Close snapshot" workflow (if today's isn't saved yet)
  after it     pipeline.py (themes, groups, gainers, 1W/1M/3M, ADR, 200-day SMA) + gradelog.py update
               -> stocks.json, themes.json, build.json, gradelog.json on radar-data, and the job ends.
A GitHub job can run 6 hours at most, so after about 5h40m the job starts a fresh copy of itself
and stops; the copy carries on. Started by the schedule, or by hand (Actions -> Radar day -> Run workflow).
"""
import datetime, json, os, subprocess, sys, time, zoneinfo

NY = zoneinfo.ZoneInfo("America/New_York")
REPO = os.environ.get("GITHUB_REPOSITORY", "goattrader40-lgtm/radar-close-snapshots")
HERE = os.path.dirname(os.path.abspath(__file__))
WORK, OUT = "/tmp/radar/work", "/tmp/radar/out"
HOLIDAYS = set("2026-11-26 2026-12-25 2027-01-01 2027-01-18 2027-02-15 2027-03-26 2027-05-31 2027-06-18 "
               "2027-07-05 2027-09-06 2027-11-25 2027-12-24".split())
BUDGET = 5 * 3600 + 40 * 60
T0 = time.monotonic()


def log(*a):
    print(datetime.datetime.now(NY).strftime("%H:%M:%S"), *a, flush=True)


def sh(*a, check=True, cwd=None):
    r = subprocess.run(a, capture_output=True, text=True, cwd=cwd)
    if check and r.returncode:
        raise RuntimeError(f"{' '.join(a)} failed ({r.returncode}): {r.stderr.strip()[-800:]}")
    return r


def now():
    return datetime.datetime.now(NY)


def hm(t):
    return (t.hour, t.minute)


def trading_day(d):
    return d.weekday() < 5 and d.isoformat() not in HOLIDAYS


def data_file(name):
    """a file from the radar-data branch, or None"""
    sh("git", "fetch", "-q", "--depth", "1", "origin", "+refs/heads/radar-data:refs/remotes/origin/radar-data", check=False)
    r = sh("git", "show", f"refs/remotes/origin/radar-data:{name}", check=False)
    return r.stdout if r.returncode == 0 else None


def main_file(path):
    sh("git", "fetch", "-q", "--depth", "1", "origin", "+refs/heads/main:refs/remotes/origin/main", check=False)
    r = sh("git", "show", f"refs/remotes/origin/main:{path}", check=False)
    return r.stdout if r.returncode == 0 else None


def dispatch(workflow, **inputs):
    args = ["gh", "workflow", "run", workflow, "--repo", REPO, "--ref", "main"]
    for k, v in inputs.items():
        args += ["-f", f"{k}={v}"]
    r = sh(*args, check=False)
    log(f"started {workflow}" if r.returncode == 0 else f"could not start {workflow}: {r.stderr.strip()[:300]}")
    return r.returncode == 0


def premarket_saved_today():
    txt = main_file("premarket/latest.json")
    try:
        return json.loads(txt)["date"] == now().date().isoformat()
    except Exception:
        return False


def close_saved_today():
    txt = main_file("close/latest.json")
    try:
        return json.loads(txt)["saved_at"][:10] == now().date().isoformat()
    except Exception:
        return False


def live_once():
    os.makedirs(OUT, exist_ok=True)
    for name in ("stocks.json", "themes.json"):
        txt = data_file(name)
        if not txt:
            log(f"no {name} on radar-data yet: run the daily refresh first")
            return False
        open(os.path.join(OUT, "base_" + name), "w").write(txt)
    extra = []
    et = data_file("etfs.json")
    if et:
        open(os.path.join(OUT, "base_etfs.json"), "w").write(et)
        extra += ["--etfs", os.path.join(OUT, "base_etfs.json")]
    vp = data_file("volprofile.json")
    if vp:
        open(os.path.join(OUT, "base_volprofile.json"), "w").write(vp)
        extra += ["--profile", os.path.join(OUT, "base_volprofile.json"), "--sipcal", os.path.join(OUT, "sipcal.json")]
    load_opens()
    r = sh(sys.executable, os.path.join(HERE, "live.py"), os.path.join(OUT, "base_stocks.json"),
           os.path.join(OUT, "base_themes.json"), os.path.join(OUT, "live.json"), "--force", *extra, check=False)
    log("live:", (r.stdout or r.stderr).strip()[-300:])
    if r.returncode:
        return False
    files = [os.path.join(OUT, "live.json")]
    if os.path.exists(os.path.join(OUT, "opens.json")):
        files.append(os.path.join(OUT, "opens.json"))      # the day's opens, for a fresh job after the handover
    # phone alerts: launches and breakouts as they happen (radar/alerts.py; sent when NTFY_TOPIC is set)
    lj = main_file("setups/launch.json")
    if lj:
        open(os.path.join(OUT, "launch.json"), "w").write(lj)
        # the morning record (9:30-11:00): what the live data showed for the watch list's movers (radar/livelog.py)
        hp = load_history()
        sh(sys.executable, os.path.join(HERE, "livelog.py"), os.path.join(OUT, "live.json"), os.path.join(OUT, "launch.json"), hp,
           os.path.join(OUT, "sipcal.json"), check=False)
        if os.path.exists(hp):
            files.append(hp)
        load_alert_state()
        r = sh(sys.executable, os.path.join(HERE, "alerts.py"), os.path.join(OUT, "live.json"), os.path.join(OUT, "launch.json"),
               os.path.join(OUT, "alerts.json"), *premarket_args(), check=False)
        log((r.stdout or r.stderr).strip()[-600:])
        if r.returncode == 0 and os.path.exists(os.path.join(OUT, "alerts.json")):
            files.append(os.path.join(OUT, "alerts.json"))
    sh(sys.executable, os.path.join(HERE, "publish.py"), "live " + now().strftime("%F %H:%M"), *files)
    return True


def load_alert_state():
    """what was alerted today: this job's own copy, else the radar-data branch's (a fresh job after a handover)"""
    p = os.path.join(OUT, "alerts.json")
    try:
        if json.load(open(p)).get("date") == now().date().isoformat():
            return
    except Exception:
        pass
    st = data_file("alerts.json")
    if st:
        open(p, "w").write(st)


def load_opens():
    """the day's opens (radar/live.py fill_opens: the movers' opens from the first 1-minute bar, kept for the day): this
    job's own copy, else the radar-data branch's. A fresh job after the noon handover started with none and took Yahoo's
    quote open instead (EPAM Nov 5 2026: gap +14.9% in the 9:35 alerts, +13.7% in the afternoon's): one open all day"""
    p = os.path.join(OUT, "opens.json")
    try:
        if json.load(open(p)).get("date") == now().date().isoformat():
            return
    except Exception:
        pass
    st = data_file("opens.json")
    try:
        if st and json.loads(st).get("date") == now().date().isoformat():
            open(p, "w").write(st)
    except Exception:
        pass


def load_history():
    """the morning record's file (radar/livelog.py): this job's own copy, else the radar-data branch's (a fresh job after a handover)"""
    p = os.path.join(OUT, "live_history.json")
    try:
        if json.load(open(p)).get("date") == now().date().isoformat():
            return p
    except Exception:
        pass
    if (now().hour, now().minute) < (11, 0):
        st = data_file("live_history.json")
        if st:
            open(p, "w").write(st)
    return p


def premarket_args():
    """this morning's pre-market grades for the laggard launch alerts (news days), as alerts.py arguments"""
    p = os.path.join(OUT, "premarket_grades.json")
    if not (os.path.exists(p) and time.time() - os.path.getmtime(p) < 600):     # re-read every 10 minutes, not every check
        txt = data_file("premarket.json")
        if txt:
            open(p, "w").write(txt)
    return ["--premarket", p] if os.path.exists(p) else []


def fast_window(x):
    """the 1-minute checks run in the morning and the last hour (the user's choice, Oct 29 2026)"""
    return (9, 31) <= x < (12, 0) or (15, 0) <= x < (16, 0)


def fast_once():
    """1-minute check between the live updates: the watch list and the followed launches, for the big gap-ups and breakouts"""
    need = [os.path.join(OUT, f) for f in ("launch.json", "base_stocks.json", "base_volprofile.json")]
    if not all(os.path.exists(f) for f in need):
        return                                        # the first live update writes these
    out = os.path.join(OUT, "live_fast.json")
    load_opens()
    r = sh(sys.executable, os.path.join(HERE, "fast.py"), *need[:3], os.path.join(OUT, "sipcal.json"), out, check=False)
    if r.returncode:
        log("fast:", (r.stderr or r.stdout).strip()[-300:])
        return
    sh(sys.executable, os.path.join(HERE, "livelog.py"), out, need[0], load_history(), os.path.join(OUT, "sipcal.json"), check=False)   # the morning record
    load_alert_state()
    r = sh(sys.executable, os.path.join(HERE, "alerts.py"), out, need[0], os.path.join(OUT, "alerts.json"), "--fast", *premarket_args(), check=False)
    txt = (r.stdout or r.stderr).strip()
    if r.returncode == 0 and " 0 new," not in txt:
        log("fast:", txt[-600:])
        sh(sys.executable, os.path.join(HERE, "publish.py"), "alerts " + now().strftime("%F %H:%M"), os.path.join(OUT, "alerts.json"))


def daily():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(WORK, exist_ok=True)
    # each stock's Yahoo industry for the industry groups (radar/profiles.py), refreshed weekly (new listings)
    pf = data_file("profiles.json")
    if pf:
        open(os.path.join(WORK, "profiles.json"), "w").write(pf)
    r = sh(sys.executable, "-I", os.path.join(HERE, "pipeline.py"), WORK, OUT, REPO, check=False)
    log("pipeline:", r.stdout.strip()[-600:])
    if r.returncode:
        log(r.stderr[-2000:])
        raise RuntimeError("pipeline failed")
    stocks = json.load(open(os.path.join(OUT, "stocks.json")))
    if len(stocks) < 2000:
        raise RuntimeError(f"only {len(stocks)} stocks, not publishing")
    files = [os.path.join(OUT, f) for f in ("stocks.json", "themes.json", "build.json")]
    if os.path.exists(os.path.join(OUT, "groups.json")):
        files.append(os.path.join(OUT, "groups.json"))
    try:
        age = (now() - datetime.datetime.fromisoformat(json.loads(pf)["built_at"])).days if pf else 99
    except Exception:
        age = 99
    if age >= 7:                                       # next evening's groups use the refreshed profiles
        r = sh(sys.executable, os.path.join(HERE, "profiles.py"), os.path.join(OUT, "stocks.json"), os.path.join(OUT, "profiles.json"), check=False)
        log("profiles:", (r.stdout or r.stderr).strip()[-200:])
        if r.returncode == 0:
            files.append(os.path.join(OUT, "profiles.json"))
    r = sh(sys.executable, os.path.join(HERE, "etfs.py"), os.path.join(OUT, "themes.json"), os.path.join(OUT, "etfs.json"), check=False)
    log("etfs:", (r.stdout or r.stderr).strip()[-300:])
    if r.returncode == 0:
        files.append(os.path.join(OUT, "etfs.json"))
    gl = data_file("gradelog.json")
    if gl:
        p = os.path.join(OUT, "gradelog.json")
        open(p, "w").write(gl)
        r = sh(sys.executable, "-I", os.path.join(HERE, "gradelog.py"), "update", p,
               os.path.join(OUT, "stocks.json"), os.path.join(OUT, "build.json"), check=False)
        log("gradelog:", (r.stdout or r.stderr).strip()[-300:])
        if r.returncode == 0:
            files.append(p)
    r = sh(sys.executable, os.path.join(HERE, "revenue.py"), os.path.join(OUT, "themes.json"), os.path.join(OUT, "revenue.json"), check=False)
    log("revenue:", (r.stdout or r.stderr).strip()[-200:])
    if r.returncode == 0:
        files.append(os.path.join(OUT, "revenue.json"))
    sh(sys.executable, os.path.join(HERE, "publish.py"), "daily " + now().strftime("%F %H:%M"), *files)
    if gl and os.path.join(OUT, "gradelog.json") in files:   # dated copy of the track record, kept with history
        bk = os.path.join(OUT, "backup")
        os.makedirs(bk, exist_ok=True)
        dst = os.path.join(bk, f"gradelog-{now().date().isoformat()}.json")
        open(dst, "w").write(open(os.path.join(OUT, "gradelog.json")).read())
        r = sh(sys.executable, os.path.join(HERE, "publish.py"), "--branch", "radar-backup", "--keep-history",
               "gradelog backup " + now().strftime("%F"), dst, check=False)
        log("backup:", (r.stdout or r.stderr).strip()[-200:])
    log("daily refresh published")
    try:
        volprofile()
    except Exception as e:
        log("volume curves failed:", e)


def pm_once():
    """one live pre-market scan -> premarket_live.json on radar-data"""
    os.makedirs(OUT, exist_ok=True)
    txt = data_file("stocks.json")
    if not txt:
        return False
    p = os.path.join(OUT, "pm_stocks.json")
    open(p, "w").write(txt)
    r = sh(sys.executable, os.path.join(HERE, "pmlive.py"), p, os.path.join(OUT, "premarket_live.json"), check=False)
    log("pre-market:", (r.stdout or r.stderr).strip()[-300:])
    if r.returncode:
        return False
    sh(sys.executable, os.path.join(HERE, "publish.py"), "pre-market " + now().strftime("%F %H:%M"),
       os.path.join(OUT, "premarket_live.json"))
    return True


def volprofile():
    """20-session intraday volume curves for relative volume at time (about 5-10 minutes)"""
    os.makedirs(OUT, exist_ok=True)
    txt = data_file("stocks.json")
    if not txt:
        return
    p = os.path.join(OUT, "vp_stocks.json")
    open(p, "w").write(txt)
    r = sh(sys.executable, os.path.join(HERE, "volprofile.py"), p, os.path.join(OUT, "volprofile.json"), check=False)
    log("volume curves:", (r.stdout or r.stderr).strip()[-300:])
    if r.returncode == 0:
        sh(sys.executable, os.path.join(HERE, "publish.py"), "volume curves " + now().strftime("%F %H:%M"),
           os.path.join(OUT, "volprofile.json"))


def volprofile_current():
    """True when the curves already include the last complete session"""
    try:
        d = json.loads(data_file("volprofile.json"))["date"]
    except Exception:
        return False
    prev = now().date() - datetime.timedelta(days=1)
    while not trading_day(prev):
        prev -= datetime.timedelta(days=1)
    return d >= prev.isoformat()


def day_done():
    try:
        b = json.loads(data_file("build.json"))[0]
        return b["asof"] == now().date().isoformat()
    except Exception:
        return False


def sleep_until(t):
    s = (t - now()).total_seconds()
    if s > 0:
        time.sleep(min(s, 300))


def day():
    t = now()
    if not trading_day(t.date()):
        log("not a trading day")
        return
    if day_done():
        log("today's close is already processed")
        return
    # catch up first if the last after-close refresh didn't happen (e.g. yesterday's job never started)
    try:
        asof = json.loads(data_file("build.json"))[0]["asof"]
    except Exception:
        asof = ""
    prev = t.date() - datetime.timedelta(days=1)
    while not trading_day(prev):
        prev -= datetime.timedelta(days=1)
    if asof < prev.isoformat() and hm(t) < (16, 0):
        log(f"data is as of {asof}, older than {prev}: refreshing first")
        try:
            daily()
        except Exception as e:
            log("catch-up refresh failed:", e)
    if not volprofile_current() and hm(now()) < (16, 0):
        try:
            volprofile()
        except Exception as e:
            log("volume curves failed:", e)
    pm_started, snap_started, last_live, last_pm, cg_started = set(), None, None, None, set()
    while True:
        t = now()
        if time.monotonic() - T0 > BUDGET:
            log("time limit reached: handing over to a fresh run")
            dispatch("radar-day.yml", mode="day")
            return
        # pre-market scans at 8:25 and 8:40
        for slot in ((8, 25), (8, 40)):
            if hm(t) >= slot and hm(t) < (9, 25) and slot not in pm_started:
                pm_started.add(slot)
                if not premarket_saved_today():           # a job restarted mid-morning doesn't redo today's scan
                    dispatch("premarket.yml")
        # live pre-market scanner every 5 minutes, 7:00-9:29
        if (7, 0) <= hm(t) < (9, 30) and (last_pm is None or (t - last_pm).total_seconds() >= 290):
            last_pm = t
            try:
                if pm_once() and hm(t) < (9, 25):
                    # the news for that scan's 5%+ gappers, a minute later (the user, Nov 6 2026: "do it in a way it matches
                    # with the pre-market scan"): codegrade.yml in its news mode -> pmnews.json, no grades
                    dispatch("codegrade.yml", mode="news")
            except Exception as e:
                log("pre-market scan failed:", e)
        # the code grader (radar/codegrade.py) at 8:45, 8:55 and 9:00, right after that update's pre-market prices, so its
        # grades are in by 9:05 for the user's picks (the user, Nov 4 2026: each run takes about 40 seconds), then 9:10 and
        # 9:20 (the user: "pre-market is 8:45 to 9:25": a grade that changes until then still alerts); GitHub's own
        # schedule for it (8:52 / 9:05 / 9:18) often starts 5-20 minutes late and stays as a backup. A job that starts
        # later starts it once, for the latest slot that's due.
        due = [slot for slot in ((8, 45), (8, 55), (9, 0), (9, 10), (9, 20)) if slot <= hm(t) < (9, 30)]
        if due and due[-1] not in cg_started:
            cg_started.update(due)
            dispatch("codegrade.yml")
        # live prices every 5 minutes, 9:30-4:10
        if (9, 30) <= hm(t) <= (16, 10):
            due = last_live is None or (t - last_live).total_seconds() >= 290
            if due:
                last_live = t
                try:
                    live_once()
                except Exception as e:
                    log("live update failed:", e)
            elif fast_window(hm(t)):
                try:
                    fast_once()                           # 9:31-9:34 the early heads-ups, then the big gap-ups and breakouts
                except Exception as e:
                    log("1-minute check failed:", e)
        # close snapshot at 4:06, then the daily refresh
        if hm(t) >= (16, 6) and snap_started is None:
            snap_started = t
            if not close_saved_today():
                dispatch("snapshot.yml")
        if hm(t) > (16, 10):
            while not close_saved_today() and (now() - snap_started).total_seconds() < 40 * 60:
                time.sleep(60)
            if not close_saved_today():
                log("close snapshot not saved after 40 minutes: refreshing with the public files only")
            daily()
            return
        # next tick: the next minute during the session (live update on the 5-minute marks), else the next event
        nxt = t.replace(second=20, microsecond=0) + datetime.timedelta(minutes=5 - t.minute % 5)
        if (9, 30) <= hm(t) < (16, 0) and (fast_window(hm(t)) or hm(t) < (9, 31)):
            nxt = t.replace(second=20, microsecond=0) + datetime.timedelta(minutes=1)
        if hm(t) < (7, 0):
            nxt = min(nxt, t.replace(hour=7, minute=0, second=5, microsecond=0))
        sleep_until(nxt)


if __name__ == "__main__":
    mode = (sys.argv[1] if len(sys.argv) > 1 else "day") or "day"
    os.chdir(os.path.dirname(HERE))
    if mode == "daily":
        daily()
    elif mode == "volprofile":
        volprofile()
    elif mode == "premarket":
        pm_once()
    elif mode == "etfs":
        os.makedirs(OUT, exist_ok=True)
        open(os.path.join(OUT, "e_themes.json"), "w").write(data_file("themes.json"))
        sh(sys.executable, os.path.join(HERE, "etfs.py"), os.path.join(OUT, "e_themes.json"), os.path.join(OUT, "etfs.json"))
        sh(sys.executable, os.path.join(HERE, "publish.py"), "etfs " + now().strftime("%F %H:%M"), os.path.join(OUT, "etfs.json"))
    elif mode == "live":
        live_once()
    else:
        day()
