from django.db import migrations


HINTS = {
    'voiture': 'Marque / modèle (ex. Nissan Qashqai)',
    'appartement': 'Nom de la résidence ou du bien (ex. Résidence Les Oliviers)',
    'velo': 'Marque ou modèle (ex. Trek FX 2)',
    'outillage': 'Marque ou référence (ex. Bosch Professional)',
    'electronique': 'Marque ou modèle (ex. Apple MacBook Air)',
}


def forwards(apps, schema_editor):
    Category = apps.get_model('properties', 'Category')
    for slug, hint in HINTS.items():
        Category.objects.filter(slug=slug).update(hint_nom_reference=hint)


def backwards(apps, schema_editor):
    Category = apps.get_model('properties', 'Category')
    for slug in HINTS:
        Category.objects.filter(slug=slug).update(hint_nom_reference='')


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0003_category_hint_nom_reference_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
