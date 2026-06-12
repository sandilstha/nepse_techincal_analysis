"""
market_insights.py — aggregation layer for the Market Insights dashboard.

Builds the entire dashboard payload (market overview, breadth, top gainers /
losers, most-active scrips, sector performance, heatmap tiles and the NEPSE
index trend history) from the locally-synced NEPSE tables — never from any
external source.

Everything below is derived from a SINGLE daily-stock query (the latest
available trading day) plus a couple of small index queries, then cached so
repeated dashboard polls do not re-hit the database on every request.
"""
from __future__ import annotations

import math

from concurrent.futures import ThreadPoolExecutor

from django.core.cache import cache
from django.db.models import Max

from core_analysis.models import (
    CompanyProfile,
    NepseDailyStockPrice,
    NepseMarketIndex,
)
from core_analysis.services.live_price import fetch_live_rows
from core_analysis.services.nepse_subindices import fetch_subindices
from core_analysis.services.nepse_market_summary import fetch_market_summary
from core_analysis.services.nepse_contributors import fetch_contributors
from core_analysis.services.nepse_top_movers import (
    fetch_top_gainers,
    fetch_top_losers,
    fetch_top_active,
)

CACHE_KEY = "market_insights_payload"
CACHE_TTL = 15  # seconds — short so the live feed actually flows through to polls

# Last successful payload, kept for an hour. Served to callers when a rebuild is
# already in flight (stampede control) so a cold cache never fans out into N×7
# duplicate external requests.
CACHE_LAST_GOOD_KEY = "market_insights_payload_last_good"
CACHE_LAST_GOOD_TTL = 3600
# Only one cold rebuild runs at a time; the lock self-expires so a crashed build
# can't wedge the dashboard.
BUILD_LOCK_KEY = "market_insights_build_lock"
BUILD_LOCK_TTL = 20

NEPSE_INDEX_NAME = "NEPSE INDEX"
SUBINDEX_NEPSE_KEY = "NepseIndex"  # NEPSE headline key in the NepseSubIndices feed
HISTORY_DAYS = 180
# Size of the heatmap pool sent to the client. The dashboard shows the top 60
# by turnover when "All sectors" is selected, but ships a larger pool so the
# sector filter can drill into a sector's full constituent set.
HEATMAP_POOL = 300
TABLE_LIMIT = 5

# Sector sub-indices surfaced in the Sector Performance widget. Deliberately
# excludes the headline NEPSE index and the float / sensitive aggregate indices
# (which are not sectors).
SECTOR_INDEX_NAMES = (
    "BANKING SUBINDEX",
    "DEVELOPMENT BANK INDEX",
    "FINANCE INDEX",
    "HOTELS AND TOURISM INDEX",
    "HYDROPOWER INDEX",
    "INVESTMENT INDEX",
    "LIFE INSURANCE",
    "MANUFACTURING AND PROCESSING",
    "MICROFINANCE INDEX",
    "MUTUAL FUND",
    "NON LIFE INSURANCE",
    "OTHERS INDEX",
    "TRADING INDEX",
)

SECTOR_LABELS = {
    "BANKING SUBINDEX": "Banking",
    "DEVELOPMENT BANK INDEX": "Dev. Bank",
    "FINANCE INDEX": "Finance",
    "HOTELS AND TOURISM INDEX": "Hotels & Tourism",
    "HYDROPOWER INDEX": "Hydropower",
    "INVESTMENT INDEX": "Investment",
    "LIFE INSURANCE": "Life Insurance",
    "MANUFACTURING AND PROCESSING": "Manufacturing",
    "MICROFINANCE INDEX": "Microfinance",
    "MUTUAL FUND": "Mutual Fund",
    "NON LIFE INSURANCE": "Non-Life Insurance",
    "OTHERS INDEX": "Others",
    "TRADING INDEX": "Trading",
}


# ── helpers ────────────────────────────────────────────────────────────────

