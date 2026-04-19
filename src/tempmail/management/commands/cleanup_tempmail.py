from django.core.management.base import BaseCommand
from django.utils import timezone
from tempmail.models import TempInbox, TempEmail


class Command(BaseCommand):
    help = 'تنظيف صناديق البريد والرسائل المنتهية الصلاحية'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='فرض الDelete بدون تأكيد',
        )

    def handle(self, *args, **options):
        # # Search    
        expired_inboxes = TempInbox.objects.filter(
            expires_at__lt=timezone.now()
        )
        
        count = expired_inboxes.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('لا توجد صناديق منتهية الصلاحية'))
            return
        
        self.stdout.write(
            self.style.WARNING(f'تم العثور على {count} صناديق منتهية الصلاحية')
        )
        
        if options['force']:
            expired_inboxes.delete()
            self.stdout.write(
                self.style.SUCCESS(f'تم Delete {count} صندوق بريد')
            )
        else:
            self.stdout.write(
                'استخدم --force لتأكيد الDelete 🗑️'
            )
