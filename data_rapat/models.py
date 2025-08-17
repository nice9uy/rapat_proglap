from django.db import models

# Create your models here.
class DataRapat(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    tanggal = models.DateTimeField()
    jam = models.CharField(max_length=10, null=True, blank=True)
    nama = models.CharField(max_length=100, null=True, blank=True)
    judul_kontrak = models.CharField(max_length=100, null=True, blank=True)
    kas_masuk = models.IntegerField(default=0)
    kas_keluar = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = "judul_kontrak"