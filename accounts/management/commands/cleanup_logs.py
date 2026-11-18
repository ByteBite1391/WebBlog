from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import ActivityLog


class Command(BaseCommand):
    help = "پاک کردن لاگ‌های قدیمی‌تر از N روز"

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=30,
                            help="نگه‌داشتن لاگ‌های N روز اخیر (پیش‌فرض: 30)")
        parser.add_argument("--dry-run", action="store_true",
                            help="فقط شمارش، بدون حذف")

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=options["days"])
        qs = ActivityLog.objects.filter(created_at__lt=cutoff)
        count = qs.count()
        if options["dry_run"]:
            self.stdout.write(f"🔍 {count} لاگ قدیمی‌تر از {cutoff:%Y-%m-%d} پیدا شد.")
            return
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f"✓ {count} لاگ قدیمی حذف شد."))