from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from blog.admin import PostAdmin, CategoryAdmin, CommentAdmin
from blog.models import Post, Category, Comment


class AdminTest(TestCase):
    """تست تنظیمات ادمین — فقط پیکربندی، نه UI"""

    def setUp(self):
        self.site = AdminSite()
        self.user = User.objects.create_user("admin", "a@a.com", "pass12345",
                                              is_staff=True, is_superuser=True)

    def test_post_admin_config(self):
        ma = PostAdmin(Post, self.site)
        self.assertIn("title", ma.list_display)
        self.assertIn("status", ma.list_filter)
        self.assertIn("title", ma.search_fields)
        self.assertEqual(ma.list_editable, ("status",))

    def test_category_admin_config(self):
        ma = CategoryAdmin(Category, self.site)
        self.assertIn("name", ma.list_display)
        self.assertIn("slug", ma.prepopulated_fields)

    def test_comment_admin_config(self):
        ma = CommentAdmin(Comment, self.site)
        self.assertIn("is_approved", ma.list_filter)