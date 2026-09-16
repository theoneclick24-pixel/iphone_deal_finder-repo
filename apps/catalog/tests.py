from django.test import TestCase
from apps.catalog.models import IPhoneModel, StorageCapacity, ColorTier, ProductVariant

class CatalogTestCase(TestCase):
    def test_catalog_variant_creation(self):
        model_11 = IPhoneModel.objects.create(name='iPhone 11', release_year=2019)
        storage_128 = StorageCapacity.objects.create(gb=128)
        color_white = ColorTier.objects.create(name='Plata / Blanco', is_premium_tier=True)

        variant = ProductVariant.objects.create(
            iphone_model=model_11,
            storage=storage_128,
            color_tier=color_white,
            base_reference_price_usd=210.00
        )

        self.assertEqual(str(variant), 'iPhone 11 128GB (Plata / Blanco)')
        self.assertEqual(variant.base_reference_price_usd, 210.00)
