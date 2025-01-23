from django.core.management.base import BaseCommand

from evetradeanalyzer.trade_analysis.utils import fetch_and_process_data_task


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        fetch_and_process_data_task()
