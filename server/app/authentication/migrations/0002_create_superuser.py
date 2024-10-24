# Generated by Django 5.1.2 on 2024-10-24 06:30

import os

from django.db import migrations


def generate_superuser(apps, schema_editor):
    User = apps.get_model("authentication", "User")

    username = os.getenv("DJANGO_SUPERUSER_USERNAME")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
    admin = User.objects.create_superuser(username, password=password)

    admin.creator = admin
    admin.editor = admin
    admin.save()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("authentication", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            generate_superuser,
            reverse_code=migrations.RunPython.noop,
            atomic=True,
        ),
    ]
