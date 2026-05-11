from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'objet', 'statut', 'date_debut', 'date_fin')
    list_filter = ('statut',)
