from django.db import models
from django.utils import timezone


class URLAnalysisResult(models.Model):
    """Store URL analysis results"""
    
    RISK_LEVELS = [
        ('safe', 'Safe'),
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]
    
    original_url = models.URLField(max_length=2000)
    expanded_url = models.URLField(max_length=2000, blank=True, null=True)
    domain = models.CharField(max_length=255)
    
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='safe')
    
    # Phishing detection
    is_phishing = models.BooleanField(default=False)
    phishing_score = models.FloatField(default=0.0)  # 0-100
    phishing_indicators = models.JSONField(default=dict, blank=True)
    
    # URL analysis
    has_shortener = models.BooleanField(default=False)
    shortener_service = models.CharField(max_length=100, blank=True, null=True)
    
    # Domain information
    domain_age_days = models.IntegerField(blank=True, null=True)
    domain_reputation = models.CharField(max_length=50, blank=True, null=True)
    
    # Additional info
    title = models.CharField(max_length=500, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    
    # Technical details
    has_ssl = models.BooleanField(default=False)
    uses_http = models.BooleanField(default=False)
    suspicious_chars = models.JSONField(default=list, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_ip = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.domain} - {self.risk_level}"


class PhishingIndicator(models.Model):
    """Store phishing detection indicators for reference"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    weight = models.FloatField(default=1.0)  # Weight for scoring
    
    def __str__(self):
        return self.name


class URLBlacklist(models.Model):
    """Known malicious URLs/domains"""
    
    url_or_domain = models.CharField(max_length=500, unique=True)
    reason = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "URL Blacklists"
    
    def __str__(self):
        return self.url_or_domain
