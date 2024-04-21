# Generated by Django 5.0.4 on 2024-04-21 12:34

import django.db.models.deletion
import phonenumber_field.modelfields
import user.services
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "mobile",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=11, region=None, unique=True
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="CallbackToken",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_active", models.BooleanField(default=True)),
                ("to_alias", models.CharField(blank=True, max_length=254)),
                ("to_alias_type", models.CharField(blank=True, max_length=20)),
                (
                    "key",
                    models.CharField(
                        default=user.services.generate_numeric_token, max_length=4
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("AUTH", "Auth"), ("VERIFY", "Verify")], max_length=20
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="callback_tokens",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Callback Token",
                "ordering": ["-id"],
                "get_latest_by": "created_at",
                "abstract": False,
            },
        ),
    ]
