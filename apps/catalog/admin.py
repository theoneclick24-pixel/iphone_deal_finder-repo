from django.contrib import admin
from .models import IPhoneModel, StorageCapacity, ColorTier, ProductVariant

@admin.register(IPhoneModel)
class IPhoneModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'release_year')
    search_fields = ('name',)

@admin.register(StorageCapacity)
class StorageCapacityAdmin(admin.ModelAdmin):
    list_display = ('gb',)
    ordering = ('gb',)

@admin.register(ColorTier)
class ColorTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_premium_tier')
    list_filter = ('is_premium_tier',)

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('iphone_model', 'storage', 'color_tier', 'base_reference_price_usd')
    list_filter = ('iphone_model', 'storage', 'color_tier')
    search_fields = ('iphone_model__name',)
