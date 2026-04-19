from django.urls import path
from . import views

app_name = 'dnstools'

urlpatterns = [
    path('', views.dnstools_index, name='index'),
    path('api/query/', views.api_dns_query, name='api_query'),
]
