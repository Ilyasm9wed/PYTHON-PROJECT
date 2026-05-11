from django.contrib import admin
from .models import Category, Property, PropertyImage, Disponibilite

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'hint_nom_reference')

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('titre', 'nom_reference_categorie', 'proprietaire', 'category',
                    'prix_jour', 'disponibilite', 'created_at')
    list_filter = ('category', 'disponibilite')
    search_fields = ('titre', 'nom_reference_categorie', 'description', 'localisation')

admin.site.register(PropertyImage)
admin.site.register(Disponibilite)
