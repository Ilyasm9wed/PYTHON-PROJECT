from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from datetime import datetime
from django.utils import timezone
from .models import Reservation
from properties.models import Property
from properties.availability import reservation_period_has_conflict
from messaging.models import Conversation, Message

class CreateReservationView(LoginRequiredMixin, View):
    def get(self, request, property_id):
        property_obj = get_object_or_404(Property, pk=property_id)
        return render(request, 'reservations/create_reservation.html', {
            'property': property_obj,
        })
    
    def post(self, request, property_id):
        property_obj = get_object_or_404(Property, pk=property_id)
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        message_locataire = request.POST.get('message_locataire')
        contrat_accepte = request.POST.get('contrat_accepte') == 'on'
        
        if not property_obj.disponibilite:
            messages.error(request, 'Cette annonce n\'est pas disponible pour la réservation.')
            return render(request, 'reservations/create_reservation.html', {
                'property': property_obj,
            })
        
        if not contrat_accepte:
            messages.error(request, 'Vous devez accepter le contrat de location.')
            return render(request, 'reservations/create_reservation.html', {
                'property': property_obj,
            })
        
        date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
        date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()

        if date_fin <= date_debut:
            messages.error(
                request,
                'La date de fin doit être après la date de début (jour de départ non inclus).',
            )
            return render(request, 'reservations/create_reservation.html', {
                'property': property_obj,
            })

        if reservation_period_has_conflict(property_obj, date_debut, date_fin):
            messages.error(
                request,
                'Cette période est indisponible (déjà réservée ou marquée indisponible au calendrier).',
            )
            return render(request, 'reservations/create_reservation.html', {
                'property': property_obj,
            })
        
        reservation = Reservation.objects.create(
            utilisateur=request.user,
            objet=property_obj,
            date_debut=date_debut,
            date_fin=date_fin,
            message_locataire=message_locataire,
            contrat_accepte=contrat_accepte,
            statut='pending'
        )
        
        # Send message to owner
        conversation = Conversation.objects.create(property=property_obj)
        conversation.participants.add(request.user, property_obj.proprietaire)
        Message.objects.create(
            conversation=conversation,
            contenu=f"Nouvelle demande de réservation du {date_debut} au {date_fin}. {message_locataire}",
            expediteur=request.user
        )
        
        messages.success(request, 'Réservation créée avec succès.')
        return redirect('pay_reservation', pk=reservation.pk)

class ReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'reservations/my_reservations.html'
    context_object_name = 'reservations'

    def get_context_data(self, **kwargs):
        from users.models import UserNotification
        from users.notifications import mark_reservation_outcome_notifications_read

        context = super().get_context_data(**kwargs)
        u = self.request.user
        context['recent_notifications'] = list(
            UserNotification.objects.filter(recipient=u, read=False).order_by('-created_at')[:8]
        )
        mark_reservation_outcome_notifications_read(u)
        context['user_unread_notifications_count'] = UserNotification.objects.filter(
            recipient=u, read=False
        ).count()
        return context

    def get_queryset(self):
        return Reservation.objects.filter(utilisateur=self.request.user).select_related('objet')


class UpdateReservationView(LoginRequiredMixin, UpdateView):
    model = Reservation
    template_name = 'reservations/edit_reservation.html'
    fields = ['date_debut', 'date_fin', 'message_locataire']

    def dispatch(self, request, *args, **kwargs):
        reservation = self.get_object()
        is_owner_user = reservation.utilisateur == request.user
        is_admin = request.user.is_staff or request.user.is_superuser

        if not (is_owner_user or is_admin):
            messages.error(request, 'Non autorisé.')
            return redirect('my_reservations')

        if is_owner_user and reservation.statut not in ['pending', 'accepted']:
            messages.error(request, 'Cette réservation ne peut plus être modifiée.')
            return redirect('my_reservations')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        reservation = self.get_object()
        date_debut = form.cleaned_data['date_debut']
        date_fin = form.cleaned_data['date_fin']

        if date_fin <= date_debut:
            form.add_error('date_fin', 'La date de fin doit être après la date de début.')
            return self.form_invalid(form)

        if reservation_period_has_conflict(
            reservation.objet, date_debut, date_fin, exclude_reservation_id=reservation.pk
        ):
            form.add_error(
                None,
                'Cette période est indisponible (réservation active ou calendrier).',
            )
            return self.form_invalid(form)

        messages.success(self.request, 'Réservation modifiée avec succès.')
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return reverse_lazy('admin:reservations_reservation_changelist')
        return reverse_lazy('my_reservations')

class ProprietaireReservationsView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'reservations/owner_reservations.html'
    context_object_name = 'reservations'
    
    def get_queryset(self):
        return Reservation.objects.filter(
            objet__proprietaire=self.request.user
        ).select_related('objet', 'utilisateur')

class AcceptReservationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        if reservation.objet.proprietaire != request.user:
            messages.error(request, 'Non autorisé.')
            return redirect('owner_reservations')
        
        reservation.statut = 'accepted'
        reservation.contrat_proprietaire_confirme = True
        reservation.contrat_date_confirmation = timezone.now()
        if not reservation.contrat_reference:
            reservation.contrat_reference = f"CTR-{reservation.id:06d}"
        reservation.save()
        
        # Send confirmation message
        conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=reservation.utilisateur
        ).first()
        
        if conversation:
            Message.objects.create(
                conversation=conversation,
                contenu=f"Votre réservation a été acceptée.",
                expediteur=request.user
            )

        from users.notifications import notify_reservation_outcome

        notify_reservation_outcome(reservation, accepted=True)
        messages.success(request, 'Réservation acceptée.')
        return redirect('owner_reservations')

class RefuseReservationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        if reservation.objet.proprietaire != request.user:
            messages.error(request, 'Non autorisé.')
            return redirect('owner_reservations')
        
        reservation.statut = 'refused'
        reservation.save()

        conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=reservation.utilisateur
        ).first()
        if conversation:
            Message.objects.create(
                conversation=conversation,
                contenu='Votre réservation a été refusée.',
                expediteur=request.user,
            )

        from users.notifications import notify_reservation_outcome

        notify_reservation_outcome(reservation, accepted=False)
        messages.success(request, 'Réservation refusée.')
        return redirect('owner_reservations')

class CancelReservationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        if reservation.utilisateur != request.user:
            messages.error(request, 'Non autorisé.')
            return redirect('my_reservations')
        
        reservation.statut = 'cancelled'
        reservation.save()
        
        if hasattr(reservation, 'paiement'):
            reservation.paiement.rembourser()
        
        messages.success(request, 'Réservation annulée.')
        return redirect('my_reservations')

class ContratView(LoginRequiredMixin, View):
    def get(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        is_participant = request.user in [reservation.utilisateur, reservation.objet.proprietaire]
        if not is_participant:
            messages.error(request, 'Non autorisé.')
            return redirect('my_reservations')

        if not reservation.contrat_reference:
            reservation.contrat_reference = f"CTR-{reservation.id:06d}"
            reservation.save(update_fields=['contrat_reference'])

        return render(request, 'reservations/contrat.html', {
            'reservation': reservation,
        })
