"""
Data migration: seeds the Campus table with sample universities.
"""
from django.db import migrations


def seed_campuses(apps, schema_editor):
    Campus = apps.get_model('core', 'Campus')
    campuses = [
        ('University of Nairobi', 'Nairobi, Kenya'),
        ('Kenyatta University', 'Nairobi, Kenya'),
        ('Strathmore University', 'Nairobi, Kenya'),
        ('USIU Africa', 'Nairobi, Kenya'),
        ('Daystar University', 'Nairobi, Kenya'),
        ('Moi University', 'Eldoret, Kenya'),
        ('Egerton University', 'Nakuru, Kenya'),
        ('Maseno University', 'Kisumu, Kenya'),
        ('Makerere University', 'Kampala, Uganda'),
        ('University of Dar es Salaam', 'Dar es Salaam, Tanzania'),
        ('University of Cape Town', 'Cape Town, South Africa'),
        ('Wits University', 'Johannesburg, South Africa'),
        ('University of Ghana', 'Accra, Ghana'),
        ('MIT', 'Cambridge, USA'),
        ('Harvard University', 'Cambridge, USA'),
        ('Stanford University', 'Stanford, USA'),
        ('University of Oxford', 'Oxford, UK'),
        ('University of Cambridge', 'Cambridge, UK'),
        ('Technical University of Kenya', 'Nairobi, Kenya'),
        ('Multimedia University of Kenya', 'Nairobi, Kenya'),
    ]
    for name, location in campuses:
        Campus.objects.get_or_create(name=name, defaults={'location': location})


def unseed_campuses(apps, schema_editor):
    pass  # No rollback needed for seed data


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_campuses, unseed_campuses),
    ]
