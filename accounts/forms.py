from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="ایمیل", required=True)
    first_name = forms.CharField(label="نام", max_length=50, required=False)
    last_name = forms.CharField(label="نام خانوادگی", max_length=50, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name",
                  "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("این ایمیل قبلاً ثبت شده است.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "username": "نام کاربری",
            "email": "ایمیل",
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "password1": "رمز عبور",
            "password2": "تکرار رمز عبور",
        }
        for name, ph in placeholders.items():
            if name in self.fields:
                self.fields[name].widget.attrs.update(
                    {"placeholder": ph, "class": "form-input"}
                )


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"placeholder": "نام کاربری", "class": "form-input"})
        self.fields["password"].widget.attrs.update(
            {"placeholder": "رمز عبور", "class": "form-input"})


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label="نام", max_length=50, required=False)
    last_name = forms.CharField(label="نام خانوادگی", max_length=50, required=False)
    email = forms.EmailField(label="ایمیل", required=True)

    class Meta:
        model = Profile
        fields = ("display_name", "bio", "website", "avatar")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "درباره من..."}),
            "website": forms.URLInput(attrs={"placeholder": "https://..."}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", "form-input")
        if self.user:
            self.fields["first_name"].initial = self.user.first_name
            self.fields["last_name"].initial = self.user.last_name
            self.fields["email"].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email) \
                .exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("این ایمیل توسط کاربر دیگری استفاده می‌شود.")
        return email

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar and avatar.size > 3 * 1024 * 1024:
            raise forms.ValidationError("حجم تصویر نباید از ۳ مگابایت بیشتر باشد.")
        return avatar

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data["first_name"]
            self.user.last_name = self.cleaned_data["last_name"]
            self.user.email = self.cleaned_data["email"]
            self.user.save()
        if commit:
            profile.save()
        return profile