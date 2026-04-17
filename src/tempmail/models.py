from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
import random
import string


class TempMailDomain(models.Model):
    """Domain list for temp email generation"""
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Temp Mail Domain"
        verbose_name_plural = "Temp Mail Domains"
    
    def __str__(self):
        return self.name


class TempInbox(models.Model):
    """Temporary inbox model"""
    EXPIRY_CHOICES = [
        (3600, '1 hour'),
        (7200, '2 hours'),
        (14400, '4 hours'),
        (86400, '1 day'),
        (604800, '7 days'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    domain = models.ForeignKey(TempMailDomain, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='temp_inboxes')
    
    # Expiry settings
    ttl = models.IntegerField(choices=EXPIRY_CHOICES, default=3600, help_text="Time to live in seconds")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    is_expired = models.BooleanField(default=False, db_index=True)
    
    # Stats
    email_count = models.IntegerField(default=0)
    last_email_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    description = models.CharField(max_length=255, blank=True, null=True)
    is_favorite = models.BooleanField(default=False)
    access_token = models.CharField(max_length=100, unique=True, editable=False)
    
    class Meta:
        verbose_name = "Temp Inbox"
        verbose_name_plural = "Temp Inboxes"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(seconds=self.ttl)
        if not self.access_token:
            self.access_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        super().save(*args, **kwargs)
    
    @property
    def time_remaining(self):
        """Get remaining time in seconds"""
        if self.is_expired:
            return 0
        remaining = (self.expires_at - timezone.now()).total_seconds()
        return max(0, int(remaining))
    
    @property
    def is_active(self):
        """Check if inbox is still active"""
        return not self.is_expired and self.time_remaining > 0
    
    def mark_expired(self):
        """Mark inbox as expired and delete emails"""
        self.is_expired = True
        self.save()
        self.emails.all().delete()


class TempEmail(models.Model):
    """Temporary email model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inbox = models.ForeignKey(TempInbox, on_delete=models.CASCADE, related_name='emails')
    
    # Email fields
    from_email = models.EmailField()
    from_name = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=500)
    body_text = models.TextField()
    body_html = models.TextField(blank=True, null=True)
    
    # Headers
    message_id = models.CharField(max_length=500, unique=True, editable=False)
    in_reply_to = models.CharField(max_length=500, blank=True, null=True)
    
    # Metadata
    received_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_read = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)
    size_bytes = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Temp Email"
        verbose_name_plural = "Temp Emails"
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['inbox', '-received_at']),
            models.Index(fields=['message_id']),
        ]
    
    def __str__(self):
        return f"{self.subject} -> {self.inbox.email}"
    
    def mark_as_read(self):
        """Mark email as read"""
        self.is_read = True
        self.save()


class TempEmailAttachment(models.Model):
    """Attachments for temp emails"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.ForeignKey(TempEmail, on_delete=models.CASCADE, related_name='attachments')
    
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size_bytes = models.IntegerField()
    data = models.BinaryField()
    
    class Meta:
        verbose_name = "Attachment"
        verbose_name_plural = "Attachments"
    
    def __str__(self):
        return self.filename


class APIKey(models.Model):
    """API Keys for authentication"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tempmail_api_keys')
    
    key = models.CharField(max_length=100, unique=True, editable=False)
    name = models.CharField(max_length=255)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
    
    def __str__(self):
        return f"{self.name} - {self.key[:10]}..."
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = f"sk_{''.join(random.choices(string.ascii_letters + string.digits, k=32))}"
        super().save(*args, **kwargs)


class UsageStats(models.Model):
    """Track usage statistics"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tempmail_stats')
    
    total_inboxes_created = models.IntegerField(default=0)
    total_emails_received = models.IntegerField(default=0)
    total_api_calls = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Usage Stats"
        verbose_name_plural = "Usage Stats"
    
    def __str__(self):
        return f"Stats for {self.user.username}"
