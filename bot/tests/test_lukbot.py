"""python3 -m unittest discover -s bot/tests -v      (no packages needed; ib_async only for lukbot.ibkr)"""
import datetime as dt
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lukbot import (Brake, Config, Held, LOOSE_BRAKE, LukSession, financed_stop, is_fast_leader, size_position,  # noqa: E402
                    stats, tier_cap)
from lukbot.manage import Trade, TradeManager, ema_today  # noqa: E402
from lukbot.portfolio import Candidate, check_entry, rotation_candidates  # noqa: E402

D0 = dt.date(2026, 11, 2)


class Sizing(unittest.TestCase):
    def test_luk_2026_numbers(self):
        """0.3% risk on his 1.28% median stop in a liquid leader = a 23.4% position (Muninn: typical 20-30%)"""
        s = size_position(Config(), 1_000_000, 100.0, 98.72, adr_pct=4.0, dvol_m=500)
        self.assertEqual(s.binding, "risk")
        self.assertAlmostEqual(s.position_pct, 23.4, delta=0.1)
        self.assertAlmostEqual(s.risk_pct, 0.30, delta=0.005)

    def test_cap_35(self):
        """0.5% risk on a 1% stop would be 50%: capped at 35%, so the trade risks 0.35% (Muninn's chart: 1.5% stop = 33.3%)"""
        s = size_position(Config(risk_pct=0.5), 1_000_000, 100.0, 99.0, adr_pct=4.0, dvol_m=500, gap_pct=3.0)
        self.assertEqual(s.binding, "tier cap")
        self.assertAlmostEqual(s.position_pct, 35.0, delta=0.05)
        s2 = size_position(Config(risk_pct=0.5), 1_000_000, 100.0, 98.5, adr_pct=4.0, dvol_m=500, gap_pct=3.0)
        self.assertAlmostEqual(s2.position_pct, 33.3, delta=0.1)

    def test_stop_rules(self):
        c = Config()
        self.assertIn("ADR", size_position(c, 1e6, 100, 97.0, adr_pct=4.0, dvol_m=500).reject)     # 0.75 ADR
        self.assertIn("5.0%", size_position(c, 1e6, 100, 94.0, adr_pct=15.0, dvol_m=500).reject)  # 6%
        self.assertIn("noise", size_position(c, 1e6, 100, 99.7, adr_pct=4.0, dvol_m=500).reject)  # 0.3%

    def test_liquidity_tiers_and_capacity(self):
        c = Config()
        self.assertEqual(tier_cap(c, 150), 35.0)
        self.assertEqual(tier_cap(c, 60), 25.0)
        self.assertEqual(tier_cap(c, 25), 15.0)
        self.assertEqual(tier_cap(c, 10), 0.0)
        s = size_position(c, 1_000_000, 100, 98.7, adr_pct=4.0, dvol_m=30)        # $30M/day < 50x $1M
        self.assertIn("50x", s.reject)
        s = size_position(c, 100_000, 100, 98.7, adr_pct=4.0, dvol_m=30)
        self.assertLessEqual(s.position_pct, 15.0)

    def test_gap_cap_small_cap(self):
        """a 12% bad overnight gap: position x 12% <= 2% -> at most 16.7%, whatever the tight stop says"""
        s = size_position(Config(), 200_000, 50, 49.2, adr_pct=7.0, dvol_m=200, gap_pct=12.0)
        self.assertEqual(s.binding, "gap cap")
        self.assertLessEqual(s.position_pct, 16.7)

    def test_brake_multiplier_applies(self):
        a = size_position(Config(), 1e6, 100, 98.72, 4.0, 500)
        b = size_position(Config(), 1e6, 100, 98.72, 4.0, 500, mult=0.5)
        self.assertAlmostEqual(b.position_pct, a.position_pct / 2, delta=0.1)
        self.assertIn("brake", size_position(Config(), 1e6, 100, 98.72, 4.0, 500, mult=0.0).reject)

    def test_short(self):
        s = size_position(Config(), 1e6, 100, 101.3, adr_pct=4.0, dvol_m=500, side=-1)
        self.assertEqual(s.reject, "")
        self.assertAlmostEqual(s.position_pct, 23.1, delta=0.1)


