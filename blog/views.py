from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import Http404
from django.views.decorators.http import require_POST

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm
from accounts.utils import log_activity

POSTS_PER_PAGE = 9


def home(request):
    posts = Post.objects.published().select_related("author", "category")
    categories = Category.objects.annotate(
        num_posts=Count("posts", filter=Q(posts__status="published"))
    ).filter(num_posts__gt=0)[:8]
    context = {
        "recent_posts": posts[:6],
        "categories": categories,
        "popular_posts": posts.order_by("-views")[:3],
        "total_posts": posts.count(),
    }
    return render(request, "blog/home.html", context)


def post_list(request):
    qs = Post.objects.published().select_related("author", "category")
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "").strip()
    sort = request.GET.get("sort", "new")

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(summary__icontains=q) |
                       Q(content__icontains=q))
    if cat:
        qs = qs.filter(category__slug=cat)
    qs = qs.order_by("published_at" if sort == "old" else "-published_at")

    paginator = Paginator(qs, POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "blog/post_list.html", {
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "query": q,
        "current_cat": cat,
        "current_sort": sort,
        "is_search": bool(q or cat),
    })


def search(request):
    q = request.GET.get("q", "").strip()
    if q:
        log_activity(
            request, "search",
            user=request.user if request.user.is_authenticated else None,
            query=q,
            filters={k: v for k, v in request.GET.items() if k != "page"},
        )
    return post_list(request)


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.select_related("author", "category"), slug=slug)

    if not post.is_published:
        if not request.user.is_authenticated or request.user != post.author:
            raise Http404("مقاله یافت نشد.")

    viewed = request.session.get("viewed_posts", [])
    if post.pk not in viewed:
        Post.objects.filter(pk=post.pk).update(views=post.views + 1)
        viewed.append(post.pk)
        request.session["viewed_posts"] = viewed[-100:]

    log_activity(
        request, "view_post",
        user=request.user if request.user.is_authenticated else None,
        post_id=post.pk, title=post.title,
    )

    comments = post.comments.filter(is_approved=True).select_related("author")
    related = (Post.objects.published()
               .filter(category=post.category).exclude(pk=post.pk)[:3]
               if post.category else Post.objects.none())

    return render(request, "blog/post_detail.html", {
        "post": post,
        "comments": comments,
        "related_posts": related,
        "comment_form": CommentForm(),
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    qs = (Post.objects.published().filter(category=category)
          .select_related("author"))
    page_obj = Paginator(qs, POSTS_PER_PAGE).get_page(request.GET.get("page"))
    return render(request, "blog/category_detail.html", {
        "category": category, "page_obj": page_obj,
    })


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, author=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            log_activity(
                request, "post_create", user=request.user,
                post_id=post.pk, title=post.title,
                status=post.status, has_cover=bool(post.cover),
            )
            messages.success(request, "مقاله ایجاد شد.")
            return redirect("blog:dashboard")
    else:
        form = PostForm(author=request.user)
    return render(request, "blog/post_form.html", {"form": form, "mode": "create"})


@login_required
def post_update(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post,
                        author=request.user)
        if form.is_valid():
            form.save()
            log_activity(
                request, "post_update", user=request.user,
                post_id=post.pk, title=post.title, status=post.status,
            )
            messages.success(request, "مقاله به‌روزرسانی شد.")
            return redirect("blog:dashboard")
    else:
        form = PostForm(instance=post, author=request.user)
    return render(request, "blog/post_form.html", {
        "form": form, "post": post, "mode": "edit",
    })


@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == "POST":
        post_id, title = post.pk, post.title
        post.delete()
        log_activity(
            request, "post_delete", user=request.user,
            post_id=post_id, title=title,
        )
        messages.success(request, "مقاله حذف شد.")
        return redirect("blog:dashboard")
    return render(request, "blog/post_confirm_delete.html", {"post": post})


@login_required
def dashboard(request):
    posts = Post.objects.filter(author=request.user).select_related("category")
    my_comments = (Comment.objects.filter(post__author=request.user)
                   .select_related("post", "author"))
    return render(request, "blog/dashboard.html", {
        "posts": posts,
        "total": posts.count(),
        "published": posts.filter(status="published").count(),
        "drafts": posts.filter(status="draft").count(),
        "my_comments": my_comments,
        "comments_count": my_comments.count(),
    })


@login_required
@require_POST
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if not post.is_published:
        raise Http404
    form = CommentForm(request.POST)
    if form.is_valid():
        c = form.save(commit=False)
        c.post = post
        c.author = request.user
        c.save()
        log_activity(
            request, "comment_create", user=request.user,
            comment_id=c.pk, post_id=post.pk, post_title=post.title,
            body_length=len(c.body),
        )
        messages.success(request, "نظر شما ثبت شد.")
    else:
        messages.error(request, "خطا در ثبت نظر.")
    return redirect("blog:detail", slug=slug)


@login_required
@require_POST
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user and not request.user.is_staff:
        messages.error(request, "اجازه حذف این نظر را ندارید.")
        return redirect("blog:detail", slug=comment.post.slug)
    slug = comment.post.slug
    comment_id = comment.pk
    post_title = comment.post.title
    comment.delete()
    log_activity(
        request, "comment_delete", user=request.user,
        comment_id=comment_id, post_title=post_title,
    )
    messages.success(request, "نظر حذف شد.")
    return redirect("blog:detail", slug=slug)


def handler404(request, exception):
    return render(request, "404.html", status=404)


def handler500(request):
    return render(request, "500.html", status=500)