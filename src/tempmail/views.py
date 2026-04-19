from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import random
import string
import logging

from .models import TempMailDomain, TempInbox, TempEmail, TempEmailAttachment, APIKey, UsageStats
from .serializers import (
    TempMailDomainSerializer, TempInboxSerializer, TempEmailSerializer,
    TempEmailAttachmentSerializer, APIKeySerializer, UsageStatsSerializer,
    DovecotEmailSerializer, DovecotMailboxSerializer
)
from .email_receiver import process_incoming_email, cleanup_expired_inboxes
from .dovecot_reader import DovecotMailReader

logger = logging.getLogger(__name__)


# # View   TempMail Landing Page
def tempmail_home(request):
    domains = TempMailDomain.objects.filter(is_active=True)
    context = {
        'domains': domains,
        'total_inboxes': TempInbox.objects.filter(is_expired=False).count(),
    }
    return render(request, 'tempmail/home.html', context)


# # View Show Dovecot Inbox
def dovecot_inbox(request):
    """View for Dovecot direct mail inbox"""
    return render(request, 'tempmail/dovecot_inbox.html')


# # View Show  
def inbox_view(request, inbox_id):
    inbox = get_object_or_404(TempInbox, id=inbox_id)
    emails = inbox.tempemail_set.all().order_by('-received_at')
    context = {
        'inbox': inbox,
        'emails': emails,
    }
    return render(request, 'tempmail/inbox.html', context)


# # View Show  API
def api_docs(request):
    """View for API Documentation"""
    return render(request, 'tempmail/api-docs.html')


# API ViewSets
class TempMailDomainViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TempMailDomain.objects.filter(is_active=True)
    serializer_class = TempMailDomainSerializer
    permission_classes = [AllowAny]


