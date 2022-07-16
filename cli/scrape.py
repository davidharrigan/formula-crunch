import click
from datetime import date

import sqlalchemy
from scrape.drivers import scrape_drivers


@click.group()
def scrape():
    pass


@scrape.command()
@click.option('--year', default='current', help='scrape driver data for this year')
@click.option('--force', default=False, is_flag=True, help='overwrite cached data from API')
def drivers(year, force):
    if not year or year == 'current':
        year = date.today().year
    scrape_drivers(year, force)
