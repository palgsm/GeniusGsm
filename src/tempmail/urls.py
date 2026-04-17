from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'tempmail'

router = DefaultRouter()
router.register(r'domains', views.TempMailDomainViewSet, basename='domain')
router.register(r'inboxes', views.TempInboxViewSet, basename='inbox')
router.register(r'emails', views.TempEmailViewSet, basename='email')
router.register(r'attachments', views.TempEmailAttachmentViewSet, basename='attachment')
router.register(r'api-keys', views.APIKeyViewSet, basename='api-key')
router.register(r'stats', views.UsageStatsViewSet, basename='stats')

urlpatterns = [
    path('', views.tempmail_home, name='home'),
    path('api-docs/', views.api_docs, name='api_docs'),
    path('inbox/<str:inbox_id>/', views.inbox_view, name='inbox_view'),
    path('dovecot/', views.dovecot_inbox, name='dovecot_inbox'),
    path('api/', include(router.urls)),
    
    # Email Webhook Endpoints
    path('api/webhook/email/', views.receive_email_webhook, name='receive_email_webhook'),
    path('api/admin/cleanup/', views.cleanup_expired_inboxes_endpoint, name='cleanup_inboxes'),
    
    # Dovecot Direct Mail Endpoints
    path('api/dovecot/users/', views.list_dovecot_users, name='dovecot_users'),
    path('api/dovecot/mailbox/<str:username>/', views.get_dovecot_mailbox, name='dovecot_mailbox'),
    path('api/dovecot/mailbox/<str:username>/<str:filename>/', views.get_dovecot_email, name='dovecot_email'),
    path('api/dovecot/mailbox/<str:username>/<str:filename>/delete/', views.delete_dovecot_email, name='dovecot_delete_email'),
    
    # Simple TempMail Creation Endpoint
    path('api/create-temp-email/', views.create_temp_email, name='create_temp_email'),
]
