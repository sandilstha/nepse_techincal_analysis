from django.urls import path
from .views import (
    crud_dashboard_view, 
    crud_operations_handler, 
    crud_delete_handler,
    trigger_daily_api_sync_view,
    symbol_autocomplete_view,
    trigger_sync_and_calculate
)

urlpatterns = [
    
    # HTML View Form CRUD Engine Interfaces
    path('', crud_dashboard_view, name='crud_dashboard'),
    path('dashboard/process/', crud_operations_handler, name='crud_operations'),
    path('dashboard/delete/<int:pk>/', crud_delete_handler, name='crud_delete'),
    path('dashboard/sync/', trigger_daily_api_sync_view, name='trigger_daily_sync'),
    path('dashboard/sync-calculate/', trigger_sync_and_calculate, name='trigger_sync_and_calculate'),
    # NEW — lightweight autocomplete endpoint for symbol search boxes
    path('dashboard/symbols/', symbol_autocomplete_view, name='symbol_autocomplete'),
]