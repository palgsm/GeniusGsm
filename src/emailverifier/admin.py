from django.contrib import admin
from .models import EmailCheck

@admin.register(EmailCheck)
class EmailCheckAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_valid', 'created_at')
    list_filter = ('is_valid', 'created_at')
