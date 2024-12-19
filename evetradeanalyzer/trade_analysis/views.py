import pandas as pd
import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt  # Декоратор для работы с POST-запросами
def station_to_station_analysis(request):
    return render(request, "trade_analysis/station_to_station.html")


def index(request):
    return render(request, "trade_analysis/index.html")


def region_analysis(request):
    return render(request, "trade_analysis/region_analysis.html")


def in_station_analysis(request):
    return render(request, "trade_analysis/in_station.html")


def inventory_analysis(request):
    return render(request, "trade_analysis/inventory_analysis.html")
