# Generated by Django 5.0.7 on 2024-09-30 16:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0018_followed_artists_liked_albums_liked_songs'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Liked_songs',
            new_name='Liked_musics',
        ),
    ]
