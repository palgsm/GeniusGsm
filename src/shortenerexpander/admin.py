from django.contrib import admin
from .models import ShortenerExpansion


@admin.register(ShortenerExpansion)
class ShortenerExpansionAdmin(admin.ModelAdmin):
    list_display = ['original_url', 'shortener_service', 'is_valid', 'expansion_time_ms', 'created_at']
    list_filter = ['shortener_service', 'is_valid', 'created_at']
    search_fields = ['original_url', 'expanded_url']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('URL Information', {
            'fields': ('original_url', 'expanded_url')
        }),
        ('Expansion Details', {
            'fields': ('shortener_service', 'title', 'is_valid', 'expansion_time_ms')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
