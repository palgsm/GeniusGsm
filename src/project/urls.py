"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views, api, blog_media, test_views
from iplookup import views as ip_views
from django.urls import include as _include
from django.conf import settings
from django.conf.urls.static import static

# Customize Django Admin Site
admin.site.site_header = "GeniusGsm Administration"
admin.site.site_title = "GeniusGsm Admin"
admin.site.index_title = "Welcome to GeniusGsm Administration"

urlpatterns = [
    path('', views.home, name='home'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Blog featured images
    path('media/blog/featured/<str:filename>', blog_media.serve_blog_image, name='blog_image'),
    # DEBUG: Test image page
    path('test-images/', test_views.test_image_page, name='test_images'),
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),  # Logout, login, password change, etc
    path('api/ip/', include('iplookup.urls')),
    path('api/session/', api.session_info, name='api_session_info'),
    path('api/dashboard/', api.dashboard_stats, name='api_dashboard_stats'),
    path('api/token/', api.token_status, name='api_token_status'),
    # Simple web UI for IP lookup (form + result view)
    path('ip/lookup/', ip_views.ip_lookup_page, name='ip_lookup'),
    path('abuse/', _include('abusecheck.urls')),
    path('ipbulk/', _include('ipbulk.urls')),
    path('tempmail/', _include('tempmail.urls')),
    path('randomlines/', _include('randomlines.urls')),
    path('duplicatecounter/', _include('duplicatecounter.urls')),
    path('jwtchecker/', _include('jwtchecker.urls')),
    path('urlanalyzer/', _include('urlanalyzer.urls')),
    path('shortener/', _include('shortenerexpander.urls')),
    path('phishing/', _include('phishingdetector.urls')),
    path('preview/', _include('linkpreview.urls')),
    path('speedtest/', _include('speedtest.urls')),
    path('hashtools/', _include('hashtools.urls')),
    path('dnstools/', _include('dnstools.urls')),
    path('domainchecker/', _include('domainchecker.urls')),
    path('emailverifier/', _include('emailverifier.urls')),
    path('sslchecker/', _include('sslchecker.urls')),
    path('passwordchecker/', _include('passwordchecker.urls')),
    path('geolocation/', _include('geolocation.urls')),
    path('comparator/', _include('textcomparator.urls')),
    path('scanurlmalware/', _include('urlmalwarescanner.urls')),  # URL Malware Scanner - Phase 1
    path('subdomains/', _include('subdomainfinder.urls')),  # Subdomain Finder - Phase 1
    path('vulnerable/', _include('vulnerabilityscanner.urls')),  # Vulnerability Scanner - Phase 1
    path('blog/', _include('blog.urls')),  # Blog for content marketing
]

# Serve media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers
handler404 = 'project.views.page_not_found'
handler500 = 'project.views.server_error'
