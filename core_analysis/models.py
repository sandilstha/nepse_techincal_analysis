from django.conf import settings
from django.db import models
from django.utils import timezone

class Broker(models.Model):
    """
    Table: nepse_brokers
    Reference list of NEPSE stock brokers (and stock dealers), keyed by the
    broker number that appears as ``buyer`` / ``seller`` in the floorsheet feed.
    Used to resolve a broker number to a human-readable name across the broker
    analytics dashboard (Floor sheet page).
    """
    broker_number = models.IntegerField(
        primary_key=True, help_text="NEPSE broker code; matches floorsheet buyer/seller"
    )
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, default="ACTIVE", db_index=True)
    tms_link = models.CharField(max_length=255, null=True, blank=True)
    is_dealer = models.BooleanField(
        default=False, help_text="True if the firm also operates as a NEPSE stock dealer"
    )

    class Meta:
        db_table = 'nepse_brokers'
        ordering = ['broker_number']

    def __str__(self):
        return f"{self.broker_number} - {self.name}"


class CompanyProfile(models.Model):
    """
    Table: nepse_company_profiles
    Stores the unique list of companies from the /api/listed-companies/companies/ endpoint.
    """
    symbol = models.CharField(max_length=20, primary_key=True, db_index=True, help_text="Maps to script_ticker")
    security_name = models.CharField(max_length=255, help_text="Maps to company_name")
    sector_name = models.CharField(max_length=100, null=True, blank=True, help_text="Maps to sector")
    status = models.CharField(max_length=50, default="Active")

    class Meta:
        db_table = 'nepse_company_profiles'
        ordering = ['symbol']

    def __str__(self):
        return f"{self.symbol} - {self.security_name}"


class StockPriceAdjustment(models.Model):
    """
    Table: nepse_todayprice_adj
    Stores the daily historical pricing rows from the /api/stock-adjustments/stock-price-adj/ endpoint.
    """
    external_id = models.IntegerField(unique=True, help_text="The raw ID from the source API")
    business_date = models.DateField(db_index=True)
    
    # Foreign Key relationship mapping straight to the CompanyProfile table via its unique symbol
    # Django will treat 'company' as the object, but MySQL will name the actual column 'symbol'
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, to_field='symbol', db_column='symbol')
    security_id = models.IntegerField()
    
    # Raw Market Prices
    open_price = models.DecimalField(max_digits=12, decimal_places=2)
    high_price = models.DecimalField(max_digits=12, decimal_places=2)
    low_price = models.DecimalField(max_digits=12, decimal_places=2)
    close_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Corporate Action Adjusted Prices
    open_price_adj = models.DecimalField(max_digits=12, decimal_places=2)
    high_price_adj = models.DecimalField(max_digits=12, decimal_places=2)
    low_price_adj = models.DecimalField(max_digits=12, decimal_places=2)
    close_price_adj = models.DecimalField(max_digits=12, decimal_places=2)
    adjustment_factor = models.DecimalField(max_digits=14, decimal_places=10)
    average_traded_price_adj = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'nepse_todayprice_adj'
        ordering = ['-business_date', 'company'] # Changed from symbol to company
        
        # Composite unique constraint using the linked company relationship field
        unique_together = ('business_date', 'company')

    def __str__(self):
        return f"{self.company_id} - {self.business_date}"
    

