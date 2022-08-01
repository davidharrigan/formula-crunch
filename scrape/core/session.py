from __future__ import annotations
import logging

import pandas as pd
import numpy as np

import fastf1 as ff1

from scrape.core.timing import Timing, get_timing_data

__all__ = ["get_session", "Session"]


def get_session(year, gp, identifier=None, *, force_ergast=False, event=None) -> Session:
    session = ff1.get_session(
        year, gp, identifier=identifier, force_ergast=force_ergast, event=event
    )
    return Session(session)


class Session(ff1.core.Session):
    def __init__(self, parent):
        for key, val in vars(parent).items():
            setattr(self, key, val)
        self._timing_data: Timing
        self._track_status_data: pd.DataFrame

    @property
    def timings(self):
        return self._get_property_warn_not_loaded("_timing_data")

    @property
    def track_status(self):
        return self._get_property_warn_not_loaded("_track_status_data")

    def load(
        self, *, laps=True, telemetry=True, weather=True, messages=True, timing=True, livedata=None
    ):
        super().load(
            laps=laps, telemetry=telemetry, weather=weather, messages=messages, livedata=livedata
        )

        if timing:
            try:
                self._load_timing_data()
            except Exception as exc:
                logging.warning("Failed to load timing data!")
                logging.warning("Timing data failure traceback:", exc_info=exc)

        self._track_status_data = pd.DataFrame(ff1.api.track_status_data(self.api_path))

    def _load_timing_data(self):
        df = get_timing_data(self.api_path)
        logging.info("Processing timing data...")

        def set_status(idx, df, value):
            df.at[idx, "Status"] = value

        df = df.rename(columns={"Status": "RawStatus"})

        last_pit_status = None
        cp = df.copy()
        pit_ins = 0
        pit_outs = 0
        drv = None
        for idx, row in cp.iterrows():
            if row["DriverNumber"] != drv:
                drv = row["DriverNumber"]
                pit_ins = 0
                pit_outs = 0
            if row["LastSectorSegmentStatus"] == 2064:
                set_status(idx, df, "PIT_LANE")
                if last_pit_status == "PIT_OUT":
                    last_pit_status = None
            elif row["PitIn"]:
                set_status(idx, df, "PIT_IN")
                last_pit_status = "PIT_IN"
                pit_ins += 1
            elif row["PitOut"]:
                set_status(idx, df, "PIT_OUT")
                last_pit_status = "PIT_OUT"
                pit_outs += 1
            elif pit_ins > 1 and last_pit_status in ("PIT_IN", "PIT_OUT"):
                set_status(idx, df, "PIT_LANE")

        df = df[Timing._COLUMNS]

        self._timing_data = Timing(df, session=self)
