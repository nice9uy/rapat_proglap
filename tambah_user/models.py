from django.db import models


class NamaDb(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    nama = models.CharField(max_length=100, null=True, blank=True)
  
    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "nama"