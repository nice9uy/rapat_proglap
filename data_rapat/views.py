from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import bleach
from datetime import time
from django.http import JsonResponse
from .models import DataRapatDb
from tambah_user.models import NamaDb
from django.contrib import messages
from django.core.paginator import Paginator
import logging


logger = logging.getLogger(__name__)


# Create your views here.
@login_required(login_url="/accounts/login/")
def data_rapat(request):
    nama_anggota = list(NamaDb.objects.all().values_list("nama", flat=True))

    data_rapat = DataRapatDb.objects.all().values("id")

    print(data_rapat)

    cek_group = list(request.user.groups.all())
    group = [group.name for group in cek_group]

    context = {
        "page_title": "DATA RAPAT",
        "nama_anggota": nama_anggota,
        "group": group,
        "data_rapat": data_rapat,
    }
    return render(request, "data_rapat/index.html", context)


@login_required(login_url="/accounts/login/")
def data_rapat_api(request):
    try:
        try:
            page = int(request.GET.get("page", 1))
            size = int(request.GET.get("size", 15))
        except (ValueError, TypeError):
            return JsonResponse(
                {"error": "Parameter page dan size harus angka positif"}, status=400
            )

        if page < 1 or size < 1:
            return JsonResponse(
                {"error": "Page dan size harus lebih besar dari 0"}, status=400
            )

        size = min(size, 100)  # Batasi maksimal 100 per halaman

        base_query = DataRapatDb.objects.all().order_by("tanggal", "id")
        data_queryset = []

        # Fungsi bantu untuk format Rupiah
        def format_rupiah(amount):
            try:
                amount = float(amount or 0)
                return f"{amount:,.0f}".replace(",", ".")
            except (ValueError, TypeError):
                return "0"

        for obj in base_query:
            # Format tanggal
            tanggal_str = ""
            if obj.tanggal:
                try:
                    if isinstance(obj.tanggal, str):
                        date_obj = datetime.strptime(obj.tanggal, "%Y-%m-%d")
                    else:
                        date_obj = obj.tanggal
                    tanggal_str = date_obj.strftime("%d-%m-%Y")
                except Exception:
                    tanggal_str = str(obj.tanggal)

            # Format jam
            jam_str = ""
            if obj.jam:
                try:
                    if isinstance(obj.jam, str):
                        time_obj = datetime.strptime(obj.jam, "%H:%M:%S").time()
                    else:
                        time_obj = obj.jam
                    jam_str = time_obj.strftime("%H:%M")
                except Exception:
                    jam_str = str(obj.jam or "")

            # Format kas dengan mata uang
            kas_masuk_formatted = format_rupiah(obj.kas_masuk)
            kas_keluar_formatted = format_rupiah(obj.kas_keluar)

            data_queryset.append(
                {
                    "tanggal": tanggal_str,
                    "jam": jam_str,
                    "nama": obj.nama or "",
                    "judul_kontrak": obj.judul_kontrak or "",
                    "kas_masuk": kas_masuk_formatted,
                    "kas_keluar": kas_keluar_formatted,
                }
            )

        paginator = Paginator(data_queryset, size)
        page_obj = paginator.get_page(page)
        data = list(page_obj.object_list)

        return JsonResponse(
            {
                "data": data,
                "last_page": paginator.num_pages,
                "total": paginator.count,
                "current_page": page,
                "per_page": size,
            },
            safe=False,
        )

    except Exception as e:
        logger.error(f"Error fetching DataRapatDb list: {e}", exc_info=True)
        return JsonResponse({"error": "Terjadi kesalahan server internal"}, status=500)


def tambah_data_rapat(request):
    cek_group = list(request.user.groups.all())
    group = [group.name for group in cek_group]

    # if group == ''

    if request.method == "POST":
        raw_date = bleach.clean(
            request.POST.get("tanggal_rapat", "").strip(),
            tags=[],
            attributes={},
            protocols=[],
            strip=True,
        )

        tanggal_rapat = datetime.strptime(raw_date, "%d %B %Y").date()

        raw_jam = bleach.clean(
            request.POST.get("jam_rapat", "").strip(),
            tags=[],
            attributes={},
            protocols=[],
            strip=True,
        )

        jam_rapat = time(hour=int(raw_jam), minute=0)  # → 09:00:00

        nama = bleach.clean(
            str(request.POST.get("nama", "")).upper(),
            tags=[],
            attributes={},
            protocols=[],
            strip=True,
        )

        kontrak = bleach.clean(
            str(request.POST.get("kontrak", "")).upper(),
            tags=[],
            attributes={},
            protocols=[],
            strip=True,
        )

        kas_masuk_raw = bleach.clean(
            (request.POST.get("kas_masuk", "")),
            tags=[],
            attributes={},
            protocols=[],
            strip=True,
        )

        kas_masuk = int(kas_masuk_raw.replace(".", ""))

        kas_keluar_raw = bleach.clean(
            (request.POST.get("kas_keluar", "")),
            tags=[],
            attributes={},
            protocols=[],
            strip=True,
        )

        kas_keluar = int(kas_keluar_raw.replace(".", ""))

        id_nama_anggota = list(
            NamaDb.objects.filter(nama=nama).values_list("id", flat=True)
        )[0]

        DataRapatDb.objects.create(
            id_nama_anggota=id_nama_anggota,
            tanggal=tanggal_rapat,
            jam=jam_rapat,
            nama=nama,
            judul_kontrak=kontrak,
            kas_masuk=kas_masuk,
            kas_keluar=kas_keluar,
            updated_at=None,
        )
        messages.success(request, "Data Rapat berhasil ditambahkan.")
        return redirect("data_rapat")
