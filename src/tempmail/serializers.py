from rest_framework import serializers
from .models import TempMailDomain, TempInbox, TempEmail, TempEmailAttachment, APIKey, UsageStats


class TempEmailAttachmentSerializer(serializers.ModelSerializer):
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = TempEmailAttachment
        fields = ['id', 'filename', 'content_type', 'file_size']
    
    def get_file_size(self, obj):
        return obj.size_bytes


class TempEmailSerializer(serializers.ModelSerializer):
    attachments = TempEmailAttachmentSerializer(source='attachments', many=True, read_only=True)
    inbox_email = serializers.CharField(source='inbox.email', read_only=True)
    
    class Meta:
        model = TempEmail
        fields = ['id', 'inbox', 'inbox_email', 'from_email', 'subject', 'body_text', 
                  'message_id', 'is_read', 'received_at', 'attachments']
        read_only_fields = ['id', 'inbox', 'message_id', 'received_at']


class TempInboxSerializer(serializers.ModelSerializer):
    email_count = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = TempInbox
        fields = ['id', 'email', 'domain', 'ttl', 'access_token', 'created_at', 
                  'expires_at', 'time_remaining', 'is_expired', 'email_count']
        read_only_fields = ['id', 'access_token', 'created_at', 'expires_at', 'is_expired']
    
    def get_email_count(self, obj):
        return obj.email_count
    
    def get_time_remaining(self, obj):
        from django.utils import timezone
        if obj.is_expired:
            return 0
        remaining = (obj.expires_at - timezone.now()).total_seconds()
        return max(0, int(remaining))


class TempMailDomainSerializer(serializers.ModelSerializer):
    inbox_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TempMailDomain
        fields = ['id', 'name', 'is_active', 'created_at', 'inbox_count']
        read_only_fields = ['id', 'created_at']
    
    def get_inbox_count(self, obj):
        return obj.tempinbox_set.count()


class APIKeySerializer(serializers.ModelSerializer):
    key_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = APIKey
        fields = ['id', 'name', 'key', 'key_preview', 'is_active', 'created_at']
        read_only_fields = ['id', 'key', 'created_at', 'key_preview']
    
    def get_key_preview(self, obj):
        return obj.key[:12] + '...' + obj.key[-4:]


class UsageStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageStats
        fields = ['user', 'total_inboxes_created', 'total_emails_received', 'total_api_calls', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


# Dovecot Direct Mail Serializers
class DovecotEmailSerializer(serializers.Serializer):
    """Serializer for emails read directly from Dovecot Maildir"""
    filename = serializers.CharField(read_only=True)
    subject = serializers.CharField(read_only=True)
    from_email = serializers.CharField(source='from', read_only=True)
    to_email = serializers.CharField(source='to', read_only=True)
    body_text = serializers.CharField(read_only=True)
    body_html = serializers.CharField(read_only=True)
    message_id = serializers.CharField(read_only=True)
    received_at = serializers.DateTimeField(read_only=True)
    size_bytes = serializers.IntegerField(read_only=True)
    is_new = serializers.BooleanField(read_only=True)
    
    def create(self, validated_data):
        raise NotImplementedError("Dovecot emails are read-only")
    
    def update(self, instance, validated_data):
        raise NotImplementedError("Dovecot emails are read-only")


class DovecotMailboxSerializer(serializers.Serializer):
    """Serializer for user mailbox information"""
    username = serializers.CharField(read_only=True)
    email = serializers.SerializerMethodField()
    total_emails = serializers.IntegerField(read_only=True)
    unread_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    def get_email(self, obj):
        return f"{obj.get('username')}@geniusgsm.com"
