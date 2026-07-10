"""
broker_views.py — page + JSON endpoints for the Dalal Street X broker dashboard
(rendered on the Floor sheet page). All heavy lifting lives in
``services.broker_analytics``; these views are thin, fail soft (never 500 the
page), and return JSON the frontend renders per tab.
"""
from __future__ import annotations

import logging
import re
from datetime import date
from functools import wraps

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from core_analysis.services import broker_analytics as ba

logger = logging.getLogger(__name__)

MAX_SELECTED_BROKERS = 200
_SYMBOL_RE = re.compile(r"^[A-Z0-9._-]{1,50}$")


class QueryValidationError(ValueError):
    """A malformed dashboard query that should produce a clean HTTP 400."""


def _validated_query(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except QueryValidationError as exc:
            return JsonResponse({"ok": False, "error": str(exc)}, status=400)

    return wrapped


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


def floorsheet_sop_view(request):
    """Methodology SOP for the Floorsheet (Dalal Street X) broker desk.

    One anchored section per tab / metric; the whole-page (?) icon in the tab bar
    deep-links here. Static content — every formula, data source and assumption is
    documented in the template itself, so it never touches the analytics engine.
    """
    return render(
        request,
        "core_analysis/floorsheet_sop.html",
        {"asset_version": _asset_version()},
    )


def _window(request):
    """Extract the shared date-range selection (range + optional custom dates).

    Returns a kwargs dict (``range_key`` always; ``start`` / ``end`` only when a
    'custom' range supplies them) to splat into any analytics builder.
    """
    range_key = (request.GET.get("range") or "today").strip().lower()
    if range_key not in ba.NAMED_RANGES | {"custom"}:
        raise QueryValidationError("Unknown date range.")
    kw = {"range_key": range_key}
    if range_key == "custom":
        start_raw = request.GET.get("start_date") or request.GET.get("start")
        end_raw = request.GET.get("end_date") or request.GET.get("end")
        try:
            start_date = date.fromisoformat((start_raw or "").strip())
            end_date = date.fromisoformat((end_raw or "").strip())
        except ValueError:
            raise QueryValidationError("Custom dates must use YYYY-MM-DD format.")
        if start_date > end_date:
            raise QueryValidationError("Custom start date must not be after the end date.")
        if (end_date - start_date).days + 1 > ba.CUSTOM_RANGE_MAX_DAYS:
            raise QueryValidationError(
                f"Custom date range cannot exceed {ba.CUSTOM_RANGE_MAX_DAYS} days."
            )
        kw["start"] = start_date.isoformat()
        kw["end"] = end_date.isoformat()
    return kw


def _brokers(request):
    raw = request.GET.get("brokers") or request.GET.get("broker") or ""
    parts = [part.strip() for part in raw.split(",") if part.strip()]
    if len(parts) > MAX_SELECTED_BROKERS:
        raise QueryValidationError(
            f"Select no more than {MAX_SELECTED_BROKERS} brokers."
        )
    brokers, seen = [], set()
    for part in parts:
        if len(part) > 6 or not part.isascii() or not part.isdecimal():
            raise QueryValidationError("Broker numbers must be positive integers.")
        broker = int(part)
        if broker <= 0:
            raise QueryValidationError("Broker numbers must be positive integers.")
        if broker not in seen:
            seen.add(broker)
            brokers.append(broker)
    return brokers


def _view_mode(request):
    value = (request.GET.get("view") or "shares").strip().lower()
    if value not in {"shares", "turnover"}:
        raise QueryValidationError("View must be either 'shares' or 'turnover'.")
    return value


def _sector(request):
    value = (request.GET.get("sector") or "All").strip() or "All"
    if len(value) > 100:
        raise QueryValidationError("Sector is too long.")
    return value


def _symbol(request):
    value = (request.GET.get("symbol") or "").strip().upper()
    if not value or not _SYMBOL_RE.fullmatch(value):
        raise QueryValidationError("Symbol must be 1-50 valid ticker characters.")
    return value


def _boolean(request, name):
    value = (request.GET.get(name) or "0").strip().lower()
    if value in {"1", "true", "yes"}:
        return True
    if value in {"0", "false", "no", ""}:
        return False
    raise QueryValidationError(f"{name} must be true or false.")


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
@_validated_query
def broker_favorites_api(request):
    return _safe(
        ba.broker_favorites,
        _brokers(request),
        view=_view_mode(request),
        **_window(request),
    )


@require_GET
@_validated_query
def broker_persistence_api(request):
    # Same broker multi-select contract as favorites. Persistence is inherently a
    # multi-session lens, so it owns its own lookback (default 1 month, floored at
    # 1 week) rather than collapsing to one day when the tab is on "Current Day".
    rk = (request.GET.get("lookback") or "1m").strip().lower()
    if rk not in {"1w", "1m", "3m"}:
        raise QueryValidationError("Lookback must be 1w, 1m or 3m.")
    return _safe(
        ba.broker_persistence,
        _brokers(request),
        range_key=rk,
        sector=_sector(request),
        exclude_mf=_boolean(request, "exclude_mf"),
    )


@require_GET
@_validated_query
def broker_signals_api(request):
    # Bundles the four research-desk signals (divergence / breadth / two-sided /
    # sector rotation). Uses the shared date-window contract like the other desks
    # (range preset or custom start/end).
    return _safe(
        ba.broker_signals,
        _brokers(request),
        sector=_sector(request),
        exclude_mf=_boolean(request, "exclude_mf"),
        **_window(request),
    )


@require_GET
@_validated_query
def stock_wise_api(request):
    return _safe(
        ba.stock_wise,
        _symbol(request),
        view=_view_mode(request),
        **_window(request),
    )


@require_GET
@_validated_query
def net_holding_api(request):
    return _safe(
        ba.net_holding,
        _brokers(request),
        exclude_mf=_boolean(request, "exclude_mf"),
        sector=_sector(request),
        **_window(request),
    )


@require_GET
@_validated_query
def broker_concentration_api(request):
    return _safe(
        ba.broker_concentration,
        sector=_sector(request),
        **_window(request),
    )


@require_GET
@_validated_query
def hotstocks_api(request):
    return _safe(
        ba.hotstocks,
        view=_view_mode(request),
        sector=_sector(request),
        **_window(request),
    )


@require_GET
@_validated_query
def broker_flow_radar_api(request):
    return _safe(ba.broker_flow_radar, **_window(request))
