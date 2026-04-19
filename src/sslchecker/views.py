import ssl
import socket
from datetime import datetime
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .models import SSLCheck
from .forms import SSLCheckForm

def check_ssl(domain):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                return {
                    'valid': True,
                    'subject': str(cert.get('subject', 'N/A')),
                    'issuer': str(cert.get('issuer', 'N/A')),
                }
    except Exception as e:
        return {'valid': False, 'error': str(e)}

@require_http_methods(["GET", "POST"])
def sslchecker_index(request):
    result = None
    form = SSLCheckForm()
    
    if request.method == 'POST':
        form = SSLCheckForm(request.POST)
        if form.is_valid():
            domain = form.cleaned_data['domain']
            result = check_ssl(domain)
            SSLCheck.objects.create(domain=domain, is_valid=result['valid'])
    
    return render(request, 'sslchecker/index.html', {'form': form, 'result': result})
