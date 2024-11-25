# Generated by Django 5.0.7 on 2024-10-16 17:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0025_rename_artist_followed_artists_artists'),
    ]

    operations = [
        migrations.CreateModel(
            name='L_musics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('list_music', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.music')),
                ('list_musics', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.list')),
            ],
        ),
        migrations.RemoveField(
            model_name='list',
            name='musics',
            field=models.ManyToManyField(through='myapp.L_musics', to='myapp.music'),
        ),
        migrations.AddField(
            model_name='list',
            name='musics',
            field=models.ManyToManyField(through='myapp.L_musics', to='myapp.music'),
        ),
    ]
