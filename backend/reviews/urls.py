from django.urls import path
from .views import CreateAvisView, SignalementView

urlpatterns = [
    path('create/<int:reservation_id>/', CreateAvisView.as_view(), name='create_avis'),
    path('report/<int:property_id>/', SignalementView.as_view(), name='signalement'),
]
