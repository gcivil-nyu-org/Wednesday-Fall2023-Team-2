# Generated by Django 4.2.6 on 2023-11-05 03:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("map", "0002_remove_parkingspace_id_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="parkingspace",
            old_name="dca_license_number",
            new_name="parking_spot_id",
        ),
        migrations.RenameField(
            model_name="parkingspace",
            old_name="business_name",
            new_name="parking_spot_name",
        ),
        migrations.AddField(
            model_name="parkingspace",
            name="borough",
            field=models.CharField(default="unknown", max_length=200),
        ),
        migrations.AddField(
            model_name="parkingspace",
            name="detail",
            field=models.CharField(default="unknown", max_length=200),
        ),
        migrations.AddField(
            model_name="parkingspace",
            name="operation_hours",
            field=models.CharField(default="unknown", max_length=200),
        ),
        migrations.AddField(
            model_name="parkingspace",
            name="type",
            field=models.CharField(default="unknown", max_length=200),
        ),
    ]