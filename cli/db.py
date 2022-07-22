import click
from datetime import date

from scrape.db import create_connection
from scrape.model import Base


@click.group()
def db():
    pass


@db.command()
def create_tables():
    conn = create_connection()
    Base.metadata.create_all(conn)


@db.command()
def drop_all_tables():
    conn = create_connection()
    Base.metadata.drop_all(conn)
