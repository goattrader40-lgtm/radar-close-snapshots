#!/usr/bin/env python3
"""Theme & Group Radar: one GitHub job runs the whole market day.

  python3 radar/day.py day      # the full day (default): pre-market scans, 5-minute live prices, then the close
  python3 radar/day.py daily    # only the after-close refresh (pipeline + track record), now
  python3 radar/day.py live     # one live update, now (works any time)

Timeline (ET, trading days):
  8:25, 8:40   start the "Pre-market scan" workflow (if today's scan isn't saved yet)
  9:30-4:10    every 5 minutes: live prices -> live.json on the radar-data branch
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
    vp = data_file("volprofile.json")
    if vp:
        open(os.path.join(OUT, "base_volprofile.json"), "w").write(vp)
        extra = ["--profile", os.path.join(OUT, "base_volprofile.json")]
    r = sh(sys.executable, os.path.join(HERE, "live.py"), os.path.join(OUT, "base_stocks.json"),
           os.path.join(OUT, "base_themes.json"), os.path.join(OUT, "live.json"), "--force", *extra, check=False)
    log("live:", (r.stdout or r.stderr).strip()[-300:])
    if r.returncode:
        return False
    sh(sys.executable, os.path.join(HERE, "publish.py"), "live " + now().strftime("%F %H:%M"), os.path.join(OUT, "live.json"))
    return True


def daily():
    os.makedirs(OUT, exist_ok=True)
    r = sh(sys.executable, "-I", os.path.join(HERE, "pipeline.py"), WORK, OUT, REPO, check=False)
    log("pipeline:", r.stdout.strip()[-600:])
    if r.returncode:
        log(r.stderr[-2000:])
        raise RuntimeError("pipeline failed")
    stocks = json.load(open(os.path.join(OUT, "stocks.json")))
    if len(stocks) < 2000:
        raise RuntimeError(f"only {len(stocks)} stocks, not publishing")
    files = [os.path.join(OUT, f) for f in ("stocks.json", "themes.json", "build.json")]
    gl = data_file("gradelog.json")
    if gl:
        p = os.path.join(OUT, "gradelog.json")
        open(p, "w").write(gl)
        r = sh(sys.executable, "-I", os.path.join(HERE, "gradelog.py"), "update", p,
               os.path.join(OUT, "stocks.json"), os.path.join(OUT, "build.json"), check=False)
        log("gradelog:", (r.stdout or r.stderr).strip()[-300:])
        if r.returncode == 0:
            files.append(p)
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
    pm_started, snap_started, last_live = set(), None, None
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
                if slot == (8, 25) or not premarket_saved_today():
                    dispatch("premarket.yml")
        # live prices every 5 minutes, 9:30-4:10
        if (9, 30) <= hm(t) <= (16, 10):
            due = last_live is None or (t - last_live).total_seconds() >= 290
            if due:
                last_live = t
                try:
                    live_once()
                except Exception as e:
                    log("live update failed:", e)
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
        # next tick: the next 5-minute mark during the session, else the next event
        nxt = t.replace(second=20, microsecond=0) + datetime.timedelta(minutes=5 - t.minute % 5)
        if hm(t) < (8, 25):
            nxt = min(nxt, t.replace(hour=8, minute=25, second=5, microsecond=0))
        sleep_until(nxt)


if __name__ == "__main__":
    mode = (sys.argv[1] if len(sys.argv) > 1 else "day") or "day"
    os.chdir(os.path.dirname(HERE))
    if mode == "daily":
        daily()
    elif mode == "volprofile":
        volprofile()
    elif mode == "live":
        live_once()
    else:
        day()
