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
    """Render the dashboard shell with the initial payload embedded as JSON."""
    try:
        payload = build_payload()
        error = None if payload.get("has_data") else "No market data has been synced yet."
    except Exception:  # pragma: no cover - defensive
        logger.exception("Market Insights initial build failed")
        payload = _empty_payload("Unable to load market data right now.")
        error = "Unable to load market data right now."

    context = {
        # json_script safely escapes </script>, <, >, & — never use |safe with
        # raw json.dumps here, that allows a stock name to break out of the tag.
        "bootstrap_payload": payload,
        "refresh_seconds": _refresh_seconds(),
        "load_error": error,
        "asset_version": _asset_version(),
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
