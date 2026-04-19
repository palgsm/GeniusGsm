from django.urls import path
from . import views

app_name = 'passwordchecker'

urlpatterns = [
    path('', views.passwordchecker_index, name='index'),
]
