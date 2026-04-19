from django.contrib import admin
from .models import DNSQuery


@admin.register(DNSQuery)
class DNSQueryAdmin(admin.ModelAdmin):
    list_display = ('domain', 'query_type', 'created_at')
    list_filter = ('query_type', 'created_at')
    search_fields = ('domain',)
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
