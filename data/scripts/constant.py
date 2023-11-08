import os

from preprocess_utils import _partialDatetime


PRIMARY_KEY_COLUMNS = ["DCA License Number"]


PARKING_LIST_CSV_FILE_PATH1 = os.path.join(os.getcwd(), "../parking_list.csv")
PARKING_LIST_CSV_FILE_PATH2 = os.path.join(os.getcwd(), "../parking_list2.csv")

PARKING_LIST1_COLUMNS = [
    {"name": "Address ZIP", "required": True, "type": str},
    {"name": "License Type", "required": False, "type": str},
    {"name": "Address City", "required": True, "type": str},
    {"name": "Borough Code", "required": False, "type": str},
    {"name": "Business Name", "required": True, "type": str},
    {"name": "Address State", "required": True, "type": str},
    {"name": "Business Name 2", "required": False, "type": str},
    {"name": "Address Borough", "required": True, "type": str},
    {"name": "Address Building", "required": True, "type": str},
    {"name": "DCA License Number", "required": True, "type": str},
    {"name": "Address Street Name", "required": True, "type": str},
    {"name": "Contact Phone Number", "required": False, "type": str},
    {"name": "Secondary Address Street Name", "required": False, "type": str},
    {
        "required": True,
        "name": "License Expiration Date",
        "type": _partialDatetime(),
    },
]

PARKING_LIST2_COLUMNS = [
    {"name": "BIN", "required": False, "type": str},
    {"name": "BBL", "required": False, "type": str},
    {"name": "NTA", "required": False, "type": str},
    {"name": "Detail", "required": False, "type": str},
    {"name": "Industry", "required": False, "type": str},
    {"name": "Latitude", "required": True, "type": float},
    {"name": "Location", "required": False, "type": str},
    {"name": "Longitude", "required": True, "type": float},
    {"name": "Address ZIP", "required": False, "type": str},
    {"name": "Address City", "required": False, "type": str},
    {"name": "Borough Code", "required": False, "type": str},
    {"name": "Census Tract", "required": False, "type": str},
    {"name": "Business Name", "required": True, "type": str},
    {"name": "Address State", "required": False, "type": str},
    {"name": "Business Name 2", "required": False, "type": str},
    {"name": "Address Borough", "required": False, "type": str},
    {"name": "Community Board", "required": False, "type": str},
    {"name": "Address Building", "required": False, "type": str},
    {"name": "Council District", "required": False, "type": str},
    {"name": "DCA License Number", "required": True, "type": str},
    {"name": "Address Street Name", "required": False, "type": str},
    {"name": "Contact Phone Number", "required": False, "type": str},
    {"name": "Secondary Address Street Name", "required": False, "type": str},
    {
        "name": "License Creation Date",
        "required": False,
        "type": _partialDatetime(),
    },
    {
        "name": "License Expiration Date",
        "required": True,
        "type": _partialDatetime(),
    },
]
