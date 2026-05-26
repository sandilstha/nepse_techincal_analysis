import logging
from typing import Dict, Tuple

import numpy as np
import pandas as pd

try:
    import pandas_ta as ta
except Exception:
    ta = None


logger = logging.getLogger(__name__)


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denominator = denominator.replace(0, np.nan)
    return numerator / denominator


def classify_score(score: pd.Series) -> pd.Series:
    conditions = [
        score >= 80,
        (score >= 65) & (score < 80),
        (score >= 50) & (score < 65),
        (score >= 35) & (score < 50),
        score < 35,
    ]
    labels = [
        "Strong Buy",
        "Buy / Accumulate",
        "Neutral Watchlist",
        "Weak",
        "Avoid",
    ]
    return pd.Series(np.select(conditions, labels, default="Neutral Watchlist"), index=score.index)


def calculate_relative_strength(stock_df: pd.DataFrame, nepse_df: pd.DataFrame, lookback: int = 20) -> pd.Series:
    if nepse_df is None or nepse_df.empty:
        return pd.Series(np.nan, index=stock_df.index)

    nepse = nepse_df[["business_date", "close_price_adj"]].copy()
    nepse = nepse.rename(columns={"close_price_adj": "nepse_close"})
    merged = stock_df[["business_date", "close_price_adj"]].merge(nepse, on="business_date", how="left")

    stock_return = merged["close_price_adj"].pct_change(lookback)
    nepse_return = merged["nepse_close"].pct_change(lookback)
    rs = _safe_divide(stock_return, nepse_return)
    return rs.reindex(stock_df.index)


def generate_buy_signal(df: pd.DataFrame) -> pd.Series:
    prev_macd = df["MACD_line"].shift(1)
    prev_signal = df["MACD_signal"].shift(1)
    macd_cross_up = (prev_macd <= prev_signal) & (df["MACD_line"] > df["MACD_signal"])

    vwap = pd.to_numeric(df["VWAP"], errors="coerce")
    close = pd.to_numeric(df["close_price_adj"], errors="coerce")

    return (
        (df["close_price_adj"] > df["SMA_50"]) &
        (df["close_price_adj"] > df["SMA_200"]) &
        (df["SMA_20"] > df["SMA_50"]) &
        (df["RSI_14"].between(50, 70, inclusive="both")) &
        (df["volume"] > df["VOL_SMA_20"]) &
        (df["relative_strength"] > 1.0) &
        (df["supertrend_bullish"]) &
        (macd_cross_up) &
        (close > vwap)
    )


def generate_sell_signal(df: pd.DataFrame) -> pd.Series:
    prev_macd = df["MACD_line"].shift(1)
    prev_signal = df["MACD_signal"].shift(1)
    macd_cross_down = (prev_macd >= prev_signal) & (df["MACD_line"] < df["MACD_signal"])

    close = pd.to_numeric(df["close_price_adj"], errors="coerce")
    atr_stop = pd.to_numeric(df["atr_trailing_stop"], errors="coerce")

    return (
        (df["RSI_14"] > 80) |
        macd_cross_down |
        (df["close_price_adj"] < df["SMA_20"]) |
        (~df["supertrend_bullish"]) |
        (close < atr_stop)
    )


def _build_position_signals(raw_buy: pd.Series, raw_sell: pd.Series) -> Tuple[pd.Series, pd.Series]:
    """
    Convert condition booleans into event signals:
    - buy_signal: True only on entry bar (when flat -> long)
    - sell_signal: True only on exit bar (when long -> flat)
    """
    buy_evt = pd.Series(False, index=raw_buy.index)
    sell_evt = pd.Series(False, index=raw_sell.index)
    in_position = False

    for i in raw_buy.index:
        if not in_position and bool(raw_buy.loc[i]):
            buy_evt.loc[i] = True
            in_position = True
        elif in_position and bool(raw_sell.loc[i]):
            sell_evt.loc[i] = True
            in_position = False

    return buy_evt, sell_evt


def calculate_volume_greed(df: pd.DataFrame) -> pd.Series:
    """
    Calculates a Volume Greed/Fear Meter based on Volume Ratio and Price Action.
    High volume on up days = Greed (Accumulation)
    High volume on down days = Fear (Distribution)
    Low volume = Neutral / Indecision
    """
    conditions = [
        (df["price_change_pct"] > 0) & (df["volume_ratio"] >= 2.0),
        (df["price_change_pct"] > 0) & (df["volume_ratio"] >= 1.2),
        (df["price_change_pct"] < 0) & (df["volume_ratio"] >= 2.0),
        (df["price_change_pct"] < 0) & (df["volume_ratio"] >= 1.2),
    ]
    labels = [
        "Extreme Greed",
        "Greed",
        "Extreme Fear",
        "Fear"
    ]
    return pd.Series(np.select(conditions, labels, default="Neutral"), index=df.index)


