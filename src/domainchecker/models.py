from django.db import models


class DomainCheck(models.Model):
    """Store domain check history"""
    domain = models.CharField(max_length=255)
    check_status = models.CharField(max_length=50, choices=[
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
        ('error', 'Error'),
    ])
    whois_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.domain} - {self.created_at}"