class TempInboxViewSet(viewsets.ModelViewSet):
    queryset = TempInbox.objects.all()
    serializer_class = TempInboxSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def create_inbox(self, request):
        """Create new inbox"""
        domain_id = request.data.get('domain_id')
        ttl = request.data.get('ttl', 3600)  # Default: 1 hour (in seconds)
        
        if not domain_id:
            return Response(
                {'error': 'domain_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # #  TTL  integer   string
        if isinstance(ttl, str):
            try:
                ttl = int(ttl)
            except (ValueError, TypeError):
                ttl = 3600  # Default fallback
        
        try:
            domain = TempMailDomain.objects.get(id=domain_id, is_active=True)
        except TempMailDomain.DoesNotExist:
            return Response(
                {'error': 'Domain not found or inactive'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # # Create  
        random_prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        email = f"{random_prefix}@{domain.name}"
        
        # # Verify     
        while TempInbox.objects.filter(email=email).exists():
            random_prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            email = f"{random_prefix}@{domain.name}"
        
        inbox = TempInbox.objects.create(
            email=email,
            domain=domain,
            ttl=ttl
        )
        
        # # Add    
        if request.user.is_authenticated:
            stats, _ = UsageStats.objects.get_or_create(user=request.user)
            stats.total_inboxes += 1
            stats.save()
        
        serializer = self.get_serializer(inbox)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def emails(self, request, id=None):
        """Get all emails in the inbox"""
        inbox = self.get_object()
        emails = inbox.tempemail_set.all().order_by('-received_at')
        serializer = TempEmailSerializer(emails, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def mark_as_read(self, request, id=None):
        """Mark all emails in inbox as read"""
        inbox = self.get_object()
        inbox.tempemail_set.update(read=True)
        return Response({'message': 'All emails marked as read'})
    
    @action(detail=True, methods=['delete'], permission_classes=[AllowAny])
    def delete_inbox(self, request, id=None):
        """Delete the inbox"""
        inbox = self.get_object()
        email = inbox.email
        inbox.delete()
        return Response({'message': f'Inbox {email} deleted successfully'})


class TempEmailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TempEmail.objects.all()
    serializer_class = TempEmailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def mark_as_read(self, request, id=None):
        """Mark email as read"""
        email = self.get_object()
        email.read = True
        email.save()
        serializer = self.get_serializer(email)
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'], permission_classes=[AllowAny])
    def delete_email(self, request, id=None):
        """Delete email"""
        email = self.get_object()
        subject = email.subject
        email.delete()
        return Response({'message': f'Email deleted: {subject}'})


class TempEmailAttachmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TempEmailAttachment.objects.all()
    serializer_class = TempEmailAttachmentSerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def download(self, request, pk=None):
        """Download attachment"""""
        attachment = self.get_object()
        if attachment.data:
            response = Response(
                attachment.data.read(),
                content_type=attachment.content_type
            )
            response['Content-Disposition'] = f'attachment; filename="{attachment.filename}"'
            return response
        return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)


class APIKeyViewSet(viewsets.ModelViewSet):
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_key(self, request):
        """Create new API key"""
        name = request.data.get('name', 'API Key')
        
        api_key = APIKey.objects.create(
            user=request.user,
            name=name
        )
        
        stats, _ = UsageStats.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(api_key)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate API key"""
        api_key = self.get_object()
        if api_key.user != request.user:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        api_key.is_active = False
        api_key.save()
        return Response({'message': 'API key deactivated'})


class UsageStatsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UsageStatsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UsageStats.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_stats(self, request):
        """My personal statistics"""
        stats, created = UsageStats.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(stats)
        return Response(serializer.data)


# ===== Email Webhook Endpoints =====

@api_view(['POST'])
def receive_email_webhook(request):
    """
    Webhook endpoint to receive incoming emails
    
    Expected JSON payload:
    {
        "to": "user@tempmail.com",
        "from": "sender@example.com",
        "subject": "Email Subject",
        "text": "Plain text body",
        "html": "<html>HTML body</html>",
        "attachments": [
            {
                "filename": "file.pdf",
                "content_type": "application/pdf",
                "data": "base64_encoded_data"
            }
        ]
    }
    """
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['to', 'from', 'subject', 'text']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Process the email
        temp_email = process_incoming_email(
            email_to=data.get('to'),
            from_address=data.get('from'),
            subject=data.get('subject'),
            body_text=data.get('text', ''),
            body_html=data.get('html'),
            attachments=data.get('attachments', [])
        )
        
        if temp_email:
            logger.info(f"Email received successfully: {temp_email.message_id}")
            return Response(
                {
                    'success': True,
                    'message_id': str(temp_email.message_id),
                    'email_id': str(temp_email.id)
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to process email'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        logger.error(f"Error in email webhook: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def cleanup_expired_inboxes_endpoint(request):
    """
    Admin endpoint to cleanup expired inboxes
    Requires API key authentication
    """
    # Check for API key
    api_key = request.query_params.get('api_key')
    if not api_key:
        return Response(
            {'error': 'API key required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Verify API key
    if not APIKey.objects.filter(key=api_key, is_active=True).exists():
        return Response(
            {'error': 'Invalid API key'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Run cleanup
    count = cleanup_expired_inboxes()
    return Response(
        {
            'success': True,
            'cleaned_inboxes': count
        }
    )


# Dovecot Direct Mail Endpoints
@api_view(['GET'])
def list_dovecot_users(request):
    """List all users in Dovecot mailbox"""
    try:
        users = DovecotMailReader.list_users()
        return Response({
            'success': True,
            'users': users,
            'total_users': len(users)
        })
    except Exception as e:
        logger.error(f"Error listing Dovecot users: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_dovecot_mailbox(request, username):
    """Get mailbox information and emails from Dovecot (real-time)"""
    try:
        # Construct the full email address
        email = f'{username}@geniusgsm.com'
        
        # Get inbox from database
        try:
            inbox = TempInbox.objects.get(email=email)
        except TempInbox.DoesNotExist:
            return Response(
                {'error': f'Inbox not found for {email}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get emails from Dovecot (real-time)
        emails_from_dovecot = DovecotMailReader.get_user_emails(username, include_read=True)
        unread_count = DovecotMailReader.get_unread_count(username)
        
        # Format emails for response
        formatted_emails = []
        for email_obj in emails_from_dovecot:
            formatted_email = {
                'id': email_obj.get('id', ''),
                'filename': email_obj.get('filename', ''),
                'from': email_obj.get('from', ''),
                'from_email': email_obj.get('from_email', ''),
                'from_name': email_obj.get('from_name', ''),
                'to': email,
                'subject': email_obj.get('subject', '(No Subject)'),
                'date': email_obj.get('received_at', '').isoformat() if hasattr(email_obj.get('received_at', ''), 'isoformat') else str(email_obj.get('received_at', '')),
                'received_at': email_obj.get('received_at', '').isoformat() if hasattr(email_obj.get('received_at', ''), 'isoformat') else str(email_obj.get('received_at', '')),
                'size': email_obj.get('size', 0),
                'body_text': email_obj.get('body', ''),
                'body_html': email_obj.get('body_html', ''),
                'is_new': email_obj.get('is_new', False),
                'is_read': email_obj.get('is_read', False),
                'headers': email_obj.get('headers', {}),
                'attachments': email_obj.get('attachments', [])
            }
            formatted_emails.append(formatted_email)
        
        mailbox_data = {
            'username': username,
            'email': email,
            'total_emails': len(emails_from_dovecot),
            'unread_count': unread_count,
            'created_at': inbox.created_at.isoformat(),
            'emails': formatted_emails
        }
        
        logger.info(f"Retrieved mailbox {email} with {len(emails_from_dovecot)} emails from Dovecot (real-time)")
        return Response({
            'success': True,
            'mailbox': mailbox_data
        })
    except Exception as e:
        logger.error(f"Error getting mailbox {username}: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_dovecot_email(request, username, filename):
    """Get a specific email from database and mark as read"""
    try:
        # Extract email ID from filename (format: email_{uuid}.eml)
        email_id = filename.replace('email_', '').replace('.eml', '')
        
        try:
            email_obj = TempEmail.objects.get(id=email_id)
        except TempEmail.DoesNotExist:
            return Response(
                {'error': f'Email not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify inbox matches username
        if email_obj.inbox.email != f'{username}@geniusgsm.com':
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get attachments
        attachments = []
        for attachment in email_obj.attachments.all():
            attachments.append({
                'filename': attachment.filename,
                'content_type': attachment.content_type,
                'size': attachment.size_bytes
            })
        
        # Mark as read
        if not email_obj.is_read:
            email_obj.is_read = True
            email_obj.save()
        
        email_data = {
            'id': str(email_obj.id),
            'filename': filename,
            'from': f'{email_obj.from_name} <{email_obj.from_email}>' if email_obj.from_name else email_obj.from_email,
            'from_email': email_obj.from_email,
            'from_name': email_obj.from_name,
            'to': email_obj.inbox.email,
            'subject': email_obj.subject,
            'date': email_obj.received_at.isoformat(),
            'received_at': email_obj.received_at.isoformat(),
            'size': email_obj.size_bytes,
            'body': email_obj.body_text,
            'body_text': email_obj.body_text,
            'body_html': email_obj.body_html,
            'is_read': True,
            'headers': {
                'message_id': email_obj.message_id,
                'in_reply_to': email_obj.in_reply_to or ''
            },
            'attachments': attachments
        }
        
        logger.info(f"Retrieved email {email_id} from database")
        return Response({
            'success': True,
            'email': email_data
        })
    except Exception as e:
        logger.error(f"Error getting email {filename}: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
def delete_dovecot_email(request, username, filename):
    """Delete an email from database"""
    try:
        # Extract email ID from filename
        email_id = filename.replace('email_', '').replace('.eml', '')
        
        try:
            email_obj = TempEmail.objects.get(id=email_id)
        except TempEmail.DoesNotExist:
            return Response(
                {'error': f'Email not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify inbox matches username
        if email_obj.inbox.email != f'{username}@geniusgsm.com':
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Delete email and attachments (cascading delete)
        email_obj.delete()
        
        logger.info(f"Deleted email {email_id} from database")
        return Response({
            'success': True,
            'message': f'Email deleted'
        })
    except Exception as e:
        logger.error(f"Error deleting email {filename}: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# # Create       Data
@api_view(['POST'])
def create_temp_email(request):
    """Create a new temporary email and save to database
    POST /tempmail/api/create-temp-email/
    {
        "email_name": "optional_custom_name"  # optional
    }
    """
    try:
        # Get the first active domain
        domain = TempMailDomain.objects.filter(is_active=True).first()
        if not domain:
            return Response(
                {'error': 'No domains available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get email name from request or generate random one
        email_name = request.data.get('email_name', '').strip()
        if not email_name:
            email_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        
        # Verify that email hasn't been created before
        email = f"{email_name}@{domain.name}"
        max_attempts = 10
        attempts = 0
        while TempInbox.objects.filter(email=email).exists() and attempts < max_attempts:
            email_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
            email = f"{email_name}@{domain.name}"
            attempts += 1
        
        if attempts >= max_attempts:
            return Response(
                {'error': 'Failed to create unique email'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Create the inbox on the database
        # No specific TTL specified - inbox will be retained permanently in DB
        inbox = TempInbox.objects.create(
            email=email,
            domain=domain,
            ttl=86400 * 90  # 90 days (but will never be deleted from DB)
        )
        
        # Create Dovecot mailbox directories
        import os
        from pathlib import Path
        vmail_root = Path("/var/vmail/geniusgsm.com")
        mailbox_path = vmail_root / email_name
        
        try:
            # Create mailbox directory structure
            (mailbox_path / "new").mkdir(parents=True, exist_ok=True)
            (mailbox_path / "cur").mkdir(parents=True, exist_ok=True)
            (mailbox_path / "tmp").mkdir(parents=True, exist_ok=True)
            
            # Set correct permissions (vmail:vmail, 0700)
            os.chmod(mailbox_path, 0o700)
            os.chmod(mailbox_path / "new", 0o700)
            os.chmod(mailbox_path / "cur", 0o700)
            os.chmod(mailbox_path / "tmp", 0o700)
            
            # Change owner to vmail:vmail
            import pwd
            import grp
            vmail_uid = pwd.getpwnam('vmail').pw_uid
            vmail_gid = grp.getgrnam('vmail').gr_gid
            os.chown(mailbox_path, vmail_uid, vmail_gid)
            os.chown(mailbox_path / "new", vmail_uid, vmail_gid)
            os.chown(mailbox_path / "cur", vmail_uid, vmail_gid)
            os.chown(mailbox_path / "tmp", vmail_uid, vmail_gid)
            
            logger.info(f"Created mailbox for {email_name}")
        except Exception as e:
            logger.warning(f"Could not create mailbox directories: {e}")
            # Don't fail the email creation, just log it
        
        return Response({
            'success': True,
            'email': email,
            'inbox_id': str(inbox.id),
            'created_at': inbox.created_at.isoformat()
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"Error creating temp email: {e}")
        return Response(
            {'error': f'Error creating email: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
