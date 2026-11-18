from django.test import TestCase
from django.contrib.auth.models import User
from blog.forms import PostForm, CommentForm


class PostFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("u", "u@u.com", "pass12345")

    def test_valid(self):
        form = PostForm(data={
            "title": "عنوان معتبر",
            "content": "محتوای کافی برای این مقاله تست.",
            "status": "draft",
        }, author=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_title_too_short(self):
        form = PostForm(data={
            "title": "کوتاه",  # 5 کاراکتر نیست
            "content": "x" * 30, "status": "draft",
        }, author=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_content_too_short(self):
        form = PostForm(data={
            "title": "عنوان معتبر",
            "content": "کم", "status": "draft",
        }, author=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)


class CommentFormTest(TestCase):

    def test_valid(self):
        form = CommentForm(data={"body": "نظر خوب"})
        self.assertTrue(form.is_valid())

    def test_empty(self):
        form = CommentForm(data={"body": ""})
        self.assertFalse(form.is_valid())

    def test_short(self):
        form = CommentForm(data={"body": "ا"})
        self.assertFalse(form.is_valid())