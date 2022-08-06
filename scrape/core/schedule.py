import datetime
import fastf1 as ff1
import pandas as pd

from scrape.data import DataMapping, flatten

__all__ = ["get_drivers", "add_driver_id_or_number"]


def get_schedule(year: int) -> pd.DataFrame:
    URL = "https://ergast.com/api/f1/{year}.json"
    mapping: dict[str, DataMapping] = {
        "Circuit.circuitId": DataMapping("CircuitID", str),
        "Circuit.Location.locality": DataMapping("Locality", str),
        "date": DataMapping("Date", datetime.date),
    }

    url = URL.format(year=year)

    res = ff1.api.Cache.requests_get(url)
    if res.status_code != 200:
        raise Exception(f"expected 200 status, got: {res.status_code}")

    content = res.json()["MRData"]["RaceTable"]["Races"]
    events = []
    for item in content:
        flattened = flatten(item)
        data = {}
        for key, dm in mapping.items():
            data[dm.column] = dm.transform(flattened[key])
        events.append(data)

    df = pd.DataFrame(data=events)
    return df
