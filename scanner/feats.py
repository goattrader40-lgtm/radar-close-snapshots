"""Extra measures for a buy point on day j, from the bars up to the day before (no hindsight)."""
import numpy as np
import launch


def _adr(st, k):
    x = float(st.adr[k])
    return x if x > 0 else 5.0


def late(a, j):
    """how late in its run the stock is"""
    st = a.st
    c, h, l = st.c, st.h, st.l
    p = j - 1
    ms = launch.momentum_start(a, p)
    adr_p, adr_ms = _adr(st, p), _adr(st, max(ms, 1))
    # bases since the momentum start: a pullback of 2.5+ ADRs (the ADR at its high) lasting 5+ sessions, then a new high
    H, kh, Lo, bases, depths = h[ms], ms, np.inf, 0, []
    for k in range(ms + 1, p + 1):
        if h[k] > H:
            d = 100 * (1 - Lo / H) / _adr(st, kh) if Lo < np.inf else 0
            if k - kh >= 5 and d >= 2.5:
                bases += 1
                depths.append(round(d, 1))
            H, kh, Lo = h[k], k, np.inf
        else:
            Lo = min(Lo, l[k])
    cur_depth = 100 * (1 - Lo / H) / _adr(st, kh) if Lo < np.inf else 0.0
    chg_adr = [100 * (c[k] / c[k - 1] - 1) / _adr(st, k - 1) for k in range(p - 19, p + 1)]
    gap_adr = [100 * (st.o[k] / c[k - 1] - 1) / _adr(st, k - 1) for k in range(p - 19, p + 1)]
    run = 100 * (c[p] / l[ms] - 1)
    kp = ms + int(np.argmax(h[ms:p + 1]))
    peak = dict(peak_date=st.dates[kp], run_to_peak_pct=round(float(100 * (h[kp] / l[ms] - 1)), 1),
                dd_from_peak_pct=round(float(100 * (1 - c[p] / h[kp])), 1), dd_from_peak_adr=round(float(100 * (1 - c[p] / h[kp]) / _adr(st, kp)), 1),
                max_dd_since_peak_pct=round(float(100 * (1 - l[kp:p + 1].min() / h[kp])), 1), sessions_since_peak=p - kp,
                under50_since_peak=int(np.sum(c[kp:p + 1] < a.e50[kp:p + 1])),
                e21_under_50_since_peak=int(np.any(a.e21[kp:p + 1] < a.e50[kp:p + 1])))
    return dict(**peak,
        ms_date=st.dates[ms], adr_at_start=round(adr_ms, 2), adr_expansion=round(adr_p / adr_ms, 2),
        adr_vs_6m=round(adr_p / _adr(st, max(p - 126, 1)), 2),
        bases_since_start=bases, base_depths=depths, current_base_depth_adr=round(cur_depth, 1),
        stage=bases + 1, run_in_start_adrs=round(run / adr_ms, 1),
        ext50_pct=round(100 * (c[p] / a.e50[p] - 1), 1), e50_over_200_pct=round(100 * (a.e50[p] / a.s200[p] - 1), 1) if a.s200[p] > 0 else None,
        ext10w_adr=round(100 * (c[p] / a.e50[p] - 1) / adr_p, 2),
        climax_days_20=int(sum(x >= 2 for x in chg_adr)), max_up_day_adr_20=round(max(chg_adr), 2),
        gap_ups_20=int(sum(x >= 1 for x in gap_adr)),
        run_per_month=round(run / max(1, (p - ms) / 21), 1),
    )


def trend(a, j, i0):
    """how clean the trend is: legs without chop"""
    st = a.st
    c, o, h, l = st.c, st.o, st.h, st.l
    p = j - 1
    w = 60
    k0 = p - w + 1
    seg = c[k0:p + 1]
    moves = np.abs(np.diff(c[k0 - 1:p + 1])).sum()
    er60 = abs(c[p] - c[k0 - 1]) / moves if moves > 0 else 0
    m20 = np.abs(np.diff(c[p - 20:p + 1])).sum()
    er20 = abs(c[p] - c[p - 20]) / m20 if m20 > 0 else 0
    x = np.arange(w)
    y = np.log(seg)
    r = np.corrcoef(x, y)[0, 1]
    over21 = c[k0:p + 1] > a.e21[k0:p + 1]
    crosses = int(np.sum(over21[1:] != over21[:-1]))
    rng = h[p - 19:p + 1] - l[p - 19:p + 1]
    body = np.abs(c[p - 19:p + 1] - o[p - 19:p + 1])
    wick = float(np.mean(np.where(rng > 0, 1 - body / np.where(rng > 0, rng, 1), 0)))
    chg_adr = np.array([100 * (c[k] / c[k - 1] - 1) / _adr(st, k - 1) for k in range(k0, p + 1)])
    peak, dd = -np.inf, 0.0
    for k in range(k0, p + 1):
        peak = max(peak, c[k])
        dd = max(dd, 100 * (1 - c[k] / peak) / _adr(st, k))
    s0 = max(i0, p - 250)
    since = c[s0:p + 1] > a.e21[s0:p + 1]
    return dict(
        er60=round(float(er60), 3), er20=round(float(er20), 3), r2_60=round(float(r * r) * (1 if r > 0 else -1), 3),
        over21_60=round(float(over21.mean()), 2), x21_60=crosses, under50_60=int(np.sum(c[k0:p + 1] < a.e50[k0:p + 1])),
        wick20=round(wick, 2), big_down_60=int(np.sum(chg_adr <= -1.5)), dd60_adr=round(dd, 1),
        stacked=int(a.e10[p] > a.e21[p] > a.e50[p]), e50_slope10=round(float(100 * (a.e50[p] / a.e50[p - 10] - 1)), 2),
        over21_since_launch=round(float(since.mean()), 2) if since.size else None,
        x21_since_launch=int(np.sum(since[1:] != since[:-1])) if since.size > 1 else 0,
    )


def market(spy, date):
    st = spy.st
    if date not in st.dates:
        return {}
    k = st.dates.index(date) - 1
    return dict(spy_over_50=int(st.c[k] > st.c[k - 49:k + 1].mean()), spy_over_200=int(st.c[k] > spy.s200[k]),
                spy_21_over_50=int(spy.e21[k] > spy.e50[k]), spy_ret20=round(float(100 * (st.c[k] / st.c[k - 20] - 1)), 1))
