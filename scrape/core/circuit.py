import fastf1 as ff1
import pandas as pd
from scrape.data import DataMapping, flatten

__all__ = ["get_circuits"]


def get_circuits(year: int) -> pd.DataFrame:
    mapping: dict[str, DataMapping] = {
        "circuitId": DataMapping("CircuitID", str),
        "circuitName": DataMapping("Name", str),
        "Location.locality": DataMapping("Locality", str),
        "Location.country": DataMapping("Country", str),
    }

    url = "https://ergast.com/api/f1/{year}/circuits.json".format(year=year)

    res = ff1.api.Cache.requests_get(url)
    if res.status_code != 200:
        raise Exception(f"expected 200 status, got: {res.status_code}")

    content = res.json()["MRData"]["CircuitTable"]["Circuits"]
    circuits = []
    for item in content:
        data = {}
        flattened = flatten(item)
        for key, dm in mapping.items():
            data[dm.column] = dm.transform(flattened[key])
        circuits.append(data)
    return pd.DataFrame(data=circuits)
