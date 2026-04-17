from django.urls import path
from . import views

app_name = 'iplookup'

urlpatterns = [
    path('', views.ip_info, name='ip_info_root'),
    path('<str:ip>/', views.ip_info, name='ip_info'),
]
