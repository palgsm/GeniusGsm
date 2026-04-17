from django.contrib import admin
from .models import PhishingDetection


@admin.register(PhishingDetection)
class PhishingDetectionAdmin(admin.ModelAdmin):
    list_display = ['domain', 'risk_level', 'phishing_score', 'is_phishing', 'form_fields', 'created_at']
    list_filter = ['risk_level', 'is_phishing', 'created_at']
    search_fields = ['url', 'domain', 'page_title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('URL Information', {
            'fields': ('url', 'domain')
        }),
        ('Detection Results', {
            'fields': ('phishing_score', 'risk_level', 'is_phishing')
        }),
        ('Indicators', {
            'fields': ('indicators_found', 'page_title', 'form_fields')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
