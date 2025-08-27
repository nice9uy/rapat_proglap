from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from data_rapat.models import DataRapatDb
from tambah_user.models import NamaDb
from django.utils import timezone
import polars as pl
from django.core.paginator import Paginator


@login_required(login_url="/accounts/login/")
def dashboard(request):
    user = request.user.username
    group = ", ".join([group.name for group in request.user.groups.all()])

    bulan_ini = datetime.now().month
    tahun_ini = datetime.now().year

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
            df.filter(
                (pl.col("tanggal").dt.year() == tahun_ini)
                & (pl.col("tanggal").dt.month() == bulan_ini)
            )
            .select(pl.count())
            .item()
        )

    except Exception as e:
        total_kas = 0
        total_kas_keluar_bulan_ini = 0
        total_kas_bulan_ini = 0
        jumlah_rapat_bulan_ini = 0
        print(f"error karena : {e}")

    context = {
        "page_title": "DASHBOARD",
        "bulan_ini": datetime.now(),
        "group": group,
        "user": user,
        "total_kas": total_kas,
        "total_kas_bulan_ini": total_kas_bulan_ini,
        "total_kas_keluar_bulan_ini": total_kas_keluar_bulan_ini,
        "jumlah_rapat_bulan_ini": jumlah_rapat_bulan_ini,
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

        # Sort data
        data_sorted = sorted(data, key=lambda x: x["jumlah_perbulan"], reverse=True)

        # Pagination
        page = request.GET.get("page", 1)
        per_page = request.GET.get("per_page", 10)  # Adjust as needed

        paginator = Paginator(data_sorted, per_page)
        page_obj = paginator.get_page(page)

        # Format response for remote pagination
        response_data = {
            "current_page": page_obj.number,
            "last_page": paginator.num_pages,
            "total": paginator.count,
            "data": list(page_obj.object_list),
            "from": page_obj.start_index(),
            "to": page_obj.end_index(),
            "per_page": per_page,
            "next_page_url": page_obj.has_next()
            and f"?page={page_obj.next_page_number()}"
            or None,
            "prev_page_url": page_obj.has_previous()
            and f"?page={page_obj.previous_page_number()}"
            or None,
            "status": "success",
        }

        return JsonResponse(response_data, safe=False)

    except Exception as e:
        # Always return consistent structure
        return JsonResponse(
            {
                "status": "error",
                "message": str(e),
                "current_page": 1,
                "last_page": 1,
                "total": 0,
                "data": [],
            },
            safe=False,
        )
