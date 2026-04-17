from django.db import models


class ShortenerExpansion(models.Model):
    """Model to store short URL expansion history"""
    
    SHORTENER_SERVICES = [
        ('bitly', 'Bit.ly'),
        ('tinyurl', 'TinyURL'),
        ('owly', 'Ow.ly'),
        ('googl', 'Goo.gl'),
        ('shortlink', 'Short.link'),
        ('blinkk', 'Bl.ink'),
        ('rebrantly', 'Rebrand.ly'),
        ('tinycc', 'Tiny.cc'),
        ('qrnet', 'QR.net'),
        ('unknown', 'Unknown Shortener'),
    ]
    
    original_url = models.URLField(max_length=2000)
    expanded_url = models.URLField(max_length=2000)
    shortener_service = models.CharField(
        max_length=50,
        choices=SHORTENER_SERVICES,
        default='unknown'
    )
    title = models.CharField(max_length=500, blank=True, null=True)
    is_valid = models.BooleanField(default=True)
    expansion_time_ms = models.IntegerField(null=True, blank=True)  # Time to expand in milliseconds
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Shortener Expansions"
    
    def __str__(self):
        return f"{self.shortener_service}: {self.original_url[:50]}..."
