from django.urls import path
from .views import (
     belum_diinput
)

urlpatterns = [
    path("", belum_diinput, name="belum_diinput"),
   
]
