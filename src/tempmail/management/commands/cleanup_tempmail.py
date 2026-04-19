from django.core.management.base import BaseCommand
from django.utils import timezone
from tempmail.models import TempInbox, TempEmail


class Command(BaseCommand):
    help = 'Clean up expired mailboxes and emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force delete without confirmation',
        )

    def handle(self, *args, **options):
        # # Search    
        expired_inboxes = TempInbox.objects.filter(
            expires_at__lt=timezone.now()
        )
        
        count = expired_inboxes.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No expired mailboxes found'))
            return
        
        self.stdout.write(
            self.style.WARNING(f'Found {count} expired mailboxes')
        )
        
        if options['force']:
            expired_inboxes.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {count} mailboxes')
            )
        else:
            self.stdout.write(
                'Use --force to confirm deletion'
            )
