import click
from nasa_wildfires import get_modis, get_viirs


@click.group()
def cmd():
    """
    A command-line interface for downloading wildfire data from NASA satellites.

    Returns GeoJSON.
    """
    pass


@cmd.command(help="Wildfires spotted in the last 24 hours by the MODIS satellite")
def modis():
    click.echo(get_modis())


@cmd.command(help="Wildfires spotted in the last 24 hours by the VIRRS satellite")
def viirs():
    click.echo(get_viirs())


if __name__ == '__main__':
    cli()
