from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.conf import settings
from django.http import HttpResponse
from abusecheck.models import AbuseReport
from .models import SEOConfig
import socket


def get_seo_config(app_name):
    """
    Utility function to get SEO configuration for a specific application
    Returns a dictionary with all SEO metadata for use in templates
    """
    try:
        config = SEOConfig.objects.get(app_name=app_name)
        return {
            'title': config.title,
            'meta_description': config.meta_description,
            'meta_keywords': config.meta_keywords,
            'og_title': config.og_title,
            'og_description': config.og_description,
            'og_url': config.canonical_url,
            'twitter_title': config.twitter_title or config.og_title,
            'twitter_description': config.twitter_description or config.og_description,
            'canonical_url': config.canonical_url,
        }
    except SEOConfig.DoesNotExist:
        # Return default values if config doesn't exist
        return None

def home(request):
    # Get featured blog posts
    try:
        from blog.models import BlogPost
        featured_posts = BlogPost.objects.filter(
            status='published',
            featured=True
        ).order_by('-published_date')[:3]
    except:
        featured_posts = None
    
    context = {
        'featured_posts': featured_posts
    }
    return render(request, 'home.html', context)

def custom_logout(request):
    """Custom logout view that accepts GET and redirects properly"""
    logout(request)
    return redirect('home')

@login_required(login_url='/admin/login/')
def dashboard(request):
    """
    Show الداشبورد الرئيسي مع معلومات الجلسة والـ Token والإحصائيات
    """
    # #  
    session_timeout_minutes = settings.SESSION_COOKIE_AGE // 60  # #    
    
    # #  IP 
    try:
        current_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'N/A'))
        if ',' in current_ip:
            current_ip = current_ip.split(',')[0].strip()
    except:
        current_ip = 'N/A'
    
    # # 
    total_requests = request.session.get('total_requests', 0)
    abuse_reports = AbuseReport.objects.filter(archived=False).count()
    active_services = 3  # IP Lookup, Abuse Check, Stats
    
    # #   
    reports = AbuseReport.objects.filter(archived=False)[:20]
    
    context = {
        'session_timeout_minutes': session_timeout_minutes,
        'current_ip': current_ip,
        'total_requests': total_requests,
        'abuse_reports': abuse_reports,
        'active_services': active_services,
        'reports': reports,
    }
    
    return render(request, 'dashboard.html', context)


def robots_txt(request):
    """Return robots.txt for search engine crawlers"""
    robots_content = """# GeniusGsm SEO Robots Configuration
# Allow all search engines to crawl the site

User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /static/admin/
Allow: /

# Specific search engines
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Slurp
Allow: /

User-agent: DuckDuckBot
Allow: /

# Crawl delay settings
User-agent: *
Crawl-delay: 1

# Sitemap location
Sitemap: https://geniusgsm.com/sitemap.xml
Sitemap: https://geniusgsm.com/sitemap-pages.xml
"""
    return HttpResponse(robots_content, content_type='text/plain')


def sitemap_xml(request):
    """Return sitemap.xml for search engines"""
    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
        xmlns:mobile="http://www.google.com/schemas/sitemap-mobile/1.0">
    
    <!-- Homepage -->
    <url>
        <loc>https://geniusgsm.com/</loc>
        <lastmod>2026-04-17</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>

    <!-- NETWORK TOOLS CATEGORY -->
    
    <!-- Tool 1: IP Lookup - Search IP address geolocation -->
    <url>
        <loc>https://geniusgsm.com/ip/lookup/</loc>
        <lastmod>2026-04-17</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.9</priority>
    </url>

    <!-- Tool 2: Abuse Check - Check IP reputation and blacklist status -->
    <url>
        <loc>https://geniusgsm.com/abuse/lookup/</loc>
        <lastmod>2026-04-17</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.9</priority>
    </url>

    <!-- Tool 5: IP Bulk - Process multiple IP addresses at once -->
    <url>
        <loc>https://geniusgsm.com/ipbulk/groups/</loc>
        <lastmod>2026-04-17</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>

    <!-- URL TOOLS CATEGORY -->
    
    <!-- Tool 8: URL Analyzer - Analyze links for phishing and safety -->
    <url>
        <loc>https://geniusgsm.com/urlanalyzer/</loc>
        <lastmod>2026-04-17</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.9</priority>
    </url>

    <!-- Tool 9: Short Link Expander - Expand shortened URLs (bit.ly, tinyurl) -->
    <url>
        <loc>https://geniusgsm.com/shortener/</loc>
        <lastmod>2026-04-17</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>

    <!-- Tool 11: Link Preview - Preview website content without visiting -->
    <url>
        <loc>https://geniusgsm.com/preview/</loc>
        <lastmod>2026-04-17</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>

    <!-- Tool 10: Phishing Detector - Detect phishing and malicious websites -->
    <url>
        <loc>https://geniusgsm.com/phishing/</loc>
        <lastmod>2026-04-17</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.9</priority>
    </url>

    <!-- TEXT TOOLS CATEGORY -->
    
    <!-- Tool 6: Random Lines - Shuffle and randomize text lines -->
    <url>
        <loc>https://geniusgsm.com/randomlines/</loc>
        <lastmod>2026-04-17</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>

    <!-- Tool 7: Duplicate Counter - Count and remove duplicate lines -->
    <url>
        <loc>https://geniusgsm.com/duplicatecounter/</loc>
        <lastmod>2026-04-17</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>

    <!-- SECURITY TOOLS CATEGORY -->
    
    <!-- Tool 3: JWT Checker - Parse and analyze JWT tokens -->
    <url>
        <loc>https://geniusgsm.com/jwtchecker/</loc>
        <lastmod>2026-04-17</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>

    <!-- Tool 4: Temp Mail - Generate temporary email addresses -->
    <url>
        <loc>https://geniusgsm.com/tempmail/</loc>
        <lastmod>2026-04-17</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>

    <!-- UTILITIES CATEGORY -->
    
    <!-- Tool 12: Speed Test - Measure download, upload and ping speed -->
    <url>
        <loc>https://geniusgsm.com/speedtest/</loc>
        <lastmod>2026-04-17</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>

</urlset>"""
    return HttpResponse(sitemap_content, content_type='application/xml')


def page_not_found(request, exception):
    """Handle 404 errors with custom template"""
    return render(request, '404.html', status=404)


def server_error(request):
    """Handle 500 errors with custom template"""
    return render(request, '500.html', status=500)
