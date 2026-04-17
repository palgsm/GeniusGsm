from django.urls import path
from .views import blog_index, BlogListView, BlogDetailView

app_name = 'blog'

urlpatterns = [
    # Blog index/listing
    path('', blog_index, name='index'),
    path('list/', BlogListView.as_view(), name='list'),
    path('category/<slug:category_slug>/', BlogListView.as_view(), name='category'),
    
    # Individual post
    path('<slug:slug>/', BlogDetailView.as_view(), name='detail'),
]
