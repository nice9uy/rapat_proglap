from django.db import models


# Create your models here.
class DataRapatDb(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    id_nama_anggota = models.CharField(max_length=50, null=True, blank=True)
    tanggal = models.DateField()
    jam = models.TimeField(max_length=10, null=True, blank=True)
    nama = models.CharField(max_length=100, null=True, blank=True)
    judul_surat = models.CharField(max_length=100, null=True, blank=True)
    judul_kontrak = models.CharField(max_length=100, null=True, blank=True)
    kas_masuk = models.IntegerField(default=0)
    kas_keluar = models.IntegerField(default=0)
    created_at = models.DateField(auto_now_add=True) 
    tanggal_update = models.DateField(null=True, blank=True)
    jam_update= models.TimeField(null=True, blank=True)
    file_bast = models.FileField(upload_to='BAST/', null=True, blank=True) 
    no_bast =  models.CharField(max_length=100, null=True, blank=True)
    pengecualian = models.BooleanField(default=False)

    def __str__(self):
        return self.judul_kontrak

    class Meta:
        verbose_name_plural = "Kontrak"