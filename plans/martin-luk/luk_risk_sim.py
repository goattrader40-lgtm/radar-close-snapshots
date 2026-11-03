#!/usr/bin/env python3
"""Monte Carlo of Martin Luk's risk model, built from the numbers he and the article you sent published.

Not part of the Radar pipeline: a study for plans/martin-luk/PLAN.md. Run:  python3 plans/martin-luk/luk_risk_sim.py

The trade distribution (one year, 461 trades, the article's "2026 dataset"):
  305 trades at the full -1R stop · 91 winners (19.7%: shorts 23.5% of 42%, longs 16.9% of 58%) · 65 scratches
  (breakeven stops after a trim, small partial losses) · net +300R · the 10 best trades +220R.
Everything below is in R (1R = the planned loss at the stop) and in % of the account at a given risk per trade.
"""
import numpy as np

RNG = np.random.default_rng(20261103)
N_TRADES = 461
N_SIMS = 4000


def luk_trades():
    """the 461 R results, built to match the published totals exactly"""
    top10 = np.array([13, 15, 17, 19, 21, 22, 24, 27, 29, 33], float)          # +220R
    stops = -np.ones(305)                                                        # -305R
    scratch = np.linspace(-0.6, 0.4, 65)                                         # about -6.5R
    rest_sum = 300 - top10.sum() - stops.sum() - scratch.sum()                   # the other 81 winners
    q = (np.arange(81) + 0.5) / 81
    w = np.exp(np.log(3.0) + 0.8 * np.sqrt(2) * erfinv(2 * q - 1))               # lognormal shape, median ~3R
    for _ in range(50):                                                          # scale to the total, none over 12R
        w = np.clip(w * rest_sum / w.sum(), 1.0, 12.0)
    out = np.concatenate([stops, scratch, w, top10])
    assert abs(out.sum() - 300) < 1e-6 and out.size == N_TRADES
    return out


def erfinv(y):
    """inverse error function (numpy has none): Giles' approximation, plenty for quantiles"""
    y = np.asarray(y, float)
    w = -np.log((1.0 - y) * (1.0 + y))
    a = w - 2.5
    p1 = 2.81022636e-08
    for c in (3.43273939e-07, -3.5233877e-06, -4.39150654e-06, 0.00021858087, -0.00125372503, -0.00417768164, 0.246640727, 1.50140941):
        p1 = c + p1 * a
    b = np.sqrt(np.maximum(w, 5)) - 3
    p2 = -0.000200214257
    for c in (0.000100950558, 0.00134934322, -0.00367342844, 0.00573950773, -0.0076224613, 0.00943887047, 1.00167406, 2.83297682):
        p2 = c + p2 * b
    p = np.where(w < 5, p1, p2)
    return p * y


def path_stats(r_seq, risk):
    """equity path of one year at `risk` (fraction of the account per 1R), compounding: return, max drawdown, worst losing streak"""
    eq = np.cumprod(1 + risk * r_seq)
    peak = np.maximum.accumulate(np.concatenate([[1.0], eq]))[1:]
    dd = 1 - eq / peak
    losses = r_seq < 0
    streak = best = 0
    for x in losses:
        streak = streak + 1 if x else 0
        best = max(best, streak)
    return eq[-1] - 1, dd.max(), best


def table_fixed(R, risks, label):
    """each simulated year draws its trades from the distribution with replacement: a year can catch fewer or more of
    the big winners, which is what decides the year"""
    print(f"\n== {label}: {R.size} trades a year, expectancy {R.mean():+.2f}R, win rate {100 * (R > 0.5).mean():.1f}%")
    print("risk/trade | median year | 5th pct year | median maxDD | 95th pct maxDD | P(maxDD>25%) | worst streak (median / 95th)")
    for f in risks:
        res = np.array([path_stats(RNG.choice(R, size=R.size, replace=True), f) for _ in range(N_SIMS)])
        print(f"  {100 * f:4.2f}%   |  {100 * np.median(res[:, 0]):+8.0f}%  |  {100 * np.percentile(res[:, 0], 5):+8.0f}%  |"
              f"   {100 * np.median(res[:, 1]):4.1f}%     |    {100 * np.percentile(res[:, 1], 95):4.1f}%      |"
              f"   {100 * (res[:, 1] > 0.25).mean():4.1f}%     |   {np.median(res[:, 2]):.0f} / {np.percentile(res[:, 2], 95):.0f}")