class NepseDailyStockPrice(models.Model):
    """
    Table: nepse_daily_stock_prices
    Stores the raw daily transaction data rows from /api/stock-prices/
    """
    api_id = models.IntegerField(unique=True, help_text="Maps to JSON 'id'")
    business_date = models.DateField(db_index=True)
    security_id = models.CharField(max_length=20)
    symbol = models.CharField(max_length=20, db_index=True)
    security_name = models.CharField(max_length=255)
    
    # Pricing Matrix
    open_price = models.DecimalField(max_digits=12, decimal_places=2)
    high_price = models.DecimalField(max_digits=12, decimal_places=2)
    low_price = models.DecimalField(max_digits=12, decimal_places=2)
    close_price = models.DecimalField(max_digits=12, decimal_places=2)
    previous_close = models.DecimalField(max_digits=12, decimal_places=2)
    average_traded_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Volumetric Data
    total_traded_quantity = models.BigIntegerField()
    total_traded_value = models.DecimalField(max_digits=16, decimal_places=2)
    total_trades = models.IntegerField()
    market_capitalization = models.DecimalField(max_digits=16, decimal_places=2)
    
    # 52 Week Ranges
    fifty_two_week_high = models.DecimalField(max_digits=12, decimal_places=2)
    fifty_two_week_low = models.DecimalField(max_digits=12, decimal_places=2)
    
    last_updated_time = models.DateTimeField()

    class Meta:
        db_table = 'nepse_daily_stock_prices'
        ordering = ['-business_date', 'symbol']
        unique_together = ('business_date', 'symbol')

    def __str__(self):
        return f"{self.symbol} - {self.business_date}"


class NepseMarketIndex(models.Model):
    """
    Table: nepse_market_indices
    Stores historical daily sector and macro index data rows from /api/indices/
    """
    api_id = models.IntegerField(unique=True, help_text="Maps to JSON 'id'")
    business_date = models.DateField(db_index=True, help_text="Maps to JSON 'date'")
    sector_name = models.CharField(max_length=100, db_index=True, help_text="Maps to JSON 'sector'")
    
    # Index Coordinates
    open_index = models.DecimalField(max_digits=12, decimal_places=2, help_text="Maps to JSON 'open'")
    high_index = models.DecimalField(max_digits=12, decimal_places=2, help_text="Maps to JSON 'high'")
    low_index = models.DecimalField(max_digits=12, decimal_places=2, help_text="Maps to JSON 'low'")
    close_index = models.DecimalField(max_digits=12, decimal_places=2, help_text="Maps to JSON 'close'")
    
    # Variations
    absolute_change = models.DecimalField(max_digits=12, decimal_places=2)
    percentage_change = models.DecimalField(max_digits=6, decimal_places=4)
    
    # Volumetric Fields
    turnover_values = models.DecimalField(max_digits=18, decimal_places=2)
    turnover_volume = models.BigIntegerField()
    total_transaction = models.IntegerField()
    
    # 52 Week Ranges
    number_52_weeks_high = models.DecimalField(max_digits=12, decimal_places=2)
    number_52_weeks_low = models.DecimalField(max_digits=12, decimal_places=2)
    
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'nepse_market_indices'
        ordering = ['-business_date', 'sector_name']
        unique_together = ('business_date', 'sector_name')

    def __str__(self):
        return f"{self.sector_name} - {self.business_date}"


