import requests
from decimal import Decimal
from django.core.management.base import BaseCommand
from core_analysis.models import NepseDailyStockPrice, NepseMarketIndex

class Command(BaseCommand):
    help = "Pulls live data streams from /api/stock-prices/ and /api/indices/ networks straight into MySQL tables."

    def handle(self, *args, **options):
        session = requests.Session()
        batch_size = 2000

        # CRASH-PROOFED CONVERSION PARSER
        def clean_dec(val):
            if val is None:
                return Decimal('0.00')
            val_str = str(val).strip()
            if val_str == "" or val_str.lower() in ["none", "null", "nan", "-"]:
                return Decimal('0.00')
            try:
                return Decimal(val_str)
            except Exception:
                return Decimal('0.00')

        # ==========================================
        # PIPELINE PART 1: RAW STOCK PRICES INGESTION
        # ==========================================
        stock_url = "http://192.168.1.35:8000/api/nepse-data/api/stock-prices/?format=json"
        self.stdout.write(self.style.SUCCESS("Opening stock prices pipeline stream..."))
        
        stock_batch = []
        stock_saved = 0
        seen_api_ids = set()

        while stock_url:
            try:
                response = session.get(stock_url, timeout=15)
                if response.status_code != 200:
                    break
                payload = response.json()
                results = payload.get('results', [])

                for item in results:
                    current_id = item['id']
                    if current_id in seen_api_ids:
                        continue

                    stock_obj = NepseDailyStockPrice(
                        api_id=current_id,
                        business_date=item['business_date'],
                        security_id=item['security_id'],
                        symbol=item['symbol'],
                        security_name=item['security_name'],
                        open_price=clean_dec(item['open_price']),
                        high_price=clean_dec(item['high_price']),
                        low_price=clean_dec(item['low_price']),
                        close_price=clean_dec(item['close_price']),
                        previous_close=clean_dec(item['previous_close']),
                        average_traded_price=clean_dec(item['average_traded_price']),
                        total_traded_quantity=item['total_traded_quantity'],
                        total_traded_value=clean_dec(item['total_traded_value']),
                        total_trades=item['total_trades'],
                        market_capitalization=clean_dec(item['market_capitalization']),
                        fifty_two_week_high=clean_dec(item['fifty_two_week_high']),
                        fifty_two_week_low=clean_dec(item['fifty_two_week_low']),
                        last_updated_time=item['last_updated_time']
                    )
                    stock_batch.append(stock_obj)
                    seen_api_ids.add(current_id)

                    if len(stock_batch) >= batch_size:
                        NepseDailyStockPrice.objects.bulk_create(stock_batch, ignore_conflicts=True)
                        stock_saved += len(stock_batch)
                        self.stdout.write(self.style.WARNING(f"Processed {stock_saved} stock records to MySQL..."))
                        stock_batch = []

                stock_url = payload.get('next')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Stock pipeline broken: {str(e)}"))
                break

        if stock_batch:
            NepseDailyStockPrice.objects.bulk_create(stock_batch, ignore_conflicts=True)
            stock_saved += len(stock_batch)

        self.stdout.write(self.style.SUCCESS(f"[✓] Stock prices ingestion locked. Total processed: {stock_saved}"))

        # ==========================================
        # PIPELINE PART 2: MARKET INDICES INGESTION
        # ==========================================
        index_url = "http://192.168.1.35:8000/api/nepse-data/api/indices/?format=json"
        self.stdout.write(self.style.SUCCESS("Opening aggregate market index pipeline stream..."))

        index_batch = []
        index_saved = 0
        seen_index_ids = set()

        while index_url:
            try:
                response = session.get(index_url, timeout=15)
                if response.status_code != 200:
                    break
                payload = response.json()
                results = payload.get('results', [])

                for item in results:
                    current_idx_id = item['id']
                    if current_idx_id in seen_index_ids:
                        continue

                    idx_obj = NepseMarketIndex(
                        api_id=current_idx_id,
                        business_date=item['date'],
                        sector_name=item['sector'],
                        open_index=clean_dec(item['open']),
                        high_index=clean_dec(item['high']),
                        low_index=clean_dec(item['low']),
                        close_index=clean_dec(item['close']),
                        absolute_change=clean_dec(item['absolute_change']),
                        percentage_change=clean_dec(item['percentage_change']),
                        turnover_values=clean_dec(item['turnover_values']),
                        turnover_volume=item['turnover_volume'],
                        total_transaction=item['total_transaction'],
                        number_52_weeks_high=clean_dec(item['number_52_weeks_high']),
                        number_52_weeks_low=clean_dec(item['number_52_weeks_low']),
                        created_at=item['created_at']
                    )
                    index_batch.append(idx_obj)
                    seen_index_ids.add(current_idx_id)

                    if len(index_batch) >= batch_size:
                        NepseMarketIndex.objects.bulk_create(index_batch, ignore_conflicts=True)
                        index_saved += len(index_batch)
                        self.stdout.write(self.style.WARNING(f"Processed {index_saved} index records to MySQL..."))
                        index_batch = []

                index_url = payload.get('next')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Index pipeline broken: {str(e)}"))
                break

        if index_batch:
            NepseMarketIndex.objects.bulk_create(index_batch, ignore_conflicts=True)
            index_saved += len(index_batch)

        self.stdout.write(self.style.SUCCESS(f"[✓] Market indices ingestion locked. Total processed: {index_saved}"))