from django.urls import path
from .views import (
    PropertyListView, PropertyDetailView, PropertyCreateView,
    PropertyUpdateView, PropertyDeleteView, MyPropertiesView, DisponibiliteView
)

urlpatterns = [
    path('', PropertyListView.as_view(), name='property_list'),
    path('<int:pk>/', PropertyDetailView.as_view(), name='property_detail'),
    path('create/', PropertyCreateView.as_view(), name='property_create'),
    path('<int:pk>/edit/', PropertyUpdateView.as_view(), name='property_update'),
    path('<int:pk>/delete/', PropertyDeleteView.as_view(), name='property_delete'),
    path('mes-annonces/', MyPropertiesView.as_view(), name='my_properties'),
    path('<int:pk>/disponibilite/', DisponibiliteView.as_view(), name='disponibilite'),
]