def _f(value):
    """Coerce Decimal/str/None to a finite float, else None."""
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _round(value, ndigits=2):
    return round(value, ndigits) if value is not None else None


# ── core data pulls ────────────────────────────────────────────────────────

def _latest_stock_rows():
    """Return (latest_business_date, [raw rows]) for the most recent day."""
    latest = NepseDailyStockPrice.objects.aggregate(d=Max("business_date"))["d"]
    if latest is None:
        return None, []
    rows = list(
        NepseDailyStockPrice.objects.filter(business_date=latest).values(
            "symbol",
            "security_name",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "previous_close",
            "total_traded_quantity",
            "total_traded_value",
            "total_trades",
            "market_capitalization",
        )
    )
    return latest, rows


def _sector_map():
    """symbol -> sector_name, for tagging heatmap tiles."""
    pairs = CompanyProfile.objects.exclude(sector_name__isnull=True).exclude(
        sector_name__exact=""
    ).values_list("symbol", "sector_name")
    return dict(pairs)


def _live_get(row, *keys):
    """First non-null value among the given keys (tolerates camelCase + snake_case)."""
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return None


def _live_close(row):
    """Effective close for a live quote.

    The official closePrice is null intraday and only fills in after the 3 PM
    close, so it falls back to the average traded price, then the last traded
    price.
    """
    close = _f(_live_get(row, "closePrice", "close_price"))
    if close is None:
        close = _f(_live_get(row, "averageTradedPrice", "average_traded_price"))
    if close is None:
        close = _f(_live_get(row, "lastUpdatedPrice", "last_updated_price"))
    return close


def _enrich_live(rows, sector_map):
    """Map raw live-feed quotes (camelCase or snake_case) into display dicts."""
    enriched = []
    for r in rows:
        close = _live_close(r)
        if close is None:
            continue
        prev = _f(_live_get(r, "previousDayClosePrice", "previous_day_close_price"))
        change = pct = None
        if prev is not None and prev > 0:
            change = close - prev
            pct = (change / prev) * 100.0
        symbol = _live_get(r, "symbol")
        enriched.append({
            "symbol": symbol,
            "name": _live_get(r, "securityName", "security_name"),
            "sector": sector_map.get(symbol) or "Other",
            "ltp": _round(close),
            "prev": _round(prev),
            "open": _round(_f(_live_get(r, "openPrice", "open_price"))),
            "high": _round(_f(_live_get(r, "highPrice", "high_price"))),
            "low": _round(_f(_live_get(r, "lowPrice", "low_price"))),
            "change": _round(change),
            "pct": _round(pct),
            "volume": int(_live_get(r, "totalTradedQuantity", "total_traded_quantity") or 0),
            "turnover": _f(_live_get(r, "totalTradedValue", "total_traded_value")) or 0.0,
            "trades": int(_live_get(r, "totalTrades", "total_trades") or 0),
            "market_cap": _f(_live_get(r, "marketCapitalization", "market_capitalization")) or 0.0,
        })
    return enriched


def _enrich(rows, sector_map):
    """Turn raw daily rows into display dicts with computed daily change."""
    enriched = []
    for r in rows:
        close = _f(r["close_price"])
        prev = _f(r["previous_close"])
        if close is None:
            continue
        change = pct = None
        if prev is not None and prev > 0:
            change = close - prev
            pct = (change / prev) * 100.0
        enriched.append({
            "symbol": r["symbol"],
            "name": r["security_name"],
            "sector": sector_map.get(r["symbol"]) or "Other",
            "ltp": _round(close),
            "prev": _round(prev),
            "open": _round(_f(r["open_price"])),
            "high": _round(_f(r["high_price"])),
            "low": _round(_f(r["low_price"])),
            "change": _round(change),
            "pct": _round(pct),
            "volume": int(r["total_traded_quantity"] or 0),
            "turnover": _f(r["total_traded_value"]) or 0.0,
            "trades": int(r["total_trades"] or 0),
            "market_cap": _f(r["market_capitalization"]) or 0.0,
        })
    return enriched


