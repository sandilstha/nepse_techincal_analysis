"""
seasonal_returns.py — monthly seasonal-return model for NEPSE indices.

Answers "which calendar months are historically strong / weak for each index".
Built entirely from the local ``NepseMarketIndex`` end-of-day table (no external
call — this is the "our own DB" search the desk runs on):

  * month-end close  = the last close of each calendar month per index,
  * monthly return   = month-over-month % change of those closes,
  * seasonal average = the mean monthly return grouped by calendar month (Jan-Dec)
                       across every year on record.

The payload is fully display-ready (pre-formatted strings + colours) so the
template stays dumb, and it is cached because the underlying scan touches the
whole index history (tens of thousands of rows) and only changes once a day.
"""
from __future__ import annotations

import calendar
import logging

from django.core.cache import cache

from core_analysis.services.RGG_indices import RRG_EXCLUDED_INDICES

logger = logging.getLogger(__name__)

# Broad-market gauges that aren't sector indices (Sensitive / Float / Sensitive
# Float) — excluded from every index analytic. Reuses the RRG exclusion set so
# there is one source of truth across RRG, Seasonal and the sub-index comparison.
EXCLUDED_INDICES = set(RRG_EXCLUDED_INDICES)

CACHE_TTL = 1800  # 30 min — the EOD indices only change once per session.

# Display order: NEPSE headline first, then the broad-market gauges, then the
# sector sub-indices. Anything not listed is appended alphabetically.
_INDEX_ORDER = [
    "NEPSE INDEX",
    "BANKING SUBINDEX", "DEVELOPMENT BANK INDEX", "FINANCE INDEX",
    "HOTELS AND TOURISM INDEX", "HYDROPOWER INDEX", "INVESTMENT INDEX",
    "LIFE INSURANCE", "MANUFACTURING AND PROCESSING", "MICROFINANCE INDEX",
    "MUTUAL FUND", "NON LIFE INSURANCE", "OTHERS INDEX", "TRADING INDEX",
]

MONTH_NAMES = [calendar.month_name[m] for m in range(1, 13)]  # January…December

# Nepali (Bikram Sambat) month labels, keyed by Gregorian month number. Each
# Gregorian month is mapped to the BS month that BEGINS within it (Magh starts
# mid-Jan, Baishakh mid-Apr, …) — the usual NEPSE convention. Approximate, since
# BS months straddle two Gregorian months; the averages themselves stay Gregorian.
NEPALI_MONTHS = {
    1: "माघ", 2: "फागुन", 3: "चैत", 4: "बैशाख", 5: "जेठ", 6: "असार",
    7: "साउन", 8: "भदौ", 9: "असोज", 10: "कात्तिक", 11: "मंसिर", 12: "पुस",
}

# Nepali fiscal-year row order for the seasonality matrix: the FY starts on 1
# Shrawan (≈ mid-July) and ends in Ashadh (≈ mid-July next year). With our
# Gregorian→BS mapping (July = Shrawan), that is simply July→June — i.e. Shrawan,
# Bhadra, Ashwin, Kartik, Mangsir, Poush, Magh, Falgun, Chaitra, Baishakh,
# Jestha, Ashadh.
_FY_MONTH_ORDER = (7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6)

_POS = "#16a34a"   # green — positive return
_NEG = "#dc2626"   # red   — negative return
_MUTED = "#94a3b8"  # no data


def _label(name: str) -> str:
    """Human display label for an index code: title-case, but keep 'NEPSE'."""
    words = [("NEPSE" if w.upper() == "NEPSE" else w.capitalize()) for w in name.split()]
    return " ".join(words)


def _fmt(value):
    """Signed percent string, e.g. +2.60% / -4.20% / — for None."""
    if value is None:
        return "—"
    return f"{'+' if value >= 0 else '-'}{abs(value):.2f}%"


def _color(value):
    if value is None:
        return _MUTED
    return _POS if value >= 0 else _NEG


def _cell_bg(value, cap):
    """Diverging heat tint (green +, red −) scaled by |value| / cap."""
    if value is None or not cap:
        return "transparent"
    alpha = min(1.0, abs(value) / cap) * 0.30
    rgb = "22, 163, 74" if value >= 0 else "220, 38, 38"
    return f"rgba({rgb}, {alpha:.3f})"


def _ordered_indices(present):
    ordered = [name for name in _INDEX_ORDER if name in present]
    extras = sorted(name for name in present if name not in _INDEX_ORDER)
    return ordered + extras


