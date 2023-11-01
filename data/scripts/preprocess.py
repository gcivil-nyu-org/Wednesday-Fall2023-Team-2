import os
import csv
import argparse

from preprocess_utils import (
    join,
    parse_data,
    save_csv_file,
    filter_invalid_rows,
    filter_license_expired_rows,
)
from constant import (
    PRIMARY_KEY_COLUMNS,
    PARKING_LIST1_COLUMNS,
    PARKING_LIST2_COLUMNS,
    PARKING_LIST_CSV_FILE_PATH1,
    PARKING_LIST_CSV_FILE_PATH2,
)

# * Initialize the Parser
parser = argparse.ArgumentParser(description="Preprocess command line config interface")

# * Adding Arguments
parser.add_argument(
    "-d",
    "--destination",
    type=str,
    default=os.getcwd(),
    help="Specify a folder to save preprocess results",
)
parser.add_argument(
    "-n",
    "--name",
    type=str,
    default="../result.csv",
    help="Specify the file name to save the result as",
)
parser.add_argument(
    "-s",
    "--save",
    type=bool,
    default=True,
    help="Whether to save intermediate files",
)

args = parser.parse_args()
SAVE_PATH = os.path.abspath(os.path.join(args.destination, args.name))

print(">>> Processing...\n")


print(f">>> Working on {PARKING_LIST_CSV_FILE_PATH1}")
parkingListCSV1 = []
with open(PARKING_LIST_CSV_FILE_PATH1, "r") as f:
    parkingListCSV1 = list(csv.DictReader(f))
    print(f">>> Finished reading CSV file at '{PARKING_LIST_CSV_FILE_PATH1}'")

    parkingListCSV1 = filter_invalid_rows(parkingListCSV1, PARKING_LIST1_COLUMNS)
    print(">>> Finished filtering invalid rows")

    parkingListCSV1 = parse_data(parkingListCSV1, PARKING_LIST1_COLUMNS)
    print(">>> Finished parsing data to corresponding type")

    parkingListCSV1 = filter_license_expired_rows(parkingListCSV1)
    print(">>> Finished filtering out parking lots whose license has expired\n")

if args.save:
    save_csv_file(f"{PARKING_LIST_CSV_FILE_PATH1[:-4]}_processed.csv", parkingListCSV1)

print(f">>> Working on {PARKING_LIST_CSV_FILE_PATH2}")
parkingListCSV2 = []
with open(PARKING_LIST_CSV_FILE_PATH2, "r") as f:
    parkingListCSV2 = list(csv.DictReader(f))
    print(f">>> Finished reading CSV file at '{PARKING_LIST_CSV_FILE_PATH2}'")

    parkingListCSV2 = filter_invalid_rows(parkingListCSV2, PARKING_LIST2_COLUMNS)
    print(">>> Finished filtering invalid rows")

    parkingListCSV2 = parse_data(parkingListCSV2, PARKING_LIST2_COLUMNS)
    print(">>> Finished parsing data to corresponding type")

    parkingListCSV2 = filter_license_expired_rows(parkingListCSV2)
    print(">>> Finished filtering out parking lots whose license has expired\n")

if args.save:
    save_csv_file(f"{PARKING_LIST_CSV_FILE_PATH2[:-4]}_processed.csv", parkingListCSV2)

print(">>> Joining tables...\n")
parkingList = join(parkingListCSV1, parkingListCSV2, PRIMARY_KEY_COLUMNS)

save_csv_file(SAVE_PATH, parkingList)

print(">>> Preprocess finished")
