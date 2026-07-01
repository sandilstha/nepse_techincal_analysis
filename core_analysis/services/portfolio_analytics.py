"""
portfolio_analytics.py — valuation + risk roll-ups for a user's Portfolio.

Everything is derived from the positions in a ``Portfolio`` plus the local NEPSE
end-of-day tables (``NepseDailyStockPrice`` for prices, ``NepseMarketIndex`` for
the benchmark, ``CompanyProfile`` for sector/name). No cost basis is required —
the Meroshare "My Shares" CSV carries only balances and current prices — so this
focuses on *position* risk (exposure, concentration, volatility, beta), not P&L.

NEPSE realities deliberately shaped the design:
  * Holdings are marked to each scrip's most-recent close (not a single session),
    because illiquid names don't trade every day.
  * Volatility / beta are best-effort and degrade to None on thin history; they
    are close-to-close estimates and inherit NEPSE's stale-price / circuit-band
    quirks, so they're presented as estimates, not guarantees.
  * Portfolio beta is the weight-weighted sum of holding betas (valid); a true
    covariance-based portfolio VaR/vol is a later phase and is NOT faked here.
"""
from __future__ import annotations

import logging
import math
from datetime import timedelta

from django.core.cache import cache

logger = logging.getLogger(__name__)

NEPSE_INDEX_NAME = "NEPSE Index"  # matched case-insensitively (data has mixed casing)
RISK_LOOKBACK_DAYS = 370          # ~1 trading year of sessions for vol/beta/VaR
TRADING_DAYS_YEAR = 246           # NEPSE trades Sun–Fri (~246 sessions/yr)
MIN_RETURNS = 20                  # need at least this many returns for vol/beta
MIN_VAR_POINTS = 30               # need at least this many sessions for VaR
VAR_HORIZON_DAYS = 10             # second VaR horizon (√-time scaled)
# Per-holding VaR horizons for the Portfolio Summary desk, in NEPSE sessions.
VAR_1W_SESSIONS = 5               # ~1 trading week
VAR_1M_SESSIONS = 20             # ~1 trading month
Z95, Z99 = 1.645, 2.326           # normal quantiles for parametric VaR
# Hypothetical market shocks (% NEPSE move) propagated to the book via beta.
STRESS_SHOCKS = (-20, -10, -5, 10)
# HHI bands (0–10000), aligned with the broker-analytics concentration read.
HHI_MODERATE = 1500
HHI_HIGH = 2500
# Liquidity: average daily volume window + the share of ADV a desk can realistically
# trade per session without moving the price (days-to-liquidate denominator).
LIQ_LOOKBACK_DAYS = 45            # ~30 sessions of ADV
PARTICIPATION_RATE = 0.20
DTL_LIQUID, DTL_MODERATE = 1.0, 5.0   # days-to-liquidate tier thresholds
CACHE_TTL = 180

# Default investment-policy limits monitored on every portfolio. "warn" raises a
# watch, "breach" a violation. Sensible institutional defaults tuned for a
# concentrated NEPSE retail book; a future per-user RiskLimit model can override.
LIMITS = {
    "single_name": {"warn": 12.0, "breach": 15.0},    # max one-stock weight %
    "top5": {"warn": 45.0, "breach": 55.0},           # max top-5 weight %
    "sector": {"warn": 30.0, "breach": 40.0},         # max one-sector weight %
    "illiquid": {"warn": 15.0, "breach": 25.0},       # max % in >5-day-to-exit names
    "untradeable": {"warn": 3.0, "breach": 8.0},      # max % with no ADV
    "var_1d_95": {"warn": 3.0, "breach": 5.0},         # max 1-day 95% VaR %
    "diversification": {"warn": 10.0, "breach": 6.0},  # min effective holdings
    "beta": {"soft": (0.6, 1.4), "hard": (0.4, 1.6)},  # acceptable beta band
}


