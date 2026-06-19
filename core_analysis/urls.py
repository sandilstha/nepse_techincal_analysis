from django.urls import path
from .views import (
    crud_dashboard_view,
    dashboard_tab_calc,
    crud_operations_handler,
    crud_delete_handler,
    trigger_daily_api_sync_view,
    trigger_floorsheet_sync_view,
    symbol_autocomplete_view,
    trigger_sync_and_calculate
)
from .insights_views import (
    market_insights_view,
    market_insights_api,
    subindex_comparison_api,
    technical_analysis_view,
)
from .broker_views import (
    floorsheet_view,
    broker_meta_api,
    broker_favorites_api,
    broker_persistence_api,
    broker_signals_api,
    stock_wise_api,
    net_holding_api,
    broker_concentration_api,
    hotstocks_api,
    broker_trend_api,
)
from .udf_views import (
    udf_config,
    udf_time,
    udf_symbols,
    udf_search,
    udf_history,
)
from .indicator_views import indicator_catalog, indicator_data

urlpatterns = [

    # Market Insights is the landing page (served at root); /insights/ kept as an alias.
    path('', market_insights_view, name='market_insights'),
    path('insights/', market_insights_view),
    path('insights/api/', market_insights_api, name='market_insights_api'),
    path('insights/subindices/', subindex_comparison_api, name='subindex_comparison_api'),

    # Technical Analysis terminal (Lightweight Charts: price + volume + indicators).
    path('chart/', technical_analysis_view, name='technical_analysis'),
    path('chart/indicators', indicator_catalog, name='indicator_catalog'),
    path('chart/indicator', indicator_data, name='indicator_data'),
    path('chart/<str:symbol>/', technical_analysis_view, name='technical_analysis_symbol'),

    # Floor sheet — Dalal Street X broker analytics (built on the floorsheet feed).
    path('floorsheet/', floorsheet_view, name='floorsheet'),
    path('floorsheet/api/meta/', broker_meta_api, name='broker_meta_api'),
    path('floorsheet/api/favorites/', broker_favorites_api, name='broker_favorites_api'),
    path('floorsheet/api/persistence/', broker_persistence_api, name='broker_persistence_api'),
    path('floorsheet/api/signals/', broker_signals_api, name='broker_signals_api'),
    path('floorsheet/api/stockwise/', stock_wise_api, name='stock_wise_api'),
    path('floorsheet/api/netholding/', net_holding_api, name='net_holding_api'),
    path('floorsheet/api/concentration/', broker_concentration_api, name='broker_concentration_api'),
    path('floorsheet/api/hotstocks/', hotstocks_api, name='hotstocks_api'),
    path('floorsheet/api/trend/', broker_trend_api, name='broker_trend_api'),

    # Analytics workbench (moved off root to /workbench/)
    path('workbench/', crud_dashboard_view, name='crud_dashboard'),
    # AJAX: run one tab's calculation and return only its results partial.
    path('workbench/calc/', dashboard_tab_calc, name='dashboard_tab_calc'),
    path('dashboard/process/', crud_operations_handler, name='crud_operations'),
    path('dashboard/delete/<int:pk>/', crud_delete_handler, name='crud_delete'),
    path('dashboard/sync/', trigger_daily_api_sync_view, name='trigger_daily_sync'),
    path('dashboard/sync-floorsheet/', trigger_floorsheet_sync_view, name='trigger_floorsheet_sync'),
    path('dashboard/sync-calculate/', trigger_sync_and_calculate, name='trigger_sync_and_calculate'),
    # NEW — lightweight autocomplete endpoint for symbol search boxes
    path('dashboard/symbols/', symbol_autocomplete_view, name='symbol_autocomplete'),

    # TradingView Advanced Charts UDF datafeed (no trailing slashes — UDF spec)
    path('insights/udf/config', udf_config, name='udf_config'),
    path('insights/udf/time', udf_time, name='udf_time'),
    path('insights/udf/symbols', udf_symbols, name='udf_symbols'),
    path('insights/udf/search', udf_search, name='udf_search'),
    path('insights/udf/history', udf_history, name='udf_history'),
]