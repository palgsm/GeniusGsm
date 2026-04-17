from django.db import models


class PhishingDetection(models.Model):
    """Model to store phishing detection results"""
    
    RISK_LEVELS = [
        ('safe', 'Safe'),
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical'),
    ]
    
    url = models.URLField(max_length=2000)
    domain = models.CharField(max_length=500)
    phishing_score = models.IntegerField(default=0)  # 0-100
    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVELS,
        default='safe'
    )
    is_phishing = models.BooleanField(default=False)
    
    # Detection indicators
    suspicious_domain = models.BooleanField(default=False)
    suspicious_ssl = models.BooleanField(default=False)
    suspicious_chars = models.BooleanField(default=False)
    suspicious_url_structure = models.BooleanField(default=False)
    phishing_keywords = models.BooleanField(default=False)
    form_fields = models.IntegerField(default=0)
    redirect_chains = models.IntegerField(default=0)
    
    # Additional data
    indicators_found = models.TextField(blank=True, null=True)  # JSON
    page_title = models.CharField(max_length=500, blank=True, null=True)
    detection_method = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Phishing Detections"
    
    def __str__(self):
        return f"{self.domain} - {self.risk_level} ({self.phishing_score}%)"
