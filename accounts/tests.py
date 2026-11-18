from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile
from accounts.forms import RegisterForm, ProfileForm


class ProfileModelTest(TestCase):
    """تست مدل Profile"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="ali", email="ali@example.com", password="pass12345"
        )

    def test_profile_created_by_signal(self):
        """سیگنال post_save باید Profile بسازد"""
        self.assertTrue(hasattr(self.user, "profile"))
        self.assertIsInstance(self.user.profile, Profile)

    def test_profile_name_falls_back_to_username(self):
        """اگر نام و display_name خالی باشد، username برگردد"""
        self.assertEqual(self.user.profile.name, "ali")

    def test_profile_name_uses_full_name(self):
        """اگر first/last name پر باشد، نام کامل برگردد"""
        self.user.first_name = "علی"
        self.user.last_name = "رضایی"
        self.user.save()
        self.assertEqual(self.user.profile.name, "علی رضایی")

    def test_profile_name_uses_display_name(self):
        """display_name اولویت دارد بر username"""
        self.user.profile.display_name = "علی‌جان"
        self.user.profile.save()
        self.assertEqual(self.user.profile.name, "علی‌جان")

    def test_profile_str(self):
        self.assertEqual(str(self.user.profile), "پروفایل ali")


class RegisterFormTest(TestCase):
    """تست فرم ثبت‌نام"""

    def test_valid_form(self):
        form = RegisterForm(data={
            "username": "newuser",
            "email": "new@example.com",
            "password1": "StrongPass!2345",
            "password2": "StrongPass!2345",
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_duplicate_email_rejected(self):
        User.objects.create_user("u1", "dup@example.com", "pass12345")
        form = RegisterForm(data={
            "username": "u2",
            "email": "dup@example.com",
            "password1": "StrongPass!2345",
            "password2": "StrongPass!2345",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_password_mismatch(self):
        form = RegisterForm(data={
            "username": "u3",
            "email": "u3@example.com",
            "password1": "StrongPass!2345",
            "password2": "DifferentPass!2345",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)


class ProfileFormTest(TestCase):
    """تست فرم ویرایش پروفایل"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="sara", email="sara@example.com", password="pass12345"
        )

    def test_update_names_and_email(self):
        form = ProfileForm(
            data={
                "first_name": "سارا",
                "last_name": "احمدی",
                "email": "sara.new@example.com",
                "display_name": "سارا",
                "bio": "برنامه‌نویس",
                "website": "",
            },
            instance=self.user.profile,
            user=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "سارا")
        self.assertEqual(self.user.last_name, "احمدی")
        self.assertEqual(self.user.email, "sara.new@example.com")

    def test_duplicate_email_rejected(self):
        User.objects.create_user("other", "other@example.com", "pass12345")
        form = ProfileForm(
            data={
                "first_name": "سارا", "last_name": "احمدی",
                "email": "other@example.com",
                "display_name": "", "bio": "", "website": "",
            },
            instance=self.user.profile,
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class AuthViewsTest(TestCase):
    """تست ویوهای احراز هویت"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test", email="t@t.com", password="pass12345"
        )

    # ---------- ثبت‌نام ----------

    def test_register_get(self):
        r = self.client.get(reverse("accounts:register"))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "accounts/register.html")

    def test_register_post_success(self):
        r = self.client.post(reverse("accounts:register"), {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "StrongPass!2345",
            "password2": "StrongPass!2345",
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())
        # کاربر بعد از ثبت‌نام لاگین شده باشد
        self.assertEqual(int(self.client.session["_auth_user_id"]),
                         User.objects.get(username="newuser").pk)

    def test_register_redirect_if_logged_in(self):
        self.client.login(username="test", password="pass12345")
        r = self.client.get(reverse("accounts:register"))
        self.assertEqual(r.status_code, 302)

    # ---------- ورود ----------

    def test_login_get(self):
        r = self.client.get(reverse("accounts:login"))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "accounts/login.html")

    def test_login_post_success(self):
        r = self.client.post(reverse("accounts:login"), {
            "username": "test", "password": "pass12345",
        })
        self.assertEqual(r.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_post_invalid(self):
        r = self.client.post(reverse("accounts:login"), {
            "username": "test", "password": "wrong",
        })
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_with_next_redirect(self):
        r = self.client.post(
            reverse("accounts:login") + "?next=/dashboard/",
            {"username": "test", "password": "pass12345"},
        )
        self.assertRedirects(r, "/dashboard/")

    # ---------- خروج ----------

    def test_logout(self):
        self.client.login(username="test", password="pass12345")
        r = self.client.get(reverse("accounts:logout"))
        self.assertEqual(r.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

    # ---------- پروفایل ----------

    def test_profile_requires_login(self):
        r = self.client.get(reverse("accounts:profile"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/accounts/login/", r.url)

    def test_profile_view(self):
        self.client.login(username="test", password="pass12345")
        r = self.client.get(reverse("accounts:profile"))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "accounts/profile.html")

    # ---------- ویرایش پروفایل ----------

    def test_profile_edit_get(self):
        self.client.login(username="test", password="pass12345")
        r = self.client.get(reverse("accounts:profile_edit"))
        self.assertEqual(r.status_code, 200)

    def test_profile_edit_post(self):
        self.client.login(username="test", password="pass12345")
        r = self.client.post(reverse("accounts:profile_edit"), {
            "first_name": "نام", "last_name": "خانوادگی",
            "email": "t2@t.com", "display_name": "", "bio": "", "website": "",
        })
        self.assertEqual(r.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "نام")

    # ---------- تغییر رمز ----------

    def test_change_password(self):
        self.client.login(username="test", password="pass12345")
        r = self.client.post(reverse("accounts:change_password"), {
            "old_password": "pass12345",
            "new_password1": "NewStrong!2345",
            "new_password2": "NewStrong!2345",
        })
        self.assertEqual(r.status_code, 302)
        # لاگین بماند
        self.assertIn("_auth_user_id", self.client.session)
        # رمز جدید کار کند
        self.client.logout()
        self.assertTrue(self.client.login(username="test",
                                           password="NewStrong!2345"))