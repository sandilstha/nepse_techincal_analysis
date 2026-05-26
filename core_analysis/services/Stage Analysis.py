import pandas as pd
import pandas_ta as ta

def calculate_stage_analysis(df):
    """
    NEPSE-adapted Stage Analysis (Weinstein method).
    All 4 stages now defined. ema_10w and returns_3m are actively used.
    """
    if df.empty or 'close' not in df.columns or 'volume' not in df.columns:
        return df

    # =========================
    # Moving Averages
    # =========================
    df['ema_30w'] = ta.ema(df['close'], length=150)
    df['ema_10w'] = ta.ema(df['close'], length=50)

    # =========================
    # Volume Ratio
    # =========================
    df['avg_volume'] = df['volume'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / df['avg_volume']

    # =========================
    # Resistance Breakout
    # =========================
    df['resistance'] = df['high'].rolling(20).max().shift(1)

    # =========================
    # Trend Conditions
    # =========================
    df['ema30_rising'] = df['ema_30w'] > df['ema_30w'].shift(5)

    # =========================
    # Momentum (NEPSE-specific)
    # =========================
    df['returns_3m'] = df['close'].pct_change(periods=60)

    # =========================
    # Stage Conditions
    # =========================
    conditions_stage2 = (
        (df['close'] > df['ema_30w']) &
        (df['ema30_rising']) &
        (df['close'] > df['resistance']) &
        (df['volume_ratio'] > 1.5) &
        (df['returns_3m'] > 0)          # FIX ④: now actually used
    )

    # FIX ②: Stage 3 now defined — uses ema_10w (FIX ①)
    conditions_stage3 = (
        (df['close'] < df['ema_10w']) &
        (df['ema_10w'] < df['ema_30w']) &
        (df['ema30_rising'])             # EMA30 still rising = early distribution
    )

    conditions_stage4 = (
        (df['close'] < df['ema_30w']) &
        (df['ema_30w'] < df['ema_30w'].shift(5))
    )

    # FIX ③: Apply in ascending priority — Stage 2 wins over all
    df['stage'] = 'Stage 1'                                  # residual basing
    df.loc[conditions_stage4, 'stage'] = 'Stage 4'
    df.loc[conditions_stage3, 'stage'] = 'Stage 3'
    df.loc[conditions_stage2, 'stage'] = 'Stage 2'           # highest priority

    return df
