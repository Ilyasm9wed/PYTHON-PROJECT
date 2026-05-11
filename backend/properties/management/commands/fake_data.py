from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from properties.models import Category, Property, Disponibilite
from reservations.models import Reservation
from paiement.models import Paiement
from reviews.models import Avis
from messaging.models import Conversation, Message
from faker import Faker
from datetime import datetime, timedelta
import random

User = get_user_model()
fake = Faker('fr_FR')

CATEGORY_HINTS = {
    'voiture': 'Marque / modèle (ex. Nissan Qashqai)',
    'appartement': 'Nom de la résidence ou du bien (ex. Résidence Les Oliviers)',
    'velo': 'Marque ou modèle (ex. Trek FX 2)',
    'outillage': 'Marque ou référence (ex. Bosch Professional)',
    'electronique': 'Marque ou modèle (ex. Apple MacBook Air)',
}


def _exemple_nom_reference(slug):
    if slug == 'voiture':
        return random.choice(['Nissan Micra', 'Peugeot 208', 'Renault Clio', 'Dacia Sandero'])
    if slug == 'appartement':
        return random.choice([
            'Résidence Les Jardins',
            'Résidence Marina Bay',
            'Résidence Les Oliviers',
        ])
    if slug == 'velo':
        return random.choice(['Trek FX', 'Brompton C Line', 'Decathlon Riverside'])
    if slug == 'outillage':
        return random.choice(['Bosch Professional GSR', 'Makita DHP', 'DeWalt DCD'])
    if slug == 'electronique':
        return random.choice(['Apple MacBook Air', 'Samsung Galaxy Tab', 'Sony WH-1000XM'])
    return fake.company()


class Command(BaseCommand):
    help = 'Generate fake data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Generating fake data...')
        
        # Create categories
        categories_data = [
            {'name': 'Voiture', 'slug': 'voiture', 'icon': 'fa-car'},
            {'name': 'Appartement', 'slug': 'appartement', 'icon': 'fa-house'},
            {'name': 'Vélo', 'slug': 'velo', 'icon': 'fa-bicycle'},
            {'name': 'Outillage', 'slug': 'outillage', 'icon': 'fa-wrench'},
            {'name': 'Électronique', 'slug': 'electronique', 'icon': 'fa-laptop'},
        ]
        
        categories = []
        for cat_data in categories_data:
            slug = cat_data['slug']
            defaults = {
                **cat_data,
                'hint_nom_reference': CATEGORY_HINTS.get(slug, ''),
            }
            cat, created = Category.objects.get_or_create(
                slug=slug,
                defaults=defaults
            )
            if not created and not cat.hint_nom_reference:
                cat.hint_nom_reference = CATEGORY_HINTS.get(slug, '')
                cat.save(update_fields=['hint_nom_reference'])
            categories.append(cat)
            if created:
                self.stdout.write(f'Created category: {cat.name}')
        
        # Create users
        users = []
        for i in range(10):
            is_owner = i < 5
            username = f'user_{i}'
            email = f'user_{i}@example.com'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'phone': fake.phone_number(),
                    'address': fake.address(),
                    'is_proprietaire': is_owner,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                users.append(user)
                self.stdout.write(f'Created user: {username}')
            else:
                users.append(user)
        
        owners = [u for u in users if u.is_proprietaire]
        renters = [u for u in users if not u.is_proprietaire]
        
        # Create properties
        properties = []
        for i in range(15):
            owner = random.choice(owners)
            category = random.choice(categories)
            
            slug = category.slug if category else ''
            property_obj, created = Property.objects.get_or_create(
                titre=f'Annonce {i} — {fake.catch_phrase()[:40]}',
                defaults={
                    'nom_reference_categorie': _exemple_nom_reference(slug),
                    'description': fake.text(),
                    'prix_jour': random.randint(10, 100),
                    'prix_semaine': random.randint(50, 500),
                    'prix_mois': random.randint(200, 1500),
                    'caution': random.randint(50, 200),
                    'disponibilite': random.choice([True, True, False]),
                    'localisation': fake.city(),
                    'category': category,
                    'proprietaire': owner,
                }
            )
            if created:
                properties.append(property_obj)
                self.stdout.write(f'Created property: {property_obj.titre}')
            else:
                properties.append(property_obj)
        
        # Create availabilities
        for i in range(20):
            property_obj = random.choice(properties)
            date_debut = fake.date_between(start_date='today', end_date='+30d')
            date_fin = date_debut + timedelta(days=random.randint(1, 14))
            
            Disponibilite.objects.create(
                property=property_obj,
                date_debut=date_debut,
                date_fin=date_fin,
                disponible=random.choice([True, False])
            )
            self.stdout.write(f'Created availability for {property_obj.titre}')
        
        # Create reservations
        reservations = []
        for i in range(10):
            renter = random.choice(renters)
            property_obj = random.choice(properties)
            date_debut = fake.date_between(start_date='today', end_date='+30d')
            date_fin = date_debut + timedelta(days=random.randint(1, 7))
            statut = random.choice(['pending', 'accepted', 'refused', 'cancelled', 'completed'])
            
            reservation, created = Reservation.objects.get_or_create(
                utilisateur=renter,
                objet=property_obj,
                date_debut=date_debut,
                date_fin=date_fin,
                defaults={
                    'statut': statut,
                    'contrat_accepte': True,
                    'message_locataire': fake.text(),
                }
            )
            if created:
                reservations.append(reservation)
                self.stdout.write(f'Created reservation for {property_obj.titre}')
            else:
                reservations.append(reservation)
        
        # Create payments
        for i in range(8):
            if i < len(reservations):
                reservation = reservations[i]
                statut = random.choice(['completed', 'pending'])
                
                Paiement.objects.get_or_create(
                    reservation=reservation,
                    defaults={
                        'montant': reservation.calculer_montant_total(),
                        'caution': reservation.objet.caution,
                        'statut': statut,
                    }
                )
                self.stdout.write(f'Created payment for reservation {reservation.id}')
        
        # Create reviews
        for i in range(10):
            if i < len(reservations):
                reservation = reservations[i]
                if reservation.statut == 'completed':
                    auteur = reservation.utilisateur
                    cible = reservation.objet.proprietaire
                    
                    Avis.objects.get_or_create(
                        auteur=auteur,
                        reservation=reservation,
                        defaults={
                            'cible': cible,
                            'note': random.randint(1, 5),
                            'commentaire': fake.text(),
                        }
                    )
                    self.stdout.write(f'Created review by {auteur.username}')
        
        # Create messages
        for i in range(5):
            property_obj = random.choice(properties)
            participants = random.sample(users, 2)
            
            conversation, created = Conversation.objects.get_or_create(
                property=property_obj
            )
            if created:
                conversation.participants.set(participants)
            
            Message.objects.create(
                conversation=conversation,
                contenu=fake.text(),
                expediteur=random.choice(participants)
            )
            self.stdout.write(f'Created message')
        
        self.stdout.write(self.style.SUCCESS('Fake data generated successfully!'))
