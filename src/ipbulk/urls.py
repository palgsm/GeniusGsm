from django.urls import path
from . import views

app_name = 'ipbulk'

urlpatterns = [
    # Groups
    path('groups/', views.IPGroupListView.as_view(), name='group_list'),
    path('groups/<int:pk>/', views.IPGroupDetailView.as_view(), name='group_detail'),
    path('groups/create/', views.IPGroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/delete/', views.IPGroupDeleteView.as_view(), name='group_delete'),
    
    # Import
    path('import/', views.bulk_import_view, name='bulk_import'),
    path('groups/<int:group_id>/add-range/', views.add_ip_range_view, name='add_range'),
    path('ranges/<int:pk>/delete/', views.delete_ip_range_view, name='delete_range'),
    
    # IP Lookup
    path('bulk-lookup/', views.bulk_ip_lookup_view, name='bulk_lookup'),
    
    # # Search  
    path('by-country/', views.country_ranges_view, name='by_country'),
    
    # # Verify  IP
    path('check-ip/', views.check_ip_view, name='check_ip'),
]
