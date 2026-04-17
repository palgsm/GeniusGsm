from django.urls import path
from . import views

app_name = 'abusecheck'

urlpatterns = [
    path('lookup/', views.abuse_lookup_page, name='lookup'),
    path('api/<str:ip>/', views.abuse_info, name='api'),
]
