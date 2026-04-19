from django.db import models


class DNSQuery(models.Model):
    """Store DNS query history"""
    domain = models.CharField(max_length=255)
    query_type = models.CharField(
        max_length=10,
        choices=[
            ('A', 'A - IPv4'),
            ('AAAA', 'AAAA - IPv6'),
            ('MX', 'MX - Mail'),
            ('NS', 'NS - Nameserver'),
            ('SOA', 'SOA - Authority'),
            ('CNAME', 'CNAME - Alias'),
            ('TXT', 'TXT - Text'),
            ('PTR', 'PTR - Reverse'),
        ]
    )
    result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['-created_at'])]
    
    def __str__(self):
        return f"{self.domain} - {self.query_type}"
