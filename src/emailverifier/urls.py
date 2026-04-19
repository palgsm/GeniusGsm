from django.urls import path
from . import views

app_name = 'emailverifier'

urlpatterns = [
    path('', views.emailverifier_index, name='index'),
    path('api/verify/', views.api_verify_email, name='api_verify'),
]