def calculate_technical_score(df: pd.DataFrame) -> pd.Series:
    trend_score = (
        np.where(df["close_price_adj"] > df["SMA_200"], 15, 0) +
        np.where(df["close_price_adj"] > df["SMA_50"], 10, 0) +
        np.where(df["SMA_20"] > df["SMA_50"], 10, 0) +
        np.where(df["SMA_50"] > df["SMA_200"], 5, 0)
    )

    momentum_score = np.select(
        [
            df["RSI_14"].between(55, 65, inclusive="both"),
            df["RSI_14"].between(45, 55, inclusive="left"),
            df["RSI_14"].between(65, 70, inclusive="right"),
            df["RSI_14"].between(70, 80, inclusive="right"),
            df["RSI_14"] > 80,
            df["RSI_14"] < 40,
        ],
        [15, 10, 8, 3, -10, -8],
        default=0,
    )

    volume_score = (
        np.where(df["volume"] > df["VOL_SMA_20"], 10, 0) +
        np.where((df["price_change_pct"] > 0) & (df["volume_change_pct"] > 0), 10, 0) +
        np.where((df["price_change_pct"] < 0) & (df["volume_change_pct"] > 0), -12, 0)
    )

    greed_score = np.select(
        [
            df["volume_greed"] == "Extreme Greed",
            df["volume_greed"] == "Greed",
            df["volume_greed"] == "Extreme Fear",
            df["volume_greed"] == "Fear",
        ],
        [15, 5, -15, -5],
        default=0,
    )

    rs_score = np.select(
        [
            df["relative_strength"] > 1.0,
            df["relative_strength"].between(0.9, 1.0, inclusive="both"),
            df["relative_strength"] < 0.9,
        ],
        [10, 3, -10],
        default=0,
    )

    vol_score = np.select(
        [
            df["atr_percent"] < 3,
            df["atr_percent"].between(3, 6, inclusive="both"),
            df["atr_percent"] > 8,
        ],
        [5, 2, -8],
        default=0,
    )

    raw_score = trend_score + momentum_score + volume_score + greed_score + rs_score + vol_score
    return pd.Series(raw_score, index=df.index).clip(0, 100)


