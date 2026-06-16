"""
indicator_views.py — server-side technical-indicator endpoints for the
Technical Analysis terminal.

The chart (Lightweight Charts) draws price + volume from the UDF history feed;
these endpoints add the *indicators* the user selects from the dropdown. Each
indicator is computed with TA-Lib against the locally-synced NEPSE bars.

TA-Lib (the C library, via the `talib` wrapper) is the engine because its
Wilder-smoothed implementations stay numerically stable on NEPSE's index
history, ~63% of whose bars record only a close (high == low). pandas_ta's
ADX/DMI divides by a near-zero ATR on those flat bars and explodes (−DI hit 474,
1467 bars > 100), wrecking the pane auto-scaling; TA-Lib's MINUS_DI peaks at a
correct 96.9 on the same data. pandas_ta is retained ONLY for SuperTrend, which
TA-Lib has no equivalent for.

    GET /chart/indicators            -> catalogue for the dropdown
    GET /chart/indicator?symbol=&name=&length=  -> computed series for one indicator

Indicators are tagged with a `pane`:
  * "overlay"  -> drawn on the price chart (moving averages, bands, PSAR…)
  * "separate" -> drawn in the lower oscillator pane (RSI, MACD, ADX…)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pandas_ta as ta  # retained only for SuperTrend (no TA-Lib equivalent)
import talib
from django.http import JsonResponse
from django.views.decorators.http import require_GET

# Reuse the UDF datafeed's symbol resolution + bar loader so price and
# indicators always come from exactly the same source rows.
from core_analysis.udf_views import _resolve, _bars


# ── series helpers ───────────────────────────────────────────────────────────

def _arr(s):
    """Float64 numpy array — the input dtype TA-Lib requires."""
    return np.asarray(s, dtype=float)


def _emit(dates, series, key, color, typ="line", clip=None):
    """Turn a series (numpy array from TA-Lib, or pandas Series) aligned to
    `dates` into a Lightweight Charts list, dropping NaN lookback points.

    `clip=(lo, hi)` clamps a mathematically bounded oscillator (e.g. ADX/DMI and
    RSI to 0-100, Williams %R to -100-0) to its canonical range. NEPSE's index
    history records only a close on ~63% of bars (high == low), so the true range
    collapses toward zero and range-normalised indicators like ±DI = 100·DM/ATR
    blow up to finite-but-absurd values (−DI hits 474 on this data). A single such
    spike makes Lightweight Charts auto-scale the whole pane around it; clamping
    keeps the pane readable. np.isfinite still drops NaN/±inf.
    """
    out = []
    vals = pd.to_numeric(pd.Series(series), errors="coerce").to_numpy(dtype=float)
    if clip is not None:
        vals = np.clip(vals, clip[0], clip[1])  # NaN passes through np.clip unchanged
    for i, v in enumerate(vals):
        if np.isfinite(v):
            out.append({"time": dates[i], "value": round(float(v), 4)})
    return {"key": key, "type": typ, "color": color, "data": out}


# ── indicator implementations ─────────────────────────────────────────────────
# Each fn takes (df, dates, length) and returns a list of emitted series.

def _sma(df, d, n):  return [_emit(d, talib.SMA(_arr(df.close), timeperiod=n), f"SMA {n}", "#f5a623")]
def _ema(df, d, n):  return [_emit(d, talib.EMA(_arr(df.close), timeperiod=n), f"EMA {n}", "#4a90e2")]
def _wma(df, d, n):  return [_emit(d, talib.WMA(_arr(df.close), timeperiod=n), f"WMA {n}", "#9b59b6")]


def _bbands(df, d, n):
    upper, mid, lower = talib.BBANDS(_arr(df.close), timeperiod=n, nbdevup=2, nbdevdn=2, matype=0)
    return [
        _emit(d, lower, "BB Lower", "#888"),
        _emit(d, mid, "BB Mid", "#f5a623"),
        _emit(d, upper, "BB Upper", "#888"),
    ]


def _psar(df, d, n):
    # TA-Lib's SAR already returns one continuous series (no long/short split).
    return [_emit(d, talib.SAR(_arr(df.high), _arr(df.low), acceleration=0.02, maximum=0.2), "PSAR", "#e0414b")]


def _supertrend(df, d, n):
    # pandas_ta only — TA-Lib has no SuperTrend.
    st = ta.supertrend(df.high, df.low, df.close, length=n or 10, multiplier=3.0)
    line = [c for c in st.columns if c.startswith("SUPERT_")][0]
    return [_emit(d, st[line], "SuperTrend", "#14b88a")]


def _rsi(df, d, n):   return [_emit(d, talib.RSI(_arr(df.close), timeperiod=n), f"RSI {n}", "#7e57c2", clip=(0, 100))]
def _cci(df, d, n):   return [_emit(d, talib.CCI(_arr(df.high), _arr(df.low), _arr(df.close), timeperiod=n), f"CCI {n}", "#26a69a")]
def _willr(df, d, n): return [_emit(d, talib.WILLR(_arr(df.high), _arr(df.low), _arr(df.close), timeperiod=n), f"%R {n}", "#ef5350", clip=(-100, 0))]
def _roc(df, d, n):   return [_emit(d, talib.ROC(_arr(df.close), timeperiod=n), f"ROC {n}", "#42a5f5")]
def _mom(df, d, n):   return [_emit(d, talib.MOM(_arr(df.close), timeperiod=n), f"MOM {n}", "#ab47bc")]
def _atr(df, d, n):   return [_emit(d, talib.ATR(_arr(df.high), _arr(df.low), _arr(df.close), timeperiod=n), f"ATR {n}", "#ff7043")]
def _obv(df, d, n):   return [_emit(d, talib.OBV(_arr(df.close), _arr(df.volume)), "OBV", "#66bb6a")]
def _mfi(df, d, n):   return [_emit(d, talib.MFI(_arr(df.high), _arr(df.low), _arr(df.close), _arr(df.volume), timeperiod=n), f"MFI {n}", "#26c6da", clip=(0, 100))]


def _cmf(df, d, n):
    # Chaikin Money Flow — TA-Lib has no CMF (only AD/ADOSC), so compute the
    # standard rolling form directly: money-flow multiplier × volume, summed over
    # n bars and normalised by volume. On flat bars (high == low) the multiplier
    # is 0 by convention (no money flow) — NOT NaN, otherwise a single flat bar
    # would void its whole n-bar window and, given NEPSE's ~63% flat bars, leave
    # CMF almost entirely empty.
    rng = df.high - df.low
    mfm = (((df.close - df.low) - (df.high - df.close)) / rng).where(rng != 0, 0.0)
    mfv = mfm * df.volume
    cmf = mfv.rolling(n).sum() / df.volume.rolling(n).sum()
    return [_emit(d, cmf, f"CMF {n}", "#5c6bc0", clip=(-1, 1))]


def _macd(df, d, n):
    macd, signal, hist = talib.MACD(_arr(df.close), fastperiod=12, slowperiod=26, signalperiod=9)
    return [
        _emit(d, macd, "MACD", "#42a5f5"),
        _emit(d, signal, "Signal", "#ff7043"),
        _emit(d, hist, "Histogram", "#888", typ="histogram"),
    ]


def _adx(df, d, n):
    h, l, c = _arr(df.high), _arr(df.low), _arr(df.close)
    return [
        _emit(d, talib.ADX(h, l, c, timeperiod=n), f"ADX {n}", "#fbc02d", clip=(0, 100)),
        _emit(d, talib.PLUS_DI(h, l, c, timeperiod=n), "+DI", "#14b88a", clip=(0, 100)),
        _emit(d, talib.MINUS_DI(h, l, c, timeperiod=n), "-DI", "#e0414b", clip=(0, 100)),
    ]


def _stoch(df, d, n):
    # 14/3/3 (fast-%K / slow-%K / %D) — matches the prior pandas_ta defaults.
    k, dd = talib.STOCH(_arr(df.high), _arr(df.low), _arr(df.close),
                        fastk_period=14, slowk_period=3, slowk_matype=0,
                        slowd_period=3, slowd_matype=0)
    return [
        _emit(d, k, "%K", "#42a5f5", clip=(0, 100)),
        _emit(d, dd, "%D", "#ff7043", clip=(0, 100)),
    ]


# name -> (label, pane, default_length, fn)
INDICATORS = {
    # overlays (on price)
    "SMA":        ("Simple MA",        "overlay",  20, _sma),
    "EMA":        ("Exponential MA",   "overlay",  20, _ema),
    "WMA":        ("Weighted MA",      "overlay",  20, _wma),
    "BBANDS":     ("Bollinger Bands",  "overlay",  20, _bbands),
    "PSAR":       ("Parabolic SAR",    "overlay",   0, _psar),
    "SUPERTREND": ("SuperTrend",       "overlay",  10, _supertrend),
    # oscillators (separate pane)
    "RSI":        ("RSI",              "separate", 14, _rsi),
    "MACD":       ("MACD",             "separate",  0, _macd),
    "ADX":        ("ADX / DMI",        "separate", 14, _adx),
    "STOCH":      ("Stochastic",       "separate", 14, _stoch),
    "CCI":        ("CCI",              "separate", 20, _cci),
    "WILLR":      ("Williams %R",      "separate", 14, _willr),
    "ATR":        ("ATR",              "separate", 14, _atr),
    "MFI":        ("Money Flow Index", "separate", 14, _mfi),
    "CMF":        ("Chaikin Money Flow","separate", 20, _cmf),
    "ROC":        ("Rate of Change",   "separate", 10, _roc),
    "MOM":        ("Momentum",         "separate", 10, _mom),
    "OBV":        ("On-Balance Volume","separate",  0, _obv),
}


# ── endpoints ──────────────────────────────────────────────────────────────

@require_GET
def indicator_catalog(request):
    """List available indicators for the dropdown."""
    return JsonResponse(
        [
            {"name": name, "label": label, "pane": pane, "length": length}
            for name, (label, pane, length, _fn) in INDICATORS.items()
        ],
        safe=False,
    )


@require_GET
def indicator_data(request):
    """Compute one indicator's series for a symbol."""
    name = (request.GET.get("name") or "").strip().upper()
    if name not in INDICATORS:
        return JsonResponse({"s": "error", "errmsg": "unknown_indicator"}, status=404)

    kind, key = _resolve(request.GET.get("symbol", ""))
    if not kind:
        return JsonResponse({"s": "error", "errmsg": "unknown_symbol"}, status=404)

    label, pane, default_len, fn = INDICATORS[name]
    try:
        length = int(request.GET.get("length", default_len)) or default_len
    except (TypeError, ValueError):
        length = default_len

    rows = _bars(kind, key, None, None, None)  # full daily history
    if not rows or len(rows) < (length + 2):
        return JsonResponse({"s": "no_data"})

    df = pd.DataFrame(rows, columns=["business_date", "open", "high", "low", "close", "volume"])
    for col in ("open", "high", "low", "close", "volume"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    dates = [d.isoformat() for d in df["business_date"]]

    try:
        series = fn(df, dates, length)
    except Exception:  # a single bad indicator must never 500 the page
        return JsonResponse({"s": "error", "errmsg": "calc_failed"}, status=200)

    series = [s for s in series if s and s["data"]]
    if not series:
        return JsonResponse({"s": "no_data"})

    return JsonResponse({"s": "ok", "name": name, "label": label, "pane": pane, "series": series})
