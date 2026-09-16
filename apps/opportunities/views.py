from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from apps.catalog.models import IPhoneModel, StorageCapacity, ColorTier, ProductVariant
from apps.listings.models import Listing, SourceType, ScreenCondition, BodyCondition
from apps.opportunities.models import Opportunity, OpportunityStatus
from apps.opportunities.services import OpportunityEngine
from prototype_fb_capture import parse_listing_text

def get_demo_user():
    """Helper to retrieve or create the active demo user for MVP."""
    user, _ = User.objects.get_or_create(username='demouser', defaults={'email': 'demo@iphonedealfinder.local'})
    return user

def dashboard_view(request):
    """
    Phase 8: User Private Dashboard.
    Displays opportunity cards, active filters, metrics header, and manual/assisted listing import modal.
    """
    user = get_demo_user()
    profile = user.profile

    # Filters
    status_filter = request.GET.get('status', 'QUALIFIED')
    model_filter = request.GET.get('model', '')

    opportunities = Opportunity.objects.filter(user=user)

    if status_filter and status_filter != 'ALL':
        opportunities = opportunities.filter(status=status_filter)
    if model_filter:
        opportunities = opportunities.filter(listing__variant__iphone_model__id=model_filter)

    # Metrics
    total_opportunities = Opportunity.objects.filter(user=user, status=OpportunityStatus.QUALIFIED).count()
    total_saved = Opportunity.objects.filter(user=user, is_favorite=True).count()
    
    # Calculate average projected profit for qualified deals
    qualified_deals = Opportunity.objects.filter(user=user, status=OpportunityStatus.QUALIFIED)
    avg_profit = float(sum(op.projected_profit for op in qualified_deals) / qualified_deals.count()) if qualified_deals.exists() else 0.0

    models = IPhoneModel.objects.all()

    context = {
        'user': user,
        'profile': profile,
        'opportunities': opportunities,
        'total_opportunities': total_opportunities,
        'total_saved': total_saved,
        'avg_profit': round(avg_profit, 2),
        'status_filter': status_filter,
        'models': models,
    }
    return render(request, 'dashboard/index.html', context)


def import_listing_view(request):
    """
    Fast manual or text-paste import view that uses prototype_fb_capture
    to extract fields and evaluate the deal in 1 step.
    """
    user = get_demo_user()

    if request.method == 'POST':
        raw_text = request.POST.get('raw_text', '').strip()
        city = request.POST.get('city', user.profile.operational_city).strip()
        
        if raw_text:
            parsed = parse_listing_text(raw_text, location_hint=city)
            extracted = parsed['extracted']

            # Match or fallback to catalog
            iphone_model_obj = IPhoneModel.objects.filter(name__icontains=extracted['model']).first()
            if not iphone_model_obj:
                iphone_model_obj = IPhoneModel.objects.first()

            storage_gb = int(extracted['storage'].replace('GB', '')) if extracted['storage'] else 128
            storage_obj, _ = StorageCapacity.objects.get_or_create(gb=storage_gb)

            is_premium = "Silver" in extracted['color_tier']
            color_obj = ColorTier.objects.filter(is_premium_tier=is_premium).first() or ColorTier.objects.first()

            # Product Variant
            variant, _ = ProductVariant.objects.get_or_create(
                iphone_model=iphone_model_obj,
                storage=storage_obj,
                color_tier=color_obj,
                defaults={'base_reference_price_usd': Decimal(str(extracted['price_usd'] or 200)) + Decimal('60.00')}
            )

            # Create Listing
            listing = Listing.objects.create(
                user=user,
                variant=variant,
                source=SourceType.FACEBOOK,
                raw_title=raw_text[:250],
                city=city,
                asking_price_usd=Decimal(str(extracted['price_usd'] or 150)),
                battery_health_pct=extracted['battery_health'],
                screen_condition=ScreenCondition.CRACKED if extracted['screen_condition'] == 'Cracked / Broken Screen' else ScreenCondition.INTACT,
                face_id_working='Face ID Broken' not in extracted['defects'],
                camera_working='Camera Defect' not in extracted['defects']
            )

            # Evaluate Opportunity
            OpportunityEngine.evaluate_and_save_opportunity(user, listing)

        return redirect('dashboard')

    return render(request, 'dashboard/import_listing.html')


def toggle_favorite_view(request, opportunity_id):
    """Toggles favorite/saved status on an opportunity."""
    user = get_demo_user()
    opportunity = get_object_or_404(Opportunity, id=opportunity_id, user=user)
    opportunity.is_favorite = not opportunity.is_favorite
    opportunity.save()
    return redirect('dashboard')
