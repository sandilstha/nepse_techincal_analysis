import pandas as pd
import numpy as np


def run_rrg_simulation(
    stock_df: pd.DataFrame,
    benchmark_df: pd.DataFrame,
    lookback: int = 14
):
    """
    Calculates Relative Rotation Graph (RRG) coordinates (RS-Ratio and RS-Momentum)
    for a given stock against a benchmark (typically NEPSE INDEX).
    
    RRG Quadrants:
    - Leading (Green): RS-Ratio > 100, RS-Momentum > 100
    - Weakening (Yellow): RS-Ratio > 100, RS-Momentum < 100
    - Lagging (Red): RS-Ratio < 100, RS-Momentum < 100
    - Improving (Blue): RS-Ratio < 100, RS-Momentum > 100
    """
    if stock_df.empty or benchmark_df.empty:
        return {"error": "Missing data for RRG calculation."}, pd.DataFrame()
    if lookback < 2:
        return {"error": "RRG lookback must be at least 2 bars."}, pd.DataFrame()

    required_cols = {"business_date", "close_price_adj"}
    if not required_cols.issubset(stock_df.columns) or not required_cols.issubset(benchmark_df.columns):
        return {"error": "Input data missing required columns."}, pd.DataFrame()

    stock = _prepare_price_frame(stock_df, "stock_close")
    bench = _prepare_price_frame(benchmark_df, "bench_close")
    
    df = pd.merge(stock, bench, on="business_date", how="inner").sort_values("business_date").reset_index(drop=True)
    df = df[(df["stock_close"] > 0) & (df["bench_close"] > 0)].copy()
    source_bars = int(len(stock))
    benchmark_bars = int(len(bench))
    matched_bars = int(len(df))
    
    if len(df) < lookback * 2:
        return {
            "error": (
                f"Insufficient overlapping data for RRG({lookback}). "
                f"Need at least {lookback * 2} shared trading dates; found {matched_bars}."
            ),
            "source_bars": source_bars,
            "benchmark_bars": benchmark_bars,
            "matched_bars": matched_bars,
            "lookback": lookback,
        }, pd.DataFrame()

    # 1. Calculate Relative Strength (RS)
    df["RS"] = (df["stock_close"] / df["bench_close"]) * 100.0

    # 2. RS-Ratio: z-score of RS against its own rolling window, centred at 100
    #    (the standard public JdK approximation). The previous RS/SMA×100 form
    #    made the distance from 100 scale with each symbol's OWN volatility, so
    #    on a multi-symbol chart the volatile series always plotted farther out
    #    than the placid ones even with equal relative trend — z-scoring puts
    #    every symbol on the same footing, which is the point of an RRG.
    #    A locally flat RS window (std == 0) means "exactly on trend" → 100.
    df["RS_Ratio"] = 100.0 + _z(df["RS"], lookback)

    # 3. RS-Momentum: the same normalization applied to RS-Ratio itself —
    #    above its own recent mean = relative strength still accelerating.
    df["RS_Momentum"] = 100.0 + _z(df["RS_Ratio"], lookback)

    # Determine quadrant
    conditions = [
        (df["RS_Ratio"] >= 100) & (df["RS_Momentum"] >= 100),
        (df["RS_Ratio"] >= 100) & (df["RS_Momentum"] < 100),
        (df["RS_Ratio"] < 100) & (df["RS_Momentum"] < 100),
        (df["RS_Ratio"] < 100) & (df["RS_Momentum"] >= 100),
    ]
    labels = ["Leading", "Weakening", "Lagging", "Improving"]
    df["Quadrant"] = np.select(conditions, labels, default="Unknown")

    out_df = df.dropna().copy()
    if out_df.empty:
        return {"error": "Not enough data points after calculating RRG."}, pd.DataFrame()

    latest = out_df.iloc[-1]
    previous = out_df.iloc[-2] if len(out_df) > 1 else latest

    # Rotation context: how long the symbol has been in its current quadrant
    # and where it rotated in from — "just entered Leading" is the actionable
    # RRG event, and the quadrant label alone doesn't carry it.
    quadrants = out_df["Quadrant"].tolist()
    bars_in_quadrant = 1
    for q in reversed(quadrants[:-1]):
        if q != quadrants[-1]:
            break
        bars_in_quadrant += 1
    rotated_from = (
        quadrants[-bars_in_quadrant - 1] if bars_in_quadrant < len(quadrants) else None
    )

    metrics = {
        "bars_in_quadrant": int(bars_in_quadrant),
        "rotated_from": rotated_from,
        "latest_rs_ratio": round(float(latest["RS_Ratio"]), 2),
        "latest_rs_momentum": round(float(latest["RS_Momentum"]), 2),
        "latest_quadrant": latest["Quadrant"],
        "rs_ratio_delta": round(float(latest["RS_Ratio"] - previous["RS_Ratio"]), 2),
        "rs_momentum_delta": round(float(latest["RS_Momentum"] - previous["RS_Momentum"]), 2),
        "data_points": int(len(out_df)),
        "source_bars": source_bars,
        "benchmark_bars": benchmark_bars,
        "matched_bars": matched_bars,
        "lookback": lookback,
    }

    return metrics, out_df


def _z(series: pd.Series, lookback: int) -> pd.Series:
    """Rolling z-score of ``series`` over ``lookback`` bars.

    std == 0 (a locally flat window) is treated as zero deviation rather than
    NaN so a symbol tracking its trend exactly stays plotted at the centre
    instead of silently dropping out of the chart.
    """
    mean = series.rolling(window=lookback).mean()
    std = series.rolling(window=lookback).std(ddof=0)
    z = (series - mean) / std.replace(0, np.nan)
    # Flat window (std 0) → deviation 0; keep warmup NaNs (mean still NaN).
    return z.where(std != 0, 0.0).where(mean.notna())


def _prepare_price_frame(source_df: pd.DataFrame, close_column_name: str) -> pd.DataFrame:
    df = source_df[["business_date", "close_price_adj"]].copy()
    df["business_date"] = pd.to_datetime(df["business_date"], errors="coerce")
    df["close_price_adj"] = pd.to_numeric(df["close_price_adj"], errors="coerce")
    df = df.dropna(subset=["business_date", "close_price_adj"])
    df = df.sort_values("business_date").drop_duplicates(subset=["business_date"], keep="last")
    return df.rename(columns={"close_price_adj": close_column_name})
