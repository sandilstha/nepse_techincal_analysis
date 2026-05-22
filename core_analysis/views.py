from decimal import Decimal

import numpy as np
import pandas as pd
import requests
from django.contrib import messages
from django.core.cache import cache
from django.db.models import OuterRef, Q, Subquery
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.management import call_command
from django.views.decorators.http import require_POST

from core_analysis.models import CompanyProfile, NepseDailyStockPrice, NepseMarketIndex, StockPriceAdjustment
from core_analysis.services.CCI import run_cci_long_only_simulation
from core_analysis.services.IMM import run_imm_scoring_system
from core_analysis.services.msv_strategy import run_msv_long_only_simulation
from core_analysis.services.moving_average import run_ema_50_200_long_only_simulation
from core_analysis.services.RSI_SMA import run_rsi_sma_long_only_simulation
from core_analysis.services.strategy_tester import run_t3ma_macd_ribbon_simulation

@require_POST
def trigger_sync_and_calculate(request):
    try:
        call_command("sync_and_calculate")
        messages.success(request, "Market Data and Signals sync_and_calculate successfully generated!")
    except Exception as e:
        messages.error(request, f"Command execution failed: {str(e)}")
    return redirect("core_dashboard")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default, minimum=None):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    if minimum is not None and parsed < minimum:
        return default
    return parsed


def _get_symbol_lists():
    """
    FIX #1 — Cache symbol lists for 5 minutes so the two full-table scans
    (CompanyProfile + NepseMarketIndex) do NOT run on every page load.
    Cache is invalidated automatically on timeout; call cache.delete() in any
    view that adds/removes symbols if you need instant consistency.
    """
    CACHE_KEY = "nepse_symbol_lists"
    cached = cache.get(CACHE_KEY)
    if cached:
        return cached["companies"], cached["indices"]

    db_companies = sorted(
        CompanyProfile.objects.values_list("symbol", flat=True).distinct()
    )
    db_indices = sorted(
        NepseMarketIndex.objects.values_list("sector_name", flat=True).distinct()
    )
    cache.set(CACHE_KEY, {"companies": db_companies, "indices": db_indices}, timeout=300)
    return db_companies, db_indices


def _build_standard_dataframe(symbol, start_date, end_date):
    """
    OPTIMIZED: Normalizes data from StockPriceAdjustment and NepseMarketIndex 
    into an identical DataFrame with strict date filtering applied at the database level.
    Returns ONLY the data within the user-specified date range.
    """
    symbol = (symbol or "").strip()
    symbol_upper = symbol.upper()

    valid_sectors = [
        "BANKING SUBINDEX", "DEVELOPMENT BANK INDEX", "FINANCE INDEX", "FLOAT INDEX",
        "HOTELS AND TOURISM INDEX", "HYDROPOWER INDEX", "INVESTMENT INDEX", "LIFE INSURANCE",
        "MANUFACTURING AND PROCESSING", "MICROFINANCE INDEX", "MUTUAL FUND", "NEPSE INDEX",
        "NON LIFE INSURANCE", "OTHERS INDEX", "SENSITIVE FLOAT INDEX", "SENSITIVE INDEX", "TRADING INDEX"
    ]
    empty_schema = pd.DataFrame(columns=[
        "business_date", "open_price_adj", "high_price_adj", "low_price_adj", "close_price_adj", "volume"
    ])

    if symbol_upper in valid_sectors:
        # OPTIMIZED: Only select required columns and apply date filter at DB level
        qs = NepseMarketIndex.objects.filter(
            sector_name__exact=symbol_upper,
            business_date__gte=start_date,
            business_date__lte=end_date,
        ).values(
            "business_date", "open_index", "high_index", "low_index", "close_index", "turnover_volume"
        ).order_by("business_date")
        
        data = list(qs)
        if not data:
            return empty_schema
        df = pd.DataFrame(data)
        df.rename(columns={
            "open_index":  "open_price_adj",
            "high_index":  "high_price_adj",
            "low_index":   "low_price_adj",
            "close_index": "close_price_adj",
            "turnover_volume": "volume",
        }, inplace=True)
    else:
        # OPTIMIZED: Only select required columns and apply date filter at DB level
        qs = StockPriceAdjustment.objects.filter(
            company_id__exact=symbol_upper,
            business_date__gte=start_date,
            business_date__lte=end_date,
        ).values(
            "business_date", "open_price_adj", "high_price_adj",
            "low_price_adj", "close_price_adj",
        ).order_by("business_date")
        
        data = list(qs)
        if not data:
            return empty_schema
        df = pd.DataFrame(data)
        volume_qs = NepseDailyStockPrice.objects.filter(
            symbol__exact=symbol_upper,
            business_date__gte=start_date,
            business_date__lte=end_date,
        ).values("business_date", "total_traded_quantity")
        volume_df = pd.DataFrame(list(volume_qs))
        if not volume_df.empty:
            volume_df.rename(columns={"total_traded_quantity": "volume"}, inplace=True)
            df = df.merge(volume_df, on="business_date", how="left")
        else:
            df["volume"] = np.nan

    # Convert data types
    df["business_date"] = pd.to_datetime(df["business_date"])
    for col in ["open_price_adj", "high_price_adj", "low_price_adj", "close_price_adj"]:
        df[col] = df[col].astype(float)
    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    
    # CRITICAL: Ensure dataframe only contains data within the specified date range
    # This prevents simulation functions from processing extra data
    df = df[
        (df["business_date"] >= pd.to_datetime(start_date)) & 
        (df["business_date"] <= pd.to_datetime(end_date))
    ].reset_index(drop=True)
    
    return df


