from django.contrib import admin
from .models import DataRapatDb

# Register your models here.

class ListDbDataRapat(admin.ModelAdmin):
    list_display = (
        "id",
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