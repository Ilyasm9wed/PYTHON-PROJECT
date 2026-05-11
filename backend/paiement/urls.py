from django.urls import path

from .views import PaiementView, FactureView

urlpatterns = [
    path('<int:pk>/pay/', PaiementView.as_view(), name='pay_reservation'),
    path('<int:pk>/facture/', FactureView.as_view(), name='facture'),
]
