"""ابزارهای ثبت لاگ فعالیت"""
import json
from .models import ActivityLog


def get_client_ip(request):
    """آی‌پی واقعی کاربر (با در نظر گرفتن پراکسی)"""
    if request is None:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_activity(request, action, user=None, **metadata):
    """
    ثبت یک فعالیت.

    - request: می‌تواند None باشد (از سیگنال‌ها)
    - user: اگر None باشد و request موجود باشد، از request.user استفاده می‌شود
    - metadata: هر داده اضافی (id مقاله، عنوان، ...)
    """
    if user is None and request is not None:
        u = getattr(request, "user", None)
        if u is not None and u.is_authenticated:
            user = u

    clean_metadata = {}
    for k, v in metadata.items():
        try:
            json.dumps(v)
            clean_metadata[k] = v
        except (TypeError, ValueError):
            clean_metadata[k] = str(v)

    return ActivityLog.objects.create(
        user=user,
        action=action,
        ip_address=get_client_ip(request),
        user_agent=(request.META.get("HTTP_USER_AGENT", "")[:500]
                    if request else ""),
        path=(request.path[:500] if request else ""),
        method=(request.method if request else ""),
        metadata=clean_metadata,
    )