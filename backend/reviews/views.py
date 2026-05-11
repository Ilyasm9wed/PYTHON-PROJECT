from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Avis, Signalement
from properties.models import Property
from reservations.models import Reservation

class CreateAvisView(LoginRequiredMixin, CreateView):
    model = Avis
    template_name = 'reviews/create_avis.html'
    fields = ['note', 'commentaire']
    
    def dispatch(self, request, *args, **kwargs):
        reservation_id = kwargs.get('reservation_id')
        reservation = get_object_or_404(Reservation, pk=reservation_id)
        if request.user not in [reservation.utilisateur, reservation.objet.proprietaire]:
            messages.error(request, 'Non autorisé.')
            return redirect('my_reservations')
        
        if reservation.statut != 'completed':
            messages.error(request, 'Vous ne pouvez noter que les réservations terminées.')
            return redirect('my_reservations')
        
        if Avis.objects.filter(auteur=request.user, reservation=reservation).exists():
            messages.error(request, 'Vous avez déjà noté cette réservation.')
            return redirect('my_reservations')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        reservation_id = self.kwargs.get('reservation_id')
        reservation = get_object_or_404(Reservation, pk=reservation_id)
        form.instance.auteur = self.request.user
        if self.request.user == reservation.utilisateur:
            form.instance.cible = reservation.objet.proprietaire
        else:
            form.instance.cible = reservation.utilisateur
        form.instance.reservation = reservation
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('my_reservations')

class SignalementView(LoginRequiredMixin, CreateView):
    model = Signalement
    template_name = 'reviews/create_signalement.html'
    fields = ['raison', 'description']
    
    def dispatch(self, request, *args, **kwargs):
        property_id = kwargs.get('property_id')
        property_obj = get_object_or_404(Property, pk=property_id)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        property_id = self.kwargs.get('property_id')
        property_obj = get_object_or_404(Property, pk=property_id)
        form.instance.auteur = self.request.user
        form.instance.objet = property_obj
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('property_list')
