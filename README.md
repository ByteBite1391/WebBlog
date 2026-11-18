# وبلاگ حرفه‌ای Django

یک وبلاگ کامل، فارسی، راست‌به‌چپ و ریسپانسیو با Django. شامل احراز هویت کامل، مدیریت مقالات، دسته‌بندی، جستجو، نظرات، داشبورد نویسنده، پروفایل با آواتار، سیستم لاگ کامل فعالیت‌ها و آیکون‌های SVG (بدون Font Awesome).

---

## فهرست

- ویژگی‌ها
- پیش‌نیازها
- نصب و راه‌اندازی
- ساختار پروژه
- مدل‌ها
- مسیرها (URLs)
- تنظیمات مهم
- داده نمونه
- تست‌ها
- سیستم لاگ
- امنیت
- عیب‌یابی
- توسعه

---

## ویژگی‌ها

### کاربران
- ثبت‌نام، ورود، خروج
- پروفایل با آواتار، نام، نام خانوادگی، ایمیل، بیو، وب‌سایت، نام نمایشی
- ویرایش پروفایل از داخل داشبورد
- تغییر رمز عبور
- فراموشی رمز عبور (ایمیل — در توسعه در کنسول چاپ می‌شود)

### مقالات
- ایجاد، ویرایش، حذف توسط نویسنده
- وضعیت پیش‌نویس / منتشرشده
- تاریخ انتشار خودکار
- تصویر شاخص
- slug یکتا با پشتیبانی از حروف فارسی
- شمارنده بازدید (یک‌بار در هر session)
- مقالات مرتبط بر اساس دسته

### دسته‌بندی
- مدیریت از پنل ادمین
- slug خودکار
- نمایش تعداد مقالات منتشرشده
- صفحه اختصاصی هر دسته

### جستجو و فیلتر
- جستجو در عنوان، خلاصه و محتوا
- فیلتر بر اساس دسته
- مرتب‌سازی جدیدترین / قدیمی‌ترین
- صفحه‌بندی ۹ مقاله در هر صفحه
- حفظ پارامترها در صفحه‌بندی

### نظرات
- ثبت توسط کاربران واردشده
- حذف توسط صاحب نظر یا کارکنان
- فیلد تأیید (is_approved)
- اعتبارسنجی سمت سرور

### داشبورد نویسنده
- کارت پروفایل با آواتار
- آمار: کل مقالات، منتشرشده، پیش‌نویس، نظرات
- لیست مقالات من با عملیات سریع
- نظرات روی مقالات من

### رابط کاربری
- فونت Vazirmatn
- کاملاً RTL
- ریسپانسیو (موبایل، تبلت، دسکتاپ)
- آیکون‌های SVG Sprite (بدون CDN، آفلاین)
- انیمیشن‌های ظریف CSS
- دسترس‌پذیری (aria-label روی لینک‌های آیکونی)

### لاگ‌گیری
- مدل ActivityLog با IP، User-Agent، مسیر، متد، متادیتا
- ثبت خودکار ورود/خروج/ورود ناموفق از طریق سیگنال
- ثبت خودکار ایجاد/ویرایش/حذف مقاله و نظر
- ثبت لاگ خطاها در logs/errors.log
- ثبت رخدادهای امنیتی در logs/security.log
- مدیریت لاگ‌ها از پنل ادمین
- دستور پاکسازی لاگ‌های قدیمی

---

## پیش‌نیازها

- Python 3.10 یا بالاتر
- Django 4.2 یا بالاتر
- Pillow (برای آپلود تصویر)

---

## نصب و راه‌اندازی

### ۱. کلون یا باز کردن پوشه پروژه

    cd blogsite

### ۲. ساخت محیط مجازی (توصیه‌شده)

    # ویندوز
    python -m venv .venv
    .venv\Scripts\activate

    # لینوکس / مک
    python3 -m venv .venv
    source .venv/bin/activate

### ۳. نصب وابستگی‌ها

    pip install -r requirements.txt

یا دستی:

    pip install "Django>=4.2,<5.0" Pillow

### ۴. ساخت مایگریشن‌ها و اعمال

    python manage.py makemigrations accounts
    python manage.py makemigrations blog
    python manage.py migrate

