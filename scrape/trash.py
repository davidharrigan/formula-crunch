import logging
import os
from typing import List

import pandas as pd
from sqlalchemy.orm import Session

import fastf1

from sqlalchemy.orm import Session

from .models import (
    Driver,
    Circuit,
    Race,
    DriverRaceSummary,
    LapTimeSummary,
    PitStopSummary,
    PitStop,
    SpeedSummary,
    SpeedTrapSummary,
    SectorTimeSummary,
    Overtake,
)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
fastf1.Cache.enable_cache(os.path.join(ROOT_DIR, "..", "data", "cache"))


def scrape_race_data(tx: Session, event, year, force=False):
    session = fastf1.get_session(year, event, "Race")
    session.load(telemetry=True, laps=True, weather=False)

    # Get circuit
    circuit = _get_circuit(tx, session)

    # Load drivers
    drivers = _get_drivers(tx, session)

    race = _get_or_create_race(tx, session, circuit, drivers)
    for driver in drivers:
        logging.info(f"Processing data for driver {driver.code}")
        race_summary = _get_or_create_race_summary(tx, race, driver)

        _process_lap_time_summary(tx, session, race_summary)
        logging.info("processed lap time summary")

        _process_pit_stops(tx, session, race_summary)
        logging.info("processed pit stop summary")

        _process_speed_summary(tx, session, race_summary)
        logging.info("processed speed summary")

        _process_speed_trap_summary(tx, session, race_summary)
        logging.info("processed speed trap summary")

        _process_sector_time_summary(tx, session, race_summary)
        logging.info("processed sector time summary")

        _process_overtakes(tx, session, race_summary)
        logging.info("processed overtakes")


def _process_lap_time_summary(tx: Session, session, rs: DriverRaceSummary) -> LapTimeSummary:
    lts = tx.query(LapTimeSummary).filter_by(driver_race_summary_id=rs.id).one_or_none()
    if lts:
        return lts

    laps = session.laps.pick_driver(rs.driver.code)
    fastest_lap = laps.pick_fastest()

    # excludes laps where pitted
    average = (
        laps.query('PitOutTime == "" and PitInTime == ""')
        .filter(items=["LapTime"])
        .mean()["LapTime"]
    )

    lts = LapTimeSummary(
        driver_race_summary_id=rs.id,
        fastest_lap_number=fastest_lap["LapNumber"].item(),
        fastest=fastest_lap["LapTime"].to_pytimedelta(),
        average=average.round("ms").to_pytimedelta(),
    )
    tx.add(lts)
    tx.commit()
    return lts


def _process_pit_stops(tx: Session, session, rs: DriverRaceSummary) -> PitStopSummary:
    pss = tx.query(PitStopSummary).filter_by(driver_race_summary_id=rs.id).one_or_none()
    if pss:
        return pss

    laps = session.laps.pick_driver(rs.driver.code)

    pit_stops = []
    last_pit_in = None
    for _, lap in laps.iterrows():
        lap_number = lap["LapNumber"]
        pit_in = lap["PitInTime"]
        pit_out = lap["PitOutTime"]

        if last_pit_in and not pd.isnull(pit_out):
            pit_stops.append((lap_number - 1, pd.Timedelta(pit_out - last_pit_in)))
            last_pit_in = None
        if not pd.isnull(pit_in):
            last_pit_in = pit_in

    df = pd.DataFrame(data=pit_stops, columns=["lap", "time"])
    average = df.filter(items=["time"]).mean()["time"].round("ms").to_pytimedelta()
    total = df.filter(items=["time"]).sum()["time"].round("ms").to_pytimedelta()

    pss = PitStopSummary(
        driver_race_summary_id=rs.id,
        average=average,
        total_time=total,
    )
    tx.add(pss)
    tx.commit()

    for lap, time in pit_stops:
        ps = PitStop(
            pit_stop_summary_id=pss.id, lap_number=lap, time=time.round("ms").to_pytimedelta()
        )
        tx.add(ps)
    tx.commit()
    return pss


def _process_speed_summary(tx: Session, session, rs: DriverRaceSummary) -> SpeedSummary:
    ss = tx.query(SpeedSummary).filter_by(driver_race_summary_id=rs.id).one_or_none()
    if ss:
        return ss

    laps = session.laps.pick_driver(rs.driver.code)

    fastest_lap = laps.pick_fastest()
    fastest_lap_avg = fastest_lap.get_car_data().mean(numeric_only=True)["Speed"].round(3).item()
    all_lap_avg = (
        laps.query('PitOutTime == "" and PitInTime == ""')
        .get_car_data()
        .mean(numeric_only=True)["Speed"]
        .round(3)
        .item()
    )

    ss = SpeedSummary(
        driver_race_summary_id=rs.id,
        fastest_lap_average=fastest_lap_avg,
        all_laps_average=all_lap_avg,
    )
    tx.add(ss)
    tx.commit()
    return ss


