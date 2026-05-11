from django import forms


class PaiementForm(forms.Form):
    nom_carte = forms.CharField(max_length=100, label='Nom sur la carte')
    numero_carte = forms.CharField(max_length=16, label='Numéro de carte')
    expiration = forms.CharField(max_length=5, label='Expiration (MM/YY)')
    cvv = forms.CharField(max_length=3, label='CVV')
