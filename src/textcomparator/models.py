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
        return f"Comparison ({self.comparison_type}) - {self.similarity_percentage}% similar"


class MultiFileComparison(models.Model):
    """Store multi-file comparison history (1 file with multiple files)"""
    
    COMPARISON_TYPES = [
        ('character', 'Character-by-Character'),
        ('word', 'Word-by-Word'),
        ('line', 'Line-by-Line'),
    ]
    
    base_file_name = models.CharField(max_length=255, help_text="Name of the base file")
    comparison_file_names = models.TextField(help_text="Comma-separated names of files compared against")
    comparison_type = models.CharField(
        max_length=20,
        choices=COMPARISON_TYPES,
        default='character'
    )
    total_files = models.IntegerField(default=2, help_text="Total number of files compared")
    similarity_data = models.JSONField(default=dict, help_text="Dictionary of file names to similarity percentages")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Multi-File Comparison"
        verbose_name_plural = "Multi-File Comparisons"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Multi-File Comparison: {self.base_file_name} vs {self.total_files-1} files"
    
    def __str__(self):
        return f"Comparison - {self.get_comparison_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
