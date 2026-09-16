from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('settings/', views.update_settings_view, name='update_settings'),
    path('import/', views.import_listing_view, name='import_listing'),
    path('api/import/', views.api_import_listing_view, name='api_import_listing'),
    path('favorite/<int:opportunity_id>/', views.toggle_favorite_view, name='toggle_favorite'),
]
