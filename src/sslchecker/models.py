from django.db import models

class SSLCheck(models.Model):
    domain = models.CharField(max_length=255)
    is_valid = models.BooleanField(default=False)
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
