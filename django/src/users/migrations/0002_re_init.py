# Generated by Django 4.2.7 on 2024-03-10 06:08

import uuid

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="public_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(choices=[("ADMIN", "Admin"), ("WORKER", "Worker")], default="WORKER", max_length=100),
        ),
    ]
