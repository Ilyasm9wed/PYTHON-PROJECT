from django.db.models.signals import post_save
from django.dispatch import receiver

from reservations.models import Reservation
from paiement.models import Paiement

from .audit import write_audit


@receiver(post_save, sender=Reservation, dispatch_uid='auditlog_reservation')
def audit_reservation_save(sender, instance, created, **kwargs):
    action = 'reservation.created' if created else 'reservation.updated'
    detail = (
        f"statut={instance.statut} dates={instance.date_debut}->{instance.date_fin} "
        f"user_id={instance.utilisateur_id} property_id={instance.objet_id}"
    )
    write_audit(action, 'Reservation', instance.pk, detail)


@receiver(post_save, sender=Paiement, dispatch_uid='auditlog_paiement')
def audit_paiement_save(sender, instance, created, **kwargs):
    action = 'paiement.created' if created else 'paiement.updated'
    detail = (
        f"statut={instance.statut} montant={instance.montant} "
        f"reservation_id={instance.reservation_id}"
    )
    write_audit(action, 'Paiement', instance.pk, detail)
