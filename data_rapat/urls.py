from django.urls import path
from . views import data_rapat

urlpatterns = [
    path("", data_rapat, name="data_rapat"),
]