"""Methods for downloading and processing wildfire data from NASA FIRMS."""

from __future__ import annotations

import csv
import random

import geojson
import requests
from retry import retry

from .options import REGION_DICT, SATELLITE_LIST, TIME_RANGE_LIST, Satellite
from .records import Hotspot

REGION_LIST = list(REGION_DICT.keys())

__all__ = [
    "REGION_LIST",
    "SATELLITE_LIST",
    "Hotspot",
    "TIME_RANGE_LIST",
    "Satellite",
    "get_hotspot_records",
    "get_hotspots",
    "get_modis",
    "get_viirs_noaa",
    "get_viirs_noaa21",
    "get_viirs_suomi",
]


def get_hotspots(
    satellite: Satellite | str,
    region: str = "global",
    time_range: str = "24h",
    verbose: bool = False,
) -> geojson.FeatureCollection:
    """Hotspots detected by any satellite that NASA FIRMS publishes.

    Defaults to the world in a recent 24-hour period.

    Args:
        satellite: The satellite to download, as a ``Satellite`` or its short
            name, such as "modis", "viirs-suomi", "viirs-noaa" or
            "viirs-noaa21".
        region: The region to download. Defaults to "global".
        time_range: The time range to download. Defaults to "24h".
        verbose: Print verbose output. Defaults to False.

    Returns:
        A GeoJSON feature collection with one point for each hotspot.

    Examples:
        >>> import nasa_wildfires
        >>> data = nasa_wildfires.get_hotspots("viirs-noaa21", region="alaska")
        >>> data = nasa_wildfires.get_hotspots(
        ...     nasa_wildfires.Satellite.MODIS, time_range="7d"
        ... )
    """
    satellite = Satellite(satellite)
    name = REGION_DICT[region]
    csv_path = satellite.csv_path(name, time_range)
    features = _get_features(csv_path, verbose=verbose)
    return geojson.FeatureCollection(features)


def get_hotspot_records(
    satellite: Satellite | str,
    region: str = "global",
    time_range: str = "24h",
    verbose: bool = False,
) -> list[Hotspot]:
    """Hotspots from any satellite, as typed records instead of GeoJSON.

    Each record has numbers already parsed and one timezone-aware UTC
    ``acquired_at`` time. See ``Hotspot`` for every field.

    Args:
        satellite: The satellite to download, as a ``Satellite`` or its short
            name.
        region: The region to download. Defaults to "global".
        time_range: The time range to download. Defaults to "24h".
        verbose: Print verbose output. Defaults to False.

    Returns:
        A list of ``Hotspot`` records, one for each detection.

    Raises:
        ValueError: If a row from NASA is missing a column or has a value that
            cannot be read.

    Examples:
        >>> import nasa_wildfires
        >>> records = nasa_wildfires.get_hotspot_records("modis", region="alaska")
        >>> for hotspot in records:
        ...     print(hotspot.acquired_at, hotspot.latitude, hotspot.frp)
    """
    satellite = Satellite(satellite)
    csv_path = satellite.csv_path(REGION_DICT[region], time_range)
    rows = _get_rows(csv_path, verbose=verbose)
    return [Hotspot.from_row(row, satellite) for row in rows]


def get_modis(
    region: str = "global", time_range: str = "24h", verbose: bool = False
) -> geojson.FeatureCollection:
    """Hotspots detected by the MODIS satellite.

    Defaults to the world in a recent 24-hour period.

    Args:
        region: The region to download. Defaults to "global".
        time_range: The time range to download. Defaults to "24h".
        verbose: Print verbose output. Defaults to False.

    Returns:
        A GeoJSON feature collection with one point for each hotspot.

    Examples:
        >>> data = get_modis(region="usa-hawaii", time_range="48h")
    """
    return get_hotspots(Satellite.MODIS, region, time_range, verbose)


def get_viirs_suomi(
    region: str = "global", time_range: str = "24h", verbose: bool = False
) -> geojson.FeatureCollection:
    """Hotspots detected by the VIIRS Suomi-NPP (S-NPP) satellite.

    Defaults to the world in a recent 24-hour period.

    Args:
        region: The region to download. Defaults to "global".
        time_range: The time range to download. Defaults to "24h".
        verbose: Print verbose output. Defaults to False.

    Returns:
        A GeoJSON feature collection with one point for each hotspot.

    Examples:
        >>> data = get_viirs_suomi(region="canada")
    """
    return get_hotspots(Satellite.VIIRS_SUOMI, region, time_range, verbose)


def get_viirs_noaa(
    region: str = "global", time_range: str = "24h", verbose: bool = False
) -> geojson.FeatureCollection:
    """Hotspots detected by the VIIRS NOAA-20 satellite.

    Defaults to the world in a recent 24-hour period.

    Args:
        region: The region to download. Defaults to "global".
        time_range: The time range to download. Defaults to "24h".
        verbose: Print verbose output. Defaults to False.

    Returns:
        A GeoJSON feature collection with one point for each hotspot.

    Examples:
        >>> data = get_viirs_noaa(region="europe", time_range="7d")
    """
    return get_hotspots(Satellite.VIIRS_NOAA, region, time_range, verbose)


def get_viirs_noaa21(
    region: str = "global", time_range: str = "24h", verbose: bool = False
) -> geojson.FeatureCollection:
    """Hotspots detected by the VIIRS NOAA-21 satellite.

    Defaults to the world in a recent 24-hour period.

    Args:
        region: The region to download. Defaults to "global".
        time_range: The time range to download. Defaults to "24h".
        verbose: Print verbose output. Defaults to False.

    Returns:
        A GeoJSON feature collection with one point for each hotspot.

    Examples:
        >>> data = get_viirs_noaa21(region="australia-newzealand")
    """
    return get_hotspots(Satellite.VIIRS_NOAA21, region, time_range, verbose)


@retry((AssertionError), delay=4, tries=3, backoff=2, jitter=1)
def _get_rows(csv_path: str, verbose: bool = False) -> list[dict[str, str]]:
    """Download one of NASA's hotspot CSV files and read its rows.

    Args:
        csv_path: The path to the CSV file to download.
        verbose: Print verbose output. Defaults to False.

    Returns:
        One dictionary of column names to text for each row.
    """
    domain_list = [
        "firms.modaps.eosdis.nasa.gov",
        "firms2.modaps.eosdis.nasa.gov",
    ]
    domain = random.choice(domain_list)
    base_url = f"https://{domain}/data/active_fire/"
    url = f"{base_url}{csv_path}"

    # Get the URL
    if verbose:
        print(f"Requesting {url}")
    r = requests.get(url)

    # Make sure it came back kosher
    try:
        assert r.ok
    except AssertionError:
        raise AssertionError(
            f"Request failed with status code {r.status_code}"
        ) from None

    # Read in the CSV
    decoded_content = r.content.decode("utf-8")
    reader = csv.DictReader(decoded_content.splitlines(), delimiter=",")
    return list(reader)


def _get_features(csv_path: str, verbose: bool = False) -> list[geojson.Feature]:
    """Download one of NASA's hotspot CSV files and reformat it as GeoJSON.

    Args:
        csv_path: The path to the CSV file to download.
        verbose: Print verbose output. Defaults to False.

    Returns:
        One GeoJSON point feature for each row, with the row's columns as
        properties.
    """
    features = []
    for row in _get_rows(csv_path, verbose=verbose):
        coords = map(float, [row["longitude"], row["latitude"]])
        f = geojson.Feature(geometry=geojson.Point(coords), properties=row)
        features.append(f)
    return features
