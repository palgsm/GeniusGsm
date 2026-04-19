from django.db import models


class TextComparison(models.Model):
    """Store text comparison history"""
    
    COMPARISON_TYPES = [
        ('character', 'Character-by-Character'),
        ('word', 'Word-by-Word'),
        ('line', 'Line-by-Line'),
    ]
    
    text1 = models.TextField(help_text="First text for comparison")
    text2 = models.TextField(help_text="Second text for comparison")
    comparison_type = models.CharField(
        max_length=20,
        choices=COMPARISON_TYPES,
        default='character'
    )
    similarity_percentage = models.FloatField(default=0)
    differences_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Text Comparison"
        verbose_name_plural = "Text Comparisons"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Comparison - {self.get_comparison_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
