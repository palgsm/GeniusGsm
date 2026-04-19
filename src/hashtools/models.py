from django.db import models
from django.utils import timezone


class HashHistory(models.Model):
    """Store hash/encoding operations history"""
    operation_type = models.CharField(
        max_length=50,
        choices=[
            ('md5', 'MD5'),
            ('sha1', 'SHA-1'),
            ('sha256', 'SHA-256'),
            ('sha512', 'SHA-512'),
            ('blake2', 'BLAKE2'),
            ('base64_encode', 'Base64 Encode'),
            ('base64_decode', 'Base64 Decode'),
            ('url_encode', 'URL Encode'),
            ('url_decode', 'URL Decode'),
            ('html_encode', 'HTML Encode'),
            ('html_decode', 'HTML Decode'),
            ('hex_encode', 'Hex Encode'),
            ('hex_decode', 'Hex Decode'),
        ]
    )
    input_data = models.TextField(max_length=5000)
    output_data = models.TextField(max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['-created_at'])]
    
    def __str__(self):
        return f"{self.operation_type} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class EncodingHistory(models.Model):
    """Store encoding operations history"""
    encoding_type = models.CharField(
        max_length=50,
        choices=[
            ('base64_encode', 'Base64 Encode'),
            ('base64_decode', 'Base64 Decode'),
            ('url_encode', 'URL Encode'),
            ('url_decode', 'URL Decode'),
            ('html_encode', 'HTML Encode'),
            ('html_decode', 'HTML Decode'),
            ('hex_encode', 'Hex Encode'),
            ('hex_decode', 'Hex Decode'),
        ]
    )
    input_data = models.TextField(max_length=5000)
    output_data = models.TextField(max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['-created_at'])]
    
    def __str__(self):
        return f"{self.encoding_type} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
