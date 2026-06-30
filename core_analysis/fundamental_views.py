"""
fundamental_views.py — Fundamental Analysis Desk.

Reads the company financial-statement line items harvested by the separate
``fundamentals`` app (mapped read-only as ``FinancialStatement``) and serves
them as a per-company desk: headline ratios, the three statements
(Key Statistics / Income Statement / Balance Sheet) for a chosen fiscal
period, and a multi-year trend of the marquee metrics.

Two endpoints:
  * fundamental_analysis_view — renders the desk shell. The symbol list for the
    picker is embedded so the page is usable without a round-trip.
  * fundamental_data_api      — JSON the page fetches on load / on symbol or
    period change.

Amounts are passed through raw with a ``fmt`` hint per field/row so the client
owns presentation (the ``%`` units are stored as fractions, ``Rs. 000`` values
as thousands of rupees, everything else as a plain number).
"""
from __future__ import annotations

import logging
import re
import statistics

from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from core_analysis.models import CompanyProfile, FinancialStatement
from core_analysis.insights_views import _asset_version

logger = logging.getLogger(__name__)

# Statement types present in the source table, in display order, with labels.
STATEMENT_TYPES = (
    ("BS", "Balance Sheet"),
    ("IS", "Income Statement"),
    ("KS", "Key Statistics"),
)

# KS item codes are sector-prefixed (cb_ / hp_ / mfg_ …) but share a stable
# numeric key after "_ks_": 501=revenue, 505=net income, 507=ROA, 508=ROE,
# 509=EPS, 510=P/E, 511=book value, 512=market price, 513=DPS, 504=gross margin.
# Keying on that number (not the full prefixed code) makes every metric below
# work across all sectors, not just banks.
_KS_NUM_RE = re.compile(r"_ks_(\d+)")


def _ks_num(item_code):
    """Numeric KS key from a (possibly sector-prefixed) item_code, or None."""
    m = _KS_NUM_RE.search(item_code or "")
    return m.group(1) if m else None


# Headline ratio cards, by KS numeric code, in display order. fmt drives the
# client formatter: pct (fraction → %), rs000 (thousands of Rs), num (plain).
HEADLINE_METRICS = (
    ("512", "Market Price", "num"),
    ("509", "EPS (Annualized)", "num"),
    ("510", "P/E (Annualized)", "num"),
    ("511", "Book Value / Share", "num"),
    ("508", "ROE (TTM)", "pct"),
    ("507", "ROA (TTM)", "pct"),
    ("513", "Dividend / Share", "num"),
    ("505", "Net Income", "rs000"),
    ("501", "Total Revenue", "rs000"),
    ("504", "Gross Margin (MRQ)", "pct"),
)

# Marquee metrics charted across fiscal years (annual = Q4 rows).
TREND_METRICS = (
    ("501", "Total Revenue", "rs000"),
    ("505", "Net Income", "rs000"),
    ("509", "EPS", "num"),
    ("508", "ROE", "pct"),
)


# ── Morningstar tab: sector-peer ranking + fair-value estimate ──────────────
# Mirrors two Morningstar concepts: "% Rank in Category" (relative standing vs a
# peer group) and the Equity Research "Fair Value Estimate" / Price-to-Fair-Value.
# Everything is computed from the same KS line items, scoped to one fiscal period.

# (key, label, fmt, higher_is_better) for each ranked metric.
MS_METRICS = (
    ("pe", "Price / Earnings", "num", False),
    ("pb", "Price / Book", "num", False),
    ("div_yield", "Dividend Yield", "pct", True),
    ("roe", "Return on Equity", "pct", True),
    ("roa", "Return on Assets", "pct", True),
    ("net_margin", "Net Margin", "pct", True),
)


def _ms_derive(d):
    """Derive the comparable metrics for one ticker from its KS amounts.

    ``d`` is keyed by numeric KS code (see _ks_num), so this is sector-agnostic.
    """
    pe = d.get("510")
    price = d.get("512")
    bvps = d.get("511")
    dps = d.get("513")
    revenue = d.get("501")
    net_income = d.get("505")
    return {
        "pe": pe if (pe and pe > 0) else None,
        "pb": (price / bvps) if (price is not None and bvps and bvps > 0) else None,
        "div_yield": (dps / price) if (dps is not None and price and price > 0) else None,
        "roe": d.get("508"),
        "roa": d.get("507"),
        "net_margin": (net_income / revenue) if (net_income is not None and revenue and revenue > 0) else None,
    }


