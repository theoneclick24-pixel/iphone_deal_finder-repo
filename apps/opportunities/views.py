import json
import re
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from apps.catalog.models import IPhoneModel, StorageCapacity, ColorTier, ProductVariant
from apps.listings.models import Listing, SourceType, ScreenCondition
from apps.opportunities.models import Opportunity, OpportunityStatus
from apps.opportunities.services import OpportunityEngine
from apps.opportunities.fb_url_parser import fetch_fb_marketplace_url
from prototype_fb_capture import parse_listing_text

def get_demo_user():
    """Helper to retrieve or create the active demo user for MVP."""
    user, _ = User.objects.get_or_create(username='demouser', defaults={'email': 'demo@iphonedealfinder.local'})
    return user

def dashboard_view(request):
    """
    Phase 8: User Private Dashboard.
    Displays opportunity cards, active filters, metrics header, and URL/Text import modal.
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


def update_settings_view(request):
    """
    Allows user to update operational city, budget limits, and profit targets in real time.
    """
    user = get_demo_user()
    profile = user.profile

    if request.method == 'POST':
        city = request.POST.get('operational_city', '').strip()
        min_b = request.POST.get('min_budget', '100')
        max_b = request.POST.get('max_budget', '250')
        min_p = request.POST.get('min_profit', '30')

        if city:
            profile.operational_city = city
        profile.min_budget = Decimal(min_b)
        profile.max_budget = Decimal(max_b)
        profile.min_profit = Decimal(min_p)
        profile.save()

        # Re-evaluate existing listings with new settings
        for listing in Listing.objects.filter(user=user):
            OpportunityEngine.evaluate_and_save_opportunity(user, listing)

    return redirect('dashboard')


def process_listing_input(user, input_text: str, city: str, explicit_url: str = None) -> Opportunity:
    """
    Intelligent processor:
    Checks if input_text is a URL or contains a URL.
    If it's a URL, fetches metadata automatically from Facebook.
    Extracts attributes and generates an evaluated Opportunity.
    """
    input_text = input_text.strip()
    target_url = explicit_url
    raw_text_to_parse = input_text

    # URL Detection
    url_match = re.search(r'https?://[^\s]+|facebook\.com/[^\s]+|fb\.com/[^\s]+', input_text)
    if url_match:
        target_url = url_match.group(0)
        # Fetch metadata from Facebook URL
        fetched = fetch_fb_marketplace_url(target_url)
        raw_text_to_parse = f"{input_text} {fetched['raw_text']}"

    parsed = parse_listing_text(raw_text_to_parse, location_hint=city)
    extracted = parsed['extracted']

    # Match iPhone Model
    iphone_model_obj = IPhoneModel.objects.filter(name__icontains=extracted['model']).first()
    if not iphone_model_obj:
        iphone_model_obj = IPhoneModel.objects.first()

    storage_gb = int(extracted['storage'].replace('GB', '')) if extracted['storage'] else 128
    storage_obj, _ = StorageCapacity.objects.get_or_create(gb=storage_gb)

    is_premium = "Silver" in extracted['color_tier'] or "White" in extracted['color_tier']
    color_obj = ColorTier.objects.filter(is_premium_tier=is_premium).first() or ColorTier.objects.first()

    # Base reference price
    asking = Decimal(str(extracted['price_usd'] or 150))
    variant, _ = ProductVariant.objects.get_or_create(
        iphone_model=iphone_model_obj,
        storage=storage_obj,
        color_tier=color_obj,
        defaults={'base_reference_price_usd': asking + Decimal('60.00')}
    )

    # Create listing
    listing = Listing.objects.create(
        user=user,
        variant=variant,
        source=SourceType.FACEBOOK,
        raw_title=raw_text_to_parse[:250],
        listing_url=target_url,
        city=city,
        asking_price_usd=asking,
        battery_health_pct=extracted['battery_health'],
        screen_condition=ScreenCondition.CRACKED if extracted['screen_condition'] == 'Cracked / Broken Screen' else ScreenCondition.INTACT,
        face_id_working='Face ID Broken' not in extracted['defects'],
        camera_working='Camera Defect' not in extracted['defects']
    )

    # Evaluate opportunity
    return OpportunityEngine.evaluate_and_save_opportunity(user, listing)


def import_listing_view(request):
    """View to import listings from pasted URL or text description."""
    user = get_demo_user()

    if request.method == 'POST':
        raw_input = request.POST.get('raw_text', '').strip()
        city = request.POST.get('city', user.profile.operational_city).strip()
        listing_url = request.POST.get('listing_url', '').strip() or None

        if raw_input or listing_url:
            process_listing_input(user, raw_input or listing_url, city, explicit_url=listing_url)

        return redirect('dashboard')

    return render(request, 'dashboard/import_listing.html')


@csrf_exempt
def api_import_listing_view(request):
    """
    API Endpoint for Bookmarklet or Extension. Accepts URL or text and auto-fetches data.
    """
    user = get_demo_user()

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST

        raw_text = data.get('raw_text', '') or data.get('url', '')
        city = data.get('city', user.profile.operational_city)
        url = data.get('url', None)

        if not raw_text and not url:
            return JsonResponse({'status': 'error', 'message': 'No text or URL provided'}, status=400)

        opportunity = process_listing_input(user, raw_text or url, city, explicit_url=url)

        return JsonResponse({
            'status': 'success',
            'opportunity_id': opportunity.id,
            'opportunity_status': opportunity.get_status_display(),
            'projected_profit': float(opportunity.projected_profit),
            'explanation': opportunity.explanation_text
        })

    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)


def toggle_favorite_view(request, opportunity_id):
    """Toggles favorite/saved status on an opportunity."""
    user = get_demo_user()
    opportunity = get_object_or_404(Opportunity, id=opportunity_id, user=user)
    opportunity.is_favorite = not opportunity.is_favorite
    opportunity.save()
    return redirect('dashboard')
