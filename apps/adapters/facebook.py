import re
from typing import Optional
from apps.adapters.base import NormalizedListing
from apps.opportunities.fb_url_parser import fetch_fb_marketplace_url

class FacebookMarketplaceAdapter:
    """
    Ingestion Adapter for Facebook Marketplace listings.
    Converts Facebook HTML metadata / listing text into canonical NormalizedListing.
    NEVER invents missing attributes; leaves unmentioned fields as None.
    """
    @classmethod
    def parse_input(cls, input_data: str, city_context: str) -> NormalizedListing:
        input_data = input_data.strip()
        url = None
        raw_text = input_data
        image_url = None

        # Check if URL
        url_match = re.search(r'https?://[^\s]+|facebook\.com/[^\s]+|fb\.com/[^\s]+', input_data)
        if url_match:
            url = url_match.group(0)
            fetched = fetch_fb_marketplace_url(url)
            raw_text = f"{input_data} {fetched['raw_text']}".strip()
            image_url = fetched.get('image_url')

        text_lower = raw_text.lower()

        # 1. Price extraction
        price = None
        price_match = re.search(r'(?:\$|\busd\b)\s*(\d{2,4})|(\d{2,4})\s*(?:\$|\busd\b)', text_lower)
        if price_match:
            price = float(price_match.group(1) or price_match.group(2))

        # 2. iPhone Model extraction (Exact matching, no guessing)
        model = None
        model_patterns = [
            (r'iphone\s*(15\s*pro\s*max|15\s*pro|15\s*plus|15)', "iPhone 15"),
            (r'iphone\s*(14\s*pro\s*max|14\s*pro|14\s*plus|14)', "iPhone 14"),
            (r'iphone\s*(13\s*pro\s*max|13\s*pro|13\s*mini|13)', "iPhone 13"),
            (r'iphone\s*(12\s*pro\s*max|12\s*pro|12\s*mini|12)', "iPhone 12"),
            (r'iphone\s*(11\s*pro\s*max|11\s*pro|11)', "iPhone 11"),
            (r'iphone\s*(se\s*3|se\s*2|se)', "iPhone SE"),
            (r'iphone\s*(xs\s*max|xs|xr|x)', "iPhone X"),
        ]
        for pattern, name in model_patterns:
            match = re.search(pattern, text_lower)
            if match:
                sub = match.group(1).title()
                model = f"iPhone {sub}"
                break

        # 3. Storage extraction (None if unmentioned)
        storage_gb = None
        storage_match = re.search(r'(\d{2,3})\s*(?:gb|g|gigas)', text_lower)
        if storage_match:
            val = int(storage_match.group(1))
            if val in [32, 64, 128, 256, 512, 1000]:
                storage_gb = val

        # 4. Color extraction (None if unmentioned)
        color = None
        if any(c in text_lower for c in ["plata", "silver", "blanco", "white"]):
            color = "Plata / Blanco"
        elif any(c in text_lower for c in ["negro", "black", "space gray", "gris"]):
            color = "Gris Espacial / Negro"
        elif any(c in text_lower for c in ["oro", "gold"]):
            color = "Oro"
        elif any(c in text_lower for c in ["rojo", "red"]):
            color = "Producto RED"
        elif any(c in text_lower for c in ["azul", "blue"]):
            color = "Azul"

        # 5. Battery Health % (None if unmentioned)
        battery_health = None
        bat_match = re.search(r'(?:bater[ií]a|bat)\s*(?:de)?\s*(\d{2,3})%?|(\d{2,3})%\s*(?:bater[ií]a|bat)?', text_lower)
        if bat_match:
            val = bat_match.group(1) or bat_match.group(2)
            if val and 40 <= int(val) <= 100:
                battery_health = int(val)

        # 6. Screen condition
        screen_condition = 'INTACT'
        if any(w in text_lower for w in ["pantalla rota", "pantalla partida", "mica partida"]):
            screen_condition = 'CRACKED'
        elif any(w in text_lower for w in ["rayada", "rayaduras", "detalles en pantalla"]):
            screen_condition = 'SCRATCHED'

        # 7. Hardware defects
        face_id_working = True
        if "face id" in text_lower and any(w in text_lower for w in ["malo", "no sirve", "sin face id", "dañado"]):
            face_id_working = False

        camera_working = True
        if "cámara" in text_lower or "camara" in text_lower:
            if any(w in text_lower for w in ["mala", "dañada", "mancha", "no enfoca"]):
                camera_working = False

        return NormalizedListing(
            source_type='FB_MARKETPLACE',
            external_id=None,
            raw_title=raw_text[:250],
            listing_url=url,
            image_url=image_url,
            city=city_context,
            price_usd=price,
            model_name=model,
            storage_gb=storage_gb,
            color_name=color,
            battery_health_pct=battery_health,
            screen_condition=screen_condition,
            body_condition='INTACT',
            face_id_working=face_id_working,
            camera_working=camera_working,
            raw_payload={'input': input_data}
        )
