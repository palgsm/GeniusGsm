from django.urls import path
from . import views

app_name = 'linkpreview'

urlpatterns = [
    path('', views.LinkPreviewView.as_view(), name='index'),
    path('api/preview/', views.LinkPreviewAPIView.as_view(), name='api_preview'),
]