def _f(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# ─────────────────────────────────────────────────────────────────────────────
# Reference data (latest prices, sectors, names)
# ─────────────────────────────────────────────────────────────────────────────
def _latest_session():
    from core_analysis.models import NepseDailyStockPrice

    return (
        NepseDailyStockPrice.objects.order_by("-business_date")
        .values_list("business_date", flat=True)
        .first()
    )


def _latest_prices(symbols):
    """{symbol: (close, business_date, market_cap)} at each symbol's MOST RECENT
    session — illiquid scrips may not have a row on the very latest day."""
    from core_analysis.models import NepseDailyStockPrice

    if not symbols:
        return {}
    latest = _latest_session()
    if not latest:
        return {}
    start = latest - timedelta(days=20)
    rows = (
        NepseDailyStockPrice.objects.filter(
            symbol__in=symbols, business_date__gte=start
        )
        .order_by("symbol", "-business_date")
        .values_list("symbol", "business_date", "close_price", "market_capitalization")
    )
    out = {}
    for sym, bd, close, mcap in rows:
        if sym not in out:
            out[sym] = (_f(close), bd, _f(mcap))
    return out


def _company_meta(symbols):
    """{symbol: (security_name, sector_name)} from CompanyProfile (best-effort)."""
    from core_analysis.models import CompanyProfile

    meta = {}
    try:
        for sym, name, sector in CompanyProfile.objects.filter(
            symbol__in=symbols
        ).values_list("symbol", "security_name", "sector_name"):
            meta[sym] = (name or sym, sector or "Other")
    except Exception:  # pragma: no cover - reference table optional
        meta = {}
    return meta


def _liquidity(symbols):
    """Average daily volume / turnover per symbol → ``({sym: {...}}, sessions)``.

    ADV is the whole-market traded quantity for the scrip averaged over the
    *market* sessions in the window (``total_traded_quantity`` from the EOD
    table), NOT over only the days it traded — so a name that prints on 3 of 22
    sessions is correctly scored as thin, not falsely liquid.
    """
    from core_analysis.models import NepseDailyStockPrice

    out = {}
    if not symbols:
        return out, 0
    try:
        latest = _latest_session()
        if not latest:
            return out, 0
        start = latest - timedelta(days=LIQ_LOOKBACK_DAYS)
        # True market-session count over the window, taken from the whole EOD
        # table (NOT just the held symbols' trade days) — otherwise a book of
        # thin names would divide by too few sessions and look falsely liquid.
        sessions = (
            NepseDailyStockPrice.objects.filter(business_date__gte=start)
            .values("business_date").distinct().count()
        )
        rows = NepseDailyStockPrice.objects.filter(
            symbol__in=symbols, business_date__gte=start
        ).values_list("symbol", "business_date", "total_traded_quantity", "total_traded_value")
        agg = {}
        for sym, bd, q, v in rows:
            a = agg.setdefault(sym, [0.0, 0.0])
            a[0] += _f(q)
            a[1] += _f(v)
        sessions = sessions or 1
        for sym, (q, v) in agg.items():
            out[sym] = {"adv_qty": q / sessions, "adv_turnover": v / sessions}
        return out, sessions
    except Exception:  # pragma: no cover - liquidity overlay is best-effort
        logger.exception("liquidity load failed")
        return out, 0


# ─────────────────────────────────────────────────────────────────────────────
# Risk stats (per-holding volatility + beta to NEPSE)
# ─────────────────────────────────────────────────────────────────────────────
def _returns(series):
    """Close-to-close simple returns from a date-sorted [(date, close), …]."""
    out = {}
    prev = None
    for bd, close in series:
        if prev is not None and prev[1]:
            out[bd] = (close - prev[1]) / prev[1]
        prev = (bd, close)
    return out


def _stdev(values):
    n = len(values)
    if n < 2:
        return None
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    return math.sqrt(var)


def _load_returns(symbols):
    """(stock_ret, index_ret) daily simple returns over the risk window.

    ``stock_ret`` is ``{symbol: {date: ret}}``; ``index_ret`` is ``{date: ret}``
    for the NEPSE benchmark (deduped by date, mixed-case name). Best-effort —
    returns empties on any failure so risk is just omitted, never fatal.
    """
    from core_analysis.models import NepseDailyStockPrice, NepseMarketIndex

    stock_ret, index_ret = {}, {}
    if not symbols:
        return stock_ret, index_ret
    try:
        latest = _latest_session()
        if not latest:
            return stock_ret, index_ret
        start = latest - timedelta(days=RISK_LOOKBACK_DAYS)

        idx_rows = NepseMarketIndex.objects.filter(
            sector_name__iexact=NEPSE_INDEX_NAME, business_date__gte=start
        ).values_list("business_date", "close_index")
        idx_map = {}
        for bd, c in idx_rows:
            idx_map[bd] = _f(c)
        index_ret = _returns(sorted(idx_map.items()))

        series = {}
        rows = (
            NepseDailyStockPrice.objects.filter(
                symbol__in=symbols, business_date__gte=start
            )
            .order_by("symbol", "business_date")
            .values_list("symbol", "business_date", "close_price")
        )
        for sym, bd, close in rows:
            series.setdefault(sym, []).append((bd, _f(close)))
        for sym, ser in series.items():
            stock_ret[sym] = _returns(ser)
    except Exception:  # pragma: no cover - risk overlay is best-effort
        logger.exception("portfolio return load failed")
    return stock_ret, index_ret


def _beta_resid(stock_ret, index_ret):
    """OLS (beta, residual daily std) of a stock vs the index over shared dates.

    The residual std is the stock-specific (idiosyncratic) daily volatility left
    after the market move is regressed out — the raw material for the factor risk
    decomposition. Returns ``(None, None)`` on thin overlap.
    """
    common = [d for d in stock_ret if d in index_ret]
    if len(common) < MIN_RETURNS:
        return None, None
    xs = [index_ret[d] for d in common]
    ys = [stock_ret[d] for d in common]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n - 1)
    var = sum((x - mx) ** 2 for x in xs) / (n - 1)
    if not var:
        return None, None
    beta = cov / var
    alpha = my - beta * mx
    resid = [ys[k] - (alpha + beta * xs[k]) for k in range(n)]
    return beta, _stdev(resid)


