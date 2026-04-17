from django.db import models
import json


class LinkPreview(models.Model):
    """Model to store link preview data"""
    
    url = models.URLField(max_length=2000, unique=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(max_length=2000, blank=True, null=True)
    favicon_url = models.URLField(max_length=500, blank=True, null=True)
    domain = models.CharField(max_length=500, blank=True, null=True)
    
    # Page info
    page_size = models.IntegerField(null=True, blank=True)  # In KB
    load_time = models.FloatField(null=True, blank=True)  # In seconds
    content_type = models.CharField(max_length=100, blank=True, null=True)
    
    # Open Graph data (stored as JSON)
    og_data = models.TextField(blank=True, null=True)  # JSON
    
    # Twitter Card data (stored as JSON)
    twitter_data = models.TextField(blank=True, null=True)  # JSON
    
    # Color info
    dominant_color = models.CharField(max_length=7, blank=True, null=True)  # HEX color
    
    # Status
    is_valid = models.BooleanField(default=True)
    error_message = models.CharField(max_length=500, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-last_accessed']
        verbose_name_plural = "Link Previews"
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.domain} - {self.title[:50] if self.title else 'No title'}"
    
    def get_og_data(self):
        """Parse OG data from JSON"""
        try:
            return json.loads(self.og_data) if self.og_data else {}
        except:
            return {}
    
    def get_twitter_data(self):
        """Parse Twitter data from JSON"""
        try:
            return json.loads(self.twitter_data) if self.twitter_data else {}
        except:
            return {}
