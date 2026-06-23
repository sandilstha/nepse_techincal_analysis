# Graph Report - nepse_analytics_platform  (2026-06-23)

## Corpus Check
- 66 files · ~83,103 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1934 nodes · 4837 edges · 122 communities (74 shown, 48 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 131 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `934d789c`
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
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
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
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 87|Community 87]]
- [[_COMMUNITY_Community 88|Community 88]]
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]
- [[_COMMUNITY_Community 91|Community 91]]
- [[_COMMUNITY_Community 92|Community 92]]
- [[_COMMUNITY_Community 93|Community 93]]
- [[_COMMUNITY_Community 94|Community 94]]
- [[_COMMUNITY_Community 95|Community 95]]
- [[_COMMUNITY_Community 96|Community 96]]
- [[_COMMUNITY_Community 97|Community 97]]
- [[_COMMUNITY_Community 98|Community 98]]
- [[_COMMUNITY_Community 99|Community 99]]
- [[_COMMUNITY_Community 100|Community 100]]
- [[_COMMUNITY_Community 101|Community 101]]
- [[_COMMUNITY_Community 110|Community 110]]
- [[_COMMUNITY_Community 112|Community 112]]
- [[_COMMUNITY_Community 113|Community 113]]
- [[_COMMUNITY_Community 114|Community 114]]
- [[_COMMUNITY_Community 115|Community 115]]
- [[_COMMUNITY_Community 116|Community 116]]
- [[_COMMUNITY_Community 117|Community 117]]
- [[_COMMUNITY_Community 118|Community 118]]
- [[_COMMUNITY_Community 119|Community 119]]
- [[_COMMUNITY_Community 120|Community 120]]
- [[_COMMUNITY_Community 121|Community 121]]

## God Nodes (most connected - your core abstractions)
1. `_()` - 162 edges
2. `vn` - 114 edges
3. `sn()` - 68 edges
4. `f()` - 61 edges
5. `as()` - 58 edges
6. `yi` - 56 edges
7. `fs()` - 42 edges
8. `NepseMarketIndex` - 38 edges
9. `hs()` - 38 edges
10. `pn` - 37 edges

## Surprising Connections (you probably didn't know these)
- `Command` --uses--> `CompanyProfile`  [INFERRED]
  core_analysis/management/commands/sync_and_calculate.py → core_analysis/models.py
- `Command` --uses--> `StockPriceAdjustment`  [INFERRED]
  core_analysis/management/commands/sync_and_calculate.py → core_analysis/models.py
- `Command` --uses--> `NepseFloorsheet`  [INFERRED]
  core_analysis/management/commands/sync_floorsheet.py → core_analysis/models.py
- `Command` --uses--> `NepseDailyStockPrice`  [INFERRED]
  core_analysis/management/commands/sync_nepse_data.py → core_analysis/models.py
- `Command` --uses--> `NepseMarketIndex`  [INFERRED]
  core_analysis/management/commands/sync_nepse_data.py → core_analysis/models.py

## Import Cycles
- None detected.

