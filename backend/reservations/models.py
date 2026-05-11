from django.db import models

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('refused', 'Refusée'),
        ('cancelled', 'Annulée'),
        ('completed', 'Terminée'),
    ]
    utilisateur = models.ForeignKey('users.CustomUser',
                                    on_delete=models.CASCADE,
                                    related_name='reservations')
    objet = models.ForeignKey('properties.Property',
                              on_delete=models.CASCADE,
                              related_name='reservations')
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(max_length=20,
                              choices=STATUS_CHOICES,
                              default='pending')
    # Contrat de location simplifié (cahier des charges)
    contrat_accepte = models.BooleanField(default=False)
    contrat_proprietaire_confirme = models.BooleanField(default=False)
    contrat_reference = models.CharField(max_length=50, blank=True)
    contrat_date_confirmation = models.DateTimeField(null=True, blank=True)
    message_locataire = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by_staff = models.BooleanField(
        default=False,
        verbose_name='Créée par le staff',
        help_text='True si la réservation a été créée depuis l’interface administrateur.',
    )

    def calculer_duree(self):
        return (self.date_fin - self.date_debut).days

    def calculer_montant_total(self):
        return self.objet.calculer_prix(self.calculer_duree())

    def __str__(self):
        return f"Reservation #{self.id} - {self.statut}"
