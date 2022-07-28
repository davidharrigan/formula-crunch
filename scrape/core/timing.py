import logging

import fastf1 as ff1
from fastf1.utils import recursive_dict_get
import numpy as np
import pandas as pd

from scrape.data import DataMapping


EMPTY_STREAM = {
    "Time": pd.NaT,
    # Driver info
    "DriverNumber": str(),
    "Position": np.NaN,
    "GapToLeader": np.NaN,
    "IntervalToPositionAhead": np.NaN,
    "Retired": np.NaN,
    # Lap
    "LapNumber": np.NaN,
    "Status": np.NaN,
    # Sector
    "LastSectorSegmentNumber": np.NaN,
    "LastSectorSegmentStatus": np.NaN,
    # Flags
    "PitIn": False,
    "PitOut": False,
}


@ff1.api.Cache.api_request_wrapper
def get_timing_data(path, response=None, livedata=None) -> pd.DataFrame:
    logging.info("Fetching timing stream data...")

    if response is not None or livedata is not None:
        raise Exception("response and livedata params aren't supported at this time")

    response = ff1.api.fetch_page(path, "timing_data")
    if response is None:
        raise ff1.api.SessionNotAvailableError(
            "No data for this session! If this session only finished "
            "recently, please try again in a few minutes."
        )

    logging.info("Parsing timing stream data...")

    # split up response per driver for easier iteration and processing later
    resp_per_driver = dict()
    for entry in response:
        if (len(entry) < 2) or "Lines" not in entry[1]:
            continue
        for drv in entry[1]["Lines"]:
            if drv not in resp_per_driver.keys():
                resp_per_driver[drv] = [(entry[0], entry[1]["Lines"][drv])]
            else:
                resp_per_driver[drv].append((entry[0], entry[1]["Lines"][drv]))

    # create empty data dicts and populate them with data from all drivers after that
    timing_data = {key: list() for key, val in EMPTY_STREAM.items()}
    for drv in resp_per_driver.keys():
        drv_timing_data = timing_data_driver(resp_per_driver[drv], EMPTY_STREAM, drv)

        for key in EMPTY_STREAM.keys():
            timing_data[key].extend(drv_timing_data[key])

    df = pd.DataFrame(timing_data)
    df = df[~df["LapNumber"].isnull()]
    return df


def timing_data_driver(driver_raw, empty_vals, drv):
    """
    Data is on a timestamp basis.

    TODO: determine lap #1

    Params:
        driver_raw (list): raw api response for this driver only [(Timestamp, data), (...), ...]
        empty_vals (dict): dictionary of column names and empty column values
        drv (str): driver identifier

    Returns:
         dictionary of timing stream data for this driver
    """
    mapping: dict[str, DataMapping] = {
        "Position": DataMapping("Position", int),
        "GapToLeader": DataMapping("GapToLeader", str),
        "Retired": DataMapping("Retired", str),
        "Status": DataMapping("Status", int),
        "InPit": DataMapping("PitIn", bool),
        "PitOut": DataMapping("PitOut", bool),
    }

    # entries are pre-filled with empty or previous values and only overwritten if they exist in the response line
    # basically interpolation by filling up with last known value because not every value is in every response
    drv_data = {
        key: [
            val,
        ]
        for key, val in empty_vals.items()
    }

    i = 0
    keep_last = ["Position", "LapNumber"]

    if "Position" not in driver_raw[2][1]:
        driver_raw[2][1]["Position"] = driver_raw[0][1]["Position"]

    # iterate through the data; timestamp + any of the values triggers new row in data
    # first two rows contain metadata and the initial position, so we can skip those.
    pit_out = False
    for time, resp in driver_raw[2:]:
        new_entry = False
        for key, dm in mapping.items():
            if val := recursive_dict_get(resp, key):
                drv_data[dm.column][i] = dm.transform(val)
                new_entry = True

        if val := recursive_dict_get(resp, "NumberOfLaps"):
            drv_data["LapNumber"][i] = DataMapping.to_str(int(val) + 1)
            new_entry = True

        if val := recursive_dict_get(resp, "IntervalToPositionAhead", "Value"):
            drv_data["IntervalToPositionAhead"][i] = DataMapping.to_str(val)
            new_entry = True

        if val := recursive_dict_get(resp, "Sectors"):
            sector_data = _parse_sector_data(val)
            for k, v in sector_data.items():
                drv_data[k][i] = v
                new_entry = True

        # at least one value was present, create next row
        if new_entry:
            drv_data["Time"][i] = DataMapping.to_timedelta(time)
            drv_data["DriverNumber"][i] = DataMapping.to_str(drv)
            i += 1

            # create next row of data with empty values
            for key, val in empty_vals.items():
                if key in keep_last:
                    drv_data[key].append(drv_data[key][-1])
                else:
                    drv_data[key].append(val)

    for key in drv_data.keys():
        drv_data[key] = drv_data[key][:-1]  # remove very last row again

    return drv_data


