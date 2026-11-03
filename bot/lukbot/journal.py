"""The trade journal: one JSON line per closed trade, and the numbers to compare with Luk's and the simulation's."""
import json
import os


class Journal:
    def __init__(self, path: str):
        self.path = path

    def record(self, **trade):
        """symbol, side, setup, trigger type, opened, closed, entry, stop0, r, stopped, mae_r, mfe_r, slippage_entry,
        slippage_stop, gap_event, regime, brake_m, manual (an override), ..."""
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        with open(self.path, "a") as f:
            f.write(json.dumps(trade, default=str) + "\n")

    def trades(self) -> list:
        if not os.path.exists(self.path):
            return []
        return [json.loads(x) for x in open(self.path) if x.strip()]


def stats(rs: list) -> dict:
    """win rate, payoff, expectancy, the top-10 share and the worst losing streak of a list of R results.
    Luk for reference (Muninn's audit of 461 trades in 2026; Kinfo verified): win rate 19.3% (20.4%), payoff 8.0:1
    (~7:1), 66% of trades at the full -1R, the 10 best trades 73% of the net R, worst streak 33"""
    n = len(rs)
    if not n:
        return dict(n=0)
    wins = [r for r in rs if r > 0]
    losses = [r for r in rs if r <= 0]
    streak = best = 0
    for r in rs:
        streak = streak + 1 if r <= 0 else 0
        best = max(best, streak)
    net = sum(rs)
    top10 = sum(sorted(rs)[-10:])
    avg_w = sum(wins) / len(wins) if wins else 0.0
    avg_l = -sum(losses) / len(losses) if losses else 0.0
    return dict(n=n, win_rate=round(100 * len(wins) / n, 1), avg_win_r=round(avg_w, 2), avg_loss_r=round(avg_l, 2),
                payoff=round(avg_w / avg_l, 2) if avg_l else None, expectancy_r=round(net / n, 3), net_r=round(net, 1),
                top10_share=round(100 * top10 / net, 0) if net > 0 else None, worst_streak=best,
                full_stops_pct=round(100 * sum(1 for r in rs if r <= -0.95) / n, 1))
