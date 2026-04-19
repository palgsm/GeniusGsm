from django.contrib import admin
from .models import TextComparison, MultiFileComparison


@admin.register(TextComparison)
class TextComparisonAdmin(admin.ModelAdmin):
    """Admin interface for text comparisons"""
    
    list_display = ('comparison_type', 'similarity_percentage', 'differences_count', 'created_at')
    list_filter = ('comparison_type', 'created_at')
    readonly_fields = ('created_at', 'similarity_percentage', 'differences_count')
    search_fields = ('text1', 'text2')
    
    fieldsets = (
        ('Comparison Info', {
            'fields': ('comparison_type', 'similarity_percentage', 'differences_count')
        }),
        ('Texts', {
            'fields': ('text1', 'text2')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(MultiFileComparison)
class MultiFileComparisonAdmin(admin.ModelAdmin):
    """Admin interface for multi-file comparisons"""
    
    list_display = ('base_file_name', 'total_files', 'comparison_type', 'created_at')
    list_filter = ('comparison_type', 'total_files', 'created_at')
    readonly_fields = ('created_at', 'base_file_name', 'comparison_file_names', 'similarity_data')
    search_fields = ('base_file_name', 'comparison_file_names')
    
    fieldsets = (
        ('Files Info', {
            'fields': ('base_file_name', 'comparison_file_names', 'total_files')
        }),
        ('Comparison', {
            'fields': ('comparison_type', 'similarity_data')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return True
