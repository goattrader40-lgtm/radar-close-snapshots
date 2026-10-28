#!/usr/bin/env python3
"""After-close heads-ups from the evening launch scan (setups/launch.json), to the phone (ntfy).

  python3 radar/eod_alerts.py <launch.json>      (NTFY_TOPIC set: sends; unset: only prints)

  tight    2+ tight closes just under the buy point (a base top or a pattern's pivot): a breakout may come next
           (ANF Oct 15-16 2026 under its 155.22 base top, out on Oct 19; RPD Oct 21 under 13.87, out Oct 22)
  retest   it came back to its broken base top and closed above it: another entry (ANF Oct 23 2026)
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
            out.append((f"{r['symbol']} retest held", f"came back to its broken base top {r.get('last_breakout_top')} (broken {r.get('last_breakout_date')})"
                        f" and closed above it at ${r['price']:.2f}: another entry" + tail, r.get("tv") or r["symbol"]))
        elif (r.get("tight_days") or 0) >= 2 and r.get("buy_point"):
            base = (f" · base {r['base_len']} sessions (since {r['base_from']}), {r['base_low_pct']:.0f}% deep ({r['base_low_adr']:.1f} ADRs)"
                    + (f", {r['msf_pattern']}" if r.get("msf_pattern") else "")) if r.get("base_len") else ""
            out.append((f"{r['symbol']} tight under its buy point", f"{r['tight_days']} tight closes just under ${r['buy_point']:.2f}, the base high{base},"
                        f" now ${r['price']:.2f}: watch for the breakout" + tail, r.get("tv") or r["symbol"]))
    if len(out) > MAX:
        out = out[:MAX - 1] + [(f"{len(out) - MAX + 1} more heads-ups", ", ".join(t.split()[0] for t, _, _ in out[MAX - 1:]), "SPY")]
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    for title, msg, tvs in out:
        print(f"{title}: {msg}")
        if topic:
            try:
                send(topic, title + " (after the close)", msg, "default", tvs)
            except Exception as e:
                print("not sent:", e, file=sys.stderr)
    print(f"eod alerts: {len(out)}" + ("" if topic else " (no NTFY_TOPIC: printed, not sent)"))


if __name__ == "__main__":
    main()
