from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    icon = models.CharField(max_length=50, blank=True,
                            help_text="FontAwesome class ex: fa-car")
    hint_nom_reference = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="Aide pour le nom lié à la catégorie",
        help_text="Affichée sur le formulaire d'annonce (ex. marque pour une voiture).",
    )

    def __str__(self):
        return self.name

class Property(models.Model):
    # Tarification (cahier des charges: jour/semaine/mois)
    titre = models.CharField(
        max_length=250,
        verbose_name="Nom de l'annonce",
        help_text="Nom visible de votre objet (ex. « Location weekend »).",
    )
    nom_reference_categorie = models.CharField(
        max_length=250,
        blank=True,
        default='',
        verbose_name="Nom selon la catégorie",
        help_text="Ex. marque/modèle pour une voiture, nom de résidence pour un appartement.",
    )
    description = models.TextField()
    prix_jour = models.DecimalField(max_digits=10, decimal_places=2)
    prix_semaine = models.DecimalField(max_digits=10, decimal_places=2,
                                       null=True, blank=True)
    prix_mois = models.DecimalField(max_digits=10, decimal_places=2,
                                    null=True, blank=True)
    caution = models.DecimalField(max_digits=10, decimal_places=2,
                                  default=0)
    disponibilite = models.BooleanField(default=True)
    localisation = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, related_name='properties')
    image = models.ImageField(null=True, blank=True,
                              upload_to='properties/')
    proprietaire = models.ForeignKey('users.CustomUser',
                                     on_delete=models.CASCADE,
                                     related_name='objets')
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.IntegerField(default=0)

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('property_detail', kwargs={'pk': self.pk})

    def calculer_prix(self, nb_jours):
        if nb_jours >= 30 and self.prix_mois:
            return self.prix_mois * (nb_jours // 30)
        elif nb_jours >= 7 and self.prix_semaine:
            return self.prix_semaine * (nb_jours // 7)
        return self.prix_jour * nb_jours

class PropertyImage(models.Model):
    # Multiple photos per property (cahier des charges)
    property = models.ForeignKey(Property, on_delete=models.CASCADE,
                                 related_name='images')
    image = models.ImageField(upload_to='properties/gallery/')
    def __str__(self):
        return f"Image of {self.property.titre}"

class Disponibilite(models.Model):
    # Calendar availability (FullCalendar integration)
    property = models.ForeignKey(Property, on_delete=models.CASCADE,
                                 related_name='disponibilites')
    date_debut = models.DateField()
    date_fin = models.DateField()
    disponible = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.property.titre}: {self.date_debut} → {self.date_fin}"