def kelly(R):
    """the growth-optimal risk per trade on this distribution (maximises E[log(1 + f R)])"""
    fs = np.linspace(0.001, 0.2, 400)
    g = [np.mean(np.log1p(np.maximum(f * R, -0.999))) for f in fs]
    return fs[int(np.argmax(g))]


# ---------- regimes: trend months and chop months (December 2025: 74 trades, 9 winners, -26.6%) ----------
def month_trades(chop, rng, base):
    """one month of trades: a trend month draws from the year's distribution; a chop month trades more (Luk's December:
    74 trades), wins 12% of the time and the winners stay small (capped at 3R)"""
    if not chop:
        return rng.choice(base, size=rng.poisson(38))
    n = rng.poisson(70)
    win = rng.random(n) < 0.12
    r = np.where(win, rng.uniform(1.0, 3.0, n), np.where(rng.random(n) < 0.85, -1.0, rng.uniform(-0.6, 0.2, n)))
    return r


def run_policy(policy, years=2000, base=None, p_chop=0.25, gap_p=0.0, seed=7):
    """a year of 12 months under a sizing policy; returns per-year (return, maxDD, worst month)"""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(years):
        eq, peak, maxdd, worst_m = 1.0, 1.0, 0.0, 0.0
        streak = 0
        for m in range(12):
            chop = rng.random() < p_chop
            start_m = eq
            for r in month_trades(chop, rng, base):
                if gap_p and r <= -0.99 and rng.random() < gap_p / 0.66:    # a stop that gapped through: 2-6R instead of 1R
                    r = -rng.uniform(2, 6)
                mult = policy(eq, peak, streak, eq / start_m - 1)
                if mult <= 0:
                    continue
                eq *= 1 + 0.005 * mult * r
                streak = streak + 1 if r < 0 else 0
                peak = max(peak, eq)
                maxdd = max(maxdd, 1 - eq / peak)
            worst_m = min(worst_m, eq / start_m - 1)
        out.append((eq - 1, maxdd, worst_m))
    return np.array(out)


def fixed(eq, peak, streak, mtd):
    return 1.0


def throttle(eq, peak, streak, mtd):
    """the brake proposed in PLAN.md (Task 1, section 1.4): drawdown ladder + losing-streak brake + monthly loss limit"""
    dd = 1 - eq / peak
    m = 1.0 if dd < 0.05 else 0.5 if dd < 0.10 else 0.25
    if streak >= 5:
        m = min(m, 0.5)
    if mtd <= -0.08:
        m = min(m, 0.25)
    if mtd <= -0.12:
        return 0.0          # paper only for the rest of the month
    return m


def throttle_loose(eq, peak, streak, mtd):
    """the same brake with wider steps: full size down to an 8% drawdown, half to 15%, then a quarter"""
    dd = 1 - eq / peak
    m = 1.0 if dd < 0.08 else 0.5 if dd < 0.15 else 0.25
    if streak >= 7:
        m = min(m, 0.5)
    if mtd <= -0.10:
        m = min(m, 0.25)
    if mtd <= -0.15:
        return 0.0
    return m


def throttle_cushion(eq, peak, streak, mtd):
    """the brake plus Luk's 'more risk on A+ setups when I have a cushion': 1.5x while the month is up 5%+ and the
    account is at its high"""
    m = throttle(eq, peak, streak, mtd)
    if m == 1.0 and mtd >= 0.05 and eq >= peak * 0.98:
        m = 1.5
    return m


