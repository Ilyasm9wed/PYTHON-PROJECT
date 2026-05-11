"""Création et lecture des notifications in-app (locataire : réservation acceptée / refusée)."""

from reservations.models import Reservation


def notify_reservation_outcome(reservation, accepted: bool):
    """Enregistre une notification pour le locataire (appelé après acceptation ou refus)."""
    from .models import UserNotification

    titre = reservation.objet.titre[:120]
    if accepted:
        kind = UserNotification.KIND_RESERVATION_ACCEPTED
        message = f'Votre réservation pour « {titre} » a été acceptée.'
    else:
        kind = UserNotification.KIND_RESERVATION_REFUSED
        message = f'Votre réservation pour « {titre} » a été refusée.'
    UserNotification.objects.create(
        recipient=reservation.utilisateur,
        kind=kind,
        reservation=reservation,
        message=message[:255],
    )


def mark_reservation_outcome_notifications_read(user):
    """Marque comme lues les notifications liées à une décision sur réservation (liste « Mes réservations »)."""
    from .models import UserNotification

    if not user.is_authenticated:
        return
    UserNotification.objects.filter(
        recipient=user,
        read=False,
        kind__in=[
            UserNotification.KIND_RESERVATION_ACCEPTED,
            UserNotification.KIND_RESERVATION_REFUSED,
        ],
    ).update(read=True)


def staff_pending_user_reservations_count():
    """Demandes en attente créées par un utilisateur (hors création staff)."""
    return Reservation.objects.filter(statut='pending', created_by_staff=False).count()