> مهم: همیشه makemigrations قبل از migrate. اگر migrate را بدون ساخت مایگریشن اجرا کنید، جدول‌ها ساخته نمی‌شوند.

### ۵. ساخت سوپریوزر

    python manage.py createsuperuser

### ۶. (اختیاری) پر کردن با داده نمونه

    python manage.py seed_data

این دستور می‌سازد:
- ۱ ادمین: admin / admin12345
- ۴ کاربر عادی (رمز همه: pass12345): ali, sara, reza, mina
- ۷ دسته‌بندی
- ۱۵ مقاله (بیشتر منتشرشده، برخی پیش‌نویس)
- حدود ۲۰ نظر

برای پاک کردن و ساخت مجدد:

    python manage.py seed_data --reset

### ۷. اجرا

    python manage.py runserver

سپس:

- وبلاگ: http://127.0.0.1:8000/
- پنل ادمین: http://127.0.0.1:8000/admin/

---

## ساختار پروژه

    blogsite/
    ├── manage.py
    ├── requirements.txt
    ├── README.md
    ├── db.sqlite3                  # دیتابیس توسعه
    ├── logs/                       # لاگ‌ها
    │   ├── app.log
    │   ├── errors.log
    │   └── security.log
    ├── media/                      # آپلودها
    │   ├── avatars/
    │   └── covers/
    ├── static/
    │   └── css/
    │       ├── main.css
    │       └── grid.css
    ├── templates/
    │   ├── base.html
    │   ├── 404.html
    │   ├── 500.html
    │   ├── partials/
    │   │   ├── icons.html          # SVG Sprite
    │   │   ├── navbar.html
    │   │   └── footer.html
    │   ├── blog/
    │   │   ├── home.html
    │   │   ├── post_list.html
    │   │   ├── post_detail.html
    │   │   ├── post_form.html
    │   │   ├── post_confirm_delete.html
    │   │   ├── category_detail.html
    │   │   └── dashboard.html
    │   └── accounts/
    │       ├── login.html
    │       ├── register.html
    │       ├── profile.html
    │       ├── profile_edit.html
    │       ├── change_password.html
    │       └── password_reset*.html
    ├── blogsite/                   # تنظیمات پروژه
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    ├── accounts/                   # اپ کاربران
    │   ├── models.py               # Profile, ActivityLog
    │   ├── forms.py
    │   ├── views.py
    │   ├── urls.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── signals.py
    │   ├── middleware.py
    │   ├── utils.py
    │   ├── tests.py
    │   └── management/
    │       └── commands/
    │           └── cleanup_logs.py
    └── blog/                       # اپ وبلاگ
        ├── models.py               # Category, Post, Comment
        ├── forms.py
        ├── views.py
        ├── urls.py
        ├── admin.py
        ├── apps.py
        ├── signals.py
        ├── context_processors.py
        ├── tests/
        │   ├── test_models.py
        │   ├── test_views.py
        │   ├── test_forms.py
        │   ├── test_permissions.py
        │   └── test_admin.py
        └── management/
            └── commands/
                └── seed_data.py

---

## مدل‌ها

### accounts.Profile

| فیلد | نوع | توضیح |
|------|-----|-------|
| user | OneToOne → User | کاربر |
| display_name | CharField | نام نمایشی |
| bio | TextField | بیوگرافی |
| website | URLField | وب‌سایت |
| avatar | ImageField | آواتار (حداکثر ۳MB) |
| created_at / updated_at | DateTime | زمان‌ها |

Profile به‌طور خودکار با سیگنال post_save روی User ساخته می‌شود. property name اولویت می‌دهد به: نام کامل → نام نمایشی → username.

### accounts.ActivityLog

| فیلد | نوع | توضیح |
|------|-----|-------|
| user | FK → User (nullable) | کاربر (ناشناس = null) |
| action | CharField + choices | نوع فعالیت (۱۵ نوع) |
| ip_address | GenericIPAddressField | IP (با پشتیبانی X-Forwarded-For) |
| user_agent | TextField | مرورگر |
| path | CharField | مسیر درخواست |
| method | CharField | GET/POST/... |
| metadata | JSONField | داده‌های اضافی |
| duration_ms | PositiveInteger | مدت پاسخ |
| status_code | SmallInteger | کد وضعیت HTTP |
| created_at | DateTime | زمان |

