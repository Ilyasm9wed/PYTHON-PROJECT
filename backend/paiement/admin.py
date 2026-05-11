from django.contrib import admin

from .models import Paiement


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'montant', 'caution', 'statut', 'numero_facture')
