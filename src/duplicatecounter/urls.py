from django.urls import path
from . import views

app_name = 'duplicatecounter'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/count/', views.count_duplicates, name='count'),
    path('api/analyze/', views.analyze_items, name='analyze'),
]