def run_imm_scoring_system(
    stock_df: pd.DataFrame,
    nepse_index_df: pd.DataFrame,
    rs_lookback: int = 20,
    atr_length: int = 14,
    rsi_length: int = 14,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
    supertrend_length: int = 10,
    supertrend_multiplier: float = 3.0,
) -> Tuple[Dict, pd.DataFrame]:
    warnings = []

    if ta is None:
        return {"error": "pandas_ta is unavailable.", "warnings": ["Install pandas_ta to run IMM scoring."]}, pd.DataFrame()

    if stock_df is None or stock_df.empty:
        return {"error": "Stock dataframe is empty.", "warnings": ["No stock data available for selected range."]}, pd.DataFrame()

    required = {"business_date", "open_price_adj", "high_price_adj", "low_price_adj", "close_price_adj", "volume"}
    missing = sorted(required.difference(stock_df.columns))
    if missing:
        return {"error": f"Missing required fields: {', '.join(missing)}", "warnings": []}, pd.DataFrame()

    if rs_lookback < 2 or atr_length < 2 or rsi_length < 2 or macd_fast < 1 or macd_slow < 2:
        return {"error": "Invalid indicator settings.", "warnings": ["Lookback settings are too small."]}, pd.DataFrame()
    if macd_fast >= macd_slow:
        return {"error": "Invalid MACD settings.", "warnings": ["MACD fast must be smaller than MACD slow."]}, pd.DataFrame()

    min_bars = max(200, rs_lookback + 5, macd_slow + macd_signal + 5, atr_length + 5, supertrend_length + 5)
    if len(stock_df) < min_bars:
        return {
            "error": f"Insufficient historical data: need at least {min_bars} rows.",
            "warnings": ["Extend date range to stabilize long-term indicators like SMA 200."],
        }, pd.DataFrame()

    df = stock_df.sort_values("business_date").reset_index(drop=True).copy()
    for c in ["open_price_adj", "high_price_adj", "low_price_adj", "close_price_adj", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["SMA_20"] = ta.sma(df["close_price_adj"], length=20)
    df["SMA_50"] = ta.sma(df["close_price_adj"], length=50)
    df["SMA_200"] = ta.sma(df["close_price_adj"], length=200)
    df["RSI_14"] = ta.rsi(df["close_price_adj"], length=rsi_length)
    df["VOL_SMA_20"] = ta.sma(df["volume"], length=20)

    macd_df = ta.macd(df["close_price_adj"], fast=macd_fast, slow=macd_slow, signal=macd_signal)
    if macd_df is None or macd_df.empty:
        return {"error": "MACD calculation failed.", "warnings": []}, pd.DataFrame()
    df["MACD_line"] = macd_df.iloc[:, 0]
    df["MACD_histogram"] = macd_df.iloc[:, 1]
    df["MACD_signal"] = macd_df.iloc[:, 2]

    st = ta.supertrend(
        df["high_price_adj"],
        df["low_price_adj"],
        df["close_price_adj"],
        length=supertrend_length,
        multiplier=supertrend_multiplier,
    )
    if st is None or st.empty:
        return {"error": "Supertrend calculation failed.", "warnings": []}, pd.DataFrame()
    st_col = next((c for c in st.columns if c.startswith("SUPERT_")), None)
    dir_col = next((c for c in st.columns if c.startswith("SUPERTd_")), None)
    if st_col is None or dir_col is None:
        return {"error": "Unexpected Supertrend output format.", "warnings": []}, pd.DataFrame()
    df["Supertrend"] = st[st_col]
    df["supertrend_bullish"] = st[dir_col] > 0

    df["VWAP"] = ta.vwap(df["high_price_adj"], df["low_price_adj"], df["close_price_adj"], df["volume"])
    df["ATR"] = ta.atr(df["high_price_adj"], df["low_price_adj"], df["close_price_adj"], length=atr_length)
    # Normalize indicator dtypes to avoid float-vs-NoneType comparison errors.
    for col in ["SMA_20", "SMA_50", "SMA_200", "RSI_14", "MACD_line", "MACD_signal", "MACD_histogram", "Supertrend", "VWAP", "ATR"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["atr_percent"] = _safe_divide(df["ATR"], df["close_price_adj"]) * 100.0

    df["price_change_pct"] = df["close_price_adj"].pct_change() * 100.0
    df["volume_change_pct"] = df["volume"].pct_change() * 100.0
    
    # Calculate volume ratio and greed meter
    df["volume_ratio"] = _safe_divide(df["volume"], df["VOL_SMA_20"])
    df["volume_breakout"] = df["volume_ratio"] >= 2.0
    df["volume_breakout_status"] = np.where(df["volume_breakout"], "BREAKOUT", "NORMAL")
    df["volume_greed"] = calculate_volume_greed(df)

    df["relative_strength"] = calculate_relative_strength(df, nepse_index_df, lookback=rs_lookback)

    df["atr_trailing_stop"] = df["close_price_adj"].cummax() - (2.0 * df["ATR"])

    df["technical_score"] = calculate_technical_score(df)
    df["score_classification"] = classify_score(df["technical_score"])

    df["trend_alignment"] = (
        (df["close_price_adj"] > df["SMA_50"]) &
        (df["close_price_adj"] > df["SMA_200"]) &
        (df["SMA_20"] > df["SMA_50"]) &
        (df["SMA_50"] > df["SMA_200"])
    )
    df["momentum_alignment"] = df["RSI_14"].between(50, 70, inclusive="both")

    raw_buy = generate_buy_signal(df)
    raw_sell = generate_sell_signal(df)
    df["buy_signal"], df["sell_signal"] = _build_position_signals(raw_buy, raw_sell)

    indicator_cols = [
        "technical_score", "relative_strength", "atr_percent", "SMA_20", "SMA_50", "SMA_200", "RSI_14",
        "MACD_line", "MACD_signal", "MACD_histogram", "Supertrend", "VWAP", "ATR"
    ]
    nan_count = int(df[indicator_cols].isna().sum().sum())
    if nan_count > 0:
        warnings.append("NaN values detected in warmup periods; early rows may not be signal-eligible.")

    output_cols = [
        "business_date",
        "close_price_adj",
        "technical_score",
        "score_classification",
        "buy_signal",
        "sell_signal",
        "relative_strength",
        "atr_percent",
        "volume_ratio",
        "volume_breakout",
        "volume_breakout_status",
        "volume_greed",
        "trend_alignment",
        "momentum_alignment",
        "MACD_line",
        "MACD_signal",
        "MACD_histogram",
        "Supertrend",
        "VWAP",
        "ATR",
    ]

    out = df[output_cols].copy()
    latest = out.iloc[-1]

    metrics = {
        "warnings": warnings,
        "latest_score": float(latest["technical_score"]) if pd.notna(latest["technical_score"]) else None,
        "latest_classification": str(latest["score_classification"]),
        "latest_volume_greed": str(latest["volume_greed"]),
        "latest_volume_ratio": float(latest["volume_ratio"]) if pd.notna(latest["volume_ratio"]) else None,
        "latest_buy_signal": bool(latest["buy_signal"]) if pd.notna(latest["buy_signal"]) else False,
        "latest_sell_signal": bool(latest["sell_signal"]) if pd.notna(latest["sell_signal"]) else False,
        "latest_relative_strength": float(latest["relative_strength"]) if pd.notna(latest["relative_strength"]) else None,
        "latest_atr_percent": float(latest["atr_percent"]) if pd.notna(latest["atr_percent"]) else None,
        "buy_count": int(out["buy_signal"].fillna(False).sum()),
        "sell_count": int(out["sell_signal"].fillna(False).sum()),
    }

    logger.info(
        "IMM scoring completed | rows=%s latest_score=%s class=%s",
        len(out), metrics["latest_score"], metrics["latest_classification"],
    )

    return metrics, out
