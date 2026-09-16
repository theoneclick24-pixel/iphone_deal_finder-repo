from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass
class NormalizedListing:
    """
    Canonical Listing Interface contract for all Ingestion Adapters.
    Every adapter (Facebook, WhatsApp, Amazon, Manual) MUST return this structure.
    Attributes are NULL if not explicitly present in raw data.
    """
    source_type: str                  # 'FB_MARKETPLACE', 'WHATSAPP_GROUPS', 'AMAZON_REFURBISHED', 'MANUAL_IMPORT'
    external_id: Optional[str]        # External listing ID
    raw_title: str                    # Original visible title or text
    listing_url: Optional[str]        # Direct URL
    image_url: Optional[str]          # Product image thumbnail URL
    city: str                         # City location
    price_usd: Optional[float]        # Asking price in USD (None if missing)
    model_name: Optional[str]         # Extracted model (e.g. 'iPhone 11', None if missing)
    storage_gb: Optional[int]         # Extracted storage GB (e.g. 128, None if missing)
    color_name: Optional[str]         # Extracted color (e.g. 'Plata', None if missing)
    battery_health_pct: Optional[int] # Battery health % (None if missing)
    screen_condition: str             # 'INTACT', 'SCRATCHED', 'CRACKED'
    body_condition: str               # 'INTACT', 'SCRATCHED', 'DAMAGED'
    face_id_working: Optional[bool]   # True/False/None
    camera_working: Optional[bool]    # True/False/None
    raw_payload: Dict                 # Full raw metadata for audit
