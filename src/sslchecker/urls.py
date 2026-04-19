from django.urls import path
from . import views

app_name = 'sslchecker'

urlpatterns = [
    path('', views.sslchecker_index, name='index'),
]
