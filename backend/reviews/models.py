from django.db import models

class Avis(models.Model):
    note = models.IntegerField(choices=[(i,i) for i in range(1,6)])
    commentaire = models.TextField()
    auteur = models.ForeignKey('users.CustomUser',
                               on_delete=models.CASCADE,
                               related_name='avis_donnes')
    cible = models.ForeignKey('users.CustomUser',
                              on_delete=models.CASCADE,
                              related_name='avis_recus')
    reservation = models.ForeignKey('reservations.Reservation',
                                    on_delete=models.CASCADE,
                                    null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One review per reservation per user
        unique_together = ['auteur', 'reservation']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cible.update_note_moyenne()

    def __str__(self):
        return f"Avis {self.note}/5 par {self.auteur}"

class Signalement(models.Model):
    # Système de signalement (cahier des charges)
    RAISON_CHOICES = [
        ('spam', 'Spam'),
        ('fake', 'Fausse annonce'),
        ('inappropriate', 'Contenu inapproprié'),
        ('other', 'Autre'),
    ]
    auteur = models.ForeignKey('users.CustomUser',
                               on_delete=models.CASCADE,
                               related_name='signalements')
    objet = models.ForeignKey('properties.Property',
                              on_delete=models.CASCADE,
                              null=True, blank=True)
    raison = models.CharField(max_length=50, choices=RAISON_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    traite = models.BooleanField(default=False)

    def __str__(self):
        return f"Signalement par {self.auteur}"