# ── live index helpers ─────────────────────────────────────────────────────

def _live_index_metrics(row):
    """Correct value / change for a live index row, working around the feed's
    intraday quirks.

    `closing_index` is 0 until the 3 PM close, so the feed's own abs_change /
    percentage_change are computed off zero and useless intraday. We instead:
      * take the current value from closing_index once set, else the snapshot
        the feed mirrors into open/high/low_index;
      * recover the true previous close from the feed identity
        abs_change = closing_index - prev_close  →  prev = closing_index - abs_change.
    """
    raw_close = _f(_live_get(row, "closing_index", "closingIndex")) or 0.0
    abs_change = _f(_live_get(row, "abs_change", "absChange"))
    high = _f(_live_get(row, "high_index", "highIndex"))
    open_v = _f(_live_get(row, "open_index", "openIndex"))
    low = _f(_live_get(row, "low_index", "lowIndex"))

    value = raw_close if raw_close > 0 else (high or open_v or low)
    prev = (raw_close - abs_change) if abs_change is not None else None
    change = pct = None
    if value is not None and prev is not None and prev > 0:
        change = value - prev
        pct = (change / prev) * 100.0

    return {
        "value": value,
        "prev": prev,
        "change": change,
        "pct": pct,
        "high": high,
        "low": low,
        "turnover": _f(_live_get(row, "turnover_value", "turnoverValue")) or 0.0,
        "volume": int(_live_get(row, "turnover_volume", "turnoverVolume") or 0),
        "transactions": int(_live_get(row, "total_transaction", "totalTransaction") or 0),
        "date": _live_get(row, "business_date", "businessDate"),
    }


def _live_index_by_name(rows):
    """Map UPPERCASED index name -> raw row."""
    out = {}
    for row in rows or []:
        name = (_live_get(row, "index_name", "indexName") or "").strip().upper()
        if name:
            out[name] = row
    return out


def _sectors_live(rows):
    """Sector performance from the live-index feed (same labels as _sectors)."""
    sectors = []
    for name, row in _live_index_by_name(rows).items():
        if name not in SECTOR_INDEX_NAMES:
            continue
        m = _live_index_metrics(row)
        sectors.append({
            "sector": SECTOR_LABELS.get(name, name.title()),
            "raw": name,
            "index": _round(m["value"]),
            "change": _round(m["change"]),
            "pct": _round(m["pct"]),
            "turnover": m["turnover"],
        })
    sectors.sort(key=lambda s: (s["pct"] is None, -(s["pct"] or 0.0)))
    return sectors


# ── NepseSubIndices feed (authoritative index source) ──────────────────────

def _subindex_metrics(row):
    """Value / change for one NepseSubIndices row. `closingIndex` is populated
    and `absChange`/`percentageChange` are correct here; if the close hasn't been
    published yet intraday (0), fall back to the live snapshot and recover the
    previous close from absChange (= closingIndex - prev)."""
    if not row:
        return {"value": None, "change": None, "pct": None, "high": None, "low": None,
                "turnover": 0.0, "date": None}
    close = _f(row.get("closingIndex")) or 0.0
    high = _f(row.get("highIndex"))
    low = _f(row.get("lowIndex"))
    open_v = _f(row.get("openIndex"))
    abs_change = _f(row.get("absChange"))
    pct_given = _f(row.get("percentageChange"))

    if close > 0:
        value, change, pct = close, abs_change, pct_given
        prev = (close - abs_change) if abs_change is not None else None
        # Guard against a bogus -100%-style value left over from a zero close.
        if (pct is None or abs(pct) >= 99.9) and prev and prev > 0:
            change = value - prev
            pct = (change / prev) * 100.0
    else:
        value = high or open_v or low
        prev = (0.0 - abs_change) if abs_change is not None else None
        change = (value - prev) if (value is not None and prev is not None) else None
        pct = (change / prev) * 100.0 if (change is not None and prev) else None

    return {
        "value": value,
        "change": change,
        "pct": pct,
        "high": high,
        "low": low,
        "turnover": _f(row.get("turnoverValue")) or 0.0,
        "date": row.get("businessDate"),
    }


