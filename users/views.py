from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm
from .utils import has_assigned_stations


def login_view(request):
    if request.user.is_authenticated:
        return redirect("balance_list")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        if not has_assigned_stations(user):
            return redirect("account_pending")
        return redirect("balance_list")
    return render(request, "users/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("balance_list")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("account_pending")
    return render(request, "users/register.html", {"form": form})


@login_required
def account_pending_view(request):
    if has_assigned_stations(request.user):
        return redirect("balance_list")
    return render(request, "users/account_pending.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")
