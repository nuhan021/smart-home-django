# Generated by Django 5.1.5 on 2025-04-03 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control_pin', '0004_pin_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='pin',
            name='pin_16',
            field=models.BooleanField(default=False),
        ),
    ]
