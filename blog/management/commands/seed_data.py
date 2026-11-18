"""
دستور مدیریتی برای پر کردن دیتابیس با داده‌های نمونه.

استفاده:
    python manage.py seed_data
    python manage.py seed_data --reset       # پاک کردن داده‌های قبلی نمونه
    python manage.py seed_data --users 5 --posts 20
"""
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from blog.models import Category, Post, Comment
from accounts.models import Profile


CATEGORIES = [
    ("برنامه‌نویسی", "آموزش‌ها و مقالات مرتبط با برنامه‌نویسی"),
    ("جنگو", "همه‌چیز درباره فریم‌ورک Django"),
    ("پایتون", "مقالات زبان برنامه‌نویسی پایتون"),
    ("فرانت‌اند", "HTML، CSS، JavaScript و طراحی رابط کاربری"),
    ("دواپس", "ابزارها و مفاهیم DevOps"),
    ("هوش مصنوعی", "یادگیری ماشین و مدل‌های زبانی"),
    ("تجربه کاربری", "طراحی تجربه و رابط کاربری"),
]

USERS = [
    # (username, email, first_name, last_name, password, is_staff)
    ("ali", "ali@example.com", "علی", "رضایی", "pass12345", False),
    ("sara", "sara@example.com", "سارا", "احمدی", "pass12345", False),
    ("reza", "reza@example.com", "رضا", "کریمی", "pass12345", False),
    ("mina", "mina@example.com", "مینا", "حسینی", "pass12345", False),
]

ADMIN = ("admin", "admin@example.com", "مدیر", "سیستم", "admin12345", True)

TITLES = [
    "جنگو چیست و چرا محبوب است؟",
    "آموزش نصب و راه‌اندازی Django",
    "مدل‌ها در جنگو: از صفر تا صد",
    "تفاوت Function-Based و Class-Based View",
    "چگونه امنیت وب‌سایت جنگو را افزایش دهیم",
    "بهترین روش‌های کار با فرم‌ها در جنگو",
    "آشنایی با ORM و کوئری‌های بهینه",
    "قالب‌ها و ارث‌بری در Django Template Engine",
    "مدیریت کاربران و احراز هویت در جنگو",
    "آپلود فایل و تصویر در جنگو",
    "پکیج‌های پرکاربرد Django",
    "تست‌نویسی حرفه‌ای در جنگو",
    "استقرار پروژه جنگو روی سرور",
    "کش کردن و بهینه‌سازی سرعت در جنگو",
    "سیگنال‌ها در جنگو: چه زمانی و چگونه",
    "ساخت REST API با DRF",
    "مدیریت نشست و کوکی در جنگو",
    "تنظیمات امنیتی مهم settings.py",
    "لاگ‌گیری و مانیتورینگ پروژه جنگو",
    "چگونه یک وبلاگ حرفه‌ای با جنگو بسازیم",
]

SUMMARIES = [
    "در این مقاله به‌طور کامل با این موضوع آشنا می‌شوید.",
    "بررسی جامع و کاربردی برای توسعه‌دهندگان جنگو.",
    "راهنمای گام‌به‌گام با مثال‌های عملی.",
    "نکات مهمی که هر برنامه‌نویس باید بداند.",
    "تجربه‌ای واقعی از پروژه‌های حرفه‌ای.",
]

CONTENT_TEMPLATE = """
<p>{intro}</p>

<h2>مقدمه</h2>
<p>در دنیای امروز توسعه وب، انتخاب ابزار مناسب نقش کلیدی در موفقیت پروژه دارد.
فریم‌ورک Django یکی از محبوب‌ترین گزینه‌ها برای ساخت وب‌سایت‌های امن و مقیاس‌پذیر است.
در این مقاله می‌خواهیم به‌طور دقیق به این موضوع بپردازیم.</p>

<h2>چرا این موضوع مهم است؟</h2>
<p>درک درست این مفهوم می‌تواند کیفیت کد شما را به‌طور چشمگیری افزایش دهد
و از بروز بسیاری از خطاهای رایج جلوگیری کند. برنامه‌نویسان حرفه‌ای همیشه
به اصول و بهترین روش‌ها پایبند هستند.</p>

<h2>مثال عملی</h2>
<p>فرض کنید می‌خواهیم یک قابلیت جدید به پروژه اضافه کنیم. مسیر استاندارد
شامل مراحل زیر است: طراحی مدل، ساخت مهاجرت، نوشتن ویو، اتصال URL و در نهایت
ساخت تمپلیت. اگر هر یک از این مراحل به‌درستی انجام شود، نتیجه‌ای حرفه‌ای خواهیم داشت.</p>

<h2>نکات مهم</h2>
<ul>
  <li>همیشه اعتبارسنجی سمت سرور را جدی بگیرید.</li>
  <li>از ORM به‌جای کوئری خام استفاده کنید.</li>
  <li>دسترسی‌ها را در هر ویو بررسی کنید.</li>
  <li>تست بنویسید تا تغییرات آینده بی‌خطر باشند.</li>
</ul>

<h2>جمع‌بندی</h2>
<p>امیدواریم این مقاله برای شما مفید بوده باشد. اگر سؤال یا نظری دارید،
در بخش نظرات با ما در میان بگذارید.</p>
"""

COMMENTS = [
    "مقاله بسیار مفیدی بود، ممنون!",
    "خیلی خوب توضیح داده شده. ادامه بدهید.",
    "من هم با این موضوع مواجه شدم و مشکل حل شد.",
    "لطفاً درباره این موضوع بیشتر بنویسید.",
    "بهترین مقاله‌ای بود که در این باره خوندم.",
    "یک سؤال داشتم: آیا این روش در نسخه‌های قدیمی هم کار می‌کند؟",
    "دست شما درد نکنه، خیلی کمک کرد.",
    "منتظر مقالات بعدی هستم.",
]


