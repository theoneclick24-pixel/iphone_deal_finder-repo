"""
iPhone Deal Finder — Data Capture & Normalization Prototype (Phase 1)
Validates visible field extraction from raw listing text without anti-bot evasion.
"""

import re
import json

def parse_listing_text(raw_text: str, location_hint: str = "Maturín") -> dict:
    """
    Parses a raw Marketplace listing text into a normalized domain object.
    Extracts:
    - Model (e.g., iPhone 11, iPhone 12 Pro)
    - Storage (e.g., 64GB, 128GB, 256GB)
    - Color (e.g., Silver, White, Black, Red)
    - Price (in USD)
    - Battery Health %
    - Screen condition (Scratched, Cracked, Intact)
    - Hardware defects (Face ID broken, Camera issues)
    """
    text_lower = raw_text.lower()
    
    # 1. Price extraction (e.g., $180, 180$, 180 usd, $ 180)
    price = None
    price_match = re.search(r'(?:\$|\busd\b)\s*(\d{2,4})|(\d{2,4})\s*(?:\$|\busd\b)', text_lower)
    if price_match:
        price = int(price_match.group(1) or price_match.group(2))
    
    # 2. iPhone Model extraction
    model = "iPhone (Unknown)"
    model_patterns = [
        (r'iphone\s*(15\s*pro\s*max|15\s*pro|15\s*plus|15)', "iPhone 15"),
        (r'iphone\s*(14\s*pro\s*max|14\s*pro|14\s*plus|14)', "iPhone 14"),
        (r'iphone\s*(13\s*pro\s*max|13\s*pro|13\s*mini|13)', "iPhone 13"),
        (r'iphone\s*(12\s*pro\s*max|12\s*pro|12\s*mini|12)', "iPhone 12"),
        (r'iphone\s*(11\s*pro\s*max|11\s*pro|11)', "iPhone 11"),
        (r'iphone\s*(se\s*3|se\s*2|se)', "iPhone SE"),
        (r'iphone\s*(xs\s*max|xs|xr|x)', "iPhone X"),
        (r'iphone\s*(8\s*plus|8|7\s*plus|7)', "iPhone Legacy"),
    ]
    for pattern, name in model_patterns:
        match = re.search(pattern, text_lower)
        if match:
            sub = match.group(1).title()
            model = f"iPhone {sub}"
            break
            
    # 3. Storage extraction (e.g., 64gb, 128 gb, 256g)
    storage = None
    storage_match = re.search(r'(\d{2,3})\s*(?:gb|g|gigas)', text_lower)
    if storage_match:
        storage_val = int(storage_match.group(1))
        if storage_val in [32, 64, 128, 256, 512, 1000]:
            storage = f"{storage_val}GB"
            
    # 4. Color tier
    color = "Black/Standard"
    if any(c in text_lower for c in ["plata", "silver", "blanco", "white"]):
        color = "Silver/White (Premium Tier)"
    elif any(c in text_lower for c in ["rojo", "red", "azul", "blue", "verde", "green"]):
        color = "Color/Special"
    elif any(c in text_lower for c in ["negro", "black", "space gray", "gris"]):
        color = "Black/Standard"

    # 5. Battery Health % (e.g., bateria 85%, 85% bat, bat 80)
    battery_health = None
    bat_match = re.search(r'(?:bater[ií]a|bat)\s*(?:de)?\s*(\d{2,3})%?|(\d{2,3})%\s*(?:bater[ií]a|bat)?', text_lower)
    if bat_match:
        val = bat_match.group(1) or bat_match.group(2)
        if val and 40 <= int(val) <= 100:
            battery_health = int(val)

    # 6. Screen Condition
    screen_condition = "Intact"
    if any(w in text_lower for w in ["pantalla rota", "pantalla partida", "mica partida", "pantalla mica rota"]):
        screen_condition = "Cracked / Broken Screen"
    elif any(w in text_lower for w in ["rayada", "rayaduras", "detalles esteticos en pantalla"]):
        screen_condition = "Scratched Screen"

    # 7. Hardware Defects
    defects = []
    if "face id" in text_lower and any(w in text_lower for w in ["malo", "no sirve", "sin face id", "dañado"]):
        defects.append("Face ID Broken")
    if "cámara" in text_lower or "camara" in text_lower:
        if any(w in text_lower for w in ["mala", "dañada", "mancha", "no enfoca"]):
            defects.append("Camera Defect")

    return {
        "raw_text": raw_text,
        "location": location_hint,
        "extracted": {
            "model": model,
            "storage": storage,
            "color_tier": color,
            "price_usd": price,
            "battery_health": battery_health,
            "screen_condition": screen_condition,
            "defects": defects
        }
    }


def run_prototype_tests():
    samples = [
        "iPhone 11 128gb bateria 85% pantalla impecable en Maturin $180",
        "iPhone 12 Pro 256GB bateria 78% Face ID malo detalles esteticos color blanco $240 usd",
        "iPhone 13 128 GB Bateria 90% perfecto estado color plata $250",
        "iPhone X 64gb bateria 82% camara trasera mala pantalla partida $110",
    ]

    print("=== iPhone Deal Finder: Data Capture Prototype (Phase 1) ===")
    parsed_results = []
    for sample in samples:
        res = parse_listing_text(sample)
        parsed_results.append(res)
        print(f"\nRaw: {sample}")
        print(f"Extracted: {json.dumps(res['extracted'], indent=2)}")

    return parsed_results

if __name__ == "__main__":
    run_prototype_tests()
