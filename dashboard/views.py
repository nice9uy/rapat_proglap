from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from data_rapat.models import DataRapatDb
from tambah_user.models import NamaDb
from django.utils import timezone
import polars as pl


@login_required(login_url="/accounts/login/")
def dashboard(request):
    user = request.user.username
    group = ", ".join([group.name for group in request.user.groups.all()])

    bulan_ini = datetime.now().month
    tahun_ini = datetime.now().year

    # print(bulan_ini)

    # data_rapat = list(DataRapatDb.objects.all().values())

    try:
        fields = ["tanggal", "kas_masuk", "kas_keluar"]
        data_list = list(DataRapatDb.objects.values(*fields).iterator(chunk_size=2000))

        df = pl.DataFrame(data_list)

        #### TOTAL KAS #####################
        kas_masuk = df["kas_masuk"].sum()
        kas_keluar = df["kas_keluar"].sum()

        total_kas = kas_masuk - kas_keluar
        ####################################

        #### Total Kas bulan INi ###########
        total_kas_masuk_bulan_ini = (
            df.filter(
                (pl.col("tanggal").dt.month() == bulan_ini)
                & (pl.col("tanggal").dt.year() == tahun_ini)
            )
            .select(pl.sum("kas_masuk"))
            .item()
        )

        total_kas_keluar_bulan_ini = (
            df.filter(
                (pl.col("tanggal").dt.month() == bulan_ini)
                & (pl.col("tanggal").dt.year() == tahun_ini)
            )
            .select(pl.sum("kas_keluar"))
            .item()
        )

        total_kas_bulan_ini = total_kas_masuk_bulan_ini - total_kas_keluar_bulan_ini

        #####################################



        jumlah_rapat_bulan_ini = (
            df
            .filter(
                (pl.col("tanggal").dt.year() == tahun_ini) &
                (pl.col("tanggal").dt.month() == bulan_ini)
            )
            .select(pl.count())
            .item()
        )

    except Exception as e:
        print(f"error karena : {e}")

    context = {
        "page_title": "DASHBOARD",
        "bulan_ini": datetime.now(),
        "group": group,
        "user": user,
        "total_kas": total_kas,
        "total_kas_bulan_ini": total_kas_bulan_ini,
        "total_kas_keluar_bulan_ini": total_kas_keluar_bulan_ini,
        "jumlah_rapat_bulan_ini": jumlah_rapat_bulan_ini
    }

    return render(request, "dashboard/index.html", context)


@login_required(login_url="/accounts/login/")
def dashboard_api(request):
    try:
        data = []
        sekarang = timezone.now()
        bulan_sekarang = sekarang.month
        tahun_sekarang = sekarang.year

        anggota_list = NamaDb.objects.all()

        rapat_bulanan = DataRapatDb.objects.filter(tanggal__month=bulan_sekarang)
        semua_rapat = DataRapatDb.objects.filter(tanggal__year=tahun_sekarang)

        for anggota in anggota_list:
            nama_anggota = anggota.nama
            jumlah_perbulan = rapat_bulanan.filter(nama=nama_anggota).count()
            jumlah_keseluruhan = semua_rapat.filter(nama=nama_anggota).count()

            data.append(
                {
                    "id": anggota.id,
                    "nama": nama_anggota,
                    "jumlah_perbulan": jumlah_perbulan,
                    "jumlah_keseluruhan": jumlah_keseluruhan,
                }
            )

        data_sorted = sorted(data, key=lambda x: x["jumlah_perbulan"], reverse=True)

        return JsonResponse({"status": "success", "data": data_sorted}, safe=False)
    except Exception:
        return JsonResponse({"status": "success", "data": data_sorted}, safe=False)
