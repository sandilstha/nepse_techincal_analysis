import unittest
from contextlib import ExitStack
from datetime import date
from unittest.mock import patch

import numpy as np
import pandas as pd
from django.core.exceptions import ImproperlyConfigured

from core_analysis.services import IMM, msv_strategy
from core_analysis.services.advanced_market_structure import (
    generate_dummy_ohlcv,
    run_advanced_market_structure_analysis,
)
from core_analysis.services.support_resistance import (
    build_institutional_analysis_rows,
    run_support_resistance_analysis,
)

try:
    from core_analysis.services import market_insights
except ImproperlyConfigured:  # Allows `python core_analysis/tests.py` outside Django.
    market_insights = None


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


@unittest.skipIf(market_insights is None, "Django settings unavailable")
class MarketInsightsHeadlineTests(unittest.TestCase):
    def test_payload_prefers_contributor_headline_over_stale_subindex(self):
        stale_subindex = {
            "NepseIndex": {
                "closingIndex": 2731.53,
                "absChange": 3.50,
                "percentageChange": 0.13,
                "highIndex": 2731.53,
                "lowIndex": 2721.40,
                "turnoverValue": 0,
                "businessDate": "2026-06-11",
            }
        }
        live_contributors = {
            "index": {
                "value": 2721.72,
                "change": -6.31,
                "prev_close": 2728.03,
                "pct": -0.23,
            },
            "positive": [],
            "negative": [],
        }
        summary = [{
            "businessDate": "2026-06-12",
            "totalTurnover": 1164469269.88,
            "totalTradedShares": 2524762,
            "totalTransactions": 0,
            "tradedScrips": 0,
        }]

        patches = [
            patch.object(market_insights.cache, "get", return_value=None),
            patch.object(market_insights.cache, "set"),
            patch.object(market_insights, "fetch_live_rows", return_value=None),
            patch.object(market_insights, "fetch_subindices", return_value=stale_subindex),
            patch.object(market_insights, "fetch_market_summary", return_value=summary),
            patch.object(market_insights, "fetch_contributors", return_value=live_contributors),
            patch.object(market_insights, "fetch_top_gainers", return_value=None),
            patch.object(market_insights, "fetch_top_losers", return_value=None),
            patch.object(market_insights, "fetch_top_active", return_value=None),
            patch.object(market_insights, "_sector_map", return_value={}),
            patch.object(market_insights, "_latest_stock_rows", return_value=(date(2026, 6, 11), [])),
            patch.object(market_insights, "_nepse_history", return_value=[]),
        ]

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)
            payload = market_insights.build_payload(force=True)

        self.assertEqual(payload["as_of"], "2026-06-12")
        self.assertEqual(payload["overview"]["nepse_index"], 2721.72)
        self.assertEqual(payload["overview"]["nepse_change"], -6.31)
        self.assertEqual(payload["overview"]["nepse_pct"], -0.23)
        self.assertEqual(payload["overview"]["turnover"], 1164469269.88)
        self.assertEqual(payload["overview"]["volume"], 2524762)


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


