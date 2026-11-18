from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
import uuid

class Category(models.Model):
    name = models.CharField("نام", max_length=100, unique=True)
    slug = models.SlugField("اسلاگ", max_length=110, unique=True, allow_unicode=True)
    description = models.TextField("توضیحات", blank=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name, allow_unicode=True) or str(uuid.uuid4())[:8]
            slug, i = base, 2
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"; i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:category", args=[self.slug])

    @property
    def post_count(self):
        return self.posts.filter(status="published").count()

class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status="published", published_at__lte=timezone.now())

class Post(models.Model):
    STATUS_CHOICES = (("draft", "پیش‌نویس"), ("published", "منتشر شده"))
    title = models.CharField("عنوان", max_length=200)
    slug = models.SlugField("اسلاگ", max_length=220, unique=True, allow_unicode=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name="posts", verbose_name="نویسنده")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                  null=True, blank=True,
                                  related_name="posts", verbose_name="دسته‌بندی")
    summary = models.CharField("خلاصه", max_length=300, blank=True)
    content = models.TextField("محتوا")
    cover = models.ImageField("تصویر شاخص", upload_to="covers/", blank=True, null=True)
    status = models.CharField("وضعیت", max_length=10, choices=STATUS_CHOICES, default="draft")
    views = models.PositiveIntegerField("بازدید", default=0)
    published_at = models.DateTimeField("تاریخ انتشار", null=True, blank=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    objects = PostQuerySet.as_manager()

    RESERVED_SLUGS = {"new", "dashboard", "edit", "delete", "comment", "create"}

    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "-published_at"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=True)[:200] or str(uuid.uuid4())[:8]
            if base in self.RESERVED_SLUGS:
                base = f"{base}-post"
            slug, i = base, 2
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"; i += 1
            self.slug = slug
        if self.status == "published" and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:detail", args=[self.slug])

    @property
    def is_published(self):
        return (self.status == "published" and self.published_at
                and self.published_at <= timezone.now())

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                              related_name="comments", verbose_name="مقاله")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name="comments", verbose_name="نویسنده")
    body = models.TextField("متن نظر", max_length=2000)
    is_approved = models.BooleanField("تأیید شده", default=True)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)

    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"نظر {self.author.username} روی {self.post.title}"
