from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver
from .utils import log_activity


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    log_activity(request, "login", user=user, username=user.username)


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    if user is not None:
        log_activity(request, "logout", user=user, username=user.username)


@receiver(user_login_failed)
def on_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get("username", "?")
    log_activity(
        request, "login_failed",
        user=None,
        username=username,
        reason="اعتبارنامه نامعتبر",
    )