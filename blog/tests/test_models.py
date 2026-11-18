from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from blog.models import Category, Post, Comment


class CategoryModelTest(TestCase):

    def test_auto_slug(self):
        cat = Category.objects.create(name="جنگو")
        self.assertEqual(cat.slug, "جنگو")

    def test_unique_slug_generation(self):
        Category.objects.create(name="python", slug="python")
        c2 = Category.objects.create(name="python")  # بدون slug
        self.assertEqual(c2.slug, "python-2")

    def test_post_count_only_published(self):
        cat = Category.objects.create(name="اخبار")
        user = User.objects.create_user("u", "u@u.com", "pass12345")
        Post.objects.create(title="منتشر", slug="pub", author=user,
                            category=cat, content="x" * 30, status="published")
        Post.objects.create(title="پیش‌نویس", slug="draft", author=user,
                            category=cat, content="x" * 30, status="draft")
        self.assertEqual(cat.post_count, 1)

    def test_get_absolute_url(self):
        cat = Category.objects.create(name="دسته", slug="cat")
        self.assertEqual(cat.get_absolute_url(), "/category/cat/")


class PostModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("author", "a@a.com", "pass12345")

    def test_auto_slug_fa(self):
        p = Post.objects.create(title="جنگو چیست؟", author=self.user,
                                content="x" * 30)
        self.assertTrue(p.slug)
        self.assertIn("جنگو", p.slug)

    def test_reserved_slug_rejected(self):
        p = Post.objects.create(title="new", author=self.user, content="x" * 30)
        self.assertNotEqual(p.slug, "new")

    def test_published_at_set_on_publish(self):
        p = Post.objects.create(title="تست", author=self.user,
                                content="x" * 30, status="published")
        self.assertIsNotNone(p.published_at)

    def test_is_published_true(self):
        p = Post.objects.create(title="تست", author=self.user,
                                content="x" * 30, status="published")
        self.assertTrue(p.is_published)

    def test_is_published_false_for_future(self):
        p = Post.objects.create(title="آینده", author=self.user,
                                content="x" * 30, status="published")
        Post.objects.filter(pk=p.pk).update(
            published_at=timezone.now() + timedelta(days=1)
        )
        p.refresh_from_db()
        self.assertFalse(p.is_published)

    def test_published_manager(self):
        user = self.user
        Post.objects.create(title="پ", slug="p1", author=user,
                            content="x" * 30, status="published")
        Post.objects.create(title="د", slug="d1", author=user,
                            content="x" * 30, status="draft")
        self.assertEqual(Post.objects.published().count(), 1)

    def test_get_absolute_url_unicode(self):
        p = Post.objects.create(title="جنگو چیست", author=self.user,
                                content="x" * 30)
        self.assertIn("جنگو", p.get_absolute_url())


class CommentModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("u", "u@u.com", "pass12345")
        self.post = Post.objects.create(
            title="تست", slug="test", author=self.user,
            content="x" * 30, status="published"
        )

    def test_create_comment(self):
        c = Comment.objects.create(post=self.post, author=self.user, body="سلام")
        self.assertEqual(c.post, self.post)
        self.assertTrue(c.is_approved)  # پیش‌فرض

    def test_str(self):
        c = Comment.objects.create(post=self.post, author=self.user, body="x")
        self.assertIn("u", str(c))