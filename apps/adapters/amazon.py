from decimal import Decimal
from typing import Dict, Optional

class AmazonReferenceAdapter:
    """
    Ingestion Adapter for Amazon Refurbished benchmark reference data.
    Provides real benchmark market prices per exact (Model, Storage) variant.
    Used ONLY for computing speculation index and market reference standards.
    """
    # Real reference benchmarks for Amazon Refurbished / Renewed ($ USD)
    AMAZON_BENCHMARKS: Dict[str, Dict[int, Decimal]] = {
        "iPhone 11": {64: Decimal("209.00"), 128: Decimal("239.00"), 256: Decimal("269.00")},
        "iPhone 11 Pro": {64: Decimal("269.00"), 256: Decimal("319.00"), 512: Decimal("359.00")},
        "iPhone 12": {64: Decimal("259.00"), 128: Decimal("289.00"), 256: Decimal("329.00")},
        "iPhone 12 Pro": {128: Decimal("349.00"), 256: Decimal("399.00"), 512: Decimal("449.00")},
        "iPhone 13": {128: Decimal("379.00"), 256: Decimal("439.00"), 512: Decimal("519.00")},
        "iPhone 13 Pro": {128: Decimal("499.00"), 256: Decimal("569.00"), 512: Decimal("649.00")},
        "iPhone 14": {128: Decimal("459.00"), 256: Decimal("529.00")},
        "iPhone X": {64: Decimal("149.00"), 256: Decimal("179.00")},
    }

    @classmethod
    def get_amazon_reference_price(cls, model_name: str, storage_gb: int) -> Optional[Decimal]:
        """
        Retrieves real Amazon Refurbished benchmark price for an exact model and storage capacity.
        Returns None if no benchmark exists.
        """
        model_benchmarks = cls.AMAZON_BENCHMARKS.get(model_name)
        if model_benchmarks:
            return model_benchmarks.get(storage_gb)
        return None
