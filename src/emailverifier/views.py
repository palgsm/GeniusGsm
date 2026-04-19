import dns.resolver
import re
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import EmailCheck
from .forms import EmailCheckForm

TEMP_MAIL_DOMAINS = ['tempmail.com', '10minutemail.com', 'guerrillamail.com', 'maildrop.cc']

def verify_email(email):
    try:
        _, domain = email.split('@')
        
        # Check if temp mail
        is_temp = any(domain.lower() == tmp for tmp in TEMP_MAIL_DOMAINS)
        if is_temp:
            return {'valid': False, 'reason': 'Temporary email service'}
        
        # Check MX records
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            return {'valid': True, 'reason': 'Valid'}
        except:
            return {'valid': False, 'reason': 'No MX records found'}
    except:
        return {'valid': False, 'reason': 'Invalid email format'}

@require_http_methods(["GET", "POST"])
def emailverifier_index(request):
    result = None
    form = EmailCheckForm()
    history = EmailCheck.objects.all()[:10]
    
    if request.method == 'POST':
        form = EmailCheckForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            result = verify_email(email)
            EmailCheck.objects.create(email=email, is_valid=result['valid'])
    
    return render(request, 'emailverifier/index.html', {'form': form, 'result': result, 'history': history})

@require_http_methods(["POST"])
def api_verify_email(request):
    try:
        email = request.POST.get('email')
        result = verify_email(email)
        EmailCheck.objects.create(email=email, is_valid=result['valid'])
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
