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

from django.db.models import Count, Max
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from core_analysis.models import CompanyProfile, FinancialStatement, NepseDailyStockPrice
from core_analysis.insights_views import _asset_version

logger = logging.getLogger(__name__)

# Statement types present in the source table, in display order, with labels.
STATEMENT_TYPES = (
    ("BS", "Balance Sheet"),
    ("IS", "Income Statement"),
    ("KS", "Key Statistics"),
)

# IMPORTANT: KS item codes are NOT numbered consistently across sectors — e.g.
# bank 508 = ROE but microfinance 508 = EPS. The DESCRIPTIVE name is stable,
# so every metric lookup keys on this classifier, never the bare number.
def _ks_key(item_code):
    """Map a KS item_code to a canonical metric key by its descriptive name."""
    c = (item_code or "").lower()
    if "return_on_equity" in c:
        return "roe"
    if "return_on_asset" in c:
        return "roa"
    if "book_value_per_share" in c:
        return "bvps"
    if "market_value_per_share" in c:
        return "price"
    if "dividend_per_share" in c:
        return "dps"
    if "reported_pe" in c:
        return "pe"
    if "eps" in c:
        return "eps"
    if "total_revenue" in c:
        return "revenue"
    if "net_income" in c:
        return "net_income"
    if "non_performing" in c or "npl_to_total" in c:
        return "npl"
    if "capital_fund_to_rwa" in c:
        return "car"
    if "margin_mrq" in c:
        return "gross_margin"
    if "outstanding_shares" in c:
        return "shares"
    return None


# Headline ratio cards, by canonical metric key, in display order. fmt drives
# the client formatter: pct (fraction → %), rs000 (thousands of Rs), num (plain).
HEADLINE_METRICS = (
    ("price", "Market Price", "num"),
    ("eps", "EPS (Annualized)", "num"),
    ("pe", "P/E (Annualized)", "num"),
    ("bvps", "Book Value / Share", "num"),
    ("roe", "ROE (TTM)", "pct"),
    ("roa", "ROA (TTM)", "pct"),
    ("dps", "Dividend / Share", "num"),
    ("net_income", "Net Income", "rs000"),
    ("revenue", "Total Revenue", "rs000"),
    ("gross_margin", "Gross Margin (MRQ)", "pct"),
)

# Marquee metrics charted across fiscal years (annual = Q4 rows).
TREND_METRICS = (
    ("revenue", "Total Revenue", "rs000"),
    ("net_income", "Net Income", "rs000"),
    ("eps", "EPS", "num"),
    ("roe", "ROE", "pct"),
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

    # Index the selected period's KS rows by canonical metric key (name-based,
    # so it's correct for every sector's distinct numbering).
    ks_rows = next((s["rows"] for s in statements if s["type"] == "KS"), [])
    ks_by_key = {}
    for r in ks_rows:
        key = _ks_key(r["code"])
        if key and key not in ks_by_key:
            ks_by_key[key] = r["amount"]
    headline = [
        {
            "label": label,
            "value": ks_by_key.get(key),
            "fmt": fmt,
        }
        for key, label, fmt in HEADLINE_METRICS
        if ks_by_key.get(key) is not None
    ]

    # Multi-year trend: annual (Q4) KS rows for the marquee metrics.
    annual_qs = base.filter(fs_type="KS", quarter=4).order_by("fiscal_year_ad")
    trend_index = {}
    for r in annual_qs.values("fiscal_year_ad", "item_code", "amount"):
        key = _ks_key(r["item_code"])
        if not key:
            continue
        amt = float(r["amount"]) if r["amount"] is not None else None
        trend_index.setdefault(r["fiscal_year_ad"], {})[key] = amt
    trend_years = sorted(trend_index.keys())
    trend = []
    for key, label, fmt in TREND_METRICS:
        points = [
            {"fy": fy, "value": trend_index[fy].get(key)}
            for fy in trend_years
            if trend_index[fy].get(key) is not None
        ]
        if points:
            trend.append({"label": label, "fmt": fmt, "points": points})

    # BFI dividend-sustainability inputs. Only emitted when the selected period's
    # Income Statement carries a Distributable Profit line — i.e. the banks,
    # finance and insurance sectors whose IS runs the NRB/Beema-mandated
    # distributable-profit waterfall. The item_code prefix is sector-specific
    # (cb_/db_/fi_/inv_/li_/nli_…) but always ends in "_distributable_profit",
    # so a suffix match covers every BFI sub-sector with one branch. The client
    # turns these into DPS-coverage and reserve-haircut grades.
    is_rows = rows_by_type.get("IS", {})
    distributable = next(
        (amt for code, amt in is_rows.items() if code.endswith("_distributable_profit")),
        None,
    )
    bfi = None
    if distributable is not None:
        reg_reserve = next(
            (amt for code, amt in is_rows.items() if "transferred_to_regulatory_reserve" in code),
            None,
        )
        bfi = {
            "distributable_profit": distributable,        # Rs '000
            "regulatory_reserve_transfer": reg_reserve,   # Rs '000 (negative = moved into reserve)
            "net_income": ks_by_key.get("net_income"),    # Rs '000
            "dps": ks_by_key.get("dps"),                  # Rs / share
            "shares": ks_by_key.get("shares"),            # '000 shares
            "eps": ks_by_key.get("eps"),                  # Rs / share
        }

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
            "bfi": bfi,
        }
    )


