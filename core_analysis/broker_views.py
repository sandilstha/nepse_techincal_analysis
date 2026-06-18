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
        request.GET.get("range", "today"),
        request.GET.get("view", "shares"),
    )


@require_GET
def stock_wise_api(request):
    return _safe(
        ba.stock_wise,
        request.GET.get("symbol"),
        request.GET.get("range", "today"),
        request.GET.get("view", "shares"),
    )


@require_GET
def net_holding_api(request):
    return _safe(
        ba.net_holding,
        request.GET.get("broker"),
        request.GET.get("range", "today"),
        request.GET.get("exclude_mf") in ("1", "true", "yes"),
        request.GET.get("sector", "All"),
    )


@require_GET
def broker_concentration_api(request):
    return _safe(
        ba.broker_concentration,
        request.GET.get("range", "today"),
        request.GET.get("sector", "All"),
    )


@require_GET
def hotstocks_api(request):
    return _safe(
        ba.hotstocks,
        request.GET.get("range", "today"),
        request.GET.get("view", "shares"),
        request.GET.get("sector", "All"),
    )


@require_GET
def broker_trend_api(request):
    return _safe(
        ba.trend,
        request.GET.get("symbol"),
        request.GET.get("side", "buy"),
    )
