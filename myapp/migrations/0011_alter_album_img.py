# Generated by Django 5.0.7 on 2024-07-30 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_alter_album_img_alter_music_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='myapp/static/img/albums/'),
        ),
    ]
