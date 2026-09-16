import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.catalog.models import IPhoneModel, StorageCapacity, ColorTier, ProductVariant

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

    print("\n=== Seeding Completado Exitosamente ===")

if __name__ == "__main__":
    seed_database()
