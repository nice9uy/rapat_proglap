from django.urls import path
from .views import (
    perubahan_data,
)

urlpatterns = [
    path("", perubahan_data, name="perubahan_data"),

]
