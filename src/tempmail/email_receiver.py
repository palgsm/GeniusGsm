"""
Email Receiver Module for TempMail
Handles incoming emails and stores them in the database
"""

from django.utils import timezone
from django.core.mail import message
from .models import TempInbox, TempEmail, TempEmailAttachment
import uuid
import logging

logger = logging.getLogger(__name__)


def process_incoming_email(email_to, from_address, subject, body_text, body_html=None, attachments=None):
    """
    Process incoming email and store it in database
    
    Args:
        email_to: Recipient email address (temp email)
        from_address: Sender email address
        subject: Email subject
        body_text: Plain text body
        body_html: HTML body (optional)
        attachments: List of attachments (optional)
    
    Returns:
        TempEmail instance or None
    """
    try:
        # Extract inbox from email_to
        if '@' not in email_to:
            logger.error(f"Invalid email format: {email_to}")
            return None
        
        inbox_email, domain = email_to.split('@', 1)
        
        # Find the inbox
        try:
            inbox = TempInbox.objects.get(email=email_to)
        except TempInbox.DoesNotExist:
            logger.warning(f"Inbox not found for email: {email_to}")
            return None
        
        # Check if inbox is expired
        if inbox.is_expired or inbox.expires_at < timezone.now():
            logger.warning(f"Inbox expired: {email_to}")
            inbox.is_expired = True
            inbox.save()
            return None
        
        # Generate message ID
        message_id = str(uuid.uuid4())
        
        # Create email record
        temp_email = TempEmail.objects.create(
            inbox=inbox,
            from_email=from_address,
            from_name=extract_name_from_email(from_address),
            subject=subject,
            body_text=body_text,
            body_html=body_html or '',
            message_id=message_id,
            is_read=False,
            size_bytes=len(body_text) + (len(body_html) if body_html else 0)
        )
        
        # Update inbox stats
        inbox.email_count += 1
        inbox.last_email_at = timezone.now()
        inbox.save()
        
        # Handle attachments
        if attachments:
            for attachment in attachments:
                TempEmailAttachment.objects.create(
                    email=temp_email,
                    filename=attachment.get('filename', 'attachment'),
                    content_type=attachment.get('content_type', 'application/octet-stream'),
                    size_bytes=len(attachment.get('data', b'')),
                    data=attachment.get('data', b'')
                )
        
        logger.info(f"Email stored successfully: {message_id} -> {email_to}")
        return temp_email
        
    except Exception as e:
        logger.error(f"Error processing email: {str(e)}")
        return None


def extract_name_from_email(email_address):
    """
    Extract name from email address
    Example: "John Doe <john@example.com>" -> "John Doe"
    """
    if '<' in email_address:
        return email_address.split('<')[0].strip()
    elif '@' in email_address:
        return email_address.split('@')[0]
    return email_address


def mark_inbox_as_expired(inbox_id):
    """Mark inbox as expired"""
    try:
        inbox = TempInbox.objects.get(id=inbox_id)
        inbox.is_expired = True
        inbox.save()
        logger.info(f"Inbox marked as expired: {inbox.email}")
    except TempInbox.DoesNotExist:
        logger.warning(f"Inbox not found: {inbox_id}")


def cleanup_expired_inboxes():
    """Clean up expired inboxes"""
    now = timezone.now()
    expired_inboxes = TempInbox.objects.filter(expires_at__lt=now, is_expired=False)
    count = expired_inboxes.update(is_expired=True)
    logger.info(f"Cleaned up {count} expired inboxes")
    return count