@require_GET
def fundamental_matrix_api(request):
    """Multi-period statement matrix: one line item per row, one fiscal period
    per column (newest first) — the spreadsheet-style "Company Financials" view.

    Query params:
      symbol       — ticker (required)
      statement    — BS | IS | KS (default BS)
      data_version — source label (default: the company's only / first source)
      periods      — number of period columns to return (default 12)
    """
    sym = (request.GET.get("symbol") or "").strip().upper()
    fs_type = (request.GET.get("statement") or "BS").strip().upper()
    if fs_type not in {"BS", "IS", "KS"}:
        fs_type = "BS"
    try:
        limit = int(request.GET.get("periods") or 12)
    except (TypeError, ValueError):
        limit = 12
    limit = max(4, min(40, limit))

    base = FinancialStatement.objects.filter(ticker=sym, fs_type=fs_type)
    if not sym or not base.exists():
        return JsonResponse(
            {"ok": False, "error": f"No {fs_type} data for {sym or '—'}."},
            status=404,
        )

    versions = list(
        FinancialStatement.objects.filter(ticker=sym)
        .order_by()
        .values_list("data_source", flat=True)
        .distinct()
    )
    data_version = (request.GET.get("data_version") or "").strip()
    if data_version not in versions:
        data_version = versions[0] if versions else ""
    if data_version:
        base = base.filter(data_source=data_version)

    raw = base.values(
        "fiscal_year_ad", "quarter", "item_code", "item_name", "sorting_code", "unit", "amount"
    )

    # Columns: newest fiscal periods first, capped at `limit`.
    periods = sorted(
        {(r["fiscal_year_ad"], r["quarter"]) for r in raw},
        key=lambda p: (p[0], p[1]),
        reverse=True,
    )[:limit]
    period_set = set(periods)
    columns = [{"key": f"{fy}|{q}", "fy": fy, "quarter": q} for fy, q in periods]

    # Rows: one entry per line item, ordered by the source's sorting_code.
    items = {}
    for r in raw:
        if (r["fiscal_year_ad"], r["quarter"]) not in period_set:
            continue
        code = r["item_code"]
        it = items.get(code)
        if it is None:
            name = r["item_name"] or ""
            it = {
                "code": code,
                "name": name,
                "unit": r["unit"] or "",
                "fmt": _fmt_for(r["unit"]),
                "header": name.isupper() and len(name) > 1,
                "_sort": r["sorting_code"] or "",
                "values": {},
            }
            items[code] = it
        it["values"][f"{r['fiscal_year_ad']}|{r['quarter']}"] = (
            float(r["amount"]) if r["amount"] is not None else None
        )

    rows = sorted(items.values(), key=lambda x: (x["_sort"], x["code"]))
    for r in rows:
        r.pop("_sort", None)

    return JsonResponse(
        {
            "ok": True,
            "symbol": sym,
            "statement": fs_type,
            "data_version": data_version,
            "data_versions": versions,
            "columns": columns,
            "rows": rows,
        }
    )


