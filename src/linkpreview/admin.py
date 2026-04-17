from django.contrib import admin
from .models import LinkPreview


@admin.register(LinkPreview)
class LinkPreviewAdmin(admin.ModelAdmin):
    list_display = ['domain', 'title', 'page_size', 'load_time', 'view_count', 'created_at']
    list_filter = ['created_at', 'is_valid']
    search_fields = ['url', 'domain', 'title']
    readonly_fields = ['created_at', 'updated_at', 'last_accessed', 'view_count']
    
    fieldsets = (
        ('URL Information', {
            'fields': ('url', 'domain')
        }),
        ('Page Content', {
            'fields': ('title', 'description', 'image_url', 'favicon_url')
        }),
        ('Technical Details', {
            'fields': ('page_size', 'load_time', 'content_type', 'dominant_color')
        }),
        ('Meta Data', {
            'fields': ('og_data', 'twitter_data'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_valid', 'error_message')
        }),
        ('Statistics', {
            'fields': ('view_count', 'created_at', 'updated_at', 'last_accessed'),
            'classes': ('collapse',)
        }),
    )
