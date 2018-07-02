#!/bin/python3
import click

from lib.routes import app
from lib import util


@click.group()
def cli():
    pass


@cli.command()
def run():
    app.run(host="0.0.0.0", port=8000)


@click.command()
@click.option('--no-dry-run', is_flag=True, help='Don\'t actually change anything.')
def update_posts(no_dry_run):
    if not no_dry_run:
        print("Dry-run, changes will not be performed.")
    util.update_posts(not no_dry_run)


cli.add_command(update_posts)

if __name__ == "__main__":
    cli()