### blog.Category

| فیلد | نوع |
|------|-----|
| name | CharField (unique) |
| slug | SlugField (unique, allow_unicode) |
| description | TextField |
| created_at | DateTime |

### blog.Post

| فیلد | نوع |
|------|-----|
| title | CharField |
| slug | SlugField (unique, allow_unicode) |
| author | FK → User |
| category | FK → Category (nullable) |
| summary | CharField |
| content | TextField |
| cover | ImageField |
| status | draft / published |
| views | PositiveInteger |
| published_at | DateTime (خودکار در انتشار) |
| created_at / updated_at | DateTime |

Manager سفارشی Post.objects.published() فقط مقالات منتشرشده با تاریخ گذشته را برمی‌گرداند. slugهای رزروشده (new, dashboard, ...) به‌طور خودکار پسوند -post می‌گیرند.

### blog.Comment

| فیلد | نوع |
|------|-----|
| post | FK → Post |
| author | FK → User |
| body | TextField (حداکثر ۲۰۰۰) |
| is_approved | Boolean (پیش‌فرض True) |
| created_at | DateTime |

---

## مسیرها (URLs)

### عمومی (blog)

| مسیر | نام | توضیح |
|------|-----|-------|
| / | home | صفحه اصلی |
| /posts/ | post_list | لیست مقالات |
| /search/ | search | جستجو |
| /posts/<slug>/ | detail | جزئیات مقاله |
| /category/<slug>/ | category | مقالات یک دسته |

### نویسنده (blog، نیازمند ورود)

| مسیر | نام | توضیح |
|------|-----|-------|
| /dashboard/ | dashboard | داشبورد |
| /posts/new/ | post_create | مقاله جدید |
| /posts/<slug>/edit/ | post_update | ویرایش |
| /posts/<slug>/delete/ | post_delete | حذف |
| /posts/<slug>/comment/ | add_comment | ثبت نظر (POST) |
| /comments/<pk>/delete/ | delete_comment | حذف نظر (POST) |

### احراز هویت (accounts)

| مسیر | نام |
|------|-----|
| /accounts/register/ | register |
| /accounts/login/ | login |
| /accounts/logout/ | logout |
| /accounts/profile/ | profile |
| /accounts/profile/edit/ | profile_edit |
| /accounts/password/change/ | change_password |
| /accounts/password/reset/ | password_reset |
| /accounts/password/reset/done/ | password_reset_done |
| /accounts/password/reset/<uidb64>/<token>/ | password_reset_confirm |
| /accounts/password/reset/complete/ | password_reset_complete |

### ادمین

| مسیر | توضیح |
|------|-------|
| /admin/ | پنل مدیریت Django |

> نکته slug فارسی: الگوهای <slug:...> پیش‌فرض Django فقط [a-zA-Z0-9_-] را می‌پذیرند. برای پشتیبانی از slug فارسی (مثل جنگو-چیست)، از re_path(r"^posts/(?P<slug>[-\w]+)/$", ...) استفاده شده است.

---

## تنظیمات مهم

در blogsite/settings.py:

    # امنیت
    SESSION_COOKIE_HTTPONLY = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"

    # محدودیت آپلود
    DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
    FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

    # زبان و زمان
    LANGUAGE_CODE = "fa"
    TIME_ZONE = "Asia/Tehran"
    USE_TZ = True

### متغیرهای محیطی

| متغیر | پیش‌فرض | توضیح |
|-------|---------|-------|
| DJANGO_SECRET_KEY | مقدار ناامن | در production الزامی |
| DJANGO_DEBUG | 1 | در production 0 |

مثال در production (لینوکس):

    export DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
    export DJANGO_DEBUG=0

---

## داده نمونه

### ساخت

    python manage.py seed_data

### گزینه‌ها

    # تعداد کاربران و مقالات
    python manage.py seed_data --users 3 --posts 10

    # پاک کردن قبلی‌ها
    python manage.py seed_data --reset

    # نتایج تصادفی یکسان (برای تست/CI)
    python manage.py seed_data --seed 42

