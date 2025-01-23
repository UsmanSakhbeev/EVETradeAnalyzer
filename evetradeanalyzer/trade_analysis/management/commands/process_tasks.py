from background_task.models import Task
from django.core.management.base import BaseCommand

from evetradeanalyzer.trade_analysis.utils import fetch_and_process_data_task


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        if not Task.objects.filter(
            task_name="evetradeanalyzer.trade_analysis.utils.fetch_and_process_data_task"
        ).exists():
            fetch_and_process_data_task(repeat=600)
