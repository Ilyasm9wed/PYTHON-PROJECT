from django.urls import path
from .views import (
    CreateReservationView, ReservationListView, ProprietaireReservationsView,
    AcceptReservationView, RefuseReservationView, CancelReservationView, UpdateReservationView,
    ContratView,
)

urlpatterns = [
    path('create/<int:property_id>/', CreateReservationView.as_view(), name='create_reservation'),
    path('my/', ReservationListView.as_view(), name='my_reservations'),
    path('owner/', ProprietaireReservationsView.as_view(), name='owner_reservations'),
    path('<int:pk>/edit/', UpdateReservationView.as_view(), name='edit_reservation'),
    path('<int:pk>/accept/', AcceptReservationView.as_view(), name='accept_reservation'),
    path('<int:pk>/refuse/', RefuseReservationView.as_view(), name='refuse_reservation'),
    path('<int:pk>/cancel/', CancelReservationView.as_view(), name='cancel_reservation'),
    path('<int:pk>/contrat/', ContratView.as_view(), name='contrat_reservation'),
]
