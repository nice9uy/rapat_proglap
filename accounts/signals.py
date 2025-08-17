# accounts/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group


def create_groups():
    group_names = [
        "ADMIN",
        "PENGAWAS",
        "ANGGOTA"
        # Tambahkan group lain jika perlu
    ]

    for name in group_names:
        Group.objects.get_or_create(name=name)
        # get_or_create lebih aman dari race condition & lebih bersih

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    """
    Dijalankan setelah setiap kali migrate
    Tapi hanya buat group jika belum ada
    """
    create_groups()