"""Règles de disponibilité : réservations actives + plages « indisponible » du calendrier.

Une réservation occupe l'intervalle **demi-ouvert** [date_debut, date_fin) : ``date_fin`` est le
jour de libération (non inclus), ce qui permet d'enchaîner un départ le J et une arrivée le J.

Les plages calendrier ``disponible=False`` restent des **jours entiers inclusifs** [date_debut, date_fin].
"""


def period_blocked_by_indisponibilite_calendar(property_obj, date_debut, date_fin):
    """
    True si une plage Disponibilite avec disponible=False intersecte [date_debut, date_fin).

    Plage calendrier : jours bloqués du ``date_debut`` au ``date_fin`` (inclus).
    """
    from .models import Disponibilite

    return Disponibilite.objects.filter(
        property=property_obj,
        disponible=False,
        date_fin__gte=date_debut,
        date_debut__lt=date_fin,
    ).exists()


def reservation_period_has_conflict(property_obj, date_debut, date_fin, exclude_reservation_id=None):
    """
    True si la période [date_debut, date_fin) entre en conflit avec :
    - une autre réservation pending/accepted (même convention demi-ouverte), ou
    - une plage calendrier explicitement indisponible (jours inclusifs).
    """
    from reservations.models import Reservation

    qs = Reservation.objects.filter(
        objet=property_obj,
        statut__in=['pending', 'accepted'],
        date_debut__lt=date_fin,
        date_fin__gt=date_debut,
    )
    if exclude_reservation_id:
        qs = qs.exclude(pk=exclude_reservation_id)
    if qs.exists():
        return True
    return period_blocked_by_indisponibilite_calendar(property_obj, date_debut, date_fin)