def _parse_sector_data(sectors: dict) -> dict:
    sector_data = {}

    # Note: all status marked as 0 at all sectors seems to come in after the
    # start of a new lap. I think this is meant to reset the segment values in
    # the F1 Live Timing App.
    # if len(sectors.keys()) != 1:
    #     if val := recursive_dict_get("0", "Segments", "0", "Status"):
    #         sector_data["LastSectorSegmentNumber"] = DataMapping.to_str("1.1")
    #         sector_data["LastSectorSegmentStatus"] = DataMapping.to_int(val)
    #     return sector_data

    sn = int(list(sectors.keys())[0]) + 1
    sector = list(sectors.values())[0]

    # This is a sector time of the LAST sector... it's the same thing as the
    # "Value" field below, but comes in sometime after.  Maybe it comes in when
    # lap/sector time is validated?
    if "PreviousValue" in sector:
        return sector_data

    # This is a sector time of the LAST sector recorded (almost) immediately at
    # the start of a sector.  Sometimes, it comes in a little late - so will
    # need to be sanitized and validated against sector times.
    if "Value" in sector:
        return sector_data

    sector_segments_found = 0
    last_non_zero_status = None
    if segments := recursive_dict_get(sector, "Segments"):
        if isinstance(segments, dict):  # Same story as Sectors
            for ssn, segment in segments.items():
                ssn = int(ssn) + 1
                if status := segment["Status"]:
                    segment_status = segment["Status"]
                    sector_data["LastSectorSegmentNumber"] = DataMapping.to_str(f"{sn}.{ssn}")
                    sector_data["LastSectorSegmentStatus"] = DataMapping.to_int(segment_status)
                    if segment_status != 0:
                        if segment_status != last_non_zero_status:
                            sector_segments_found += 1
                        last_non_zero_status = segment_status

    if sector_segments_found > 1:
        logging.warn(f"found {sector_segments_found} sector segments!")

    return sector_data


class Timing(pd.DataFrame):
    """
    - `Time` (timedelta): Time (0 is start of the data slice)
    - `SessionTime` (timedelta): Time elapsed since the start of the session
    - `Date` (datetime): The full date + time at which this sample was created

    Possible segment indicators:
    - Previous: 2048
    - Personal Best: 2049
    - Best Overall: 2051
    - Stopped Car: 2052
        This comes in pretty late. When calculating overtakes, track
        status should be used to see if there is a yellow / red flag.
    - PitLane: 2064
    """

    _metadata = ["session"]

    _COLUMNS = [
        "Time",
        "Position",
        "GapToLeader",
        "IntervalToPositionAhead",
        "Retired",
        "DriverNumber",
        "LapNumber",
        "Status",
        "LastSectorSegmentNumber",
        "LastSectorSegmentStatus",
        "RawStatus",
    ]

    def __init__(self, *args, session=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session

    @property
    def _constructor(self):
        def _new(*args, **kwargs):
            return Timing(*args, **kwargs).__finalize__(self)

        return _new

    @property
    def base_class_view(self):
        """For a nicer debugging experience; can view DataFrame through this property in various IDEs"""
        return pd.DataFrame(self)
