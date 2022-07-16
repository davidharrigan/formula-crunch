import logging

import coloredlogs
import click

from cmd.scrape import scrape
from cmd.render import render
from cmd.db import db

coloredlogs.install(
    level='DEBUG',
    fmt='%(levelname)s %(asctime)s [%(module)s] - %(message)s')


@click.group()
def cli():
    pass


cli.add_command(scrape)
cli.add_command(render)
cli.add_command(db)

if __name__ == '__main__':
    cli()
