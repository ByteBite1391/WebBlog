from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileForm
from .models import Profile
from .utils import log_activity


def register(request):
    if request.user.is_authenticated:
        return redirect("blog:home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            log_activity(request, "register", user=user,
                         username=user.username, email=user.email)
            messages.success(request, "ثبت‌نام با موفقیت انجام شد.")
            return redirect("blog:home")
        messages.error(request, "خطا در ثبت‌نام. فرم را بررسی کنید.")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("blog:home")
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "خوش آمدید!")
            next_url = request.GET.get("next") or "blog:home"
            return redirect(next_url)
        messages.error(request, "نام کاربری یا رمز عبور اشتباه است.")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    user = request.user if request.user.is_authenticated else None
    logout(request)
    messages.info(request, "از حساب خارج شدید.")
    return redirect("blog:home")


@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "accounts/profile.html", {"profile": profile})


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES,
                            instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            log_activity(request, "profile_update", user=request.user,
                         username=request.user.username)
            messages.success(request, "پروفایل به‌روزرسانی شد.")
            return redirect("blog:dashboard")
    else:
        form = ProfileForm(instance=profile, user=request.user)
    return render(request, "accounts/profile_edit.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            log_activity(request, "password_change", user=user,
                         username=user.username)
            messages.success(request, "رمز عبور تغییر کرد.")
            return redirect("blog:dashboard")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "accounts/change_password.html", {"form": form})