class FinancedStop(unittest.TestCase):
    def test_worst_case_zero(self):
        entry, stop = 100.0, 98.72
        R = entry - stop
        trim = entry + 4 * R
        s = financed_stop(entry, stop, 0.15, trim)
        self.assertAlmostEqual((s - entry) / R, -0.706, places=3)
        pnl = 0.15 * (trim - entry) + 0.85 * (s - entry)      # stopped on the rest
        self.assertAlmostEqual(pnl, 0.0, places=9)

    def test_short(self):
        s = financed_stop(100.0, 101.0, 0.15, 96.0, side=-1)
        self.assertAlmostEqual(s, 100.0 + 0.15 * 4 / 0.85, places=6)


class BrakeTests(unittest.TestCase):
    def test_drawdown_steps_and_ramp(self):
        b = Brake(Config(month_loss_steps=((50.0, 0.25),)), 100_000, D0)     # the month rule tested on its own below
        self.assertEqual(b.multiplier()[0], 1.0)
        b.update_equity(93_000, D0)                       # 7% under the high
        self.assertEqual(b.multiplier()[0], 0.5)
        b.update_equity(88_000, D0)                       # 12% under
        self.assertEqual(b.multiplier()[0], 0.25)
        b.update_equity(97_000, D0)                       # 3% under: the steps clear, the ramp starts at 0.25
        self.assertEqual(b.multiplier()[0], 0.25)
        b.record_exit(1.5, False); b.record_exit(0.8, False)
        self.assertEqual(b.multiplier()[0], 0.5)          # 2 winners: next step
        b.update_equity(100_500, D0)                      # a new high: full
        self.assertEqual(b.multiplier()[0], 1.0)

    def test_loose(self):
        b = Brake(Config(**LOOSE_BRAKE), 100_000, D0)
        b.update_equity(93_000, D0)
        self.assertEqual(b.multiplier()[0], 1.0)

    def test_streak_and_day_stops(self):
        b = Brake(Config(), 100_000, D0)
        for _ in range(5):
            b.record_exit(-1.0, True)
        self.assertEqual(b.multiplier()[0], 0.0)          # 5 stops today hits the 3-a-day rule too
        b.update_equity(99_000, D0 + dt.timedelta(days=1))  # next day: day stops reset, the streak stays
        self.assertEqual(b.multiplier()[0], 0.5)
        b.record_exit(1.0, False)
        self.assertEqual(b.multiplier()[0], 0.5)          # a +1R winner doesn't reset it
        b.record_exit(2.5, False)
        self.assertEqual(b.multiplier()[0], 0.5)          # a +2R winner clears it; the ramp brings size back (step 2)
        b.update_equity(100_100, D0 + dt.timedelta(days=1))
        self.assertEqual(b.multiplier()[0], 1.0)          # a new equity high: full

    def test_month_limits_and_override_lock(self):
        c = Config(dd_steps=((50.0, 0.5),))               # isolate the month rule
        b = Brake(c, 100_000, D0)
        b.update_equity(91_000, D0)
        self.assertEqual(b.multiplier()[0], 0.25)
        self.assertFalse(b.manual_allowed())
        b.update_equity(87_000, D0)
        self.assertEqual(b.multiplier()[0], 0.0)
        b.update_equity(87_000, dt.date(2026, 12, 1))     # a new month starts from here
        self.assertGreater(b.multiplier()[0], 0.0)

    def test_regime_and_distribution(self):
        b = Brake(Config(), 100_000, D0)
        self.assertEqual(b.multiplier("YELLOW")[0], 0.5)
        self.assertEqual(b.multiplier("RED")[0], 0.0)
        self.assertEqual(b.multiplier("GREEN", distribution_bounce=True)[0], 0.5)

    def test_new_positions_cap_in_drawdown(self):
        b = Brake(Config(), 100_000, D0)
        b.update_equity(94_000, D0)
        b.record_entry(); b.record_entry()
        self.assertFalse(b.new_entry_allowed()[0])

    def test_cushion(self):
        b = Brake(Config(cushion_mult=1.5), 100_000, D0)
        b.update_equity(106_000, D0)
        self.assertEqual(b.multiplier(a_setup=True)[0], 1.5)
        self.assertEqual(b.multiplier(a_setup=False)[0], 1.0)


