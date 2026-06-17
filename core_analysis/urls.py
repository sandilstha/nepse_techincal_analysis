from django.urls import path
from .views import (
    crud_dashboard_view,
    crud_operations_handler,
    crud_delete_handler,
    trigger_daily_api_sync_view,
    symbol_autocomplete_view,
    trigger_sync_and_calculate
)
from .insights_views import (
    market_insights_view,
    market_insights_api,
    subindex_comparison_api,
    floorsheet_view,
    technical_analysis_view,
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

    # Floor sheet (placeholder until a trade-level data source is wired up).
    path('floorsheet/', floorsheet_view, name='floorsheet'),

    # Analytics workbench (moved off root to /workbench/)
    path('workbench/', crud_dashboard_view, name='crud_dashboard'),
    path('dashboard/process/', crud_operations_handler, name='crud_operations'),
    path('dashboard/delete/<int:pk>/', crud_delete_handler, name='crud_delete'),
    path('dashboard/sync/', trigger_daily_api_sync_view, name='trigger_daily_sync'),
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