def _parametric_var(vol_annual_pct, sessions):
    """95% parametric VaR as a positive loss *fraction* over ``sessions`` sessions.

    ``vol_annual_pct`` is the annualised volatility % produced by
    ``_per_symbol_stats``; recover the daily sigma and √-time scale it. Returns
    None when volatility is unavailable (thin history) so callers show "—".
    """
    if not vol_annual_pct:
        return None
    daily_sigma = (vol_annual_pct / 100.0) / math.sqrt(TRADING_DAYS_YEAR)
    return Z95 * daily_sigma * math.sqrt(sessions)


def _nepse_index_level():
    """Latest NEPSE Index close + date — the baseline for the beta scenario."""
    from core_analysis.models import NepseMarketIndex

    row = (
        NepseMarketIndex.objects.filter(sector_name__iexact=NEPSE_INDEX_NAME)
        .order_by("-business_date")
        .values_list("business_date", "close_index")
        .first()
    )
    if not row:
        return {"value": None, "date": None}
    return {"value": round(_f(row[1]), 2), "date": row[0].isoformat()}


def _cost_summary(rows):
    """Book value & paper P/L over the holdings that carry a WACC cost basis.

    Computed on the *costed* subset only (market value vs book value of the same
    names) so a partial WACC import never distorts the paper P/L. ``has_cost`` is
    False until the user imports the 'My WACC' report.
    """
    costed = [r for r in rows if r.get("cost_value") is not None]
    if not costed:
        return {"has_cost": False, "covered_count": 0, "book_value": None,
                "costed_market_value": None, "paper_pl": None, "paper_pl_pct": None}
    book = round(sum(r["cost_value"] for r in costed), 2)
    mkt = round(sum(r["value"] for r in costed), 2)
    pl = round(mkt - book, 2)
    return {
        "has_cost": True,
        "covered_count": len(costed),
        "book_value": book,
        "costed_market_value": mkt,
        "paper_pl": pl,
        "paper_pl_pct": round(100.0 * pl / book, 2) if book else None,
    }


def _per_symbol_stats(symbols, stock_ret, index_ret):
    """{symbol: {'vol': annualised %|None, 'beta': float|None, 'resid': daily std|None}}."""
    stats = {s: {"vol": None, "beta": None, "resid": None} for s in symbols}
    for sym, ret in stock_ret.items():
        vals = list(ret.values())
        sd = _stdev(vals) if len(vals) >= MIN_RETURNS else None
        beta, resid = _beta_resid(ret, index_ret)
        stats[sym] = {
            "vol": round(sd * math.sqrt(TRADING_DAYS_YEAR) * 100.0, 1) if sd else None,
            "beta": round(beta, 2) if beta is not None else None,
            "resid": resid,                       # daily residual std (unrounded)
        }
    return stats


