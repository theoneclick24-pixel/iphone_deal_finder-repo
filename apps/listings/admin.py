from django.contrib import admin
from .models import Listing

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        'raw_title', 
        'user', 
        'variant', 
        'city', 
        'asking_price_usd', 
        'source', 
        'battery_health_pct', 
        'screen_condition', 
        'captured_at'
    )
    list_filter = ('source', 'city', 'screen_condition', 'body_condition', 'face_id_working')
    search_fields = ('raw_title', 'city', 'user__username', 'notes')
