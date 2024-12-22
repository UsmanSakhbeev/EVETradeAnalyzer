from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from evetradeanalyzer.trade_analysis.models import ProfitableDeal


@csrf_exempt  # Декоратор для работы с POST-запросами
def station_to_station_analysis(request):
    return render(request, "trade_analysis/station_to_station.html")


def index(request):
    return render(request, "trade_analysis/index.html")


def region_analysis(request):
    return render(request, "trade_analysis/region_analysis.html")


def in_station_analysis(request):
    return render(request, "trade_analysis/in_station.html")


def in_jita_analysis(request):
    deals_query = ProfitableDeal.objects.all().order_by("-profit_percent")
    paginator = Paginator(deals_query, 50)  # Показываем 50 записей на странице

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "trade_analysis/in_jita.html", {"page_obj": page_obj})


def inventory_analysis(request):
    return render(request, "trade_analysis/inventory_analysis.html")
