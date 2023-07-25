"""Methods for downloading and processing wildfire data from NASA FIRMS."""
from __future__ import annotations

import csv
import random

import geojson
import requests
from retry import retry

from .options import REGION_DICT

REGION_LIST = list(REGION_DICT.keys())


def get_modis(
    region: str = "global", time_range: str = "24h", verbose: bool = False
) -> geojson.FeatureCollection:
    """Hotspots detected by the MODIS satellite.

    Defaults to the world in a recent 24-hour period.

    Args:
        region: The region to download. Defaults to "global".
        time_range: The time range to download. Defaults to "24h".
        verbose: Print verbose output. Defaults to False.

    Returns GeoJSON.
    """
    name = REGION_DICT[region]
    csv_path = f"modis-c6.1/csv/MODIS_C6_1_{name}_{time_range}.csv"
    features = _get_features(csv_path, verbose=verbose)
    return geojson.FeatureCollection(features)


def get_viirs_suomi(
    region: str = "global", time_range: str = "24h", verbose: bool = False
) -> geojson.FeatureCollection:
    """Hotspots detected by the VIIRS Suomi-NPP (S-NPP) satellite.

    Defaults to the world in a recent 24-hour period.

    Args:
        region: The region to download. Defaults to "global".
        time_range: The time range to download. Defaults to "24h".
        verbose: Print verbose output. Defaults to False.

    Returns GeoJSON.
    """
    name = REGION_DICT[region]
    csv_path = f"suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_{name}_{time_range}.csv"
    features = _get_features(csv_path, verbose=verbose)
    return geojson.FeatureCollection(features)


def get_viirs_noaa(
    region: str = "global", time_range: str = "24h", verbose: bool = False
) -> geojson.FeatureCollection:
    """Hotspots detected by the VIIRS NOAA-20 satellite.

    Defaults to the world in a recent 24-hour period.

    Returns GeoJSON.
    """
    name = REGION_DICT[region]
    csv_path = f"noaa-20-viirs-c2/csv/J1_VIIRS_C2_{name}_{time_range}.csv"
    features = _get_features(csv_path, verbose=verbose)
    return geojson.FeatureCollection(features)


@retry((AssertionError), delay=4, tries=3, backoff=2, jitter=1)
def _get_features(csv_path: str, verbose: bool = False) -> list[geojson.Feature]:
    """Download CSV hotspots CSVs from NASA and reformat as GeoJSON.

    Args:
        csv_path: The path to the CSV file to download.
        verbose: Print verbose output. Defaults to False.

    Returns GeoJSON.
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
        raise AssertionError(f"Request failed with status code {r.status_code}")

    # Read in the CSV
    decoded_content = r.content.decode("utf-8")
    reader = csv.DictReader(decoded_content.splitlines(), delimiter=",")

    # Convert to GeoJSON
    features = []
    for row in reader:
        coords = map(float, [row["longitude"], row["latitude"]])
        f = geojson.Feature(geometry=geojson.Point(coords), properties=row)
        features.append(f)

    # Return the GeoJSON feature list
    return features
