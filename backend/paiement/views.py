from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from reservations.models import Reservation
from .models import Paiement


class PaiementView(LoginRequiredMixin, View):
    def get(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        if reservation.utilisateur != request.user:
            messages.error(request, 'Non autorisé.')
            return redirect('my_reservations')

        total = reservation.calculer_montant_total()
        return render(request, 'paiement/paiement.html', {
            'reservation': reservation,
            'total': total,
            'caution': reservation.objet.caution,
        })

    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        if reservation.utilisateur != request.user:
            messages.error(request, 'Non autorisé.')
            return redirect('my_reservations')

        total = reservation.calculer_montant_total()
        paiement = Paiement.objects.create(
            reservation=reservation,
            montant=total,
            caution=reservation.objet.caution,
            statut='completed',
        )
        paiement.traiter()

        messages.success(request, 'Paiement effectué avec succès.')
        return redirect('facture', pk=reservation.pk)


class FactureView(LoginRequiredMixin, View):
    def get(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        if reservation.utilisateur != request.user:
            messages.error(request, 'Non autorisé.')
            return redirect('my_reservations')

        return render(request, 'paiement/facture.html', {
            'reservation': reservation,
        })
