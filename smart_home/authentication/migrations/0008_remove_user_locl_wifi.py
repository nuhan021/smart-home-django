# Generated by Django 5.1.5 on 2025-03-23 16:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_alter_user_locl_wifi'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='locl_wifi',
        ),
    ]
