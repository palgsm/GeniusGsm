from django.db import models


class AbuseReport(models.Model):
    """A simple user-submitted abuse report for an IP address."""
    ip = models.GenericIPAddressField()
    reporter = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    category = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    source = models.CharField(max_length=32, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ip} - {self.reporter or 'anonymous'} ({self.created_at:%Y-%m-%d})"
