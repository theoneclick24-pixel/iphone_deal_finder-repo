from decimal import Decimal
from typing import Optional, Dict
from django.contrib.auth.models import User
from apps.adapters.facebook import FacebookMarketplaceAdapter
from apps.adapters.amazon import AmazonReferenceAdapter
from apps.catalog.models import IPhoneModel, StorageCapacity, ColorTier, ProductVariant
from apps.listings.models import Listing, SourceType, ScreenCondition
from apps.opportunities.models import Opportunity
from apps.opportunities.services import OpportunityEngine
from apps.listings.services import MarketReferenceEngine

class AnalyzeListingUseCase:
    """
    Application Layer Use Case: Coordinates analyzing a listing input from any source.
    1. Invokes Ingestion Adapter -> NormalizedListing.
    2. Matches exact domain ProductVariant.
    3. Fetches Amazon benchmark reference price (if available).
    4. Creates Listing & triggers OpportunityEngine.
    """
    @classmethod
    def execute(cls, user: User, input_text: str, city_context: str) -> Opportunity:
        # 1. Ingestion Adapter -> NormalizedListing
        normalized = FacebookMarketplaceAdapter.parse_input(input_data=input_text, city_context=city_context)

        # 2. Match exact Model & Storage
        model_name = normalized.model_name or "iPhone 11"
        storage_gb = normalized.storage_gb or 128
        color_name = normalized.color_name or "Gris Espacial / Negro"

        iphone_model_obj = IPhoneModel.objects.filter(name__icontains=model_name).first()
        if not iphone_model_obj:
            iphone_model_obj = IPhoneModel.objects.first()

        storage_obj, _ = StorageCapacity.objects.get_or_create(gb=storage_gb)
        color_obj, _ = ColorTier.objects.get_or_create(name=color_name)

        # 3. Fetch real Amazon Refurbished benchmark price for this variant
        amazon_ref_price = AmazonReferenceAdapter.get_amazon_reference_price(iphone_model_obj.name, storage_gb)

        variant, _ = ProductVariant.objects.get_or_create(
            iphone_model=iphone_model_obj,
            storage=storage_obj,
            color_tier=color_obj,
            defaults={'base_reference_price_usd': amazon_ref_price or Decimal('239.00')}
        )

        asking_price = Decimal(str(normalized.price_usd or 150.00))

        # 4. Create Listing entity
        listing = Listing.objects.create(
            user=user,
            variant=variant,
            source=SourceType.FACEBOOK,
            raw_title=normalized.raw_title[:250],
            listing_url=normalized.listing_url,
            image_url=normalized.image_url,
            city=city_context,
            asking_price_usd=asking_price,
            battery_health_pct=normalized.battery_health_pct,
            screen_condition=ScreenCondition.CRACKED if normalized.screen_condition == 'CRACKED' else ScreenCondition.INTACT,
            face_id_working=normalized.face_id_working if normalized.face_id_working is not None else True,
            camera_working=normalized.camera_working if normalized.camera_working is not None else True
        )

        # 5. Opportunity Engine
        return OpportunityEngine.evaluate_and_save_opportunity(user, listing)
