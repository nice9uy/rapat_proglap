from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import bleach
from django.contrib import messages
from tambah_user.models import NamaDb
from django.http import JsonResponse
from django.core.paginator import Paginator
import logging
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)


# Create your views here.
@login_required(login_url="/accounts/login/")
def tambah_user(request):
    nama_user = NamaDb.objects.all().values("id", "nama")

    context = {"page_title": "TAMBAH USER", "nama_user": nama_user}
    return render(request, "tambah_user/index.html", context)


@login_required(login_url="/accounts/login/")
def tambah_user_api(request):
    # if not request.user.is_superuser:
    #     return JsonResponse({"error": "Tidak memiliki izin"}, status=403)

    try:
        # Validasi dan parsing parameter
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

        # Query data
        base_query = NamaDb.objects.all().order_by("id")
        paginator = Paginator(base_query.values("id", "nama"), size)

        page_obj = paginator.get_page(page)
        data = list(page_obj.object_list)

        return JsonResponse(
            {
                "data": data,
                "last_page": paginator.num_pages,
                "total": paginator.count,
            },
            safe=False,
        )

    except Exception as e:
        logger.error(f"Error fetching NamaDb list: {e}")
        return JsonResponse({"error": "Terjadi kesalahan server"}, status=500)


@login_required(login_url="/accounts/login/")
def tambah_anggota(request):
    if request.method == "POST":
        nama_user = bleach.clean(
            str(request.POST.get("nama", "")).upper(),
            tags=[],
            attributes={},
            protocols=[],
            strip=True,
        )
        NamaDb.objects.create(
            nama=nama_user,
        )
        messages.success(request, f"Anggota {nama_user} berhasil ditambahkan.")
        return redirect("tambah_user")


@login_required(login_url="/accounts/login/")
def edit_anggota(request, id_edit):
    if request.method == "POST":
        get_nama = get_object_or_404(NamaDb, pk=id_edit)

        nama = bleach.clean(
            str(request.POST.get("nama", "")).upper(),
            tags=[],
            attributes={},
            protocols=[],
            strip=True,
        )

        # print(nama)

        edit_anggota = NamaDb(id=get_nama.id, nama=nama)
        edit_anggota.save()

        messages.success(
            request,
            f"{nama} Berhasil di Edit.",
        )

    return redirect("tambah_user")


@login_required(login_url="/accounts/login/")
def delete_anggota(request, id_delete):
    anggota = get_object_or_404(NamaDb, pk=id_delete)

    if request.method == "POST":
        nama = anggota.nama 
        anggota.delete()   

        messages.success(
            request,
            f"{nama} Berhasil di Hapus.",
        )

    return redirect("tambah_user")