## Communities (122 total, 48 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.18
Nodes (34): api_urls.py — router for the read-only Data API (mounted at /api/v1/).  Kept sep, CompanyProfileViewSet, _DateRangeFilterMixin, NepseDailyStockPriceViewSet, NepseFloorsheetViewSet, NepseMarketIndexViewSet, api_views.py — read-only Data API over every database table.  Each model is expo, Corporate-action-adjusted daily prices. ?symbol=, ?date_from=, ?date_to=. (+26 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (81): Any, DataFrame, Series, SupportResistanceTests, _add_level(), _add_retracements(), _add_window_extremes(), _bollinger_headline() (+73 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (23): Any, DataFrame, Series, AdvancedMarketStructureTests, BrokerFlowRadarTests, FakeTechnicalAnalysis, IMMScoringTests, IndicatorHistoryWindowTests (+15 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (65): fetch_live_rows(), live_price.py — intraday live NEPSE quotes for the Market Insights dashboard.  P, Return a list of raw live-quote dicts, or None if the feed is unavailable., _breadth(), _build_eod_payload(), build_payload(), _contributors_index_metrics(), _enrich() (+57 more)

### Community 4 - "Community 4"
Cohesion: 0.15
Nodes (15): broker_flow_radar(), broker_names(), _build_meta(), _company_meta(), _company_names(), _fallback_brokers(), meta(), meta_cached() (+7 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (47): onChange(), activateTab(), brokerName(), buildBrokerMulti(), buildBrokerTable(), buildConcTable(), buildFavTable(), buildFlowTable() (+39 more)

### Community 6 - "Community 6"
Cohesion: 0.14
Nodes (51): applyTheme(), baseChartOpts(), computeGreed(), cssVar(), deferNonCritical(), destroyCharts(), dirClass(), el() (+43 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (15): _(), b(), ce(), de(), dt(), fe(), hi(), In() (+7 more)

### Community 8 - "Community 8"
Cohesion: 0.18
Nodes (3): ii, k(), u()

### Community 9 - "Community 9"
Cohesion: 0.05
Nodes (5): nn(), ot(), R(), yi, zi

### Community 10 - "Community 10"
Cohesion: 0.25
Nodes (5): an(), en(), hn(), ln(), tn()

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (7): gs(), ks(), ls(), ms(), Ss(), ws, xs()

### Community 13 - "Community 13"
Cohesion: 0.25
Nodes (18): _asset_version(), broker_concentration_api(), broker_favorites_api(), broker_flow_radar_api(), broker_meta_api(), broker_persistence_api(), broker_signals_api(), broker_trend_api() (+10 more)

### Community 14 - "Community 14"
Cohesion: 0.18
Nodes (28): $(), addChip(), addIndicator(), addOscPane(), alignIndicatorSeries(), allCharts(), barTimeLookup(), baseOptions() (+20 more)

### Community 17 - "Community 17"
Cohesion: 0.15
Nodes (26): DataFrame, Series, _build_position_signals(), _build_position_signals_with_atr_stop(), _calculate_atr_trailing_stop(), calculate_relative_strength(), calculate_technical_score(), calculate_volume_greed() (+18 more)

### Community 19 - "Community 19"
Cohesion: 0.10
Nodes (28): _history_window(), indicator_data(), Parse UDF-style history window parameters from the indicator request., Compute one indicator's series for a symbol., _append_live_index_bar(), _bars(), _chart_bars(), _clean_symbol() (+20 more)

### Community 21 - "Community 21"
Cohesion: 0.22
Nodes (15): _build_url(), _can_stop_after_ascending_page(), _clean_date(), _clean_decimal(), _clean_int(), _clean_text(), Command, _configure_session() (+7 more)

### Community 24 - "Community 24"
Cohesion: 0.21
Nodes (23): _adx(), _arr(), _atr(), _bbands(), _cci(), _cmf(), _ema(), _emit() (+15 more)

### Community 25 - "Community 25"
Cohesion: 0.13
Nodes (3): ds(), Ts(), zs

### Community 32 - "Community 32"
Cohesion: 0.21
Nodes (16): a(), c(), d(), e(), f(), g(), h(), i() (+8 more)

### Community 33 - "Community 33"
Cohesion: 0.09
Nodes (3): ai, ei, Ri

### Community 36 - "Community 36"
Cohesion: 0.27
Nodes (13): _build_url(), _can_stop_after_page(), _clean_date(), _clean_datetime(), _clean_decimal(), _clean_int(), _clean_text(), Command (+5 more)

### Community 38 - "Community 38"
Cohesion: 0.22
Nodes (13): _build_url(), _clean_date(), _clean_decimal(), _clean_int(), _clean_text(), _clean_time(), Command, _configure_session() (+5 more)

### Community 39 - "Community 39"
Cohesion: 0.13
Nodes (4): ee(), le(), ne(), qn()

### Community 40 - "Community 40"
Cohesion: 0.17
Nodes (15): _asset_version(), _empty_payload(), market_insights_api(), market_insights_view(), insights_views.py — view layer for the Market Insights dashboard.  Two endpoints, Render the dashboard shell instantly.      The payload is embedded ONLY if it is, MetaStock-style charting terminal (Lightweight Charts).      Renders price (OHLC, JSON multi-series feed for the sub-index comparison chart.      Accepts ?days=<s (+7 more)

### Community 41 - "Community 41"
Cohesion: 0.26
Nodes (16): $(), applyColors(), buildSeries(), chartOptions(), cssVar(), deferInitialFetch(), DrawingLayer(), fetchBars() (+8 more)

### Community 44 - "Community 44"
Cohesion: 0.13
Nodes (3): Et, kt, te()

### Community 45 - "Community 45"
Cohesion: 0.19
Nodes (5): A(), Js(), qs(), ye(), zt

### Community 50 - "Community 50"
Cohesion: 0.26
Nodes (12): _clean_text(), fetch_contributors(), _first(), _num(), _parse(), _parse_sector_movers(), nepse_contributors.py — official NEPSE index + index point-contributors.  Source, Return index, stock contributors and sector contributors from HATHLYTICS. (+4 more)

### Community 51 - "Community 51"
Cohesion: 0.21
Nodes (4): H, I, X(), Z()

### Community 53 - "Community 53"
Cohesion: 0.07
Nodes (33): _build_benchmark_sparkline(), build_dashboard_context(), _build_index_dataframes(), _build_rrg_index_choices(), _build_standard_dataframe(), crud_dashboard_view(), crud_delete_handler(), crud_operations_handler() (+25 more)

### Community 56 - "Community 56"
Cohesion: 0.22
Nodes (3): bs(), Ft, wt

### Community 57 - "Community 57"
Cohesion: 0.38
Nodes (3): d(), jt, v()

### Community 58 - "Community 58"
Cohesion: 0.15
Nodes (16): broker_concentration(), broker_favorites(), hotstocks(), _metric_index(), Return a date object if ``raw`` is a valid ISO 'YYYY-MM-DD', else None., Resolve the aggregate for a tab's date selection.      ``range_key`` == 'custo, 0 = quantity (shares traded), 1 = amount (turnover)., Total traded shares for a symbol on the buy side (== sell side). (+8 more)

### Community 60 - "Community 60"
Cohesion: 0.11
Nodes (3): Cn, on, st

### Community 61 - "Community 61"
Cohesion: 0.11
Nodes (5): ci(), ji, oi(), qi(), ui()

### Community 62 - "Community 62"
Cohesion: 0.18
Nodes (3): kn, qt, vs()

### Community 65 - "Community 65"
Cohesion: 0.20
Nodes (5): ae(), it, O(), oe(), ue()

### Community 67 - "Community 67"
Cohesion: 0.12
Nodes (3): hs(), jn(), se()

### Community 69 - "Community 69"
Cohesion: 0.36
Nodes (7): DataFrame, _prepare_price_frame(), Calculates Relative Rotation Graph (RRG) coordinates (RS-Ratio and RS-Momentum), run_rrg_simulation(), _format_date(), ordered_nepse_indices(), run_rrg_indices_simulation()

### Community 72 - "Community 72"
Cohesion: 0.11
Nodes (4): ie(), pe(), ve(), zn()

### Community 74 - "Community 74"
Cohesion: 0.29
Nodes (5): _env_bool(), _load_dotenv(), Django settings for nepse_project project.  Generated by 'django-admin startpr, Load KEY=VALUE pairs from a .env file into os.environ.      Uses python-dotenv, Parse a boolean from an environment variable ('1', 'true', 'yes', 'on').

### Community 75 - "Community 75"
Cohesion: 0.22
Nodes (4): _parse_date(), _parse_int(), Parse an integer query param, raising a clean 400 on bad input., Parse an ISO YYYY-MM-DD query param, raising a clean 400 on bad input.

### Community 76 - "Community 76"
Cohesion: 0.21
Nodes (7): BaseCommand, _clean(), Command, load_brokers — seed / refresh the ``nepse_brokers`` reference table from the bun, Broker, Meta, Table: nepse_brokers     Reference list of NEPSE stock brokers (and stock deale

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

### Community 81 - "Community 81"
Cohesion: 0.22
Nodes (11): _day_has_rows(), get_latest_trading_date(), get_range_aggregate(), _is_latest(), _local_trading_dates(), List of trading-day strings for a range, newest first (incl. latest)., Trading dates from the local EOD table; avoids 90 cheap upstream probes., Sum of every day aggregate in the range. Cached. None if nothing built. (+3 more)

### Community 82 - "Community 82"
Cohesion: 0.12
Nodes (4): bn, mn, vt(), wn()

### Community 83 - "Community 83"
Cohesion: 0.50
Nodes (4): Series, _compute_rsi(), RSI/RSI-SMA long-only strategy for one-way markets (NEPSE):     1. BUY when RSI, run_rsi_sma_long_only_simulation()

### Community 86 - "Community 86"
Cohesion: 0.50
Nodes (3): fetch_live_index_rows(), live_index.py — intraday live NEPSE index / sub-index quotes.  Pulls the interna, Return a list of raw live-index dicts, or None if the feed is unavailable.

### Community 87 - "Community 87"
Cohesion: 0.29
Nodes (3): fi(), pi(), wi()

### Community 93 - "Community 93"
Cohesion: 0.25
Nodes (9): broker_persistence(), _is_mutual_fund(), net_holding(), Daily traded quantity (from cached day aggregates) + closing price (DB)., Match the dropdown's string broker against int keys in the aggregate., Per-stock net position for one or more brokers (Net Holding treemap).      Whe, Multi-day persistence + concentration for a desk (Broker Flow headline)., trend() (+1 more)

### Community 94 - "Community 94"
Cohesion: 0.33
Nodes (7): _cached_day_value(), _fetch_day_rows(), get_day_aggregate(), Every floorsheet row for one business_date, as lightweight dicts.      Returns, Compact per-day aggregate (see module docstring). Cached. None on failure., _to_float(), _wait_for_day_build()

### Community 110 - "Community 110"
Cohesion: 0.33
Nodes (6): _custom_trading_dates(), get_custom_range_aggregate(), _merge_into(), Accumulate one side ({symbol: {broker: [qty, amt]}}) into dst., Trading-day strings within [start, end] inclusive, from the local EOD table., Sum of every day aggregate in an explicit [start, end] window (inclusive).

### Community 117 - "Community 117"
Cohesion: 0.50
Nodes (4): broker_signals(), Four research-desk signals for a broker selection, one window pass.      All d, % price change over the window for each symbol (first vs last close in it)., _window_close_changes()

### Community 120 - "Community 120"
Cohesion: 0.14
Nodes (4): bi(), G, vi(), xi

## Knowledge Gaps
- **8 isolated node(s):** `Migration`, `Migration`, `Migration`, `Migration`, `Migration` (+3 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **48 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_()` connect `Community 7` to `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 15`, `Community 16`, `Community 20`, `Community 22`, `Community 23`, `Community 25`, `Community 26`, `Community 29`, `Community 30`, `Community 31`, `Community 33`, `Community 34`, `Community 37`, `Community 39`, `Community 42`, `Community 44`, `Community 45`, `Community 46`, `Community 47`, `Community 48`, `Community 49`, `Community 51`, `Community 52`, `Community 54`, `Community 56`, `Community 57`, `Community 59`, `Community 60`, `Community 61`, `Community 62`, `Community 64`, `Community 65`, `Community 66`, `Community 67`, `Community 70`, `Community 71`, `Community 72`, `Community 73`, `Community 82`, `Community 84`, `Community 87`, `Community 88`, `Community 89`, `Community 112`, `Community 113`, `Community 114`, `Community 115`, `Community 116`, `Community 118`, `Community 120`?**
  _High betweenness centrality (0.179) - this node is a cross-community bridge._
- **Why does `vn` connect `Community 66` to `Community 7`, `Community 10`, `Community 11`, `Community 18`, `Community 20`, `Community 22`, `Community 23`, `Community 27`, `Community 28`, `Community 29`, `Community 31`, `Community 34`, `Community 37`, `Community 43`, `Community 55`, `Community 59`, `Community 63`, `Community 64`, `Community 67`, `Community 68`, `Community 71`, `Community 84`, `Community 107`, `Community 108`, `Community 111`, `Community 112`, `Community 118`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `sn()` connect `Community 64` to `Community 67`, `Community 68`, `Community 37`, `Community 7`, `Community 9`, `Community 10`, `Community 107`, `Community 82`, `Community 55`, `Community 54`, `Community 23`, `Community 27`, `Community 63`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **What connects `api_urls.py — router for the read-only Data API (mounted at /api/v1/).  Kept sep`, `api_views.py — read-only Data API over every database table.  Each model is expo`, `Page-number pagination with a caller-tunable, hard-capped page size.      The pr` to the rest of the system?**
  _177 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.058549931600547195 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.056842105263157895 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.05714285714285714 - nodes in this community are weakly interconnected._