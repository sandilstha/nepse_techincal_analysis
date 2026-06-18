"""
broker_analytics.py — "Dalal Street X" style broker analytics built on top of
the trade-level floorsheet feed.

The floorsheet lives in the local ``nepse_floorsheet`` table (model
``NepseFloorsheet``), populated by the ``sync_floorsheet`` management command.
Each row is one executed trade with the fields:

    stock_symbol, buyer, seller, quantity, rate, amount, business_date,
    sector, trade_time

Strategy — never scan the whole table. For one trading day we read just that
day's rows (filtered on ``business_date``) and collapse them into a compact
per-day *aggregate*:

    {
      'date':   '2026-06-17',
      'buy':    { symbol: { broker: [qty, amount] } },   # broker == buyer
      'sell':   { symbol: { broker: [qty, amount] } },   # broker == seller
      'sector': { symbol: 'Commercial Banks' },
    }

Every tab (Broker Favorites, Stock Wise Details, Hotstocks, Net Holding, Broker
Concentration) is derived from this structure. Multi-day ranges (1W / 1M / 3M)
are just the element-wise sum of several cached day aggregates, so once a day is
built it is reused everywhere. Day aggregates are cached long (immutable history)
except the latest/most-recent day, which gets a short TTL because it still moves
intraday.
"""
from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timedelta

from django.core.cache import cache

logger = logging.getLogger(__name__)

# Floorsheet is read from the local nepse_floorsheet table (populated by the
# `sync_floorsheet` management command). Per-day aggregates are still cached so
# repeated dashboard hits don't re-run the aggregation over a day of trade rows.

# Cache TTLs.
DAY_TTL_PAST = 60 * 60 * 24 * 7     # finished sessions are immutable for a week
DAY_TTL_LATEST = int(os.environ.get("NEPSE_FLOORSHEET_LATEST_TTL", "300"))
STALE_DAY_TTL = int(os.environ.get("NEPSE_FLOORSHEET_STALE_TTL", "3600"))
LATEST_DATE_TTL = int(os.environ.get("NEPSE_FLOORSHEET_LATEST_DATE_TTL", "90"))
RANGE_TTL = int(os.environ.get("NEPSE_FLOORSHEET_RANGE_TTL", "300"))
META_TTL = 300
FAIL_SENTINEL = "FAIL"
FAIL_TTL = 30
DAY_BUILD_LOCK_TTL = int(os.environ.get("NEPSE_FLOORSHEET_BUILD_LOCK_TTL", "180"))
LOCK_WAIT_SECONDS = float(os.environ.get("NEPSE_FLOORSHEET_LOCK_WAIT_SECONDS", "20"))
LOCK_WAIT_STEP = 0.25

RANGE_DAYS = {"today": 1, "1w": 7, "1m": 30, "3m": 90}
TOP_N = 10
_MISSING = object()


# ─────────────────────────────────────────────────────────────────────────────
# Local DB read + per-day aggregate
# ─────────────────────────────────────────────────────────────────────────────
def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def get_latest_trading_date():
    """Most recent date that has floorsheet rows ('YYYY-MM-DD'), or None."""
    cached = cache.get("fs_latest_date")
    if cached is not None:
        return None if cached == FAIL_SENTINEL else cached
    try:
        from core_analysis.models import NepseFloorsheet

        latest = (
            NepseFloorsheet.objects.order_by("-business_date")
            .values_list("business_date", flat=True)
            .first()
        )
        latest = latest.isoformat() if latest else None
    except Exception:  # pragma: no cover - DB optional for this overlay
        cache.set("fs_latest_date", FAIL_SENTINEL, FAIL_TTL)
        return None
    if latest:
        cache.set("fs_latest_date", latest, LATEST_DATE_TTL)
    return latest


def _day_has_rows(date_str):
    """Cheap check whether a calendar date has any floorsheet rows in the DB."""
    key = f"fs_count_{date_str}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    try:
        from core_analysis.models import NepseFloorsheet

        has = NepseFloorsheet.objects.filter(business_date=date_str).exists()
    except Exception:  # pragma: no cover
        return False
    cache.set(key, has, DAY_TTL_PAST if not _is_latest(date_str) else DAY_TTL_LATEST)
    return has


