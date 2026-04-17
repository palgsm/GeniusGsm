#!/usr/bin/env python3
"""
Direct mail filter script that processes emails immediately when received by Dovecot
This script is called by Dovecot's LMTP for each incoming email
Saves emails directly to database on receipt (no waiting for cron job)
"""

import sys
import os
import json
import logging
from email import message_from_string
from email.utils import parsedate_to_datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()

from tempmail.models import TempInbox, TempEmail, TempEmailAttachment
from django.utils import timezone
import uuid

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/tempmail-filter.log'),
        logging.StreamHandler()
    ]
)


def extract_email_parts(email_message):
    """Extract email headers and body from email message"""
    try:
        # Extract standard headers
        from_addr = email_message.get('From', 'unknown@example.com')
        subject = email_message.get('Subject', '(No Subject)')
        message_id = email_message.get('Message-ID', str(uuid.uuid4()))
        
        # Extract body
        body_text = ""
        body_html = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                
                if content_type == 'text/plain':
                    body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                elif content_type == 'text/html':
                    body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            body_text = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        return {
            'from': from_addr,
            'subject': subject,
            'message_id': message_id,
            'body_text': body_text,
            'body_html': body_html
        }
    except Exception as e:
        logger.error(f"Error extracting email parts: {e}")
        return None


def save_email_to_db(email_to, from_address, subject, body_text, body_html="", message_id=None):
    """Save email directly to database"""
    try:
        # Find inbox
        try:
            inbox = TempInbox.objects.get(email=email_to)
        except TempInbox.DoesNotExist:
            logger.warning(f"❌ Inbox not found: {email_to}")
            return False
        
        # Check if inbox is expired
        if inbox.is_expired or inbox.expires_at < timezone.now():
            logger.warning(f"❌ Inbox expired: {email_to}")
            return False
        
        # Check if email already exists
        if message_id and TempEmail.objects.filter(message_id=message_id).exists():
            logger.info(f"⏭️  Email already saved: {message_id}")
            return False
        
        # Create email record
        temp_email = TempEmail.objects.create(
            inbox=inbox,
            from_email=from_address,
            from_name=from_address.split('<')[0].strip() if '<' in from_address else from_address.split('@')[0],
            subject=subject[:500],
            body_text=body_text[:5000],
            body_html=body_html[:10000],
            message_id=message_id or str(uuid.uuid4()),
            is_read=False,
            size_bytes=len(body_text) + len(body_html)
        )
        
        # Update inbox stats
        inbox.email_count += 1
        inbox.last_email_at = timezone.now()
        inbox.save()
        
        logger.info(f"✅ Email saved immediately: {temp_email.id} -> {email_to}")
        logger.info(f"   From: {from_address}")
        logger.info(f"   Subject: {subject[:50]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error saving email: {e}")
        return False


def main():
    """
    Main filter function - Read email from stdin (Dovecot LMTP format)
    
    Dovecot passes email as:
    - First line: recipient email address
    - Rest: Full email message
    """
    try:
        # Read email from stdin
        email_text = sys.stdin.read()
        
        if not email_text:
            logger.error("No email data received")
            sys.exit(1)
        
        # Parse email message
        email_message = message_from_string(email_text)
        
        # Get email details
        email_parts = extract_email_parts(email_message)
        if not email_parts:
            logger.error("Failed to extract email parts")
            sys.exit(1)
        
        # Get recipient from Dovecot environment variable or header
        email_to = os.environ.get('RECIPIENT', os.environ.get('MAIL_TO', ''))
        
        if not email_to:
            # Try to extract from message headers
            delivered_to = email_message.get('Delivered-To', '')
            if delivered_to:
                email_to = delivered_to
        
        if not email_to:
            logger.error("Could not determine recipient email")
            sys.exit(1)
        
        # Save to database
        success = save_email_to_db(
            email_to=email_to,
            from_address=email_parts['from'],
            subject=email_parts['subject'],
            body_text=email_parts['body_text'],
            body_html=email_parts['body_html'],
            message_id=email_parts['message_id']
        )
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Fatal error in mail filter: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
