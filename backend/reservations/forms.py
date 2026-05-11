from django import forms
from django.core.exceptions import ValidationError

from properties.availability import reservation_period_has_conflict

from .models import Reservation


class StaffReservationCreateForm(forms.ModelForm):
    """Création d'une réservation par un administrateur (interface staff)."""
    statut_initial = forms.ChoiceField(
        label='Statut à la création',
        choices=[
            ('pending', 'En attente'),
            ('accepted', 'Acceptée'),
        ],
        initial='pending',
    )

    class Meta:
        model = Reservation
        fields = ['utilisateur', 'objet', 'date_debut', 'date_fin', 'message_locataire']
        widgets = {
            'utilisateur': forms.Select(attrs={'class': 'form-select'}),
            'objet': forms.Select(attrs={'class': 'form-select'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'message_locataire': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_fin'].help_text = (
            'Jour de libération du logement (non inclus dans l’occupation : une autre '
            'réservation peut commencer ce jour-là).'
        )
        self.fields['utilisateur'].queryset = self.fields['utilisateur'].queryset.order_by(
            'username'
        )
        self.fields['objet'].queryset = self.fields['objet'].queryset.select_related(
            'proprietaire'
        ).order_by('titre')

    def clean(self):
        cleaned = super().clean()
        if self.errors:
            return cleaned
        utilisateur = cleaned.get('utilisateur')
        objet = cleaned.get('objet')
        d0 = cleaned.get('date_debut')
        d1 = cleaned.get('date_fin')
        if d0 and d1 and d1 <= d0:
            raise ValidationError(
                {'date_fin': 'La date de fin doit être après la date de début.'}
            )
        if utilisateur and objet and objet.proprietaire_id == utilisateur.id:
            raise ValidationError(
                'Le locataire ne peut pas être le propriétaire de cette annonce.'
            )
        if utilisateur and objet and d0 and d1:
            if reservation_period_has_conflict(objet, d0, d1):
                raise ValidationError(
                    'Cette période est indisponible (réservation existante ou calendrier).'
                )
        return cleaned


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date_debut', 'date_fin', 'message_locataire', 'contrat_accepte']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
            'message_locataire': forms.Textarea(attrs={'rows': 3}),
        }

