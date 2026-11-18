from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from blog.models import Category, Post, Comment


def make_posts(user, n=3, status="published"):
    return [
        Post.objects.create(
            title=f"مقاله {i}", slug=f"post-{i}", author=user,
            content="x" * 40, status=status,
        ) for i in range(n)
    ]


class HomeViewTest(TestCase):

    def test_home_ok(self):
        r = self.client.get(reverse("blog:home"))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "blog/home.html")

    def test_home_shows_published_only(self):
        user = User.objects.create_user("u", "u@u.com", "pass12345")
        Post.objects.create(title="p1", slug="p1", author=user,
                            content="x" * 30, status="published")
        Post.objects.create(title="d1", slug="d1", author=user,
                            content="x" * 30, status="draft")
        r = self.client.get(reverse("blog:home"))
        self.assertContains(r, "p1")
        self.assertNotContains(r, "d1")


class PostListViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("u", "u@u.com", "pass12345")

    def test_list_ok(self):
        r = self.client.get(reverse("blog:post_list"))
        self.assertEqual(r.status_code, 200)

    def test_search_by_title(self):
        Post.objects.create(title="آموزش جنگو", slug="a", author=self.user,
                            content="x" * 30, status="published")
        Post.objects.create(title="پایتون", slug="b", author=self.user,
                            content="x" * 30, status="published")
        r = self.client.get(reverse("blog:post_list"), {"q": "جنگو"})
        self.assertContains(r, "آموزش جنگو")
        self.assertNotContains(r, "پایتون")

    def test_search_by_content(self):
        Post.objects.create(title="عنوان", slug="c", author=self.user,
                            content="در این متن کلمه کلیدی خاص هست",
                            status="published")
        r = self.client.get(reverse("blog:post_list"), {"q": "کلیدی خاص"})
        self.assertContains(r, "عنوان")

    def test_filter_by_category(self):
        cat = Category.objects.create(name="دسته", slug="cat")
        Post.objects.create(title="در دسته", slug="x", author=self.user,
                            category=cat, content="x" * 30, status="published")
        Post.objects.create(title="بدون دسته", slug="y", author=self.user,
                            content="x" * 30, status="published")
        r = self.client.get(reverse("blog:post_list"), {"cat": "cat"})
        self.assertContains(r, "در دسته")
        self.assertNotContains(r, "بدون دسته")

    def test_sort_old(self):
        p1 = Post.objects.create(title="اول", slug="1", author=self.user,
                                 content="x" * 30, status="published")
        p2 = Post.objects.create(title="دوم", slug="2", author=self.user,
                                 content="x" * 30, status="published")
        r = self.client.get(reverse("blog:post_list"), {"sort": "old"})
        content = r.content.decode()
        self.assertLess(content.index("اول"), content.index("دوم"))

    def test_pagination(self):
        make_posts(self.user, n=15)
        r = self.client.get(reverse("blog:post_list"))
        self.assertEqual(len(r.context["page_obj"]), 9)
        r2 = self.client.get(reverse("blog:post_list"), {"page": 2})
        self.assertEqual(len(r2.context["page_obj"]), 6)


class PostDetailViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("u", "u@u.com", "pass12345")
        self.post = Post.objects.create(
            title="مقاله", slug="test-post", author=self.user,
            content="x" * 40, status="published",
        )

    def test_detail_ok(self):
        r = self.client.get(self.post.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "blog/post_detail.html")

    def test_404_for_missing(self):
        r = self.client.get("/posts/does-not-exist/")
        self.assertEqual(r.status_code, 404)

    def test_view_counter_increments(self):
        before = self.post.views
        self.client.get(self.post.get_absolute_url())
        self.post.refresh_from_db()
        self.assertEqual(self.post.views, before + 1)

    def test_view_counter_not_double_in_same_session(self):
        self.client.get(self.post.get_absolute_url())
        self.client.get(self.post.get_absolute_url())
        self.post.refresh_from_db()
        self.assertEqual(self.post.views, 1)

    def test_draft_404_for_anonymous(self):
        draft = Post.objects.create(
            title="پیش", slug="draft-x", author=self.user,
            content="x" * 40, status="draft",
        )
        r = self.client.get(draft.get_absolute_url())
        self.assertEqual(r.status_code, 404)

    def test_draft_200_for_owner(self):
        draft = Post.objects.create(
            title="پیش", slug="draft-y", author=self.user,
            content="x" * 40, status="draft",
        )
        self.client.login(username="u", password="pass12345")
        r = self.client.get(draft.get_absolute_url())
        self.assertEqual(r.status_code, 200)

    def test_draft_404_for_other(self):
        draft = Post.objects.create(
            title="پیش", slug="draft-z", author=self.user,
            content="x" * 40, status="draft",
        )
        User.objects.create_user("other", "o@o.com", "pass12345")
        self.client.login(username="other", password="pass12345")
        r = self.client.get(draft.get_absolute_url())
        self.assertEqual(r.status_code, 404)


