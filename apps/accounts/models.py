from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """
    Stores user-specific settings, operational market boundaries, budget limits,
    and target profit margins. Ensures strict multi-tenant isolation.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    operational_city = models.CharField(
        max_length=100, 
        default='Maturín', 
        help_text="Ciudad operacional donde el usuario busca ofertas de compra."
    )
    min_budget = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=100.00,
        help_text="Presupuesto mínimo asignado para compra por dispositivo ($)."
    )
    max_budget = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=250.00,
        help_text="Presupuesto máximo asignado para compra por dispositivo ($)."
    )
    min_profit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=30.00,
        help_text="Margen de ganancia neta mínima deseada por dispositivo ($)."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.user.username} - {self.operational_city} (Ganancia min: ${self.min_profit})"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()
