from django.urls import path
from .views import (
     belum_diinput, belum_diinput_api
)

urlpatterns = [
    path("", belum_diinput, name="belum_diinput"),
    path("api/", belum_diinput_api, name="belum_diinput_api"),
   
]
