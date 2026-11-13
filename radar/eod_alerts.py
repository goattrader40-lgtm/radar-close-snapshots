#!/usr/bin/env python3
"""After-close heads-ups from the evening launch scan (setups/launch.json), to the phone (ntfy).

  python3 radar/eod_alerts.py <launch.json>      (NTFY_TOPIC set: sends; unset: only prints)

  tight    2+ tight closes just under the buy point (a base top or a pattern's pivot): a breakout may come next
           (ANF Oct 15-16 2026 under its 155.22 base top, out on Oct 19; RPD Oct 21 under 13.87, out Oct 22)
  retest   it pulled back to its last breakout's level (the top of the broken base's bodies or its wick top) and
           closed above it: another entry, once per breakout; high priority with the 10 / 21 / 50 EMA there too
           (GMAB Oct 2 2026 at 34.63 with the 21 EMA; SPOT Oct 28 at 536.98-540.82 with the 21 EMA)
  2nd low  the 2nd higher low in the base (the 1st low held the 50 EMA, a bounce, then a higher low that tests the 50 EMA and
           closes back over it: APPN Sep 28-29 2026): an end-of-day entry, high priority
  21 EMA   the 21 EMA entries in the base: the retest (a controlled pullback, the low under it, the close back over it:
           TTAN Oct 29 2026, ARM May 18) and the undercut & reclaim after 2 closes under it (strong: SMCI Jun 27 2023)
  3rd try  an ascending triangle: 2 tries of the top, the last pullback shallower, now close to the top again: the 3rd try
           usually breaks out (ARM Apr 24 / May 6 2026, out May 20)
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
        if (r.get("stage") or "").startswith("2nd higher low in the base") or " · 2nd higher low in the base" in (r.get("stage") or ""):
            # the 2nd higher low in the base, an end-of-day entry (the user, Nov 13 2026: "2nd higher low can be end of day
            # trigger its end of day thing"; APPN Sep 28-29 2026)
            st_ = r["stage"]
            st_ = st_[st_.index("2nd higher low in the base"):].split(" · ")[0]
            out.append((f"{r['symbol']} 2nd higher low in its base", st_ + f" · the buy: tomorrow's break of the 5-min opening range high, the stop under "
                        f"today's low" + tail, r.get("tv") or r["symbol"], "high"))
        elif r.get("retest_today"):
            lb, lw, emas = r.get("retest_level"), r.get("retest_level_wick"), r.get("retest_ema") or []
            lv = f"${lb:.2f}" + (f"-${lw:.2f} (bodies-wicks)" if lw and lw > lb * 1.001 else "")
            out.append((f"{r['symbol']} retest held" + (" + " + " & ".join(emas) if emas else ""),
                        f"pulled back to its breakout level {lv} (broken {r.get('retest_from')}) and closed above it at ${r['price']:.2f}"
                        + (f", with the {' & '.join(emas)} there too" if emas else "") + ": another entry" + tail,
                        r.get("tv") or r["symbol"], "high" if emas else "default"))
        elif r.get("ema21_today"):
            und = r["ema21_today"] == "undercut"
            out.append((f"{r['symbol']} 21 EMA {'undercut & reclaim' if und else 'retest'} held",
                        (f"after 2 closes under its 21 EMA, it undercut it again and closed back over it at ${r['price']:.2f} (21 EMA ${r['ema21']:.2f}): strong"
                         if und else f"pulled back into its 21 EMA, the low under it, and closed back over it at ${r['price']:.2f} (21 EMA ${r['ema21']:.2f})")
                        + ": an entry in the base" + tail, r.get("tv") or r["symbol"], "high" if und else "default"))
        elif (r.get("tight_days") or 0) >= 2 and (r.get("tight_level") or r.get("buy_point")):
            base = (f" · base {r['base_len']} sessions (since {r['base_from']}), {r['base_low_pct']:.0f}% deep ({r['base_low_adr']:.1f} ADRs)"
                    + (f", {r['msf_pattern']}" if r.get("msf_pattern") else "")) if r.get("base_len") else ""
            out.append((f"{r['symbol']} tight under its buy point", f"{r['tight_days']} tight days just under ${r.get('tight_level') or r['buy_point']:.2f}, the base high{base},"
                        f" now ${r['price']:.2f}: watch for the breakout" + (" · " + r["top_tries_note"] if r.get("top_tries_note") else "") + tail,
                        r.get("tv") or r["symbol"], "default"))
        elif r.get("top_tries_note") and r.get("to_buy_point_pct") is not None and r["to_buy_point_pct"] <= 0.5 * (r.get("adr_pct") or 5.0):
            out.append((f"{r['symbol']} 3rd try of its top coming", f"{r['top_tries_note']}; now ${r['price']:.2f}, {r['to_buy_point_pct']:.1f}% under it" + tail,
                        r.get("tv") or r["symbol"], "default"))
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
    # 3-SETUPS Ready (Watchlist): tomorrow's buys, all in one message with the list as a text file
    ready = [r for r in doc.get("setups3", []) if r.get("section") == "Ready"]
    if ready:
        name, text = f"3-SETUPS-Ready-{doc['date']}.txt", ready_file(doc["date"], ready)
        print(text)
        if topic:
            try:
                send_file(topic, f"3-SETUPS Ready for tomorrow: {len(ready)} stocks",
                          " ".join(r["symbol"] for r in ready)[:300], name, text)
            except Exception as e:
                print("Ready list not sent:", e, file=sys.stderr)


def ready_file(day, rows):
    """the Ready list as text: one line per stock, the closest to its trigger first"""
    lines = [f"3-SETUPS Ready after the {day} close: the trigger within 0.7 ADR (buy over it; your entry: the 5-minute opening range high)", ""]
    for r in sorted(rows, key=lambda r: r.get("away_adr") if r.get("away_adr") is not None else 9):
        lines.append(f"{r['symbol']:6} {r.get('setup') or '':18} trigger {r.get('buy_point') or '-':>9}  {r.get('away_adr') or 0:.1f} ADR away"
                     f"  ADR {r.get('adr_pct') or 0:.1f}%" + ("  tight" + w.split("tight")[1].split(" (")[0] if "tight" in (w := r.get("why") or "") else "")
                     + ("  (" + w.split(" (")[-1] if " (from " in w else ""))
    return "\n".join(lines) + "\n"


def send_file(topic, title, msg, filename, text):
    """one ntfy message with a text file attached (ntfy: the body is the file, the message goes in a header)"""
    import urllib.request
    req = urllib.request.Request(f"https://ntfy.sh/{topic}", data=text.encode(), method="PUT", headers={
        "Title": title.encode("ascii", "replace").decode(), "Message": msg.encode("ascii", "replace").decode(),
        "Filename": filename, "Priority": "default", "Tags": "clipboard"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status


if __name__ == "__main__":
    main()
