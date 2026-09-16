from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'operational_city', 'min_budget', 'max_budget', 'min_profit', 'updated_at')
    search_fields = ('user__username', 'user__email', 'operational_city')
    list_filter = ('operational_city',)
