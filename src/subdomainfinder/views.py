from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q, Max, Avg, Sum
from django.utils import timezone
import socket
import dns.resolver
import requests
import time
import re
from urllib.parse import urlparse
from .models import SubdomainEntry, SubdomainScanHistory
from .forms import SubdomainFinderForm


# Common subdomains wordlist
COMMON_SUBDOMAINS = [
    'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
    'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'm', 'test', 'mx',
    'blog', 'shop', 'forum', 'admin', 'api', 'app', 'dev', 'staging', 'prod',
    'cdn', 'img', 'static', 'images', 'assets', 'files', 'download', 'uploads',
    'backup', 'old', 'new', 'temp', 'tmp', 'beta', 'demo', 'example', 'test2',
    'mail2', 'mail3', 'server', 'cloud', 'vpn', 'ssl', 'secure', 'support',
    'help', 'docs', 'documentation', 'wiki', 'git', 'github', 'jenkins', 'analytics',
    'gstatic', 'fonts', 'ajax', 'jquery', 'cdn1', ' cdn2', 'cpanel2', 'panel',
    'api2', 'v1', 'v2', 'v3', 'rest', 'rss', 'feed', 'feeds', 'calendar',
    'events', 'photos', 'videos', 'media', 'music', 'audio', 'db', 'database'
]


class SubdomainFinder:
    """Subdomain discovery using multiple methods"""
    
    def __init__(self, domain, timeout=5):
        self.domain = domain
        self.timeout = timeout
        self.results = []
        self.start_time = time.time()
    
    def resolve_dns(self, subdomain_name):
        """Attempt DNS resolution"""
        try:
            full_domain = f"{subdomain_name}.{self.domain}"
            answers = dns.resolver.resolve(full_domain, 'A', lifetime=self.timeout)
            return [str(rdata) for rdata in answers]
        except Exception:
            return None
    
    def check_http_status(self, subdomain_name):
        """Check HTTP/HTTPS status and headers"""
        full_domain = f"{subdomain_name}.{self.domain}"
        result = {
            'subdomain': subdomain_name,
            'ip_address': None,
            'status_code': None,
            'status': 'unknown',
            'server': '',
            'title': '',
            'response_time': 0,
            'certificate_valid': None,
            'certificate_issuer': ''
        }
        
        for protocol in ['https', 'http']:
            url = f"{protocol}://{full_domain}"
            try:
                response = requests.head(
                    url,
                    timeout=min(self.timeout, 3),  # Max 3 seconds for HEAD request
                    allow_redirects=False,  # Do NOT follow redirects to save time
                    verify=False
                )
                
                # Get response time
                result['response_time'] = response.elapsed.total_seconds()
                result['status_code'] = response.status_code
                result['server'] = response.headers.get('Server', '')
                
                # Check if active
                if 200 <= response.status_code < 400:
                    result['status'] = 'active' if response.status_code == 200 else 'redirect'
                elif response.status_code == 403:
                    result['status'] = 'forbidden'
                elif response.status_code == 404:
                    result['status'] = 'not_found'
                
                # Try to get page title (only for active pages, skip to save time)
                if response.status_code == 200 and protocol == 'https':
                    try:
                        content = requests.get(
                            url,
                            timeout=2,  # Reduced timeout
                            verify=False
                        ).text
                        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
                        if title_match:
                            result['title'] = title_match.group(1)[:255]
                    except:
                        pass
                
                # Certificate check for HTTPS
                if protocol == 'https' and response.status_code != 404:
                    result['certificate_valid'] = True
                
                return result
            
            except requests.Timeout:
                result['status'] = 'timeout'
            except Exception:
                continue
        
        return result
    
    def discover(self):
        """Run subdomain discovery"""
        found_subdomains = []
        
        # Method 1: Brute force common subdomains
        for subdomain in COMMON_SUBDOMAINS:
            # Check DNS first
            ips = self.resolve_dns(subdomain)
            if ips:
                result = self.check_http_status(subdomain)
                result['ip_address'] = ips[0]
                found_subdomains.append(result)
            else:
                # Try HTTP check even without DNS
                result = self.check_http_status(subdomain)
                if result['status_code'] and result['status_code'] < 500:
                    found_subdomains.append(result)
        
        self.results = found_subdomains
        self.execution_time = time.time() - self.start_time
        return found_subdomains


