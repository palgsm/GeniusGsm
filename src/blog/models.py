from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class BlogCategory(models.Model):
    """Blog categories for organizing posts"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='📝', help_text="Emoji icon for category")
    
    class Meta:
        verbose_name_plural = "Blog Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """Blog posts with full SEO optimization"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    # Content
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    summary = models.TextField(max_length=500, help_text="Brief summary for listings and meta description")
    featured_image = models.ImageField(upload_to='blog/featured/', blank=True)
    
    # SEO Fields
    meta_title = models.CharField(
        max_length=70,
        help_text="Page title (50-60 chars recommended)"
    )
    meta_description = models.CharField(
        max_length=160,
        help_text="Meta description (150-160 chars)"
    )
    meta_keywords = models.CharField(
        max_length=200,
        help_text="Keywords separated by commas"
    )
    canonical_url = models.URLField(blank=True)
    
    # Social Media
    og_title = models.CharField(max_length=100, blank=True)
    og_description = models.CharField(max_length=160, blank=True)
    twitter_title = models.CharField(max_length=70, blank=True)
    
    # Publishing
    author = models.CharField(max_length=100, default="GeniusGsm Team")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    # Engagement
    views = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False, help_text="Show on homepage")
    read_time = models.PositiveIntegerField(default=5, help_text="Estimated reading time in minutes")
    
    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['-published_date']),
            models.Index(fields=['status', '-published_date']),
            models.Index(fields=['category', '-published_date']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-generate slug
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-generate OG fields if empty
        if not self.og_title:
            self.og_title = self.meta_title[:100]
        if not self.og_description:
            self.og_description = self.meta_description
        if not self.twitter_title:
            self.twitter_title = self.meta_title[:70]
        if not self.canonical_url:
            self.canonical_url = f"https://geniusgsm.com/blog/{self.slug}/"
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})
    
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])


class BlogTag(models.Model):
    """Tags for blog posts (for better SEO)"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    posts = models.ManyToManyField(BlogPost, related_name='tags', blank=True)
    
    class Meta:
        verbose_name_plural = "Blog Tags"
        ordering = ['name']
    
    def __str__(self):
        return self.name
