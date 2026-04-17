from django.urls import path
from . import views

app_name = 'shortenerexpander'

urlpatterns = [
    path('', views.ShortenerExpanderView.as_view(), name='index'),
    path('api/expand/', views.ShortenerExpanderAPIView.as_view(), name='api_expand'),
]
