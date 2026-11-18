from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from blog.models import Post


class OwnershipPermissionsTest(TestCase):
    """تست IDOR — کاربر A نباید بتواند مقاله کاربر B را دستکاری کند"""

    def setUp(self):
        self.a = User.objects.create_user("a", "a@a.com", "pass12345")
        self.b = User.objects.create_user("b", "b@b.com", "pass12345")
        self.post = Post.objects.create(
            title="مقاله A", slug="post-a", author=self.a,
            content="x" * 40, status="published",
        )

    def test_b_cannot_view_edit_form(self):
        self.client.login(username="b", password="pass12345")
        r = self.client.get(reverse("blog:post_update", args=[self.post.slug]))
        self.assertEqual(r.status_code, 404)

    def test_b_cannot_post_edit(self):
        self.client.login(username="b", password="pass12345")
        self.client.post(
            reverse("blog:post_update", args=[self.post.slug]),
            {"title": "هک", "content": "x" * 40, "status": "published"},
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "مقاله A")

    def test_b_cannot_delete(self):
        self.client.login(username="b", password="pass12345")
        r = self.client.post(reverse("blog:post_delete", args=[self.post.slug]))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_anonymous_cannot_create(self):
        r = self.client.post(reverse("blog:post_create"), {
            "title": "نفوذی", "content": "x" * 40, "status": "published",
        })
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Post.objects.filter(title="نفوذی").exists())


class StaffPermissionsTest(TestCase):
    """کارکنان باید بتوانند نظر حذف کنند"""

    def setUp(self):
        self.user = User.objects.create_user("u", "u@u.com", "pass12345")
        self.staff = User.objects.create_user("s", "s@s.com", "pass12345",
                                              is_staff=True)
        self.post = Post.objects.create(
            title="تست", slug="t", author=self.user,
            content="x" * 40, status="published",
        )

    def test_staff_can_delete_comment(self):
        from blog.models import Comment
        c = Comment.objects.create(post=self.post, author=self.user, body="x")
        self.client.login(username="s", password="pass12345")
        self.client.post(reverse("blog:delete_comment", args=[c.pk]))
        self.assertFalse(Comment.objects.filter(pk=c.pk).exists())