# ── Symbol autocomplete API (used by the JS search boxes) ────────────────────

def symbol_autocomplete_view(request):
    """
    OPTIMIZED: Lightweight JSON endpoint for the search-as-you-type dropdown.
    The template no longer renders <option> for every symbol; instead JS calls
    this endpoint and builds the dropdown on demand, so the initial HTML
    response is drastically smaller.

    Usage: GET /dashboard/symbols/?q=nabil
    Returns: {"results": [{"value": "NABIL", "label": "NABIL - Nabil Bank", "type": "company"}, ...]}
    """
    q_raw = request.GET.get("q", "").strip()
    q = q_raw.upper()
    if not q:
        return JsonResponse({"results": []})

    latest_stock_price_sq = (
        StockPriceAdjustment.objects
        .filter(company_id=OuterRef("symbol"))
        .order_by("-business_date")
    )
    latest_stock_date_sq = (
        StockPriceAdjustment.objects
        .filter(company_id=OuterRef("symbol"))
        .order_by("-business_date")
    )

    # Match by ticker prefix first, then by company name.
    company_rows = list(
        CompanyProfile.objects.filter(
            Q(symbol__istartswith=q_raw) | Q(security_name__icontains=q_raw)
        )
        .annotate(
            latest_close=Subquery(latest_stock_price_sq.values("close_price_adj")[:1]),
            latest_date=Subquery(latest_stock_date_sq.values("business_date")[:1]),
        )
        .values("symbol", "security_name", "latest_close", "latest_date")
        .order_by("symbol")[:40]
    )
    index_rows = list(
        NepseMarketIndex.objects.filter(sector_name__icontains=q)
        .values_list("sector_name", flat=True)
        .distinct()
        .order_by("sector_name")[:10]
    )

    results = []
    seen = set()

    for row in company_rows:
        symbol = (row.get("symbol") or "").strip().upper()
        name = (row.get("security_name") or "").strip()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        label = f"{symbol} - {name}" if name else symbol
        latest_close = row.get("latest_close")
        latest_date = row.get("latest_date")
        results.append({
            "value": symbol,
            "label": label,
            "type": "company",
            "latest_close": float(latest_close) if latest_close is not None else None,
            "latest_date": latest_date.isoformat() if latest_date else None,
        })

    for index_name in index_rows:
        index_value = (index_name or "").strip().upper()
        if not index_value or index_value in seen:
            continue
        seen.add(index_value)
        results.append({"value": index_value, "label": index_name, "type": "index"})

    return JsonResponse({"results": results})


# ── Main dashboard ────────────────────────────────────────────────────────────

