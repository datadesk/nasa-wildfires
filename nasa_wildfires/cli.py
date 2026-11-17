"""The nasawildfires command-line interface."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import click
import geojson

from nasa_wildfires import NASAError, get_hotspots, options
from nasa_wildfires.fetch import DEFAULT_TIMEOUT
from nasa_wildfires.options import Satellite


def _common_options(func: Callable[..., Any]) -> Callable[..., Any]:
    """Add the options every download command shares.

    Args:
        func: The click command function to decorate.

    Returns:
        The same function with the region, time range, indent, sort keys and
        verbose options attached.
    """
    decorators = [
        click.option(
            "-r",
            "--region",
            default="Global",
            type=click.Choice(list(options.REGION_DICT.keys()), case_sensitive=False),
            help="Hotspot region",
        ),
        click.option(
            "-t",
            "--time-range",
            default="24h",
            type=click.Choice(options.TIME_RANGE_LIST, case_sensitive=False),
            help="Time range",
        ),
        click.option("--indent", default=0, help="Indentation of output"),
        click.option(
            "--sort-keys/--no-sort-keys",
            default=True,
            help="Sort the properties keys",
        ),
        click.option(
            "--timeout",
            default=DEFAULT_TIMEOUT,
            show_default=True,
            type=click.FloatRange(min=1),
            help="Seconds to wait for NASA on each try",
        ),
        click.option("--verbose", is_flag=True, help="Print each request to stderr"),
    ]
    for decorator in reversed(decorators):
        func = decorator(func)
    return func


def _download(
    satellite: Satellite,
    region: str,
    time_range: str,
    indent: int,
    sort_keys: bool,
    timeout: float,
    verbose: bool,
) -> None:
    """Download hotspots and print them as GeoJSON.

    Args:
        satellite: The satellite to download.
        region: The region to download.
        time_range: The time range to download.
        indent: How many spaces to indent the output.
        sort_keys: Whether to sort the properties keys.
        timeout: Seconds to wait for NASA on each try.
        verbose: Whether to print each request to standard error.

    Raises:
        click.ClickException: If NASA cannot be reached or sends back an error,
            so the command prints one line starting with "Error:" and exits
            with code 1.
    """
    try:
        data = get_hotspots(satellite, region, time_range, verbose, timeout)
    except NASAError as error:
        raise click.ClickException(str(error)) from error
    output = geojson.dumps(data, indent=indent, sort_keys=sort_keys)
    click.echo(output)


@click.group()
def cmd() -> None:
    """
    A command-line interface for downloading wildfire data from NASA satellites.

    Returns GeoJSON.
    """
    pass


@cmd.command(help="Hotspots detected by the MODIS satellite in a recent 24-hour period")
@_common_options
def modis(region, time_range, indent, sort_keys, timeout, verbose):
    _download(Satellite.MODIS, region, time_range, indent, sort_keys, timeout, verbose)


@cmd.command(
    help="Hotspots detected by the VIIRS satellite (S-NPP) in a recent 24-hour period"
)
@_common_options
def viirs_suomi(region, time_range, indent, sort_keys, timeout, verbose):
    _download(
        Satellite.VIIRS_SUOMI, region, time_range, indent, sort_keys, timeout, verbose
    )


@cmd.command(
    help="Hotspots detected by the VIIRS satellite (NOAA-20) in a recent 24-hour period"
)
@_common_options
def viirs_noaa(region, time_range, indent, sort_keys, timeout, verbose):
    _download(
        Satellite.VIIRS_NOAA, region, time_range, indent, sort_keys, timeout, verbose
    )


@cmd.command(
    help="Hotspots detected by the VIIRS satellite (NOAA-21) in a recent 24-hour period"
)
@_common_options
def viirs_noaa21(region, time_range, indent, sort_keys, timeout, verbose):
    _download(
        Satellite.VIIRS_NOAA21, region, time_range, indent, sort_keys, timeout, verbose
    )


@cmd.command(help="Hotspots detected by any satellite, chosen with --satellite")
@click.option(
    "-s",
    "--satellite",
    required=True,
    type=click.Choice(options.SATELLITE_LIST, case_sensitive=False),
    help="Satellite to download",
)
@_common_options
def hotspots(satellite, region, time_range, indent, sort_keys, timeout, verbose):
    _download(
        Satellite(satellite.lower()),
        region,
        time_range,
        indent,
        sort_keys,
        timeout,
        verbose,
    )


if __name__ == "__main__":
    cmd()
