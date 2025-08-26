from django.urls import path
from . views import dashboard , dashboard_api

urlpatterns = [
    path("", dashboard, name="dashboard"),
     path("dashboard_api/", dashboard_api, name="dashboard_api"),
]