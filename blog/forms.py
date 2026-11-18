from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "category", "summary", "content", "cover", "status")
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "عنوان مقاله"}),
            "summary": forms.TextInput(attrs={"placeholder": "خلاصه کوتاه"}),
            "content": forms.Textarea(attrs={"rows": 12,
                                             "placeholder": "متن مقاله..."}),
        }

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop("author", None)
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", "form-input")

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 5:
            raise forms.ValidationError("عنوان حداقل ۵ کاراکتر باشد.")
        return title

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if len(content) < 20:
            raise forms.ValidationError("محتوا حداقل ۲۰ کاراکتر باشد.")
        return content

    def clean_cover(self):
        cover = self.cleaned_data.get("cover")
        if cover and cover.size > 3 * 1024 * 1024:
            raise forms.ValidationError("حجم تصویر نباید از ۳ مگابایت بیشتر باشد.")
        return cover

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)
        widgets = {"body": forms.Textarea(attrs={"rows": 4,
                                                  "placeholder": "نظر خود را بنویسید..."})}

    def clean_body(self):
        body = self.cleaned_data["body"].strip()
        if len(body) < 3:
            raise forms.ValidationError("متن نظر خیلی کوتاه است.")
        return body
