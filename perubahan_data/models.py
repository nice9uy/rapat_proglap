from django.db import models

# Create your models here.
class PerubahanData(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    id_database = models.CharField(max_length=100, null=True, blank=True)
    no_kontrak = models.CharField(max_length=100, null=True, blank=True)
    tanggal = models.DateField()
    jam = models.TimeField()
    keterangan = models.CharField(max_length=300, null=True, blank=True)
  
    def __str__(self):
        return self.no_kontrak

    class Meta:
        verbose_name_plural = "LOG"


class TotalKas(models.Model):
    kas_masuk = models.IntegerField()
    kas_keluar = models.IntegerField()
    total = models.IntegerField()


    def __str__(self):
        return self.total

    class Meta:
        verbose_name_plural = "KAS"