from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from data_rapat.models import DataRapatDb
from django.core.paginator import Paginator


# Create your views here.
@login_required(login_url="/accounts/login/")
def belum_diinput(request):
    group = ', '.join([group.name for group in request.user.groups.all()])


    data_rapat = list(
        DataRapatDb.objects.all().values(
            "id", "tanggal", "jam", "nama", "judul_kontrak", "kas_masuk", "kas_keluar"
        )
    )


    context = { 
        'group' : group,
        "data_rapat" : data_rapat
     }

    return render(request, 'belum_diinput/index.html',  context)  


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
            DataRapatDb.objects.filter(kas_masuk = 0 , kas_keluar = 0)
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