class Management(unittest.TestCase):
    def setUp(self):
        self.c = Config()
        self.tm = TradeManager(self.c)
        self.t = Trade("IONQ", 1, stop=48.36, reclaim_level=49.35, setup="21 EMA & AVWAP reclaim")
        acts = self.tm.entry_orders(self.t, 49.40, 1000, adr_pct=6.0)
        self.assertEqual([a.tag for a in acts], ["entry", "stop"])
        self.tm.on_entry_fill(self.t, 49.40, 1000, "2026-05-20")

    def test_trim_then_financed_stop(self):
        R = self.t.risk
        self.assertEqual(self.tm.on_price(self.t, 49.40 + 3.9 * R), [])
        a = self.tm.on_price(self.t, 49.40 + 4.0 * R)
        self.assertEqual((a[0].tag, a[0].qty), ("trim", 150))
        self.assertEqual(self.tm.on_price(self.t, 49.40 + 5 * R), [])            # only once
        hist = dict(closes=[50 + k for k in range(10)], ema_fast=[49 + k for k in range(10)],
                    ema21=[46 + 0.8 * k for k in range(10)], adr_pct=6.0)
        m = self.tm.on_fill(self.t, "trim", 150, 49.40 + 4.0 * R, hist)
        self.assertEqual(m[0].kind, "MODIFY_STOP")
        self.assertEqual(m[0].qty, 850)
        self.assertAlmostEqual((m[0].stop - 49.40) / R, -0.706, delta=0.01)
        self.assertEqual(self.t.exit_mode, "fast")
        # stopped on the rest: the trade is a scratch, not a loss
        self.tm.on_fill(self.t, "stop", 850, self.t.stop)
        self.assertTrue(self.t.closed)
        self.assertAlmostEqual(self.t.r_result(), 0.0, delta=0.02)

    def test_breakeven_mode(self):
        tm = TradeManager(Config(stop_after_trim="breakeven"))
        t = Trade("X", 1, stop=98.72)
        tm.on_entry_fill(t, 100.0, 1000, "d")
        tm.on_price(t, 100 + 4 * t.risk)
        m = tm.on_fill(t, "trim", 150, 100 + 4 * t.risk)
        self.assertAlmostEqual(m[0].stop, 100.0, places=2)

    def test_ratchet_to_breakeven(self):
        R = self.t.risk
        self.tm.on_price(self.t, 49.40 + 4 * R)
        self.tm.on_fill(self.t, "trim", 150, 49.40 + 4 * R)
        self.assertEqual(self.tm.on_daily_close(self.t, 49.40 + 2.5 * R, 50, 48, 6.0), [])
        a = self.tm.on_daily_close(self.t, 49.40 + 3 * R, 51, 48.5, 6.0)
        self.assertEqual((a[0].tag, a[0].stop), ("ratchet", 49.40))

    def test_daily_close_trail(self):
        # steady (before the trim): price clearly under today's 21 EMA at 15:47 -> MOC
        a = self.tm.on_close_check(self.t, 47.0, prev_ema_fast=49.0, prev_ema21=48.5, adr_pct=6.0, day0=False)
        self.assertEqual((a[0].order_type, a[0].tag), ("MOC", "trail"))

    def test_close_too_close_to_call(self):
        t, tm = self.t, self.tm
        e21 = ema_today(48.5, 48.48, 21)
        self.assertEqual(tm.on_close_check(t, 48.48, 49.0, 48.5, 6.0, False), [])   # within 0.1 ADR: wait
        self.assertTrue(t.watch_close)
        tm.on_daily_close(t, 48.40, 49.0, e21, 6.0)                                   # the official close is under
        a = tm.on_next_open(t, range_low=48.10, range_high=48.90, price=48.30)
        self.assertEqual((a[0].tag, a[0].order_type, a[0].stop, a[0].deadline), ("next_open", "STP", 48.10, "10:00"))

    def test_day0_cut(self):
        a = self.tm.on_close_check(self.t, 49.10, prev_ema_fast=48.0, prev_ema21=47.0, adr_pct=6.0, day0=True)
        self.assertEqual(a[0].tag, "day0")
        t2 = Trade("Y", 1, stop=48.36, reclaim_level=49.0)
        self.tm.on_entry_fill(t2, 49.40, 100, "d")
        self.assertEqual(self.tm.on_close_check(t2, 49.20, 48.0, 47.0, 6.0, True), [])   # under the entry, over the level

    def test_event_eve(self):
        a = self.tm.on_event_eve(self.t, "earnings")
        self.assertEqual((a[0].qty, a[0].order_type), (500, "MOC"))
        self.assertEqual(self.tm.on_event_eve(self.t, "earnings"), [])

    def test_fast_leader_rule(self):
        c = Config()
        self.assertTrue(is_fast_leader(c, [110] * 10, [105] * 10, [100] * 10, 5.0))       # 2 ADRs over the 21
        self.assertFalse(is_fast_leader(c, [102] * 10, [101] * 10, [100] * 10, 5.0))      # 0.4 ADR over
        self.assertFalse(is_fast_leader(c, [110] * 10, [111] * 10, [100] * 10, 5.0))      # closes under the 10