def crud_dashboard_view(request):
    """
    OPTIMIZED: Consolidated Dashboard Controller with performance improvements.

    Performance improvements:
      1. Symbol lists are cached for 5 min (no full-table scan on every GET).
      2. Inventory queryset is only fetched when active_tab == 'inventory'.
      3. Only the active strategy tab runs its backtest computation.
      4. Date filtering is strictly enforced at the database and dataframe levels.
      5. Empty symbol lists are now passed to template (autocomplete handles search).
    """
    g = request.GET
    active_tab = g.get("active_tab", "inventory")

    # OPTIMIZED: Pass empty lists - autocomplete will handle search
    db_companies, db_indices = [], []

    # OPTIMIZED: inventory rows only when needed
    queryset = []
    if active_tab == "inventory":
        queryset = list(
            StockPriceAdjustment.objects
            .select_related("company")
            .order_by("-business_date")[:100]
        )

    # Initialise result vectors
    backtest_metrics = ema_backtest_metrics = cci_backtest_metrics = rsi_backtest_metrics = msv_backtest_metrics = imm_backtest_metrics = None
    completed_trades = ema_completed_trades = cci_completed_trades = rsi_completed_trades = msv_completed_trades = []
    msv_indicator_rows = []
    imm_indicator_rows = []
    imm_event_rows = []

    # Per-tab symbols
    selected_symbol     = g.get("backtest_symbol",     "").upper().strip()
    ema_selected_symbol = g.get("ema_backtest_symbol", "").upper().strip()
    cci_selected_symbol = g.get("cci_backtest_symbol", "").upper().strip()
    rsi_selected_symbol = g.get("rsi_backtest_symbol", "").upper().strip()
    msv_selected_symbol = g.get("msv_backtest_symbol", "").upper().strip()
    imm_selected_symbol = g.get("imm_backtest_symbol", "").upper().strip()

    # Per-tab independent date ranges
    t3_from  = g.get("t3_from_date",  g.get("from_date", "")).strip()
    t3_to    = g.get("t3_to_date",    g.get("to_date",   "")).strip()
    ema_from = g.get("ema_from_date", g.get("from_date", "")).strip()
    ema_to   = g.get("ema_to_date",   g.get("to_date",   "")).strip()
    cci_from = g.get("cci_from_date", g.get("from_date", "")).strip()
    cci_to   = g.get("cci_to_date",   g.get("to_date",   "")).strip()
    rsi_from = g.get("rsi_from_date", g.get("from_date", "")).strip()
    rsi_to   = g.get("rsi_to_date",   g.get("to_date",   "")).strip()
    msv_from = g.get("msv_from_date", g.get("from_date", "")).strip()
    msv_to   = g.get("msv_to_date",   g.get("to_date",   "")).strip()
    imm_from = g.get("imm_from_date", g.get("from_date", "")).strip()
    imm_to   = g.get("imm_to_date",   g.get("to_date",   "")).strip()

    # ── TAB 2: T3MA ──────────────────────────────────────────────────────────
    if selected_symbol and active_tab == "backtest":
        if not (t3_from and t3_to):
            backtest_metrics = {"error": "Please select both From Date and To Date."}
        else:
            df = _build_standard_dataframe(selected_symbol, t3_from, t3_to)
            if df.empty:
                backtest_metrics = {"error": f"No price data found for '{selected_symbol}' in the selected date range."}
            else:
                backtest_metrics, trades_df = run_t3ma_macd_ribbon_simulation(df)
                if isinstance(backtest_metrics, dict) and "error" not in backtest_metrics and not trades_df.empty:
                    trades_df["entry_date"] = pd.to_datetime(trades_df["entry_date"]).dt.strftime("%Y-%m-%d")
                    trades_df["exit_date"]  = pd.to_datetime(trades_df["exit_date"]).dt.strftime("%Y-%m-%d")
                    completed_trades = trades_df.to_dict(orient="records")

    # ── TAB 3: EMA 50/200 ────────────────────────────────────────────────────
    if ema_selected_symbol and active_tab == "ema_backtest":
        if not (ema_from and ema_to):
            ema_backtest_metrics = {"error": "Please select both From Date and To Date."}
        else:
            df = _build_standard_dataframe(ema_selected_symbol, ema_from, ema_to)
            if df.empty:
                ema_backtest_metrics = {"error": f"No price data found for '{ema_selected_symbol}' in the selected date range."}
            else:
                ema_backtest_metrics, ema_trades_df = run_ema_50_200_long_only_simulation(
                    df,
                    take_profit_pct=_safe_float(g.get("ema_take_profit_pct", 15), 15.0),
                    stop_loss_pct=_safe_float(g.get("ema_stop_loss_pct", 7), 7.0),
                    fast_ema_period=_safe_int(g.get("ema_fast_period", 50), 50, minimum=1),
                    slow_ema_period=_safe_int(g.get("ema_slow_period", 200), 200, minimum=1),
                )
                if isinstance(ema_backtest_metrics, dict) and "error" not in ema_backtest_metrics and not ema_trades_df.empty:
                    ema_trades_df["entry_date"] = pd.to_datetime(ema_trades_df["entry_date"]).dt.strftime("%Y-%m-%d")
                    ema_trades_df["exit_date"]  = pd.to_datetime(ema_trades_df["exit_date"]).dt.strftime("%Y-%m-%d")
                    ema_completed_trades = ema_trades_df.to_dict(orient="records")

    # ── TAB 4: CCI ───────────────────────────────────────────────────────────
    if cci_selected_symbol and active_tab == "cci_backtest":
        if not (cci_from and cci_to):
            cci_backtest_metrics = {"error": "Please select both From Date and To Date."}
        else:
            df = _build_standard_dataframe(cci_selected_symbol, cci_from, cci_to)
            if df.empty:
                cci_backtest_metrics = {"error": f"No price data found for '{cci_selected_symbol}' in the selected date range."}
            else:
                cci_backtest_metrics, cci_trades_df = run_cci_long_only_simulation(
                    df,
                    cci_period=_safe_int(g.get("cci_period", 20), 20, minimum=1),
                    adx_threshold=_safe_float(g.get("cci_adx_threshold", 25), 25.0),
                    volume_avg_period=_safe_int(g.get("cci_volume_avg_period", 20), 20, minimum=1),
                    volume_multiplier=_safe_float(g.get("cci_volume_multiplier", 1.5), 1.5),
                )
                if isinstance(cci_backtest_metrics, dict) and "error" not in cci_backtest_metrics and not cci_trades_df.empty:
                    cci_trades_df["entry_date"] = pd.to_datetime(cci_trades_df["entry_date"]).dt.strftime("%Y-%m-%d")
                    cci_trades_df["exit_date"]  = pd.to_datetime(cci_trades_df["exit_date"]).dt.strftime("%Y-%m-%d")
                    cci_completed_trades = cci_trades_df.to_dict(orient="records")

    # ── TAB 5: RSI/SMA ───────────────────────────────────────────────────────
    if rsi_selected_symbol and active_tab == "rsi_backtest":
        if not (rsi_from and rsi_to):
            rsi_backtest_metrics = {"error": "Please select both From Date and To Date."}
        else:
            df = _build_standard_dataframe(rsi_selected_symbol, rsi_from, rsi_to)
            if df.empty:
                rsi_backtest_metrics = {"error": f"No price data found for '{rsi_selected_symbol}' in the selected date range."}
            else:
                rsi_backtest_metrics, rsi_trades_df = run_rsi_sma_long_only_simulation(
                    df,
                    rsi_length=_safe_int(g.get("rsi_length", 14), 14, minimum=1),
                    rsi_sma_length=_safe_int(g.get("rsi_sma_length", 9), 9, minimum=1),
                )
                if isinstance(rsi_backtest_metrics, dict) and "error" not in rsi_backtest_metrics and not rsi_trades_df.empty:
                    rsi_trades_df["entry_date"] = pd.to_datetime(rsi_trades_df["entry_date"]).dt.strftime("%Y-%m-%d")
                    rsi_trades_df["exit_date"]  = pd.to_datetime(rsi_trades_df["exit_date"]).dt.strftime("%Y-%m-%d")
                    rsi_completed_trades = rsi_trades_df.to_dict(orient="records")

    # TAB 6: MACD + Supertrend + VWAP + ATR + RVOL (MSV)
    if msv_selected_symbol and active_tab == "msv_backtest":
        if not (msv_from and msv_to):
            msv_backtest_metrics = {"error": "Please select both From Date and To Date."}
        else:
            df = _build_standard_dataframe(msv_selected_symbol, msv_from, msv_to)
            if df.empty:
                msv_backtest_metrics = {"error": f"No price data found for '{msv_selected_symbol}' in the selected date range."}
            else:
                msv_backtest_metrics, msv_trades_df, msv_indicator_df = run_msv_long_only_simulation(
                    df,
                    macd_fast=_safe_int(g.get("msv_macd_fast", 12), 12, minimum=1),
                    macd_slow=_safe_int(g.get("msv_macd_slow", 26), 26, minimum=2),
                    macd_signal=_safe_int(g.get("msv_macd_signal", 9), 9, minimum=1),
                    atr_length=_safe_int(g.get("msv_atr_length", 14), 14, minimum=2),
                    atr_multiplier=_safe_float(g.get("msv_atr_multiplier", 2.0), 2.0),
                    rvol_period=_safe_int(g.get("msv_rvol_period", 20), 20, minimum=2),
                    rvol_threshold=_safe_float(g.get("msv_rvol_threshold", 1.5), 1.5),
                    supertrend_length=_safe_int(g.get("msv_supertrend_length", 10), 10, minimum=2),
                    supertrend_multiplier=_safe_float(g.get("msv_supertrend_multiplier", 3.0), 3.0),
                )
                if isinstance(msv_backtest_metrics, dict) and "error" not in msv_backtest_metrics:
                    if not msv_trades_df.empty:
                        msv_trades_df["entry_date"] = pd.to_datetime(msv_trades_df["entry_date"]).dt.strftime("%Y-%m-%d")
                        msv_trades_df["exit_date"] = pd.to_datetime(msv_trades_df["exit_date"]).dt.strftime("%Y-%m-%d")
                        msv_completed_trades = msv_trades_df.to_dict(orient="records")
                    if not msv_indicator_df.empty:
                        msv_indicator_df["business_date"] = pd.to_datetime(msv_indicator_df["business_date"]).dt.strftime("%Y-%m-%d")
                        msv_indicator_rows = msv_indicator_df.tail(150).to_dict(orient="records")

    # TAB 7: IMM institutional technical scoring
    if imm_selected_symbol and active_tab == "imm_backtest":
        if not (imm_from and imm_to):
            imm_backtest_metrics = {"error": "Please select both From Date and To Date."}
        else:
            stock_df = _build_standard_dataframe(imm_selected_symbol, imm_from, imm_to)
            nepse_df = _build_standard_dataframe("NEPSE INDEX", imm_from, imm_to)
            if stock_df.empty:
                imm_backtest_metrics = {"error": f"No price data found for '{imm_selected_symbol}' in the selected date range."}
            elif nepse_df.empty:
                imm_backtest_metrics = {"error": "No NEPSE INDEX data found for the selected date range."}
            else:
                imm_backtest_metrics, imm_df = run_imm_scoring_system(
                    stock_df=stock_df,
                    nepse_index_df=nepse_df,
                    rs_lookback=_safe_int(g.get("imm_rs_lookback", 20), 20, minimum=2),
                    atr_length=_safe_int(g.get("imm_atr_length", 14), 14, minimum=2),
                    rsi_length=_safe_int(g.get("imm_rsi_length", 14), 14, minimum=2),
                    macd_fast=_safe_int(g.get("imm_macd_fast", 12), 12, minimum=1),
                    macd_slow=_safe_int(g.get("imm_macd_slow", 26), 26, minimum=2),
                    macd_signal=_safe_int(g.get("imm_macd_signal", 9), 9, minimum=1),
                    supertrend_length=_safe_int(g.get("imm_supertrend_length", 10), 10, minimum=2),
                    supertrend_multiplier=_safe_float(g.get("imm_supertrend_multiplier", 3.0), 3.0),
                )
                if isinstance(imm_backtest_metrics, dict) and "error" not in imm_backtest_metrics and not imm_df.empty:
                    imm_df["business_date"] = pd.to_datetime(imm_df["business_date"]).dt.strftime("%Y-%m-%d")
                    imm_indicator_rows = imm_df.tail(150).to_dict(orient="records")
                    imm_event_rows = imm_df[(imm_df["buy_signal"] == True) | (imm_df["sell_signal"] == True)].tail(120).to_dict(orient="records")

    return render(request, "core_analysis/crud.html", {
        "records": queryset,

        # OPTIMIZED: Empty symbol lists (autocomplete handles search)
        "company_choices": db_companies,
        "index_choices":   db_indices,

        # T3MA
        "backtest_metrics":  backtest_metrics,
        "completed_trades":  completed_trades,
        "selected_symbol":   selected_symbol,
        "t3_from_date":      t3_from,
        "t3_to_date":        t3_to,

        # EMA
        "ema_backtest_metrics": ema_backtest_metrics,
        "ema_completed_trades": ema_completed_trades,
        "ema_selected_symbol":  ema_selected_symbol,
        "ema_from_date":        ema_from,
        "ema_to_date":          ema_to,

        # CCI
        "cci_backtest_metrics": cci_backtest_metrics,
        "cci_completed_trades": cci_completed_trades,
        "cci_selected_symbol":  cci_selected_symbol,
        "cci_from_date":        cci_from,
        "cci_to_date":          cci_to,

        # RSI
        "rsi_backtest_metrics": rsi_backtest_metrics,
        "rsi_completed_trades": rsi_completed_trades,
        "rsi_selected_symbol":  rsi_selected_symbol,
        "rsi_from_date":        rsi_from,
        "rsi_to_date":          rsi_to,
        "msv_backtest_metrics": msv_backtest_metrics,
        "msv_completed_trades": msv_completed_trades,
        "msv_indicator_rows":   msv_indicator_rows,
        "msv_selected_symbol":  msv_selected_symbol,
        "msv_from_date":        msv_from,
        "msv_to_date":          msv_to,
        "imm_backtest_metrics": imm_backtest_metrics,
        "imm_indicator_rows":   imm_indicator_rows,
        "imm_event_rows":       imm_event_rows,
        "imm_selected_symbol":  imm_selected_symbol,
        "imm_from_date":        imm_from,
        "imm_to_date":          imm_to,

        # EMA parameters
        "ema_take_profit_pct": g.get("ema_take_profit_pct", "15"),
        "ema_stop_loss_pct":   g.get("ema_stop_loss_pct", "7"),
        "ema_fast_period":     g.get("ema_fast_period", "50"),
        "ema_slow_period":     g.get("ema_slow_period", "200"),

        # CCI parameters
        "cci_period":        g.get("cci_period", "20"),
        "cci_adx_threshold": g.get("cci_adx_threshold", "25"),
        "cci_volume_avg_period": g.get("cci_volume_avg_period", "20"),
        "cci_volume_multiplier": g.get("cci_volume_multiplier", "1.5"),

        # RSI parameters
        "rsi_length":     g.get("rsi_length", "14"),
        "rsi_sma_length": g.get("rsi_sma_length", "9"),
        "msv_macd_fast": g.get("msv_macd_fast", "12"),
        "msv_macd_slow": g.get("msv_macd_slow", "26"),
        "msv_macd_signal": g.get("msv_macd_signal", "9"),
        "msv_atr_length": g.get("msv_atr_length", "14"),
        "msv_atr_multiplier": g.get("msv_atr_multiplier", "2.0"),
        "msv_rvol_period": g.get("msv_rvol_period", "20"),
        "msv_rvol_threshold": g.get("msv_rvol_threshold", "1.5"),
        "msv_supertrend_length": g.get("msv_supertrend_length", "10"),
        "msv_supertrend_multiplier": g.get("msv_supertrend_multiplier", "3.0"),
        "imm_rs_lookback": g.get("imm_rs_lookback", "20"),
        "imm_atr_length": g.get("imm_atr_length", "14"),
        "imm_rsi_length": g.get("imm_rsi_length", "14"),
        "imm_macd_fast": g.get("imm_macd_fast", "12"),
        "imm_macd_slow": g.get("imm_macd_slow", "26"),
        "imm_macd_signal": g.get("imm_macd_signal", "9"),
        "imm_supertrend_length": g.get("imm_supertrend_length", "10"),
        "imm_supertrend_multiplier": g.get("imm_supertrend_multiplier", "3.0"),

        "active_tab": active_tab,
    })


