from django.db import models


class SpeedTest(models.Model):
    """Model to store speed test results"""
    
    SPEED_GRADES = [
        ('poor', 'Poor (< 5 Mbps)'),
        ('fair', 'Fair (5-25 Mbps)'),
        ('good', 'Good (25-100 Mbps)'),
        ('excellent', 'Excellent (> 100 Mbps)'),
    ]
    
    download_speed = models.FloatField(help_text="Download speed in Mbps")
    upload_speed = models.FloatField(help_text="Upload speed in Mbps")
    ping = models.FloatField(help_text="Ping latency in ms")
    grade = models.CharField(max_length=20, choices=SPEED_GRADES, default='fair')
    ip_address = models.GenericIPAddressField()
    isp = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Speed Test Result'
        verbose_name_plural = 'Speed Test Results'
    
    def __str__(self):
        return f"Speed Test - {self.download_speed} Mbps - {self.timestamp}"
    
    def get_grade(self):
        """Calculate grade based on download speed"""
        if self.download_speed >= 100:
            return 'excellent'
        elif self.download_speed >= 25:
            return 'good'
        elif self.download_speed >= 5:
            return 'fair'
        else:
            return 'poor'
