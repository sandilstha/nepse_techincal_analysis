import requests
from decimal import Decimal
from django.core.management.base import BaseCommand
from core_analysis.models import CompanyProfile, StockPriceAdjustment

class Command(BaseCommand):
    help = "Pure ETL: Downloads listed companies and adjusted stock prices from APIs and saves them directly to MySQL."

    def handle(self, *args, **options):
        session = requests.Session()
        
        # ==========================================
        # 1. DOWNLOAD AND STORE COMPANIES LIST
        # ==========================================
        company_url = "http://192.168.1.35:8000/api/listed-companies/companies/?format=json"
        self.stdout.write(self.style.SUCCESS("Downloading Company List from API..."))
        
        while company_url:
            try:
                response = session.get(company_url, timeout=10)
                if response.status_code != 200:
                    break
                
                payload = response.json()
                results = payload.get('results', [])
                
                for item in results:
                    CompanyProfile.objects.update_or_create(
                        symbol=item['script_ticker'],
                        defaults={
                            'security_name': item['company_name'],
                            'sector_name': item.get('sector'),
                            'status': item.get('status', 'Active')
                        }
                    )
                company_url = payload.get('next')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Company Profile download error: {str(e)}"))
                break
                
        self.stdout.write(self.style.SUCCESS("All company profiles stored successfully."))

        # ==========================================
        # 2. DOWNLOAD AND STORE ADJUSTED PRICE DATA
        # ==========================================
        price_url = "http://192.168.1.35:8000/api/stock-adjustments/stock-price-adj/?format=json"
        self.stdout.write(self.style.SUCCESS("Downloading Adjusted Stock Prices from API..."))
        
        batch_size = 2000
        records_batch = []
        total_saved = 0

        while price_url:
            try:
                response = session.get(price_url, timeout=15)
                if response.status_code != 200:
                    break
                
                payload = response.json()
                results = payload.get('results', [])
                
                for item in results:
                    ticker_symbol = item['symbol']
                    
                    # Core Rule: Only store prices if the company exists in our company profiles table
                    if not CompanyProfile.objects.filter(symbol=ticker_symbol).exists():
                        continue
                        
                    # Skip duplicate row rows
                    if StockPriceAdjustment.objects.filter(external_id=item['id']).exists():
                        continue

                    def clean_decimal(val):
                        return Decimal(str(val)) if val is not None else None

                    # Map incoming API fields directly to MySQL columns
                    price_obj = StockPriceAdjustment(
                        external_id=item['id'],
                        business_date=item['business_date'],
                        company_id=ticker_symbol, # Maps straight to foreign key symbol column
                        security_id=item['security_id'],
                        open_price=clean_decimal(item['open_price']),
                        high_price=clean_decimal(item['high_price']),
                        low_price=clean_decimal(item['low_price']),
                        close_price=clean_decimal(item['close_price']),
                        open_price_adj=clean_decimal(item['open_price_adj']),
                        high_price_adj=clean_decimal(item['high_price_adj']),
                        low_price_adj=clean_decimal(item['low_price_adj']),
                        close_price_adj=clean_decimal(item['close_price_adj']),
                        adjustment_factor=clean_decimal(item['adjustment_factor']),
                        average_traded_price_adj=clean_decimal(item.get('average_traded_price_adj')),
                    )
                    records_batch.append(price_obj)

                    # Bulk insert chunk loop for maximum storage performance
                    if len(records_batch) >= batch_size:
                        StockPriceAdjustment.objects.bulk_create(records_batch)
                        total_saved += len(records_batch)
                        self.stdout.write(self.style.WARNING(f"Stored {total_saved} data rows inside MySQL..."))
                        records_batch = []

                # Automatically step to the next paginated page url
                price_url = payload.get('next')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Data storage error: {str(e)}"))
                break

        # Store any remaining rows left in the final batch
        if records_batch:
            StockPriceAdjustment.objects.bulk_create(records_batch)
            total_saved += len(records_batch)

        self.stdout.write(self.style.SUCCESS(f"Complete! Data transfer finished. Total rows stored in MySQL: {total_saved}"))