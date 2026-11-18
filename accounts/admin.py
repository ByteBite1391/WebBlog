from django.contrib import admin
from .models import Profile, ActivityLog


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "website", "updated_at")
    search_fields = ("user__username", "user__email", "display_name")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at", "user", "action_display", "ip_address",
        "method", "path_short", "status_code", "duration_ms",
    )
    list_filter = ("action", "created_at", "status_code")
    search_fields = ("user__username", "ip_address", "path",
                     "user_agent", "metadata")
    readonly_fields = [f.name for f in ActivityLog._meta.fields]
    date_hierarchy = "created_at"
    list_select_related = ("user",)
    list_per_page = 100

    def action_display(self, obj):
        return obj.get_action_display()
    action_display.short_description = "فعالیت"

    def path_short(self, obj):
        return obj.path[:60]
    path_short.short_description = "مسیر"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser