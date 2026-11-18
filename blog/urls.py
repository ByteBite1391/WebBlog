from django.urls import path, re_path
from . import views

app_name = "blog"

SLUG = r"(?P<slug>[-\w]+)"

urlpatterns = [
    path("", views.home, name="home"),
    path("posts/", views.post_list, name="post_list"),
    path("search/", views.search, name="search"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("posts/new/", views.post_create, name="post_create"),

    re_path(rf"^posts/{SLUG}/$", views.post_detail, name="detail"),
    re_path(rf"^posts/{SLUG}/edit/$", views.post_update, name="post_update"),
    re_path(rf"^posts/{SLUG}/delete/$", views.post_delete, name="post_delete"),
    re_path(rf"^posts/{SLUG}/comment/$", views.add_comment, name="add_comment"),
    path("comments/<int:pk>/delete/", views.delete_comment, name="delete_comment"),

    re_path(rf"^category/{SLUG}/$", views.category_detail, name="category"),
]