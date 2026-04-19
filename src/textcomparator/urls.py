from django.urls import path
from . import views

app_name = 'textcomparator'

urlpatterns = [
    path('', views.textcomparator_view, name='index'),
    path('api/compare/', views.api_compare, name='api_compare'),
]
