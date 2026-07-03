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
import math

from django.core.cache import cache

from core_analysis.services.RGG_indices import RRG_EXCLUDED_INDICES

logger = logging.getLogger(__name__)

# Broad-market gauges that aren't sector indices (Sensitive / Float / Sensitive
# Float) — excluded from every index analytic. Reuses the RRG exclusion set so
# there is one source of truth across RRG, Seasonal and the sub-index comparison.
EXCLUDED_INDICES = set(RRG_EXCLUDED_INDICES)

CACHE_TTL = 1800  # 30 min — the EOD indices only change once per session.

# Display order: NEPSE headline first, then the sector sub-indices. Anything not
# listed is appended alphabetically.
_INDEX_ORDER = [
    "NEPSE INDEX",
    "BANKING SUBINDEX",
    "DEVELOPMENT BANK INDEX",
    "FINANCE INDEX",
    "MICROFINANCE INDEX",
    "HOTELS AND TOURISM INDEX",
    "HYDROPOWER INDEX",
    "LIFE INSURANCE",
    "NON LIFE INSURANCE",
    "MANUFACTURING AND PROCESSING",
    "INVESTMENT INDEX",
    "OTHERS INDEX",
    "TRADING INDEX",
    "MUTUAL FUND",   # not in the requested list — kept, placed last
]

MONTH_NAMES = [calendar.month_name[m] for m in range(1, 13)]  # January…December

