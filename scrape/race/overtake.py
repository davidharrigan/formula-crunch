from enum import Enum, auto

import fastf1 as ff1
import pandas as pd
import numpy as np

from scrape.race.pit import is_time_during_pit
from scrape.core import Session, timing

__all__ = ["get_overtakes", "get_driver_overtakes"]


class OvertakeStatus(Enum):
    OK = auto()

    # There were multiple overtakes against the same driver in the same lap.
    DUPLICATE = auto()

    # Driver against is in pit
    PIT = auto()

    # No lap data when overtake occurred
    NO_LAP = auto()

    # Overtake happened on the first lap
    FIRST_LAP = auto()

    # No position data available to determine on/off track status.
    NO_POSITION_DATA = auto()

    # Driver against is off track
    OFF_TRACK = auto()

    # Driver against may be off track (driving slower than 30km/h)
    MAYBE_OFF_TRACK = auto()

    # Position was lost too quickly (within 3 seconds)
    LOST_TOO_QUICK = auto()

    # No lap data for the passed driver when overtake occurred. This driver may have retired.
    NO_LAP_OTHER = auto()

    # Passed driver is still in their first lap
    FIRST_LAP_OTHER = auto()


def get_overtakes(session: Session) -> pd.DataFrame:
    """
    Returns overtakes that occurred during a session.
    """
    dfs = []
    for driver in session.drivers:
        dfs.append(get_driver_overtakes(session, driver))
    return pd.concat(dfs).reset_index(drop=True)


def get_driver_overtakes(
    session: Session,
    driver_number: str,
) -> pd.DataFrame:
    """
    Returns overtakes performed by the given driver.
    """
    timings = session.timings.pick_driver(driver_number)

    last_position = timings.iloc[0]["Position"]
    overtakes = []
    for idx, row in timings.iterrows():
        position = row["Position"]
        if position == last_position:  # no improvement
            continue
        if position > last_position:
            last_position = position
            continue

        last_position = position
        time = row["Time"]

        against, status = __is_overtake(session, position, time, driver_number)
        overtakes.append(
            {
                "Time": time,
                "LapNumber": row["LapNumber"],
                "Position": position,
                "Against": against,
                "PassingStatus": status.name,
            }
        )

    df = pd.DataFrame(overtakes)

    # filter null lap numbers
    df = df[~df["LapNumber"].isnull()]

    # mark data where multiple overtakes occur within the same lap against the same driver
    dup = df.duplicated(["LapNumber", "Position", "Against"], keep="last")
    df.loc[dup, "PassingStatus"] = OvertakeStatus.DUPLICATE.name

    return df.reset_index(drop=True)


def __is_overtake(session, position, time, overtaker) -> (str, OvertakeStatus):
    driver_against = timing.get_driver_at_position(session, time, position + 1)

    # 1. is not the first lap
    laps = session.laps.pick_driver(overtaker)
    lap = timing.get_lap_at_time(time, laps)
    if lap is None:
        return driver_against, OvertakeStatus.NO_LAP
    if lap["LapNumber"] == 1:
        return driver_against, OvertakeStatus.FIRST_LAP

    overtaken_driver_laps = session.laps.pick_driver(driver_against)
    overtaken_driver_lap = timing.get_lap_at_time(time, overtaken_driver_laps)
    if overtaken_driver_lap is None:
        return driver_against, OvertakeStatus.NO_LAP_OTHER
    if overtaken_driver_lap["LapNumber"] == 1:
        return driver_against, OvertakeStatus.FIRST_LAP_OTHER

    # 2. overtaken driver is not pitted
    overtaken_driver_timings = session.timings.pick_driver(driver_against)
    if timing.is_in_pit(time, overtaken_driver_timings):
        return driver_against, OvertakeStatus.PIT

    # 3. position is maintained for 3 seconds
    pos_maintained_tolerance = pd.Timedelta(3, "s")
    timings = session.timings.pick_driver(overtaker)
    positions_next_5_seconds = timings[
        (timings["Time"] > time) & (timings["Time"] <= time + pos_maintained_tolerance)
    ]
    for _, row in positions_next_5_seconds.iterrows():
        if row["Position"] > position:
            return driver_against, OvertakeStatus.LOST_TOO_QUICK

    # 4. overtaken driver is not off track
    off_track_tolerance = pd.Timedelta(2, "s")
    pos_data = overtaken_driver_lap.get_pos_data().slice_by_time(
        time - off_track_tolerance, time + off_track_tolerance
    )
    if pos_data.empty:
        return driver_against, OvertakeStatus.NO_POSITION_DATA
    elif not pos_data[pos_data["Status"] == "OffTrack"].empty:
        return driver_against, OvertakeStatus.OFF_TRACK

    # 5. overtaken driver driving slower than 30km/h are considered maybe off track
    car_data = overtaken_driver_lap.get_car_data().slice_by_time(
        time - off_track_tolerance, time + off_track_tolerance
    )
    if car_data["Speed"].mean() <= 30:
        return driver_against, OvertakeStatus.MAYBE_OFF_TRACK

    return driver_against, OvertakeStatus.OK


def __get_driver_position_changes(laps: ff1.core.Laps, timing_data: pd.DataFrame) -> pd.DataFrame:
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

            lap = timing.get_lap_at_time(time, laps)

            delta = last_changed_position - position
            prev_position = position + delta

            driver_ahead = timing.get_driver_at_position(time, position - 1, timing_data)
            driver_behind = timing.get_driver_at_position(time, position + 1, timing_data)
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