def _process_speed_trap_summary(tx: Session, session, rs: DriverRaceSummary) -> SpeedTrapSummary:
    sts = tx.query(SpeedTrapSummary).filter_by(driver_race_summary_id=rs.id).one_or_none()
    if sts:
        return sts

    laps = session.laps.pick_driver(rs.driver.code)

    fastest_lap = laps.pick_fastest()
    all_laps = laps.filter(items=["SpeedST"]).max()

    sts = SpeedTrapSummary(
        driver_race_summary_id=rs.id,
        fastest_lap=fastest_lap["SpeedST"].item(),
        all_laps=all_laps["SpeedST"].item(),
    )
    tx.add(sts)
    tx.commit()
    return sts


def _process_sector_time_summary(tx: Session, session, rs: DriverRaceSummary) -> SectorTimeSummary:
    sts = tx.query(SectorTimeSummary).filter_by(driver_race_summary_id=rs.id).one_or_none()
    if sts:
        return sts

    laps = session.laps.pick_driver(rs.driver.code)

    df_avg = laps.filter(items=["Sector1Time", "Sector2Time", "Sector3Time"]).mean().round("ms")
    df_fastest = laps.filter(items=["Sector1Time", "Sector2Time", "Sector3Time"]).min().round("ms")

    sts = SectorTimeSummary(
        driver_race_summary_id=rs.id,
        sector_1_average=df_avg["Sector1Time"].to_pytimedelta(),
        sector_2_average=df_avg["Sector2Time"].to_pytimedelta(),
        sector_3_average=df_avg["Sector3Time"].to_pytimedelta(),
        sector_1_fastest=df_fastest["Sector1Time"].to_pytimedelta(),
        sector_2_fastest=df_fastest["Sector2Time"].to_pytimedelta(),
        sector_3_fastest=df_fastest["Sector3Time"].to_pytimedelta(),
    )
    tx.add(sts)
    tx.commit()


