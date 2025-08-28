from datetime import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
import bleach
from datetime import time
from django.http import JsonResponse
from .models import DataRapatDb
from tambah_user.models import NamaDb
from django.contrib import messages
from django.core.paginator import Paginator
import logging
from django.db import transaction

logger = logging.getLogger(__name__)


# Create your views here.
@login_required(login_url="/accounts/login/")
def data_rapat(request):
    nama_anggota = list(NamaDb.objects.all().values_list("nama", flat=True))
    user = request.user

    data_rapat = list(
        DataRapatDb.objects.all().values(
            "id",
            "tanggal",
            "jam",
            "nama",
            "judul_surat",
            "judul_kontrak",
            "kas_masuk",
            "kas_keluar",
            "file_bast",
            "no_bast",
        )
    )

    group = ", ".join([group.name for group in request.user.groups.all()])

    # print(group)

    context = {
        "page_title": "DATA RAPAT",
        "nama_anggota": nama_anggota,
        "group": group,
        "data_rapat": data_rapat,
        "user": user,
    }
    return render(request, "data_rapat/index.html", context)


@login_required(login_url="/accounts/login/")
def data_rapat_api(request):
    try:
        # Ambil parameter pagination
        try:
            page = int(request.GET.get("page", 1))
            size = int(request.GET.get("size", 10))
        except (ValueError, TypeError):
            return JsonResponse(
                {"error": "Parameter page dan size harus angka positif"}, status=400
            )

        if page < 1 or size < 1:
            return JsonResponse(
                {"error": "Page dan size harus lebih besar dari 0"}, status=400
            )

        size = min(size, 100)  # Batasi maksimal 100

        # Ambil objek model asli (bukan .values()) agar bisa akses .url
        base_queryset = DataRapatDb.objects.all().order_by("tanggal", "jam")

        # Paginasi
        paginator = Paginator(base_queryset, size)
        page_obj = paginator.get_page(page)

        # Format data
        data = []
        for obj in page_obj.object_list:
            # Akses file_bast (pastikan nama field di model = file_bast)
            file_bast_url = obj.file_bast.url if obj.file_bast else None

            data.append(
                {
                    "id": obj.id,
                    "tanggal": obj.tanggal.isoformat() if obj.tanggal else None,
                    "jam": obj.jam.strftime("%H:%M") if obj.jam else None,
                    "nama": obj.nama or "",
                    "judul_surat": obj.judul_surat or "",
                    "judul_kontrak": obj.judul_kontrak or "",
                    "kas_masuk": float(obj.kas_masuk or 0),
                    "kas_keluar": float(obj.kas_keluar or 0),
                    "file_bast": file_bast_url,  
                    "no_bast": obj.no_bast,  
                }
            )

        # print(data)

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


