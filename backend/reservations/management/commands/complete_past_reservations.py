from django.core.management.base import BaseCommand
from django.utils import timezone

from reservations.models import Reservation


class Command(BaseCommand):
    help = (
        'Passe en « terminée » les réservations acceptées dont la date de fin est passée. '
        'À planifier (cron) : python manage.py complete_past_reservations. '
        'Note : QuerySet.update() ne déclenche pas les signaux post_save (pas d’audit ligne par ligne).'
    )

    def handle(self, *args, **options):
        today = timezone.localdate()
        qs = Reservation.objects.filter(statut='accepted', date_fin__lt=today)
        n = qs.update(statut='completed')
        self.stdout.write(self.style.SUCCESS(f'{n} réservation(s) marquée(s) comme terminées.'))
