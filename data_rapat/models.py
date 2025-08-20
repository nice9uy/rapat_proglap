from django.db import models
import uuid


# Create your models here.
class DataRapatDb(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_nama_anggota = models.CharField(max_length=50, null=True, blank=True)
    tanggal = models.DateField()
    jam = models.CharField(max_length=10, null=True, blank=True)
    nama = models.CharField(max_length=100, null=True, blank=True)
    judul_kontrak = models.CharField(max_length=100, null=True, blank=True)
    kas_masuk = models.IntegerField(default=0)
    kas_keluar = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.judul_kontrak

    class Meta:
        verbose_name_plural = "Kontrak"