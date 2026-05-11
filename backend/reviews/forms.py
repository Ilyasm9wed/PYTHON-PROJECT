from django import forms
from .models import Avis, Signalement

class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ['note', 'commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={'rows': 4}),
        }

class SignalementForm(forms.ModelForm):
    class Meta:
        model = Signalement
        fields = ['raison', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
