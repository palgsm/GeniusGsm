from django.contrib import admin
from .models import DomainCheck


@admin.register(DomainCheck)
class DomainCheckAdmin(admin.ModelAdmin):
    list_display = ('domain', 'check_status', 'created_at')
    list_filter = ('check_status', 'created_at')
    search_fields = ('domain',)
