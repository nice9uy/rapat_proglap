from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url="/accounts/login/")
def belum_diinput(request):
    return render(request, 'belum_diinput/index.html')  