# Nepali (Bikram Sambat) month labels — romanised (English letters), keyed by
# Gregorian month number. Each Gregorian month is mapped to the BS month that
# BEGINS within it (Magh starts mid-Jan, Baishakh mid-Apr, …) — the usual NEPSE
# convention. Approximate, since BS months straddle two Gregorian months; the
# averages themselves stay Gregorian.
NEPALI_MONTHS = {
    1: "Magh", 2: "Falgun", 3: "Chaitra", 4: "Baishakh", 5: "Jestha", 6: "Ashadh",
    7: "Shrawan", 8: "Bhadra", 9: "Ashwin", 10: "Kartik", 11: "Mangsir", 12: "Poush",
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
    if _is_missing(value):
        return "—"
    return f"{'+' if value >= 0 else '-'}{abs(value):.2f}%"


def _color(value):
    if _is_missing(value):
        return _MUTED
    return _POS if value >= 0 else _NEG


def _cell_bg(value, cap):
    """Diverging heat tint (green +, red −) scaled by |value| / cap."""
    if _is_missing(value) or not cap:
        return "transparent"
    alpha = min(1.0, abs(value) / cap) * 0.30
    rgb = "22, 163, 74" if value >= 0 else "220, 38, 38"
    return f"rgba({rgb}, {alpha:.3f})"


def _is_missing(value):
    if value is None:
        return True
    try:
        return math.isnan(float(value))
    except (TypeError, ValueError):
        return False


def _ordered_indices(present):
    ordered = [name for name in _INDEX_ORDER if name in present]
    extras = sorted(name for name in present if name not in _INDEX_ORDER)
    return ordered + extras


def _compute():
    import pandas as pd

    from core_analysis.models import NepseMarketIndex

    rows = NepseMarketIndex.objects.values_list(
        "sector_name", "business_date", "close_index", "high_index", "low_index")
    df = pd.DataFrame.from_records(list(rows), columns=["index", "date", "close", "high", "low"])
    if df.empty:
        return {"ok": False, "reason": "No index history available."}

    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df["high"] = pd.to_numeric(df["high"], errors="coerce")
    df["low"] = pd.to_numeric(df["low"], errors="coerce")
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
    avg_by_month, avg_opp_by_month, latest, best_worst = {}, {}, {}, {}
    for idx, g in df.groupby("index"):
        g = g.sort_values("date")
        by_period = g.groupby(g["date"].dt.to_period("M"))
        # Last close of each calendar month (period index keeps months ordered).
        monthly = by_period["close"].last()
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

        # Directional intra-month opportunity: from the earliest trading day's High
        # (if the month's high came first) down to the month low, or from that day's
        # Low (if the low came first) up to the month high — the tradable swing, not
        # just open→close. Averaged per calendar month, partial month excluded.
        opp_buckets = {}
        for period, gm in by_period:
            if period == current_period:
                continue
            gm = gm.sort_values("date")
            m_high, m_low = gm["high"].max(), gm["low"].min()
            if _is_missing(m_high) or _is_missing(m_low):
                continue
            first = gm.iloc[0]
            hh_date = gm.loc[gm["high"].idxmax(), "date"]   # first occurrence
            ll_date = gm.loc[gm["low"].idxmin(), "date"]
            if hh_date <= ll_date:                          # high peaked first → decline
                ref, target = first["high"], m_low
            else:                                           # low bottomed first → rise
                ref, target = first["low"], m_high
            if _is_missing(ref) or _is_missing(target) or ref <= 0:
                continue
            opp_buckets.setdefault(period.month, []).append((target - ref) / ref * 100.0)
        if opp_buckets:
            avg_opp_by_month[idx] = {m: round(sum(v) / len(v), 2) for m, v in opp_buckets.items()}

        # "Latest Monthly Return" = the most recent COMPLETE month, i.e. exclude
        # the in-progress month so the figure is a full-month move, not a 1-day
        # partial print. Fall back to whatever exists if only the partial month is.
        complete = [p for p in ret.index if p != current_period]
        last_period = complete[-1] if complete else ret.index[-1]
        latest[idx] = {
            "month": last_period.month,
            "year": last_period.year,
            "value": round(float(ret.loc[last_period]), 2),
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

    # Latest Monthly Return — one row per index in the fixed matrix order.
    # Alongside the actual latest-month return we show that calendar month's
    # seasonal Avg Return and Opportunity, plus the actual-vs-average difference.
    def _latest_row(idx):
        lt = latest[idx]
        m, yr = lt["month"], lt["year"]
        avg_v = avg_by_month[idx].get(m)
        opp_v = (avg_opp_by_month.get(idx) or {}).get(m)
        # Difference = latest completed month's actual Return vs its seasonal Avg
        # Return (positive = the month beat its historical norm).
        diff_v = (lt["value"] - avg_v) if avg_v is not None else None
        return {
            "label": _label(idx),
            "period_en": f"{calendar.month_name[m]} {yr}",
            "period_np": f"{NEPALI_MONTHS.get(m, '')} {yr}",
            "value_str": _fmt(lt["value"]), "value_color": _color(lt["value"]),
            "avg_str": _fmt(avg_v), "avg_color": _color(avg_v),
            "opp_str": _fmt(opp_v), "opp_color": _color(opp_v),
            "diff_str": _fmt(diff_v), "diff_color": _color(diff_v),
            "value": lt["value"],
        }

    # Kept in the fixed index order (not sorted by value) so every table lines up.
    latest_rows = [_latest_row(idx) for idx in order]

    # Best / Worst month by index (average), in the fixed index order.
    bestworst_rows = [
        {
            "label": _label(idx),
            "best_month": best_worst[idx]["best_month"],
            "best_str": _fmt(best_worst[idx]["best_value"]),
            "worst_month": best_worst[idx]["worst_month"],
            "worst_str": _fmt(best_worst[idx]["worst_value"]),
            "latest_str": _fmt(latest[idx]["value"]),
            "latest_color": _color(latest[idx]["value"]),
        }
        for idx in order
    ]

    # Seasonality matrix (rows = months, cols = indices). Each cell carries BOTH
    # the average monthly return and the directional opportunity %, each on its own
    # heat scale, so the desk can toggle between the two metrics client-side.
    cap_ret = max(
        (abs(v) for mm in avg_by_month.values() for v in mm.values()), default=1.0,
    ) or 1.0
    cap_opp = max(
        (abs(v) for mm in avg_opp_by_month.values() for v in mm.values()), default=1.0,
    ) or 1.0
    def _cell(rv, ov):
        return {
            "ret_text": _fmt(rv), "ret_color": _color(rv), "ret_bg": _cell_bg(rv, cap_ret),
            "opp_text": _fmt(ov), "opp_color": _color(ov), "opp_bg": _cell_bg(ov, cap_opp),
        }

    def _avg(vals):
        vals = [v for v in vals if not _is_missing(v)]
        return round(sum(vals) / len(vals), 2) if vals else None

    columns = [{"key": idx, "label": _label(idx)} for idx in order]
    matrix_rows = []
    for m in _FY_MONTH_ORDER:   # Nepali fiscal-year order: Shrawan (Jul) → Ashadh (Jun)
        rets = [avg_by_month[idx].get(m) for idx in order]
        opps = [(avg_opp_by_month.get(idx) or {}).get(m) for idx in order]
        cells = [_cell(rets[i], opps[i]) for i in range(len(order))]
        matrix_rows.append({
            "month": calendar.month_name[m],
            "month_np": NEPALI_MONTHS.get(m, ""),
            "cells": cells,
            # Month-wise average across all indices (right-hand "Avg" column).
            "row_avg": _cell(_avg(rets), _avg(opps)),
        })

    # Total-average row: per index, the mean of its 12 monthly values (both metrics)
    # — the index's average monthly Return / Opportunity across the year. The final
    # "grand" cell is the overall average across every index and month.
    total_cells = [
        _cell(_avg(avg_by_month.get(idx, {}).values()),
              _avg((avg_opp_by_month.get(idx) or {}).values()))
        for idx in order
    ]
    grand = _cell(
        _avg([v for mm in avg_by_month.values() for v in mm.values()]),
        _avg([v for mm in avg_opp_by_month.values() for v in mm.values()]),
    )
    total_row = {"label": "Average", "cells": total_cells, "grand": grand}

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
        "total_row": total_row,
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
