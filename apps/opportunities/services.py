from decimal import Decimal
from django.contrib.auth.models import User
from apps.listings.models import Listing
from apps.listings.services import ValuationEngine
from apps.opportunities.models import Opportunity, OpportunityStatus

class OpportunityEngine:
    """
    Phase 7 & 8: Opportunity Evaluation Engine.
    Filters listings strictly by user operational market, budget range, and profit margin.
    Applies explicit reason codes for every evaluation result.
    """
    @classmethod
    def evaluate_and_save_opportunity(cls, user: User, listing: Listing) -> Opportunity:
        profile = user.profile
        
        # Rule 1: Operational Market Isolation Check
        if not listing.is_operational_opportunity_candidate():
            opportunity, _ = Opportunity.objects.update_or_create(
                user=user,
                listing=listing,
                defaults={
                    'status': OpportunityStatus.NON_OPERATIONAL,
                    'projected_profit': Decimal('0.00'),
                    'estimated_resale_value': Decimal('0.00'),
                    'total_repairs_cost': Decimal('0.00'),
                    'explanation_code': 'NON_OPERATIONAL_CITY',
                    'explanation_text': f"Publicación en '{listing.city}'. Tu ciudad operacional configurada es '{profile.operational_city}'. Sirve como dato de referencia, no como oportunidad de compra."
                }
            )
            return opportunity

        # Rule 2: Budget Limit Check
        if listing.asking_price_usd > profile.max_budget:
            opportunity, _ = Opportunity.objects.update_or_create(
                user=user,
                listing=listing,
                defaults={
                    'status': OpportunityStatus.OVER_BUDGET,
                    'projected_profit': Decimal('0.00'),
                    'estimated_resale_value': Decimal('0.00'),
                    'total_repairs_cost': Decimal('0.00'),
                    'explanation_code': 'EXCEEDS_BUDGET',
                    'explanation_text': f"Precio pedido (${listing.asking_price_usd}) excede tu presupuesto máximo configurado de ${profile.max_budget}."
                }
            )
            return opportunity

        # Fetch baseline resale reference price from ProductVariant
        base_resale = listing.variant.base_reference_price_usd or (listing.asking_price_usd + Decimal('60.00'))

        # Rule 3: Valuation & Condition Deductions
        val = ValuationEngine.evaluate_listing_condition(listing, base_reference_resale=base_resale)
        profit = val['net_projected_profit']
        total_repairs = val['total_repairs_cost']
        est_resale = val['estimated_resale_value']
        breakdown = " | ".join(val['deductions_breakdown']) if val['deductions_breakdown'] else "Sin defectos reportados."

        # Rule 4: Profit Margin Target Check
        if profit >= profile.min_profit:
            status = OpportunityStatus.QUALIFIED
            code = "HIGH_PROFIT_DEAL" if profit >= Decimal('50.00') else "MARGIN_OK"
            explanation = f"¡Excelente oportunidad! Ganancia estimada de ${profit:.2f} (Supera tu objetivo de ${profile.min_profit}). Reventa estimada: ${est_resale:.2f}. Reparaciones: ${total_repairs:.2f} ({breakdown})."
        else:
            status = OpportunityStatus.LOW_PROFIT
            code = "BELOW_MIN_PROFIT"
            explanation = f"Ganancia estimada de ${profit:.2f} no alcanza tu margen mínimo deseado de ${profile.min_profit:.2f}."

        opportunity, _ = Opportunity.objects.update_or_create(
            user=user,
            listing=listing,
            defaults={
                'status': status,
                'projected_profit': profit,
                'estimated_resale_value': est_resale,
                'total_repairs_cost': total_repairs,
                'explanation_code': code,
                'explanation_text': explanation
            }
        )
        return opportunity
