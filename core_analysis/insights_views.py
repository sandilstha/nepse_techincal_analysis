"""
insights_views.py — view layer for the Market Insights dashboard.

Two endpoints:
  * market_insights_view  — renders the dashboard shell with the first payload
                            embedded (fast first paint, no initial fetch).
  * market_insights_api   — JSON endpoint the page polls to auto-refresh.

Both fail gracefully: a DB / service error never 500s the page — the shell
renders with an error banner and the poller surfaces a "stale data" state.
"""
from __future__ import annotations

import logging
import os

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from core_analysis.services.market_insights import build_payload

logger = logging.getLogger(__name__)

DEFAULT_REFRESH_SECONDS = 30

# A forced rebuild bypasses the payload cache and re-runs every DB query, so
# rate-limit it: at most one forced rebuild per this window across all clients,
# regardless of how often "?force=1" is hit (manual-refresh spam / scripted GETs).
FORCE_COOLDOWN_KEY = "market_insights_force_cooldown"
FORCE_COOLDOWN_SECONDS = 5

# Static assets fingerprinted for cache-busting: the page appends ?v=<version>
# to these so the browser fetches fresh copies whenever a file changes.
_ASSET_FILES = (
    "core_analysis/css/insights.css",
    "core_analysis/js/insights.js",
    "core_analysis/js/ohlc-chart.js",
    "core_analysis/js/tv-chart.js",
)


def _asset_version():
    """Latest mtime across the dashboard's static assets (cache-bust token)."""
    latest = 0
    for rel in _ASSET_FILES:
        path = finders.find(rel)
        try:
            if path:
                latest = max(latest, int(os.path.getmtime(path)))
        except OSError:
            pass
    return latest or 1


_TV_LIBRARY_REL = "core_analysis/charting_library/charting_library.standalone.js"
_tv_installed_cache = None


def _tv_library_installed():
    """True if the licensed TradingView Advanced Charts bundle is present.

    Result is memoised — the file only appears at deploy time (see
    TRADINGVIEW_SETUP.md), so there's no need to stat it on every request.
    """
    global _tv_installed_cache
    if _tv_installed_cache is None:
        _tv_installed_cache = bool(finders.find(_TV_LIBRARY_REL))
    return _tv_installed_cache


def _refresh_seconds():
    value = getattr(settings, "INSIGHTS_REFRESH_SECONDS", DEFAULT_REFRESH_SECONDS)
    try:
        return max(5, int(value))
    except (TypeError, ValueError):
        return DEFAULT_REFRESH_SECONDS


def _empty_payload(error):
    return {
        "as_of": None,
        "has_data": False,
        "overview": {},
        "breadth": {},
        "gainers": [],
        "losers": [],
        "most_active": [],
        "sectors": [],
        "heatmap": [],
        "history": [],
        "stock_count": 0,
        "error": error,
    }


@require_GET
def market_insights_view(request):
    """Render the dashboard shell instantly.

    The payload is embedded ONLY if it is already cached — the render path never
    blocks on the external NEPSE feeds. On a cold cache the shell ships with an
    empty payload and the browser fetches the live data from /insights/api/ on
    demand (insights.js triggers an immediate fetch when the embedded payload
    carries no data). This keeps time-to-first-byte independent of how slow or
    reachable the upstream feeds are.
    """
    try:
        payload = build_payload(cache_only=True)
    except Exception:  # pragma: no cover - defensive
        logger.exception("Market Insights cached read failed")
        payload = None

    if payload is None:
        # Nothing cached yet: render the shell, let the client fetch on demand.
        payload = _empty_payload(None)
        error = None
    else:
        error = None if payload.get("has_data") else "No market data has been synced yet."

    context = {
        # json_script safely escapes </script>, <, >, & — never use |safe with
        # raw json.dumps here, that allows a stock name to break out of the tag.
        "bootstrap_payload": payload,
        "refresh_seconds": _refresh_seconds(),
        "load_error": error,
        "asset_version": _asset_version(),
        # Only emit the TradingView loader when the licensed library is actually
        # installed — otherwise it fires two guaranteed 404s on every page load.
        "tv_enabled": _tv_library_installed(),
    }
    return render(request, "core_analysis/market_insights.html", context)


@require_GET
def floorsheet_view(request):
    """Placeholder Floor sheet page (feature pending a trade-level data source)."""
    return render(
        request,
        "core_analysis/floorsheet.html",
        {"asset_version": _asset_version()},
    )


@require_GET
def market_insights_api(request):
    """JSON snapshot used by the front-end auto-refresh poller."""
    try:
        force = request.GET.get("force") == "1"
        # Throttle forced rebuilds so "?force=1" can't be looped to bypass the
        # cache and hammer the DB; serve the cached payload once one fires.
        if force:
            if cache.get(FORCE_COOLDOWN_KEY):
                force = False
            else:
                cache.set(FORCE_COOLDOWN_KEY, 1, FORCE_COOLDOWN_SECONDS)
        payload = build_payload(force=force)
        payload["ok"] = True
        return JsonResponse(payload)
    except Exception:  # pragma: no cover - defensive
        logger.exception("Market Insights API build failed")
        return JsonResponse(
            {"ok": False, "error": "Unable to load market data right now."}, status=500
        )
