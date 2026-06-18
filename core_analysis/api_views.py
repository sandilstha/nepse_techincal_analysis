"""
api_views.py — read-only Data API over every database table.

Each model is exposed as a DRF ReadOnlyModelViewSet (list + retrieve only —
the data is owned by the sync pipeline, never mutated through the API). Records
are paginated (?page=, ?page_size=) and orderable (?ordering=); the price/index
viewsets add explicit query-param filters for the columns callers actually slice
on — symbol, sector and a business_date range — implemented by hand so no extra
dependency (django-filter) is required.

Routes (wired in api_urls.py under /api/v1/):
    GET /api/v1/companies/                 list companies        (?sector=, ?status=, ?search=)
    GET /api/v1/companies/<symbol>/        one company
    GET /api/v1/price-adjustments/         adjusted price rows   (?symbol=, ?date_from=, ?date_to=)
    GET /api/v1/daily-prices/              raw daily price rows  (?symbol=, ?date_from=, ?date_to=)
    GET /api/v1/indices/                   index rows            (?sector=, ?date_from=, ?date_to=)
"""
from __future__ import annotations

from datetime import date

from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination

from core_analysis.models import (
    CompanyProfile,
    NepseDailyStockPrice,
    NepseMarketIndex,
    StockPriceAdjustment,
)
from core_analysis.serializers import (
    CompanyProfileSerializer,
    NepseDailyStockPriceSerializer,
    NepseMarketIndexSerializer,
    StockPriceAdjustmentSerializer,
)


class StandardPagination(PageNumberPagination):
    """Page-number pagination with a caller-tunable, hard-capped page size.

    The price/index tables hold years of daily rows, so an unbounded list would
    be enormous. Default 100 per page; callers may raise it with ?page_size= up
    to a 1000 ceiling so a runaway value can't pull the whole table into memory.
    """

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


def _parse_date(raw, param_name):
    """Parse an ISO YYYY-MM-DD query param, raising a clean 400 on bad input."""
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise ValidationError({param_name: "Expected a date in YYYY-MM-DD format."})


class _DateRangeFilterMixin:
    """Apply ?date_from= / ?date_to= (inclusive) on the model's date field."""

    date_field = "business_date"

    def filter_date_range(self, queryset):
        params = self.request.query_params
        date_from = _parse_date(params.get("date_from"), "date_from")
        date_to = _parse_date(params.get("date_to"), "date_to")
        if date_from:
            queryset = queryset.filter(**{f"{self.date_field}__gte": date_from})
        if date_to:
            queryset = queryset.filter(**{f"{self.date_field}__lte": date_to})
        return queryset


class CompanyProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """Listed companies. Filter with ?sector= / ?status=, free-text ?search=."""

    serializer_class = CompanyProfileSerializer
    pagination_class = StandardPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["symbol", "security_name"]
    ordering_fields = ["symbol", "security_name", "sector_name", "status"]
    ordering = ["symbol"]
    lookup_field = "symbol"
    # Symbols can contain characters the default \w+ path converter rejects on
    # lookup; allow anything non-slash so /companies/<symbol>/ always resolves.
    lookup_value_regex = "[^/]+"

    def get_queryset(self):
        qs = CompanyProfile.objects.all()
        params = self.request.query_params
        sector = (params.get("sector") or "").strip()
        status = (params.get("status") or "").strip()
        if sector:
            qs = qs.filter(sector_name__iexact=sector)
        if status:
            qs = qs.filter(status__iexact=status)
        return qs


class StockPriceAdjustmentViewSet(_DateRangeFilterMixin, viewsets.ReadOnlyModelViewSet):
    """Corporate-action-adjusted daily prices. ?symbol=, ?date_from=, ?date_to=."""

    serializer_class = StockPriceAdjustmentSerializer
    pagination_class = StandardPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ["business_date", "company"]
    ordering = ["-business_date"]

    def get_queryset(self):
        qs = StockPriceAdjustment.objects.select_related("company")
        symbol = (self.request.query_params.get("symbol") or "").strip().upper()
        if symbol:
            qs = qs.filter(company_id=symbol)
        return self.filter_date_range(qs)


class NepseDailyStockPriceViewSet(_DateRangeFilterMixin, viewsets.ReadOnlyModelViewSet):
    """Raw daily transaction rows. ?symbol=, ?date_from=, ?date_to=."""

    serializer_class = NepseDailyStockPriceSerializer
    pagination_class = StandardPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ["business_date", "symbol", "total_traded_value"]
    ordering = ["-business_date"]

    def get_queryset(self):
        qs = NepseDailyStockPrice.objects.all()
        symbol = (self.request.query_params.get("symbol") or "").strip().upper()
        if symbol:
            qs = qs.filter(symbol=symbol)
        return self.filter_date_range(qs)


class NepseMarketIndexViewSet(_DateRangeFilterMixin, viewsets.ReadOnlyModelViewSet):
    """Sector / macro index rows. ?sector=, ?date_from=, ?date_to=."""

    serializer_class = NepseMarketIndexSerializer
    pagination_class = StandardPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ["business_date", "sector_name"]
    ordering = ["-business_date"]

    def get_queryset(self):
        qs = NepseMarketIndex.objects.all()
        sector = (self.request.query_params.get("sector") or "").strip().upper()
        if sector:
            qs = qs.filter(sector_name__iexact=sector)
        return self.filter_date_range(qs)
