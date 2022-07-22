import fastf1 as ff1
import pandas as pd
import numpy as np

from scrape.race.timing import (
    get_timing_data,
    add_lap_number_to_timing_data,
    get_lap_start_end_time,
    get_lap_at_time,
    get_position_at_lap,
)
from scrape.race.pit import is_time_during_pit

__all__ = ["get_overtakes", "get_driver_overtakes"]


def get_overtakes(session: ff1.core.Session) -> pd.DataFrame:
    """
    Returns overtakes that occurred during a session.

    TODO:
    Pit data from the fastf1 library currently isn't very accurate. To make it a
    little more accurate, the raw timing data should be examined.
    SectorSegmentStatus 2064 can be used to determine when a driver is entering
    the pit lane. More information on this in notebooks/raw_timing_data.ipynb
    """
    dfs = []
    timing = get_timing_data(session)
    for driver in session.drivers:
        dfs.append(get_driver_overtakes(session, timing, driver))
    return pd.concat(dfs).reset_index(drop=True)


def get_driver_overtakes(
    session: ff1.core.Session, timing: pd.DataFrame, driver_number: str
) -> pd.DataFrame:
    """
    Returns overtakes performed by the given driver.

    The following columns are present in the resulting DataFrame:
    - DriverNumber
    - LapNumber
    - Position
    - PositionBefore
    - PassedDriverNumber
    - PassingStatus
    - GapToLeader
    - IntervalToPositionAhead

    PassingStatus is populated for position improvements that match the
    following criteria and should be excluded from the result:
    - Overtakes performed during lap 1.
    - Position that is not maintained for at least 3 seconds.
    - The driver must be ahead of the passsed driver at the end of the lap.
    - Passing driver who retired on circuit.
    - Passing that occurs during a pit window
    - Due to the limitation of data from FastF1, laps where pit stops occur are
        considered inaccurate and are not counted.
    - Cars that have been lapped.
    - Cars that are off track.
    - Cars driving slower than 30Km/h are considered "MaybeOffTrack" and are not
        counted.
    - Multiple overtakes that occur during the same lap against the same driver
        competing for the same position.
    """
    time_ahead_tolerance = pd.Timedelta(5, "s")
    off_track_tolerance = pd.Timedelta(2, "s")
    maybe_pit_tolerance = pd.Timedelta(10, "s")

    max_laps = session.laps["LapNumber"].max()
    driver_timing = timing.query(f'DriverNumber == "{driver_number}"').reset_index(drop=True)
    laps = session.laps.pick_driver(driver_number).reset_index(drop=True)

    possible_overtakes = __get_possible_overtakes(laps, timing, pd.Timedelta(3, "s"))

    # Add additional information to filter result at the end
    df = possible_overtakes.copy()
    df["PassingStatus"] = np.nan

    for idx, lap in laps.iterlaps():
        lap_number = lap["LapNumber"]

        overtakes = possible_overtakes.query(f"LapNumber == '{lap_number}'")
        if overtakes.empty:
            continue

        # lap start position and lap end position
        _, pos_end = get_position_at_lap(lap, driver_timing)

        for oidx, overtake in overtakes.iterrows():
            time = overtake["Time"]
            position = overtake["Position"]
            position_before = overtake["PositionBefore"]
            passed_driver_number = overtake["PassedDriverNumber"]

            if not passed_driver_number:
                continue

            # First lap is not counted.
            if lap_number == 1:
                df.at[oidx, "PassingStatus"] = "FirstLap"
                continue

            # If the next position is the same as the previous position, no overtake may
            # be happening and they are running side by side trading posistions.  In this
            # case, make sure the current position persisted for at least the threashold
            # amount and update the status accordingly.
            if oidx != 0:
                next_position, next_time = None, None
                if oidx < len(possible_overtakes) - 2:
                    next_position, next_time = (
                        possible_overtakes[["Position", "Time"]].iloc[oidx + 1].array
                    )
                prev_position, prev_time = (
                    possible_overtakes[["Position", "Time"]].iloc[oidx - 1].array
                )
                if next_position and prev_position == next_position:
                    if next_time - prev_time < time_ahead_tolerance:
                        df.at[oidx, "PassingStatus"] = "PositionThreasholdNotMet"
                        continue

            passed_driver_laps = session.laps.pick_driver(passed_driver_number)
            passed_driver_lap = get_lap_at_time(time, passed_driver_laps)

            # This driver is likely retired, updated status accordingly
            if passed_driver_lap is None:
                pd_max_laps = passed_driver_laps["LapNumber"].max()
                if pd_max_laps < max_laps:
                    df.at[oidx, "PassingStatus"] = "Retired"
                else:
                    df.at[oidx, "PassingStatus"] = "Unknown"

            # Check if the passed driver is pitted
            elif is_time_during_pit(
                time, passed_driver_laps, lap_number_hint=passed_driver_lap["LapNumber"]
            ):
                df.at[oidx, "PassingStatus"] = "Pit"

            # The lap is considered not accurate if pit stop occurs (and other criteria)
            # If not accurate, try checking pit window again with a very wide tolerance
            elif not passed_driver_lap["IsAccurate"]:
                if not (
                    pd.isnull(passed_driver_lap["PitInTime"])
                    and pd.isnull(passed_driver_lap["PitOutTime"])
                ):
                    if is_time_during_pit(
                        time,
                        passed_driver_laps,
                        passed_driver_lap["LapNumber"],
                        maybe_pit_tolerance,
                        maybe_pit_tolerance,
                    ):
                        df.at[oidx, "PassingStatus"] = "MaybePit"
                else:
                    df.at[oidx, "PassingStatus"] = "NotAccurate"

            # Ensure car is not lapped
            elif passed_driver_lap["LapNumber"] < lap_number:
                df.at[oidx, "PassingStatus"] = "Lapped"

            # Check if the car is off track
            else:
                pos_data = passed_driver_lap.get_pos_data().slice_by_time(
                    time - off_track_tolerance, time + off_track_tolerance
                )
                if pos_data.empty:
                    df.at[oidx, "PassingStatus"] = "PositionDataUnavailable"
                elif not pos_data[pos_data["Status"] == "OffTrack"].empty:
                    df.at[oidx, "PassingStatus"] = "OffTrack"
                else:
                    # car maya have spun out or went into the gravel - check if the car is going very slow at this time
                    car_data = passed_driver_lap.get_car_data().slice_by_time(
                        time - off_track_tolerance, time + off_track_tolerance
                    )
                    if car_data["Speed"].mean() <= 30:
                        df.at[oidx, "PassingStatus"] = "MaybeOffTrack"

    # mark data where multiple overtakes occur within the same lap against the same driver
    dup = df.duplicated(["LapNumber", "Position", "PassedDriverNumber"], keep="last")
    df.loc[dup, "PassingStatus"] = "Duplicate"

    return df.reset_index(drop=True)


