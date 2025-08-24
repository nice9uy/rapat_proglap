from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from data_rapat.models import DataRapatDb
from tambah_user.models import NamaDb
from django.utils import timezone


@login_required(login_url="/accounts/login/")
def dashboard(request):
    user = request.user.username
    group = ", ".join([group.name for group in request.user.groups.all()])

    sekarang = timezone.now()
    bulan_sekarang = sekarang.month
    tahun_sekarang = sekarang.year

    anggota_list = NamaDb.objects.all()

    rapat_bulanan = DataRapatDb.objects.filter(tanggal__month=bulan_sekarang)
    semua_rapat = DataRapatDb.objects.filter(tanggal__year=tahun_sekarang)

    data = []
    for anggota in anggota_list:
        nama_anggota = anggota.nama
        jumlah_perbulan = rapat_bulanan.filter(nama=nama_anggota).count()
        jumlah_keseluruhan = semua_rapat.filter(nama=nama_anggota).count()

        data.append({
            'id': anggota.id,
            'nama': nama_anggota,
            'jumlah_perbulan': jumlah_perbulan,
            'jumlah_keseluruhan': jumlah_keseluruhan,

        })

    context = {
        "page_title": "DASHBOARD",
        "bulan_ini": datetime.now(),
        "group": group,
        "user": user,
        'data' :data
    }

    return render(request, "dashboard/index.html", context)



















