import fastf1 as ff1
import pandas as pd
import numpy as np

from scrape.core import Session


def __interval_to_timedelta(x):
    """
    Convert interval (formatted as +xx:xx) to timedelta
    """
    if isinstance(x, str):
        return ff1.utils.to_timedelta(x.lstrip("+"))


def get_lap_start_end_time(lap: ff1.core.Lap) -> tuple[pd.Timedelta, pd.Timedelta]:
    """
    Returns start and end time of the given lap.
    """
    lap_time = lap["LapTime"]
    lap_start = lap["LapStartTime"]
    lap_end = lap_start + lap_time

    # replace null time with 0
    if pd.isnull(lap_start):
        lap_start = pd.Timedelta(0, "s")
    return lap_start, lap_end


def get_position_at_lap(lap: ff1.core.Lap, timing_data: pd.DataFrame) -> tuple[int, int]:
    """
    Returns driver position at the start and end of the lap.

    timing_data should be a DataFrame containing Time and Positiion data (ff1.api.timing_data)
    """
    lap_start, lap_end = get_lap_start_end_time(lap)

    # if there is no exact match, get closest
    closest_idx_lap_start = timing_data[timing_data["Time"] >= lap_start]["Time"].idxmin()
    position_at_start = timing_data.iloc[closest_idx_lap_start]["Position"]

    closest_idx_lap_end = timing_data[timing_data["Time"] >= lap_end]["Time"].idxmin()
    position_at_end = timing_data.iloc[closest_idx_lap_end]["Position"]

    return (position_at_start, position_at_end)


def add_lap_number_to_timing_data(laps: ff1.core.Laps, timing_data: pd.DataFrame) -> pd.DataFrame:
    """
    Adds LapNumber column to the timing_data.
    """
    laps = laps.reset_index(drop=True)
    if len(laps["DriverNumber"].unique()) != 1:
        raise Exception("Expected only 1 driver in given laps")

    df = timing_data.copy()

    if "LapNumber" not in df:
        df["LapNumber"] = np.nan

    for idx, t in laps.iterlaps():
        lap_number = str(idx + 1)
        lap_start, lap_end = get_lap_start_end_time(t)
        matching = df[(lap_start <= df["Time"]) & (lap_end > df["Time"])]
        for ii, m in matching.iterrows():
            df.at[ii, "LapNumber"] = lap_number

    return df


def merge_leader_lap(
    target: pd.DataFrame, laps: ff1.core.Laps, timing_data: pd.DataFrame, target_time_column="Time"
) -> pd.DataFrame:
    target = target.copy()
    target["LapLeader"] = np.nan
    for idx, t in target.iterrows():
        time = t["Time"]
        leader = get_driver_at_position(time, 1, timing_data)
        if leader:
            leader_lap = get_lap_at_time(time, laps.pick_driver(leader))
            if leader_lap is not None:
                target.at[idx, "LapLeader"] = str(leader_lap.LapNumber)
    return target