# ─────────────────────────────────────────────────────────────────────────────
# Value at Risk + stress testing
# ─────────────────────────────────────────────────────────────────────────────
def _percentile(sorted_vals, q):
    """Linear-interpolated quantile of an already-sorted list (q in 0..1)."""
    n = len(sorted_vals)
    if n == 0:
        return None
    if n == 1:
        return sorted_vals[0]
    pos = q * (n - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, n - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def _portfolio_returns(weight_frac, stock_ret):
    """Current-weights historical return series: rₜ = Σ wᵢ·rᵢ,ₜ.

    A held name with no trade on date t contributes 0 (NEPSE illiquidity =
    no-move assumption), so the book is valued on every session any holding
    traded. Returns ``{date: portfolio_return}``.
    """
    dates = set()
    for sym in weight_frac:
        dates.update(stock_ret.get(sym, {}).keys())
    out = {}
    for d in dates:
        out[d] = sum(w * stock_ret.get(sym, {}).get(d, 0.0) for sym, w in weight_frac.items())
    return out


def _max_drawdown(ordered_returns):
    """Worst peak-to-trough on the current-holdings equity curve (≤ 0)."""
    eq = peak = 1.0
    mdd = 0.0
    for r in ordered_returns:
        eq *= (1.0 + r)
        peak = max(peak, eq)
        if peak:
            mdd = min(mdd, (eq - peak) / peak)
    return mdd


def _worst_window(ordered_returns, k):
    """Worst compounded return over any k consecutive sessions (≤ 0), or None."""
    n = len(ordered_returns)
    if n < k:
        return None
    worst = None
    for i in range(n - k + 1):
        prod = 1.0
        for r in ordered_returns[i:i + k]:
            prod *= (1.0 + r)
        ret = prod - 1.0
        worst = ret if worst is None else min(worst, ret)
    return worst


def _risk_block(weight_frac, total_value, port_beta, stock_ret):
    """Historical-simulation VaR/CVaR + beta-propagated stress scenarios.

    Historical simulation is primary (NEPSE returns are fat-tailed and circuit
    bands truncate them, so a normal-distribution VaR is unreliable); the
    parametric figure is included only as a flagged comparison. All ₨ figures are
    losses on the marked-to-market book (positive = expected loss).
    """
    if total_value <= 0:
        return {"ok": False, "reason": "Portfolio has no marked value."}
    port = _portfolio_returns(weight_frac, stock_ret)
    if len(port) < MIN_VAR_POINTS:
        return {"ok": False,
                "reason": f"Not enough price history for VaR (need {MIN_VAR_POINTS}+ sessions)."}

    items = sorted(port.items())                 # by date, ascending
    rets = [r for _d, r in items]
    svals = sorted(rets)
    sigma = _stdev(rets) or 0.0
    s10 = math.sqrt(VAR_HORIZON_DAYS)

    def loss_at(q):                              # historical VaR (positive loss)
        p = _percentile(svals, q)
        return -p if p is not None else 0.0

    v95, v99 = loss_at(0.05), loss_at(0.01)
    thr = _percentile(svals, 0.05)
    tail = [r for r in rets if thr is not None and r <= thr]
    cvar95 = -(sum(tail) / len(tail)) if tail else v95
    worst = min(items, key=lambda kv: kv[1])
    mdd = _max_drawdown(rets)
    w5 = _worst_window(rets, 5)

    def rs(p):
        return round(p * total_value, 2)

    beta = port_beta if port_beta is not None else 1.0
    scenarios = [
        {"label": f"NEPSE {shock:+d}%", "shock": shock,
         "impact_pct": round(beta * shock, 2), "impact_rs": rs(beta * shock / 100.0)}
        for shock in STRESS_SHOCKS
    ]

    return {
        "ok": True,
        "sessions": len(rets),
        "ann_vol_pct": round(sigma * math.sqrt(TRADING_DAYS_YEAR) * 100.0, 1) if sigma else None,
        "var": {
            "hist_95_1d_pct": round(v95 * 100, 2), "hist_95_1d_rs": rs(v95),
            "hist_99_1d_pct": round(v99 * 100, 2), "hist_99_1d_rs": rs(v99),
            "hist_95_10d_pct": round(v95 * s10 * 100, 2), "hist_95_10d_rs": rs(v95 * s10),
            "cvar_95_1d_pct": round(cvar95 * 100, 2), "cvar_95_1d_rs": rs(cvar95),
            "param_95_1d_pct": round(Z95 * sigma * 100, 2), "param_95_1d_rs": rs(Z95 * sigma),
            # Diversified parametric VaR at the summary horizons — Z·σ_p·√h on the
            # *portfolio* daily sigma (correlation already baked into the return
            # series), so it is lower than the sum of per-holding VaRs.
            "param_95_1w_pct": round(Z95 * sigma * math.sqrt(VAR_1W_SESSIONS) * 100, 2),
            "param_95_1w_rs": rs(Z95 * sigma * math.sqrt(VAR_1W_SESSIONS)),
            "param_95_1m_pct": round(Z95 * sigma * math.sqrt(VAR_1M_SESSIONS) * 100, 2),
            "param_95_1m_rs": rs(Z95 * sigma * math.sqrt(VAR_1M_SESSIONS)),
        },
        "worst_day": {"date": worst[0].isoformat(), "pct": round(worst[1] * 100, 2),
                      "rs": rs(worst[1])},
        "max_drawdown_pct": round(mdd * 100, 2), "max_drawdown_rs": rs(mdd),
        "worst_5d_pct": round(w5 * 100, 2) if w5 is not None else None,
        "worst_5d_rs": rs(w5) if w5 is not None else None,
        "beta_used": round(beta, 2),
        "scenarios": scenarios,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Factor risk decomposition (single-factor: NEPSE market + stock-specific)
# ─────────────────────────────────────────────────────────────────────────────
def _factor_decomposition(rows, stats, index_ret):
    """Split portfolio risk into systematic (market) vs idiosyncratic, and
    attribute it by sector and by name — the institutional "where does my risk
    come from" view.

    Variance model (single NEPSE factor, residuals assumed uncorrelated):
        σ²_p = β_p,eff²·σ²_m + Σ wᵢ²·residᵢ²
    Each holding's risk contribution = wᵢ·βᵢ·β_p,eff·σ²_m (systematic) +
    wᵢ²·residᵢ² (idiosyncratic); contributions sum *exactly* to σ²_p, so the
    sector/name splits are exhaustive. Names lacking return history sit outside
    the covered weight rather than distorting the result.
    """
    idx_vals = list(index_ret.values())
    sigma_m = _stdev(idx_vals) if len(idx_vals) >= MIN_RETURNS else None
    if not sigma_m:
        return {"ok": False, "reason": "No market history for the factor model."}
    sm2 = sigma_m * sigma_m

    covered = []
    for r in rows:
        st = stats.get(r["symbol"], {})
        b, resid = st.get("beta"), st.get("resid")
        if b is not None and resid is not None:
            covered.append((r, b, resid, r["weight"] / 100.0))
    if not covered:
        return {"ok": False, "reason": "Not enough return history to decompose risk."}

    beta_p = sum(w * b for _r, b, _e, w in covered)
    sys_var = beta_p * beta_p * sm2
    idio_var = sum((w * w) * (e * e) for _r, _b, e, w in covered)
    total_var = sys_var + idio_var
    if total_var <= 0:
        return {"ok": False, "reason": "Degenerate risk (no variance)."}

    sectors, names = {}, []
    for r, b, e, w in covered:
        rc = (w * b * beta_p * sm2) + (w * w * e * e)   # exhaustive contribution
        sectors[r["sector"]] = sectors.get(r["sector"], 0.0) + rc
        names.append((r["symbol"], rc))

    def ann(v):
        return round(math.sqrt(max(v, 0.0) * TRADING_DAYS_YEAR) * 100.0, 1)

    sec_rows = sorted(
        ({"sector": s, "pct": round(100.0 * rc / total_var, 1)} for s, rc in sectors.items()),
        key=lambda x: x["pct"], reverse=True,
    )
    name_rows = sorted(
        ({"symbol": s, "pct": round(100.0 * rc / total_var, 1)} for s, rc in names),
        key=lambda x: x["pct"], reverse=True,
    )
    return {
        "ok": True,
        "total_vol_pct": ann(total_var),
        "systematic_vol_pct": ann(sys_var),
        "idiosyncratic_vol_pct": ann(idio_var),
        "systematic_pct": round(100.0 * sys_var / total_var, 1),
        "idiosyncratic_pct": round(100.0 * idio_var / total_var, 1),
        "beta": round(beta_p, 2),
        "covered_weight_pct": round(sum(w for _r, _b, _e, w in covered) * 100.0, 1),
        "sectors": sec_rows[:8],
        "top_contributors": name_rows[:6],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Compliance: investment-policy limit monitoring
# ─────────────────────────────────────────────────────────────────────────────
def _check_max(key, label, current, limit_fmt, detail=""):
    """A 'must stay below' limit (concentration / exposure / VaR)."""
    lim = LIMITS[key]
    status = "breach" if current >= lim["breach"] else "warn" if current >= lim["warn"] else "ok"
    return {"key": key, "label": label, "status": status,
            "current": limit_fmt.format(current), "limit": "≤ " + limit_fmt.format(lim["breach"]),
            "detail": detail}


def build_compliance(rows, sectors, concentration, risk, port_beta, total):
    """Evaluate the portfolio against the default investment-policy limits.

    Returns ``{summary, checks}`` where each check is ok / warn / breach with its
    current value, the limit, and the offending names where relevant. Pure
    roll-up of metrics already computed — no extra queries.
    """
    checks = []
    if not rows or not total:
        return {"summary": {"ok": 0, "warn": 0, "breach": 0}, "checks": []}

    # Single-name concentration.
    over = [r for r in rows if r["weight"] >= LIMITS["single_name"]["warn"]]
    top = concentration.get("top_symbol")
    checks.append(_check_max(
        "single_name", "Single-stock concentration", concentration.get("top_weight", 0.0),
        "{:.1f}%",
        detail=(", ".join(f"{r['symbol']} {r['weight']:.1f}%" for r in over[:4]) if over
                else (f"largest: {top}" if top else "")),
    ))

    # Top-5 concentration.
    top5 = sum(r["weight"] for r in sorted(rows, key=lambda r: r["weight"], reverse=True)[:5])
    checks.append(_check_max("top5", "Top-5 holdings concentration", top5, "{:.1f}%",
                             detail=f"{min(5, len(rows))} largest positions"))

    # Sector concentration.
    if sectors:
        worst = max(sectors, key=lambda s: s["weight"])
        checks.append(_check_max("sector", "Sector concentration", worst["weight"], "{:.1f}%",
                                 detail=f"{worst['sector']} ({worst['weight']:.1f}%)"))

    # Illiquid + untradeable exposure.
    illiq_val = sum(r["value"] for r in rows if r["dtl"] is None or r["dtl"] > DTL_MODERATE)
    untr_val = sum(r["value"] for r in rows if r["dtl"] is None)
    illiq_names = [r for r in rows if (r["dtl"] is None or r["dtl"] > DTL_MODERATE)]
    checks.append(_check_max(
        "illiquid", "Illiquid exposure (>5 days to exit)", 100.0 * illiq_val / total, "{:.1f}%",
        detail=(", ".join(r["symbol"] for r in illiq_names[:5]) if illiq_names else "none"),
    ))
    untr_names = [r["symbol"] for r in rows if r["dtl"] is None]
    checks.append(_check_max("untradeable", "Untradeable exposure (no volume)",
                             100.0 * untr_val / total, "{:.1f}%",
                             detail=(", ".join(untr_names[:6]) + (" +%d more" % (len(untr_names) - 6)
                                     if len(untr_names) > 6 else "")) if untr_names else "none"))

    # 1-day 95% VaR.
    if risk and risk.get("ok"):
        checks.append(_check_max("var_1d_95", "1-day Value at Risk (95%)",
                                 risk["var"]["hist_95_1d_pct"], "{:.2f}%",
                                 detail=f"≈ Rs {risk['var']['hist_95_1d_rs']:,.0f} loss"))

    # Diversification (a minimum, not a maximum).
    eff = concentration.get("effective_holdings", 0.0)
    dlim = LIMITS["diversification"]
    dstatus = "breach" if eff < dlim["breach"] else "warn" if eff < dlim["warn"] else "ok"
    checks.append({"key": "diversification", "label": "Diversification (effective holdings)",
                   "status": dstatus, "current": f"{eff:.1f}", "limit": f"≥ {dlim['breach']:.0f}",
                   "detail": f"{len(rows)} positions"})

    # Portfolio beta band.
    soft, hard = LIMITS["beta"]["soft"], LIMITS["beta"]["hard"]
    if port_beta is None:
        bstatus, bcur, bdetail = "ok", "—", "insufficient history"
    else:
        bstatus = ("breach" if port_beta < hard[0] or port_beta > hard[1]
                   else "warn" if port_beta < soft[0] or port_beta > soft[1] else "ok")
        bcur = f"{port_beta:.2f}"
        bdetail = "more volatile than market" if port_beta > 1 else "less volatile than market"
    checks.append({"key": "beta", "label": "Market beta within band", "status": bstatus,
                   "current": bcur, "limit": f"{hard[0]:.1f}–{hard[1]:.1f}", "detail": bdetail})

    summary = {
        "ok": sum(1 for c in checks if c["status"] == "ok"),
        "warn": sum(1 for c in checks if c["status"] == "warn"),
        "breach": sum(1 for c in checks if c["status"] == "breach"),
    }
    # Worst-first so violations surface at the top.
    order = {"breach": 0, "warn": 1, "ok": 2}
    checks.sort(key=lambda c: order[c["status"]])
    return {"summary": summary, "checks": checks}


# ─────────────────────────────────────────────────────────────────────────────
# Main payload
# ─────────────────────────────────────────────────────────────────────────────
def build_portfolio_payload(portfolio):
    """Full valuation + risk roll-up for one portfolio (cached briefly)."""
    holdings = list(portfolio.holdings.all())
    latest = _latest_session()
    # Full-resolution timestamp (microseconds) so two imports within the same
    # second don't collide on a 1-second-truncated key and serve stale data.
    ck = f"pf_payload_{portfolio.id}_{portfolio.updated_at.timestamp()}_{latest}"
    cached = cache.get(ck)
    if cached is not None:
        return cached

    symbols = [h.symbol for h in holdings]
    costs = {c.symbol: c for c in portfolio.costs.all()}  # WACC cost basis by symbol
    prices = _latest_prices(symbols)
    meta = _company_meta(symbols)
    stock_ret, index_ret = _load_returns(symbols)
    stats = _per_symbol_stats(symbols, stock_ret, index_ret)
    liq, liq_sessions = _liquidity(symbols)

    rows, total = [], 0.0
    for h in holdings:
        live = prices.get(h.symbol)
        if live:
            price, priced_on, mcap = live
            price_source = "eod"
        else:
            # Fall back to the imported snapshot price when the scrip isn't in the
            # local EOD table (newly listed / delisted / symbol typo).
            price = _f(h.last_close) or _f(h.ltp)
            priced_on, mcap = None, 0.0
            price_source = "snapshot"
        qty = _f(h.quantity)
        value = qty * price
        total += value
        name, sector = meta.get(h.symbol, (h.symbol, "Other"))
        st = stats.get(h.symbol, {})

        # Days to liquidate at PARTICIPATION_RATE of ADV; tier the result.
        adv = (liq.get(h.symbol) or {}).get("adv_qty", 0.0)
        if adv > 0 and qty > 0:
            dtl = qty / (PARTICIPATION_RATE * adv)
            tier = ("liquid" if dtl <= DTL_LIQUID
                    else "moderate" if dtl <= DTL_MODERATE else "illiquid")
        else:
            dtl, tier = None, "untradeable"

        # Per-holding parametric VaR (95%) at the 1-week / 1-month horizons, as a
        # signed loss (negative) both in % and in ₨ on this position's value.
        v1w = _parametric_var(st.get("vol"), VAR_1W_SESSIONS)
        v1m = _parametric_var(st.get("vol"), VAR_1M_SESSIONS)

        # Cost basis (WACC), matched by symbol from the imported "My WACC" report.
        # Book value marks the CURRENT balance at its average cost; paper P/L is
        # market value minus that. None until the user imports the WACC report.
        cost = costs.get(h.symbol)
        wacc = _f(cost.wacc_rate) if (cost and cost.wacc_rate is not None) else None
        cost_value = round(wacc * qty, 2) if wacc is not None else None
        pl = round(value - cost_value, 2) if cost_value is not None else None

        rows.append({
            "symbol": h.symbol,
            "name": name,
            "sector": sector,
            "quantity": qty,
            "price": round(price, 2),
            "value": round(value, 2),
            "price_source": price_source,
            "priced_on": priced_on.isoformat() if priced_on else None,
            "market_cap": round(mcap, 2),
            "vol": st.get("vol"),
            "beta": st.get("beta"),
            "wacc": round(wacc, 2) if wacc is not None else None,
            "cost_value": cost_value,
            "pl": pl,
            "var_1w_pct": round(-v1w * 100, 2) if v1w is not None else None,
            "loss_1w": round(-v1w * value, 2) if v1w is not None else None,
            "var_1m_pct": round(-v1m * 100, 2) if v1m is not None else None,
            "loss_1m": round(-v1m * value, 2) if v1m is not None else None,
            "adv_qty": round(adv),
            "dtl": round(dtl, 1) if dtl is not None else None,
            "liq_tier": tier,
        })

    # Weights + concentration.
    for r in rows:
        r["weight"] = round(100.0 * r["value"] / total, 2) if total else 0.0
    rows.sort(key=lambda r: r["value"], reverse=True)

    hhi = sum((r["weight"] / 100.0) ** 2 for r in rows) * 10000.0 if total else 0.0
    eff_n = (10000.0 / hhi) if hhi else 0.0
    top = rows[0] if rows else None
    risk_band = "high" if hhi >= HHI_HIGH else "moderate" if hhi >= HHI_MODERATE else "low"

    # Portfolio beta = Σ wᵢ·βᵢ over holdings that have a beta (re-based to their
    # own weight sum so a few missing betas don't understate it).
    bw = sum(r["weight"] for r in rows if r["beta"] is not None)
    port_beta = (
        round(sum(r["weight"] * r["beta"] for r in rows if r["beta"] is not None) / bw, 2)
        if bw else None
    )

    # Sector exposure.
    sec = {}
    for r in rows:
        s = sec.setdefault(r["sector"], {"sector": r["sector"], "value": 0.0, "count": 0})
        s["value"] += r["value"]
        s["count"] += 1
    sectors = sorted(sec.values(), key=lambda s: s["value"], reverse=True)
    for s in sectors:
        s["value"] = round(s["value"], 2)
        s["weight"] = round(100.0 * s["value"] / total, 2) if total else 0.0

    # Liquidity: how much of the book can be unwound in 1 / 5 sessions, and the
    # least-liquid names. Fraction of a position sellable in D days = min(1, D/dtl).
    def _liq_pct(days):
        if not total:
            return 0.0
        sellable = 0.0
        for r in rows:
            d = r["dtl"]
            if d is None:
                frac = 0.0            # no ADV → can't be unwound
            elif d <= 0:
                frac = 1.0            # rounds to ~0 days → fully liquidatable
            else:
                frac = min(1.0, days / d)
            sellable += r["value"] * frac
        return round(100.0 * sellable / total, 1)

    priced = [r for r in rows if r["dtl"] is not None]
    wsum = sum(r["value"] for r in priced)
    wavg_days = round(sum(r["value"] * r["dtl"] for r in priced) / wsum, 1) if wsum else None
    least_liquid = sorted(
        rows, key=lambda r: r["dtl"] if r["dtl"] is not None else float("inf"), reverse=True
    )[:6]
    liquidity = {
        "ok": bool(rows),
        "participation_pct": round(PARTICIPATION_RATE * 100),
        "lookback_sessions": liq_sessions,
        "liquidatable_1d_pct": _liq_pct(1),
        "liquidatable_5d_pct": _liq_pct(5),
        "wavg_days": wavg_days,
        "illiquid_count": sum(1 for r in rows if r["dtl"] is None or r["dtl"] > DTL_MODERATE),
        "untradeable_count": sum(1 for r in rows if r["dtl"] is None),
        "least_liquid": [
            {"symbol": r["symbol"], "dtl": r["dtl"], "tier": r["liq_tier"],
             "adv_qty": r["adv_qty"], "weight": r["weight"]}
            for r in least_liquid
        ],
    }

    # Value at Risk + stress testing (historical simulation on current weights).
    try:
        weight_frac = {r["symbol"]: r["weight"] / 100.0 for r in rows}
        risk = _risk_block(weight_frac, total, port_beta, stock_ret)
    except Exception:  # pragma: no cover - never let the risk overlay break valuation
        logger.exception("portfolio VaR/stress failed")
        risk = {"ok": False, "reason": "Risk engine error."}

    try:
        factors = _factor_decomposition(rows, stats, index_ret)
    except Exception:  # pragma: no cover
        logger.exception("portfolio factor decomposition failed")
        factors = {"ok": False, "reason": "Factor engine error."}

    try:
        compliance = build_compliance(rows, sectors, {
            "top_weight": top["weight"] if top else 0.0,
            "top_symbol": top["symbol"] if top else None,
            "effective_holdings": round(eff_n, 1),
        }, risk, port_beta, total)
    except Exception:  # pragma: no cover
        logger.exception("portfolio compliance failed")
        compliance = {"summary": {"ok": 0, "warn": 0, "breach": 0}, "checks": []}

    payload = {
        "ok": True,
        "portfolio": portfolio.name,
        "as_of": latest.isoformat() if latest else None,
        "total_value": round(total, 2),
        "holdings_count": len(rows),
        "rows": rows,
        "sectors": sectors,
        "concentration": {
            "hhi": round(hhi),
            "risk": risk_band,
            "effective_holdings": round(eff_n, 1),
            "top_weight": top["weight"] if top else 0.0,
            "top_symbol": top["symbol"] if top else None,
        },
        "portfolio_beta": port_beta,
        "nepse_index": _nepse_index_level(),
        "cost": _cost_summary(rows),
        "snapshot_count": sum(1 for r in rows if r["price_source"] == "snapshot"),
        "risk": risk,
        "liquidity": liquidity,
        "compliance": compliance,
        "factors": factors,
    }
    cache.set(ck, payload, CACHE_TTL)
    return payload
