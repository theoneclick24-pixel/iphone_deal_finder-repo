import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.catalog.models import IPhoneModel, StorageCapacity, ColorTier, ProductVariant
from apps.listings.models import Listing, SourceType, ScreenCondition
from apps.opportunities.services import OpportunityEngine

def seed_database():
    print("=== Seeding iPhone Deal Finder Catalog & Initial Data ===")

    # 1. Models
    models_data = [
        ("iPhone X", 2017),
        ("iPhone XR", 2018),
        ("iPhone XS", 2018),
        ("iPhone XS Max", 2018),
        ("iPhone 11", 2019),
        ("iPhone 11 Pro", 2019),
        ("iPhone 11 Pro Max", 2019),
        ("iPhone SE (2nd Gen)", 2020),
        ("iPhone 12", 2020),
        ("iPhone 12 Mini", 2020),
        ("iPhone 12 Pro", 2020),
        ("iPhone 12 Pro Max", 2020),
        ("iPhone 13", 2021),
        ("iPhone 13 Mini", 2021),
        ("iPhone 13 Pro", 2021),
        ("iPhone 13 Pro Max", 2021),
        ("iPhone 14", 2022),
        ("iPhone 14 Plus", 2022),
        ("iPhone 14 Pro", 2022),
        ("iPhone 14 Pro Max", 2022),
        ("iPhone 15", 2023),
        ("iPhone 15 Pro", 2023),
    ]
    for model_name, year in models_data:
        IPhoneModel.objects.get_or_create(name=model_name, defaults={'release_year': year})
    print(f"[OK] {len(models_data)} modelos de iPhone creados/verificados.")

    # 2. Storage capacities
    capacities = [64, 128, 256, 512, 1000]
    for gb in capacities:
        StorageCapacity.objects.get_or_create(gb=gb)
    print(f"[OK] {len(capacities)} capacidades de almacenamiento (GB) creadas.")

    # 3. Colors
    colors = [
        ("Plata / Blanco", True),
        ("Gris Espacial / Negro", False),
        ("Oro", True),
        ("Azul", False),
        ("Verde / Alpine", False),
        ("Producto RED", False),
        ("Morado", False),
    ]
    for color_name, is_premium in colors:
        ColorTier.objects.get_or_create(name=color_name, defaults={'is_premium_tier': is_premium})
    print(f"[OK] {len(colors)} clasificaciones de color creadas.")

    # 4. Default Demo User
    user, created = User.objects.get_or_create(
        username="demouser",
        defaults={'email': 'demo@iphonedealfinder.local', 'is_staff': True}
    )
    if created:
        user.set_password("demo12345")
        user.save()
        print("[OK] Usuario demo 'demouser' creado con éxito.")

    profile = user.profile
    profile.operational_city = "Maturín"
    profile.min_budget = 100.00
    profile.max_budget = 250.00
    profile.min_profit = 35.00
    profile.save()
    print(f"[OK] Perfil configurado: Ciudad = {profile.operational_city}, Rango = ${profile.min_budget}-${profile.max_budget}, Ganancia Mínima = ${profile.min_profit}")

    # 5. Create Sample Listings & Evaluate Opportunities
    model_11 = IPhoneModel.objects.filter(name="iPhone 11").first()
    storage_128 = StorageCapacity.objects.filter(gb=128).first()
    color_white = ColorTier.objects.filter(is_premium_tier=True).first()

    if model_11 and storage_128 and color_white:
        variant, _ = ProductVariant.objects.get_or_create(
            iphone_model=model_11,
            storage=storage_128,
            color_tier=color_white,
            defaults={'base_reference_price_usd': 220.00}
        )

        sample_listings = [
            ("iPhone 11 128GB Plata bateria 88% impecable en Maturin $160", "Maturín", 160.00, 88, ScreenCondition.INTACT, True, True),
            ("iPhone 11 128GB Negro bateria 75% pantalla mica partida Maturin $130", "Maturín", 130.00, 75, ScreenCondition.CRACKED, True, True),
            ("iPhone 11 128GB Blanco impecable Caracas $140", "Caracas", 140.00, 92, ScreenCondition.INTACT, True, True),
        ]

        for raw, city, price, bat, screen, face, cam in sample_listings:
            listing, _ = Listing.objects.get_or_create(
                user=user,
                raw_title=raw,
                defaults={
                    'variant': variant,
                    'source': SourceType.FACEBOOK,
                    'city': city,
                    'asking_price_usd': price,
                    'battery_health_pct': bat,
                    'screen_condition': screen,
                    'face_id_working': face,
                    'camera_working': cam
                }
            )
            OpportunityEngine.evaluate_and_save_opportunity(user, listing)

        print("[OK] Oportunidades de prueba evaluadas y registradas para el usuario demo.")

    print("\n=== Seeding Completado Exitosamente ===")

if __name__ == "__main__":
    seed_database()
