# Generated by Django 5.0.7 on 2024-08-02 15:40

import myapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_music_song_alter_music_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='img',
            field=models.ImageField(upload_to=myapp.models.albums_directory),
        ),
    ]