# ── Growth & Value scoring model (Morningstar-style), sector-wide ────────────
# All weights/thresholds live here so the model is tuned in one place (per the
# SOP). It is KS-only and keyed on canonical metric names (see _ks_key), so it
# works for every sector — bank-specific inputs (NPL, capital adequacy) are
# simply absent for non-financials and the weights renormalise over what's present.

# Growth Score: year-on-year growth of these canonical metrics → weight.
GV_GROWTH_WEIGHTS = (
    ("revenue", 0.25),
    ("net_income", 0.35),
    ("eps", 0.20),
    ("bvps", 0.20),
)

# Value Score sub-metrics: (key, weight, mode, a, b)
#   mode "inv" → inverse_score(value, best=a, worst=b)   [lower is better]
#   mode "dir" → direct_score(value_pct, best=a)          [higher is better, %]
GV_VALUE_SPECS = (
    ("pe",         0.22, "inv", 8, 25),
    ("pb",         0.22, "inv", 0.8, 3),
    ("div_yield",  0.15, "dir", 8, None),
    ("earn_yield", 0.15, "dir", 12, None),
    ("roe",        0.16, "dir", 18, None),
    ("roa",        0.10, "dir", 5, None),
    ("npl",        0.10, "inv", 1, 5),     # bank-only
    ("car",        0.05, "dir", 15, None), # bank-only
)
GV_STRONG = 50.0   # growth & value both ≥ this → score 3
GV_WATCH = 40.0    # growth or value ≥ this → score 2
GV_LARGE_CAP_SHARE = 0.55  # Large = top tickers up to 55% of cumulative market cap
GV_MID_CAP_SHARE = 0.85    # Mid = next 30% (cumulative 55%–85%); Small = last 15%
MILLION = 1_000_000.0


def _gv_clamp(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))


def _gv_norm_growth(frac):
    """25% YoY growth → 100; linear; clamped. ``frac`` is a fraction (0.12)."""
    if frac is None:
        return None
    return _gv_clamp(frac * 400.0)


def _gv_inv(v, best, worst):
    if v is None:
        return None
    if v <= best:
        return 100.0
    if v >= worst:
        return 0.0
    return _gv_clamp((worst - v) / (worst - best) * 100.0)


def _gv_dir(v_pct, best):
    if v_pct is None:
        return None
    return _gv_clamp(v_pct / best * 100.0)


def _gv_weighted(pairs):
    """Weighted mean of (score, weight), renormalised over present scores."""
    num = sum(s * w for s, w in pairs if s is not None)
    den = sum(w for s, w in pairs if s is not None)
    return (num / den) if den else None


def _prev_fy(fy):
    """'2025/26' → '2024/25' (one fiscal year earlier)."""
    parts = (fy or "").split("/")
    if len(parts) != 2:
        return None
    try:
        a, b = int(parts[0]), int(parts[1])
    except ValueError:
        return None
    return f"{a - 1}/{(b - 1) % 100:02d}"


def _gv_value_inputs(d):
    """Comparable value metrics for one ticker from its canonical key→amount
    dict. Percent-style metrics (stored as fractions) become whole percents."""
    price = d.get("price")
    bvps = d.get("bvps")
    eps = d.get("eps")
    dps = d.get("dps")
    return {
        "pe": d.get("pe") if (d.get("pe") and d.get("pe") > 0) else None,
        "pb": (price / bvps) if (price is not None and bvps and bvps > 0) else None,
        "div_yield": (dps / price * 100) if (dps is not None and price and price > 0) else None,
        "earn_yield": (eps / price * 100) if (eps is not None and price and price > 0) else None,
        "roe": (d.get("roe") * 100) if d.get("roe") is not None else None,
        "roa": (d.get("roa") * 100) if d.get("roa") is not None else None,
        "npl": (d.get("npl") * 100) if d.get("npl") is not None else None,
        "car": (d.get("car") * 100) if d.get("car") is not None else None,
    }


