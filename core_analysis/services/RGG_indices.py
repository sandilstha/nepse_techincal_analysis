from collections import Counter

import pandas as pd

from core_analysis.services.RGG_Chart import run_rrg_simulation


NEPSE_INDEX_ORDER = [
    "NEPSE INDEX",
    "BANKING SUBINDEX",
    "DEVELOPMENT BANK INDEX",
    "FINANCE INDEX",
    "MICROFINANCE INDEX",
    "LIFE INSURANCE",
    "NON LIFE INSURANCE",
    "HYDROPOWER INDEX",
    "HOTELS AND TOURISM INDEX",
    "MANUFACTURING AND PROCESSING",
    "TRADING INDEX",
    "OTHERS INDEX",
    "INVESTMENT INDEX",
    "MUTUAL FUND",
]

RRG_EXCLUDED_INDICES = {
    "SENSITIVE INDEX",
    "FLOAT INDEX",
    "SENSITIVE FLOAT INDEX",
}

NEPSE_INDEX_LABELS = {
    "NEPSE INDEX": "NEPSE",
    "BANKING SUBINDEX": "BANKING",
    "DEVELOPMENT BANK INDEX": "DEV BANK",
    "FINANCE INDEX": "FINANCE",
    "MICROFINANCE INDEX": "MICROFINANCE",
    "LIFE INSURANCE": "LIFE INS",
    "NON LIFE INSURANCE": "NON LIFE",
    "HYDROPOWER INDEX": "HYDROPOWER",
    "HOTELS AND TOURISM INDEX": "HOTELS",
    "MANUFACTURING AND PROCESSING": "MFG",
    "TRADING INDEX": "TRADING",
    "OTHERS INDEX": "OTHERS",
    "INVESTMENT INDEX": "INVESTMENT",
    "MUTUAL FUND": "MUTUAL FUND",
}


def ordered_nepse_indices(available_indices, benchmark_symbol="NEPSE INDEX"):
    available = {
        str(name).strip().upper()
        for name in available_indices
        if str(name).strip() and str(name).strip().upper() not in RRG_EXCLUDED_INDICES
    }
    benchmark = (benchmark_symbol or "NEPSE INDEX").strip().upper()
    ordered = [name for name in NEPSE_INDEX_ORDER if name in available and name != benchmark]
    extras = sorted(name for name in available if name not in NEPSE_INDEX_ORDER and name != benchmark)
    return ordered + extras


def run_rrg_indices_simulation(
    index_frames,
    benchmark_df,
    benchmark_symbol="NEPSE INDEX",
    lookback=14,
    tail_length=30,
    selected_symbols=None,
):
    if benchmark_df.empty:
        return {"error": f"No benchmark data found for '{benchmark_symbol}'."}, [], [], []
    if lookback < 2:
        return {"error": "RRG lookback must be at least 2 bars."}, [], [], []

    benchmark = (benchmark_symbol or "NEPSE INDEX").strip().upper()
    ordered_symbols = ordered_nepse_indices(index_frames.keys(), benchmark)
    if selected_symbols is not None:
        selected_set = {str(symbol).strip().upper() for symbol in selected_symbols if str(symbol).strip()}
        ordered_symbols = [symbol for symbol in ordered_symbols if symbol in selected_set]
    if not ordered_symbols:
        return {"error": "No NEPSE indices selected for RRG plotting."}, [], [], []

    points = []
    trails = []
    skipped = []

    for order, symbol in enumerate(ordered_symbols, start=1):
        index_df = index_frames.get(symbol, pd.DataFrame())
        metrics, rrg_df = run_rrg_simulation(index_df, benchmark_df, lookback=lookback)
        if isinstance(metrics, dict) and metrics.get("error"):
            skipped.append({"symbol": symbol, "reason": metrics["error"]})
            continue
        if rrg_df.empty:
            skipped.append({"symbol": symbol, "reason": "No calculated RRG rows."})
            continue

        latest = rrg_df.iloc[-1]
        previous = rrg_df.iloc[-2] if len(rrg_df) > 1 else latest
        label = NEPSE_INDEX_LABELS.get(symbol, symbol.replace(" INDEX", ""))
        point = {
            "order": order,
            "symbol": symbol,
            "label": label,
            "business_date": _format_date(latest["business_date"]),
            "close": round(float(latest["stock_close"]), 2),
            "benchmark_close": round(float(latest["bench_close"]), 2),
            "RS": round(float(latest["RS"]), 4),
            "RS_Ratio": round(float(latest["RS_Ratio"]), 2),
            "RS_Momentum": round(float(latest["RS_Momentum"]), 2),
            "ratio_delta": round(float(latest["RS_Ratio"] - previous["RS_Ratio"]), 2),
            "momentum_delta": round(float(latest["RS_Momentum"] - previous["RS_Momentum"]), 2),
            "Quadrant": str(latest["Quadrant"]),
            "data_points": int(len(rrg_df)),
        }
        points.append(point)

        for step, (_, row) in enumerate(rrg_df.tail(tail_length).iterrows(), start=1):
            trails.append({
                "order": order,
                "symbol": symbol,
                "label": label,
                "step": step,
                "business_date": _format_date(row["business_date"]),
                "RS_Ratio": round(float(row["RS_Ratio"]), 2),
                "RS_Momentum": round(float(row["RS_Momentum"]), 2),
                "Quadrant": str(row["Quadrant"]),
            })

    if not points:
        return {"error": "No NEPSE indices had enough data for the selected RRG lookback."}, [], [], skipped

    quadrant_counts = Counter(point["Quadrant"] for point in points)
    metrics = {
        "benchmark_symbol": benchmark,
        "indices_scanned": len(ordered_symbols),
        "indices_plotted": len(points),
        "skipped_count": len(skipped),
        "lookback": lookback,
        "latest_date": max(point["business_date"] for point in points),
        "quadrant_counts": {
            "Leading": quadrant_counts.get("Leading", 0),
            "Weakening": quadrant_counts.get("Weakening", 0),
            "Lagging": quadrant_counts.get("Lagging", 0),
            "Improving": quadrant_counts.get("Improving", 0),
        },
    }
    return metrics, points, trails, skipped


def _format_date(value):
    if pd.isna(value):
        return ""
    return pd.to_datetime(value).strftime("%Y-%m-%d")
