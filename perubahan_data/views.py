from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url="/accounts/login/")
def perubahan_data(request):
    return render(request, 'perubahan_data/index.html')