class NepseFloorsheet(models.Model):
    """
    Table: floorsheet_raw
    Stores trade-level floorsheet rows (one row per executed trade) from
    /api/nepse-data/api/floorsheet/. This is a high-volume table — tens of
    millions of rows — so it is synced day-by-day filtered on calculation_date.

    The upstream JSON 'id' is used directly as this table's primary key (it is a
    stable, globally-unique trade id), so there is no separate surrogate key and
    no `api_id` column. Most trade-economics columns are nullable to mirror the
    raw feed, which occasionally omits them.
    """
    # Source 'id' is the primary key (not auto-generated locally).
    id = models.BigIntegerField(primary_key=True, help_text="Maps to JSON 'id'")
    contract_no = models.CharField(
        max_length=255, null=True, blank=True, db_index=True, help_text="Maps to JSON 'contract_no'"
    )
    stock_symbol = models.CharField(max_length=50, db_index=True)

    # Counterparties (broker numbers).
    buyer = models.IntegerField(null=True, blank=True, db_index=True)
    seller = models.IntegerField(null=True, blank=True, db_index=True)

    # Trade economics.
    quantity = models.IntegerField(null=True, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    sector = models.CharField(max_length=100, null=True, blank=True, db_index=True)

    # DB column is `calculation_date`; kept as `business_date` in Python for
    # parity with the other NEPSE models and the analytics layer.
    business_date = models.DateField(
        db_column='calculation_date', db_index=True, help_text="Maps to JSON 'calculation_date'"
    )

    # Execution clock time (HH:MM:SS.ffffff), nullable for malformed rows.
    trade_time = models.TimeField(
        db_column='time', null=True, blank=True, help_text="Maps to JSON 'time'"
    )

    class Meta:
        db_table = 'floorsheet_raw'
        ordering = ['-business_date', 'stock_symbol']
        indexes = [
            models.Index(fields=['stock_symbol', 'business_date']),
            models.Index(fields=['business_date', 'buyer']),
            models.Index(fields=['business_date', 'seller']),
            models.Index(fields=['business_date', 'sector']),
        ]

    def __str__(self):
        return f"{self.contract_no} - {self.stock_symbol} - {self.business_date}"


class FinancialStatement(models.Model):
    """
    Table: fundamentals_financialstatdbs (read-only mapping).

    Company financial-statement line items (one row per
    ticker × fiscal year × quarter × statement type × item), as harvested by the
    separate ``fundamentals`` app that owns this table. We map it here only to
    *read* fundamentals alongside the price/floorsheet data — hence
    ``managed = False`` so Django never creates, alters or drops it, and the two
    foreign-key columns are mapped as plain integer ids (their parent tables,
    ``nepali_datetime_fiscalyear`` and ``fundamentals_accountdictionary``, are not
    modelled in this project).
    """
    id = models.BigAutoField(primary_key=True)

    # Identity / classification.
    sector = models.CharField(max_length=100, db_index=True)
    fiscal_year_ad = models.CharField(
        max_length=10, db_index=True, help_text="Gregorian fiscal year label, e.g. '2024/25'"
    )
    quarter = models.PositiveSmallIntegerField(db_index=True, help_text="0 = annual / 1–4 = quarter")
    data_source = models.CharField(max_length=20, db_index=True)
    ticker = models.CharField(max_length=20, db_index=True)
    fs_type = models.CharField(
        max_length=10, db_index=True, help_text="Statement type, e.g. BS / PL / CF"
    )

    # Line item.
    item_name = models.CharField(max_length=255)
    item_code = models.CharField(max_length=80, db_index=True)
    sorting_code = models.CharField(max_length=20, db_index=True)
    unit = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    remarks = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField()

    # Foreign-key columns from the source schema, kept as raw ids (their parent
    # tables live in other apps and aren't modelled here).
    fiscal_year_bs = models.BigIntegerField(
        db_column="fiscal_year_bs_id",
        help_text="FK id -> nepali_datetime_fiscalyear.id (not modelled here)",
    )
    item = models.BigIntegerField(
        db_column="item_id",
        help_text="FK id -> fundamentals_accountdictionary.id (not modelled here)",
    )

    class Meta:
        db_table = "fundamentals_financialstatdbs"
        managed = False  # owned by the `fundamentals` app; never migrate it here
        ordering = ["ticker", "fiscal_year_ad", "quarter", "sorting_code"]
        # Mirrors the source table's natural key (financialstatdbs_unique_row).
        unique_together = (
            ("sector", "fiscal_year_ad", "quarter", "data_source", "ticker", "fs_type", "item_code"),
        )

    def __str__(self):
        return f"{self.ticker} {self.fiscal_year_ad} Q{self.quarter} {self.fs_type} {self.item_code}"


class Portfolio(models.Model):
    """
    Table: portfolio_portfolio
    A logged-in user's private holdings portfolio — typically imported from a
    Meroshare "My Shares" CSV. One user may keep several named portfolios. Risk /
    valuation analytics are derived on the fly from the linked NEPSE EOD prices,
    so only the positions live here.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portfolios"
    )
    name = models.CharField(max_length=120, default="My Portfolio")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "portfolio_portfolio"
        ordering = ["-updated_at"]
        unique_together = (("user", "name"),)

    def __str__(self):
        return f"{self.name} (user {self.user_id})"


class Holding(models.Model):
    """
    Table: portfolio_holding
    One scrip position inside a portfolio. ``quantity`` is the demat balance; the
    two price columns are the *snapshot* the CSV was exported with (kept for
    reference only). Live valuation always re-prices against the latest
    ``NepseDailyStockPrice`` close so every holding is marked to the same session.
    """
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="holdings"
    )
    symbol = models.CharField(max_length=20, db_index=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    # Import-time snapshot prices (informational; not used for live valuation).
    last_close = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    ltp = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "portfolio_holding"
        ordering = ["symbol"]
        unique_together = (("portfolio", "symbol"),)

    def __str__(self):
        return f"{self.symbol} x{self.quantity}"


class HoldingCost(models.Model):
    """
    Table: portfolio_holding_cost
    Cost basis (WACC) for one scrip, imported from the broker "My WACC" report
    (Sani Securities / any TMS — CSV, Excel or PDF). Kept in its OWN table rather
    than on ``Holding`` so re-importing the Meroshare "My Shares" CSV — which
    replaces every ``Holding`` — never wipes the cost basis. Joined to holdings
    by ``symbol`` at valuation time to derive book value & paper P/L.
    """
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="costs"
    )
    symbol = models.CharField(max_length=20, db_index=True)
    # Weighted-average cost per share, and the report's own quantity / total cost
    # (informational; live book value is wacc_rate × the current demat balance).
    wacc_rate = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    modified = models.CharField(max_length=32, blank=True, default="")  # report's "Last Modification Date"
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "portfolio_holding_cost"
        ordering = ["symbol"]
        unique_together = (("portfolio", "symbol"),)

    def __str__(self):
        return f"{self.symbol} @ {self.wacc_rate}"


class PageVisit(models.Model):
    """
    Table: site_page_visit
    One row per page view, written by ``VisitTrackingMiddleware`` on every HTML
    page load. This is the self-hosted alternative to Google Analytics — it works
    on an offline / air-gapped LAN because nothing leaves the server. The /stats/
    dashboard rolls these rows up into visit / unique-visitor / top-page counts.

    Only real page navigations are stored (GET, text/html, HTTP 200); static
    files, the admin, JSON API polls and AJAX requests are filtered out by the
    middleware so the table isn't flooded by the dashboards' auto-refresh.
    """
    path = models.CharField(max_length=300, db_index=True)
    method = models.CharField(max_length=8, default="GET")
    status_code = models.PositiveSmallIntegerField(default=200)
    # Client IP is the unique-visitor key on a LAN (each device has one). Nullable
    # because a misconfigured proxy can hide it.
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    session_key = models.CharField(max_length=40, blank=True, default="", db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="page_visits",
    )
    user_agent = models.CharField(max_length=400, blank=True, default="")
    referer = models.CharField(max_length=400, blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "site_page_visit"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at", "path"]),
        ]

    def __str__(self):
        return f"{self.path} @ {self.created_at:%Y-%m-%d %H:%M} ({self.ip_address or '?'})"


class AccountApproval(models.Model):
    """Admin review state for a self-service portfolio account request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="account_approval"
    )
    contact_email = models.EmailField(unique=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=PENDING, db_index=True
    )
    review_note = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_account_approvals",
    )

    class Meta:
        db_table = "account_approval_request"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.contact_email} ({self.get_status_display()})"

    @property
    def is_pending(self):
        return self.status == self.PENDING

    def approve(self, reviewer=None, note=""):
        self.status = self.APPROVED
        self.reviewed_by = reviewer
        self.review_note = note or ""
        self.reviewed_at = timezone.now()
        self.user.is_active = True
        self.user.save(update_fields=["is_active"])
        self.save(update_fields=["status", "reviewed_by", "review_note", "reviewed_at"])

    def reject(self, reviewer=None, note=""):
        self.status = self.REJECTED
        self.reviewed_by = reviewer
        self.review_note = note or ""
        self.reviewed_at = timezone.now()
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        self.save(update_fields=["status", "reviewed_by", "review_note", "reviewed_at"])
