import click
import logging
from datetime import date

from sqlalchemy.orm import Session

from scrape.scrape import (
    scrape_drivers,
    scrape_circuits,
    scrape_race_data,
)
from scrape.db import create_connection
from scrape.core.schedule import get_schedule


@click.group()
def scrape():
    pass


@scrape.command()
@click.option("--year", default="current", help="scrape driver data for this year")
def drivers(year):
    if not year or year == "current":
        year = date.today().year
    conn = create_connection()
    with Session(conn) as tx:
        scrape_drivers(tx, year)


@scrape.command()
@click.option("--year", default="current", help="scrape circuit data for this year")
def circuits(year):
    if not year or year == "current":
        year = date.today().year
    conn = create_connection()
    with Session(conn) as tx:
        scrape_circuits(tx, year)


# TODO: get the latest event by default
@scrape.command()
@click.option("--event", required=True, help="circuit name or country name")
@click.option("--year", default="current", help="scrape race data for this year")
def race(event, year):
    if not year or year == "current":
        year = date.today().year

    conn = create_connection()
    with Session(conn) as tx:
        scrape_race_data(tx, event, year)


@scrape.command()
@click.option("--year", default="current", help="scrape race data for this year")
def all_races(year):
    if not year or year == "current":
        year = date.today().year

    events = get_schedule(year)
    conn = create_connection()

    with Session(conn) as tx:
        for _, event in events.iterrows():
            if event["Date"] <= date.today():
                logging.info(f"scrape {event['Locality']}")
                scrape_race_data(tx, event["Locality"], year)
