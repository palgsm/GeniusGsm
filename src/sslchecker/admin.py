from django.contrib import admin
from .models import SSLCheck

@admin.register(SSLCheck)
class SSLCheckAdmin(admin.ModelAdmin):
    list_display = ('domain', 'is_valid', 'created_at')
