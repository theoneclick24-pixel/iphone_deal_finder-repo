from django.db import models
from django.contrib.auth.models import User
from apps.listings.models import Listing

class OpportunityStatus(models.TextChoices):
    QUALIFIED = 'QUALIFIED', '🟢 Oportunidad Aprobada'
    LOW_PROFIT = 'LOW_PROFIT', '🟡 Ganancia Insuficiente'
    OVER_BUDGET = 'OVER_BUDGET', '🟠 Excede Presupuesto'
    NON_OPERATIONAL = 'NON_OPERATIONAL', '🔴 Fuera de Ciudad Operacional'

class Opportunity(models.Model):
    """
    Evaluated opportunity generated specifically for a user based on their
    operational city, budget limits, target profit margin, and condition rules.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opportunities')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='opportunities')
    status = models.CharField(max_length=30, choices=OpportunityStatus.choices, default=OpportunityStatus.QUALIFIED)
    
    projected_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estimated_resale_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_repairs_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    explanation_code = models.CharField(max_length=50, help_text="Código corto de explicación (ej. HIGH_PROFIT, LOW_MARGIN).")
    explanation_text = models.TextField(help_text="Explicación detallada para el usuario.")
    is_favorite = models.BooleanField(default=False, help_text="Guardado en la lista de ofertas destacadas.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-projected_profit', '-created_at']
        unique_together = ('user', 'listing')
        verbose_name = "Oportunidad de Compra"
        verbose_name_plural = "Oportunidades de Compra"

    def __str__(self):
        return f"[{self.get_status_display()}] {self.listing.variant} -> Ganancia: ${self.projected_profit}"
