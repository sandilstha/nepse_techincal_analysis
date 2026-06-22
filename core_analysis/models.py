from django.db import models

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
