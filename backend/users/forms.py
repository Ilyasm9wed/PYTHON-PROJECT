from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

from properties.forms import PropertyForm

from .models import CustomUser


class StaffPropertyForm(PropertyForm):
    """Création d’annonce par un admin : choix du propriétaire."""

    class Meta(PropertyForm.Meta):
        fields = ['proprietaire'] + list(PropertyForm.Meta.fields)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proprietaire'].queryset = CustomUser.objects.order_by('username')
        self.fields['proprietaire'].widget.attrs.setdefault('class', 'form-select')


class NormalUserCreationForm(UserCreationForm):
    """Inscription utilisateur (jamais staff / superuser via ce formulaire)."""
    is_proprietaire = forms.BooleanField(
        label='Propriétaire (peut publier des annonces)',
        required=False,
        widget=forms.CheckboxInput(),
    )

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'username', 'email',
            'phone', 'address', 'is_proprietaire', 'password1', 'password2',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''


class AdminUserCreationForm(UserCreationForm):
    """Inscription administrateur Django — protégée par une clé secrète (settings)."""
    registration_secret = forms.CharField(
        label="Clé d'inscription administrateur",
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        help_text='Fournie par l’équipe technique (variable ADMIN_SIGNUP_SECRET).',
    )

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'username', 'email',
            'phone', 'address', 'password1', 'password2',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
    def clean_registration_secret(self):
        key = self.cleaned_data.get('registration_secret', '')
        expected = getattr(settings, 'ADMIN_SIGNUP_SECRET', '') or ''
        if not expected:
            raise ValidationError(
                "L'inscription administrateur n'est pas activée sur ce serveur "
                "(définir ADMIN_SIGNUP_SECRET)."
            )
        if key != expected:
            raise ValidationError('Clé incorrecte.')
        return key


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone', 'address', 'avatar', 'identity_document', 'bio']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
