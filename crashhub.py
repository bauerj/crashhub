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
@click.option('--dry-run', default=True, help='Don\'t actually change anything.')
def update_posts(dry_run):
    if dry_run:
        print("Dry-run, changes will not be performed.")
    util.update_posts(dry_run)


cli.add_command(update_posts)

if __name__ == "__main__":
    cli()
