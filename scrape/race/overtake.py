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

    # There was never a battle against this driver.
    NO_BATTLE = auto()

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

    # Yellow, red, safety car, etc.
    TRACK_STATUS = auto()

    # Position was regained after losing it for a split second
    POSITION_REGAINED = auto()


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
    this_lap = None
    for idx, row in timings.iterrows():
        position = row["Position"]
        if position == last_position:  # no change
            continue
        if position > last_position:  # no improvement
            last_position = position
            continue

        gained = last_position - position
        time = row["Time"]

        if this_lap != row["LapNumber"]:
            this_lap = row["LapNumber"]

        for i in range(1, gained + 1):
            against, status = __is_overtake(session, last_position - i, time, driver_number)
            overtakes.append(
                {
                    "Time": time,
                    "LapNumber": row["LapNumber"],
                    "Position": position,
                    "DriverNumber": driver_number,
                    "DriverNumberAgainst": against,
                    "PassingStatus": status.name,
                }
            )

        last_position = position

    df = pd.DataFrame(overtakes)

    # filter null lap numbers
    df = df[~df["LapNumber"].isnull()]

    # mark data where multiple overtakes occur within the same lap against the same driver
    dup = df.duplicated(
        ["LapNumber", "Position", "DriverNumberAgainst", "PassingStatus"], keep="last"
    )
    df.loc[dup, "PassingStatus"] = OvertakeStatus.DUPLICATE.name

    return df.reset_index(drop=True)


def __is_overtake(session, position, time, overtaker) -> (str, OvertakeStatus):
    """
    TODO: check car is full car length ahead for both the driver and the driver
        against for the past x seconds.
    """
    # driver data
    laps = session.laps.pick_driver(overtaker)
    lap = timing.get_lap_at_time(time, laps)
    timings = session.timings.pick_driver(overtaker)

    driver_against = timing.get_driver_at_position(
        session, time, position + 1, not_include=[overtaker]
    )
    driver_against_laps = session.laps.pick_driver(driver_against)
    driver_against_lap = timing.get_lap_at_time(time, driver_against_laps)
    driver_against_timings = session.timings.pick_driver(driver_against)

    # 1. is not the first lap
    if lap is None:
        return driver_against, OvertakeStatus.NO_LAP
    if lap["LapNumber"] == 1:
        return driver_against, OvertakeStatus.FIRST_LAP

    if driver_against_lap is None:
        return driver_against, OvertakeStatus.NO_LAP_OTHER
    if driver_against_lap["LapNumber"] == 1:
        return driver_against, OvertakeStatus.FIRST_LAP_OTHER

    # 2. track status is clear with 3 second tolerance for when a non-clear status indicator is raised.
    last_non_green = None
    track_status_raised_tolerance = pd.Timedelta(3, "s")
    for _, ts in session.track_status.iterrows():
        if last_non_green is None and ts["Status"] != "1":
            last_non_green = ts
        if last_non_green is not None and ts["Status"] == "1":
            if (
                time >= last_non_green["Time"] - track_status_raised_tolerance
                and time <= ts["Time"]
            ):
                return driver_against, OvertakeStatus.TRACK_STATUS
            last_non_green = None

    # 3. overtaken driver is not pitted
    pit_tolerance = pd.Timedelta(2, "s")
    if timing.is_in_pit(time, driver_against_timings, pit_tolerance):
        return driver_against, OvertakeStatus.PIT

    # 4. position is maintained for 5 seconds
    pos_maintained_tolerance = pd.Timedelta(10, "s")
    next_positions = timings[
        (timings["Time"] > time) & (timings["Time"] <= time + pos_maintained_tolerance)
    ]
    for _, row in next_positions.iterrows():
        if row["Position"] > position:
            return driver_against, OvertakeStatus.LOST_TOO_QUICK

    # 5. make sure the other driver was ahead in the last 5 seconds (e.g.
    # position did not improve due to someone in front pitting, retiring, etc.)
    time_ahead_tolerance = pd.Timedelta(5, "s")
    driver_against_prev_positions = driver_against_timings[
        (driver_against_timings["Time"] < time)
        & (driver_against_timings["Time"] >= time - time_ahead_tolerance)
    ]
    for _, row in driver_against_prev_positions.iterrows():
        pos_now_idx = timings[timings["Time"] >= row["Time"]]["Time"].idxmin()
        pos_now = timings.loc[pos_now_idx]["Position"]
        if pos_now != position and row["Position"] > pos_now:  # make sure they were ahead
            return driver_against, OvertakeStatus.NO_BATTLE

    # 6. overtaken driver is off track
    off_track_tolerance = pd.Timedelta(2, "s")
    pos_data = driver_against_lap.get_pos_data().slice_by_time(
        time - off_track_tolerance, time + off_track_tolerance
    )
    if pos_data.empty:
        return driver_against, OvertakeStatus.NO_POSITION_DATA
    elif not pos_data[pos_data["Status"] == "OffTrack"].empty:
        return driver_against, OvertakeStatus.OFF_TRACK

    # 7. overtaken driver driving slower than 30km/h are considered maybe off track
    car_data = driver_against_lap.get_car_data().slice_by_time(
        time - off_track_tolerance, time + off_track_tolerance
    )
    if car_data["Speed"].mean() <= 30:
        return driver_against, OvertakeStatus.MAYBE_OFF_TRACK

    # 8. overtaken driver had the lead over this driver for at least 5 seconds
    # TODO: this is shit
    # od_previous_positions = driver_against_timings[
    #     (driver_against_timings["Time"] < time)
    #     & (driver_against_timings["Time"] >= time - pd.Timedelta(15, "s"))
    # ]
    # first_occurance, last_occurance = None, None
    # for _, row in od_previous_positions.iterrows():
    #     # pos_now_idx = timings[timings["Time"] >= row["Time"]]["Time"].idxmin()
    #     # pos_now = timings.loc[pos_now_idx]["Position"]
    #     if row["Position"] <= position:  # and pos_now > row["Position"]:
    #         if first_occurance is None:
    #             first_occurance = row["Time"]
    #         last_occurance = row["Time"]

    # if first_occurance and last_occurance - first_occurance < pd.Timedelta(5, "s"):
    #     return driver_against, OvertakeStatus.POSITION_REGAINED
    # --

    # 8. overtaken driver had sufficient lead
    # make sure the driver had a gap larger than 0.025s in the last 10 seconds
    # to filter side-by-side actions
    # prev_positions = timings[
    #     (timings["Time"] < time) & (timings["Time"] >= time - pd.Timedelta(10, "s"))
    # ]
    # for _, row in prev_positions.iterrows():
    #     if row["Position"] > position:
    #         interval = __interval_to_timedelta(row["IntervalToPositionAhead"])
    #         if interval and interval > pd.Timedelta(25, "ms"):
    #             break
    #     return driver_against, OvertakeStatus.POSITION_REGAINED

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
