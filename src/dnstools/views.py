import dns.resolver
import dns.rdatatype
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import DNSQuery
from .forms import DNSQueryForm


def query_dns(domain, query_type):
    """Perform DNS query"""
    try:
        resolver = dns.resolver.Resolver()
        resolver.lifetime = 5  # Timeout
        
        # Get record type
        rdtype = dns.rdatatype.from_text(query_type)
        
        # Perform query
        answers = resolver.resolve(domain, rdtype)
        results = []
        
        for rdata in answers:
            results.append(str(rdata))
        
        return {
            'success': True,
            'results': results,
            'count': len(results)
        }
    except dns.resolver.NXDOMAIN:
        return {
            'success': False,
            'error': f'Domain Not Found: {domain}'
        }
    except dns.resolver.NoAnswer:
        return {
            'success': False,
            'error': f'No {query_type} records found for {domain}'
        }
    except dns.exception.Timeout:
        return {
            'success': False,
            'error': 'DNS query timeout'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error: {str(e)}'
        }


@require_http_methods(["GET", "POST"])
def dnstools_index(request):
    """DNS Tools main view"""
    result = None
    form = DNSQueryForm()
    history = DNSQuery.objects.all()[:20]
    
    if request.method == 'POST':
        form = DNSQueryForm(request.POST)
        if form.is_valid():
            domain = form.cleaned_data['domain']
            query_type = form.cleaned_data['query_type']
            
            result = query_dns(domain, query_type)
            
            if result['success']:
                # Save to history
                DNSQuery.objects.create(
                    domain=domain,
                    query_type=query_type,
                    result=json.dumps(result['results'])
                )
    
    context = {
        'form': form,
        'result': result,
        'history': history,
        'page_title': 'DNS Lookup Tools',
        'page_description': 'Query DNS records for a domain (A, AAAA, MX, NS, SOA, CNAME, TXT)',
    }
    
    return render(request, 'dnstools/index.html', context)


@require_http_methods(["POST"])
def api_dns_query(request):
    """API endpoint for DNS queries"""
    try:
        domain = request.POST.get('domain')
        query_type = request.POST.get('query_type')
        
        if not domain or not query_type:
            return JsonResponse({'error': 'Missing parameters'}, status=400)
        
        result = query_dns(domain, query_type)
        
        if result['success']:
            DNSQuery.objects.create(
                domain=domain,
                query_type=query_type,
                result=json.dumps(result['results'])
            )
        
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
