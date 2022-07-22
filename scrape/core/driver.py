import datetime
import fastf1 as ff1
import pandas as pd

from scrape.data import DataMapping

__all__ = ["get_drivers", "add_driver_id_or_number"]


def get_drivers(year: int) -> pd.DataFrame:
    URL = "https://ergast.com/api/f1/{year}/drivers.json"
    mapping: dict[str, DataMapping] = {
        "driverId": DataMapping("DriverID", str),
        "permanentNumber": DataMapping("PermanentNumber", str),
        "code": DataMapping("Code", str),
        "givenName": DataMapping("FirstName", str),
        "familyName": DataMapping("LastName", str),
        "dateOfBirth": DataMapping("Birthday", datetime.date),
        "nationality": DataMapping("Nationality", str),
    }

    url = URL.format(year=year)

    res = ff1.api.Cache.requests_get(url)
    if res.status_code != 200:
        raise Exception(f"expected 200 status, got: {res.status_code}")

    content = res.json()["MRData"]["DriverTable"]["Drivers"]
    drivers = []
    for item in content:
        data = {}
        for key, dm in mapping.items():
            data[dm.column] = dm.transform(item[key])
        drivers.append(data)

    df = pd.DataFrame(data=drivers)
    df["DriverNumber"] = df["PermanentNumber"]
    cols = df.columns.tolist()
    df = df[cols[0:1] + cols[-1:] + cols[1:-1]]
    if year == 2022:
        df.loc[df["Code"] == "VER", "DriverNumber"] = "1"
    return df


def add_driver_id_or_number(target: pd.DataFrame, source: pd.DataFrame) -> pd.DataFrame:
    """
    Add DriverID or DriverNumber column to the target DataFrame from the source DataFrame containing both information.
    """
    cols = target.columns
    if "DriverNumber" in cols:
        on = "DriverNumber"
        added = "DriverID"
        idx = 0
    elif "DriverID" in cols:
        on = "DriverID"
        added = "DriverNumber"
        idx = 1
    else:
        raise Exception("expected one of DriverNumber or DriverID")

    target = target.merge(source[["DriverNumber", "DriverID"]], on=on, how="left")
    target = target[cols.insert(idx, added)]
    return target
