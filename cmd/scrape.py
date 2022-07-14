import click

from scrape.drivers import scrape_drivers


@click.group()
def scrape():
    pass


@scrape.command()
@click.option('--year', default='current', help='scrape driver data for this year')
def drivers(year):
    scrape_drivers(year)
