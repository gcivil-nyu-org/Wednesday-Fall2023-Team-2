import os
import csv
from tqdm import tqdm
from pathlib import Path
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand

from map.models import ParkingSpace

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
csv_file_path = os.path.join(BASE_DIR, "data/concat_result.csv")


class Command(BaseCommand):
    """load latest data and merge into database"""

    def handle(self, *args, **options):
        print(f"csv file path is: {csv_file_path}")

        count = 0
        with open(csv_file_path, "r") as file:
            reader = csv.DictReader(file)
            for row in tqdm(reader):
                try:
                    ParkingSpace.objects.create(
                        type=row["type"],
                        detail=row["detail"],
                        borough=row["borough"],
                        latitude=row["latitude"],
                        longitude=row["longitude"],
                        address_zip=row["address_zip"],
                        operation_hours=row["operation_hours"],
                        parking_spot_id=row["parking_spot_id"],
                        parking_spot_name=row["parking_spot_name"],
                    )
                    count += 1
                except IntegrityError:
                    print(f"Skipping Parking Space Record[{row['parking_spot_id']}]")
        print(f"{count} records added!")
