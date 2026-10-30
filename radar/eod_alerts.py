#!/usr/bin/env python3
"""After-close heads-ups from the evening launch scan (setups/launch.json), to the phone (ntfy).

  python3 radar/eod_alerts.py <launch.json>      (NTFY_TOPIC set: sends; unset: only prints)

  tight    2+ tight closes just under the buy point (a base top or a pattern's pivot): a breakout may come next
           (ANF Oct 15-16 2026 under its 155.22 base top, out on Oct 19; RPD Oct 21 under 13.87, out Oct 22)
  retest   it pulled back to its last breakout's level (the top of the broken base's bodies or its wick top) and
           closed above it: another entry, once per breakout; high priority with the 10 / 21 / 50 EMA there too
           (GMAB Oct 2 2026 at 34.63 with the 21 EMA; SPOT Oct 28 at 536.98-540.82 with the 21 EMA)
Only for a scan of today's close; each stock once.
"""
import datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from alerts import NY, send  # noqa: E402

MAX = 8


def main():
    doc = json.load(open(sys.argv[1]))
    if doc.get("date") != datetime.datetime.now(NY).date().isoformat():
        print("eod alerts: the scan isn't today's close")
        return
    out = []
    for r in doc.get("launches", []):
        late = " (late leg)" if r.get("late") else ""
        tail = f" · leg {r.get('leg')}{late} · {'your pick since ' + r['pick'][:10] if r.get('grade') == 'You' else 'launched ' + r['date'] + ' (' + r['grade'] + ')'} · theme {r.get('group_now') or '-'} ({(r.get('group_status_now') or '').lower()})"
        if r.get("retest_today"):
            lb, lw, emas = r.get("retest_level"), r.get("retest_level_wick"), r.get("retest_ema") or []
            lv = f"${lb:.2f}" + (f"-${lw:.2f} (bodies-wicks)" if lw and lw > lb * 1.001 else "")
            out.append((f"{r['symbol']} retest held" + (" + " + " & ".join(emas) if emas else ""),
                        f"pulled back to its breakout level {lv} (broken {r.get('retest_from')}) and closed above it at ${r['price']:.2f}"
                        + (f", with the {' & '.join(emas)} there too" if emas else "") + ": another entry" + tail,
                        r.get("tv") or r["symbol"], "high" if emas else "default"))
        elif (r.get("tight_days") or 0) >= 2 and (r.get("tight_level") or r.get("buy_point")):
            base = (f" · base {r['base_len']} sessions (since {r['base_from']}), {r['base_low_pct']:.0f}% deep ({r['base_low_adr']:.1f} ADRs)"
                    + (f", {r['msf_pattern']}" if r.get("msf_pattern") else "")) if r.get("base_len") else ""
            out.append((f"{r['symbol']} tight under its buy point", f"{r['tight_days']} tight days just under ${r.get('tight_level') or r['buy_point']:.2f}, the base high{base},"
                        f" now ${r['price']:.2f}: watch for the breakout" + tail, r.get("tv") or r["symbol"], "default"))
    if len(out) > MAX:
        out = out[:MAX - 1] + [(f"{len(out) - MAX + 1} more heads-ups", ", ".join(t.split()[0] for t, _, _, _ in out[MAX - 1:]), "SPY", "default")]
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    for title, msg, tvs, prio in out:
        print(f"{title}: {msg}")
        if topic:
            try:
                send(topic, title + " (after the close)", msg, prio, tvs)
            except Exception as e:
                print("not sent:", e, file=sys.stderr)
    print(f"eod alerts: {len(out)}" + ("" if topic else " (no NTFY_TOPIC: printed, not sent)"))


if __name__ == "__main__":
    main()
