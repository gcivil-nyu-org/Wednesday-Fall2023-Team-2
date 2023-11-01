import csv
import os
from ..models import ParkingSpace
from django.conf import settings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
csv_file_path = os.path.join(BASE_DIR, "data/result.csv")

def run():
    print("csv file path is:", csv_file_path)
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ParkingSpace.objects.create(dca_license_number=row['DCA License Number'],
                                        address_zip=row['Address ZIP'],
                                        longitude=row['Longitude'],
                                        latitude=row['Latitude'],
                                        business_name=row['Business Name'])


