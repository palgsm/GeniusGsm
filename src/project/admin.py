from django.contrib import admin
from .models import SEOConfig

# Custom site texts
admin.site.site_header = "GeniusGsm Admin — Welcome"
admin.site.site_title = "GeniusGsm Admin"
admin.site.index_title = "Administration Dashboard"


@admin.register(SEOConfig)
class SEOConfigAdmin(admin.ModelAdmin):
    """
    Admin interface for managing SEO configuration for all applications
    """
    list_display = ('get_app_display', 'updated_at', 'preview_keywords')
    list_filter = ('app_name', 'updated_at')
    search_fields = ('app_name', 'meta_keywords', 'meta_description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Application', {
            'fields': ('app_name',)
        }),
        ('Page Information', {
            'fields': ('title', 'meta_description'),
            'classes': ('wide',)
        }),
        ('Keywords & SEO', {
            'fields': ('meta_keywords',),
            'classes': ('wide',)
        }),
        ('Social Media & Sharing', {
            'fields': ('og_title', 'og_description', 'twitter_title', 'twitter_description'),
            'classes': ('wide', 'collapse'),
            'description': 'Configuration for Open Graph and Twitter Card sharing'
        }),
        ('Technical SEO', {
            'fields': ('canonical_url',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Automatic timestamps'
        }),
    )
    
    def get_app_display(self, obj):
        return obj.get_app_name_display()
    get_app_display.short_description = 'Application'
    
    def preview_keywords(self, obj):
        """Preview first 50 characters of keywords"""
        keywords = obj.meta_keywords[:50]
        if len(obj.meta_keywords) > 50:
            keywords += '...'
        return keywords
    preview_keywords.short_description = 'Keywords Preview'
