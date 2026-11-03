"""The bot's only input from the Radar: setups/launch.json (read-only; the Radar never places orders).

Reads the Launches rows and the Luk fields the portal shows (test/luk branch: trend, AVWAP, exit line, pullback zone,
the market gauge) and turns them into plans the bot can size and check."""
import json
import urllib.request

RAW = "https://raw.githubusercontent.com/goattrader40-lgtm/radar-close-snapshots/{ref}/setups/launch.json"


def load(src: str = None, ref: str = "main") -> dict:
    """a local path, a URL, or (default) the live file on GitHub"""
    src = src or RAW.format(ref=ref)
    if src.startswith("http"):
        with urllib.request.urlopen(src, timeout=30) as r:
            return json.load(r)
    return json.load(open(src))


def regime(doc: dict) -> (str, bool):
    """(GREEN / YELLOW / RED, a first bounce after a distribution day) from the Radar's market gauge;
    without the gauge: YELLOW (half size) until it is there"""
    b = doc.get("breadth") or {}
    return b.get("mode", "YELLOW"), bool(b.get("distribution_bounce"))


def next_resistance(row: dict, above: float):
    lv = [x[1] for x in (row.get("resistance") or []) if isinstance(x, (list, tuple)) and len(x) > 1 and x[1] > above]
    return min(lv) if lv else None


def plans(doc: dict, min_rs: int = 0, only_zone: bool = False) -> list:
    """one plan per Launches row with a buy point (or in a Luk pullback zone): what the bot needs to size and check it.
    The stop is NOT here: it comes from the live intraday structure (the flush low / today's low / the 1-5 minute
    AVWAP), like Luk's 1.28% median stop."""
    out = []
    for r in doc.get("launches", []):
        zone = r.get("luk_zone")
        if only_zone and not zone:
            continue
        trig = r.get("buy_point")
        if not trig and not zone:
            continue
        if min_rs and (r.get("rs_now") or 0) < min_rs:
            continue
        grp = (r.get("group_rank_now") or "").split(" #")[0] or r.get("group_now") or r.get("group") or ""
        out.append(dict(
            symbol=r["symbol"], setup=r.get("pattern") or r.get("stage", ""), trigger=trig, zone=zone,
            trend=r.get("trend"), adr_pct=r.get("adr_pct"), dvol_m=r.get("dollar_vol_20d_m"), group=grp,
            group_tier=r.get("group_tier_now"), rs=r.get("rs_now"), exit_line=r.get("exit_line"),
            avwap=r.get("avwap_near"), ema10=r.get("ema10"), ema21=r.get("ema21"), close=r.get("price"),
            resistance=next_resistance(r, trig or r.get("price") or 0), earnings_launch=r.get("earnings")))
    return out
