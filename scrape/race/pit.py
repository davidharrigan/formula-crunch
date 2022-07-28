import datetime
import fastf1 as ff1
import pandas as pd

from scrape.data import DataMapping

__all__ = ["get_pit_summary"]


def get_pit_summary(
    session: ff1.core.Session, tz_offset=datetime.timedelta(0)
) -> tuple[pd.DataFrame, pd.DataFrame]:
    mapping: dict[str, DataMapping] = {
        "driverId": DataMapping("DriverID", str),
        "lap": DataMapping("LapNumber", str),
        "stop": DataMapping("Stop", int),
        "time": DataMapping("PitDate", str),  # this converted to datetime below
        "duration": DataMapping("Duration", datetime.timedelta),
    }

    year = session.event["EventDate"].year
    race_round = session.event["RoundNumber"]

    limit = 30
    offset = 0
    content = []

    base_url = (
        "https://ergast.com/api/f1/{year}/{round}/pitstops.json?limit={limit}&offset={offset}"
    )
    url = base_url.format(year=year, round=race_round, limit=0, offset=offset)
    res = ff1.api.Cache.requests_get(url)

    while True:
        url = base_url.format(year=year, round=race_round, limit=limit, offset=offset)
        res = ff1.api.Cache.requests_get(url)
        if res.status_code != 200:
            raise Exception(f"expected 200 status, got: {res.status_code}")
        body = res.json()
        total = int(body["MRData"]["total"])
        content.extend(body["MRData"]["RaceTable"]["Races"][0]["PitStops"])
        if offset + limit >= total:
            break
        offset += limit

    pit_stops = []
    for item in content:
        data = {}
        for key, dm in mapping.items():
            data[dm.column] = dm.transform(item[key])

        parts = data["PitDate"].split(":")
        pit_date = (
            datetime.datetime(
                session.t0_date.year,
                session.t0_date.month,
                session.t0_date.day,
                hour=int(parts[0]),
                minute=int(parts[1]),
                second=int(parts[2]),
            )
            + tz_offset
        )
        # TODO: ergast API returns pit time as local time :(
        # TODO: can get GMT offset from livetiming.formula1.com SessionInfo
        pit_time = pit_date - session.t0_date
        data["PitDate"] = pit_date
        data["Time"] = pit_time  # Time is ff1 SessionStartTime
        pit_stops.append(data)

    pit_stop_df = pd.DataFrame(data=pit_stops)

    gb = pit_stop_df.groupby(["DriverID"])
    summary_df = gb.size().to_frame(name="TotalStops")
    summary_df = (
        summary_df.join(gb.agg({"Duration": "mean"}).rename(columns={"Duration": "Average"}))
        .join(gb.agg({"Duration": "sum"}).rename(columns={"Duration": "TotalTime"}))
        .reset_index()
    )
    return summary_df, pit_stop_df


def is_time_during_pit(
    time: pd.Timedelta,
    laps: ff1.core.Laps,
    lap_number_hint=0,
    pit_in_tolerance=pd.Timedelta(0, "s"),
    pit_out_tolerance=pd.Timedelta(0, "s"),
):
    """
    Returns True if the given time occurs during a pit window.

    Args:
        time: time to check
        lap_number_hint: narrow down the search to a specific lap
        pit_in_tolerance: the dataset currently doesn't account for when the
            driver is entering the pitlane. This value adds tolerance to the given
            time to allow for a wider window.
        pit_out_tolerance: same thing as pit_in_tolerance but for when exiting pit.
    """
    if lap_number_hint:
        laps = laps[
            (laps["LapNumber"] >= lap_number_hint - 1) & (laps["LapNumber"] <= lap_number_hint + 1)
        ]

    last_pit_in = None
    for _, lap in laps.iterrows():
        pit_in = lap["PitInTime"] - pit_in_tolerance
        pit_out = lap["PitOutTime"] + pit_out_tolerance

        if not pd.isnull(pit_in):
            if time <= pit_in and time >= pit_in:
                return True
            last_pit_in = pit_in

        if not pd.isnull(pit_out):
            if time <= pit_out and time >= pit_out:
                return True
            if last_pit_in:
                if time >= last_pit_in and time <= pit_out:
                    return True
                last_pit_in = None
    return False
