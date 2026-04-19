from django.contrib import admin
from .models import IPGeolocation

@admin.register(IPGeolocation)
class IPGeolocationAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'country', 'city', 'created_at')
