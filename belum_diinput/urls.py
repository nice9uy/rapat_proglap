from django.urls import path
from .views import belum_diinput, belum_diinput_api, edit_nominal_belom_diinput

urlpatterns = [
    path("", belum_diinput, name="belum_diinput"),
    path("api/", belum_diinput_api, name="belum_diinput_api"),
    path(
        "edit_nominal_belom_diinput/<int:rapat_id>/",
        edit_nominal_belom_diinput,
        name="edit_nominal_belom_diinput",
    ),
]
