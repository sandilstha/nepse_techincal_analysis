"""
broker_views.py — page + JSON endpoints for the Dalal Street X broker dashboard
(rendered on the Floor sheet page). All heavy lifting lives in
``services.broker_analytics``; these views are thin, fail soft (never 500 the
page), and return JSON the frontend renders per tab.
"""
from __future__ import annotations

import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from core_analysis.services import broker_analytics as ba

logger = logging.getLogger(__name__)


def _asset_version():
    # Reuse the Market Insights cache-bust helper so all pages move together.
    from core_analysis.insights_views import _asset_version as v

    return v()


def floorsheet_view(request):
    """Render the broker analytics dashboard shell (Floor sheet page)."""
    return render(
        request,
        "core_analysis/floorsheet.html",
        {"asset_version": _asset_version(), "meta": ba.meta_cached()},
    )


def _window(request):
    """Extract the shared date-range selection (range + optional custom dates).

    Returns a kwargs dict (``range_key`` always; ``start`` / ``end`` only when a
    'custom' range supplies them) to splat into any analytics builder.
    """
    range_key = request.GET.get("range", "today")
    kw = {"range_key": range_key}
    if range_key == "custom":
        kw["start"] = request.GET.get("start_date") or request.GET.get("start")
        kw["end"] = request.GET.get("end_date") or request.GET.get("end")
    return kw


def _safe(builder, *args, **kwargs):
    try:
        data = builder(*args, **kwargs)
        data.setdefault("ok", True)
        return JsonResponse(data)
    except Exception:  # pragma: no cover - defensive
        logger.exception("Broker analytics endpoint failed: %s", builder.__name__)
        return JsonResponse(
            {"ok": False, "error": "Unable to load broker data right now."}, status=500
        )


@require_GET
def broker_meta_api(request):
    return _safe(ba.meta)


@require_GET
def broker_favorites_api(request):
    # Accept "brokers=1,2,3" (multi-select) and fall back to single "broker".
    raw = request.GET.get("brokers") or request.GET.get("broker") or ""
    brokers = [b for b in (s.strip() for s in raw.split(",")) if b]
    return _safe(
        ba.broker_favorites,
        brokers,
        view=request.GET.get("view", "shares"),
        **_window(request),
    )


@require_GET
def broker_persistence_api(request):
    # Same broker multi-select contract as favorites. Persistence is inherently a
    # multi-session lens, so it owns its own lookback (default 1 month, floored at
    # 1 week) rather than collapsing to one day when the tab is on "Current Day".
    raw = request.GET.get("brokers") or request.GET.get("broker") or ""
    brokers = [b for b in (s.strip() for s in raw.split(",")) if b]
    rk = request.GET.get("lookback", "1m")
    rk = rk if rk in ("1w", "1m", "3m") else "1m"
    return _safe(
        ba.broker_persistence,
        brokers,
        range_key=rk,
        sector=request.GET.get("sector", "All"),
        exclude_mf=request.GET.get("exclude_mf") in ("1", "true", "yes"),
    )


@require_GET
def broker_signals_api(request):
    # Bundles the four research-desk signals (divergence / breadth / two-sided /
    # sector rotation). Uses the shared date-window contract like the other desks
    # (range preset or custom start/end).
    raw = request.GET.get("brokers") or request.GET.get("broker") or ""
    brokers = [b for b in (s.strip() for s in raw.split(",")) if b]
    return _safe(
        ba.broker_signals,
        brokers,
        sector=request.GET.get("sector", "All"),
        exclude_mf=request.GET.get("exclude_mf") in ("1", "true", "yes"),
        **_window(request),
    )


@require_GET
def stock_wise_api(request):
    return _safe(
        ba.stock_wise,
        request.GET.get("symbol"),
        view=request.GET.get("view", "shares"),
        **_window(request),
    )


@require_GET
def net_holding_api(request):
    # Accept "brokers=1,2,3" (multi-select) and fall back to single "broker".
    raw = request.GET.get("brokers") or request.GET.get("broker") or ""
    brokers = [b for b in (s.strip() for s in raw.split(",")) if b]
    return _safe(
        ba.net_holding,
        brokers,
        exclude_mf=request.GET.get("exclude_mf") in ("1", "true", "yes"),
        sector=request.GET.get("sector", "All"),
        **_window(request),
    )


@require_GET
def broker_concentration_api(request):
    return _safe(
        ba.broker_concentration,
        sector=request.GET.get("sector", "All"),
        **_window(request),
    )


@require_GET
def hotstocks_api(request):
    return _safe(
        ba.hotstocks,
        view=request.GET.get("view", "shares"),
        sector=request.GET.get("sector", "All"),
        **_window(request),
    )


@require_GET
def broker_trend_api(request):
    return _safe(
        ba.trend,
        request.GET.get("symbol"),
        request.GET.get("side", "buy"),
        broker=request.GET.get("broker"),
    )
