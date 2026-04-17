from django.contrib import admin
from .models import AbuseReport


@admin.register(AbuseReport)
class AbuseReportAdmin(admin.ModelAdmin):
    list_display = ('ip', 'reporter', 'category', 'source', 'created_at', 'archived')
    list_filter = ('source', 'category', 'archived')
    search_fields = ('ip', 'reporter', 'email', 'description')
    readonly_fields = ('created_at',)
