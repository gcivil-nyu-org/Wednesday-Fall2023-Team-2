import csv
import os
from ..models import ParkingSpace
from django.conf import settings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
csv_file_path = os.path.join(BASE_DIR, "data/concat_result.csv")


def run():
    print("csv file path is:", csv_file_path)
    with open(csv_file_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            ParkingSpace.objects.create(
                parking_spot_id=row["parking_spot_id"],
                address_zip=row["address_zip"],
                longitude=row["longitude"],
                latitude=row["latitude"],
                parking_spot_name=row["parking_spot_name"],
                type=row["type"],
                borough=row["borough"],
                detail=row["detail"],
                operation_hours=row["operation_hours"],
            )
