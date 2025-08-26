from django.contrib import admin
from .models import DashboardDb

# Register your models here.

class ListDashboardDB(admin.ModelAdmin):
    list_display = (
        "nama",
        "bulan_ini",
        "tahun_ini",
    )

admin.site.register(DashboardDb, ListDashboardDB)