def _is_latest(date_str):
    return date_str == cache.get("fs_latest_date") or date_str == get_latest_trading_date()


def _fetch_day_rows(date_str):
    """Every floorsheet row for one business_date, as lightweight dicts.

    Returns the same column names the aggregate builder expects (stock_symbol,
    buyer, seller, quantity, amount, sector), read straight from the local table.
    """
    from core_analysis.models import NepseFloorsheet

    qs = NepseFloorsheet.objects.filter(business_date=date_str).values(
        "stock_symbol", "buyer", "seller", "quantity", "amount", "sector"
    )
    return list(qs)


def _cached_day_value(key, stale_key):
    cached = cache.get(key)
    if cached is None:
        return _MISSING
    if cached == FAIL_SENTINEL:
        stale = cache.get(stale_key)
        return stale if stale is not None else None
    return cached


def _wait_for_day_build(key, stale_key):
    deadline = time.monotonic() + LOCK_WAIT_SECONDS
    while time.monotonic() < deadline:
        time.sleep(LOCK_WAIT_STEP)
        cached = _cached_day_value(key, stale_key)
        if cached is not _MISSING:
            return cached
    stale = cache.get(stale_key)
    return stale if stale is not None else _MISSING


def get_day_aggregate(date_str):
    """Compact per-day aggregate (see module docstring). Cached. None on failure."""
    key = f"fs_agg_{date_str}"
    stale_key = f"fs_agg_stale_{date_str}"
    cached = _cached_day_value(key, stale_key)
    if cached is not _MISSING:
        return cached

    lock_key = f"{key}_lock"
    if not cache.add(lock_key, "1", DAY_BUILD_LOCK_TTL):
        cached = _wait_for_day_build(key, stale_key)
        return None if cached is _MISSING else cached

    try:
        try:
            cached = _cached_day_value(key, stale_key)
            if cached is not _MISSING:
                return cached
            rows = _fetch_day_rows(date_str)
        except Exception:  # pragma: no cover - DB read failure
            cache.set(key, FAIL_SENTINEL, FAIL_TTL)
            stale = cache.get(stale_key)
            return stale if stale is not None else None

        buy, sell, sector = {}, {}, {}
        for r in rows:
            sym = r.get("stock_symbol")
            if not sym:
                continue
            qty = _to_float(r.get("quantity"))
            amt = _to_float(r.get("amount"))
            buyer, seller = r.get("buyer"), r.get("seller")
            if r.get("sector"):
                sector.setdefault(sym, r["sector"])
            if buyer is not None:
                b = buy.setdefault(sym, {})
                cell = b.get(buyer)
                if cell:
                    cell[0] += qty
                    cell[1] += amt
                else:
                    b[buyer] = [qty, amt]
            if seller is not None:
                s = sell.setdefault(sym, {})
                cell = s.get(seller)
                if cell:
                    cell[0] += qty
                    cell[1] += amt
                else:
                    s[seller] = [qty, amt]

        agg = {"date": date_str, "buy": buy, "sell": sell, "sector": sector}
        is_latest = _is_latest(date_str)
        ttl = DAY_TTL_LATEST if is_latest else DAY_TTL_PAST
        cache.set(key, agg, ttl)
        cache.set(stale_key, agg, STALE_DAY_TTL)
        if is_latest:
            cache.set("fs_meta", _build_meta(date_str, agg), META_TTL)
        return agg
    finally:
        cache.delete(lock_key)


def _trading_dates(range_key):
    """List of trading-day strings for a range, newest first (incl. latest)."""
    latest = get_latest_trading_date()
    if not latest:
        return []
    if range_key == "today":
        return [latest]
    span = RANGE_DAYS.get(range_key, 1)
    start = datetime.strptime(latest, "%Y-%m-%d").date()
    local_dates = _local_trading_dates(start, span)
    if local_dates:
        return local_dates
    dates = []
    for i in range(span):
        d = start - timedelta(days=i)
        ds = d.isoformat()
        if ds == latest or _day_has_rows(ds):
            dates.append(ds)
    return dates