def __get_position_changes(timing_data: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a subset of the given timing_data for when position changes occur
    """
    if len(timing_data["DriverNumber"].unique()) != 1:
        raise Exception("Expected only 1 driver in the given timing_data")

    current_position = timing_data.iloc[0]["Position"]
    position_changes = [timing_data.iloc[0]]
    for _, t in timing_data.iterrows():
        if t["Position"] != current_position:
            position_changes.append(t)
            current_position = t["Position"]
    df = pd.DataFrame(data=position_changes)
    return df.reset_index(drop=True)


def __get_possible_overtakes(
    laps: ff1.core.Laps, timing_data: pd.DataFrame, threashold: pd.Timedelta
) -> pd.DataFrame:
    """
    Returns a DataFrame of possible overtakes for a driver. Possible overtakes
    are whenever a position improvement occurs and the driver must maintan
    position for the given threashold amount.

    This does not account for pit stops, retirements, etc.

    The resultng DataFrame is a subset of the given timing_data with LapTime and
    PreviousPosition columns.
    """
    driver_numbers = laps["DriverNumber"].unique()
    if len(driver_numbers) != 1:
        raise Exception("Expected only 1 driver in the given laps")

    # gather necessary data
    driver_number = driver_numbers[0]
    driver_timing = timing_data.query(f'DriverNumber == "{driver_number}"').reset_index(drop=True)
    laps = laps.reset_index(drop=True)
    position_changes = __get_position_changes(driver_timing)
    position_changes = add_lap_number_to_timing_data(laps, position_changes)

    possible_overtakes = []
    for idx, t in position_changes.iterrows():
        if idx == 0:
            continue

        cur_lap = t["LapNumber"]
        cur_position = t["Position"]
        cur_time = t["Time"]

        next_position, next_time = None, None
        if idx < len(position_changes) - 2:
            next_position, next_time = position_changes[["Position", "Time"]].iloc[idx + 1].array
        prev_position, prev_time = position_changes[["Position", "Time"]].iloc[idx - 1].array

        # only care about if this position improved from the previous position
        if prev_position < cur_position:
            continue

        # find the passed driver timing by closest time
        candidates = timing_data[
            (timing_data["Position"] == prev_position) & (timing_data["Time"] <= cur_time)
        ]
        passed_driver_timing = timing_data.iloc[candidates["Time"].idxmax()]
        passed_driver_number = passed_driver_timing["DriverNumber"]

        t_copy = t.copy()
        t_copy["PositionBefore"] = prev_position
        t_copy["PassedDriverNumber"] = passed_driver_number
        possible_overtakes.append(t_copy)

    return pd.DataFrame(data=possible_overtakes).reset_index(drop=True)
