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


# def generate_random_id():
#     """Generate random 15-character ID (uppercase + digits)"""
#     characters = string.ascii_uppercase + string.digits  # A-Z, 0-9
#     return "".join(random.choices(characters, k=32))


# Create your views here.
@login_required(login_url="/accounts/login/")
def data_rapat(request):
    nama_anggota = list(NamaDb.objects.all().values_list("nama", flat=True))

    data_rapat = list(DataRapatDb.objects.all().values( "id", "tanggal", "jam", "nama", "judul_kontrak", "kas_masuk", "kas_keluar"))
    # print(data_rapat)

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
        # Ambil parameter pagination
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

        size = min(size, 100)  # Batasi maksimal 100

        # Query: urutkan dan ambil field penting saja
        base_queryset = DataRapatDb.objects.all().order_by("tanggal", "id").values(
            "id", "tanggal", "jam", "nama", "judul_kontrak", "kas_masuk", "kas_keluar"
        )

        # Paginasi
        paginator = Paginator(base_queryset, size)
        page_obj = paginator.get_page(page)

        # Ambil data mentah (tanpa formatting!)
        data = []
        for obj in page_obj.object_list:
            data.append({
                "id": obj["id"],
                "tanggal": obj["tanggal"],      # ISO format: YYYY-MM-DD
                "jam": obj["jam"],              # Time object atau string
                "nama": obj["nama"] or "",
                "judul_kontrak": obj["judul_kontrak"] or "",
                "kas_masuk": float(obj["kas_masuk"] or 0),   # Kirim float
                "kas_keluar": float(obj["kas_keluar"] or 0),
            })

        return JsonResponse({
            "data": data,
            "last_page": paginator.num_pages,
            "total": paginator.count,
            "current_page": page,
            "per_page": size,
        }, safe=False)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching DataRapatDb list: {e}", exc_info=True)
        return JsonResponse({"error": "Terjadi kesalahan server internal"}, status=500)

@login_required(login_url="/accounts/login/")
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

@login_required(login_url="/accounts/login/")
def edit_data_rapat(request):
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