class Portfolio(unittest.TestCase):
    def test_heat_group_gross(self):
        c = Config()
        held = [Held("MU", 1, 2500, 100, 98.7, 101, "Memory", 4.0), Held("SNDK", 1, 200, 1000, 987, 1005, "Memory", 5.0)]
        cand = Candidate("WDC", 1, 80, 79, 3000, "Memory", 5.0)
        bad = check_entry(c, 1_000_000, held, cand)
        self.assertTrue(any("Memory" in x for x in bad))
        cand2 = Candidate("NET", 1, 200, 197.4, 1150, "Cybersecurity", 4.0, resistance=203.0)
        bad2 = check_entry(c, 1_000_000, held, cand2)
        self.assertTrue(any("resistance" in x for x in bad2))
        cand3 = Candidate("NET", 1, 200, 197.4, 1150, "Cybersecurity", 4.0, earnings_sessions=1)
        self.assertTrue(any("earnings" in x for x in check_entry(c, 1_000_000, held, cand3)))

    def test_rotation(self):
        held = [Held("A", 1, 100, 100, 98, 99, ""), Held("B", 1, 100, 100, 98, 110, "")]
        self.assertEqual(rotation_candidates(held, 4000)[0], ("A", 50))


class SessionFlow(unittest.TestCase):
    def test_full_trade_and_journal(self):
        with tempfile.TemporaryDirectory() as d:
            s = LukSession(Config(), equity=500_000, journal=os.path.join(d, "t.jsonl"), trades_done=100, today=D0)
            acts, why = s.plan_entry("IONQ", 1, trigger=49.40, stop=48.77, adr_pct=6.0, dvol_m=900, group="Quantum",
                                     held=[], regime="GREEN", setup="21 EMA & AVWAP reclaim", reclaim_level=49.35)
            self.assertEqual(len(acts), 2, why)
            qty = acts[0].qty
            s.on_entry_fill("IONQ", 49.42, qty, "2026-05-20")
            t = s.trades["IONQ"]
            trim = s.on_price("IONQ", t.entry + 4 * t.risk)
            s.on_fill("IONQ", "trim", trim[0].qty, t.entry + 4 * t.risk)
            s.on_fill("IONQ", "trail", t.shares, 73.65, date="2026-06-03")
            rows = s.journal.trades()
            self.assertEqual(len(rows), 1)
            self.assertGreater(rows[0]["r"], 20)                 # the article: +25R on IONQ
            self.assertNotIn("IONQ", s.trades)

    def test_refusals(self):
        s = LukSession(Config(), equity=500_000, journal=os.devnull, today=D0)
        acts, why = s.plan_entry("X", 1, 50, 47, adr_pct=4.0, dvol_m=900)
        self.assertEqual(acts, [])
        self.assertTrue(any("stop" in w for w in why))   # a 6% stop
        acts, why = s.plan_entry("X", 1, 50, 49.4, adr_pct=4.0, dvol_m=900, regime="RED")
        self.assertEqual(acts, [])


class Stats(unittest.TestCase):
    def test_luk_like(self):
        rs = [-1.0] * 305 + [0.0] * 65 + [5.0] * 81 + [22.0] * 10
        st = stats(rs)
        self.assertEqual(st["n"], 461)
        self.assertAlmostEqual(st["win_rate"], 19.7, delta=0.1)
        self.assertEqual(st["worst_streak"], 370)               # sorted list: the worst case
        self.assertGreater(st["expectancy_r"], 0.6)


if __name__ == "__main__":
    unittest.main()
