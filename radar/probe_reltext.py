#!/usr/bin/env python3
"""Earnings reader check (test/earnfix): the week's press releases as plain text, to test a reader fix offline.

  python3 radar/probe_reltext.py <earnings.json> <out.json> [SYM ...]

For every reported row of earnings.json that has a release (rel_url), or only the SYMs given: the release text
(cleaned the same way as radar/earnings.py SEC.release, first 60,000 characters) and the saved estimates the reader
checks against (rev_est, rev_yago, eps_est, nq, fy), plus what the live reader stored (rev_act, guide, read).
"""
import html, json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from earnings import http, retry, SEC_UA  # noqa: E402

KEEP = ("sym", "date", "when", "rel_url", "rel_filed", "rev_est", "rev_yago", "eps_est", "eps_yago", "nq", "fy",
        "rev_act", "rev_src", "rev_growth", "rev_surprise", "eps_act", "eps_src", "eps_surprise", "guide", "read", "why",
        "points", "move", "move_after", "move_kind")


def main():
    src, out, syms = sys.argv[1], sys.argv[2], set(s.upper() for s in sys.argv[3:])
    rows = [r for r in json.load(open(src)).get("rows", []) if r.get("rel_url") and (not syms or r["sym"] in syms)]
    res = {}
    for r in rows:
        o = {k: r.get(k) for k in KEEP}
        try:
            raw = retry(lambda: http(r["rel_url"], SEC_UA)).decode("utf-8", "replace")
            txt = re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style).*?</\1>", " ", raw))
            o["text"] = re.sub(r"\s+", " ", html.unescape(txt)).strip()[:60000]
        except Exception as e:
            o["error"] = repr(e)[:200]
        res[r["sym"]] = o
        time.sleep(0.15)                                # the SEC asks for at most 10 requests a second
    json.dump({"n": len(res), "rows": res}, open(out, "w"))
    print(len(res), "releases,", sum(1 for v in res.values() if v.get("error")), "errors")


if __name__ == "__main__":
    main()
