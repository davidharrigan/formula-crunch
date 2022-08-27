import fastf1 as ff1
import pandas as pd

from scrape.core import Session

__all__ = ["get_stint_summary"]


def get_stint_summary(session: Session) -> pd.DataFrame:
    df = session.laps.query("IsAccurate == True")
    df = df[~df["LapTime"].isnull()]
    gb = df.groupby(["DriverNumber", "Stint"])

    time = (
        gb.agg(
            minidx=("LapTime", "idxmin"),
            AverageTime=("LapTime", "mean"),
            Compound=("Compound", "unique"),
        )
        .join(df[["LapNumber", "LapTime"]], on="minidx")
        .rename(columns={"LapNumber": "FastestLap", "LapTime": "FastestLapTime"})
        .drop(columns=["minidx"])
        .reset_index()
    )

    df = session.laps
    gb = df.groupby(["DriverNumber", "Stint"])
    lap_count = gb.agg(LapCount=("LapNumber", "count")).reset_index()

    time = time.merge(
        lap_count, left_on=["DriverNumber", "Stint"], right_on=["DriverNumber", "Stint"]
    )

    for i, t in time.iterrows():
        compounds = [c for c in t.Compound if c != "UNKNOWN"]
        compound = "UNKNOWN"
        if len(compounds) == 1:
            compound = compounds[0]
        time.at[i, "Compound"] = compound

    return time