class SupportResistanceTests(unittest.TestCase):
    def _sample_support_resistance_frame(self):
        return pd.DataFrame(
            {
                "business_date": pd.to_datetime(["2025-06-01", "2025-06-02"]),
                "high_price_adj": [29.20, 28.64],
                "low_price_adj": [28.70, 28.01],
                "close_price_adj": [28.99, 28.17],
                "price_source": ["Adjusted", "Adjusted"],
            }
        )

    def test_support_resistance_pivots_match_standard_formula(self):
        df = self._sample_support_resistance_frame()

        metrics, rows = run_support_resistance_analysis(df, symbol="KGC")
        levels_by_label = {
            label: row["price"]
            for row in rows
            for label in row["level_names"]
        }

        self.assertNotIn("error", metrics)
        self.assertEqual(metrics["pivot"], 28.27)
        self.assertEqual(levels_by_label["Pivot Point 1st Resistance Point"], 28.54)
        self.assertEqual(levels_by_label["Pivot Point 2nd Level Resistance"], 28.90)
        self.assertEqual(levels_by_label["Pivot Point 3rd Level Resistance"], 29.17)
        self.assertEqual(levels_by_label["Pivot Point 1st Support Point"], 27.91)
        self.assertEqual(levels_by_label["Pivot Point 2nd Support Point"], 27.64)
        self.assertEqual(levels_by_label["Pivot Point 3rd Support Point"], 27.28)
        self.assertEqual(len(metrics["simple_level_rows"]), 8)
        self.assertEqual(metrics["simple_level_rows"][-1]["basis"], "Pivot S1/S2/R1/R2")

    def test_support_resistance_honors_selected_level_families(self):
        df = self._sample_support_resistance_frame()

        metrics, rows = run_support_resistance_analysis(
            df,
            symbol="KGC",
            enabled_families=["hlc"],
        )
        labels = {
            label
            for row in rows
            for label in row["level_names"]
        }

        self.assertEqual(metrics["enabled_families"], ["hlc"])
        self.assertIn("High", labels)
        self.assertIn("Low", labels)
        self.assertNotIn("Pivot Point", labels)

    def test_nearest_headline_levels_use_confluence(self):
        df = pd.DataFrame(
            {
                "business_date": pd.to_datetime(["2025-06-01", "2025-06-02", "2025-06-03"]),
                "open_price_adj": [90.0, 118.0, 101.0],
                "high_price_adj": [120.0, 116.0, 105.0],
                "low_price_adj": [80.0, 96.0, 95.0],
                "close_price_adj": [118.0, 102.0, 100.0],
                "volume": [1000, 1200, 900],
            }
        )

        metrics, _ = run_support_resistance_analysis(df, symbol="BB")

        # Headline cards now use the confluence engine (real reaction levels with
        # >= 2 agreeing methods), not the raw Bollinger band.
        self.assertEqual(metrics["nearest_level_basis"], "Confluence")
        self.assertEqual(metrics["nearest_resistance"]["basis"], "Confluence")
        self.assertEqual(metrics["nearest_support"]["basis"], "Confluence")
        self.assertGreaterEqual(metrics["nearest_resistance"]["method_count"], 2)
        self.assertGreaterEqual(metrics["nearest_support"]["method_count"], 2)
        self.assertGreaterEqual(metrics["nearest_resistance"]["price"], metrics["latest_price"])
        self.assertLessEqual(metrics["nearest_support"]["price"], metrics["latest_price"])
        # Bollinger bands are still computed and exposed as a reference.
        self.assertIn("middle_band", metrics["bollinger_bands"])


class AdvancedMarketStructureTests(unittest.TestCase):
    def test_advanced_market_structure_runs_on_dummy_ohlcv(self):
        df = generate_dummy_ohlcv(rows=180, seed=7)

        metrics = run_advanced_market_structure_analysis(df, symbol="DUMMY", fractal_window=5)

        self.assertNotIn("error", metrics)
        self.assertEqual(metrics["symbol"], "DUMMY")
        self.assertGreater(metrics["pivot_count"], 0)
        self.assertIn("density_zones", metrics)
        self.assertIn("profile", metrics)
        self.assertIn("chart", metrics)
        self.assertGreater(len(metrics["chart"]["candles"]), 0)

    def test_advanced_market_structure_rejects_short_data(self):
        df = generate_dummy_ohlcv(rows=8, seed=7)

        metrics = run_advanced_market_structure_analysis(df, symbol="SHORT", fractal_window=5)

        self.assertIn("error", metrics)


class InstitutionalAnalysisTests(unittest.TestCase):
    def test_institutional_analysis_returns_exact_framework_table_contract(self):
        df = generate_dummy_ohlcv(rows=160, seed=11)
        support_metrics, _ = run_support_resistance_analysis(df)
        advanced_metrics = run_advanced_market_structure_analysis(df, symbol="DUMMY", fractal_window=5)

        rows = build_institutional_analysis_rows(support_metrics, advanced_metrics)

        # 9 framework systems plus the appended "Institutional Consensus" row.
        self.assertEqual(len(rows), 10)
        self.assertEqual(rows[-1]["system"], "Institutional Consensus")
        # Keys are lowercase snake_case to match the template ({{ row.system }}).
        for row in rows:
            self.assertIn("system", row)
            self.assertIn("institutional_logic", row)
            self.assertIn("price_sentiment", row)
            self.assertIn("status", row)
            self.assertTrue(row["system"])
            self.assertTrue(row["institutional_logic"])
            self.assertTrue(row["price_sentiment"])
            self.assertTrue(row["status"])


if __name__ == "__main__":
    unittest.main()
