from django.contrib import admin
from .models import PasswordCheck

@admin.register(PasswordCheck)
class PasswordCheckAdmin(admin.ModelAdmin):
    list_display = ('strength', 'created_at')
