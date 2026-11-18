import time
import logging
from .utils import log_activity

logger = logging.getLogger(__name__)


class ActivityLogMiddleware:
    """
    ثبت خودکار:
    - خطاهای 500
    - درخواست‌های POST با پاسخ 403/404 (تلاش مشکوک)
    - زمان پاسخ
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = int((time.time() - start) * 1000)

        if self._should_log(request, response):
            self._log(request, response, duration)

        return response

    def _should_log(self, request, response):
        if response.status_code >= 500:
            return True
        if response.status_code in (403, 404) and request.method == "POST":
            return True
        return False

    def _log(self, request, response, duration):
        try:
            user = getattr(request, "user", None)
            if user is not None and not user.is_authenticated:
                user = None
            log_activity(
                request, "admin_access" if request.path.startswith("/admin/") else "search",
                user=user,
                status_code=response.status_code,
                duration_ms=duration,
            )
        except Exception:
            logger.exception("خطا در ثبت ActivityLog")


class ErrorLogMiddleware:
    """لاگ کامل استثناها در فایل"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.exception(
            "Unhandled exception at %s %s by user=%s",
            request.method, request.path,
            getattr(getattr(request, "user", None), "username", "anon"),
            exc_info=exception,
        )
        return None