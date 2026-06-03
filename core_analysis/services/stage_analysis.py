import numpy as np
import pandas as pd
import pandas_ta as ta

_MIN_ROWS = 150


def _coerce_int(value, default, minimum=1):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed >= minimum else default


def _coerce_float(value, default, minimum=None):
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if minimum is not None and parsed < minimum:
        return default
    return parsed


def _as_bool(value):
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def calculate_stage_analysis(
    df,
    volume_multiplier=1.5,
    resistance_lookback=20,
    volume_lookback=20,
    momentum_period=60,
    rsi_length=14,
    rsi_threshold=55.0,
    adx_length=14,
    adx_threshold=20.0,
    use_rsi_filter=False,
    use_adx_filter=False,
):
    """
    NEPSE-adapted Stage Analysis (Weinstein method).

    Returns an annotated dataframe with stage classification columns.
    """
    volume_multiplier = _coerce_float(volume_multiplier, 1.5, minimum=0.1)
    resistance_lookback = _coerce_int(resistance_lookback, 20, minimum=2)
    volume_lookback = _coerce_int(volume_lookback, 20, minimum=2)
    momentum_period = _coerce_int(momentum_period, 60, minimum=2)
    rsi_length = _coerce_int(rsi_length, 14, minimum=2)
    rsi_threshold = _coerce_float(rsi_threshold, 55.0, minimum=0.0)
    adx_length = _coerce_int(adx_length, 14, minimum=2)
    adx_threshold = _coerce_float(adx_threshold, 20.0, minimum=0.0)
    use_rsi_filter = _as_bool(use_rsi_filter)
    use_adx_filter = _as_bool(use_adx_filter)

    required_columns = {'close', 'high', 'volume'}
    if use_adx_filter:
        required_columns.add('low')
    if df.empty or not required_columns.issubset(df.columns):
        return df

    if len(df) < _MIN_ROWS:
        df['stage'] = 'Insufficient Data'
        return df

    df['ema_30w'] = ta.ema(df['close'], length=150)
    df['ema_10w'] = ta.ema(df['close'], length=50)

    df['avg_volume'] = df['volume'].rolling(volume_lookback).mean()
    safe_avg = df['avg_volume'].replace(0, np.nan)
    df['volume_ratio'] = df['volume'] / safe_avg

    df['resistance'] = df['high'].rolling(resistance_lookback).max().shift(1)

    df['ema30_rising'] = df['ema_30w'] > df['ema_30w'].shift(5)
    df['returns_3m'] = df['close'].pct_change(periods=momentum_period)

    df['rsi'] = ta.rsi(df['close'], length=rsi_length)
    df['adx'] = np.nan
    if 'low' in df.columns:
        adx_df = ta.adx(df['high'], df['low'], df['close'], length=adx_length)
        if isinstance(adx_df, pd.DataFrame) and not adx_df.empty:
            adx_col = next((col for col in adx_df.columns if col.upper().startswith('ADX_')), None)
            if adx_col is not None:
                df['adx'] = adx_df[adx_col]

    rsi_confirm = df['rsi'] >= rsi_threshold
    adx_confirm = df['adx'] >= adx_threshold
    rsi_gate = rsi_confirm if use_rsi_filter else pd.Series(True, index=df.index)
    adx_gate = adx_confirm if use_adx_filter else pd.Series(True, index=df.index)

    df['above_ema30'] = df['close'] > df['ema_30w']
    df['breakout'] = df['close'] > df['resistance']
    df['volume_confirm'] = df['volume_ratio'] > volume_multiplier
    df['momentum_confirm'] = df['returns_3m'] > 0
    df['rsi_confirm'] = rsi_confirm
    df['adx_confirm'] = adx_confirm
    df['stage2_score'] = (
        df['above_ema30'].fillna(False).astype(int) +
        df['ema30_rising'].fillna(False).astype(int) +
        df['breakout'].fillna(False).astype(int) +
        df['volume_confirm'].fillna(False).astype(int) +
        df['momentum_confirm'].fillna(False).astype(int) +
        df['rsi_confirm'].fillna(False).astype(int) +
        df['adx_confirm'].fillna(False).astype(int)
    )

    conditions_stage2 = (
        df['above_ema30'] &
        (df['ema30_rising']) &
        df['breakout'] &
        df['volume_confirm'] &
        df['momentum_confirm'] &
        rsi_gate &
        adx_gate
    )

    conditions_stage3 = (
        (df['close'] < df['ema_10w']) &
        (df['ema_10w'] < df['ema_30w']) &
        (df['ema30_rising']) &
        (df['close'] >= df['ema_30w'] * 0.85)
    )

    conditions_stage4 = (
        (df['close'] < df['ema_30w']) &
        (df['ema_30w'] < df['ema_30w'].shift(5))
    )

    # Keep canonical stage labels so downstream UI/filters match exactly.
    # Priority: Stage 2 > Stage 3 > Stage 4 > Stage 1
    df['stage'] = 'Stage 1'
    df.loc[conditions_stage4, 'stage'] = 'Stage 4'
    df.loc[conditions_stage3, 'stage'] = 'Stage 3'
    df.loc[conditions_stage2, 'stage'] = 'Stage 2'

    return df
