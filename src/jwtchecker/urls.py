from django.urls import path
from . import views

app_name = 'jwtchecker'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/check/', views.check_jwt, name='check_jwt'),
]
