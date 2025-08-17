# from datetime import datetime
from django.shortcuts import render
# from django.utils.html import strip_tags

from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages



def login_view(request):
    context = {"page_title": "login"}

    if request.method == "POST":
        # Cek apakah 'username' dan 'password' ada di POST
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, "Username dan password wajib diisi.")
            return render(request, 'auth/login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Ganti 'home' dengan nama URL tujuan
        else:
            messages.error(request, "Username atau password salah.")

    return render(request, "auth/login.html", context)


def logout_view(request):
    logout(request)
    return redirect("login")


def custom_404_view(request):
    return render(request, "404.html", status=404)

