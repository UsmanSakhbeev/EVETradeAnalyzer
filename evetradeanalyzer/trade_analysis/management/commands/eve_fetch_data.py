from django.core.management.base import BaseCommand

from evetradeanalyzer.trade_analysis.models import ProfitableDeal
from evetradeanalyzer.trade_analysis.utils import (
    fetch_and_save_market_data,
    find_profitable_deals,
    save_orders_to_db,
)


def save_profitable_deals_to_db(deals):
    ProfitableDeal.objects.all().delete() 
    for deal in deals:
        ProfitableDeal.objects.create(
            item_name=deal["item_name"],
            last_price=deal["last_price"],
            prev_price=deal["prev_price"],
            price_difference=deal["price_difference"],
            profit_percent=deal["profit_percent"],
            max_buy_price=deal["max_buy_price"],
            volume_remain=deal["volume_remain"],
        )
    print(f"Сохранено {len(deals)} выгодных сделок в базу данных.")


class Command(BaseCommand):
    help = "Fetch market data from EVE Online API and process profitable deals."

    def handle(self, *args, **kwargs):
        self.stdout.write("Fetching or loading market data...")
        all_orders = fetch_and_save_market_data()

        if not all_orders:
            self.stdout.write("Не удалось загрузить данные.")
            return

        self.stdout.write("Saving orders to database...")
        save_orders_to_db(all_orders)

        self.stdout.write("Processing profitable deals...")
        profitable_deals = find_profitable_deals(threshold=0.35)

        if profitable_deals:
            self.stdout.write(f"Found {len(profitable_deals)} profitable deals.")
            self.stdout.write("Saving profitable deals to database...")
            save_profitable_deals_to_db(profitable_deals)
        else:
            self.stdout.write("No profitable deals found.")