class Command(BaseCommand):
    help = "پر کردن دیتابیس با کاربران، دسته‌بندی‌ها، مقالات و نظرات نمونه"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users", type=int, default=4,
            help="تعداد کاربران عادی (پیش‌فرض: 4)",
        )
        parser.add_argument(
            "--posts", type=int, default=15,
            help="تعداد مقالات (پیش‌فرض: 15)",
        )
        parser.add_argument(
            "--reset", action="store_true",
            help="پاک کردن داده‌های قبلی نمونه قبل از ساخت",
        )
        parser.add_argument(
            "--seed", type=int, default=None,
            help="مقدار seed برای بازتولید نتایج تصادفی یکسان",
        )

    def handle(self, *args, **options):
        if options["seed"] is not None:
            random.seed(options["seed"])

        if options["reset"]:
            self._reset()

        admin = self._create_admin()
        users = self._create_users(options["users"])
        categories = self._create_categories()
        posts = self._create_posts(users, categories, options["posts"])
        self._create_comments(posts, users)

        self.stdout.write(self.style.SUCCESS("\n✅ داده‌های نمونه با موفقیت ساخته شدند."))
        self.stdout.write(self.style.SUCCESS(
            f"   ادمین: {admin.username} / {ADMIN[4]}\n"
            f"   کاربران: {len(users)} | دسته‌بندی: {len(categories)} | "
            f"مقالات: {len(posts)} | نظرات: {sum(p.comments.count() for p in posts)}"
        ))

    # ----------------------------------------------------------
    def _reset(self):
        self.stdout.write(self.style.WARNING("⚠️  پاک کردن داده‌های قبلی..."))
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Category.objects.all().delete()
        # فقط کاربران تستی پاک شوند، نه superuser اصلی
        usernames = [u[0] for u in USERS] + [ADMIN[0]]
        User.objects.filter(username__in=usernames).delete()
        self.stdout.write(self.style.WARNING("   پاک شد.\n"))

    # ----------------------------------------------------------
    def _create_admin(self):
        username, email, first, last, password, is_staff = ADMIN
        admin, created = User.objects.get_or_create(
            username=username,
            defaults=dict(email=email, first_name=first, last_name=last,
                         is_staff=True, is_superuser=True),
        )
        if created:
            admin.set_password(password)
            admin.save()
            self.stdout.write(f"  ✓ ادمین ساخته شد: {username}")
        else:
            self.stdout.write(f"  • ادمین موجود است: {username}")
        return admin

    # ----------------------------------------------------------
    def _create_users(self, count):
        users = []
        for i, (username, email, first, last, password, _) in enumerate(USERS):
            if i >= count:
                break
            user, created = User.objects.get_or_create(
                username=username,
                defaults=dict(email=email, first_name=first, last_name=last),
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f"  ✓ کاربر ساخته شد: {username}")
            else:
                self.stdout.write(f"  • کاربر موجود است: {username}")
            users.append(user)
        return users

    # ----------------------------------------------------------
    def _create_categories(self):
        cats = []
        for name, desc in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                name=name, defaults={"description": desc},
            )
            if created:
                self.stdout.write(f"  ✓ دسته‌بندی: {name}")
            cats.append(cat)
        return cats

    # ----------------------------------------------------------
    def _create_posts(self, users, categories, count):
        posts = []
        titles = TITLES[:count]
        now = timezone.now()

        for i, title in enumerate(titles):
            # slug را از عنوان نمی‌سازیم تا از تداخل مطمئن باشیم
            # اما اگر وجود داشت skip می‌کنیم
            if Post.objects.filter(title=title).exists():
                self.stdout.write(f"  • مقاله موجود است: {title}")
                posts.append(Post.objects.get(title=title))
                continue

            author = users[i % len(users)]
            category = categories[i % len(categories)]
            status = "published" if i % 4 != 0 else "draft"

            # تاریخ‌های متنوع در ۶۰ روز گذشته
            days_ago = random.randint(1, 60)
            pub_date = now - timedelta(days=days_ago)

            content = CONTENT_TEMPLATE.format(
                intro=f"در این مقاله می‌خواهیم درباره «{title}» صحبت کنیم."
            )

            post = Post.objects.create(
                title=title,
                author=author,
                category=category,
                summary=random.choice(SUMMARIES),
                content=content,
                status=status,
                published_at=pub_date if status == "published" else None,
                views=random.randint(10, 500),
            )
            posts.append(post)
            self.stdout.write(f"  ✓ مقاله: {post.title[:50]}")

        return posts

    # ----------------------------------------------------------
    def _create_comments(self, posts, users):
        if not posts or not users:
            return

        count = 0
        for post in posts:
            if post.status != "published":
                continue
            # ۰ تا ۴ نظر برای هر مقاله
            n = random.randint(0, 4)
            for _ in range(n):
                author = random.choice(users)
                body = random.choice(COMMENTS)
                c = Comment.objects.create(
                    post=post,
                    author=author,
                    body=body,
                    is_approved=True,
                )
                # تاریخ نظر بعد از مقاله
                c.created_at = post.published_at + timedelta(
                    hours=random.randint(1, 100)
                )
                c.save(update_fields=["created_at"])
                count += 1

        if count:
            self.stdout.write(f"  ✓ {count} نظر ساخته شد")