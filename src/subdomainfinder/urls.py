from django.urls import path
from . import views

app_name = 'subdomainfinder'

urlpatterns = [
    path('', views.subdomain_finder_view, name='index'),
    path('api/subdomains/', views.subdomains_api, name='subdomains_api'),
    path('api/statistics/', views.subdomain_statistics_api, name='statistics_api'),
]
