from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group
from django.apps import apps
from django.core.management import call_command

def create_default_data(sender, **kwargs):
    if apps.is_installed("myapp"):
        Album = apps.get_model('myapp', 'Album')
        Album.objects.get_or_create(name='Ninguno')
        
        Genre = apps.get_model('myapp', 'Genre')
        Genre.objects.get_or_create(name='Rock')
        Genre.objects.get_or_create(name='Pop')
        Genre.objects.get_or_create(name='Electronica')
        Genre.objects.get_or_create(name='Metal')
        Genre.objects.get_or_create(name='Folk')
        Genre.objects.get_or_create(name='Clasica')
        Genre.objects.get_or_create(name='Jazz')
        Genre.objects.get_or_create(name='Blues')
        Genre.objects.get_or_create(name='Hip Hop')
        Genre.objects.get_or_create(name='Country')
        Genre.objects.get_or_create(name='Punk')
        Genre.objects.get_or_create(name='Rap')

post_migrate.connect(create_default_data)