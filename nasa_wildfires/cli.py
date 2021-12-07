import click
import geojson
from nasa_wildfires import get_modis, get_viirs_suomi, get_viirs_noaa


@click.group()
def cmd():
    """
    A command-line interface for downloading wildfire data from NASA satellites.

    Returns GeoJSON.
    """
    pass


@cmd.command(help="Hotspots detected by the MODIS satellite in a recent 24-hour period")
@click.option('--indent', default=0, help='Indentation of output')
@click.option('--sort-keys/--no-sort-keys', default=True, help="Sort the properties keys")
def modis(indent, sort_keys):
    data = get_modis()
    output = geojson.dumps(data, indent=indent, sort_keys=sort_keys)
    click.echo(output)


@cmd.command(help="Hotspots detected by the VIIRS satellite (S-NPP) in a recent 24-hour period")
@click.option('--indent', default=0, help='Indentation of output')
@click.option('--sort-keys/--no-sort-keys', default=True, help="Sort the properties keys")
def viirs_suomi(indent, sort_keys):
    data = get_viirs_suomi()
    output = geojson.dumps(data, indent=indent, sort_keys=sort_keys)
    click.echo(output)

@cmd.command(help="Hotspots detected by the VIIRS satellite (NOAA-20) in a recent 24-hour period")
@click.option('--indent', default=0, help='Indentation of output')
@click.option('--sort-keys/--no-sort-keys', default=True, help="Sort the properties keys")
def viirs_noaa(indent, sort_keys):
    data = get_viirs_noaa()
    output = geojson.dumps(data, indent=indent, sort_keys=sort_keys)
    click.echo(output)



if __name__ == '__main__':
    cmd()
