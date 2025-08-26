from datetime import datetime
import bleach
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from data_rapat.models import DataRapatDb
from django.core.paginator import Paginator
from tambah_user.models import NamaDb
from django.contrib import messages


# Create your views here.
@login_required(login_url="/accounts/login/")
def belum_diinput(request):
    group = ", ".join([group.name for group in request.user.groups.all()])
    nama_anggota = list(NamaDb.objects.all().values_list("nama", flat=True))

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
        )
    )

    context = {
        "page_title": "BELUM DIINPUT",
        "group": group,
        "data_rapat": data_rapat,
        "nama_anggota": nama_anggota,
    }

    return render(request, "belum_diinput/index.html", context)


@login_required(login_url="/accounts/login/")
def belum_diinput_api(request):
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
            DataRapatDb.objects.filter(kas_masuk=0, kas_keluar=0)
            .order_by("tanggal", "jam")
            .values(
                "id",
                "tanggal",
                "jam",
                "nama",
                "judul_surat",
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
                    "judul_surat": obj["judul_surat"] or "",
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
def edit_nominal_belom_diinput(request, rapat_id):
    data_rapat = get_object_or_404(DataRapatDb, pk=rapat_id)
    tgl_sekarang = datetime.now().date()
    jam_sekarang = datetime.now().strftime("%H:%M:%S")

    if request.method == "POST":
        kas_masuk_raw = bleach.clean(
            (request.POST.get("kas_masuk_belum_diinput", "")),
            tags=[],
            attributes={},
            protocols=[],
            strip=True,
        )

        kas_masuk = int(kas_masuk_raw.replace(".", ""))

        kas_keluar_raw = bleach.clean(
            (request.POST.get("kas_keluar_belum_diinput", "")),
            tags=[],
            attributes={},
            protocols=[],
            strip=True,
        )

        kas_keluar = int(kas_keluar_raw.replace(".", ""))

        print(kas_masuk)
        print(kas_keluar)

        if kas_masuk != 0 or kas_keluar != 0:
            data_rapat.kas_masuk = kas_masuk
            data_rapat.kas_keluar = kas_keluar
            data_rapat.tanggal_update = tgl_sekarang
            data_rapat.jam_update = jam_sekarang
            data_rapat.save()

            messages.success(request, "Kas Berhasil di Input.")
            return redirect("belum_diinput")
        
        else:
            messages.warning(request, "Nominal Belum diinput!!!")
            return redirect("belum_diinput")

    return redirect("belum_diinput")