def _percentile(series, value, higher_better):
    """Percentile (0–100) of ``value`` within ``series`` — always 'better than N%
    of the sector', so a cheap P/E and a high ROE both score high."""
    clean = [v for v in series if v is not None]
    if value is None or len(clean) < 3:
        return None
    if higher_better:
        beaten = sum(1 for v in clean if value >= v)
    else:
        beaten = sum(1 for v in clean if value <= v)
    return round(100 * beaten / len(clean))


def _morningstar_block(sector, fy, quarter, sym):
    """Sector-peer percentile ranks + a fair-value estimate for one company.

    Returns None when there aren't at least three sector peers in the period —
    a rank against one or two names would be meaningless.
    """
    if not sector:
        return None

    rows = FinancialStatement.objects.filter(
        sector=sector, fiscal_year_ad=fy, quarter=quarter, fs_type="KS",
    ).values("ticker", "item_code", "amount")

    by_ticker = {}
    for r in rows:
        num = _ks_num(r["item_code"])
        if not num:
            continue
        amt = float(r["amount"]) if r["amount"] is not None else None
        by_ticker.setdefault(r["ticker"], {})[num] = amt
    if len(by_ticker) < 3 or sym not in by_ticker:
        return None

    derived = {t: _ms_derive(d) for t, d in by_ticker.items()}
    self_d = derived[sym]

    ranks = []
    for key, label, fmt, higher_better in MS_METRICS:
        value = self_d.get(key)
        if value is None:
            continue
        series = [d.get(key) for d in derived.values()]
        clean = [v for v in series if v is not None]
        ranks.append({
            "label": label,
            "fmt": fmt,
            "value": value,
            "percentile": _percentile(series, value, higher_better),
            "median": statistics.median(clean) if clean else None,
            "higher_better": higher_better,
        })

    # Fair value: the sector's median P/E applied to the company's own EPS.
    pes = [d["pe"] for d in derived.values() if d.get("pe")]
    eps = by_ticker[sym].get("509")
    price = by_ticker[sym].get("512")
    fair_value = None
    if pes and eps and eps > 0:
        sector_pe = statistics.median(pes)
        estimate = sector_pe * eps
        ratio = (price / estimate) if (price and estimate) else None
        if ratio is None:
            verdict = "—"
        elif ratio < 0.85:
            verdict = "Undervalued"
        elif ratio <= 1.15:
            verdict = "Fairly valued"
        else:
            verdict = "Overvalued"
        fair_value = {
            "estimate": estimate,
            "price": price,
            "ratio": ratio,
            "verdict": verdict,
            "sector_pe": sector_pe,
        }

    return {
        "sector": sector,
        "peer_count": len(by_ticker),
        "ranks": ranks,
        "fair_value": fair_value,
    }


def _fmt_for(unit: str) -> str:
    """Map a source ``unit`` string to a client formatter hint."""
    u = (unit or "").strip().lower()
    if u == "%":
        return "pct"
    if u.startswith("rs"):
        return "rs000"
    return "num"


def _fundamental_tickers():
    """Active companies that have fundamentals, with names — for the search box.

    Restricted to CompanyProfile.status == Active so the picker never offers
    delisted / suspended scrips (the API still serves any ticker typed in by
    hand). Tickers with fundamentals but no active profile are omitted.
    """
    fund_tickers = set(
        FinancialStatement.objects.order_by().values_list("ticker", flat=True).distinct()
    )
    active = CompanyProfile.objects.filter(
        status__iexact="Active", symbol__in=fund_tickers
    ).values_list("symbol", "security_name")
    return [{"symbol": s, "name": n or ""} for s, n in sorted(active)]


@require_GET
def fundamental_analysis_view(request, symbol=None):
    """Render the Fundamental Analysis desk shell.

    The symbol is only the initial ticker — the client validates it against the
    fundamentals feed and falls back to the first available one if unknown.
    """
    sym = (symbol or request.GET.get("symbol") or "").strip().upper()
    context = {
        "symbol": sym,
        "symbols": _fundamental_tickers(),
        "asset_version": _asset_version(),
    }
    return render(request, "core_analysis/fundamental_analysis.html", context)


def _statement_rows(qs):
    """Order a queryset of line items for tabular display.

    A row is flagged ``header`` when its name reads as a section total
    (all-uppercase in the source), so the client can emphasise it.
    """
    rows = []
    for r in qs.order_by("sorting_code", "item_code"):
        name = r.item_name or ""
        rows.append(
            {
                "code": r.item_code,
                "name": name,
                "amount": float(r.amount) if r.amount is not None else None,
                "unit": r.unit or "",
                "fmt": _fmt_for(r.unit),
                "header": name.isupper() and len(name) > 1,
            }
        )
    return rows


