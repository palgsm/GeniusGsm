from django.urls import path
from . import views

app_name = 'phishingdetector'

urlpatterns = [
    path('', views.PhishingDetectorView.as_view(), name='index'),
    path('api/detect/', views.PhishingDetectorAPIView.as_view(), name='api_detect'),
]