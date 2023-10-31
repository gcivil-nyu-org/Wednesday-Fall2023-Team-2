import csv

from tqdm import tqdm
from datetime import datetime
from typing import List, Dict, Callable


def _partialDatetime(datetimePatternStr: str = "%m/%d/%Y") -> Callable[[str], str]:
    """higher order function for datetime.strptime with datatime format specified

    Args:
        datetimePatternStr (str): the datetime pattern string

    Returns:
        Callable[[str], str]: wrapped datetime.strptime
    """
    return lambda datetimeStr: datetime.strptime(datetimeStr, datetimePatternStr).date()


def filter_invalid_rows(
    data: List[Dict[str, str]], columns: List[tuple]
) -> List[Dict[str, str]]:
    """filter out invalid rows and return the new data

    Args:
        data (List[Dict[str, str]]): data in the form of of a list of dictionaries
        columns (List[tuple]): refer to .constant.PARKING_LIST_COLUMNS

    Returns:
        List[Dict[str, str]]: data list after filtering out invalid rows
    """
    # * swap invalid rows to the end of the data list
    slowIdx = 0
    fastIdx = len(data) - 1
    while slowIdx <= fastIdx:
        row = data[slowIdx]
        retain = True
        for column in columns:
            if not column["required"] or row[column["name"]]:
                continue
            retain = False
            break
        if not retain:
            data[slowIdx], data[fastIdx] = data[fastIdx], data[slowIdx]
            fastIdx -= 1
            continue

        slowIdx += 1

    # * chop out invalid rows
    print(
        f"> # of rows before filtering: {len(data)}\n> # of rows after filtering: {slowIdx}"
    )
    return data[:slowIdx]


def parse_data(
    data: List[Dict[str, str]], columns: List[tuple]
) -> List[Dict[str, str]]:
    """parse data to their corresponding type

    Args:
        data (List[Dict[str, str]]): data in the form of of a list of dictionaries
        columns (List[tuple]): refer to .constant.PARKING_LIST_COLUMNS

    Returns:
        List[Dict[str, str]]: data list with each row parsed
    """
    for row in tqdm(data):
        for column in columns:
            row[column["name"]] = column["type"](row[column["name"]])

    return data


def filter_license_expired_rows(
    data: List[Dict[str, str]], column_name: str = "License Expiration Date"
) -> List[Dict[str, str]]:
    # * swap rows whose license is expired to the end of the data list
    slowIdx = 0
    fastIdx = len(data) - 1
    today = datetime.now().date()
    while slowIdx <= fastIdx:
        row = data[slowIdx]
        if row[column_name] < today:
            data[slowIdx], data[fastIdx] = data[fastIdx], data[slowIdx]
            fastIdx -= 1
            continue

        slowIdx += 1

    # * chop out invalid rows
    print(
        f"> # of rows before filtering: {len(data)}\n> # of rows after filtering: {slowIdx}"
    )
    return data[:slowIdx]


def join(
    data1: List[Dict[str, str]], data2: List[Dict[str, str]], pks: List[str]
) -> List[Dict[str, str]]:
    """join two data list, use the latter (data2) as the source of truth if conflict content encountered

    Args:
        data1 (List[Dict[str, str]]): data list 1
        data2 (List[Dict[str, str]]): data list 2
        pk (List[str]): names of the columns to use as primary keys

    Returns:
        List[Dict[str, str]]: joined data list
    """
    result = []
    print(f"> # of rows in data1 {len(data1)}\n> # of rows in data2 {len(data2)}")
    for rowData1 in tqdm(data1):
        for rowData2 in data2:
            # * check all pk columns
            isMatch = True
            for pk in pks:
                if rowData1[pk] == rowData2[pk]:
                    continue
                isMatch = False
                break
            if not isMatch:
                continue

            # * if all match, join the two rows
            joinedRow = {}
            for key1 in rowData1.keys():
                joinedRow[key1] = rowData1[key1]
            for key2 in rowData2.keys():
                joinedRow[key2] = rowData2[key2]

            result.append(joinedRow)

    print(f"> # of rows after joining with key '{pk}': {len(result)}")
    return result


def save_csv_file(savePath: str, csvContent: List[Dict[str, str]]) -> bool:
    print(f">>> Saving file to {savePath}\n")
    try:
        with open(savePath, "w") as f:
            # * creating a csv dict writer object
            writer = csv.DictWriter(f, list(csvContent[0].keys()))

            # * writing headers (field names)
            writer.writeheader()

            # * writing data rows
            writer.writerows(csvContent)
        return True
    except Exception as e:
        print(e)
        return False
