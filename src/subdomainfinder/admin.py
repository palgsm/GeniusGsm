from django.contrib import admin
from .models import SubdomainEntry, SubdomainScanHistory


@admin.register(SubdomainEntry)
class SubdomainEntryAdmin(admin.ModelAdmin):
    list_display = ('full_subdomain', 'domain', 'status', 'status_code', 'ip_address', 'is_active', 'created_at')
    list_filter = ('status', 'is_active', 'domain', 'created_at')
    search_fields = ('domain', 'subdomain', 'ip_address')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Domain Information', {
            'fields': ('domain', 'subdomain', 'full_url')
        }),
        ('Network Information', {
            'fields': ('ip_address', 'status_code', 'status')
        }),
        ('HTTP Information', {
            'fields': ('server_header', 'title', 'content_length', 'response_time')
        }),
        ('SSL/Certificate', {
            'fields': ('certificate_valid', 'certificate_issuer')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def full_subdomain(self, obj):
        return f"{obj.subdomain}.{obj.domain}"
    full_subdomain.short_description = 'Subdomain'


@admin.register(SubdomainScanHistory)
class SubdomainScanHistoryAdmin(admin.ModelAdmin):
    list_display = ('domain', 'scan_date', 'total_subdomains_found', 'active_subdomains', 'scan_time')
    list_filter = ('domain', 'scan_date')
    search_fields = ('domain',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Scan Information', {
            'fields': ('domain', 'scan_date')
        }),
        ('Results', {
            'fields': ('total_subdomains_found', 'active_subdomains', 'scan_time')
        }),
        ('User Information', {
            'fields': ('user_ip',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