def _contributors_index_metrics(row, fallback=None):
    """Headline NEPSE metrics parsed from the contributors page.

    The contributors page carries the exchange-matching live headline during the
    session. Keep high/low/date from the sub-index feed when available because
    the contributor summary only exposes value, change and previous close.
    """
    if not row:
        return None

    fallback = fallback or {}
    value = _f(row.get("value"))
    if value is None:
        return None

    change = _f(row.get("change"))
    prev = _f(row.get("prev_close"))
    if change is None and prev is not None:
        change = value - prev
    if prev is None and change is not None:
        prev = value - change

    pct = _f(row.get("pct"))
    if pct is None and change is not None and prev and prev > 0:
        pct = (change / prev) * 100.0

    return {
        "value": value,
        "prev": prev,
        "change": change,
        "pct": pct,
        "high": _f(row.get("high")) if row.get("high") is not None else fallback.get("high"),
        "low": _f(row.get("low")) if row.get("low") is not None else fallback.get("low"),
        "turnover": _f(row.get("turnover")) if row.get("turnover") is not None else fallback.get("turnover", 0.0),
        "date": (
            row.get("date")
            or row.get("businessDate")
            or row.get("business_date")
            or fallback.get("date")
        ),
    }


def _sectors_from_subindices(subidx):
    """Sector performance from the NepseSubIndices feed (same labels as _sectors)."""
    sectors = []
    for name, row in (subidx or {}).items():
        key = str(name).strip().upper()
        if key not in SECTOR_INDEX_NAMES:
            continue
        m = _subindex_metrics(row)
        sectors.append({
            "sector": SECTOR_LABELS.get(key, name),
            "raw": key,
            "index": _round(m["value"]),
            "change": _round(m["change"]),
            "pct": _round(m["pct"]),
            "turnover": m["turnover"],
        })
    sectors.sort(key=lambda s: (s["pct"] is None, -(s["pct"] or 0.0)))
    return sectors


# ── widget builders ────────────────────────────────────────────────────────

def _overview(enriched, nepse_live=None, market_summary=None):
    # Market totals: prefer the official MarketSummaryHistory row; otherwise sum
    # the live-price feed (which runs slightly low vs the exchange).
    ms = market_summary or {}
    ms_turnover = _f(ms.get("totalTurnover"))
    ms_volume = _f(ms.get("totalTradedShares"))
    ms_trades = ms.get("totalTransactions")
    ms_scrips = ms.get("tradedScrips")
    totals = {
        "turnover": round(ms_turnover, 2) if ms_turnover is not None else round(sum(s["turnover"] for s in enriched), 2),
        "volume": int(ms_volume) if ms_volume is not None else sum(s["volume"] for s in enriched),
        "trades": int(ms_trades) if ms_trades is not None else sum(s["trades"] for s in enriched),
        "scrips_traded": int(ms_scrips) if ms_scrips is not None else len(enriched),
    }

    if nepse_live and nepse_live.get("value") is not None:
        nepse = {
            "nepse_index": _round(nepse_live["value"]),
            "nepse_change": _round(nepse_live["change"]),
            "nepse_pct": _round(nepse_live["pct"]),
            "nepse_high": _round(nepse_live["high"]),
            "nepse_low": _round(nepse_live["low"]),
            "nepse_date": nepse_live["date"],
        }
    else:
        row = (
            NepseMarketIndex.objects.filter(sector_name=NEPSE_INDEX_NAME)
            .order_by("-business_date")
            .first()
        )
        nepse = {
            "nepse_index": _round(_f(row.close_index)) if row else None,
            "nepse_change": _round(_f(row.absolute_change)) if row else None,
            "nepse_pct": _round(_f(row.percentage_change)) if row else None,
            "nepse_high": _round(_f(row.high_index)) if row else None,
            "nepse_low": _round(_f(row.low_index)) if row else None,
            "nepse_date": row.business_date.isoformat() if row else None,
        }

    nepse.update(totals)
    return nepse


