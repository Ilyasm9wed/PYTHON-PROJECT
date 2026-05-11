from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    note_moyenne = models.FloatField(default=0.0)
    is_proprietaire = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    identity_verified = models.BooleanField(default=False)
    identity_document = models.ImageField(upload_to='identity_documents/', null=True, blank=True)
    identity_document_submitted = models.BooleanField(default=False)
    bio = models.TextField(blank=True)

    groups = models.ManyToManyField(Group,
        related_name="customuser_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission,
        related_name="customuser_permissions", blank=True)

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def update_note_moyenne(self):
        from django.db.models import Avg
        result = self.avis_recus.aggregate(Avg('note'))['note__avg']
        self.note_moyenne = result or 0.0
        self.save()

    def __str__(self):
        return self.username


class UserNotification(models.Model):
    """Notification in-app (badge) pour l’utilisateur — ex. statut d’une réservation."""

    KIND_RESERVATION_ACCEPTED = 'reservation_accepted'
    KIND_RESERVATION_REFUSED = 'reservation_refused'
    KIND_CHOICES = [
        (KIND_RESERVATION_ACCEPTED, 'Réservation acceptée'),
        (KIND_RESERVATION_REFUSED, 'Réservation refusée'),
    ]

    recipient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='in_app_notifications',
    )
    kind = models.CharField(max_length=40, choices=KIND_CHOICES)
    reservation = models.ForeignKey(
        'reservations.Reservation',
        on_delete=models.CASCADE,
        related_name='user_notifications',
    )
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.recipient_id} {self.kind}'


class AuditLog(models.Model):
    """Journal des changements sur réservations et paiements (acteur = requête courante si connue)."""

    actor = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_actions',
    )
    action = models.CharField(max_length=80)
    target_model = models.CharField(max_length=80)
    target_id = models.CharField(max_length=40)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} {self.target_model}#{self.target_id}"
