from django.urls import path
from . import views

app_name = 'textcomparator'

urlpatterns = [
    path('', views.textcomparator_view, name='index'),
    path('api/compare/', views.api_compare, name='api_compare'),
    path('api/download/', views.download_comparison_results, name='download_results'),
]
