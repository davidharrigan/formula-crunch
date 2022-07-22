import coloredlogs
import click

from cli.scrape import scrape
from cli.render import render
from cli.db import db

coloredlogs.install(level="INFO", fmt="%(levelname)s %(asctime)s [%(module)s] - %(message)s")


@click.group()
def cli():
    pass


cli.add_command(scrape)
cli.add_command(render)
cli.add_command(db)

if __name__ == "__main__":
    cli()