class PostCRUDTest(TestCase):

    def setUp(self):
        self.author = User.objects.create_user("author", "a@a.com", "pass12345")
        self.other = User.objects.create_user("other", "o@o.com", "pass12345")
        self.post = Post.objects.create(
            title="مقاله", slug="test-post", author=self.author,
            content="x" * 40, status="published",
        )

    # ---------- ساخت ----------

    def test_create_requires_login(self):
        r = self.client.get(reverse("blog:post_create"))
        self.assertEqual(r.status_code, 302)

    def test_create_get(self):
        self.client.login(username="author", password="pass12345")
        r = self.client.get(reverse("blog:post_create"))
        self.assertEqual(r.status_code, 200)

    def test_create_post(self):
        self.client.login(username="author", password="pass12345")
        r = self.client.post(reverse("blog:post_create"), {
            "title": "مقاله جدید من",
            "content": "محتوای کامل مقاله جدید برای تست",
            "status": "published",
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Post.objects.filter(title="مقاله جدید من").exists())
        # نویسنده درست ثبت شود
        p = Post.objects.get(title="مقاله جدید من")
        self.assertEqual(p.author, self.author)

    # ---------- ویرایش ----------

    def test_update_owner(self):
        self.client.login(username="author", password="pass12345")
        r = self.client.get(reverse("blog:post_update", args=[self.post.slug]))
        self.assertEqual(r.status_code, 200)

    def test_update_other_404(self):
        self.client.login(username="other", password="pass12345")
        r = self.client.get(reverse("blog:post_update", args=[self.post.slug]))
        self.assertEqual(r.status_code, 404)

    def test_update_post(self):
        self.client.login(username="author", password="pass12345")
        r = self.client.post(
            reverse("blog:post_update", args=[self.post.slug]),
            {"title": "عنوان جدید", "content": "x" * 40, "status": "published"},
        )
        self.assertEqual(r.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "عنوان جدید")

    # ---------- حذف ----------

    def test_delete_owner_get(self):
        self.client.login(username="author", password="pass12345")
        r = self.client.get(reverse("blog:post_delete", args=[self.post.slug]))
        self.assertEqual(r.status_code, 200)

    def test_delete_other_404(self):
        self.client.login(username="other", password="pass12345")
        r = self.client.get(reverse("blog:post_delete", args=[self.post.slug]))
        self.assertEqual(r.status_code, 404)

    def test_delete_post(self):
        self.client.login(username="author", password="pass12345")
        r = self.client.post(reverse("blog:post_delete", args=[self.post.slug]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())


class DashboardViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("u", "u@u.com", "pass12345")

    def test_requires_login(self):
        r = self.client.get(reverse("blog:dashboard"))
        self.assertEqual(r.status_code, 302)

    def test_stats(self):
        Post.objects.create(title="p", slug="p", author=self.user,
                            content="x" * 30, status="published")
        Post.objects.create(title="d", slug="d", author=self.user,
                            content="x" * 30, status="draft")
        self.client.login(username="u", password="pass12345")
        r = self.client.get(reverse("blog:dashboard"))
        self.assertEqual(r.context["total"], 2)
        self.assertEqual(r.context["published"], 1)
        self.assertEqual(r.context["drafts"], 1)

    def test_shows_only_own_posts(self):
        User.objects.create_user("o", "o@o.com", "pass12345")
        other_post = Post.objects.create(
            title="مقاله دیگران", slug="others", author=User.objects.get(username="o"),
            content="x" * 30, status="published",
        )
        self.client.login(username="u", password="pass12345")
        r = self.client.get(reverse("blog:dashboard"))
        self.assertNotContains(r, "مقاله دیگران")


class CommentViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("u", "u@u.com", "pass12345")
        self.other = User.objects.create_user("o", "o@o.com", "pass12345")
        self.post = Post.objects.create(
            title="تست", slug="test", author=self.user,
            content="x" * 40, status="published",
        )

    def test_add_comment_requires_login(self):
        r = self.client.post(
            reverse("blog:add_comment", args=[self.post.slug]),
            {"body": "نظر"},
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Comment.objects.count(), 0)

    def test_add_comment(self):
        self.client.login(username="u", password="pass12345")
        r = self.client.post(
            reverse("blog:add_comment", args=[self.post.slug]),
            {"body": "نظر تست"},
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)
        c = Comment.objects.first()
        self.assertEqual(c.author, self.user)
        self.assertEqual(c.post, self.post)

    def test_comment_empty_body_rejected(self):
        self.client.login(username="u", password="pass12345")
        self.client.post(
            reverse("blog:add_comment", args=[self.post.slug]),
            {"body": ""},
        )
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_short_body_rejected(self):
        self.client.login(username="u", password="pass12345")
        self.client.post(
            reverse("blog:add_comment", args=[self.post.slug]),
            {"body": "ا"},
        )
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_on_draft_404(self):
        draft = Post.objects.create(
            title="پیش", slug="draft", author=self.user,
            content="x" * 40, status="draft",
        )
        self.client.login(username="u", password="pass12345")
        r = self.client.post(
            reverse("blog:add_comment", args=[draft.slug]),
            {"body": "نظر"},
        )
        self.assertEqual(r.status_code, 404)

    def test_delete_comment_owner(self):
        c = Comment.objects.create(post=self.post, author=self.user, body="x")
        self.client.login(username="u", password="pass12345")
        r = self.client.post(reverse("blog:delete_comment", args=[c.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=c.pk).exists())

    def test_delete_comment_other_forbidden(self):
        c = Comment.objects.create(post=self.post, author=self.user, body="x")
        self.client.login(username="o", password="pass12345")
        self.client.post(reverse("blog:delete_comment", args=[c.pk]))
        self.assertTrue(Comment.objects.filter(pk=c.pk).exists())

    def test_unapproved_comment_hidden(self):
        Comment.objects.create(post=self.post, author=self.user,
                               body="مخفی", is_approved=False)
        r = self.client.get(self.post.get_absolute_url())
        self.assertNotContains(r, "مخفی")