import click

from cmd.scrape import scrape
from cmd.render import render


@click.group()
def cli():
    pass


cli.add_command(scrape)
cli.add_command(render)

if __name__ == '__main__':
    cli()
