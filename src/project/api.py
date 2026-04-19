"""
API views for getting session information and real-time statistics
"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.conf import settings
from abusecheck.models import AbuseReport
from datetime import datetime, timedelta
import json

@login_required
@require_GET
def session_info(request):
    """
    Get current session information and token
    """
    session_key = request.session.session_key
    session_age = request.session.get_expiry_age()  # # Time   
    session_timeout_minutes = settings.SESSION_COOKIE_AGE // 60
    
    # #    
    expiry_time = datetime.now() + timedelta(seconds=session_age)
    
    return JsonResponse({
        'session_key': session_key[:20] + '...' if session_key else None,
        'remaining_seconds': session_age,
        'remaining_minutes': session_age // 60,
        'session_timeout_minutes': session_timeout_minutes,
        'expiry_time': expiry_time.isoformat(),
        'status': 'active'
    })

@login_required
@require_GET
def dashboard_stats(request):
    """
    Get dashboard statistics
    """
    abuse_reports = AbuseReport.objects.filter(archived=False).count()
    recent_reports = list(
        AbuseReport.objects.filter(archived=False)
        .values('ip', 'category', 'reporter', 'email', 'created_at')
        .order_by('-created_at')[:10]
    )
    
    # #    
    for report in recent_reports:
        report['created_at'] = report['created_at'].isoformat()
    
    return JsonResponse({
        'total_reports': abuse_reports,
        'recent_reports': recent_reports,
        'active_services': 3,
        'timestamp': datetime.now().isoformat()
    })

@login_required
@require_GET
def token_status(request):
    """
    Check token and session status
    """
    is_authenticated = request.user.is_authenticated
    session_key = request.session.session_key
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    current_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'Unknown'))
    
    if ',' in current_ip:
        current_ip = current_ip.split(',')[0].strip()
    
    return JsonResponse({
        'authenticated': is_authenticated,
        'username': request.user.username if is_authenticated else None,
        'session_key': session_key[:10] + '...' if session_key else None,
        'user_agent': user_agent[:50],
        'current_ip': current_ip,
        'timestamp': datetime.now().isoformat()
    })
