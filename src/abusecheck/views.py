from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods
import os

from .models import AbuseReport

from .local_lookup import whois_local, dns_local
import ipaddress


@require_GET
def abuse_info(request, ip: str):
    """Return local abuse reports and optional external providers for the given IP as JSON."""
    local = list(AbuseReport.objects.filter(ip=ip, archived=False).values('id', 'ip', 'reporter', 'email', 'category', 'description', 'source', 'created_at'))
    # Use local lookups instead of external APIs
    from .local_lookup import rdap_local, geoip_local

    external = {}
    try:
        rdap = rdap_local(ip)
        external['rdap'] = rdap
    except Exception as e:
        external['rdap'] = {'error': str(e)}
    try:
        geo = geoip_local(ip)
        external['geoip'] = geo
    except Exception as e:
        external['geoip'] = {'error': str(e)}

    return JsonResponse({'local': local, 'external': external}, safe=False)


@require_http_methods(['GET'])
def abuse_lookup_page(request):
    """Render a page to lookup abuse reports (submission disabled in UI)."""
    ip = request.GET.get('ip', '').strip() or None
    reports = []
    abuse_external = None
    shodan = None
    domain_whois = None
    domain_dns = None
    is_domain = False
    form = None

    if ip:
        # detect whether input is IP or domain
        try:
            ipaddress.ip_address(ip)
            is_domain = False
        except Exception:
            is_domain = True

        if is_domain:
            domain_whois = whois_local(ip)
            try:
                domain_dns = dns_local(ip)
            except Exception:
                domain_dns = {'error': 'dns_lookup_failed'}
        else:
            reports = AbuseReport.objects.filter(ip=ip, archived=False).order_by('-created_at')
            try:
                abuse_external = None
                # fetch local rdap/geo via local_lookup in abuse_info API; keep page light here
            except Exception:
                abuse_external = {'error': 'external lookup failed'}

    return render(request, 'abusecheck/lookup.html', {
        'query_ip': ip or '',
        'reports': reports,
        'abuse': abuse_external,
        'shodan': shodan,
        'form': form,
        'is_domain': is_domain,
        'domain_whois': domain_whois,
        'domain_dns': domain_dns,
    })