def table_policies(base, gap_p=0.0, label="", p_chop=0.25):
    print(f"\n== Policies at 0.5% base risk, {100 * p_chop:.0f}% of months chop{label}")
    print("policy            | median year | 5th pct year | median maxDD | 95th pct maxDD | worst month (median / 5th pct)")
    for name, pol in (("fixed 0.5%", fixed), ("throttle", throttle), ("throttle loose", throttle_loose), ("throttle+cushion", throttle_cushion)):
        res = run_policy(pol, base=base, gap_p=gap_p, p_chop=p_chop)
        print(f"  {name:16s}|  {100 * np.median(res[:, 0]):+8.0f}%  |  {100 * np.percentile(res[:, 0], 5):+8.0f}%  |"
              f"   {100 * np.median(res[:, 1]):4.1f}%     |    {100 * np.percentile(res[:, 1], 95):4.1f}%      |"
              f"   {100 * np.median(res[:, 2]):+5.1f}% / {100 * np.percentile(res[:, 2], 5):+5.1f}%")


def financed_stop_table():
    print("\n== Financed stop: sell a fraction f at +kR, then the stop on the rest that makes the worst case exactly 0R")
    print("   stop = -f*k/(1-f) R  (Luk: 15% at +4R banks 0.60R; breakeven on the rest locks +0.60R; -0.71R locks 0R)")
    for f in (0.10, 0.15, 0.20, 0.25):
        print("   f=%2d%%: " % (100 * f) + "  ".join(f"+{k}R -> stop {-f * k / (1 - f):+.2f}R (banked {f * k:.2f}R)" for k in (3, 4, 5)))


def sizing_table():
    print("\n== Position size = risk / stop distance (capped at 35% of the account)")
    print("   stop %  | 0.30% risk | 0.50% risk | 0.75% risk")
    for s in (1.0, 1.43, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0):
        print(f"   {s:4.2f}%  |   " + "   |   ".join(f"{min(1e4 * r / s, 35):5.1f}%" + ("*" if 1e4 * r / s > 35 else " ") for r in (0.003, 0.005, 0.0075)))
    print("   * capped at 35%: the trade then risks less than planned (0.35 x the stop %)")


if __name__ == "__main__":
    R = luk_trades()
    print(f"Luk-like year: {R.size} trades, net {R.sum():+.0f}R, winners {(R > 0.5).sum()} ({100 * (R > 0.5).mean():.1f}%), "
          f"full stops {(R <= -0.999).sum()}, best 10 = {np.sort(R)[-10:].sum():+.0f}R, expectancy {R.mean():+.3f}R a trade")
    no10 = np.sort(R)[:-10]
    half = np.where(R > 0.5, R * 0.6, R)          # winners 40% smaller (a worse execution of the same trades)
    print(f"Without the 10 best trades: {no10.mean():+.3f}R a trade; winners 40% smaller: {half.mean():+.3f}R a trade")
    print(f"Growth-optimal risk per trade (full Kelly): Luk-like {100 * kelly(R):.1f}% · without the 10 best {100 * kelly(no10):.1f}% · "
          f"winners 40% smaller {100 * kelly(half):.1f}%")
    risks = (0.0025, 0.003, 0.005, 0.0075, 0.01, 0.02, 0.03)
    table_fixed(R, risks, "Luk-like year, trades in random order")
    table_fixed(no10, risks, "Same year without the 10 best trades (the edge without the fat tail)")
    table_fixed(half, (0.003, 0.005, 0.01), "Same year, winners 40% smaller (slippage, earlier exits)")
    table_policies(R, p_chop=1 / 12)
    table_policies(R)
    table_policies(R, gap_p=0.02, label=", 2% of stops gap through to -2..-6R")
    financed_stop_table()
    sizing_table()
