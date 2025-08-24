from django.urls import path
from .views import (
    data_rapat,
    tambah_data_rapat,
    data_rapat_api,
    edit_data_rapat,
    edit_data_nominal,
)

urlpatterns = [
    path("", data_rapat, name="data_rapat"),
    path("tambah_data_rapat", tambah_data_rapat, name="tambah_data_rapat"),
    path("data_rapat_api", data_rapat_api, name="data_rapat_api"),
    path("edit_data_rapat/<int:rapat_id>/", edit_data_rapat, name="edit_data_rapat"),
    path(
        "edit_data_nominal/<int:rapat_id>/", edit_data_nominal, name="edit_data_nominal"
    ),
]
