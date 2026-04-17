from django.contrib import admin
from .models import URLAnalysisResult, PhishingIndicator, URLBlacklist


@admin.register(URLAnalysisResult)
class URLAnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('domain', 'risk_level', 'phishing_score', 'is_phishing', 'created_at')
    list_filter = ('risk_level', 'is_phishing', 'has_shortener', 'created_at')
    search_fields = ('domain', 'original_url', 'expanded_url')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('URL Information', {
            'fields': ('original_url', 'expanded_url', 'domain')
        }),
        ('Risk Assessment', {
            'fields': ('risk_level', 'is_phishing', 'phishing_score', 'phishing_indicators')
        }),
        ('URL Analysis', {
            'fields': ('has_shortener', 'shortener_service')
        }),
        ('Technical Details', {
            'fields': ('has_ssl', 'uses_http', 'suspicious_chars')
        }),
        ('Page Content', {
            'fields': ('title', 'meta_description')
        }),
        ('Domain Information', {
            'fields': ('domain_age_days', 'domain_reputation')
        }),
        ('Metadata', {
            'fields': ('user_ip', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Results are added via API only


@admin.register(PhishingIndicator)
class PhishingIndicatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    search_fields = ('name', 'description')


@admin.register(URLBlacklist)
class URLBlacklistAdmin(admin.ModelAdmin):
    list_display = ('url_or_domain', 'reason', 'is_active', 'date_added')
    list_filter = ('is_active', 'date_added')
    search_fields = ('url_or_domain', 'reason')
