import pandas as pd

business_parking = pd.read_csv(
    "../result.csv",
    usecols=[
        "DCA License Number",
        "License Type",
        "Business Name",
        "Longitude",
        "Latitude",
        "Address ZIP",
        "Address Borough",
        "Detail",
    ],
)
street_parking = pd.read_csv(
    "../street_parking_list.csv",
    usecols=[
        "Meter Number",
        "Facility",
        "Longitude",
        "Latitude",
        "Zip Codes",
        "Borough",
        "Meter_Hours",
    ],
)

business_parking["operation_hours"] = "unknown"
street_parking["type"] = "Street"
street_parking["parking_spot_name"] = ""

business_col_name_mapping = {
    "DCA License Number": "parking_spot_id",
    "License Type": "type",
    "Business Name": "parking_spot_name",
    "Longitude": "longitude",
    "Latitude": "latitude",
    "Address ZIP": "address_zip",
    "Address Borough": "borough",
    "Detail": "detail",
}

street_col_name_mapping = {
    "Meter Number": "parking_spot_id",
    "Longitude": "longitude",
    "Latitude": "latitude",
    "Zip Codes": "address_zip",
    "Borough": "borough",
    "Meter_Hours": "operation_hours",
    "Facility": "detail",
}

business_parking.rename(columns=business_col_name_mapping, inplace=True)
street_parking.rename(columns=street_col_name_mapping, inplace=True)

concat_result = pd.concat(
    [business_parking, street_parking], ignore_index=True, sort=False
)
# remove rows with no zip code
concat_result = concat_result[concat_result["address_zip"].notnull()]
concat_result["address_zip"] = concat_result["address_zip"].astype(int)
concat_result.to_csv("../concat_result.csv", index=False)