# ── CRUD handlers (unchanged) ─────────────────────────────────────────────────

def crud_operations_handler(request):
    """CREATE & UPDATE operations handler via HTML Form Actions."""
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create":
            company_symbol = request.POST.get("company").upper()
            company_profile, _ = CompanyProfile.objects.get_or_create(
                symbol=company_symbol,
                defaults={"security_name": f"Manual profile reference {company_symbol}"},
            )
            StockPriceAdjustment.objects.create(
                external_id=request.POST.get("external_id"),
                business_date=request.POST.get("business_date"),
                company=company_profile,
                security_id=request.POST.get("security_id"),
                open_price=0, high_price=0, low_price=0, close_price=0,
                open_price_adj=0, high_price_adj=0, low_price_adj=0,
                close_price_adj=request.POST.get("close_price_adj"),
                adjustment_factor=1.0,
            )
            # Invalidate symbol cache so new company appears in dropdowns
            cache.delete("nepse_symbol_lists")

        elif action == "update":
            record_id = request.POST.get("record_id")
            record = get_object_or_404(StockPriceAdjustment, id=record_id)
            record.close_price_adj = request.POST.get("close_price_adj")
            record.save(update_fields=["close_price_adj"])

    return redirect("crud_dashboard")


@require_POST
def crud_delete_handler(request, pk):
    """DELETE operation route (POST only, CSRF-protected)."""
    record = get_object_or_404(StockPriceAdjustment, id=pk)
    record.delete()
    return redirect("crud_dashboard")


