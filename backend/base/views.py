from django.shortcuts import render
from django.views import View
from properties.models import Property, Category

class HomeView(View):
    def get(self, request):
        latest_properties = Property.objects.filter(disponibilite=True)[:8]
        categories = Category.objects.all()
        return render(request, 'base/home.html', {
            'latest_properties': latest_properties,
            'categories': categories,
        })
