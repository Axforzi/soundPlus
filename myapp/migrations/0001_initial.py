# Generated by Django 5.0.7 on 2024-07-12 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Music',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('artist', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=100)),
                ('album', models.CharField(max_length=100)),
            ],
        ),
    ]