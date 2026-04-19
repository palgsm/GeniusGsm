from django.db import models

class PasswordCheck(models.Model):
    strength = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
