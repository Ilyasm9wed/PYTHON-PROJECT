from django.urls import path
from .views import (
    SignupView,
    AdminSignupView,
    CustomLoginView,
    CustomLogoutView,
    ProfileView,
    EditProfileView,
    AdminDashboardView,
    AdminSignalementListView,
    AdminSignalementTraiterView,
    StaffReservationListView,
    StaffReservationCreateView,
    StaffReservationAcceptView,
    StaffReservationRefuseView,
    StaffSignalementBulkTraiterView,
    StaffReservationExportView,
    StaffPaiementExportView,
    StaffAuditLogListView,
    StaffPropertyCreateView,
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signup-admin/', AdminSignupView.as_view(), name='signup_admin'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('staff/tableau-de-bord/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('staff/signalements/', AdminSignalementListView.as_view(), name='admin_signalements'),
    path(
        'staff/signalements/<int:pk>/traiter/',
        AdminSignalementTraiterView.as_view(),
        name='admin_signalement_traiter',
    ),
    path(
        'staff/signalements/bulk/',
        StaffSignalementBulkTraiterView.as_view(),
        name='staff_signalement_bulk',
    ),
    path(
        'staff/export/reservations/',
        StaffReservationExportView.as_view(),
        name='staff_export_reservations',
    ),
    path(
        'staff/export/paiements/',
        StaffPaiementExportView.as_view(),
        name='staff_export_paiements',
    ),
    path('staff/audit/', StaffAuditLogListView.as_view(), name='staff_audit_log'),
    path(
        'staff/annonces/create/',
        StaffPropertyCreateView.as_view(),
        name='staff_property_create',
    ),
    path('staff/reservations/', StaffReservationListView.as_view(), name='staff_reservations'),
    path(
        'staff/reservations/create/',
        StaffReservationCreateView.as_view(),
        name='staff_reservation_create',
    ),
    path(
        'staff/reservations/<int:pk>/accept/',
        StaffReservationAcceptView.as_view(),
        name='staff_reservation_accept',
    ),
    path(
        'staff/reservations/<int:pk>/refuse/',
        StaffReservationRefuseView.as_view(),
        name='staff_reservation_refuse',
    ),
]
