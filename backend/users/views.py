import csv
import json
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView, ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.conf import settings as django_settings
from django.db.models import Count
from django.utils import timezone

from properties.models import Property, PropertyImage, Category
from paiement.models import Paiement
from reviews.models import Signalement, Avis
from messaging.models import Conversation, Message

from .models import CustomUser, AuditLog
from .forms import (
    NormalUserCreationForm,
    AdminUserCreationForm,
    UserProfileForm,
    CustomLoginForm,
    StaffPropertyForm,
)
from .notifications import staff_pending_user_reservations_count, notify_reservation_outcome
from .mixins import StaffRequiredMixin
from reservations.models import Reservation
from reservations.forms import StaffReservationCreateForm

class SignupView(CreateView):
    """Inscription utilisateur normal (pas d'accès admin Django)."""
    model = CustomUser
    form_class = NormalUserCreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.is_superuser = False
        form.instance.is_staff = False
        messages.success(self.request, 'Compte créé. Vous pouvez vous connecter.')
        return super().form_valid(form)


class AdminSignupView(CreateView):
    """Inscription administrateur (staff + superuser) — page et clé séparées."""
    model = CustomUser
    form_class = AdminUserCreationForm
    template_name = 'users/signup_admin.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # En DEBUG uniquement : afficher la clé attendue sur la page (confort dev, pas pour la prod).
        if django_settings.DEBUG:
            context['admin_signup_secret_display'] = django_settings.ADMIN_SIGNUP_SECRET or ''
        else:
            context['admin_signup_secret_display'] = None
        return context

    def form_valid(self, form):
        form.instance.is_superuser = True
        form.instance.is_staff = True
        form.instance.is_proprietaire = False
        messages.success(
            self.request,
            'Compte administrateur créé. Connectez-vous puis accédez à /admin/.',
        )
        return super().form_valid(form)

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'users/login.html'

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')

class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'user_profile'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['avis_recus'] = self.object.avis_recus.all()
        context['objets'] = self.object.objets.all()
        context['reservations'] = self.object.reservations.all()
        total_as_tenant = Reservation.objects.filter(utilisateur=self.object).count()
        cancelled_as_tenant = Reservation.objects.filter(
            utilisateur=self.object, statut='cancelled'
        ).count()
        owner_reservations = Reservation.objects.filter(objet__proprietaire=self.object)
        total_as_owner = owner_reservations.count()
        accepted_as_owner = owner_reservations.filter(statut='accepted').count()
        completed_as_owner = owner_reservations.filter(statut='completed').count()

        context['fiabilite_stats'] = {
            'total_as_tenant': total_as_tenant,
            'cancel_rate_tenant': round((cancelled_as_tenant / total_as_tenant) * 100, 1)
            if total_as_tenant else 0,
            'total_as_owner': total_as_owner,
            'accept_rate_owner': round((accepted_as_owner / total_as_owner) * 100, 1)
            if total_as_owner else 0,
            'completed_as_owner': completed_as_owner,
        }
        return context

