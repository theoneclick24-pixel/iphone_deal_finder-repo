from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('import/', views.import_listing_view, name='import_listing'),
    path('favorite/<int:opportunity_id>/', views.toggle_favorite_view, name='toggle_favorite'),
]
