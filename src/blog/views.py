from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BlogPost, BlogCategory, BlogTag


class BlogListView(ListView):
    """Display all published blog posts with pagination"""
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(status='published').select_related('category')
        
        # Filter by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Search
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(summary__icontains=query) |
                Q(content__icontains=query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.all()
        context['featured_posts'] = BlogPost.objects.filter(
            status='published', is_featured=True
        )[:3]
        
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(BlogCategory, slug=category_slug)
        
        return context


class BlogDetailView(DetailView):
    """Display a single blog post"""
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    
    def get_queryset(self):
        return BlogPost.objects.filter(status='published')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        
        # Increment views
        post.increment_views()
        
        # Related posts (same category)
        context['related_posts'] = BlogPost.objects.filter(
            status='published',
            category=post.category
        ).exclude(pk=post.pk)[:3]
        
        return context


def blog_index(request):
    """Blog index page (alternative to ListView)"""
    posts = BlogPost.objects.filter(status='published').select_related('category')
    categories = BlogCategory.objects.all()
    featured_posts = BlogPost.objects.filter(status='published', is_featured=True)[:3]
    
    # Pagination
    paginator = Paginator(posts, 10)
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)
    
    context = {
        'posts': posts,
        'categories': categories,
        'featured_posts': featured_posts,
    }
    
    return render(request, 'blog/post_list.html', context)
