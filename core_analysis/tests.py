import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from core_analysis.services import IMM, msv_strategy


class FakeTechnicalAnalysis:
    @staticmethod
    def sma(series, length):
        values = pd.to_numeric(series, errors="coerce")
        if series.name == "volume":
            return pd.Series(values * 0.5, index=series.index)

        offset = {20: 1.0, 50: 2.0, 200: 3.0}.get(length, 1.0)
        return pd.Series(values - offset, index=series.index)

    @staticmethod
    def rsi(series, length):
        return pd.Series(60.0, index=series.index)

    @staticmethod
    def macd(series, fast, slow, signal):
        line = pd.Series(-1.0, index=series.index)
        if len(line) > 200:
            line.iloc[200:] = 1.0
        signal_line = pd.Series(0.0, index=series.index)
        return pd.DataFrame(
            {
                "MACD": line,
                "MACDh": line - signal_line,
                "MACDs": signal_line,
            },
            index=series.index,
        )

    @staticmethod
    def supertrend(high, low, close, length, multiplier):
        direction = pd.Series(1, index=close.index)
        if len(direction) > 205:
            direction.iloc[205] = -1
        return pd.DataFrame(
            {
                "SUPERT_10_3.0": pd.to_numeric(close, errors="coerce") - 5.0,
                "SUPERTd_10_3.0": direction,
            },
            index=close.index,
        )

    @staticmethod
    def vwap(high, low, close, volume):
        return pd.Series(pd.to_numeric(close, errors="coerce") - 1.0, index=close.index)

    @staticmethod
    def atr(high, low, close, length):
        return pd.Series(2.0, index=close.index)


def make_price_frame(close_values):
    dates = pd.date_range("2025-01-01", periods=len(close_values), freq="D")
    close = pd.Series(close_values, dtype=float)
    return pd.DataFrame(
        {
            "business_date": dates,
            "open_price_adj": close,
            "high_price_adj": close + 1.0,
            "low_price_adj": close - 1.0,
            "close_price_adj": close,
            "volume": 1000.0,
        }
    )


class IMMScoringTests(unittest.TestCase):
    def test_generate_sell_signal_tolerates_missing_atr_stop(self):
        df = pd.DataFrame(
            {
                "close_price_adj": [100.0, 99.0],
                "SMA_20": [95.0, 100.0],
                "RSI_14": [60.0, 60.0],
                "MACD_line": [1.0, 1.0],
                "MACD_signal": [0.0, 0.0],
                "supertrend_bullish": [True, False],
            }
        )

        sell_signal = IMM.generate_sell_signal(df)

        self.assertFalse(bool(sell_signal.iloc[0]))
        self.assertTrue(bool(sell_signal.iloc[1]))

    def test_position_builder_sells_on_atr_stop_and_resets_after_exit(self):
        df = pd.DataFrame(
            {
                "close_price_adj": [100.0, 105.0, 103.0, 99.0, 101.0, 102.0],
                "ATR": [2.0] * 6,
                "SMA_20": [90.0, 90.0, 90.0, 100.0, 90.0, 90.0],
                "RSI_14": [60.0] * 6,
                "MACD_line": [1.0] * 6,
                "MACD_signal": [0.0] * 6,
                "supertrend_bullish": [True, True, True, False, True, True],
            }
        )
        raw_buy = pd.Series([True, True, False, False, True, False])

        buy_signal, sell_signal, stop = IMM._build_position_signals_with_atr_stop(
            df,
            raw_buy,
            multiplier=2.0,
        )

        self.assertEqual(buy_signal[buy_signal].index.tolist(), [0, 4])
        self.assertEqual(sell_signal[sell_signal].index.tolist(), [3])
        self.assertEqual(stop.iloc[1], 101.0)
        self.assertEqual(stop.iloc[3], 101.0)
        self.assertEqual(stop.iloc[4], 97.0)

    def test_run_imm_scoring_system_returns_stop_aware_sell_event(self):
        stock_close = np.arange(100.0, 310.0)
        stock_close[205:] = stock_close[205:] - 80.0
        nepse_close = np.arange(1000.0, 1210.0)

        stock_df = make_price_frame(stock_close)
        nepse_df = make_price_frame(nepse_close)

        with patch.object(IMM, "ta", FakeTechnicalAnalysis):
            metrics, output = IMM.run_imm_scoring_system(stock_df, nepse_df)

        self.assertNotIn("error", metrics)
        self.assertEqual(metrics["buy_count"], 1)
        self.assertEqual(metrics["sell_count"], 1)
        self.assertTrue(bool(output.loc[200, "buy_signal"]))
        self.assertTrue(bool(output.loc[205, "sell_signal"]))
        self.assertTrue(pd.isna(output.loc[206, "atr_trailing_stop"]))


class MSVStrategyTests(unittest.TestCase):
    @unittest.skipIf(msv_strategy.ta is None, "pandas_ta unavailable")
    def test_msv_vwap_works_with_standard_business_date_column(self):
        close_values = np.arange(100.0, 180.0)
        stock_df = make_price_frame(close_values)

        metrics, trades, output = msv_strategy.run_msv_long_only_simulation(stock_df)

        self.assertNotIn("error", metrics)
        self.assertEqual(len(output), len(stock_df))
        self.assertFalse(output["VWAP"].isna().all())


if __name__ == "__main__":
    unittest.main()
