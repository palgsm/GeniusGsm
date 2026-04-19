import dns.resolver
import ssl
import socket
from datetime import datetime
import whois
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import DomainCheck
from .forms import DomainCheckForm


def check_domain_reputation(domain):
    """Check domain reputation"""
    try:
        # Basic WHOIS check
        try:
            w = whois.whois(domain)
            whois_data = {
                'registrar': str(w.registrar) if w.registrar else 'Unknown',
                'creation_date': str(w.creation_date) if w.creation_date else 'Unknown',
                'expiration_date': str(w.expiration_date) if w.expiration_date else 'Unknown',
                'name_servers': w.name_servers if w.name_servers else [],
            }
        except:
            whois_data = None
        
        # DNS resolution check
        try:
            ips = dns.resolver.resolve(domain, 'A')
            dns_records = [str(rdata) for rdata in ips]
        except:
            dns_records = []
        
        # SSL certificate check
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    ssl_info = {
                        'subject': cert.get('subject', 'N/A'),
                        'issuer': cert.get('issuer', 'N/A'),
                    }
        except:
            ssl_info = None
        
        return {
            'success': True,
            'whois': whois_data,
            'dns': dns_records,
            'ssl': ssl_info,
            'status': 'valid' if whois_data or dns_records else 'invalid'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'status': 'error'
        }


@require_http_methods(["GET", "POST"])
def domainchecker_index(request):
    """Domain Checker main view"""
    result = None
    form = DomainCheckForm()
    history = DomainCheck.objects.all()[:10]
    
    if request.method == 'POST':
        form = DomainCheckForm(request.POST)
        if form.is_valid():
            domain = form.cleaned_data['domain']
            result = check_domain_reputation(domain)
            
            DomainCheck.objects.create(
                domain=domain,
                check_status=result.get('status', 'error'),
                whois_data=result.get('whois')
            )
    
    context = {
        'form': form,
        'result': result,
        'history': history,
        'page_title': 'فاحص سمعة الدومين',
        'page_description': 'تحقق من معلومات الدومين والـ WHOIS و SSL والـ DNS',
    }
    
    return render(request, 'domainchecker/index.html', context)


@require_http_methods(["POST"])
def api_check_domain(request):
    """API endpoint"""
    try:
        domain = request.POST.get('domain')
        if not domain:
            return JsonResponse({'error': 'Missing domain'}, status=400)
        
        result = check_domain_reputation(domain)
        
        DomainCheck.objects.create(
            domain=domain,
            check_status=result.get('status', 'error'),
            whois_data=result.get('whois')
        )
        
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
