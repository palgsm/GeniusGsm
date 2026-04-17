from django.contrib import admin
from .models import SpeedTest


@admin.register(SpeedTest)
class SpeedTestAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'download_speed', 'upload_speed', 'ping', 'grade', 'ip_address')
    list_filter = ('grade', 'timestamp')
    search_fields = ('ip_address', 'isp', 'location')
    readonly_fields = ('timestamp',)
    
    fieldsets = (
        ('Speed Test Results', {
            'fields': ('download_speed', 'upload_speed', 'ping', 'grade')
        }),
        ('Connection Info', {
            'fields': ('ip_address', 'isp', 'location')
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )
