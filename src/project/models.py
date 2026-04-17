from django.db import models


class SEOConfig(models.Model):
    """
    SEO Configuration for each tool/app
    Allows administrators to manage meta tags and keywords for each application
    """
    
    APP_CHOICES = [
        ('home', 'Homepage'),
        ('iplookup', 'IP Lookup'),
        ('abusecheck', 'Abuse Check'),
        ('ipbulk', 'IP Bulk'),
        ('urlanalyzer', 'URL Analyzer'),
        ('shortener', 'Short Link Expander'),
        ('preview', 'Link Preview'),
        ('phishing', 'Phishing Detector'),
        ('randomlines', 'Random Lines'),
        ('duplicatecounter', 'Duplicate Counter'),
        ('jwtchecker', 'JWT Checker'),
        ('tempmail', 'Temp Mail'),
        ('speedtest', 'Speed Test'),
    ]
    
    app_name = models.CharField(
        max_length=50,
        choices=APP_CHOICES,
        unique=True,
        help_text="Select the application to configure SEO for"
    )
    
    title = models.CharField(
        max_length=70,
        help_text="Page title (recommended: 50-60 characters)"
    )
    
    meta_description = models.CharField(
        max_length=160,
        help_text="Meta description for search results (recommended: 150-160 characters)"
    )
    
    meta_keywords = models.TextField(
        help_text="Keywords separated by commas (e.g., 'keyword1, keyword2, keyword3')"
    )
    
    og_title = models.CharField(
        max_length=100,
        help_text="Open Graph title for social media sharing"
    )
    
    og_description = models.CharField(
        max_length=160,
        help_text="Open Graph description for social media sharing"
    )
    
    canonical_url = models.URLField(
        help_text="Canonical URL for this page"
    )
    
    twitter_title = models.CharField(
        max_length=70,
        blank=True,
        help_text="Twitter card title (optional)"
    )
    
    twitter_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Twitter card description (optional)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "SEO Configuration"
        verbose_name_plural = "SEO Configurations"
        ordering = ['app_name']
    
    def __str__(self):
        return f"SEO Config - {self.get_app_name_display()}"
