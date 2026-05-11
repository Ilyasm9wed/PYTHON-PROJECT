from django import forms

from .models import Property


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'category',
            'titre',
            'nom_reference_categorie',
            'description',
            'prix_jour',
            'prix_semaine',
            'prix_mois',
            'caution',
            'disponibilite',
            'localisation',
            'image',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'nom_reference_categorie': forms.TextInput(attrs={'id': 'id_nom_reference_categorie'}),
        }
