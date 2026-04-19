from django.urls import path
from . import views

app_name = 'domainchecker'

urlpatterns = [
    path('', views.domainchecker_index, name='index'),
    path('api/check/', views.api_check_domain, name='api_check'),
]