def _compute():
    import pandas as pd

    from core_analysis.models import NepseMarketIndex

    rows = NepseMarketIndex.objects.values_list("sector_name", "business_date", "close_index")
    df = pd.DataFrame.from_records(list(rows), columns=["index", "date", "close"])
    if df.empty:
        return {"ok": False, "reason": "No index history available."}

    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    # The index name is stored in mixed case across 29 years of feed ("NEPSE Index"
    # vs "NEPSE INDEX"). MySQL's case-insensitive collation treats them as one, but
    # pandas would split them into separate series — so normalise to a single
    # upper-case key before grouping, matching _INDEX_ORDER.
    df["index"] = df["index"].astype(str).str.strip().str.upper()
    df = df.dropna(subset=["date", "close"])
    df = df[(df["index"] != "") & (df["close"] > 0)]
    # Drop the non-sector broad-market gauges (Sensitive / Float / Sensitive Float).
    df = df[~df["index"].isin(EXCLUDED_INDICES)]
    if df.empty:
        return {"ok": False, "reason": "No usable index closes."}

    rows_processed = int(len(df))
    coverage = f"{df['date'].min():%Y-%m-%d} to {df['date'].max():%Y-%m-%d}"
    # The month currently in progress (only a few sessions old) is a partial-month
    # return — kept for "Latest Monthly Return" but excluded from the seasonal
    # AVERAGE so a 1-day print doesn't skew that calendar month's history.
    current_period = df["date"].max().to_period("M")

    # Per index: month-end close → monthly return → seasonal (per-calendar-month) mean.
    avg_by_month, latest, best_worst = {}, {}, {}
    for idx, g in df.groupby("index"):
        g = g.sort_values("date")
        # Last close of each calendar month (period index keeps months ordered).
        monthly = g.groupby(g["date"].dt.to_period("M"))["close"].last()
        if len(monthly) < 2:
            continue
        ret = monthly.pct_change().dropna() * 100.0
        if ret.empty:
            continue

        buckets = {}
        for period, r in ret.items():
            if period == current_period:
                continue  # exclude the in-progress month from the seasonal mean
            buckets.setdefault(period.month, []).append(float(r))
        if not buckets:
            continue
        means = {m: sum(v) / len(v) for m, v in buckets.items()}
        avg_by_month[idx] = {m: round(v, 2) for m, v in means.items()}

        last_period = ret.index[-1]
        latest[idx] = {
            "period": f"{calendar.month_name[last_period.month]} {last_period.year}",
            "value": round(float(ret.iloc[-1]), 2),
        }
        best_m = max(means, key=means.get)
        worst_m = min(means, key=means.get)
        best_worst[idx] = {
            "best_month": calendar.month_name[best_m], "best_value": round(means[best_m], 2),
            "worst_month": calendar.month_name[worst_m], "worst_value": round(means[worst_m], 2),
        }

    present = list(avg_by_month.keys())
    if not present:
        return {"ok": False, "reason": "Not enough monthly history to build seasonality."}
    order = _ordered_indices(present)

    # Latest Monthly Return — one row per index, sorted best→worst.
    latest_rows = sorted(
        (
            {
                "label": _label(idx),
                "period": latest[idx]["period"],
                "value_str": _fmt(latest[idx]["value"]),
                "color": _color(latest[idx]["value"]),
                "value": latest[idx]["value"],
            }
            for idx in order
        ),
        key=lambda r: r["value"], reverse=True,
    )

    # Best / Worst month by index (average), sorted by the best-month strength.
    bestworst_rows = sorted(
        (
            {
                "label": _label(idx),
                "best_month": best_worst[idx]["best_month"],
                "best_str": _fmt(best_worst[idx]["best_value"]),
                "worst_month": best_worst[idx]["worst_month"],
                "worst_str": _fmt(best_worst[idx]["worst_value"]),
                "latest_str": _fmt(latest[idx]["value"]),
                "latest_color": _color(latest[idx]["value"]),
                "_best": best_worst[idx]["best_value"],
            }
            for idx in order
        ),
        key=lambda r: r["_best"], reverse=True,
    )

    # Average Return by Month × Index matrix (rows = months, cols = indices).
    cap = max(
        (abs(v) for m in avg_by_month.values() for v in m.values()),
        default=1.0,
    ) or 1.0
    columns = [{"key": idx, "label": idx} for idx in order]
    matrix_rows = []
    for m in _FY_MONTH_ORDER:   # Nepali fiscal-year order: Shrawan (Jul) → Ashadh (Jun)
        cells = []
        for idx in order:
            v = avg_by_month[idx].get(m)
            cells.append({"text": _fmt(v), "color": _color(v), "bg": _cell_bg(v, cap)})
        matrix_rows.append({
            "month": calendar.month_name[m],
            "month_np": NEPALI_MONTHS.get(m, ""),
            "cells": cells,
        })

    return {
        "ok": True,
        "coverage": coverage,
        "indices_count": len(present),
        "rows_processed": rows_processed,
        "rows_processed_str": f"{rows_processed:,}",
        "latest_rows": latest_rows,
        "bestworst_rows": bestworst_rows,
        "columns": columns,
        "matrix_rows": matrix_rows,
    }


def build_seasonal_payload():
    """Cached seasonal-return payload for the RRG → Seasonal desk."""
    from core_analysis.models import NepseMarketIndex

    latest = (
        NepseMarketIndex.objects.order_by("-business_date")
        .values_list("business_date", flat=True)
        .first()
    )
    ck = f"seasonal_returns_{latest}"
    cached = cache.get(ck)
    if cached is not None:
        return cached
    try:
        payload = _compute()
    except Exception:  # pragma: no cover - never let seasonality break the tab
        logger.exception("seasonal returns computation failed")
        payload = {"ok": False, "reason": "Seasonal engine error."}
    cache.set(ck, payload, CACHE_TTL)
    return payload
