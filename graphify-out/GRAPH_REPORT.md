# Graph Report - nepse_analytics_platform  (2026-06-19)

## Corpus Check
- 62 files · ~78,361 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1896 nodes · 4749 edges · 99 communities (57 shown, 42 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 129 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dc42b30a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 88|Community 88]]
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]
- [[_COMMUNITY_Community 91|Community 91]]
- [[_COMMUNITY_Community 92|Community 92]]
- [[_COMMUNITY_Community 93|Community 93]]
- [[_COMMUNITY_Community 95|Community 95]]
- [[_COMMUNITY_Community 96|Community 96]]
- [[_COMMUNITY_Community 97|Community 97]]
- [[_COMMUNITY_Community 98|Community 98]]
- [[_COMMUNITY_Community 99|Community 99]]
- [[_COMMUNITY_Community 100|Community 100]]
- [[_COMMUNITY_Community 101|Community 101]]
- [[_COMMUNITY_Community 111|Community 111]]

## God Nodes (most connected - your core abstractions)
1. `_()` - 162 edges
2. `vn` - 114 edges
3. `sn()` - 68 edges
4. `f()` - 61 edges
5. `as()` - 58 edges
6. `yi` - 56 edges
7. `fs()` - 42 edges
8. `hs()` - 38 edges
9. `NepseMarketIndex` - 37 edges
10. `pn` - 37 edges

## Surprising Connections (you probably didn't know these)
- `AdvancedMarketStructureTests` --uses--> `NepseMarketIndex`  [INFERRED]
  core_analysis/tests.py → core_analysis/models.py
- `FakeTechnicalAnalysis` --uses--> `NepseMarketIndex`  [INFERRED]
  core_analysis/tests.py → core_analysis/models.py
- `IMMScoringTests` --uses--> `NepseMarketIndex`  [INFERRED]
  core_analysis/tests.py → core_analysis/models.py
- `IndicatorHistoryWindowTests` --uses--> `NepseMarketIndex`  [INFERRED]
  core_analysis/tests.py → core_analysis/models.py
- `InstitutionalAnalysisTests` --uses--> `NepseMarketIndex`  [INFERRED]
  core_analysis/tests.py → core_analysis/models.py

## Import Cycles
- None detected.

## Communities (99 total, 42 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (81): BaseCommand, _build_url(), _can_stop_after_ascending_page(), _clean_date(), _clean_decimal(), _clean_int(), _clean_text(), Command (+73 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (79): Any, DataFrame, Series, SupportResistanceTests, _add_level(), _add_retracements(), _add_window_extremes(), _bollinger_headline() (+71 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (22): Any, DataFrame, Series, AdvancedMarketStructureTests, FakeTechnicalAnalysis, IMMScoringTests, IndicatorHistoryWindowTests, InstitutionalAnalysisTests (+14 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (61): fetch_live_rows(), live_price.py — intraday live NEPSE quotes for the Market Insights dashboard.  P, Return a list of raw live-quote dicts, or None if the feed is unavailable., _breadth(), _build_eod_payload(), build_payload(), _contributors_index_metrics(), _enrich() (+53 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (64): broker_concentration(), broker_favorites(), broker_persistence(), broker_signals(), _build_meta(), _cached_day_value(), _company_meta(), _company_names() (+56 more)

### Community 5 - "Community 5"
Cohesion: 0.10
Nodes (42): onChange(), activateTab(), buildBrokerMulti(), buildBrokerTable(), buildConcTable(), buildFavTable(), buildHoldTable(), buildHotTable() (+34 more)

