from django.db import models


class Paiement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Payé'),
        ('refunded', 'Remboursé'),
        ('cancelled', 'Annulé'),
    ]
    reservation = models.OneToOneField(
        'reservations.Reservation',
        on_delete=models.CASCADE,
        related_name='paiement',
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    caution = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    numero_facture = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def traiter(self):
        import uuid
        self.statut = 'completed'
        self.numero_facture = f"FAC-{uuid.uuid4().hex[:8].upper()}"
        self.save()
        self.reservation.objet.disponibilite = False
        self.reservation.objet.save()

    def rembourser(self):
        self.statut = 'refunded'
        self.save()

    def __str__(self):
        return f"Paiement #{self.id} - {self.statut}"
