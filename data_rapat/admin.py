from django.contrib import admin
from .models import DataRapatDb

# Register your models here.

class ListDbDataRapat(admin.ModelAdmin):
    list_display = (
        "id",
        "id_nama_anggota",
        'id_random',
        "tanggal",
        "jam",
        "nama",
        "judul_kontrak",
        "kas_masuk",
        "kas_keluar",
        "created_at",
        "updated_at",
    )

admin.site.register(DataRapatDb, ListDbDataRapat)