def trigger_daily_api_sync_view(request):
    """
    On-demand daily sync engine endpoint: fetches the latest page from the
    stock prices endpoint and skips already-existing rows.
    """
    session = requests.Session()
    stock_url = "http://192.168.1.35:8000/api/nepse-data/api/stock-prices/?format=json"

    records_saved = 0
    seen_api_ids = set()

    def clean_dec(val):
        if val is None:
            return Decimal("0.00")
        val_str = str(val).strip()
        if val_str == "" or val_str.lower() in ["none", "null", "nan", "-"]:
            return Decimal("0.00")
        try:
            return Decimal(val_str)
        except Exception:
            return Decimal("0.00")

    try:
        response = session.get(stock_url, timeout=15)
        if response.status_code == 200:
            payload = response.json()
            results = payload.get("results", [])

            stock_instances = []
            for item in results:
                current_id = item["id"]
                if current_id in seen_api_ids:
                    continue
                if NepseDailyStockPrice.objects.filter(api_id=current_id).exists():
                    continue

                stock_instances.append(NepseDailyStockPrice(
                    api_id=current_id,
                    business_date=item["business_date"],
                    security_id=item["security_id"],
                    symbol=item["symbol"],
                    security_name=item["security_name"],
                    open_price=clean_dec(item["open_price"]),
                    high_price=clean_dec(item["high_price"]),
                    low_price=clean_dec(item["low_price"]),
                    close_price=clean_dec(item["close_price"]),
                    previous_close=clean_dec(item["previous_close"]),
                    average_traded_price=clean_dec(item["average_traded_price"]),
                    total_traded_quantity=item["total_traded_quantity"],
                    total_traded_value=clean_dec(item["total_traded_value"]),
                    total_trades=item["total_trades"],
                    market_capitalization=clean_dec(item["market_capitalization"]),
                    fifty_two_week_high=clean_dec(item["fifty_two_week_high"]),
                    fifty_two_week_low=clean_dec(item["fifty_two_week_low"]),
                    last_updated_time=item["last_updated_time"],
                ))
                seen_api_ids.add(current_id)

            if stock_instances:
                NepseDailyStockPrice.objects.bulk_create(stock_instances, ignore_conflicts=True)
                records_saved = len(stock_instances)
                # Invalidate symbol cache after a sync that may have added new symbols
                cache.delete("nepse_symbol_lists")

        messages.success(request, f"Daily sync executed successfully. Processed {records_saved} new market rows.")
    except Exception as e:
        messages.error(request, f"Daily pipeline sync interrupted: {str(e)}")

    return redirect("crud_dashboard")
