import fastf1 as ff1
import pandas as pd
import numpy as np

from scrape.race.timing import (
    get_timing_data,
    add_lap_number_to_timing_data,
    get_lap_start_end_time,
    get_lap_at_time,
    get_position_at_lap,
    get_driver_at_position,
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
    - Position that is not maintained for at least 5 seconds.
    - Driver is overtaken, and retakes position back within 5 seconds.
        TODO: maybe maintain position at least until last sector?
    - The driver must be ahead of the passsed driver at the end of the lap.
    - Passing driver who retired on circuit.
    - Passing that occurs during a pit window
    - Due to the limitation of data from FastF1, laps where pit stops occur are
        considered inaccurate and are not counted.
        TODO: get sector segment status from raw timing data.
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

    # possible_overtakes = __get_possible_overtakes(laps, timing)
    position_changes = __get_position_changes(laps, timing)

    # TODO: optimize this
    # get position changes for everyone else

    # Add additional information to filter result at the end
    df = position_changes.copy()
    df = df[df["PositionGained"] >= 1]
    df["PassingStatus"] = np.nan

    for idx, lap in laps.iterlaps():
        lap_number = lap["LapNumber"]

        pos_changes_lap = position_changes.query(
            f"LapNumber == '{lap_number}' and PositionGained >= 1"
        )
        if pos_changes_lap.empty:
            continue

        # lap end position
        pos_end = pos_changes_lap.iloc[-1]["Position"]

        for oidx, pos_change in pos_changes_lap.iterrows():
            time = pos_change["Time"]
            position = pos_change["Position"]
            position_before = pos_change["PositionBefore"]
            passed_driver_number = pos_change["DriverNumberBehind"]

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
            # TODO: we'll need to make sure this works for when a car overtakes multiple cars in 1 corner
            # or when multiple cars are trading positiions
            if oidx != 0 and oidx < len(position_changes) - 2:
                # Position improved, but maybe lost it back too quickly.
                next_position, next_time, next_pos_driver_ahead = (
                    position_changes[["Position", "Time", "DriverNumberAhead"]].iloc[oidx + 1].array
                )
                if (
                    position < next_position
                    and next_time - time < time_ahead_tolerance
                    and next_pos_driver_ahead == passed_driver_number
                ):
                    df.at[oidx, "PassingStatus"] = "PositionLostTooQuickly"
                    continue

                # TODO: position improved, but just regaining position within tolerance.
                # prev_position, prev_time = (
                #     position_changes[["Position", "Time"]].iloc[oidx - 1].array
                # )
                # if next_position and prev_position == next_position:
                #     if next_time - prev_time < time_ahead_tolerance:
                #         df.at[oidx, "PassingStatus"] = "PositionRegainedWithinTolerance"
                #         continue

            passed_driver_laps = session.laps.pick_driver(passed_driver_number)
            passed_driver_lap = get_lap_at_time(time, passed_driver_laps)

            # This driver is likely retired, updated status accordingly
            if passed_driver_lap is None:
                pd_max_laps = passed_driver_laps["LapNumber"].max()
                if pd_max_laps < max_laps:
                    df.at[oidx, "PassingStatus"] = "Retired"
                else:
                    df.at[oidx, "PassingStatus"] = "Unknown"

            # TODO: ensure the "passed driver" improved position

            # Check if the passed driver is in pit
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

    # filter null lap numbers
    df = df[~df["LapNumber"].isnull()]

    # mark data where multiple overtakes occur within the same lap against the same driver
    dup = df.duplicated(["LapNumber", "Position", "DriverNumberBehind"], keep="last")
    df.loc[dup, "PassingStatus"] = "Duplicate"

    return df.reset_index(drop=True)


def __get_possible_overtakes(laps: ff1.core.Laps, timing_data: pd.DataFrame) -> pd.DataFrame:
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
    laps = laps.reset_index(drop=True)
    position_changes = __get_position_changes(laps, timing_data)

    possible_overtakes = []
    for idx, t in position_changes.iterrows():
        if idx == 0:
            continue

        cur_lap = t["LapNumber"]
        cur_position = t["Position"]
        cur_time = t["Time"]

        if pd.isnull(cur_lap):
            continue

        # only care about if this position improved from the previous position
        prev_position = position_changes["Position"].iloc[idx - 1]
        if prev_position < cur_position:
            continue

        t_copy = t.copy()
        possible_overtakes.append(t_copy)

    return pd.DataFrame(data=possible_overtakes).reset_index(drop=True)


def __get_position_changes(laps: ff1.core.Laps, timing_data: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a subset of the given timing_data for when position changes occur

    Timing data is filtered by Driver
    """
    driver_numbers = laps["DriverNumber"].unique()
    if len(driver_numbers) != 1:
        raise Exception("Expected only 1 driver in the given laps")

    # gather necessary data
    driver_number = driver_numbers[0]
    driver_timing = timing_data.query(f'DriverNumber == "{driver_number}"').reset_index(drop=True)
    laps = laps.reset_index(drop=True)

    last_changed_position = driver_timing.iloc[0]["Position"]
    position_changes = [driver_timing.iloc[0]]

    for idx, t in driver_timing.iterrows():
        position = t["Position"]
        if position != last_changed_position:
            time = t["Time"]

            lap = get_lap_at_time(time, laps)

            delta = last_changed_position - position
            prev_position = position + delta

            driver_ahead = get_driver_at_position(time, position - 1, timing_data)
            driver_behind = get_driver_at_position(time, position + 1, timing_data)
            driver_passed = np.nan
            if delta > 0:
                driver_passed = driver_behind

            t_copy = t.copy()
            t_copy["PositionBefore"] = str(prev_position)
            t_copy["PositionGained"] = delta
            t_copy["DriverNumberAhead"] = driver_ahead
            t_copy["DriverNumberBehind"] = driver_behind
            t_copy["DriverNumberPassed"] = driver_passed
            if lap is not None:
                t_copy["LapNumber"] = str(lap["LapNumber"])
            position_changes.append(t_copy)

            last_changed_position = t["Position"]

    return pd.DataFrame(data=position_changes).reset_index(drop=True)
