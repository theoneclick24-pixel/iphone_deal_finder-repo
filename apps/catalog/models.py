from django.db import models

class IPhoneModel(models.Model):
    """
    Standardized iPhone Model Catalog (shared reference across tenants).
    e.g., iPhone 11, iPhone 12 Pro, iPhone 13, iPhone 14 Pro Max.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Nombre exacto del modelo de iPhone.")
    release_year = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Modelo de iPhone"
        verbose_name_plural = "Modelos de iPhone"
        ordering = ['name']

    def __str__(self):
        return self.name


class StorageCapacity(models.Model):
    """
    Storage capacity in GB (e.g. 64, 128, 256, 512).
    """
    gb = models.IntegerField(unique=True, help_text="Capacidad de almacenamiento en Gigabytes (GB).")

    class Meta:
        verbose_name = "Capacidad de Almacenamiento"
        verbose_name_plural = "Capacidades de Almacenamiento"
        ordering = ['gb']

    def __str__(self):
        return f"{self.gb}GB"


class ColorTier(models.Model):
    """
    Color tier classification (Silver/White preferred vs Black common).
    """
    name = models.CharField(max_length=50, unique=True)
    is_premium_tier = models.BooleanField(
        default=False, 
        help_text="Indica si es un color de alta demanda (ej. Blanco / Plata)."
    )

    class Meta:
        verbose_name = "Clasificación de Color"
        verbose_name_plural = "Clasificaciones de Color"

    def __str__(self):
        premium_label = " (Alta Demanda)" if self.is_premium_tier else ""
        return f"{self.name}{premium_label}"


class ProductVariant(models.Model):
    """
    Exact combination of Model + Storage + Color Tier.
    Forms the baseline for reference pricing and valuations.
    """
    iphone_model = models.ForeignKey(IPhoneModel, on_delete=models.CASCADE, related_name='variants')
    storage = models.ForeignKey(StorageCapacity, on_delete=models.CASCADE, related_name='variants')
    color_tier = models.ForeignKey(ColorTier, on_delete=models.CASCADE, related_name='variants')
    base_reference_price_usd = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Precio de referencia base global o de Amazon Used ($)."
    )

    class Meta:
        unique_together = ('iphone_model', 'storage', 'color_tier')
        verbose_name = "Variante de Producto"
        verbose_name_plural = "Variantes de Producto"

    def __str__(self):
        return f"{self.iphone_model.name} {self.storage.gb}GB ({self.color_tier.name})"
