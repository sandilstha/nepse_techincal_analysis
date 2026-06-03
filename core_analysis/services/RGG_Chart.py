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
    
    if len(df) < lookback * 2:
        return {"error": f"Insufficient data for RRG({lookback}). Need at least {lookback*2} bars."}, pd.DataFrame()

    # 1. Calculate Relative Strength (RS)
    df["RS"] = (df["stock_close"] / df["bench_close"]) * 100.0
    
    # 2. RS-Ratio: normalized RS using a moving average
    rs_sma = df["RS"].rolling(window=lookback).mean()
    df["RS_Ratio"] = (df["RS"] / rs_sma.replace(0, np.nan)) * 100.0
    
    # 3. RS-Momentum: rate of change of RS-Ratio
    ratio_sma = df["RS_Ratio"].rolling(window=lookback).mean()
    df["RS_Momentum"] = (df["RS_Ratio"] / ratio_sma.replace(0, np.nan)) * 100.0

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
    
    metrics = {
        "latest_rs_ratio": round(float(latest["RS_Ratio"]), 2),
        "latest_rs_momentum": round(float(latest["RS_Momentum"]), 2),
        "latest_quadrant": latest["Quadrant"],
        "rs_ratio_delta": round(float(latest["RS_Ratio"] - previous["RS_Ratio"]), 2),
        "rs_momentum_delta": round(float(latest["RS_Momentum"] - previous["RS_Momentum"]), 2),
        "data_points": int(len(out_df)),
        "lookback": lookback,
    }

    return metrics, out_df


def _prepare_price_frame(source_df: pd.DataFrame, close_column_name: str) -> pd.DataFrame:
    df = source_df[["business_date", "close_price_adj"]].copy()
    df["business_date"] = pd.to_datetime(df["business_date"], errors="coerce")
    df["close_price_adj"] = pd.to_numeric(df["close_price_adj"], errors="coerce")
    df = df.dropna(subset=["business_date", "close_price_adj"])
    df = df.sort_values("business_date").drop_duplicates(subset=["business_date"], keep="last")
    return df.rename(columns={"close_price_adj": close_column_name})
