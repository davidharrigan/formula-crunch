import logging
import os

import fastf1 as ff1

from sqlalchemy.orm import Session

from scrape import model
from scrape.race import (
    get_lap_summary,
    get_driver_overtakes,
    get_pit_summary,
    get_race,
    get_driver_summary,
    get_stint_summary,
)
from scrape.core import get_session, get_drivers, get_circuits, add_driver_id_or_number
from scrape.data import to_db_fields, get_one_from_df
from scrape.plot import create_fastest_lap_gear_plot


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ff1.Cache.enable_cache(os.path.join(ROOT_DIR, "..", "data", "cache"))


def scrape_drivers(tx: Session, year: int):
    drivers = get_drivers(year).drop(columns="DriverNumber")
    for _, driver in drivers.iterrows():
        existing = tx.query(model.Driver).filter_by(driver_id=driver["DriverID"]).one_or_none()
        if not existing:
            tx.add(model.Driver(**to_db_fields(driver)))
    tx.commit()


def scrape_circuits(tx: Session, year: int):
    circuits = get_circuits(year)
    for _, circuit in circuits.iterrows():
        existing = tx.query(model.Circuit).filter_by(circuit_id=circuit["CircuitID"]).one_or_none()
        if not existing:
            tx.add(model.Circuit(**to_db_fields(circuit)))
    tx.commit()


def scrape_race_data(tx: Session, event, year):
    session = get_session(year, event, "Race")
    session.load(telemetry=True, laps=True, weather=False)

    drivers = get_drivers(year).query("DriverNumber == @session.drivers")
    print(session.event["Location"], session.event.Country)
    circuit = (
        tx.query(model.Circuit)
        .filter_by(locality=session.event["Location"], country=session.event["Country"])
        .one()
    )
    race = _get_or_create_race(tx, session, circuit)
    logging.info("loaded race information")

    logging.info("crunching data...")
    lap_summary = get_lap_summary(session)
    stint_summary = get_stint_summary(session)
    pit_summary, pit_stops = get_pit_summary(session)
    driver_summary_df = get_driver_summary(session)

    logging.info("saving driver data...")
    for _, drv in drivers.iterrows():
        driver_id = drv["DriverID"]
        driver_number = drv["DriverNumber"]

        # race summary
        driver_summary = model.DriverRaceSummary.upsert(
            tx,
            race_id=race.id,
            driver_id=driver_id,
            **to_db_fields(
                get_one_from_df(driver_summary_df, f'DriverNumber == "{driver_number}"').drop(
                    labels="DriverNumber"
                )
            ),
        )
        tx.commit()

        # lap summary
        series = get_one_from_df(lap_summary, f'DriverNumber == "{driver_number}"')
        if series.empty:
            continue
        series = series.drop(labels="DriverNumber")
        model.LapSummary.get_or_create(
            tx, driver_race_summary_id=driver_summary.id, **to_db_fields(series)
        )
        tx.commit()

        # stint summary
        stints = stint_summary[stint_summary["DriverNumber"] == driver_number]
        for _, series in stints.iterrows():
            model.StintSummary.upsert(
                tx,
                driver_race_summary_id=driver_summary.id,
                **to_db_fields(series.drop(labels="DriverNumber")),
            )
            tx.commit()

        # pit summary
        series = get_one_from_df(pit_summary, f'DriverID == "{driver_id}"')
        if not series.empty:
            series = series.drop(labels=["TotalStops", "DriverID"])
        driver_pit_summary = model.PitSummary.get_or_create(
            tx, driver_race_summary_id=driver_summary.id, **to_db_fields(series)
        )
        tx.commit()

        # pit stops
        df = pit_stops.query(f'DriverID == "{driver_id}"')
        if not df.empty:
            df = df.drop(columns=["DriverID", "PitDate", "Time"])
        for _, p in df.iterrows():
            model.PitStop.get_or_create(tx, pit_summary_id=driver_pit_summary.id, **to_db_fields(p))
        tx.commit()

        # overtakes
        df = get_driver_overtakes(session, driver_number)
        for _, o in df.iterrows():
            passed_driver = o["DriverNumberAgainst"]
            o["PassedDriverID"] = get_one_from_df(drivers, f'DriverNumber == "{passed_driver}"')[
                "DriverID"
            ]
            model.Overtake.get_or_create(
                tx,
                driver_race_summary_id=driver_summary.id,
                **to_db_fields(o.drop(labels=["DriverNumberAgainst", "DriverNumber"])),
            )
        tx.commit()

        # gear shifts
        create_fastest_lap_gear_plot(session, race.year, race.circuit_id, driver_number, driver_id)

    logging.info("done!")


def _get_or_create_race(
    tx: Session, session: ff1.core.Session, circuit: model.Circuit
) -> model.Race:
    fields = to_db_fields(get_race(session))
    race = model.Race.get_or_create(tx, circuit_id=circuit.circuit_id, **fields)
    tx.commit()
    return race