def subdomain_finder_view(request):
    """Main subdomain finder view"""
    
    if request.method == 'POST':
        form = SubdomainFinderForm(request.POST)
        
        if form.is_valid():
            domain = form.cleaned_data['domain']
            
            # Run discovery
            finder = SubdomainFinder(domain, timeout=5)
            results = finder.discover()
            
            # Count active subdomains
            active_count = sum(1 for r in results if r['status'] in ['active', 'redirect'])
            
            # Save to database
            for result in results:
                SubdomainEntry.objects.update_or_create(
                    domain=domain,
                    subdomain=result['subdomain'],
                    defaults={
                        'ip_address': result.get('ip_address'),
                        'status_code': result.get('status_code'),
                        'status': result.get('status', 'unknown'),
                        'is_active': result.get('status') in ['active', 'redirect'],
                        'server_header': result.get('server', ''),
                        'title': result.get('title', ''),
                        'response_time': result.get('response_time'),
                        'certificate_valid': result.get('certificate_valid'),
                    }
                )
            
            # Save scan history (update if exists, create if not)
            SubdomainScanHistory.objects.update_or_create(
                domain=domain,
                scan_date=timezone.now().date(),
                defaults={
                    'total_subdomains_found': len(results),
                    'active_subdomains': active_count,
                    'scan_time': finder.execution_time,
                    'user_ip': get_client_ip(request)
                }
            )
            
            # Get all subdomains for this domain
            all_subdomains = SubdomainEntry.objects.filter(domain=domain).order_by('-is_active', 'subdomain')
            
            context = {
                'form': form,
                'domain': domain,
                'results': all_subdomains,
                'total_found': all_subdomains.count(),
                'active_count': all_subdomains.filter(is_active=True).count(),
                'execution_time': finder.execution_time,
                'status': 'success'
            }
            
            return render(request, 'subdomainfinder/index.html', context)
    else:
        form = SubdomainFinderForm()
    
    # Get recent scans
    recent_scans = SubdomainScanHistory.objects.values('domain').annotate(
        count=Count('id'),
        latest_date=Max('created_at')
    ).order_by('-latest_date')[:10]
    
    context = {
        'form': form,
        'recent_scans': recent_scans,
    }
    
    return render(request, 'subdomainfinder/index.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def subdomains_api(request):
    """API endpoint for subdomain history"""
    
    domain = request.GET.get('domain')
    
    if not domain:
        return JsonResponse({
            'status': 'error',
            'message': 'Domain parameter required'
        }, status=400)
    
    subdomains = SubdomainEntry.objects.filter(domain=domain).values()
    
    return JsonResponse({
        'status': 'success',
        'domain': domain,
        'total': subdomains.count(),
        'active': SubdomainEntry.objects.filter(domain=domain, is_active=True).count(),
        'results': list(subdomains)
    })


@csrf_exempt
@require_http_methods(["GET"])
def subdomain_statistics_api(request):
    """API endpoint for statistics"""
    
    domain = request.GET.get('domain')
    
    if not domain:
        # Return overall statistics
        stats = SubdomainScanHistory.objects.values('domain').annotate(
            scan_count=Count('id'),
            avg_time=models.Avg('scan_time'),
            total_subdomains=models.Sum('total_subdomains_found'),
            total_active=models.Sum('active_subdomains')
        ).order_by('-scan_count')[:20]
        
        return JsonResponse({
            'status': 'success',
            'statistics': list(stats)
        })
    
    # Domain-specific statistics
    history = SubdomainScanHistory.objects.filter(domain=domain).order_by('-created_at')
    
    if not history.exists():
        return JsonResponse({
            'status': 'error',
            'message': 'No scan history found'
        }, status=404)
    
    return JsonResponse({
        'status': 'success',
        'domain': domain,
        'scans': list(history.values())
    })


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
