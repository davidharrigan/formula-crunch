import numpy as np
import pandas as pd
import fastf1 as ff1
import json

from scrape.core import Session

__all__ = ["get_driver_summary"]


def get_driver_summary(session: Session) -> pd.DataFrame:
    df = session.results[
        [
            "DriverNumber",
            "Position",
            "GridPosition",
            "Status",
            "Points",
        ]
    ]

    # Get points data
    df = df.reindex(columns=df.columns.tolist() + ["SeasonPoints", "SeasonStanding"])
    res = ff1.Cache.requests_get(
        ff1.api.base_url + session.api_path + "ChampionshipPrediction.json"
    )
    if res.status_code != 200:
        raise Excepption(f"expected 200 status, got: {res.status_code}")

    decoded = res.text.encode().decode("utf-8-sig")
    content = json.loads(decoded)["Drivers"]
    for idx, row in df.iterrows():
        item = content[row["DriverNumber"]]
        df.at[idx, "SeasonPoints"] = item["PredictedPoints"]
        df.at[idx, "SeasonStanding"] = item["PredictedPosition"]

    return df