@require_GET
def fundamental_data_api(request):
    """JSON feed for one company's fundamentals.

    Query params:
      symbol  — ticker (required-ish; falls back to first available)
      fy      — fiscal year label, e.g. "2024/25" (defaults to latest)
      quarter — 1–4 (defaults to the latest available within fy)
    """
    sym = (request.GET.get("symbol") or "").strip().upper()

    base = FinancialStatement.objects.filter(ticker=sym) if sym else FinancialStatement.objects.none()
    if sym and not base.exists():
        return JsonResponse(
            {"ok": False, "error": f"No fundamentals available for {sym}."},
            status=404,
        )

    # Available periods, newest first. (Quarter 0 in the source means annual.)
    periods = list(
        base.order_by()
        .values("fiscal_year_ad", "quarter")
        .annotate(n=Count("id"))
        .order_by("-fiscal_year_ad", "-quarter")
    )
    period_list = [
        {"fy": p["fiscal_year_ad"], "quarter": p["quarter"]} for p in periods
    ]
    if not period_list:
        return JsonResponse({"ok": False, "error": "No data."}, status=404)

    # Resolve the requested period (default: most recent).
    req_fy = (request.GET.get("fy") or "").strip()
    req_q = request.GET.get("quarter")
    selected = None
    if req_fy:
        try:
            req_q_int = int(req_q) if req_q not in (None, "") else None
        except (TypeError, ValueError):
            req_q_int = None
        for p in period_list:
            if p["fy"] == req_fy and (req_q_int is None or p["quarter"] == req_q_int):
                selected = p
                break
    if selected is None:
        selected = period_list[0]

    period_qs = base.filter(
        fiscal_year_ad=selected["fy"], quarter=selected["quarter"]
    )

    statements = []
    rows_by_type = {}
    for code, label in STATEMENT_TYPES:
        rows = _statement_rows(period_qs.filter(fs_type=code))
        rows_by_type[code] = {r["code"]: r["amount"] for r in rows}
        statements.append({"type": code, "label": label, "rows": rows})

    # Index the selected period's KS rows by their numeric code (sector-agnostic).
    ks_rows = next((s["rows"] for s in statements if s["type"] == "KS"), [])
    ks_by_num = {}
    for r in ks_rows:
        num = _ks_num(r["code"])
        if num and num not in ks_by_num:
            ks_by_num[num] = r["amount"]
    headline = [
        {
            "label": label,
            "value": ks_by_num.get(num),
            "fmt": fmt,
        }
        for num, label, fmt in HEADLINE_METRICS
        if ks_by_num.get(num) is not None
    ]

    # Multi-year trend: annual (Q4) KS rows for the marquee metrics.
    annual_qs = base.filter(fs_type="KS", quarter=4).order_by("fiscal_year_ad")
    trend_index = {}
    for r in annual_qs.values("fiscal_year_ad", "item_code", "amount"):
        num = _ks_num(r["item_code"])
        if not num:
            continue
        amt = float(r["amount"]) if r["amount"] is not None else None
        trend_index.setdefault(r["fiscal_year_ad"], {})[num] = amt
    trend_years = sorted(trend_index.keys())
    trend = []
    for num, label, fmt in TREND_METRICS:
        points = [
            {"fy": fy, "value": trend_index[fy].get(num)}
            for fy in trend_years
            if trend_index[fy].get(num) is not None
        ]
        if points:
            trend.append({"label": label, "fmt": fmt, "points": points})

    profile = (
        CompanyProfile.objects.filter(symbol=sym)
        .values("symbol", "security_name", "sector_name")
        .first()
    )

    # Morningstar tab: rank against sector peers for the selected period. The
    # peer group is keyed on the source table's own sector label (not the
    # CompanyProfile one) so it matches the rows being compared.
    sector = period_qs.values_list("sector", flat=True).first()
    try:
        morningstar = _morningstar_block(sector, selected["fy"], selected["quarter"], sym)
    except Exception:  # pragma: no cover - defensive: never 500 the desk
        logger.exception("Morningstar peer block failed for %s", sym)
        morningstar = None

    return JsonResponse(
        {
            "ok": True,
            "symbol": sym,
            "profile": profile
            or {"symbol": sym, "security_name": "", "sector_name": ""},
            "selected": {"fy": selected["fy"], "quarter": selected["quarter"]},
            "periods": period_list,
            "headline": headline,
            "statements": statements,
            "trend": trend,
            "morningstar": morningstar,
        }
    )
