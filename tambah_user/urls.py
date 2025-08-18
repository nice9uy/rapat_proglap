from django.urls import path
from .views import (
    tambah_user,
    tambah_anggota,
    tambah_user_api,
    edit_anggota,
    delete_anggota,
)

urlpatterns = [
    path("", tambah_user, name="tambah_user"),
    path("tambah", tambah_anggota, name="tambah_anggota"),
    path("tambah_user_api", tambah_user_api, name="tambah_user_api"),
    path("edit_anggota/<int:id_edit>/", edit_anggota, name="edit_anggota"),
    path("delete_anggota/<int:id_delete>/", delete_anggota, name="delete_anggota"),
]
