from django.apps import AppConfig


class TradeAnalysisConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "evetradeanalyzer.trade_analysis"

    def ready(self):
        from background_task.models import Task

        from evetradeanalyzer.trade_analysis.utils import fetch_and_process_data_task

        if not Task.objects.filter(
            task_name="evetradeanalyzer.trade_analysis.utils.fetch_and_process_data_task"
        ).exists():
            fetch_and_process_data_task(repeat=600)
