from django.db import models

# Create your models here.
class DashboardDb(models.Model):
    anggota_id = models.IntegerField()  # atau ForeignKey jika ingin relasi
    nama = models.CharField(max_length=50)
    bulan_ini = models.IntegerField(default=0)
    tahun_ini = models.IntegerField(default=0)
    
    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "DASHBOARD"