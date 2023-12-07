# Generated by Django 4.2.6 on 2023-12-05 18:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("map", "0009_parkingspace_available_vehicle_spaces"),
        ("users", "0005_alter_userverification_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserWatchedParkingSpace",
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
                ("threshold", models.IntegerField(default=80)),
                (
                    "parking_space",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="map.parkingspace",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