### داده‌های ساخته‌شده
- ادمین: admin / admin12345
- کاربران: ali, sara, reza, mina — رمز همه: pass12345
- دسته‌بندی: برنامه‌نویسی، جنگو، پایتون، فرانت‌اند، دواپس، هوش مصنوعی، تجربه کاربری
- مقالات: ۱۵ عنوان مرتبط با جنگو/پایتون، بیشتر منتشرشده
- نظرات: ۰ تا ۴ نظر برای هر مقاله منتشرشده

> دستور idempotent است — اجرای دوباره داده تکراری نمی‌سازد.

---

## تست‌ها

### اجرا

    # همه
    python manage.py test

    # یک اپ
    python manage.py test accounts
    python manage.py test blog

    # یک فایل
    python manage.py test blog.tests.test_views

    # یک کلاس
    python manage.py test blog.tests.test_views.PostCRUDTest

    # با جزئیات بیشتر
    python manage.py test -v 2

    # توقف در اولین خطا
    python manage.py test --failfast

### پوشش

    pip install coverage
    coverage run --source='.' manage.py test
    coverage report -m
    coverage html   # خروجی در htmlcov/index.html

### آنچه تست می‌شود
- مدل‌ها (Profile, ActivityLog, Category, Post, Comment)
- فرم‌ها (Register, Login, Profile, Post, Comment)
- ویوهای احراز هویت (۱۲ تست)
- ویوهای مقاله (CRUD + دسترسی + شمارنده بازدید)
- داشبورد و آمار
- نظرات
- IDOR — کاربر A نمی‌تواند مقاله B را ویرایش/حذف کند
- تنظیمات ادمین

حدود ۷۵ تست.

---

## سیستم لاگ

### لاگ دیتابیس (ActivityLog)

تمام فعالیت‌های مهم در جدول accounts_activitylog ذخیره می‌شوند:

| نوع فعالیت | منبع ثبت |
|-----------|----------|
| login, logout, login_failed | سیگنال‌های Django |
| register, password_change, profile_update | ویوهای accounts |
| post_create, post_update, post_delete | سیگنال‌های blog + ویوها |
| comment_create, comment_delete | سیگنال‌های blog + ویوها |
| view_post | ویو post_detail |
| search | ویو search |
| admin_access | middleware |

مشاهده در ادمین: /admin/accounts/activitylog/

### لاگ فایل

| فایل | محتوا |
|------|-------|
| logs/app.log | همه لاگ‌های INFO+ |
| logs/errors.log | فقط ERROR+ (شامل traceback) |
| logs/security.log | رخدادهای امنیتی (CSRF، دسترسی غیرمجاز) |

چرخش خودکار: هر فایل حداکثر ۵MB، ۳ نسخه backup.

### پاکسازی لاگ‌های قدیمی

    # پیش‌فرض: نگه‌داشتن ۳۰ روز اخیر
    python manage.py cleanup_logs

    # تعداد روز دلخواه
    python manage.py cleanup_logs --days 7

    # فقط شمارش، بدون حذف
    python manage.py cleanup_logs --dry-run

در production این دستور را روزانه با cron اجرا کنید:

    0 3 * * * cd /path/to/blogsite && /path/to/venv/bin/python manage.py cleanup_logs --days 30

---

## امنیت

### پیاده‌شده

- CSRF — تمام فرم‌ها {% csrf_token %} دارند
- XSS — خروجی محتوا با linebreaks و escape خودکار تمپلیت
- IDOR — تمام عملیات نویسنده با get_object_or_404(..., author=request.user)
- دسترسی — @login_required روی همه ویوهای خصوصی
- آپلود — محدودیت حجم ۳MB در فرم‌ها + ۵MB در settings
- پیش‌نویس — فقط نویسنده (یا 404 برای دیگران)
- رمز — هش استاندارد Django + اعتبارسنجی ۴گانه
- هدرها — X-Frame-Options: DENY, nosniff, Referrer-Policy
- کوکی — SESSION_COOKIE_HTTPONLY=True
- لاگ امنیتی — رخدادهای django.security در فایل جدا

### چک‌لیست پیش از production

