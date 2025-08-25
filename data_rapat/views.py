from datetime import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
import bleach
from datetime import time
from django.http import JsonResponse

from perubahan_data.models import PerubahanData
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
    # print(user)

    data_rapat = list(
        DataRapatDb.objects.all().values(
            "id", "tanggal", "jam", "nama", "judul_kontrak", "kas_masuk", "kas_keluar"
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
        base_queryset = (
            DataRapatDb.objects.all()
            .order_by("tanggal", "jam")
            .values(
                "id",
                "tanggal",
                "jam",
                "nama",
                "judul_kontrak",
                "kas_masuk",
                "kas_keluar",
            )
        )

        # Paginasi
        paginator = Paginator(base_queryset, size)
        page_obj = paginator.get_page(page)

        # Ambil data mentah (tanpa formatting!)
        data = []
        for obj in page_obj.object_list:
            data.append(
                {
                    "id": obj["id"],
                    "tanggal": obj["tanggal"],  # ISO format: YYYY-MM-DD
                    "jam": obj["jam"],  # Time object atau string
                    "nama": obj["nama"] or "",
                    "judul_kontrak": obj["judul_kontrak"] or "",
                    "kas_masuk": float(obj["kas_masuk"] or 0),  # Kirim float
                    "kas_keluar": float(obj["kas_keluar"] or 0),
                }
            )

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
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching DataRapatDb list: {e}", exc_info=True)
        return JsonResponse({"error": "Terjadi kesalahan server internal"}, status=500)


@login_required(login_url="/accounts/login/")
def tambah_data_rapat(request):
    group = ", ".join([group.name for group in request.user.groups.all()])
    tgl_sekarang = datetime.now().date()
    jam_sekarang = datetime.now().strftime("%H:%M:%S")
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
        jam = jam_rapat.strftime("%H:%M")

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

            DataRapatDb.objects.create(
                id_nama_anggota=id_nama_anggota,
                tanggal=tanggal_rapat,
                jam=jam,
                nama=nama,
                judul_kontrak=kontrak,
                kas_masuk=kas_masuk,
                kas_keluar=kas_keluar,
            )
            messages.success(request, "Data Rapat berhasil ditambahkan.")
            return redirect("data_rapat")

        else:
            if group == "ADMIN":
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
                    jam=jam,
                    nama=nama,
                    judul_kontrak=kontrak,
                    kas_masuk=kas_masuk,
                    kas_keluar=kas_keluar,
                    tanggal_update=tgl_sekarang,
                    jam_update=jam_sekarang,
                )
                messages.success(request, "Data Rapat berhasil ditambahkan.")
                return redirect("data_rapat")

            elif group == "ANGGOTA":
                id_nama_anggota = list(
                    NamaDb.objects.filter(nama=nama).values_list("id", flat=True)
                )[0]

                DataRapatDb.objects.create(
                    id_nama_anggota=id_nama_anggota,
                    tanggal=tanggal_rapat,
                    jam=jam,
                    nama=nama,
                    judul_kontrak=kontrak,
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

        if ":" in raw_jam:
            hour_part = raw_jam.split(":")[0]  # ambil '14' dari '14:00'
        else:
            hour_part = raw_jam

        # Cek apakah hasilnya angka
        if not hour_part.isdigit():
            messages.error(request, "Jam tidak valid. Mohon diisi dengan benar")
            return redirect(
                "edit_data_rapat", rapat_id=rapat_id
            )  # ganti dengan nama URL-mu

        jam = int(hour_part)

        # Opsional: validasi rentang jam
        if jam < 0 or jam > 23:
            messages.error(request, "Jam harus antara 00-23.")
            return redirect("edit_data_rapat", rapat_id=rapat_id)

        # Buat objek time dan format ke 'HH:MM'
        jam_rapat = time(hour=jam, minute=0)
        jam_formatted = jam_rapat.strftime("%H:%M")  # →

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

        id_nama_anggota = (
            NamaDb.objects.filter(nama=nama).values_list("id", flat=True).first()
        )

        if request.user.is_superuser:
            if jam_formatted != "":
                data_rapat.id_nama_anggota = id_nama_anggota
                data_rapat.tanggal = tanggal_rapat
                data_rapat.jam = jam_formatted
                data_rapat.nama = nama
                data_rapat.judul_kontrak = kontrak
                data_rapat.save()

                messages.success(request, "Data Rapat berhasil diedit.")
                return redirect("data_rapat")
            else:
                messages.success(request, "Jam Harap di isi")
                return redirect("data_rapat")

        else:
            if group == "ADMIN":
                if jam_formatted != "":
                    data_rapat.id_nama_anggota = id_nama_anggota
                    data_rapat.tanggal = tanggal_rapat
                    data_rapat.jam = jam_formatted
                    data_rapat.nama = nama
                    data_rapat.judul_kontrak = kontrak
                    data_rapat.save()

                    messages.success(request, "Data Rapat berhasil diedit.")
                    return redirect("data_rapat")
                else:
                    messages.success(request, "Jam Harap di isi")
                    return redirect("data_rapat")

            elif group == "ANGGOTA":
                if jam_formatted != "":
                    data_rapat.id_nama_anggota = id_nama_anggota
                    data_rapat.tanggal = tanggal_rapat
                    data_rapat.jam = jam_formatted
                    data_rapat.judul_kontrak = kontrak
                    data_rapat.save()

                    messages.success(request, "Data Rapat berhasil diedit.")
                    return redirect("data_rapat")
                else:
                    messages.success(request, "Jam Harap di isi")
                    return redirect("data_rapat")
            else:
                if jam_formatted != "":
                    data_rapat.id_nama_anggota = id_nama_anggota
                    data_rapat.tanggal = tanggal_rapat
                    data_rapat.jam = jam_formatted
                    data_rapat.nama = nama
                    data_rapat.judul_kontrak = kontrak
                    data_rapat.save()

                    messages.success(request, "Data Rapat berhasil diedit.")
                    return redirect("data_rapat")
                else:
                    messages.success(request, "Jam Harap di isi")
                    return redirect("data_rapat")

    return redirect("data_rapat")


@login_required(login_url="/accounts/login/")
def edit_data_nominal(request, rapat_id):
    data_rapat = get_object_or_404(DataRapatDb, pk=rapat_id)
    tgl_sekarang = datetime.now().date()
    jam_sekarang = datetime.now().strftime("%H:%M:%S")

    awal_kas_masuk = data_rapat.kas_masuk
    awal_kas_keluar = data_rapat.kas_keluar

    print(awal_kas_masuk)
    print(awal_kas_keluar)

    try:
        # cek_update = data_rapat.tanggal_update

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

            

            try:
                with transaction.atomic():
                    data_rapat.kas_masuk = kas_masuk
                    data_rapat.kas_keluar = kas_keluar
                    data_rapat.tanggal_update = tgl_sekarang
                    data_rapat.jam_update = jam_sekarang
                    data_rapat.save()

                    PerubahanData.objects.create(
                        id_database=data_rapat.id,
                        no_kontrak=data_rapat.judul_kontrak,
                        tanggal=tgl_sekarang,
                        jam=jam_sekarang,
                        keterangan = f"KAS MASUK : {awal_kas_masuk} -> ",
                    )

                messages.success(request, "Data Rapat berhasil diedit.")
                return redirect("data_rapat")

            except Exception as e:
                messages.success(request, f"Data Rapat gagal diinput karena : {e}")
                return redirect("data_rapat")

        # print(cek_update)
    except Exception:
        cek_update = None

    if cek_update is None:
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

            # print(kas_masuk)
            # print(kas_keluar)

            try:
                with transaction.atomic():
                    data_rapat.kas_masuk = kas_masuk
                    data_rapat.kas_keluar = kas_keluar
                    data_rapat.tanggal_update = tgl_sekarang
                    data_rapat.jam_update = jam_sekarang
                    # data_rapat.save()

                    # PerubahanData.objects.create(
                    #     id_database=data_rapat.id,
                    #     no_kontrak=data_rapat.judul_kontrak,
                    #     tanggal=tgl_sekarang,
                    #     jam=jam_sekarang,
                    #     keterangan="tttt",
                    # )

                messages.success(request, "Data Rapat berhasil diedit.")
                return redirect("data_rapat")

            except Exception as e:
                messages.success(request, f"Data Rapat gagal diinput karena : {e}")
                return redirect("data_rapat")

    return redirect("data_rapat")