@login_required(login_url="/accounts/login/")
def tambah_data_rapat(request):
    group = ", ".join([group.name for group in request.user.groups.all()])
    tgl_sekarang = datetime.now().date()
    jam_sekarang = datetime.now().strftime("%H:%M:%S")

    if request.method == "POST":
        ### UPLOAD BAST ####################################
        uploaded_file_bast = request.FILES.get("bast_file")

        ############################

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
        jam = jam_rapat.strftime("%H:%M")

        nama = bleach.clean(
            str(request.POST.get("nama", "")).upper(),
            tags=[],
            attributes={},
            protocols=[],
            strip=True,
        )

        surat = bleach.clean(
            str(request.POST.get("surat", "")).upper(),
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

        no_bast = bleach.clean(
            str(request.POST.get("no_bast", "")).upper(),
            tags=[],
            attributes={},
            protocols=[],
            strip=True,
        )

        if request.user.is_superuser:
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

            with transaction.atomic():
                DataRapatDb.objects.create(
                    id_nama_anggota=id_nama_anggota,
                    tanggal=tanggal_rapat,
                    jam=jam,
                    nama=nama,
                    judul_surat=surat,
                    judul_kontrak=kontrak,
                    kas_masuk=kas_masuk,
                    kas_keluar=kas_keluar,
                    file_bast=uploaded_file_bast,
                    no_bast = no_bast
                )

                messages.success(request, "Data Rapat berhasil ditambahkan.")

            return redirect("data_rapat")

        else:
            if group == "ADMIN":
                kas_masuk_raw = bleach.clean(
                    (request.POST.get("kas_masuk_display", "")),
                    tags=[],
                    attributes={},
                    protocols=[],
                    strip=True,
                )

                kas_masuk = int(kas_masuk_raw.replace(".", ""))

                kas_keluar_raw = bleach.clean(
                    (request.POST.get("kas_keluar_display", "")),
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
                    jam=jam,
                    nama=nama,
                    judul_surat=surat,
                    judul_kontrak=kontrak,
                    file_bast=uploaded_file_bast,
                    kas_masuk=kas_masuk,
                    kas_keluar=kas_keluar,
                    tanggal_update=tgl_sekarang,
                    jam_update=jam_sekarang,
                    no_bast = no_bast
                )

                messages.success(request, "Data Rapat berhasil ditambahkan.")
                return redirect("data_rapat")

            elif group == "ANGGOTA":
                id_nama_anggota = list(
                    NamaDb.objects.filter(nama=nama).values_list("id", flat=True)
                )[0]

                kas_masuk_raw = bleach.clean(
                    (request.POST.get("kas_masuk_display", "")),
                    tags=[],
                    attributes={},
                    protocols=[],
                    strip=True,
                )

                kas_masuk = int(kas_masuk_raw.replace(".", ""))

                DataRapatDb.objects.create(
                    id_nama_anggota=id_nama_anggota,
                    tanggal=tanggal_rapat,
                    jam=jam,
                    nama=nama,
                    kas_masuk=kas_masuk,
                    judul_surat=surat,
                    judul_kontrak=kontrak,
                    file_bast=uploaded_file_bast,
                    no_bast = no_bast
                )

                messages.success(request, "Data Rapat berhasil ditambahkan.")
                return redirect("data_rapat")

            else:
                return redirect("data_rapat")


@login_required(login_url="/accounts/login/")
def edit_data_rapat(request, rapat_id):
    data_rapat = get_object_or_404(DataRapatDb, pk=rapat_id)

    group = ", ".join([group.name for group in request.user.groups.all()])

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

        raw_jam_clean = raw_jam.replace(".", ":")

        if raw_jam_clean:
            jam_obj = datetime.strptime(raw_jam_clean, "%H:%M").time()
        else:
            jam_obj = None

        nama = bleach.clean(
            str(request.POST.get("nama", "")).upper(),
            tags=[],
            attributes={},
            protocols=[],
            strip=True,
        )

        surat = bleach.clean(
            str(request.POST.get("surat", "")).upper(),
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

        id_nama_anggota = (
            NamaDb.objects.filter(nama=nama).values_list("id", flat=True).first()
        )


        no_bast = bleach.clean(
            str(request.POST.get("no_bast", "")).upper(),
            tags=[],
            attributes={},
            protocols=[],
            strip=True,
        )

        uploaded_file = request.FILES.get("bast_file")

        if uploaded_file is None:
            file_bast = data_rapat.file_bast.name

        else:
            data_rapat.file_bast.delete()
            file_bast = uploaded_file

        if request.user.is_superuser:
            data_rapat.id_nama_anggota = id_nama_anggota
            data_rapat.tanggal = tanggal_rapat
            data_rapat.jam = jam_obj
            data_rapat.nama = nama
            data_rapat.judul_surat = surat
            data_rapat.judul_kontrak = kontrak
            data_rapat.file_bast = file_bast
            data_rapat.no_bast = no_bast
            data_rapat.save()

            messages.success(request, "Data Rapat berhasil diedit.")
            return redirect("data_rapat")

        else:
            if group == "ADMIN":
                data_rapat.id_nama_anggota = id_nama_anggota
                data_rapat.tanggal = tanggal_rapat
                data_rapat.jam = jam_obj
                data_rapat.judul_surat = surat
                data_rapat.judul_kontrak = kontrak
                data_rapat.save()

                messages.success(request, "Data Rapat berhasil diedit.")
                return redirect("data_rapat")

            elif group == "ANGGOTA":
                data_rapat.id_nama_anggota = id_nama_anggota
                data_rapat.tanggal = tanggal_rapat
                data_rapat.jam = jam_obj
                data_rapat.judul_surat = surat
                data_rapat.judul_kontrak = kontrak
                data_rapat.file_bast = file_bast
                data_rapat.no_bast = no_bast
                data_rapat.save()

                messages.success(request, "Data Rapat berhasil diedit.")
                return redirect("data_rapat")

            elif group == "PENGAWAS":
                data_rapat.id_nama_anggota = id_nama_anggota
                data_rapat.tanggal = tanggal_rapat
                data_rapat.jam = jam_obj
                data_rapat.judul_surat = surat
                data_rapat.judul_kontrak = kontrak
                data_rapat.file_bast = file_bast
                data_rapat.no_bast = no_bast
                data_rapat.save()

                messages.success(request, "Data Rapat berhasil diedit.")
                return redirect("data_rapat")

            else:
                return redirect("data_rapat")

    return redirect("data_rapat")


@login_required(login_url="/accounts/login/")
def edit_data_nominal(request, rapat_id):
    data_rapat = get_object_or_404(DataRapatDb, pk=rapat_id)
    tgl_sekarang = datetime.now().date()
    jam_sekarang = datetime.now().strftime("%H:%M:%S")

    group = ", ".join([group.name for group in request.user.groups.all()])

    if request.method == "POST":
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

        if group == "ADMIN":
            messages.success(
                request, "Anda tidak mempunyai Otorisasi untuk edit pada bagian ini!!!"
            )
            return redirect("data_rapat")
        else:
            try:
                with transaction.atomic():
                    data_rapat.kas_masuk = kas_masuk
                    data_rapat.kas_keluar = kas_keluar
                    data_rapat.tanggal_update = tgl_sekarang
                    data_rapat.jam_update = jam_sekarang
                    data_rapat.save()

                messages.success(request, "Data Rapat berhasil diedit.")
                return redirect("data_rapat")

            except Exception as e:
                messages.success(request, f"Data Rapat gagal diinput karena : {e}")
                return redirect("data_rapat")

    return redirect("data_rapat")
