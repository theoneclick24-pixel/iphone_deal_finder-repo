import numpy as np
from decimal import Decimal
from typing import Dict, List, Optional
from django.db.models import Avg, Min, Max
from apps.listings.models import Listing, ScreenCondition, BodyCondition
from apps.catalog.models import ProductVariant, IPhoneModel, StorageCapacity

class ValuationEngine:
    """
    Phase 5 & 7: Condition Deductions & Fair Valuation Engine.
    Calculates repair cost deductions, estimated resale value, and projected net profit.
    """
    # Evidence-based configurable default costs ($ USD)
    DEFAULT_REPAIR_COSTS = {
        'battery_replacement': Decimal('25.00'),   # Battery health < 80%
        'cracked_screen': Decimal('45.00'),        # Broken screen
        'scratched_screen': Decimal('15.00'),      # Minor screen scratches
        'face_id_repair': Decimal('35.00'),        # Broken Face ID
        'camera_repair': Decimal('40.00'),         # Broken main/front camera
        'body_damage': Decimal('20.00'),           # Heavy body denting/scratches
    }

    @classmethod
    def evaluate_listing_condition(cls, listing: Listing, base_reference_resale: Decimal) -> Dict:
        """
        Calculates total repair deductions and net estimated resale value.
        """
        if not isinstance(base_reference_resale, Decimal):
            base_reference_resale = Decimal(str(base_reference_resale))

        total_repairs = Decimal('0.00')
        deductions_breakdown = []

        # 1. Battery Health deduction (<80%)
        if listing.battery_health_pct is not None and listing.battery_health_pct < 80:
            cost = cls.DEFAULT_REPAIR_COSTS['battery_replacement']
            total_repairs += cost
            deductions_breakdown.append(f"Batería en {listing.battery_health_pct}% (<80%): -${cost}")

        # 2. Screen condition
        if listing.screen_condition == ScreenCondition.CRACKED:
            cost = cls.DEFAULT_REPAIR_COSTS['cracked_screen']
            total_repairs += cost
            deductions_breakdown.append(f"Pantalla/Mica rota: -${cost}")
        elif listing.screen_condition == ScreenCondition.SCRATCHED:
            cost = cls.DEFAULT_REPAIR_COSTS['scratched_screen']
            total_repairs += cost
            deductions_breakdown.append(f"Pantalla rayada: -${cost}")

        # 3. Hardware defects
        if not listing.face_id_working:
            cost = cls.DEFAULT_REPAIR_COSTS['face_id_repair']
            total_repairs += cost
            deductions_breakdown.append(f"Face ID no funciona: -${cost}")

        if not listing.camera_working:
            cost = cls.DEFAULT_REPAIR_COSTS['camera_repair']
            total_repairs += cost
            deductions_breakdown.append(f"Falla de cámara: -${cost}")

        # 4. Body condition
        if listing.body_condition == BodyCondition.DAMAGED:
            cost = cls.DEFAULT_REPAIR_COSTS['body_damage']
            total_repairs += cost
            deductions_breakdown.append(f"Detalles severos en chasis: -${cost}")

        # Fair estimated resale = Base Reference Price - Screen/Body/Defect discounts
        estimated_resale_value = max(Decimal('0.00'), base_reference_resale - (total_repairs * Decimal('0.5')))
        
        asking_price = Decimal(str(listing.asking_price_usd))
        
        # Net profit = Estimated Resale Value - Purchase Price - Total Repair Costs
        net_projected_profit = estimated_resale_value - asking_price - total_repairs

        return {
            "asking_price": asking_price,
            "base_reference_resale": base_reference_resale,
            "total_repairs_cost": total_repairs,
            "estimated_resale_value": estimated_resale_value,
            "net_projected_profit": net_projected_profit,
            "deductions_breakdown": deductions_breakdown,
        }


class MarketReferenceEngine:
    """
    Phase 6: Market Statistics & Speculation Index Engine.
    Computes Averages, Medians, P25, P75, and Amazon Speculation Index.
    """
    @classmethod
    def compute_market_stats(cls, iphone_model: IPhoneModel, storage: StorageCapacity, city_filter: Optional[str] = None) -> Dict:
        """
        Calculates reference statistics for a given exact model and storage capacity.
        Separates operational city observations from reference city observations.
        """
        query = Listing.objects.filter(
            variant__iphone_model=iphone_model,
            variant__storage=storage
        )
        if city_filter:
            query = query.filter(city__icontains=city_filter)

        prices = [float(price) for price in query.values_list('asking_price_usd', flat=True)]

        if not prices:
            return {
                "sample_count": 0,
                "average_price": 0.0,
                "median_price": 0.0,
                "p25": 0.0,
                "p75": 0.0,
                "min_price": 0.0,
                "max_price": 0.0,
                "speculation_index": 1.0,
            }

        avg_price = float(np.mean(prices))
        median_price = float(np.median(prices))
        p25 = float(np.percentile(prices, 25))
        p75 = float(np.percentile(prices, 75))
        min_p = float(np.min(prices))
        max_p = float(np.max(prices))

        # Fetch Amazon baseline reference price if present
        variant = ProductVariant.objects.filter(iphone_model=iphone_model, storage=storage).first()
        amazon_price = float(variant.base_reference_price_usd) if (variant and variant.base_reference_price_usd) else None

        # Speculation index: local median vs amazon price
        speculation_index = round(median_price / amazon_price, 2) if (amazon_price and amazon_price > 0) else 1.00

        return {
            "sample_count": len(prices),
            "average_price": round(avg_price, 2),
            "median_price": round(median_price, 2),
            "p25": round(p25, 2),
            "p75": round(p75, 2),
            "min_price": round(min_p, 2),
            "max_price": round(max_p, 2),
            "amazon_reference_price": amazon_price,
            "speculation_index": speculation_index,
        }