def _breadth(enriched):
    advancing = declining = unchanged = 0
    for s in enriched:
        if s["change"] is None:
            continue
        if s["change"] > 0:
            advancing += 1
        elif s["change"] < 0:
            declining += 1
        else:
            unchanged += 1
    total = advancing + declining + unchanged
    return {
        "advancing": advancing,
        "declining": declining,
        "unchanged": unchanged,
        "total": total,
    }


def _gainers(enriched, limit=TABLE_LIMIT):
    ranked = [s for s in enriched if s["pct"] is not None]
    ranked.sort(key=lambda s: s["pct"], reverse=True)
    return _slim(ranked[:limit])


def _losers(enriched, limit=TABLE_LIMIT):
    ranked = [s for s in enriched if s["pct"] is not None]
    ranked.sort(key=lambda s: s["pct"])
    return _slim(ranked[:limit])


def _most_active(enriched, limit=TABLE_LIMIT):
    ranked = sorted(enriched, key=lambda s: s["turnover"], reverse=True)
    return _slim(ranked[:limit])


def _slim(rows):
    """Trim the table rows to just the columns the widgets render."""
    return [
        {
            "symbol": s["symbol"],
            "name": s["name"],
            "ltp": s["ltp"],
            "change": s["change"],
            "pct": s["pct"],
            "volume": s["volume"],
            "turnover": s["turnover"],
        }
        for s in rows
    ]


def _sectors():
    latest = (
        NepseMarketIndex.objects.filter(sector_name__in=SECTOR_INDEX_NAMES)
        .aggregate(d=Max("business_date"))["d"]
    )
    if latest is None:
        return []
    rows = NepseMarketIndex.objects.filter(
        business_date=latest, sector_name__in=SECTOR_INDEX_NAMES
    )
    sectors = [
        {
            "sector": SECTOR_LABELS.get(r.sector_name, r.sector_name.title()),
            "raw": r.sector_name,
            "index": _round(_f(r.close_index)),
            "change": _round(_f(r.absolute_change)),
            "pct": _round(_f(r.percentage_change)),
            "turnover": _f(r.turnover_values) or 0.0,
        }
        for r in rows
    ]
    sectors.sort(key=lambda s: (s["pct"] is None, -(s["pct"] or 0.0)))
    return sectors


def _heatmap(enriched, limit=HEATMAP_POOL):
    """Most liquid scrips, tagged with their (clean) company sector + performance.

    Sorted by turnover so the client can show the top slice for "All sectors"
    and the full constituent list when a single sector is filtered.
    """
    tiles = [s for s in enriched if s["pct"] is not None and s["turnover"] > 0]
    tiles.sort(key=lambda s: s["turnover"], reverse=True)
    return [
        {
            "symbol": s["symbol"],
            "sector": s["sector"] or "Other",
            "pct": s["pct"],
            "ltp": s["ltp"],
            "turnover": s["turnover"],
        }
        for s in tiles[:limit]
    ]


def _nepse_history(days=HISTORY_DAYS):
    qs = (
        NepseMarketIndex.objects.filter(sector_name=NEPSE_INDEX_NAME)
        .order_by("-business_date")
        .values("business_date", "close_index", "turnover_values")[:days]
    )
    rows = list(qs)[::-1]  # back to chronological order
    return [
        {
            "date": r["business_date"].isoformat(),
            "close": _f(r["close_index"]),
            "turnover": _f(r["turnover_values"]) or 0.0,
        }
        for r in rows
    ]