- [ ] DEBUG = False
- [ ] SECRET_KEY از متغیر محیطی
- [ ] ALLOWED_HOSTS با دامنه واقعی
- [ ] SECURE_SSL_REDIRECT = True
- [ ] SESSION_COOKIE_SECURE = True
- [ ] CSRF_COOKIE_SECURE = True
- [ ] SECURE_HSTS_SECONDS = 31536000
- [ ] python manage.py check --deploy
- [ ] python manage.py collectstatic
- [ ] بکاپ منظم db.sqlite3 (یا مهاجرت به PostgreSQL)
- [ ] cleanup_logs روزانه با cron
- [ ] سرور WSGI حرفه‌ای (gunicorn + nginx)

---

## عیب‌یابی

### no such table: accounts_profile

شما migrate را قبل از makemigrations اجرا کرده‌اید.

    python manage.py makemigrations
    python manage.py migrate

اگر دیتابیس داده مهمی ندارد و می‌خواهید از صفر شروع کنید:

    del db.sqlite3    # ویندوز
    rm db.sqlite3     # لینوکس
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser

### NoReverseMatch برای slug فارسی

الگوهای <slug:...> فقط ASCII می‌پذیرند. باید از re_path با الگوی [-\w]+ استفاده کنید (در blog/urls.py اعمال شده).

### Page not found برای /posts/new/

ترتیب URLها مهم است: posts/new/ باید قبل از posts/<slug>/ باشد. همچنین slug مقاله‌ای با عنوان new به new-post تغییر می‌کند.

### TemplateDoesNotExist: 404.html

Django در حالت DEBUG=False به تمپلیت 404/500 نیاز دارد. این فایل‌ها در templates/ هستند — مطمئن شوید در TEMPLATES["DIRS"] قرار دارد.

### تصویر آپلود نمی‌شود

- Pillow نصب باشد: pip install Pillow
- حجم کمتر از ۳MB
- MEDIA_ROOT و MEDIA_URL در settings
- static() در urls.py فقط در DEBUG=True

### لاگ‌ها در ActivityLog ثبت نمی‌شوند

- accounts/apps.py با def ready(): import accounts.signals باشد
- INSTALLED_APPS از accounts.apps.AccountsConfig استفاده کند (نه accounts)
- python manage.py migrate برای ساخت جدول اجرا شده باشد

### 304 روی تصاویر

مرورگر نسخه کش‌شده را دارد. Ctrl+F5 بزنید.

---

## توسعه

### افزودن اپ جدید

    python manage.py startapp myapp

سپس در settings.py به INSTALLED_APPS اضافه کنید و در blogsite/urls.py مسیر بدهید.

### افزودن آیکون SVG

۱. در templates/partials/icons.html یک <symbol> اضافه کنید:

    <symbol id="i-myicon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <!-- pathها -->
    </symbol>

۲. استفاده در تمپلیت:

    <svg class="icon"><use href="#i-myicon"/></svg>

کلاس‌های سایز: icon-sm, icon, icon-lg, icon-xl, icon-2xl. برای آیکون‌های filled: icon icon--filled.

### افزودن نوع لاگ جدید

۱. در accounts/models.py به ActivityLog.ACTION_CHOICES اضافه کنید:

    ACTION_MY_ACTION = "my_action"
    # ...
    (ACTION_MY_ACTION, "فعالیت جدید من"),

۲. در کد فراخوانی کنید:

    from accounts.utils import log_activity
    log_activity(request, "my_action", user=request.user, extra_field="value")

۳. python manage.py makemigrations accounts && migrate

### افزودن زبان جدید

فایل‌های ترجمه در locale/:

    django-admin makemessages -l ar
    # ترجمه در locale/ar/LC_MESSAGES/django.po
    django-admin compilemessages

---

## مجوز

این پروژه برای استفاده شخصی و آموزشی آزاد است. برای استفاده تجاری، کد را مرور و تنظیمات production را اعمال کنید.

---

## قدردانی

- Django — https://www.djangoproject.com/
- Vazirmatn — https://github.com/rastikerdar/vazirmatn (فونت فارسی)
- Feather Icons — https://feathericons.com/ (الهام آیکون‌های SVG)