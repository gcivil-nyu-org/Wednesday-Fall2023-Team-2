import csv
from ..models import ParkingSpace
from django.conf import settings

def run():
    csv_file_path = "./scripts/Active_DCA-Licensed_Garages_and_Parking_Lots.csv"
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ParkingSpace.objects.create(dca_license_number=row['DCA License Number'],
                                        address_zip=row['Address ZIP'],
                                        longitude=row['Longitude'],
                                        latitude=row['Latitude'],
                                        business_name=row['Business Name'])


run()