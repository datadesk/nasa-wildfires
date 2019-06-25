import click
from nasa_wildfires import get_modis, get_viirs


@click.group()
def cmd():
    """
    A command-line interface for downloading wildfire data from NASA satellites.

    Returns GeoJSON.
    """
    pass


@cmd.command(help="Hotspots detected by the MODIS satellite in a recent 24-hour period")
def modis():
    click.echo(get_modis())


@cmd.command(help="Hotspots detected by the VIRRS satellite in a recent 24-hour period")
def viirs():
    click.echo(get_viirs())


if __name__ == '__main__':
    cli()
