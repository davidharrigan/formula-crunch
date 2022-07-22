import pandas as pd
import fastf1 as ff1

__all__ = ["get_race"]


def get_race(session: ff1.core.Session) -> pd.Series:
    event = session.event

    # find session event date
    datetime = None
    for i in range(1, 6):
        sn = getattr(event, f"Session{i}")
        if sn == "Race":
            datetime = getattr(event, f"Session{i}Date")
            break
    if datetime is None:
        raise Exception("Could not find race date from event", event)

    return pd.Series(
        data={
            "Year": datetime.year,
            "RoundNumber": event["RoundNumber"].item(),
            "Date": datetime,
            "Drivers": len(pd.unique(session.laps["Driver"])),
        }
    )
