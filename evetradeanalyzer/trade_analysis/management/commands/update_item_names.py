from django.core.management.base import BaseCommand

from evetradeanalyzer.trade_analysis.utils import update_item_names


class Command(BaseCommand):
    help = "Update item names from EVE Online API."

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting to update item names...")
        update_item_names()
        self.stdout.write("Item names updated successfully!")
