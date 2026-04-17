from django.contrib import admin
from .models import IPGroup, IPRange, BulkImportLog


@admin.register(IPGroup)
class IPGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_range_count', 'get_total_ips', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_range_count(self, obj):
        return obj.ranges.count()
    get_range_count.short_description = 'Ranges Count'
    
    def get_total_ips(self, obj):
        return obj.get_total_ips()
    get_total_ips.short_description = 'Total IPs'


@admin.register(IPRange)
class IPRangeAdmin(admin.ModelAdmin):
    list_display = ['cidr', 'group', 'ip_version', 'get_ip_count', 'created_at']
    list_filter = ['group', 'ip_version', 'created_at']
    search_fields = ['cidr', 'description']
    readonly_fields = ['start_ip', 'end_ip', 'ip_version', 'created_at', 'updated_at']
    
    def get_ip_count(self, obj):
        return obj.get_ip_count()
    get_ip_count.short_description = 'IP Count'


@admin.register(BulkImportLog)
class BulkImportLogAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'group', 'status', 'successful_imports', 'failed_imports', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['file_name']
    readonly_fields = ['created_at', 'completed_at']
