from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import TempMailDomain, TempInbox, TempEmail, TempEmailAttachment, APIKey, UsageStats


@admin.register(TempMailDomain)
class TempMailDomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'inbox_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)
    
    def inbox_count(self, obj):
        count = obj.tempinbox_set.count()
        return format_html(
            '<span style="background-color: #00d4ff; color: #0a0e27; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            count
        )
    inbox_count.short_description = 'Inbox Count'


@admin.register(TempInbox)
class TempInboxAdmin(admin.ModelAdmin):
    list_display = ('email', 'domain', 'ttl', 'status_badge', 'email_count', 'created_at')
    list_filter = ('domain', 'ttl', 'is_expired', 'created_at')
    search_fields = ('email', 'id')
    readonly_fields = ('id', 'access_token', 'created_at', 'expires_at', 'message_count')
    
    fieldsets = (
        ('Email Information', {
            'fields': ('id', 'email', 'domain', 'ttl', 'user')
        }),
        ('Security', {
            'fields': ('access_token',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at', 'message_count')
        }),
    )
    
    def status_badge(self, obj):
        if not obj.is_expired:
            color = '#00ff88'
            text = 'Active'
        else:
            color = '#ff4444'
            text = 'Expired'
        return format_html(
            '<span style="background-color: {}; color: #0a0e27; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, text
        )
    status_badge.short_description = 'Status'
    
    def message_count(self, obj):
        return format_html(
            '<span style="background-color: #0096ff; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            obj.email_count
        )
    message_count.short_description = 'Message Count'


@admin.register(TempEmail)
class TempEmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'inbox_email', 'from_email_display', 'read_status', 'received_at')
    list_filter = ('inbox', 'is_read', 'received_at')
    search_fields = ('subject', 'from_email', 'body_text')
    readonly_fields = ('id', 'inbox', 'message_id', 'received_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'inbox', 'message_id')
        }),
        ('Details', {
            'fields': ('from_name', 'from_email', 'subject', 'body_text', 'body_html')
        }),
        ('Status', {
            'fields': ('is_read', 'is_spam', 'received_at')
        }),
    )
    
    def inbox_email(self, obj):
        return obj.inbox.email
    inbox_email.short_description = 'Email'
    
    def from_email_display(self, obj):
        return obj.from_email
    from_email_display.short_description = 'From'
    
    def read_status(self, obj):
        if obj.is_read:
            color = '#00ff88'
            text = 'Read'
        else:
            color = '#ff9944'
            text = 'Unread'
        return format_html(
            '<span style="background-color: {}; color: #0a0e27; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, text
        )
    read_status.short_description = 'Read Status'


@admin.register(TempEmailAttachment)
class TempEmailAttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'content_type', 'email_subject', 'file_size')
    list_filter = ('content_type', 'email__received_at')
    search_fields = ('filename', 'email__subject')
    readonly_fields = ('email', 'filename', 'content_type', 'id')
    
    def email_subject(self, obj):
        return obj.email.subject[:50]
    email_subject.short_description = 'Subject'
    
    def file_size(self, obj):
        return f"{obj.size_bytes / 1024:.2f} KB"
    file_size.short_description = 'File Size'


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_preview', 'user', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'key', 'user__username')
    readonly_fields = ('key', 'created_at', 'id')
    
    def key_preview(self, obj):
        preview = obj.key[:12] + '...' + obj.key[-4:]
        color = '#00ff88' if obj.is_active else '#999'
        return format_html(
            '<code style="background-color: {}; padding: 3px 6px; border-radius: 3px; font-family: monospace; color: #0a0e27;">{}</code>',
            color, preview
        )
    key_preview.short_description = 'Key'


@admin.register(UsageStats)
class UsageStatsAdmin(admin.ModelAdmin):
    list_display = ('user', 'inboxes_count', 'emails_count', 'total_api_calls', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user__username',)
    readonly_fields = ('user', 'created_at', 'updated_at')
    
    def inboxes_count(self, obj):
        return format_html(
            '<span style="background-color: #00d4ff; color: white;">{}</span>',
            obj.total_inboxes_created
        )
    inboxes_count.short_description = 'Inboxes'
    
    def emails_count(self, obj):
        return format_html(
            '<span style="background-color: #00ff88; color: #0a0e27;">{}</span>',
            obj.total_emails_received
        )
    emails_count.short_description = 'Emails'
    
    def has_add_permission(self, request):
        return False