def _local_trading_dates(latest_date, span):
    """Trading dates from the local EOD table; avoids 90 cheap upstream probes."""
    key = f"fs_local_dates_{latest_date.isoformat()}_{span}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    try:
        from core_analysis.models import NepseDailyStockPrice

        start_date = latest_date - timedelta(days=span - 1)
        qs = (
            NepseDailyStockPrice.objects.filter(
                business_date__gte=start_date,
                business_date__lte=latest_date,
            )
            .order_by("-business_date")
            .values_list("business_date", flat=True)
            .distinct()
        )
        dates = [d.isoformat() for d in qs]
    except Exception:  # pragma: no cover - DB optional for this overlay
        dates = []
    cache.set(key, dates, META_TTL)
    return dates


def _merge_into(dst, src):
    """Accumulate one side ({symbol: {broker: [qty, amt]}}) into dst."""
    for sym, brokers in src.items():
        d = dst.setdefault(sym, {})
        for broker, (qty, amt) in brokers.items():
            cell = d.get(broker)
            if cell:
                cell[0] += qty
                cell[1] += amt
            else:
                d[broker] = [qty, amt]


def get_range_aggregate(range_key):
    """Sum of every day aggregate in the range. Cached. None if nothing built."""
    range_key = range_key if range_key in RANGE_DAYS else "today"
    key = f"fs_range_{range_key}_{get_latest_trading_date()}"
    cached = cache.get(key)
    if cached is not None:
        return cached or None

    buy, sell, sector = {}, {}, {}
    dates = _trading_dates(range_key)
    aggs = [get_day_aggregate(ds) for ds in dates]

    for agg in aggs:
        if not agg:
            continue
        _merge_into(buy, agg["buy"])
        _merge_into(sell, agg["sell"])
        for sym, sec in agg["sector"].items():
            sector.setdefault(sym, sec)

    if not buy and not sell:
        cache.set(key, {}, FAIL_TTL)
        return None

    merged = {
        "range": range_key,
        "dates": dates,
        "buy": buy,
        "sell": sell,
        "sector": sector,
    }
    cache.set(key, merged, RANGE_TTL)
    return merged


# ─────────────────────────────────────────────────────────────────────────────
# Derived helpers
# ─────────────────────────────────────────────────────────────────────────────
def _metric_index(view):
    """0 = quantity (shares traded), 1 = amount (turnover)."""
    return 1 if view == "turnover" else 0


def _symbol_total(agg, sym):
    """Total traded shares for a symbol on the buy side (== sell side)."""
    return sum(q for q, _a in agg["buy"].get(sym, {}).values())


def _row(broker_or_sym, qty, amt, pct):
    avg = (amt / qty) if qty else 0.0
    return {
        "key": broker_or_sym,
        "quantity": round(qty),
        "amount": round(amt, 2),
        "avg_price": round(avg, 2),
        "pct": round(pct, 2),
    }


def _company_names():
    """{symbol: security_name} for nice dropdown labels (best-effort)."""
    cached = cache.get("fs_company_names")
    if cached is not None:
        return cached
    names = {row["symbol"]: row["name"] for row in _company_meta()["symbols"]}
    cache.set("fs_company_names", names, META_TTL)
    return names


def _company_meta():
    """Company symbols/sectors from local DB, used as instant dropdown fallback."""
    cached = cache.get("fs_company_meta")
    if cached is not None:
        return cached
    symbols, sectors = [], set()
    try:
        from core_analysis.models import CompanyProfile

        rows = CompanyProfile.objects.values_list("symbol", "security_name", "sector_name")
        for symbol, name, sector in rows:
            if not symbol:
                continue
            symbols.append({"symbol": symbol, "name": name or symbol})
            if sector:
                sectors.add(sector)
    except Exception:  # pragma: no cover - DB optional for this overlay
        symbols = []
    symbols.sort(key=lambda row: row["symbol"])
    out = {"symbols": symbols, "sectors": sorted(sectors)}
    cache.set("fs_company_meta", out, META_TTL)
    return out