def _process_overtakes(tx: Session, session, rs: DriverRaceSummary) -> List[Overtake]:
    sts = tx.query(Overtake).filter_by(driver_race_summary_id=rs.id).all()
    if len(sts) > 0:
        return sts

    threashold = pd.Timedelta(3, "s")
    pit_threashold = pd.Timedelta(3, "s")
    this_driver = rs.driver.driver_number
    driver_ahead = None

    laps = session.laps.pick_driver(this_driver)
    driver_tel = session.laps.pick_driver(this_driver).get_car_data()
    overtakes = []

    for _, lap in laps.iterlaps():
        lap_number = lap["LapNumber"]
        if lap_number == 1:  # exclude first lap
            continue

        # Consider successful overtake as:
        # - driver ahead has changed at t0
        # - passed driver's driver ahead is now the driver's driver ahead any time between t0 + 3 seconds
        # - the driver is ahead by 1 car length
        # - the driver's driver ahead was the passed driver any time between t0 - 3 seconds
        # - driver has driven longer distance since t0 for the entirety of the sample window t0 + 3 seconds
        # - passed driver has not been lapped
        # - passed driver is not pitted
        # - passed driver is not off track
        # Consider adding checks for:
        # - track status (no yellow flags, sc leading to lapped cars making their way around).

        # Currently, if a car is side by side and the driver is slightly in front, gets away for a split second counts as an overtake.
        lap_telemetry = lap.get_car_data().add_driver_ahead()
        for _, t in lap_telemetry.iterrows():
            if driver_ahead == t["DriverAhead"]:
                continue

            maybe_passed_driver = driver_ahead
            driver_ahead = t["DriverAhead"]

            if not maybe_passed_driver:
                continue

            t0 = t["SessionTime"]

            # Passed driver data
            pd_laps = session.laps.pick_driver(maybe_passed_driver)
            pd_lap_idx = pd_laps[(pd_laps["LapStartTime"] <= t0)]["LapStartTime"].idxmax()
            pd_lap = session.laps.iloc[pd_lap_idx]
            pd_pos = pd_laps.get_pos_data().slice_by_time(t0 - threashold, t0 + threashold)
            pd_tel = pd_laps.get_car_data()
            try:
                pd_tel_before = pd_tel[
                    (pd_tel["SessionTime"] >= (t0 - threashold)) & (pd_tel["SessionTime"] < t0)
                ].add_driver_ahead()
                pd_tel_after = (
                    pd_tel[
                        (pd_tel["SessionTime"] >= t0) & (pd_tel["SessionTime"] < (t0 + threashold))
                    ]
                    .add_driver_ahead()
                    .add_distance()
                )
            except (ValueError, IndexError):
                continue

            # Driver data
            try:
                driver_tel_after = (
                    driver_tel[
                        (driver_tel["SessionTime"] >= t0)
                        & (driver_tel["SessionTime"] < (t0 + threashold))
                    ]
                    .add_driver_ahead()
                    .add_distance()
                )
            except ValueError:
                continue

            # Ensure the car is not off track
            if not pd_pos.query(f'Status == "OffTrack"').empty:
                print("off track!!")
                continue

            # Check for possible overtake based on driver ahead during the sample windows
            if not (
                not pd_tel_before.query(f'DriverAhead == "{driver_ahead}"').empty
                and not pd_tel_after.query(f'DriverAhead == "{this_driver}"').empty
            ):
                continue

            # The drive is at least 1 car length ahead (6 meters) at any point in time during t0 + 3 seconds
            if pd_tel_after.query(
                f'DriverAhead == "{this_driver}" and DistanceToDriverAhead >= 6'
            ).empty:
                continue

            # Check passed driver has not been lapped
            if pd_lap["LapNumber"] < lap_number:
                continue

            # Check the driver has driven longer distance since t0
            if not driver_tel_after.iloc[-1]["Distance"] > pd_tel_after.iloc[-1]["Distance"]:
                continue

            # Check passed driver was not pitted
            # This is determined true if t0 does not occur during any PitInTime - 3 second and PitOutTime + 3 second
            # TODO: this could be optimized to filter laps we only care about
            was_pitted = False
            last_pit_in = None
            for _, _pd_lap in pd_laps.iterrows():
                pit_in = _pd_lap["PitInTime"]
                pit_out = _pd_lap["PitOutTime"]

                if last_pit_in and not pd.isnull(pit_out):
                    if t0 >= (last_pit_in - pit_threashold) and t0 <= (pit_out + pit_threashold):
                        was_pitted = True
                        break
                    last_pit_in = None
                if not pd.isnull(pit_in):
                    last_pit_in = pit_in
            if was_pitted:
                continue

            passed_driver_id = (
                tx.query(Driver).filter_by(driver_number=maybe_passed_driver).one().driver_id
            )
            next_driver_id = None
            if driver_ahead:
                next_driver_id = (
                    tx.query(Driver).filter_by(driver_number=driver_ahead).one().driver_id
                )

            overtakes.append(
                Overtake(
                    driver_race_summary_id=rs.id,
                    lap_number=lap_number,
                    passed_driver_id=passed_driver_id,
                    next_driver_ahead_id=next_driver_id,
                )
            )
    tx.add_all(overtakes)
    tx.commit()
    return overtakes


def _get_or_create_race_summary(tx: Session, race: Race, driver: Driver) -> DriverRaceSummary:
    rs = DriverRaceSummary.get_or_create(tx, race_id=race.id, driver_id=driver.driver_id)
    tx.commit()
    return rs


def _get_or_create_race(tx: Session, session, circuit: Circuit, drivers) -> Race:
    event = session.event
    # find session event date
    for i in range(1, 6):
        sn = getattr(event, f"Session{i}")
        if sn == "Race":
            date = getattr(event, f"Session{i}Date").date()
            break
    if date is None:
        raise Exception("Could not find race date from event", event)

    race = Race.get_or_create(
        tx,
        year=date.year,
        round_number=event["RoundNumber"].item(),
        date=date,
        drivers=len(drivers),
        circuit_id=circuit.circuit_id,
    )
    tx.commit()
    return race


def _get_circuit(tx: Session, session) -> Circuit:
    circuit = (
        tx.query(Circuit)
        .filter_by(locality=session.event["Location"], country=session.event["Country"])
        .first()
    )
    if not circuit:
        raise Exception("circuit not found")
    return circuit


def _get_drivers(tx: Session, session) -> Driver:
    session_drivers = pd.unique(session.laps["Driver"]).tolist()
    drivers = tx.query(Driver).filter(Driver.code.in_(session_drivers)).all()
    if len(drivers) != len(session_drivers):
        for d in drivers:
            if d.code in session_drivers:
                session_drivers.remove(d.code)
        raise Exception(f"drivers not found: {session_drivers}")
    return drivers
