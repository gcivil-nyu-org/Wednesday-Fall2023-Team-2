# Generated by Django 4.2.6 on 2023-11-15 13:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("map", "0004_parkingspace_occupancy_percent"),
    ]

    operations = [
        migrations.AddField(
            model_name="parkingspace",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