# ── public API ─────────────────────────────────────────────────────────────

def build_payload(force=False, cache_only=False):
    """Assemble (and cache) the full Market Insights dashboard payload.

    Stock-level widgets use the intraday live feed when it is reachable, and
    fall back to the end-of-day database otherwise. The NEPSE headline prefers
    the official contributors summary, sector indices prefer NepseSubIndices,
    and both fall back to the end-of-day database when live services are down.

    cache_only=True returns the cached payload if present, else None — without
    ever touching the external feeds. The page-render view uses this so the HTML
    shell is returned instantly; the browser then fetches the live payload from
    /insights/api/ on demand (see insights_views.market_insights_view).
    """
    if not force:
        cached = cache.get(CACHE_KEY)
        if cached is not None:
            return cached

    # Render path: do not block HTML generation on the external feeds.
    if cache_only:
        return None

    # Stampede control: only one cold rebuild runs at a time. Other callers
    # polling just after the 15s cache expired are served the last known-good
    # payload instead of each firing its own seven external requests.
    got_lock = cache.add(BUILD_LOCK_KEY, 1, BUILD_LOCK_TTL)
    if not got_lock and not force:
        last_good = cache.get(CACHE_LAST_GOOD_KEY)
        if last_good is not None:
            return last_good

    # Fetch every external feed CONCURRENTLY. Done sequentially, a single slow or
    # down service serialises into a multi-second stall (timeouts add up); in
    # parallel the cold-build cost is just the slowest single feed.
    with ThreadPoolExecutor(max_workers=7) as pool:
        f_live = pool.submit(fetch_live_rows)
        f_subidx = pool.submit(fetch_subindices)
        f_summary = pool.submit(fetch_market_summary)
        f_contrib = pool.submit(fetch_contributors)
        f_gainers = pool.submit(fetch_top_gainers, TABLE_LIMIT)
        f_losers = pool.submit(fetch_top_losers, TABLE_LIMIT)
        f_active = pool.submit(fetch_top_active, TABLE_LIMIT)
        live_rows = f_live.result()
        subidx = f_subidx.result()
        summary = f_summary.result()
        contrib = f_contrib.result()
        top_gainers = f_gainers.result()
        top_losers = f_losers.result()
        top_active = f_active.result()

    sector_map = _sector_map()

    if live_rows:
        enriched = _enrich_live(live_rows, sector_map)

    if live_rows and enriched:
        is_live = True
        as_of = _live_get(live_rows[0], "businessDate", "business_date")
        live_feed_date = as_of  # the live feed's own date, for staleness check below
        live_time = max(
            (_live_get(r, "lastUpdatedTime", "last_updated_time") or "") for r in live_rows
        ) or None
    else:
        latest_date, rows = _latest_stock_rows()
        enriched = _enrich(rows, sector_map)
        is_live = False
        as_of = latest_date.isoformat() if latest_date else None
        live_feed_date = None
        live_time = None

    # Sector performance comes from the NepseSubIndices feed. The NEPSE headline
    # prefers the contributors page below because that source tracks the live
    # exchange headline during the session, while NepseSubIndices has been
    # observed freezing closingIndex on a prior tick/session.
    headline_from_contributors = False
    if subidx:
        nepse_headline = _subindex_metrics(subidx.get(SUBINDEX_NEPSE_KEY))
        sectors = _sectors_from_subindices(subidx)
    else:
        nepse_headline = None
        sectors = _sectors()

    contrib_headline = _contributors_index_metrics((contrib or {}).get("index"), nepse_headline)
    if contrib_headline:
        nepse_headline = contrib_headline
        headline_from_contributors = True

    if nepse_headline and nepse_headline.get("value") is not None:
        index_source = "official"
        official_date = nepse_headline.get("date")
        # Label the dashboard with the official trading day. The live-price feed
        # can lag (it has served a stale prior-day date); trust the authoritative
        # index feed's date for the headline so totals and "as of" agree.
        if official_date:
            as_of = official_date
            # If the live-price feed's own date trails the official trading day,
            # it's serving stale prior-session quotes — don't badge the dashboard
            # "LIVE" off it. The headline (index/turnover) is already sourced from
            # the fresh official feeds; only the per-scrip live view is stale.
            if is_live and live_feed_date and str(live_feed_date)[:10] < official_date[:10]:
                is_live = False
                live_time = None
    else:
        nepse_headline = None  # let _overview fall back to the DB
        index_source = "eod"

    # Official daily totals (turnover / trades / shares) come from the
    # MarketSummaryHistory feed. Match the row to the AUTHORITATIVE trading day
    # reported by the official headline date, NOT the live-price feed — that
    # feed has been observed serving a stale prior-day date, which would
    # otherwise select a previous day's turnover for the headline. When the
    # contributor page supplies the headline, use the latest summary row because
    # that page does not expose its own business date.
    ms_row = None
    if summary:
        summary_day = str(summary[0].get("businessDate") or "")[:10]
        official_day = summary_day if headline_from_contributors and summary_day else (
            ((nepse_headline or {}).get("date") or as_of or "")[:10]
        )
        ms_row = next(
            (r for r in summary if str(r.get("businessDate") or "")[:10] == official_day),
            summary[0],
        )
        if headline_from_contributors and ms_row.get("businessDate"):
            as_of = ms_row.get("businessDate")
            if nepse_headline is not None:
                nepse_headline["date"] = ms_row.get("businessDate")
            if is_live and live_feed_date and str(live_feed_date)[:10] < str(as_of)[:10]:
                is_live = False
                live_time = None

    # Reconcile sector turnover to the OFFICIAL total: the 13 index sub-sectors
    # only cover indexed scrips, so the remainder (debentures, preference /
    # promoter shares) is shown as an "Other" row. This makes sector turnover
    # match the headline Total Turnover instead of reading low.
    if sectors and ms_row:
        official_turnover = _f(ms_row.get("totalTurnover"))
        sector_turnover = sum((s.get("turnover") or 0.0) for s in sectors)
        if official_turnover and official_turnover - sector_turnover > 0:
            sectors = sectors + [{
                "sector": "Other", "raw": "OTHER",
                "index": None, "change": None, "pct": None,
                "turnover": round(official_turnover - sector_turnover, 2),
            }]

    # Official top gainers / losers / most-active scrips (fetched above); fall
    # back to the lists computed from the live-price feed when unavailable.
    gainers = top_gainers or _gainers(enriched)
    losers = top_losers or _losers(enriched)
    most_active = top_active or _most_active(enriched)

    payload = {
        "as_of": as_of,
        "live": is_live,
        "index_source": index_source,
        "source": "live" if is_live else "eod",
        "live_time": live_time,
        "has_data": bool(enriched),
        "overview": _overview(enriched, nepse_headline, ms_row),
        "breadth": _breadth(enriched),
        "gainers": gainers,
        "losers": losers,
        "most_active": most_active,
        "sectors": sectors,
        "heatmap": _heatmap(enriched),
        "history": _nepse_history(),
        "contributors": {
            "positive": contrib["positive"] if contrib else [],
            "negative": contrib["negative"] if contrib else [],
            "sectors": contrib.get("sectors", {"positive": [], "negative": []}) if contrib else {"positive": [], "negative": []},
        },
        "stock_count": len(enriched),
    }
    cache.set(CACHE_KEY, payload, CACHE_TTL)
    cache.set(CACHE_LAST_GOOD_KEY, payload, CACHE_LAST_GOOD_TTL)
    cache.delete(BUILD_LOCK_KEY)
    return payload


def invalidate_cache():
    cache.delete(CACHE_KEY)
