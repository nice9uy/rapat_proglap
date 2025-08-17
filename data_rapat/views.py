from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url="/accounts/login/")
def data_rapat(request):
    context = { 
        'page_title': "DATA RAPAT", 
        # 'bulan_ini' : datetime.now(),
    }
    return render(request, 'data_rapat/index.html' ,context)