class AdminDashboardView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    """Tableau de bord dans l’app (hors /admin/) : chiffres clés + liens rapides."""
    template_name = 'users/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = {
            'users': CustomUser.objects.count(),
            'properties': Property.objects.count(),
            'reservations': Reservation.objects.count(),
            'paiements': Paiement.objects.count(),
            'avis': Avis.objects.count(),
            'conversations': Conversation.objects.count(),
            'signalements_total': Signalement.objects.count(),
            'signalements_pending': Signalement.objects.filter(traite=False).count(),
            'pending_user_reservations': staff_pending_user_reservations_count(),
        }
        context['reservations_par_statut'] = list(
            Reservation.objects.values('statut').annotate(total=Count('id')).order_by('statut')
        )
        context['admin_links'] = [
            ('Interface Django', reverse('admin:index')),
            ('Utilisateurs', reverse('admin:users_customuser_changelist')),
            ('Annonces', reverse('admin:properties_property_changelist')),
            ('Catégories', reverse('admin:properties_category_changelist')),
            ('Réservations', reverse('admin:reservations_reservation_changelist')),
            ('Paiements', reverse('admin:paiement_paiement_changelist')),
            ('Avis', reverse('admin:reviews_avis_changelist')),
            ('Signalements', reverse('admin:reviews_signalement_changelist')),
            ('Conversations', reverse('admin:messaging_conversation_changelist')),
            ('Messages', reverse('admin:messaging_message_changelist')),
        ]
        since = timezone.now() - timedelta(days=365)
        # Agrégation en Python (évite TruncMonth côté MySQL/MariaDB sans tables time_zone).
        res_counts = defaultdict(int)
        for created_at in Reservation.objects.filter(created_at__gte=since).values_list(
            'created_at', flat=True
        ):
            if created_at is None:
                continue
            key = f'{created_at.year:04d}-{created_at.month:02d}'
            res_counts[key] += 1
        reservations_chart = [
            {'month': k, 'count': res_counts[k]} for k in sorted(res_counts.keys())
        ]

        rev_totals = defaultdict(lambda: Decimal('0'))
        for created_at, montant in Paiement.objects.filter(
            statut='completed', created_at__gte=since
        ).values_list('created_at', 'montant'):
            if created_at is None:
                continue
            key = f'{created_at.year:04d}-{created_at.month:02d}'
            rev_totals[key] += montant if montant is not None else Decimal('0')
        revenue_chart = [
            {'month': k, 'total': float(rev_totals[k])} for k in sorted(rev_totals.keys())
        ]
        context['reservations_chart_json'] = json.dumps(reservations_chart)
        context['revenue_chart_json'] = json.dumps(revenue_chart)
        return context


class AdminSignalementListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Signalement
    template_name = 'users/admin_signalements.html'
    context_object_name = 'signalements'
    paginate_by = 20

    def get_queryset(self):
        return Signalement.objects.select_related('auteur', 'objet').order_by('-created_at')


class AdminSignalementTraiterView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        signalement = get_object_or_404(Signalement, pk=pk)
        signalement.traite = True
        signalement.save(update_fields=['traite'])
        messages.success(request, 'Signalement marqué comme traité.')
        return redirect('admin_signalements')


class StaffSignalementBulkTraiterView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request):
        ids = request.POST.getlist('ids')
        if not ids:
            messages.warning(request, 'Aucun signalement sélectionné.')
            return redirect('admin_signalements')
        updated = Signalement.objects.filter(pk__in=ids, traite=False).update(traite=True)
        messages.success(request, f'{updated} signalement(s) marqué(s) comme traités.')
        return redirect('admin_signalements')


class StaffReservationExportView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="reservations.csv"'
        response.write('\ufeff')
        writer = csv.writer(response)
        writer.writerow([
            'id', 'statut', 'date_debut', 'date_fin', 'locataire', 'email_locataire',
            'objet_id', 'titre_objet', 'created_at',
        ])
        for r in Reservation.objects.select_related('utilisateur', 'objet').iterator():
            writer.writerow([
                r.pk,
                r.statut,
                r.date_debut,
                r.date_fin,
                r.utilisateur.username,
                r.utilisateur.email,
                r.objet_id,
                r.objet.titre,
                r.created_at.isoformat(),
            ])
        return response


class StaffPaiementExportView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="paiements.csv"'
        response.write('\ufeff')
        writer = csv.writer(response)
        writer.writerow([
            'id', 'statut', 'montant', 'caution', 'numero_facture',
            'reservation_id', 'created_at',
        ])
        for p in Paiement.objects.select_related('reservation').iterator():
            writer.writerow([
                p.pk,
                p.statut,
                p.montant,
                p.caution,
                p.numero_facture,
                p.reservation_id,
                p.created_at.isoformat(),
            ])
        return response


class StaffAuditLogListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = AuditLog
    template_name = 'users/admin_audit_log.html'
    context_object_name = 'logs'
    paginate_by = 50

    def get_queryset(self):
        return AuditLog.objects.select_related('actor').order_by('-created_at')


class StaffReservationListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Reservation
    template_name = 'users/admin_reservations.html'
    context_object_name = 'reservations'
    paginate_by = 25

    def get_queryset(self):
        qs = Reservation.objects.select_related(
            'utilisateur', 'objet', 'objet__proprietaire'
        ).order_by('-created_at')
        uid = self.request.GET.get('utilisateur')
        if uid:
            qs = qs.filter(utilisateur_id=uid)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['users_for_filter'] = CustomUser.objects.order_by('username')
        ctx['filter_user_id'] = self.request.GET.get('utilisateur', '')
        return ctx


class StaffReservationCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Reservation
    form_class = StaffReservationCreateForm
    template_name = 'users/admin_reservation_create.html'

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.created_by_staff = True
        instance.contrat_accepte = True
        statut = form.cleaned_data['statut_initial']
        instance.statut = statut
        if statut == 'accepted':
            instance.contrat_proprietaire_confirme = True
            instance.contrat_date_confirmation = timezone.now()
        instance.save()
        if statut == 'accepted' and not instance.contrat_reference:
            instance.contrat_reference = f"CTR-{instance.pk:06d}"
            instance.save(update_fields=['contrat_reference'])

        conversation = Conversation.objects.create(property=instance.objet)
        conversation.participants.add(
            instance.utilisateur,
            instance.objet.proprietaire,
        )
        Message.objects.create(
            conversation=conversation,
            contenu=(
                f"Réservation enregistrée par l'administration du {instance.date_debut} "
                f"au {instance.date_fin}. {instance.message_locataire or ''}"
            ).strip(),
            expediteur=self.request.user,
        )
        messages.success(self.request, 'Réservation créée.')
        return redirect('staff_reservations')


class StaffReservationAcceptView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        if reservation.statut != 'pending':
            messages.error(request, 'Seules les réservations en attente peuvent être acceptées.')
            return redirect('staff_reservations')

        reservation.statut = 'accepted'
        reservation.contrat_proprietaire_confirme = True
        reservation.contrat_date_confirmation = timezone.now()
        if not reservation.contrat_reference:
            reservation.contrat_reference = f"CTR-{reservation.id:06d}"
        reservation.save()

        conversation = (
            Conversation.objects.filter(property=reservation.objet)
            .filter(participants=reservation.utilisateur)
            .filter(participants=reservation.objet.proprietaire)
            .first()
        )
        if not conversation:
            conversation = Conversation.objects.create(property=reservation.objet)
            conversation.participants.add(
                reservation.utilisateur,
                reservation.objet.proprietaire,
            )
        Message.objects.create(
            conversation=conversation,
            contenu='Votre réservation a été acceptée (par un administrateur).',
            expediteur=request.user,
        )
        notify_reservation_outcome(reservation, accepted=True)
        messages.success(request, 'Réservation acceptée.')
        return redirect('staff_reservations')


class StaffReservationRefuseView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        if reservation.statut != 'pending':
            messages.error(request, 'Seules les réservations en attente peuvent être refusées.')
            return redirect('staff_reservations')

        reservation.statut = 'refused'
        reservation.save()

        conversation = (
            Conversation.objects.filter(property=reservation.objet)
            .filter(participants=reservation.utilisateur)
            .filter(participants=reservation.objet.proprietaire)
            .first()
        )
        if not conversation:
            conversation = Conversation.objects.create(property=reservation.objet)
            conversation.participants.add(
                reservation.utilisateur,
                reservation.objet.proprietaire,
            )
        Message.objects.create(
            conversation=conversation,
            contenu='Votre réservation a été refusée (par un administrateur).',
            expediteur=request.user,
        )
        notify_reservation_outcome(reservation, accepted=False)
        messages.success(request, 'Réservation refusée.')
        return redirect('staff_reservations')


class StaffPropertyCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """Création d’une annonce par le staff (choix du propriétaire)."""

    model = Property
    form_class = StaffPropertyForm
    template_name = 'properties/staff_property_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hints_par_categorie_json'] = json.dumps({
            str(c.pk): c.hint_nom_reference for c in Category.objects.all()
        })
        context['cancel_url'] = reverse('admin_dashboard')
        context['form_heading_staff'] = True
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in self.request.FILES.getlist('gallery_images'):
            PropertyImage.objects.create(property=self.object, image=image)
        messages.success(self.request, 'Annonce créée.')
        return response

    def get_success_url(self):
        return reverse('property_detail', kwargs={'pk': self.object.pk})


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'users/edit_profile.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        # If identity document is uploaded, mark as submitted
        if 'identity_document' in self.request.FILES:
            form.instance.identity_document_submitted = True
        messages.success(self.request, 'Profil mis à jour avec succès.')
        return super().form_valid(form)
