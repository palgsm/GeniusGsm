from django.contrib import admin
from .models import HashHistory, EncodingHistory


@admin.register(HashHistory)
class HashHistoryAdmin(admin.ModelAdmin):
    list_display = ('operation_type', 'input_data', 'created_at')
    list_filter = ('operation_type', 'created_at')
    search_fields = ('input_data', 'output_data')
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(EncodingHistory)
class EncodingHistoryAdmin(admin.ModelAdmin):
    list_display = ('encoding_type', 'input_data', 'created_at')
    list_filter = ('encoding_type', 'created_at')
    search_fields = ('input_data', 'output_data')
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