### Community 6 - "Community 6"
Cohesion: 0.17
Nodes (42): applyTheme(), baseChartOpts(), cssVar(), deferNonCritical(), destroyCharts(), dirClass(), el(), escapeHtml() (+34 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (16): _(), ae(), b(), ce(), de(), fe(), In(), O() (+8 more)

### Community 8 - "Community 8"
Cohesion: 0.17
Nodes (3): gi(), he, ki()

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (7): gs(), ks(), ls(), ms(), Ss(), ws, xs()

### Community 13 - "Community 13"
Cohesion: 0.22
Nodes (19): _asset_version(), broker_concentration_api(), broker_favorites_api(), broker_meta_api(), broker_persistence_api(), broker_signals_api(), broker_trend_api(), floorsheet_view() (+11 more)

### Community 14 - "Community 14"
Cohesion: 0.18
Nodes (28): $(), addChip(), addIndicator(), addOscPane(), alignIndicatorSeries(), allCharts(), barTimeLookup(), baseOptions() (+20 more)

### Community 17 - "Community 17"
Cohesion: 0.15
Nodes (26): DataFrame, Series, _build_position_signals(), _build_position_signals_with_atr_stop(), _calculate_atr_trailing_stop(), calculate_relative_strength(), calculate_technical_score(), calculate_volume_greed() (+18 more)

### Community 18 - "Community 18"
Cohesion: 0.16
Nodes (5): an(), hn(), ln(), rn(), tn()

### Community 19 - "Community 19"
Cohesion: 0.12
Nodes (24): _append_live_index_bar(), _bars(), _chart_bars(), _clean_symbol(), _company_symbols(), _day_to_ts(), _f(), _live_index_bar() (+16 more)

### Community 20 - "Community 20"
Cohesion: 0.08
Nodes (31): _build_benchmark_sparkline(), build_dashboard_context(), _build_index_dataframes(), _build_rrg_index_choices(), _build_standard_dataframe(), crud_dashboard_view(), crud_delete_handler(), crud_operations_handler() (+23 more)

### Community 24 - "Community 24"
Cohesion: 0.21
Nodes (23): _adx(), _arr(), _atr(), _bbands(), _cci(), _cmf(), _ema(), _emit() (+15 more)

### Community 25 - "Community 25"
Cohesion: 0.07
Nodes (8): ee(), ie(), le(), ne(), pe(), qn(), ve(), zn()

### Community 27 - "Community 27"
Cohesion: 0.07
Nodes (6): di(), J, mi, ps(), wi(), zi

### Community 28 - "Community 28"
Cohesion: 0.14
Nodes (3): fi(), pi(), si

### Community 32 - "Community 32"
Cohesion: 0.21
Nodes (16): a(), c(), d(), e(), f(), g(), h(), i() (+8 more)

### Community 33 - "Community 33"
Cohesion: 0.11
Nodes (4): ai, ei, hi(), li()

### Community 37 - "Community 37"
Cohesion: 0.21
Nodes (3): ds(), T(), Ts()

### Community 40 - "Community 40"
Cohesion: 0.17
Nodes (15): _asset_version(), _empty_payload(), market_insights_api(), market_insights_view(), insights_views.py — view layer for the Market Insights dashboard.  Two endpoints, Render the dashboard shell instantly.      The payload is embedded ONLY if it is, MetaStock-style charting terminal (Lightweight Charts).      Renders price (OHLC, JSON multi-series feed for the sub-index comparison chart.      Accepts ?days=<s (+7 more)

### Community 41 - "Community 41"
Cohesion: 0.28
Nodes (15): $(), applyColors(), buildSeries(), chartOptions(), cssVar(), deferInitialFetch(), DrawingLayer(), fetchBars() (+7 more)

### Community 44 - "Community 44"
Cohesion: 0.09
Nodes (9): bi(), Et, H, kt, te(), vi(), X(), xt() (+1 more)

### Community 45 - "Community 45"
Cohesion: 0.18
Nodes (5): A(), d(), Js(), v(), zt

### Community 47 - "Community 47"
Cohesion: 0.11
Nodes (3): ht(), ke, st

### Community 50 - "Community 50"
Cohesion: 0.26
Nodes (12): _clean_text(), fetch_contributors(), _first(), _num(), _parse(), _parse_sector_movers(), nepse_contributors.py — official NEPSE index + index point-contributors.  Source, Return index, stock contributors and sector contributors from HATHLYTICS. (+4 more)

### Community 52 - "Community 52"
Cohesion: 0.14
Nodes (3): Cn, nt, on

### Community 53 - "Community 53"
Cohesion: 0.18
Nodes (4): bn, mn, vt(), wn()

### Community 56 - "Community 56"
Cohesion: 0.11
Nodes (7): bs(), ct, dt(), Ft, mt(), pt(), wt

### Community 60 - "Community 60"
Cohesion: 0.18
Nodes (3): ii, k(), u()

### Community 61 - "Community 61"
Cohesion: 0.11
Nodes (5): ci(), ji, oi(), qi(), ui()

### Community 62 - "Community 62"
Cohesion: 0.18
Nodes (3): kn, qt, vs()

### Community 67 - "Community 67"
Cohesion: 0.12
Nodes (3): hs(), jn(), se()

### Community 68 - "Community 68"
Cohesion: 0.29
Nodes (3): nn(), ot(), R()

### Community 69 - "Community 69"
Cohesion: 0.36
Nodes (7): DataFrame, _prepare_price_frame(), Calculates Relative Rotation Graph (RRG) coordinates (RS-Ratio and RS-Momentum), run_rrg_simulation(), _format_date(), ordered_nepse_indices(), run_rrg_indices_simulation()

### Community 74 - "Community 74"
Cohesion: 0.29
Nodes (5): _env_bool(), _load_dotenv(), Django settings for nepse_project project.  Generated by 'django-admin startpr, Load KEY=VALUE pairs from a .env file into os.environ.      Uses python-dotenv, Parse a boolean from an environment variable ('1', 'true', 'yes', 'on').

### Community 77 - "Community 77"
Cohesion: 0.40
Nodes (5): Series, _calc_t3_internal(), STRICT STRATEGY EXPERIMENTATION ENGINE     Runs the Tillson T3MA Ribbon + MACD, Isolated mathematical Tillson T3 Moving Average computation., run_t3ma_macd_ribbon_simulation()

### Community 78 - "Community 78"
Cohesion: 0.53
Nodes (4): calcUrl(), handleSubmit(), nativeFallback(), resultsContainer()

### Community 79 - "Community 79"
Cohesion: 0.47
Nodes (5): calculate_macd(), Backward-compatible MACD calculator used by existing architecture.     Returns a, Long-only NEPSE strategy using MACD + Supertrend + VWAP + ATR + RVOL.     Entry:, run_msv_long_only_simulation(), _to_dataframe()

### Community 80 - "Community 80"
Cohesion: 0.53
Nodes (5): _as_bool(), calculate_stage_analysis(), _coerce_float(), _coerce_int(), NEPSE-adapted Stage Analysis (Weinstein method).      Returns an annotated dataf

### Community 83 - "Community 83"
Cohesion: 0.50
Nodes (4): Series, _compute_rsi(), RSI/RSI-SMA long-only strategy for one-way markets (NEPSE):     1. BUY when RSI, run_rsi_sma_long_only_simulation()

### Community 84 - "Community 84"
Cohesion: 0.50
Nodes (4): _history_window(), indicator_data(), Parse UDF-style history window parameters from the indicator request., Compute one indicator's series for a symbol.

### Community 86 - "Community 86"
Cohesion: 0.50
Nodes (3): fetch_live_index_rows(), live_index.py — intraday live NEPSE index / sub-index quotes.  Pulls the interna, Return a list of raw live-index dicts, or None if the feed is unavailable.

## Knowledge Gaps
- **7 isolated node(s):** `Migration`, `Migration`, `Migration`, `Migration`, `Meta` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **42 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_()` connect `Community 7` to `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 15`, `Community 16`, `Community 18`, `Community 22`, `Community 23`, `Community 25`, `Community 26`, `Community 27`, `Community 28`, `Community 29`, `Community 30`, `Community 31`, `Community 33`, `Community 34`, `Community 36`, `Community 37`, `Community 38`, `Community 43`, `Community 44`, `Community 45`, `Community 46`, `Community 47`, `Community 52`, `Community 53`, `Community 54`, `Community 55`, `Community 56`, `Community 57`, `Community 58`, `Community 60`, `Community 61`, `Community 62`, `Community 64`, `Community 65`, `Community 66`, `Community 67`, `Community 68`, `Community 72`, `Community 76`, `Community 88`, `Community 89`, `Community 93`, `Community 111`?**
  _High betweenness centrality (0.200) - this node is a cross-community bridge._
- **Why does `vn` connect `Community 111` to `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 18`, `Community 21`, `Community 22`, `Community 23`, `Community 26`, `Community 28`, `Community 31`, `Community 34`, `Community 36`, `Community 37`, `Community 39`, `Community 42`, `Community 43`, `Community 49`, `Community 51`, `Community 55`, `Community 58`, `Community 64`, `Community 66`, `Community 67`, `Community 72`, `Community 73`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `sn()` connect `Community 64` to `Community 67`, `Community 68`, `Community 37`, `Community 7`, `Community 73`, `Community 42`, `Community 11`, `Community 49`, `Community 18`, `Community 51`, `Community 53`, `Community 54`, `Community 23`, `Community 28`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **What connects `api_urls.py — router for the read-only Data API (mounted at /api/v1/).  Kept sep`, `api_views.py — read-only Data API over every database table.  Each model is expo`, `Page-number pagination with a caller-tunable, hard-capped page size.      The pr` to the rest of the system?**
  _171 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.0530442035029191 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.060527825588066554 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.05886708626434654 - nodes in this community are weakly interconnected._