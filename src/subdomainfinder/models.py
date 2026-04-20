from django.db import models
from django.utils import timezone


class SubdomainEntry(models.Model):
    """Store subdomain discovery results"""
    
    STATUS_CHOICES = [
        ('active', 'Active (200)'),
        ('redirect', 'Redirect (300)'),
        ('not_found', 'Not Found (404)'),
        ('forbidden', 'Forbidden (403)'),
        ('timeout', 'Timeout'),
        ('unknown', 'Unknown'),
    ]
    
    domain = models.CharField(max_length=255, db_index=True)
    subdomain = models.CharField(max_length=255)
    full_url = models.URLField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')
    is_active = models.BooleanField(default=False)
    server_header = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True, help_text="Page title from HTML")
    content_length = models.IntegerField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True, help_text="Response time in seconds")
    certificate_valid = models.BooleanField(null=True, blank=True)
    certificate_issuer = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['domain', 'created_at']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = 'Subdomain Entry'
        verbose_name_plural = 'Subdomain Entries'
    
    def __str__(self):
        return f"{self.subdomain}.{self.domain}"


class SubdomainScanHistory(models.Model):
    """Track subdomain scan statistics"""
    
    domain = models.CharField(max_length=255, db_index=True)
    total_subdomains_found = models.IntegerField(default=0)
    active_subdomains = models.IntegerField(default=0)
    scan_date = models.DateField(auto_now_add=True, db_index=True)
    scan_time = models.FloatField(help_text="Scan duration in seconds")
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-scan_date']
        verbose_name = 'Subdomain Scan History'
        verbose_name_plural = 'Subdomain Scan Histories'
        unique_together = ['domain', 'scan_date']
    
    def __str__(self):
        return f"{self.domain} - {self.scan_date}"
