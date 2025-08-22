from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from data_rapat.models import DataRapatDb
from tambah_user.models import NamaDb
# import json


@login_required(login_url="/accounts/login/")
def dashboard(request):
    data = []
    user = request.user.username
    group = ', '.join([group.name for group in request.user.groups.all()])

    anggota_yang_rapat = list(NamaDb.objects.all().values('id', 'nama'))


    print(anggota_yang_rapat)

    # for anggota in anggota_yang_rapat:
    #     cek_anggota = DataRapatDb.objects.filter('')

    # print(user)
   
    context = { 
        'page_title': "DASHBOARD", 
        'bulan_ini' : datetime.now(),
        'group' : group,
        'user' : user
    }

    return render(request, 'dashboard/index.html' , context )