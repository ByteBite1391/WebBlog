from .models import Category
def site_globals(request):
    return {
        "SITE_NAME": "وبلاگ من",
        "SITE_TAGLINE": "دنیای مقالات و یادداشت‌ها",
        "nav_categories": Category.objects.all()[:6],
    }
