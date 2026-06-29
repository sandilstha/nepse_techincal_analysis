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

from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from core_analysis.models import CompanyProfile, FinancialStatement
from core_analysis.insights_views import _asset_version

logger = logging.getLogger(__name__)

# Statement types present in the source table, in display order, with labels.
STATEMENT_TYPES = (
    ("KS", "Key Statistics"),
    ("IS", "Income Statement"),
    ("BS", "Balance Sheet"),
)

# Headline ratio cards, by KS item_code, in display order. fmt drives the
# client formatter: pct (fraction → %), rs000 (thousands of Rs), num (plain).
HEADLINE_METRICS = (
    ("cb_ks_512_market_value_per_share", "Market Price", "num"),
    ("cb_ks_509_eps_annualized", "EPS (Annualized)", "num"),
    ("cb_ks_510_reported_pe_annualized", "P/E (Annualized)", "num"),
    ("cb_ks_511_book_value_per_share", "Book Value / Share", "num"),
    ("cb_ks_508_return_on_equity_ttm", "ROE (TTM)", "pct"),
    ("cb_ks_507_return_on_asset_ttm", "ROA (TTM)", "pct"),
    ("cb_ks_513_dividend_per_share_rs", "Dividend / Share", "num"),
    ("cb_ks_505_net_income_rs_000", "Net Income", "rs000"),
    ("cb_ks_501_total_revenue_rs_000", "Total Revenue", "rs000"),
    ("cb_ks_504_margin_mrq_percent", "Gross Margin (MRQ)", "pct"),
)

# Marquee metrics charted across fiscal years (annual = Q4 rows).
TREND_METRICS = (
    ("cb_ks_501_total_revenue_rs_000", "Total Revenue", "rs000"),
    ("cb_ks_505_net_income_rs_000", "Net Income", "rs000"),
    ("cb_ks_509_eps_annualized", "EPS", "num"),
    ("cb_ks_508_return_on_equity_ttm", "ROE", "pct"),
)


def _fmt_for(unit: str) -> str:
    """Map a source ``unit`` string to a client formatter hint."""
    u = (unit or "").strip().lower()
    if u == "%":
        return "pct"
    if u.startswith("rs"):
        return "rs000"
    return "num"


def _fundamental_tickers():
    """Distinct tickers that actually have fundamentals, with company names."""
    tickers = list(
        FinancialStatement.objects.order_by()
        .values_list("ticker", flat=True)
        .distinct()
    )
    names = dict(
        CompanyProfile.objects.filter(symbol__in=tickers).values_list(
            "symbol", "security_name"
        )
    )
    return [
        {"symbol": t, "name": names.get(t, "")}
        for t in sorted(tickers)
    ]


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

    ks_amounts = rows_by_type.get("KS", {})
    headline = [
        {
            "label": label,
            "value": ks_amounts.get(item_code),
            "fmt": fmt,
        }
        for item_code, label, fmt in HEADLINE_METRICS
        if ks_amounts.get(item_code) is not None
    ]

    # Multi-year trend: annual (Q4) KS rows for the marquee metrics.
    annual_qs = base.filter(fs_type="KS", quarter=4).order_by("fiscal_year_ad")
    trend_index = {}
    for r in annual_qs.values("fiscal_year_ad", "item_code", "amount"):
        trend_index.setdefault(r["fiscal_year_ad"], {})[r["item_code"]] = (
            float(r["amount"]) if r["amount"] is not None else None
        )
    trend_years = sorted(trend_index.keys())
    trend = []
    for item_code, label, fmt in TREND_METRICS:
        points = [
            {"fy": fy, "value": trend_index[fy].get(item_code)}
            for fy in trend_years
            if trend_index[fy].get(item_code) is not None
        ]
        if points:
            trend.append({"label": label, "fmt": fmt, "points": points})

    profile = (
        CompanyProfile.objects.filter(symbol=sym)
        .values("symbol", "security_name", "sector_name")
        .first()
    )

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
        }
    )
