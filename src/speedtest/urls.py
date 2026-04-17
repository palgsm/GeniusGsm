from django.urls import path
from . import views

app_name = 'speedtest'

urlpatterns = [
    path('', views.SpeedTestView.as_view(), name='index'),
    path('api/test/', views.SpeedTestAPIView.as_view(), name='api_test'),
    path('api/real/', views.SpeedTestRealizeView.as_view(), name='api_real'),
    path('api/upload/', views.SpeedTestUploadView.as_view(), name='api_upload'),
    path('api/download/', views.SpeedTestDownloadView.as_view(), name='api_download'),
    path('api/ping/', views.SpeedTestPingView.as_view(), name='api_ping'),
]
