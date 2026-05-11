import json
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Property, Category, Disponibilite, PropertyImage
from .forms import PropertyForm
from django.http import JsonResponse

class PropertyListView(ListView):
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    
    def get_queryset(self):
        queryset = Property.objects.select_related('category', 'proprietaire').all()
        
        q = self.request.GET.get('q')
        category = self.request.GET.get('category')
        location = self.request.GET.get('location')
        prix_min = self.request.GET.get('prix_min')
        prix_max = self.request.GET.get('prix_max')
        disponibilite = self.request.GET.get('disponibilite')
        
        if q:
            queryset = queryset.filter(
                Q(titre__icontains=q)
                | Q(nom_reference_categorie__icontains=q)
                | Q(description__icontains=q)
            )
        if category:
            queryset = queryset.filter(category_id=category)
        if location:
            queryset = queryset.filter(localisation__icontains=location)
        if prix_min:
            queryset = queryset.filter(prix_jour__gte=prix_min)
        if prix_max:
            queryset = queryset.filter(prix_jour__lte=prix_max)
        if disponibilite:
            queryset = queryset.filter(disponibilite=True)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class PropertyDetailView(DetailView):
    model = Property
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'
    
    def get_object(self):
        obj = super().get_object()
        obj.views_count += 1
        obj.save()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = self.object.images.all()
        return context

class PropertyCreateView(LoginRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hints_par_categorie_json'] = json.dumps({
            str(c.pk): c.hint_nom_reference for c in Category.objects.all()
        })
        return context

    def form_valid(self, form):
        form.instance.proprietaire = self.request.user
        response = super().form_valid(form)
        for image in self.request.FILES.getlist('gallery_images'):
            PropertyImage.objects.create(property=self.object, image=image)
        return response

class PropertyUpdateView(LoginRequiredMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hints_par_categorie_json'] = json.dumps({
            str(c.pk): c.hint_nom_reference for c in Category.objects.all()
        })
        return context

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.proprietaire != request.user:
            return redirect('property_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in self.request.FILES.getlist('gallery_images'):
            PropertyImage.objects.create(property=self.object, image=image)
        return response

class PropertyDeleteView(LoginRequiredMixin, DeleteView):
    model = Property
    template_name = 'properties/property_confirm_delete.html'
    success_url = reverse_lazy('property_list')
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.proprietaire != request.user:
            return redirect('property_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

class MyPropertiesView(LoginRequiredMixin, ListView):
    model = Property
    template_name = 'properties/my_properties.html'
    context_object_name = 'properties'
    
    def get_queryset(self):
        return Property.objects.filter(proprietaire=self.request.user)

class DisponibiliteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        property_obj = get_object_or_404(Property, pk=pk)
        if property_obj.proprietaire != request.user:
            return redirect('property_detail', pk=pk)
        
        disponibilites = property_obj.disponibilites.all()
        events = []
        for dispo in disponibilites:
            events.append({
                'title': 'Disponible' if dispo.disponible else 'Indisponible',
                'start': dispo.date_debut.strftime('%Y-%m-%d'),
                'end': dispo.date_fin.strftime('%Y-%m-%d'),
                'color': 'green' if dispo.disponible else 'red',
            })
        
        return render(request, 'properties/disponibilite.html', {
            'property': property_obj,
            'events_json': json.dumps(events),
        })
    
    def post(self, request, pk):
        property_obj = get_object_or_404(Property, pk=pk)
        if property_obj.proprietaire != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        disponible = request.POST.get('disponible') == 'true'

        if not date_debut or not date_fin:
            return JsonResponse({'success': False, 'error': 'Dates requises.'}, status=400)

        try:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Dates invalides.'}, status=400)

        if date_fin < date_debut:
            return JsonResponse({'success': False, 'error': 'La date de fin doit être après le début.'}, status=400)
        
        Disponibilite.objects.create(
            property=property_obj,
            date_debut=date_debut,
            date_fin=date_fin,
            disponible=disponible
        )
        
        return JsonResponse({'success': True})
