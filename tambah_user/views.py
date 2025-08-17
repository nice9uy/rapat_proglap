from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import bleach
from django.contrib import messages
from tambah_user.models import NamaDb
from django.http import JsonResponse
from django.core.paginator import Paginator
import logging

logger = logging.getLogger(__name__)

# Create your views here.
@login_required(login_url="/accounts/login/")
def tambah_user(request):
    # cek_group =  request.user.groups
    # user = request.user
    # # cek_admin = user.is_superuser



    # print(cek_admin)
    context = {
        'page_title': "TAMBAH USER",
    }
    return render(request, "tambah_user/index.html" , context)




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
            return JsonResponse({"error": "Parameter page dan size harus angka positif"}, status=400)

        if page < 1 or size < 1:
            return JsonResponse({"error": "Page dan size harus lebih besar dari 0"}, status=400)

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
        messages.success(request, "Anggota berhasil ditambahkan.")
        return redirect("tambah_user")