def _gv_growth_score(cur, prev):
    pairs = []
    for key, w in GV_GROWTH_WEIGHTS:
        c, p = cur.get(key), prev.get(key)
        g = (c / p - 1) if (c is not None and p is not None and p > 0) else None
        pairs.append((_gv_norm_growth(g), w))
    return _gv_weighted(pairs)


def _gv_value_score(d):
    vin = _gv_value_inputs(d)
    pairs = []
    for key, w, mode, a, b in GV_VALUE_SPECS:
        v = vin.get(key)
        s = _gv_inv(v, a, b) if mode == "inv" else _gv_dir(v, a)
        pairs.append((s, w))
    return _gv_weighted(pairs)


def _gv_final(g, v):
    if g is None or v is None:
        return None, "Insufficient data"
    if g >= GV_STRONG and v >= GV_STRONG:
        return 3, "Strong / Attractive"
    if g >= GV_WATCH or v >= GV_WATCH:
        return 2, "Average / Watchlist"
    return 1, "Weak / Avoid"


def _positive_float(value):
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None


def _latest_market_caps(symbols):
    """Latest EOD market capitalisation by symbol, converted to rupees."""
    symbols = [s for s in symbols if s]
    if not symbols:
        return {}
    latest = (
        NepseDailyStockPrice.objects.filter(symbol__in=symbols)
        .aggregate(latest=Max("business_date"))
        .get("latest")
    )
    if not latest:
        return {}
    rows = (
        NepseDailyStockPrice.objects.filter(symbol__in=symbols, business_date=latest)
        .values("symbol", "market_capitalization")
    )
    return {
        r["symbol"]: float(r["market_capitalization"]) * MILLION
        for r in rows
        if r["market_capitalization"] is not None
    }


def _gv_market_cap(d, latest_cap=None):
    """Period KS cap first, latest EOD cap second. Returns (cap, source)."""
    price = _positive_float(d.get("price"))
    shares = _positive_float(d.get("shares"))
    if price is not None and shares is not None:
        return price * shares, "period_ks"
    cap = _positive_float(latest_cap)
    if cap is not None:
        return cap, "latest_eod"
    return None, "missing"


def _gv_cap_segments(market_caps):
    """Large/Mid/Small by cumulative market-cap share, not equal-count buckets."""
    segments = {ticker: "Unclassified" for ticker in market_caps}
    ranked = sorted(
        ((ticker, cap) for ticker, cap in market_caps.items() if cap and cap > 0),
        key=lambda item: item[1],
        reverse=True,
    )
    total = sum(cap for _, cap in ranked)
    if not total:
        return segments

    cumulative = 0.0
    for ticker, cap in ranked:
        cumulative += cap
        share = cumulative / total  # cumulative share *including* this ticker
        if share <= GV_LARGE_CAP_SHARE:
            segments[ticker] = "Large"
        elif share <= GV_MID_CAP_SHARE:
            segments[ticker] = "Mid"
        else:
            segments[ticker] = "Small"
    return segments


# The source table carries per-sector aggregate rows (industry median /
# numeric average / weighted average) alongside real companies — their tickers
# end in one of these. They must never appear as a "company" in the model.
_AGGREGATE_TICKER_SUFFIXES = ("_MEDIAN", "_N_AVG", "_W_AVG")


def _is_aggregate_ticker(ticker):
    return bool(ticker) and ticker.upper().endswith(_AGGREGATE_TICKER_SUFFIXES)


