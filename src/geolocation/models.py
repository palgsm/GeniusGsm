from django.db import models

class IPGeolocation(models.Model):
    ip_address = models.GenericIPAddressField()
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
