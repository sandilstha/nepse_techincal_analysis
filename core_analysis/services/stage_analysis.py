import pandas as pd
import pandas_ta as ta

def calculate_stage_analysis(df):
    """
    NEPSE-adapted Stage Analysis.
    Focuses on early Stage 2 momentum and avoiding late Stage 3 exhaustion.
    Uses 150-day (approx 30-week) and 50-day (approx 10-week) EMAs.
    """
    
    # Check if required columns exist
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
    # Momentum Ranking (NEPSE specific)
    # =========================
    df['returns_3m'] = df['close'].pct_change(periods=60)

    # =========================
    # Stage Detection
    # =========================
    conditions_stage2 = (
        (df['close'] > df['resistance']) &
        (df['close'] > df['ema_30w']) &
        (df['volume_ratio'] > 1.5)
    )

    conditions_stage4 = (
        (df['close'] < df['ema_30w']) &
        (df['ema_30w'] < df['ema_30w'].shift(5))
    )

    df['stage'] = 'Stage 1'

    df.loc[conditions_stage2, 'stage'] = 'Stage 2'
    df.loc[conditions_stage4, 'stage'] = 'Stage 4'

    return df
