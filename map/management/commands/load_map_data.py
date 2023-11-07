import os
import csv
from pathlib import Path
from map.models import ParkingSpace
from django.core.management.base import BaseCommand

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
csv_file_path = os.path.join(BASE_DIR, "data/result.csv")


class Command(BaseCommand):
    """create an admin user"""

    def handle(self, *args, **options):
        print("csv file path is:", csv_file_path)
        with open(csv_file_path, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                ParkingSpace.objects.create(
                    latitude=row["Latitude"],
                    longitude=row["Longitude"],
                    address_zip=row["Address ZIP"],
                    business_name=row["Business Name"],
                    dca_license_number=row["DCA License Number"],
                )
