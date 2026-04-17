from django.contrib import admin
from django.utils.html import format_html
from .models import BlogPost, BlogCategory, BlogTag


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'post_count')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    def post_count(self, obj):
        count = obj.blogpost_set.filter(status='published').count()
        return format_html('<span style="color: #417690; font-weight: bold;">{}</span>', count)
    post_count.short_description = 'Published Posts'


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('posts',)
    
    def post_count(self, obj):
        count = obj.posts.filter(status='published').count()
        return count
    post_count.short_description = 'Posts'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'status_badge', 'category', 'author', 'published_date', 'views_display', 'featured_badge')
    list_filter = ('status', 'category', 'is_featured', 'published_date')
    search_fields = ('title', 'summary', 'content', 'meta_keywords')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('published_date', 'updated_date', 'views')
    
    fieldsets = (
        ('📝 Content', {
            'fields': ('title', 'slug', 'category', 'summary', 'content', 'featured_image', 'read_time'),
            'classes': ('wide',)
        }),
        ('🔍 SEO Optimization', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'canonical_url'),
            'classes': ('wide', 'collapse'),
            'description': 'Optimize for search engines'
        }),
        ('📱 Social Media', {
            'fields': ('og_title', 'og_description', 'twitter_title'),
            'classes': ('wide', 'collapse'),
            'description': 'Social media sharing optimization'
        }),
        ('✍️ Publishing', {
            'fields': ('author', 'status', 'published_date', 'updated_date'),
        }),
        ('📊 Engagement', {
            'fields': ('is_featured', 'views'),
            'description': 'Engagement tracking'
        }),
    )
    
    actions = ['make_published', 'make_draft', 'make_featured']
    
    def status_badge(self, obj):
        colors = {
            'published': '#28a745',
            'draft': '#ffc107',
            'archived': '#6c757d'
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def views_display(self, obj):
        return format_html(
            '<span style="color: #417690; font-weight: bold;">{} 👁</span>',
            obj.views
        )
    views_display.short_description = 'Views'
    
    def featured_badge(self, obj):
        if obj.is_featured:
            return format_html('<span style="color: #ff9800;">★ Featured</span>')
        return '—'
    featured_badge.short_description = 'Featured'
    
    def make_published(self, request, queryset):
        count = queryset.update(status='published')
        self.message_user(request, f'{count} posts published successfully.')
    make_published.short_description = 'Publish selected posts'
    
    def make_draft(self, request, queryset):
        count = queryset.update(status='draft')
        self.message_user(request, f'{count} posts moved to draft.')
    make_draft.short_description = 'Move to draft'
    
    def make_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} posts marked as featured.')
    make_featured.short_description = 'Mark as featured'