def _sector_model(sector, fy, quarter):
    """Growth/Value scores for every company in a sector for one period."""
    prev = _prev_fy(fy)
    rows = FinancialStatement.objects.filter(
        sector=sector, fs_type="KS", quarter=quarter,
        fiscal_year_ad__in=[fy, prev],
    ).values("ticker", "fiscal_year_ad", "item_code", "amount")

    cur_by, prev_by = {}, {}
    for r in rows:
        if _is_aggregate_ticker(r["ticker"]):
            continue
        key = _ks_key(r["item_code"])
        if not key:
            continue
        amt = float(r["amount"]) if r["amount"] is not None else None
        bucket = cur_by if r["fiscal_year_ad"] == fy else prev_by
        bucket.setdefault(r["ticker"], {})[key] = amt

    names = dict(
        CompanyProfile.objects.filter(symbol__in=list(cur_by.keys()))
        .values_list("symbol", "security_name")
    )

    latest_caps = _latest_market_caps(cur_by.keys())
    cap_by_ticker, cap_source_by_ticker = {}, {}
    for t, d in cur_by.items():
        market_cap, source = _gv_market_cap(d, latest_caps.get(t))
        cap_by_ticker[t] = market_cap
        cap_source_by_ticker[t] = source
    segments = _gv_cap_segments(cap_by_ticker)

    results = []
    for t, d in cur_by.items():
        g = _gv_growth_score(d, prev_by.get(t, {}))
        v = _gv_value_score(d)
        score, decision = _gv_final(g, v)
        market_cap = cap_by_ticker.get(t)
        results.append({
            "ticker": t,
            "name": names.get(t, ""),
            "growth": round(g, 2) if g is not None else None,
            "value": round(v, 2) if v is not None else None,
            "score": score,
            "decision": decision,
            "segment": segments.get(t, "Unclassified"),
            "market_cap": round(market_cap, 2) if market_cap is not None else None,
            "market_cap_source": cap_source_by_ticker.get(t, "missing"),
        })

    results.sort(key=lambda r: (-(r["score"] or 0), -(r["growth"] or 0)))
    return results


@require_GET
def fundamental_model_api(request):
    """Sector-wide Growth & Value scoring model (latest period for the sector).

    Pick the sector directly with ?sector=… ; ?symbol=… is accepted as a
    fallback to default to that company's sector. Also returns the full list of
    sectors so the front-end can offer a sector picker.
    """
    sectors = sorted(
        s for s in FinancialStatement.objects.order_by()
        .values_list("sector", flat=True).distinct() if s
    )

    sector = (request.GET.get("sector") or "").strip()
    sym = (request.GET.get("symbol") or "").strip().upper()
    if sector not in sectors:
        if sym:
            sector = (
                FinancialStatement.objects.filter(ticker=sym)
                .values_list("sector", flat=True).first()
            )
        sector = sector if sector in sectors else (sectors[0] if sectors else None)

    if not sector:
        return JsonResponse({"ok": False, "error": "No sectors available."}, status=404)

    periods = sorted(
        {(fy, q) for fy, q in FinancialStatement.objects
            .filter(sector=sector, fs_type="KS")
            .values_list("fiscal_year_ad", "quarter")},
        reverse=True,
    )
    if not periods:
        return JsonResponse({"ok": False, "error": f"No data for {sector}."}, status=404)
    fy, quarter = periods[0]

    try:
        results = _sector_model(sector, fy, quarter)
    except Exception:  # pragma: no cover - defensive
        logger.exception("Growth/Value model failed for %s", sector)
        results = []

    summary = {
        "total": len(results),
        "strong": sum(1 for r in results if r["score"] == 3),
        "watch": sum(1 for r in results if r["score"] == 2),
        "weak": sum(1 for r in results if r["score"] == 1),
    }
    segment_summary = {
        "Large": sum(1 for r in results if r["segment"] == "Large"),
        "Mid": sum(1 for r in results if r["segment"] == "Mid"),
        "Small": sum(1 for r in results if r["segment"] == "Small"),
        "Unclassified": sum(1 for r in results if r["segment"] == "Unclassified"),
    }
    return JsonResponse({
        "ok": True,
        "symbol": sym,
        "sector": sector,
        "sectors": sectors,
        "selected": {"fy": fy, "quarter": quarter},
        "summary": summary,
        "segment_summary": segment_summary,
        "size_method": "market_cap_cumulative_55_30_15",
        "results": results,
    })
