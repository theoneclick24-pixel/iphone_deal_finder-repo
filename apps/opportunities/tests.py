from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.catalog.models import IPhoneModel, StorageCapacity, ColorTier, ProductVariant
from apps.listings.models import Listing, SourceType, ScreenCondition
from apps.opportunities.models import Opportunity, OpportunityStatus
from apps.opportunities.services import OpportunityEngine

class OpportunityEngineTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='demouser', password='password123')
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
        self.client = Client()

    def test_opportunity_engine_qualified_deal(self):
        listing = Listing.objects.create(
            user=self.user,
            variant=self.variant,
            source=SourceType.FACEBOOK,
            raw_title="iPhone 11 128gb blanco en Maturin $160",
            city="Maturín",
            asking_price_usd=Decimal('160.00'),
            battery_health_pct=88,
            screen_condition=ScreenCondition.INTACT
        )

        opp = OpportunityEngine.evaluate_and_save_opportunity(self.user, listing)
        self.assertEqual(opp.status, OpportunityStatus.QUALIFIED)
        self.assertTrue(opp.projected_profit >= Decimal('30.00'))
        self.assertIn('HIGH_PROFIT_DEAL', opp.explanation_code)

    def test_opportunity_engine_over_budget(self):
        listing = Listing.objects.create(
            user=self.user,
            variant=self.variant,
            source=SourceType.FACEBOOK,
            raw_title="iPhone 11 128gb en Maturin $300",
            city="Maturín",
            asking_price_usd=Decimal('300.00') # Exceeds $250 max budget
        )

        opp = OpportunityEngine.evaluate_and_save_opportunity(self.user, listing)
        self.assertEqual(opp.status, OpportunityStatus.OVER_BUDGET)
        self.assertEqual(opp.explanation_code, 'EXCEEDS_BUDGET')

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'iPhone Deal Finder')
        self.assertContains(response, 'Maturín')
