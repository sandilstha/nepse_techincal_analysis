"""
industry.py — sector-wise statement comparison for the Fundamental Analysis desk.

Builds a MATRIX for one sector and one reporting period: line items down the
side, companies across the top. That orientation is the whole point — a single
company's balance sheet is already on Stock 360, and the question this desk
answers is the one you cannot ask there: how does every bank's loan book compare
in the same quarter?

WHAT IS NOT HERE, AND WHY: there is no Cash Flow Statement. The upstream feed
supplies exactly three statement types (BS 424,649 rows / IS 312,180 / KS
255,116) and no cash-flow rows exist under any type — a search of all 992k rows
for 'cash flow', 'operating activities', 'investing activities' and 'financing
activities' returns nothing. The UI shows Cash Flow as an explicitly disabled tab
rather than an empty table, so the gap reads as a known data limitation instead
of a broken page.
"""
from __future__ import annotations

import hashlib
import logging
from typing import Any

from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_TTL = 1800
# BUMP when the payload shape changes.
INDUSTRY_VERSION = 1

# fs_type -> (label, blurb). Cash flow is listed so the UI can render it as a
# disabled tab with an honest reason attached.
STATEMENTS = {
    "BS": ("Balance Sheet", "What the company owns and owes at the period end."),
    "IS": ("Income Statement", "Revenue, costs and profit earned during the period."),
    "KS": ("Key Stats & Ratios", "Per-share figures, margins and regulatory ratios."),
}
UNAVAILABLE_STATEMENTS = {
    "CF": ("Cash Flow Statement",
           "Not published to this platform. The upstream feed supplies balance "
           "sheet, income statement and key stats only — no cash-flow lines "
           "exist under any statement type."),
}


def sectors() -> list[dict[str, Any]]:
    """Sectors that have filings, with company counts. Cached."""
    from django.db.models import Count

    from core_analysis.models import FinancialStatement as F

    ck = f"industry_sectors_v{INDUSTRY_VERSION}"
    got = cache.get(ck)
    if got is not None:
        return got
    rows = (F.objects.exclude(sector="").exclude(sector__isnull=True)
            .values("sector").annotate(companies=Count("ticker", distinct=True))
            .order_by("-companies"))
    out = [{"sector": r["sector"], "companies": r["companies"]} for r in rows]
    cache.set(ck, out, CACHE_TTL)
    return out


def periods(sector: str, fs_type: str = "BS", limit: int = 12) -> list[dict[str, Any]]:
    """Reporting periods available for a sector, newest first.

    Coverage is reported per period because the newest one is usually INCOMPLETE
    — at 2026-08-20 Commercial Banks show 22 tickers for 2025/26 Q3 but only 19
    for Q4, because late filers have not reported yet. Presenting Q4 as the
    sector's position without that count would understate the sector.
    """
    from django.db.models import Count

    from core_analysis.models import FinancialStatement as F

    from core_analysis.services.canslim import _fy_sort_key

    rows = (F.objects.filter(sector=sector, fs_type=fs_type)
            .values("fiscal_year_ad", "quarter")
            .annotate(companies=Count("ticker", distinct=True)))
    out = [{"fiscal_year": r["fiscal_year_ad"], "quarter": r["quarter"],
            "companies": r["companies"],
            "label": f"{r['fiscal_year_ad']} Q{r['quarter']}"} for r in rows]
    out.sort(key=lambda p: (_fy_sort_key(p["fiscal_year"]), p["quarter"]), reverse=True)
    return out[:limit]


def best_period(sector: str, fs_type: str = "KS"):
    """(fiscal_year, quarter) to score a sector on: the newest period, unless it
    has under 80% of the previous period's filers (early filers only)."""
    avail = periods(sector, fs_type, limit=4)
    if not avail:
        return None
    chosen = avail[0]
    if len(avail) > 1 and chosen["companies"] < avail[1]["companies"] * 0.8:
        chosen = avail[1]
    return chosen["fiscal_year"], chosen["quarter"]


