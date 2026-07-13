from django.contrib.auth import views as auth_views
from django.urls import path
from .portfolio_views import (
    approval_pending_view,
    register_view,
    portfolio_view,
    portfolio_sop_view,
    portfolio_data_api,
    portfolio_manage,
    portfolio_approvals_api,
    portfolio_approval_action,
    portfolio_import,
    portfolio_wacc_import,
    portfolio_ledger_import,
    portfolio_clear,
)
from .views import (
    crud_dashboard_view,
    dashboard_tab_calc,
    gemini_sr_analysis,
    crud_operations_handler,
    crud_delete_handler,
    trigger_daily_api_sync_view,
    trigger_floorsheet_sync_view,
    symbol_autocomplete_view,
    trigger_sync_and_calculate,
    stage_sop_view,
)
from .insights_views import (
    market_insights_view,
    market_insights_api,
    subindex_comparison_api,
    technical_analysis_view,
)
from .broker_views import (
    floorsheet_view,
    floorsheet_sop_view,
    broker_meta_api,
    broker_favorites_api,
    broker_persistence_api,
    broker_signals_api,
    stock_wise_api,
    net_holding_api,
    broker_concentration_api,
    hotstocks_api,
    broker_flow_radar_api,
)
from .udf_views import (
    udf_config,
    udf_time,
    udf_symbols,
    udf_search,
    udf_history,
)
from .analytics_views import site_stats_view
from .indicator_views import indicator_catalog, indicator_data
from .fundamental_views import (
    fundamental_analysis_view,
    fundamental_sop_view,
    fundamental_data_api,
    fundamental_matrix_api,
    fundamental_model_api,
)

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

    # Fundamental Analysis Desk — company financial statements + ratios.
    path('fundamentals/', fundamental_analysis_view, name='fundamental_analysis'),
    path('fundamentals/api/', fundamental_data_api, name='fundamental_data_api'),
    path('fundamentals/matrix/', fundamental_matrix_api, name='fundamental_matrix_api'),
    path('fundamentals/model/', fundamental_model_api, name='fundamental_model_api'),
    path('fundamentals/sop/', fundamental_sop_view, name='fundamental_sop'),
    path('fundamentals/<str:symbol>/', fundamental_analysis_view, name='fundamental_analysis_symbol'),

    # Auth (user-facing; the workbench keeps its separate admin/staff login).
    path('accounts/login/', auth_views.LoginView.as_view(next_page='portfolio'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/register/', register_view, name='register'),
    path('accounts/approval-pending/', approval_pending_view, name='approval_pending'),

    # Risk & Portfolio Desk — private, per-user holdings + risk analytics.
    path('portfolio/', portfolio_view, name='portfolio'),
    path('portfolio/sop/', portfolio_sop_view, name='portfolio_sop'),
    path('portfolio/api/data/', portfolio_data_api, name='portfolio_data_api'),
    path('portfolio/manage/', portfolio_manage, name='portfolio_manage'),
    path('portfolio/api/approvals/', portfolio_approvals_api, name='portfolio_approvals_api'),
    path('portfolio/api/approvals/action/', portfolio_approval_action, name='portfolio_approval_action'),
    path('portfolio/import/', portfolio_import, name='portfolio_import'),
    path('portfolio/wacc/', portfolio_wacc_import, name='portfolio_wacc_import'),
    path('portfolio/ledger/', portfolio_ledger_import, name='portfolio_ledger_import'),
    path('portfolio/clear/', portfolio_clear, name='portfolio_clear'),

    # Floor sheet — Dalal Street X broker analytics (built on the floorsheet feed).
    path('floorsheet/', floorsheet_view, name='floorsheet'),
    path('floorsheet/sop/', floorsheet_sop_view, name='floorsheet_sop'),
    path('floorsheet/api/meta/', broker_meta_api, name='broker_meta_api'),
    path('floorsheet/api/favorites/', broker_favorites_api, name='broker_favorites_api'),
    path('floorsheet/api/persistence/', broker_persistence_api, name='broker_persistence_api'),
    path('floorsheet/api/signals/', broker_signals_api, name='broker_signals_api'),
    path('floorsheet/api/stockwise/', stock_wise_api, name='stock_wise_api'),
    path('floorsheet/api/netholding/', net_holding_api, name='net_holding_api'),
    path('floorsheet/api/concentration/', broker_concentration_api, name='broker_concentration_api'),
    path('floorsheet/api/hotstocks/', hotstocks_api, name='hotstocks_api'),
    path('floorsheet/api/flow-radar/', broker_flow_radar_api, name='broker_flow_radar_api'),

    # Analytics workbench (moved off root to /workbench/)
    path('workbench/', crud_dashboard_view, name='crud_dashboard'),
    # Methodology SOP for the Stage Analysis desk (Technical Analysis tab).
    path('stage/sop/', stage_sop_view, name='stage_sop'),
    # AJAX: run one tab's calculation and return only its results partial.
    path('workbench/calc/', dashboard_tab_calc, name='dashboard_tab_calc'),
    # AJAX: Gemini narrative for the Support & Resistance tab (JSON).
    path('workbench/ai-analysis/', gemini_sr_analysis, name='gemini_sr_analysis'),
    path('dashboard/process/', crud_operations_handler, name='crud_operations'),
    path('dashboard/delete/<int:pk>/', crud_delete_handler, name='crud_delete'),
    path('dashboard/sync/', trigger_daily_api_sync_view, name='trigger_daily_sync'),
    path('dashboard/sync-floorsheet/', trigger_floorsheet_sync_view, name='trigger_floorsheet_sync'),
    path('dashboard/sync-calculate/', trigger_sync_and_calculate, name='trigger_sync_and_calculate'),
    # NEW — lightweight autocomplete endpoint for symbol search boxes
    path('dashboard/symbols/', symbol_autocomplete_view, name='symbol_autocomplete'),

    # Self-hosted visit analytics — "how many times the site was opened" (staff only).
    path('stats/', site_stats_view, name='site_stats'),

    # TradingView Advanced Charts UDF datafeed (no trailing slashes — UDF spec)
    path('insights/udf/config', udf_config, name='udf_config'),
    path('insights/udf/time', udf_time, name='udf_time'),
    path('insights/udf/symbols', udf_symbols, name='udf_symbols'),
    path('insights/udf/search', udf_search, name='udf_search'),
    path('insights/udf/history', udf_history, name='udf_history'),
]
