from django.contrib import admin
from .models import Avis, Signalement

@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('auteur', 'cible', 'note', 'created_at')

@admin.register(Signalement)
class SignalementAdmin(admin.ModelAdmin):
    list_display = ('auteur', 'raison', 'traite')
