from django.contrib import admin
from .models import PerubahanData

class ListPerubahanData(admin.ModelAdmin):
    list_display = (
        "id",
        "id_database",
        "no_kontrak",
        "tanggal",
        "jam",
        "keterangan",
    )

admin.site.register(PerubahanData, ListPerubahanData)