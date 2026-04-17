from django.urls import path
from . import views

app_name = 'randomlines'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/randomize/', views.randomize_lines, name='randomize'),
    path('api/reverse/', views.reverse_lines, name='reverse'),
    path('api/remove-empty/', views.remove_empty, name='remove_empty'),
    path('api/remove-duplicates/', views.remove_duplicates, name='remove_duplicates'),
    path('api/sort-ascending/', views.sort_ascending, name='sort_ascending'),
    path('api/sort-descending/', views.sort_descending, name='sort_descending'),
]