def matrix(sector: str, fs_type: str = "BS", fiscal_year: str = "",
           quarter: int = 0) -> dict[str, Any]:
    """Line items x companies for one sector and period.

    Row order follows ``sorting_code`` where the feed provides one, so the
    statement reads in its filed order (TOTAL ASSETS before its components)
    rather than alphabetically.
    """
    from core_analysis.models import FinancialStatement as F

    fs_type = (fs_type or "BS").upper()
    if fs_type in UNAVAILABLE_STATEMENTS:
        label, why = UNAVAILABLE_STATEMENTS[fs_type]
        return {"ok": False, "unavailable": True, "statement": label, "reason": why}
    if fs_type not in STATEMENTS:
        return {"ok": False, "reason": f"Unknown statement type {fs_type!r}."}

    avail = periods(sector, fs_type)
    if not avail:
        return {"ok": False, "reason": f"No {STATEMENTS[fs_type][0]} filings for {sector}."}
    if not fiscal_year or not quarter:
        # Default to the newest period that is not obviously half-reported: if
        # the latest has materially fewer filers than the one before, prefer the
        # complete one and say so.
        chosen = avail[0]
        if len(avail) > 1 and chosen["companies"] < avail[1]["companies"] * 0.8:
            chosen = avail[1]
        fiscal_year, quarter = chosen["fiscal_year"], chosen["quarter"]

    # Hashed: sector names contain spaces and fiscal years contain "/", both of
    # which are illegal in a memcached key. LocMem tolerates them, so this would
    # only surface as a hard failure the day REDIS_URL is set.
    from core_analysis.services import life_indicators as li
    # Hand-entered life-insurance lines change outside the feed's sync, so
    # their revision is part of the key for the one matrix they extend.
    li_rev = li.revision() if (sector in (li.LIFE, li.NON_LIFE) and fs_type == "KS") else 0
    ck = ("industry_m_v%d_%s" % (
        INDUSTRY_VERSION,
        hashlib.md5(f"{sector}|{fs_type}|{fiscal_year}|{quarter}|{li_rev}".encode()).hexdigest()))
    got = cache.get(ck)
    if got is not None:
        return got

    rows = list(F.objects.filter(sector=sector, fs_type=fs_type,
                                 fiscal_year_ad=fiscal_year, quarter=quarter)
                .values("ticker", "item_name", "item_code", "sorting_code",
                        "amount", "unit"))
    if not rows:
        return {"ok": False,
                "reason": f"No {STATEMENTS[fs_type][0]} rows for {sector} {fiscal_year} Q{quarter}."}
    if fs_type == "KS":
        # The feed's KS block ends at li_ks_534; the hand-entered "Other
        # Indicators" continue the numbering underneath it.
        rows.extend(li.matrix_rows(sector, fiscal_year, quarter))

    tickers = sorted({r["ticker"] for r in rows})
    order: dict[str, tuple] = {}
    units: dict[str, str] = {}
    cells: dict[str, dict[str, float]] = {}
    for r in rows:
        item = (r["item_name"] or "").strip()
        if not item:
            continue
        try:
            amt = float(r["amount"])
        except (TypeError, ValueError):
            continue
        # keep the first non-empty unit seen for the row
        if r.get("unit") and item not in units:
            units[item] = r["unit"]
        sc = (r.get("sorting_code") or "").strip()
        # sorting_code is text; parse as a number so "10" sorts after "9" AND
        # sub-items like "320.1" stay under "320" (isdigit() stranded them).
        try:
            key = (0, float(sc), sc)
        except ValueError:
            key = (1 if sc else 2, 0.0, sc.lower())
        order.setdefault(item, key)
        cells.setdefault(item, {})[r["ticker"]] = amt

    items = sorted(cells, key=lambda i: (order[i], i))
    payload = {
        "ok": True,
        "sector": sector,
        "statement": STATEMENTS[fs_type][0],
        "statement_note": STATEMENTS[fs_type][1],
        "fs_type": fs_type,
        "fiscal_year": fiscal_year,
        "quarter": quarter,
        "period_label": f"{fiscal_year} Q{quarter}",
        "companies": tickers,
        "periods": avail,
        "rows": [{"item": i, "unit": units.get(i, ""),
                  "values": [cells[i].get(t) for t in tickers],
                  # coverage is per LINE ITEM: a ratio only a few banks report
                  # should not look like a sector-wide comparison
                  "reported_by": sum(1 for t in tickers if cells[i].get(t) is not None)}
                 for i in items],
        "line_items": len(items),
        "note": (f"{len(tickers)} companies filed this statement for "
                 f"{fiscal_year} Q{quarter}. Blank cells mean the company did not "
                 f"report that line — not zero."),
    }
    cache.set(ck, payload, CACHE_TTL)
    return payload
