from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name="profile", verbose_name="کاربر",
    )
    display_name = models.CharField("نام نمایشی", max_length=80, blank=True)
    bio = models.TextField("بیوگرافی", max_length=500, blank=True)
    website = models.URLField("وب‌سایت", blank=True)
    avatar = models.ImageField("آواتار", upload_to="avatars/", blank=True, null=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایل‌ها"

    def __str__(self):
        return f"پروفایل {self.user.username}"

    @property
    def name(self):
        full = self.user.get_full_name().strip()
        return full or self.display_name or self.user.username


class ActivityLog(models.Model):
    """لاگ کامل فعالیت‌های کاربران"""

    ACTION_LOGIN = "login"
    ACTION_LOGOUT = "logout"
    ACTION_LOGIN_FAILED = "login_failed"
    ACTION_REGISTER = "register"
    ACTION_PASSWORD_CHANGE = "password_change"
    ACTION_PASSWORD_RESET = "password_reset"
    ACTION_PROFILE_UPDATE = "profile_update"
    ACTION_POST_CREATE = "post_create"
    ACTION_POST_UPDATE = "post_update"
    ACTION_POST_DELETE = "post_delete"
    ACTION_COMMENT_CREATE = "comment_create"
    ACTION_COMMENT_DELETE = "comment_delete"
    ACTION_VIEW_POST = "view_post"
    ACTION_SEARCH = "search"
    ACTION_ADMIN_ACCESS = "admin_access"

    ACTION_CHOICES = [
        (ACTION_LOGIN, "ورود"),
        (ACTION_LOGOUT, "خروج"),
        (ACTION_LOGIN_FAILED, "ورود ناموفق"),
        (ACTION_REGISTER, "ثبت‌نام"),
        (ACTION_PASSWORD_CHANGE, "تغییر رمز"),
        (ACTION_PASSWORD_RESET, "بازنشانی رمز"),
        (ACTION_PROFILE_UPDATE, "ویرایش پروفایل"),
        (ACTION_POST_CREATE, "ایجاد مقاله"),
        (ACTION_POST_UPDATE, "ویرایش مقاله"),
        (ACTION_POST_DELETE, "حذف مقاله"),
        (ACTION_COMMENT_CREATE, "ثبت نظر"),
        (ACTION_COMMENT_DELETE, "حذف نظر"),
        (ACTION_VIEW_POST, "مشاهده مقاله"),
        (ACTION_SEARCH, "جستجو"),
        (ACTION_ADMIN_ACCESS, "دسترسی ادمین"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="activities", verbose_name="کاربر",
    )
    action = models.CharField(
        "نوع فعالیت", max_length=32, choices=ACTION_CHOICES, db_index=True,
    )
    ip_address = models.GenericIPAddressField("آی‌پی", null=True, blank=True)
    user_agent = models.TextField("User-Agent", blank=True)
    path = models.CharField("مسیر", max_length=500, blank=True, db_index=True)
    method = models.CharField("متد HTTP", max_length=10, blank=True)
    metadata = models.JSONField("اطلاعات اضافی", default=dict, blank=True)
    created_at = models.DateTimeField("زمان", auto_now_add=True, db_index=True)
    duration_ms = models.PositiveIntegerField("مدت (ms)", null=True, blank=True)
    status_code = models.PositiveSmallIntegerField("کد وضعیت", null=True, blank=True)

    class Meta:
        verbose_name = "لاگ فعالیت"
        verbose_name_plural = "لاگ فعالیت‌ها"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
        ]

    def __str__(self):
        who = self.user.username if self.user else "ناشناس"
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {who} → {self.get_action_display()}"


@receiver(post_save, sender=User)
def create_or_save_profile(sender, instance, created, **kwargs):
    Profile.objects.get_or_create(user=instance)