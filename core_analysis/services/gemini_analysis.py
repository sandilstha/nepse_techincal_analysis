"""
gemini_analysis.py — Gemini-powered narrative for the Support & Resistance tab.
==============================================================================

The workbench already computes a rich, *previous-data-derived* picture of a
symbol: confluence S/R zones, pivot averages, fractal swings, the nine-framework
institutional read, and the advanced SMC / volume-profile layer. The static
"Institutional Multi-Framework Analysis" table renders those numbers but its
prose is templated, so it reads the same for every symbol.

This module feeds the *computed facts* (not raw prose) to Gemini and asks for a
fresh, symbol-specific narrative that ties the levels to the recent price path.
The model never invents levels — it only interprets the numbers we pass it.

Disabled gracefully: with no GEMINI_API_KEY the public entry point returns an
``{"error": ...}`` dict and the UI shows a quiet "configure a key" note.
"""

from __future__ import annotations

import html
import json
import re
from typing import Any

import requests
from django.conf import settings

_GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
_OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


# ---------------------------------------------------------------------------
# Payload assembly — distil the computed metrics into a compact, factual brief
# ---------------------------------------------------------------------------

def _ladder(rows: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    out = []
    for row in (rows or [])[:5]:
        out.append({
            "label": row.get("label"),
            "price": row.get("price"),
            "zone": [row.get("low"), row.get("high")],
            "distance_pct": row.get("pct_distance"),
            "methods_agreeing": row.get("method_count"),
            "methods": row.get("methods"),
        })
    return out


def _institutional(rows: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    out = []
    for row in (rows or []):
        if row.get("alert") and not row.get("system"):
            continue
        out.append({
            "system": row.get("system"),
            "bias": row.get("signal") or "Neutral",
            "confidence_pct": row.get("confidence"),
            "status": row.get("status"),
            "logic": row.get("institutional_logic"),
            "price_read": row.get("price_sentiment"),
        })
    return out


def _advanced(adv: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(adv, dict) or adv.get("error"):
        return {}
    profile = adv.get("profile") or {}
    baselines = adv.get("baselines") or {}
    zones = []
    for z in (adv.get("density_zones") or [])[:6]:
        zones.append({
            "type": z.get("type"),
            "zone": [z.get("low"), z.get("high")],
            "strength": z.get("strength"),
            "touches": z.get("touches"),
            "prediction": z.get("prediction"),
            "hold_probability_pct": z.get("hold_probability"),
        })
    sweeps = []
    for s in (adv.get("structure_liquidity_rows") or [])[:6]:
        sweeps.append({
            "date": s.get("date"),
            "signal": s.get("signal"),
            "level": s.get("level"),
            "close": s.get("close"),
        })
    return {
        "volume_profile": {"poc": profile.get("poc"), "vah": profile.get("vah"), "val": profile.get("val")},
        "baselines": {
            "vwap": baselines.get("latest_vwap"),
            "hma": baselines.get("latest_hma"),
            "premium_discount": baselines.get("premium_discount"),
        },
        "density_zones": zones,
        "structure_breaks_and_sweeps": sweeps,
    }


def build_sr_brief(metrics: dict[str, Any], institutional_rows, advanced_metrics, recent_bars) -> dict[str, Any]:
    """Distil the tab's computed state into a compact JSON brief for the model."""
    m = metrics or {}
    nearest_res = m.get("nearest_resistance") or {}
    nearest_sup = m.get("nearest_support") or {}
    boll = m.get("bollinger_bands") or {}
    return {
        "symbol": m.get("symbol"),
        "as_of": m.get("latest_data_date"),
        "rows_analyzed": m.get("rows_used"),
        "latest_price": m.get("latest_price"),
        "previous_close": m.get("previous_close"),
        "latest_day_range": [m.get("latest_low"), m.get("latest_high")],
        "trend_bias": m.get("trend_bias"),
        "momentum": {"rsi": m.get("latest_rsi"), "stochastic_k": m.get("latest_stochastic_k"), "percent_b": boll.get("percent_b")},
        "nearest_resistance": {"price": nearest_res.get("price"), "distance_pct": m.get("resistance_distance_pct")},
        "nearest_support": {"price": nearest_sup.get("price"), "distance_pct": m.get("support_distance_pct")},
        "risk_reward_ratio": m.get("risk_reward_ratio"),
        "trading_inside_zone": m.get("price_zone"),
        "latest_swing_high": m.get("latest_swing_high"),
        "latest_swing_low": m.get("latest_swing_low"),
        "confluence_resistances": _ladder(m.get("confluence_resistances")),
        "confluence_supports": _ladder(m.get("confluence_supports")),
        "pivot_average": (m.get("pivot_average") or {}).get("average"),
        "institutional_frameworks": _institutional(institutional_rows),
        "advanced_market_structure": _advanced(advanced_metrics),
        "recent_price_path": recent_bars or [],
    }


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are a senior buy-side technical strategist writing a desk note for the \
Nepal Stock Exchange (NEPSE). You are given a JSON brief of PRE-COMPUTED support/resistance \
analytics for one symbol — confluence zones, pivot averages, fractal swings, a nine-framework \
institutional read, an advanced SMC / volume-profile layer, and the recent daily price path.

Write a concise, SYMBOL-SPECIFIC narrative that interprets THIS data. Rules:
- Ground every claim in the numbers provided. Never invent price levels, dates, or indicators — \
only reference values present in the brief. Prices are in NPR.
- Read the RECENT PRICE PATH: describe how price has actually behaved into the current levels \
(approaching/rejecting/breaking, building or losing momentum) instead of generic definitions.
- Reconcile the institutional frameworks: say where they AGREE and where they CONFLICT, and what \
the confidence-weighted consensus implies. Do not just restate each row.
- Be decisive and non-repetitive. No boilerplate, no disclaimers, no "as an AI". Vary sentence \
structure; do not reuse the same opening for each section.
- If data is missing (null/N/A), say so briefly rather than guessing.

Return GitHub-flavored markdown with EXACTLY these sections (use ## headings):
## Read of the Tape
2-4 sentences on the recent price path and current location vs the key zones.
## Key Levels in Play
A short markdown bullet list of the most actionable support and resistance zones (price + why it matters: confluence count / volume / swing).
## Framework Consensus
2-4 sentences reconciling the institutional frameworks and the net bias with its confidence.
## Scenarios
Two bullets — a bullish trigger and a bearish trigger — each naming the specific level that would confirm it and the next target/invalidation level.

Keep the whole note under ~320 words."""


def _build_user_text(brief: dict[str, Any]) -> str:
    return (
        "Here is the computed analytics brief (JSON). Write the desk note per your instructions.\n\n"
        + json.dumps(brief, default=str, indent=2)
    )


# ---------------------------------------------------------------------------
# Minimal, safe markdown → HTML (headings, bold, bullet lists, paragraphs)
# ---------------------------------------------------------------------------

def _inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", escaped)
    return escaped


def markdown_lite_to_html(text: str) -> str:
    """Convert the model's constrained markdown to a small, safe HTML subset.

    Input is escaped first, so model output cannot inject markup. Supports
    ## / ### headings, - or * bullet lists, **bold**/*italic*, and paragraphs.
    """
    lines = (text or "").replace("\r\n", "\n").split("\n")
    out: list[str] = []
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            close_list()
            continue
        heading = re.match(r"^(#{2,4})\s+(.*)$", line)
        bullet = re.match(r"^\s*[-*]\s+(.*)$", line)
        if heading:
            close_list()
            level = min(len(heading.group(1)), 4)
            out.append(f'<h{level} class="sr-ai-h">{_inline(heading.group(2).strip())}</h{level}>')
        elif bullet:
            if not in_list:
                out.append('<ul class="sr-ai-list">')
                in_list = True
            out.append(f"<li>{_inline(bullet.group(1).strip())}</li>")
        else:
            close_list()
            out.append(f"<p>{_inline(line.strip())}</p>")
    close_list()
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Providers — each returns (text, error, model). text is None on failure;
# (None, None, model) means "not configured" so the orchestrator skips it
# silently rather than surfacing an error.
# ---------------------------------------------------------------------------

def _try_gemini(brief: dict[str, Any]) -> tuple[str | None, str | None, str]:
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    model = getattr(settings, "GEMINI_MODEL", "gemini-2.5-pro") or "gemini-2.5-pro"
    if not api_key:
        return None, None, model
    timeout = getattr(settings, "GEMINI_TIMEOUT_SECONDS", 45)
    payload = {
        "system_instruction": {"parts": [{"text": _SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": _build_user_text(brief)}]}],
        "generationConfig": {"temperature": 0.55, "topP": 0.9, "maxOutputTokens": 1400},
    }
    try:
        resp = requests.post(
            _GEMINI_ENDPOINT.format(model=model),
            params={"key": api_key}, json=payload, timeout=timeout,
        )
    except requests.exceptions.Timeout:
        return None, "request timed out", model
    except requests.exceptions.RequestException as exc:
        return None, f"could not reach API ({exc})", model

    if resp.status_code != 200:
        detail = ""
        try:
            detail = (resp.json().get("error") or {}).get("message", "")
        except ValueError:
            detail = resp.text[:200]
        return None, f"API error {resp.status_code}: {detail or 'unknown error'}", model

    try:
        data = resp.json()
        candidate = (data.get("candidates") or [{}])[0]
        parts = (candidate.get("content") or {}).get("parts") or []
        text = "".join(part.get("text", "") for part in parts).strip()
    except (ValueError, IndexError, AttributeError):
        return None, "unexpected response shape", model

    if not text:
        finish = (data.get("candidates") or [{}])[0].get("finishReason", "")
        return None, f"empty analysis{f' (finishReason: {finish})' if finish else ''}", model
    return text, None, model


def _try_openrouter(brief: dict[str, Any]) -> tuple[str | None, str | None, str]:
    api_key = getattr(settings, "OPENROUTER_API_KEY", "")
    model = getattr(settings, "OPENROUTER_MODEL", "") or "nvidia/llama-3.1-nemotron-70b-instruct:free"
    if not api_key:
        return None, None, model
    # Common mistake: pasting the MODEL slug (e.g. "nvidia/...") into the key
    # field. Real OpenRouter keys start with "sk-or-". Catch it with a clear
    # message instead of a confusing 401.
    if "/" in api_key or not api_key.startswith("sk-or-"):
        return None, (
            "OPENROUTER_API_KEY looks invalid — it should start with 'sk-or-' "
            "(get one at https://openrouter.ai/keys). The model slug belongs in OPENROUTER_MODEL."
        ), model
    timeout = getattr(settings, "GEMINI_TIMEOUT_SECONDS", 45)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # Optional OpenRouter attribution header (used for their dashboards).
        # Must be latin-1 encodable — keep it ASCII (no em-dash etc.).
        "X-Title": "NEPSE Analytics - S/R AI Narrative",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_text(brief)},
        ],
        "temperature": 0.55,
        "top_p": 0.9,
        "max_tokens": 1400,
    }
    try:
        resp = requests.post(_OPENROUTER_ENDPOINT, headers=headers, json=payload, timeout=timeout)
    except requests.exceptions.Timeout:
        return None, "request timed out", model
    except requests.exceptions.RequestException as exc:
        return None, f"could not reach API ({exc})", model

    if resp.status_code != 200:
        detail = ""
        try:
            detail = (resp.json().get("error") or {}).get("message", "")
        except ValueError:
            detail = resp.text[:200]
        return None, f"API error {resp.status_code}: {detail or 'unknown error'}", model

    try:
        data = resp.json()
        message = (data.get("choices") or [{}])[0].get("message") or {}
        text = (message.get("content") or "").strip()
    except (ValueError, IndexError, AttributeError):
        return None, "unexpected response shape", model

    if not text:
        return None, "empty analysis", model
    return text, None, model


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_sr_ai_analysis(metrics, institutional_rows, advanced_metrics, recent_bars) -> dict[str, Any]:
    """Generate the narrative, trying Gemini first then the OpenRouter fallback.

    Returns {"analysis_html", "model", "provider"} on success or {"error"} on
    failure. Never raises — every failure is reported as an ``error`` string so
    the view can return it as JSON and the panel can show it inline.
    """
    if not isinstance(metrics, dict) or metrics.get("error"):
        return {"error": "No support/resistance data available to analyze."}

    brief = build_sr_brief(metrics, institutional_rows, advanced_metrics, recent_bars)

    errors: list[str] = []
    for provider, runner in (("Gemini", _try_gemini), ("OpenRouter", _try_openrouter)):
        try:
            text, err, model = runner(brief)
        except Exception as exc:  # never let one provider 500 the endpoint
            errors.append(f"{provider}: {exc}")
            continue
        if text:
            return {"analysis_html": markdown_lite_to_html(text), "model": model, "provider": provider}
        if err:
            errors.append(f"{provider}: {err}")

    if errors:
        return {"error": "AI analysis failed. " + " · ".join(errors)}
    return {
        "error": "AI analysis is not configured. Set GEMINI_API_KEY (or OPENROUTER_API_KEY for the "
                 "fallback) in your .env to enable it."
    }
