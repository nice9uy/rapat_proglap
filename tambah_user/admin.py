from django.contrib import admin
from .models import NamaDb

# Register your models here.

class ListDbNama(admin.ModelAdmin):
    list_display = (
        "id",
        "nama",
    
    )

admin.site.register(NamaDb, ListDbNama)