def _fallback_brokers():
    cached = cache.get("fs_default_brokers")
    if cached is not None:
        return cached
    raw = os.environ.get("NEPSE_BROKER_CHOICES", "").strip()
    if raw:
        brokers = [part.strip() for part in raw.split(",") if part.strip()]
    else:
        max_broker = int(os.environ.get("NEPSE_BROKER_MAX", "100"))
        brokers = list(range(1, max_broker + 1))
    cache.set("fs_default_brokers", brokers, META_TTL)
    return brokers


def _broker_sort_key(broker):
    try:
        return (0, int(broker))
    except (TypeError, ValueError):
        return (1, str(broker))


def _build_meta(latest, agg=None):
    brokers, symbols, sectors = set(), set(), set()
    if agg:
        for side in (agg["buy"], agg["sell"]):
            for sym, brks in side.items():
                symbols.add(sym)
                brokers.update(brks.keys())
        sectors.update(v for v in agg["sector"].values() if v)

    company_meta = _company_meta()
    names = {row["symbol"]: row["name"] for row in company_meta["symbols"]}
    if not symbols:
        return {
            "ok": bool(latest),
            "latest_date": latest,
            "brokers": _fallback_brokers(),
            "symbols": company_meta["symbols"],
            "sectors": company_meta["sectors"],
            "exact": False,
        }

    return {
        "ok": True,
        "latest_date": latest,
        "brokers": sorted(brokers, key=_broker_sort_key),
        "symbols": [{"symbol": s, "name": names.get(s, s)} for s in sorted(symbols)],
        "sectors": sorted(sectors),
        "exact": True,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Tab builders
# ─────────────────────────────────────────────────────────────────────────────
def meta():
    """Dropdown data + last-updated stamp for the dashboard shell."""
    cached = cache.get("fs_meta")
    if cached:
        return cached
    latest = get_latest_trading_date()
    agg = None
    if latest:
        cached_agg = _cached_day_value(f"fs_agg_{latest}", f"fs_agg_stale_{latest}")
        if cached_agg is not _MISSING:
            agg = cached_agg
    out = _build_meta(latest, agg)
    cache.set("fs_meta", out, META_TTL if agg else min(META_TTL, 60))
    return out


def meta_cached():
    """Non-blocking meta read for the initial page render (no upstream fetch).

    Returns whatever ``meta()`` last cached, or a local fallback. The page paints
    instantly from this; the frontend refreshes exact metadata in the background.
    """
    cached = cache.get("fs_meta")
    if cached:
        return cached
    latest = cache.get("fs_latest_date")
    if latest == FAIL_SENTINEL:
        latest = None
    return _build_meta(latest, None)


def _typed_broker(broker):
    """Match the dropdown's string broker against int keys in the aggregate."""
    try:
        return int(broker)
    except (TypeError, ValueError):
        return broker


def broker_favorites(brokers, range_key="today", view="shares"):
    """Top buy / top sell stocks for one or more brokers (Broker Favorites tab).

    ``brokers`` may be a single value or a list/iterable of broker numbers; when
    several are given their flow is pooled (qty/amount summed per stock) so the
    tables show the combined favourites of the selected desk.
    """
    agg = get_range_aggregate(range_key)
    if not agg:
        return {"ok": False, "buy": [], "sell": []}
    if isinstance(brokers, (list, tuple, set)):
        sel = {_typed_broker(b) for b in brokers}
    else:
        sel = {_typed_broker(brokers)}
    sel.discard(None)
    if not sel:
        return {"ok": True, "buy": [], "sell": []}
    mi = _metric_index(view)

    def side(side_map):
        items = []
        total = 0.0
        for sym, broker_cells in side_map.items():
            q = a = 0.0
            for b in sel:
                cell = broker_cells.get(b)
                if cell:
                    q += cell[0]
                    a += cell[1]
            if q or a:
                items.append((sym, q, a))
                total += a if mi else q
        rows = [
            _row(sym, q, a, (100.0 * (a if mi else q) / total) if total else 0.0)
            for sym, q, a in items
        ]
        rows.sort(key=lambda r: r["amount"] if mi else r["quantity"], reverse=True)
        return rows[:TOP_N]

    return {"ok": True, "buy": side(agg["buy"]), "sell": side(agg["sell"])}


def stock_wise(symbol, range_key="today", view="shares"):
    """Top buy / sell / holding brokers for one stock (Stock Wise Details tab)."""
    agg = get_range_aggregate(range_key)
    if not agg or not symbol:
        return {"ok": False, "buy": [], "sell": [], "holdings": []}
    mi = _metric_index(view)
    total = _symbol_total(agg, symbol)
    turnover = sum(a for _q, a in agg["buy"].get(symbol, {}).values())
    denom = turnover if mi else total

    def side(side_map):
        rows = [
            _row(broker, q, a, (100.0 * (a if mi else q) / denom) if denom else 0.0)
            for broker, (q, a) in side_map.get(symbol, {}).items()
        ]
        rows.sort(key=lambda r: r["amount"] if mi else r["quantity"], reverse=True)
        return rows[:TOP_N]

    # Holdings = net position per broker (buy qty - sell qty), with avg buy/sell.
    buy_b = agg["buy"].get(symbol, {})
    sell_b = agg["sell"].get(symbol, {})
    holdings = []
    for broker in set(buy_b) | set(sell_b):
        bq, ba = buy_b.get(broker, [0, 0])
        sq, sa = sell_b.get(broker, [0, 0])
        net = bq - sq
        if net == 0:
            continue
        holdings.append(
            {
                "key": broker,
                "quantity": round(net),
                "amount": round(ba, 2),
                "avg_buy": round(ba / bq, 2) if bq else 0.0,
                "avg_sell": round(sa / sq, 2) if sq else 0.0,
            }
        )
    holdings.sort(key=lambda r: abs(r["quantity"]), reverse=True)

    return {
        "ok": True,
        "symbol": symbol,
        "buy": side(agg["buy"]),
        "sell": side(agg["sell"]),
        "holdings": holdings[:TOP_N],
    }


def net_holding(broker, range_key="today", exclude_mf=False, sector="All"):
    """Per-stock net position for one broker (Net Holding treemap)."""
    agg = get_range_aggregate(range_key)
    if not agg:
        return {"ok": False, "items": []}
    broker = _typed_broker(broker)
    items = []
    symbols = set(agg["buy"]) | set(agg["sell"])
    for sym in symbols:
        if sector and sector != "All" and agg["sector"].get(sym) != sector:
            continue
        if exclude_mf and _is_mutual_fund(sym):
            continue
        bq = agg["buy"].get(sym, {}).get(broker, [0, 0])[0]
        sq = agg["sell"].get(sym, {}).get(broker, [0, 0])[0]
        net = bq - sq
        if net == 0:
            continue
        items.append(
            {"symbol": sym, "net": round(net), "size": abs(round(net)),
             "side": "buy" if net > 0 else "sell"}
        )
    items.sort(key=lambda x: x["size"], reverse=True)
    return {"ok": True, "items": items}


def _is_mutual_fund(symbol):
    # NEPSE close-ended funds end in MF / a digit (e.g. NMMF1, SBCF). Heuristic.
    return symbol.endswith("MF") or (len(symbol) > 2 and symbol[-1].isdigit() and "MF" in symbol)


def broker_concentration(range_key="today", sector="All"):
    """Per-stock top-3 broker concentration on each side (Broker Concentration)."""
    agg = get_range_aggregate(range_key)
    if not agg:
        return {"ok": False, "rows": []}
    rows = []
    symbols = set(agg["buy"]) | set(agg["sell"])
    for sym in symbols:
        if sector and sector != "All" and agg["sector"].get(sym) != sector:
            continue
        total = _symbol_total(agg, sym)
        if total <= 0:
            continue

        def top3(side_map):
            brokers = sorted(
                side_map.get(sym, {}).items(), key=lambda kv: kv[1][0], reverse=True
            )[:3]
            out = [
                {"broker": b, "pct": round(100.0 * q / total, 2)}
                for b, (q, _a) in brokers
            ]
            return out, round(sum(x["pct"] for x in out), 2)

        buy_top, buy_sum = top3(agg["buy"])
        sell_top, sell_sum = top3(agg["sell"])
        rows.append(
            {
                "symbol": sym,
                "total": round(total),
                "buy": buy_top,
                "buy_sum": buy_sum,
                "sell": sell_top,
                "sell_sum": sell_sum,
            }
        )
    rows.sort(key=lambda r: r["total"], reverse=True)
    return {"ok": True, "rows": rows}


def hotstocks(range_key="today", view="shares", sector="All"):
    """Most-active stocks with their dominant brokers (Hotstocks tab)."""
    agg = get_range_aggregate(range_key)
    if not agg:
        return {"ok": False, "rows": []}
    rows = []
    symbols = set(agg["buy"]) | set(agg["sell"])
    for sym in symbols:
        if sector and sector != "All" and agg["sector"].get(sym) != sector:
            continue
        qty = _symbol_total(agg, sym)
        if qty <= 0:
            continue
        amt = sum(a for _q, a in agg["buy"].get(sym, {}).values())

        def lead(side_map):
            brokers = side_map.get(sym, {})
            if not brokers:
                return None
            b, (q, _a) = max(brokers.items(), key=lambda kv: kv[1][0])
            return {"broker": b, "pct": round(100.0 * q / qty, 2) if qty else 0}

        rows.append(
            {
                "symbol": sym,
                "sector": agg["sector"].get(sym, ""),
                "quantity": round(qty),
                "amount": round(amt, 2),
                "avg_price": round(amt / qty, 2) if qty else 0.0,
                "buyers": len(agg["buy"].get(sym, {})),
                "sellers": len(agg["sell"].get(sym, {})),
                "top_buy": lead(agg["buy"]),
                "top_sell": lead(agg["sell"]),
            }
        )
    rows.sort(key=lambda r: r["amount"] if view == "turnover" else r["quantity"],
              reverse=True)
    return {"ok": True, "rows": rows[:50]}


# ─────────────────────────────────────────────────────────────────────────────
# 90-day trend (bars: floorsheet qty for selected ticker; line: closing price)
# ─────────────────────────────────────────────────────────────────────────────
def trend(symbol, side="buy", days=90):
    """Daily traded quantity (from cached day aggregates) + closing price (DB)."""
    if not symbol:
        return {"ok": False, "points": []}
    latest = get_latest_trading_date()
    if not latest:
        return {"ok": False, "points": []}

    # Closing prices from the local end-of-day table (cheap, authoritative).
    closes = {}
    try:
        from core_analysis.models import NepseDailyStockPrice

        start = datetime.strptime(latest, "%Y-%m-%d").date() - timedelta(days=days)
        qs = (
            NepseDailyStockPrice.objects.filter(symbol=symbol, business_date__gte=start)
            .values_list("business_date", "close_price")
        )
        closes = {bd.isoformat(): float(cp) for bd, cp in qs}
    except Exception:  # pragma: no cover
        closes = {}

    # Quantity bars: only from day aggregates already cached (avoid 90 live pulls).
    start = datetime.strptime(latest, "%Y-%m-%d").date()
    points = []
    for i in range(days):
        d = (start - timedelta(days=i)).isoformat()
        cached = cache.get(f"fs_agg_{d}")
        qty = None
        if cached and cached != FAIL_SENTINEL:
            side_map = cached.get("buy" if side != "sell" else "sell", {})
            qty = round(sum(q for q, _a in side_map.get(symbol, {}).values()))
        close = closes.get(d)
        if qty is None and close is None:
            continue
        points.append({"date": d, "quantity": qty or 0, "close": close})
    points.sort(key=lambda p: p["date"])
    return {"ok": True, "symbol": symbol, "side": side, "points": points}
