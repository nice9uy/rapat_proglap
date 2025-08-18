from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# import json


@login_required(login_url="/accounts/login/")
def dashboard(request):
   
    context = { 
        'page_title': "DASHBOARD", 
        'bulan_ini' : datetime.now(),
    }

    return render(request, 'dashboard/index.html' , context )