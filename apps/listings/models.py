from django.db import models
from django.contrib.auth.models import User
from apps.catalog.models import ProductVariant

class SourceType(models.TextChoices):
    FACEBOOK = 'FB_MARKETPLACE', 'Facebook Marketplace'
    WHATSAPP = 'WHATSAPP_GROUPS', 'Grupos / Estados de WhatsApp'
    AMAZON = 'AMAZON_REFURBISHED', 'Amazon Refurbished (Referencia)'
    MANUAL = 'MANUAL_IMPORT', 'Importación Manual'

class ScreenCondition(models.TextChoices):
    INTACT = 'INTACT', 'Intacta / Impecable'
    SCRATCHED = 'SCRATCHED', 'Con Rayaduras'
    CRACKED = 'CRACKED', 'Pantalla / Mica Rota'

class BodyCondition(models.TextChoices):
    INTACT = 'INTACT', 'Impecable'
    SCRATCHED = 'SCRATCHED', 'Detalles Estéticos / Rayones'
    DAMAGED = 'DAMAGED', 'Golpeado / Abollado'

class Listing(models.Model):
    """
    Represents a raw or captured iPhone listing from any source.
    Keeps strict separation between Operational City candidates and Reference Data.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='listings',
        help_text="Usuario propietario de la publicación."
    )
    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.CASCADE, 
        related_name='listings',
        help_text="Variante exacta de iPhone (Modelo + Almacenamiento + Color)."
    )
    source = models.CharField(
        max_length=50, 
        choices=SourceType.choices, 
        default=SourceType.FACEBOOK
    )
    raw_title = models.CharField(max_length=255)
    listing_url = models.URLField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=100, help_text="Ciudad de origen de la publicación.")
    asking_price_usd = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio pedido ($ USD).")
    
    # Condition & Defects
    battery_health_pct = models.IntegerField(null=True, blank=True, help_text="Porcentaje de salud de batería (%).")
    screen_condition = models.CharField(
        max_length=20, 
        choices=ScreenCondition.choices, 
        default=ScreenCondition.INTACT
    )
    body_condition = models.CharField(
        max_length=20, 
        choices=BodyCondition.choices, 
        default=BodyCondition.INTACT
    )
    face_id_working = models.BooleanField(default=True, help_text="¿Face ID / Touch ID funciona?")
    camera_working = models.BooleanField(default=True, help_text="¿Cámara principal y frontal funcionan correctamente?")
    
    notes = models.TextField(blank=True, null=True)
    captured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-captured_at']
        verbose_name = "Publicación de iPhone"
        verbose_name_plural = "Publicaciones de iPhones"

    def is_operational_opportunity_candidate(self) -> bool:
        """
        Critical Rule Check:
        Returns True ONLY if the listing city matches the user's operational city.
        """
        user_operational_city = self.user.profile.operational_city.strip().lower()
        listing_city = self.city.strip().lower()
        return user_operational_city in listing_city or listing_city in user_operational_city

    def __str__(self):
        return f"[{self.city}] {self.variant} - ${self.asking_price_usd}"
