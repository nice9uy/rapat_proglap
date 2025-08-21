from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# import json


@login_required(login_url="/accounts/login/")
def dashboard(request):
    user = request.user.username
    group = ', '.join([group.name for group in request.user.groups.all()])


    print(user)
   
    context = { 
        'page_title': "DASHBOARD", 
        'bulan_ini' : datetime.now(),
        'group' : group,
        'user' : user
    }

    return render(request, 'dashboard/index.html' , context )