from django.db import models
import ipaddress
from django.core.exceptions import ValidationError

class IPGroup(models.Model):
    """IP Range Group"""
    name = models.CharField(max_length=255, unique=True, help_text="Group name")
    description = models.TextField(blank=True, help_text="Group description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "IP Groups"
    
    def __str__(self):
        return self.name
    
    def get_total_ips(self):
        """Calculate total number of IPs in the group"""
        total = 0
        for ip_range in self.ranges.all():
            total += ip_range.get_ip_count()
        return total
    
    def get_countries(self):
        """Get list of countries in the group"""
        return self.ranges.values_list('country', flat=True).distinct()
    
    def get_ranges_by_country(self, country_code):
        """Get IP ranges by country"""
        return self.ranges.filter(country=country_code)


class IPRange(models.Model):
    """Single IP Range (supports CIDR notation)"""
    COUNTRY_CHOICES = [
        ('IQ', '🇮🇶 Iraq'),
        ('AE', '🇦🇪 United Arab Emirates'),
        ('SA', '🇸🇦 Saudi Arabia'),
        ('EG', '🇪🇬 Egypt'),
        ('JO', '🇯🇴 Jordan'),
        ('PS', '🇵🇸 Palestine'),
        ('LB', '🇱🇧 Lebanon'),
        ('SY', '🇸🇾 Syria'),
        ('TN', '🇹🇳 Tunisia'),
        ('MA', '🇲🇦 Morocco'),
        ('KW', '🇰🇼 Kuwait'),
        ('QA', '🇶🇦 Qatar'),
        ('BH', '🇧🇭 Bahrain'),
        ('OM', '🇴🇲 Oman'),
        ('YE', '🇾🇪 Yemen'),
        ('US', '🇺🇸 United States'),
        ('GB', '🇬🇧 United Kingdom'),
        ('CA', '🇨🇦 Canada'),
        ('AU', '🇦🇺 Australia'),
        ('JP', '🇯🇵 Japan'),
        ('DE', '🇩🇪 Germany'),
        ('FR', '🇫🇷 France'),
        ('IN', '🇮🇳 India'),
        ('CN', '🇨🇳 China'),
        ('RU', '🇷🇺 Russia'),
        ('OTHER', '🌍 Other'),
    ]
    
    group = models.ForeignKey(IPGroup, on_delete=models.CASCADE, related_name='ranges')
    cidr = models.CharField(
        max_length=43,
        help_text="IP range in CIDR format (e.g., 192.168.0.0/24 or 2001:db8::/32)"
    )
    country = models.CharField(
        max_length=10,
        choices=COUNTRY_CHOICES,
        default='OTHER',
        help_text="Country associated with this range"
    )
    start_ip = models.GenericIPAddressField(editable=False)
    end_ip = models.GenericIPAddressField(editable=False)
    ip_version = models.IntegerField(choices=[(4, 'IPv4'), (6, 'IPv6')], editable=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('group', 'cidr')
        ordering = ['country', 'start_ip']
        indexes = [
            models.Index(fields=['country', 'group']),
        ]
    
    def __str__(self):
        return f"{self.cidr} - {self.get_country_display()}"
    
    def clean(self):
        """Validate CIDR format"""
        try:
            network = ipaddress.ip_network(self.cidr, strict=False)
        except ValueError as e:
            raise ValidationError(f"Invalid CIDR format: {str(e)}")
    
    def save(self, *args, **kwargs):
        """Save data after parsing the range"""
        self.clean()
        network = ipaddress.ip_network(self.cidr, strict=False)
        self.start_ip = str(network.network_address)
        self.end_ip = str(network.broadcast_address)
        self.ip_version = network.version
        super().save(*args, **kwargs)
    
    def get_ip_count(self):
        """Get number of IPs in the range"""
        network = ipaddress.ip_network(self.cidr, strict=False)
        return network.num_addresses
    
    def contains_ip(self, ip_str):
        """Check if IP is in the range"""
        try:
            ip = ipaddress.ip_address(ip_str)
            network = ipaddress.ip_network(self.cidr, strict=False)
            return ip in network
        except ValueError:
            return False


class BulkImportLog(models.Model):
    """Bulk import log"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    file_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    group = models.ForeignKey(IPGroup, on_delete=models.SET_NULL, null=True)
    total_records = models.IntegerField(default=0)
    successful_imports = models.IntegerField(default=0)
    failed_imports = models.IntegerField(default=0)
    errors_log = models.TextField(blank=True, help_text="Error log")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.status}"
