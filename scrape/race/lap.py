import fastf1 as ff1
import pandas as pd

__all__ = ["get_lap_summary"]


def get_lap_summary(session: ff1.core.Session) -> pd.DataFrame:
    """
    Return a DataFrame containing:
        fastest lap time
        fastest lap average speed
        fastest lap speed trap
        average speed
        fastest speed trap
    """
    df = session.laps.query('PitOutTime == "" and PitInTime == ""')
    gb = df.groupby("DriverNumber")
    time = (
        gb.agg(
            minidx=("LapTime", "idxmin"),
            AverageTime=("LapTime", "mean"),
        )
        .join(df[["LapNumber", "LapTime"]], on="minidx")
        .rename(columns={"LapNumber": "FastestLap", "LapTime": "FastestLapTime"})
        .drop(columns=["minidx"])
        .reset_index()
    )

    speed_data = []
    for drv in time["DriverNumber"]:
        laps = session.laps.pick_driver(drv).query('PitOutTime == "" and PitInTime == ""')
        fastest_lap = laps.pick_fastest()

        fastest_lap_speed_avg = fastest_lap.get_car_data()["Speed"].mean().round(3)
        fastest_lap_st = fastest_lap["SpeedST"]
        speed_avg = laps.get_car_data()["Speed"].mean().round(3)
        all_laps_st_max = laps["SpeedST"].max()
        speed_data.append(
            {
                "DriverNumber": drv,
                "FastestLapAverageSpeed": fastest_lap_speed_avg,
                "FastestLapSpeedTrap": fastest_lap_st,
                "AverageSpeed": speed_avg,
                "FastestSpeedTrap": all_laps_st_max,
            }
        )
    speed = pd.DataFrame(data=speed_data)

    return time.set_index("DriverNumber").join(speed.set_index("DriverNumber")).reset_index()
