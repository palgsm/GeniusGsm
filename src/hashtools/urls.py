from django.urls import path
from . import views

app_name = 'hashtools'

urlpatterns = [
    path('', views.hashtools_index, name='index'),
    path('api/hash/', views.api_hash, name='api_hash'),
    path('api/encode/', views.api_encode, name='api_encode'),
]
