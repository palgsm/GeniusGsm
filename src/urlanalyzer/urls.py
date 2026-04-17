from django.urls import path
from . import views

app_name = 'urlanalyzer'

urlpatterns = [
    path('', views.URLAnalyzerView.as_view(), name='index'),
    path('api/analyze/', views.URLAnalyzeAPIView.as_view(), name='api_analyze'),
    path('result/<int:result_id>/', views.URLResultDetailsView.as_view(), name='result_details'),
]
