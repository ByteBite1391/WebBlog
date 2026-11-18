from django.contrib import admin
from .models import Category, Post, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "post_count", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    date_hierarchy = "created_at"

    def post_count(self, obj): return obj.post_count
    post_count.short_description = "تعداد مقالات"

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "status",
                    "views", "published_at", "created_at")
    list_filter = ("status", "category", "author", "created_at")
    search_fields = ("title", "summary", "content", "author__username")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    list_editable = ("status",)
    readonly_fields = ("views", "created_at", "updated_at", "published_at")
    list_select_related = ("author", "category")

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "short_body", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("body", "author__username", "post__title")
    list_editable = ("is_approved",)
    date_hierarchy = "created_at"

    def short_body(self, obj):
        return obj.body[:60] + ("..." if len(obj.body) > 60 else "")
    short_body.short_description = "متن"
