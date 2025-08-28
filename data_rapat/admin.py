from django.contrib import admin
from .models import DataRapatDb

# Register your models here.

class ListDbDataRapat(admin.ModelAdmin):
    list_display = (
        "id",
        "id_nama_anggota",
        "tanggal",
        "jam",
        "nama",
        "judul_surat",
        "judul_kontrak",
        "file_bast",
        "no_bast",
        "kas_masuk",
        "kas_keluar",
        "created_at",
        "tanggal_update",
        "jam_update",
        "pengecualian"
    )

admin.site.register(DataRapatDb, ListDbDataRapat)