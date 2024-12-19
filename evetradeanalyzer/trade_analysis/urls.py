from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("region-analysis/", views.region_analysis, name="region_analysis"),
    path(
        "station-to-station-analysis/",
        views.station_to_station_analysis,
        name="station_to_station_analysis",
    ),
    path("in-station-analysis/", views.in_station_analysis, name="in_station_analysis"),
    path("inventory-analysis/", views.inventory_analysis, name="inventory_analysis"),
]
