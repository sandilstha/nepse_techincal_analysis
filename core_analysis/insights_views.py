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

import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from core_analysis.services.market_insights import build_payload

DEFAULT_REFRESH_SECONDS = 30


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
    except Exception as exc:  # pragma: no cover - defensive
        payload = _empty_payload(str(exc))
        error = "Unable to load market data right now."

    context = {
        "bootstrap_json": json.dumps(payload),
        "refresh_seconds": _refresh_seconds(),
        "load_error": error,
    }
    return render(request, "core_analysis/market_insights.html", context)


@require_GET
def market_insights_api(request):
    """JSON snapshot used by the front-end auto-refresh poller."""
    try:
        force = request.GET.get("force") == "1"
        payload = build_payload(force=force)
        payload["ok"] = True
        return JsonResponse(payload)
    except Exception as exc:  # pragma: no cover - defensive
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)
