from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from apps.catalog.models import IPhoneModel, StorageCapacity, ColorTier, ProductVariant
from apps.listings.models import Listing, SourceType, ScreenCondition, BodyCondition
from apps.listings.services import ValuationEngine, MarketReferenceEngine

class ListingsAndEnginesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='trader_maturin', password='password123')
        profile = self.user.profile
        profile.operational_city = "Maturín"
        profile.min_budget = Decimal('100.00')
        profile.max_budget = Decimal('250.00')
        profile.min_profit = Decimal('30.00')
        profile.save()

        self.model_11 = IPhoneModel.objects.create(name='iPhone 11', release_year=2019)
        self.storage_128 = StorageCapacity.objects.create(gb=128)
        self.color_white = ColorTier.objects.create(name='Plata / Blanco', is_premium_tier=True)

        self.variant = ProductVariant.objects.create(
            iphone_model=self.model_11,
            storage=self.storage_128,
            color_tier=self.color_white,
            base_reference_price_usd=Decimal('220.00')
        )

    def test_operational_market_vs_reference_rule(self):
        # 1. Operational listing from Maturin
        maturin_listing = Listing.objects.create(
            user=self.user,
            variant=self.variant,
            source=SourceType.FACEBOOK,
            raw_title="iPhone 11 128gb blanco impecable",
            city="Maturín",
            asking_price_usd=Decimal('180.00')
        )
        self.assertTrue(maturin_listing.is_operational_opportunity_candidate())

        # 2. Reference listing from Caracas (MUST return False for operational opportunity)
        caracas_listing = Listing.objects.create(
            user=self.user,
            variant=self.variant,
            source=SourceType.FACEBOOK,
            raw_title="iPhone 11 128gb ofertisima Caracas",
            city="Caracas",
            asking_price_usd=Decimal('130.00') # Cheap price, but non-operational city!
        )
        self.assertFalse(caracas_listing.is_operational_opportunity_candidate())

    def test_valuation_engine_condition_deductions(self):
        listing = Listing.objects.create(
            user=self.user,
            variant=self.variant,
            source=SourceType.FACEBOOK,
            raw_title="iPhone 11 128gb bat 75% pantalla partida Face ID malo",
            city="Maturín",
            asking_price_usd=Decimal('100.00'),
            battery_health_pct=75, # $25 repair
            screen_condition=ScreenCondition.CRACKED, # $45 repair
            face_id_working=False # $35 repair
            # Total repairs = $105
        )

        res = ValuationEngine.evaluate_listing_condition(listing, base_reference_resale=Decimal('220.00'))
        self.assertEqual(res['total_repairs_cost'], Decimal('105.00'))
        self.assertEqual(len(res['deductions_breakdown']), 3)

    def test_market_reference_engine_stats_and_speculation(self):
        # Seed 4 listings in Maturin: $180, $200, $210, $250
        prices = [180.00, 200.00, 210.00, 250.00]
        for p in prices:
            Listing.objects.create(
                user=self.user,
                variant=self.variant,
                source=SourceType.FACEBOOK,
                raw_title=f"iPhone 11 ${p}",
                city="Maturín",
                asking_price_usd=Decimal(str(p))
            )

        stats = MarketReferenceEngine.compute_market_stats(self.model_11, self.storage_128, city_filter="Maturín")
        self.assertEqual(stats['sample_count'], 4)
        self.assertEqual(stats['average_price'], 210.0)
        self.assertEqual(stats['median_price'], 205.0)
        self.assertEqual(stats['amazon_reference_price'], 220.0)
        self.assertEqual(stats['speculation_index'], 0.93)
