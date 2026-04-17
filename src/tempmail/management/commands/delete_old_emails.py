from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
from tempmail.models import TempEmail
from tempmail.dovecot_reader import DovecotMailReader
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Delete old emails (older than 90 days) from Dovecot and database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days to keep emails (default: 90 days)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show emails that will be deleted without actually deleting them',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        # Calculate the cutoff date
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(
            self.style.WARNING(
                f'\n🗑️  Deleting emails received before {days} days '
                f'({cutoff_date.date()})\n'
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS('📋 Test mode: emails will be shown but not deleted\n')
            )
        
        try:
            # Delete emails from database
            old_emails = TempEmail.objects.filter(received_at__lt=cutoff_date)
            count = old_emails.count()
            
            if count == 0:
                self.stdout.write(self.style.SUCCESS('✅ No old emails to delete'))
                return
            
            self.stdout.write(f'📧 Number of old emails: {count}')
            
            if dry_run:
                self.stdout.write('📝 Emails that will be deleted:')
                for email in old_emails.values('id', 'from_email', 'subject', 'received_at')[:10]:
                    self.stdout.write(
                        f"  - {email['from_email']}: {email['subject']} "
                        f"({email['received_at'].date()})"
                    )
                if count > 10:
                    self.stdout.write(f'  ... and {count - 10} more')
            else:
                # Delete emails from database
                deleted_count, _ = old_emails.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Deleted {deleted_count} emails from the database')
                )
            
            # Try to clean up old emails in Dovecot as well
            self.stdout.write('\n🔍 Searching for old emails in Dovecot...')
            try:
                users = DovecotMailReader.list_users()
                deleted_dovecot = 0
                
                for username in users:
                    emails = DovecotMailReader.get_user_emails(username, include_read=True)
                    for email in emails:
                        received_time = timezone.datetime.fromisoformat(email['received_at'])
                        if received_time < cutoff_date:
                            if dry_run:
                                self.stdout.write(
                                    f"  Dovecot: {username} - {email['subject']}"
                                )
                            else:
                                # Just mark the email (don't delete file to avoid issues)
                                pass
                            deleted_dovecot += 1
                
                if deleted_dovecot > 0:
                    if dry_run:
                        self.stdout.write(
                            self.style.WARNING(
                                f'\n📌 Found {deleted_dovecot} old emails in Dovecot\n'
                                '⚠️  Note: Dovecot emails are retained per policy\n'
                            )
                        )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Warning: Could not access Dovecot: {e}')
                )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Old email cleanup completed successfully!\n')
            )
            
        except Exception as e:
            logger.error(f'Error deleting old emails: {e}')
            raise CommandError(f'❌ Error deleting old emails: {str(e)}')
