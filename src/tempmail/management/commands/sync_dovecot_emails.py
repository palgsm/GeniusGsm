"""
Management command to scan Dovecot mailboxes and save emails to database
Run this periodically to sync emails from Dovecot to Django database
"""

from django.core.management.base import BaseCommand
from tempmail.models import TempInbox, TempEmail
from tempmail.dovecot_reader import DovecotMailReader
import email
import logging
import uuid

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Scan Dovecot mailboxes and save new emails to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--inbox',
            type=str,
            help='Scan specific inbox (email address)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose')
        specific_inbox = options.get('inbox')

        if specific_inbox:
            self._scan_inbox(specific_inbox, verbose)
        else:
            self._scan_all_inboxes(verbose)

    def _scan_all_inboxes(self, verbose):
        """Scan all active inboxes"""
        inboxes = TempInbox.objects.filter(is_expired=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'🔍 Scanning {inboxes.count()} active inboxes...\n')
        )
        
        total_saved = 0
        for inbox in inboxes:
            username = inbox.email.split('@')[0]
            saved = self._sync_inbox(inbox, username, verbose)
            total_saved += saved
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Saved {total_saved} new emails to database')
        )

    def _scan_inbox(self, email_address, verbose):
        """Scan specific inbox"""
        try:
            inbox = TempInbox.objects.get(email=email_address)
            username = email_address.split('@')[0]
            saved = self._sync_inbox(inbox, username, verbose)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Saved {saved} new emails for {email_address}')
            )
        except TempInbox.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Inbox not found: {email_address}')
            )

    def _sync_inbox(self, inbox, username, verbose):
        """Sync emails for a single inbox"""
        try:
            # Get existing message IDs in database
            existing_ids = set(
                TempEmail.objects.filter(inbox=inbox).values_list('message_id', flat=True)
            )
            
            # Get emails from Dovecot
            email_files = DovecotMailReader.get_email_files(username, include_read=True)
            
            saved_count = 0
            for file_path, is_read in email_files:
                try:
                    # Parse email
                    email_data = DovecotMailReader.parse_email(file_path)
                    if not email_data:
                        continue
                    
                    message_id = email_data.get('message_id', '')
                    
                    # Skip if already in database
                    if message_id and message_id in existing_ids:
                        if verbose:
                            self.stdout.write(f'  ⏭️  Skip (already in DB): {message_id}')
                        continue
                    
                    # Parse from_address to extract name and email
                    from_addr = email_data.get('from', '')
                    from_email = from_addr
                    from_name = ''
                    
                    if '<' in from_addr and '>' in from_addr:
                        from_name = from_addr.split('<')[0].strip()
                        from_email = from_addr.split('<')[1].split('>')[0].strip()
                    elif '@' in from_addr:
                        from_email = from_addr
                        from_name = from_addr.split('@')[0]
                    
                    # Create email record in database
                    temp_email = TempEmail.objects.create(
                        inbox=inbox,
                        from_email=from_email,
                        from_name=from_name,
                        subject=email_data.get('subject', '(No Subject)'),
                        body_text=email_data.get('body_text', ''),
                        body_html=email_data.get('body_html', ''),
                        message_id=message_id or str(uuid.uuid4()),
                        is_read=is_read,
                        size_bytes=email_data.get('size_bytes', 0)
                    )
                    
                    # Update inbox stats
                    inbox.email_count = TempEmail.objects.filter(inbox=inbox).count()
                    inbox.last_email_at = temp_email.received_at
                    inbox.save()
                    
                    saved_count += 1
                    if verbose:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✅ Saved: {temp_email.subject[:50]}'
                            )
                        )
                    
                except Exception as e:
                    logger.error(f"Error parsing email {file_path}: {e}")
                    if verbose:
                        self.stdout.write(
                            self.style.ERROR(f'  ❌ Error: {e}')
                        )
            
            if verbose and saved_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'📧 {inbox.email}: Saved {saved_count} emails')
                )
            
            return saved_count
            
        except Exception as e:
            logger.error(f"Error syncing inbox {inbox.email}: {e}")
            self.stdout.write(
                self.style.ERROR(f'❌ Error syncing {inbox.email}: {e}')
            )
            return 0
