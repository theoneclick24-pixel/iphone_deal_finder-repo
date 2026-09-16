from django.contrib import admin
from .models import Opportunity

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'status', 'projected_profit', 'explanation_code', 'is_favorite', 'created_at')
    list_filter = ('status', 'explanation_code', 'is_favorite')
    search_fields = ('user__username', 'listing__raw_title', 'explanation_code')
