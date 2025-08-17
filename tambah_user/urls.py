from django.urls import path
from .views import tambah_user, tambah_anggota, tambah_user_api

urlpatterns = [
    path("", tambah_user, name="tambah_user"),
    path("tambah", tambah_anggota, name="tambah_anggota"),
    path("tambah_user_api", tambah_user_api, name="tambah_user_api"),
]
