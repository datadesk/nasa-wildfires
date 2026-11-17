"""Methods for downloading and processing wildfire data from NASA FIRMS."""

from __future__ import annotations

import geojson

from .errors import NASADataError, NASAError
from .fetch import DEFAULT_TIMEOUT, Fetcher, Reply, download_rows
from .options import REGION_DICT, SATELLITE_LIST, TIME_RANGE_LIST, Satellite
from .records import Hotspot

REGION_LIST = list(REGION_DICT.keys())

__all__ = [
    "REGION_LIST",
    "NASADataError",
    "NASAError",
    "Fetcher",
    "Reply",
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
    timeout: float = DEFAULT_TIMEOUT,
    *,
    get: Fetcher | None = None,
) -> geojson.FeatureCollection:
    """Hotspots detected by any satellite that NASA FIRMS publishes.

    Defaults to the world in a recent 24-hour period.

    Args:
        satellite: The satellite to download, as a ``Satellite`` or its short
            name, such as "modis", "viirs-suomi", "viirs-noaa" or
            "viirs-noaa21".
        region: The region to download. Defaults to "global".
        time_range: The time range to download. Defaults to "24h".
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for NASA on each try. Defaults to 60.
        get: A function that makes the web request, such as ``requests.get``
            (the default). Pass your own to add retries, logging or custom
            headers. It is called as ``get(url, timeout=seconds)``.

    Returns:
        A GeoJSON feature collection with one point for each hotspot.

    Raises:
        NASAError: If NASA cannot be reached after several tries, or answers
            with an error.

    Examples:
        >>> import nasa_wildfires
        >>> data = nasa_wildfires.get_hotspots("viirs-noaa21", region="alaska")
        >>> data = nasa_wildfires.get_hotspots(
        ...     nasa_wildfires.Satellite.MODIS, time_range="7d"
        ... )
        >>> data = nasa_wildfires.get_hotspots("modis", get=my_get)
    """
    satellite = Satellite(satellite)
    name = REGION_DICT[region]
    csv_path = satellite.csv_path(name, time_range)
    features = _get_features(csv_path, verbose=verbose, timeout=timeout, get=get)
    return geojson.FeatureCollection(features)


def get_hotspot_records(
    satellite: Satellite | str,
    region: str = "global",
    time_range: str = "24h",
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    *,
    get: Fetcher | None = None,
) -> list[Hotspot]:
    """Hotspots from any satellite, as typed records instead of GeoJSON.

    Each record has numbers already parsed and one timezone-aware UTC
    ``acquired_at`` time. See ``Hotspot`` for every field.

    Args:
        satellite: The satellite to download, as a ``Satellite`` or its short
            name.
        region: The region to download. Defaults to "global".
        time_range: The time range to download. Defaults to "24h".
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for NASA on each try. Defaults to 60.
        get: A function that makes the web request, such as ``requests.get``
            (the default). Pass your own to add retries, logging or custom
            headers. It is called as ``get(url, timeout=seconds)``.

    Returns:
        A list of ``Hotspot`` records, one for each detection.

    Raises:
        NASAError: If NASA cannot be reached after several tries, or answers
            with an error.
        NASADataError: If a row from NASA is missing a column or has a value
            that cannot be read. This is also a ``ValueError``.

    Examples:
        >>> import nasa_wildfires
        >>> records = nasa_wildfires.get_hotspot_records("modis", region="alaska")
        >>> for hotspot in records:
        ...     print(hotspot.acquired_at, hotspot.latitude, hotspot.frp)
        >>> records = nasa_wildfires.get_hotspot_records("modis", get=my_get)
    """
    satellite = Satellite(satellite)
    csv_path = satellite.csv_path(REGION_DICT[region], time_range)
    rows = download_rows(csv_path, verbose=verbose, timeout=timeout, get=get)
    try:
        return [Hotspot.from_row(row, satellite) for row in rows]
    except ValueError as error:
        raise NASADataError(str(error)) from error


def get_modis(
    region: str = "global",
    time_range: str = "24h",
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    *,
    get: Fetcher | None = None,
) -> geojson.FeatureCollection:
    """Hotspots detected by the MODIS satellite.

    Defaults to the world in a recent 24-hour period.

    Args:
        region: The region to download. Defaults to "global".
        time_range: The time range to download. Defaults to "24h".
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for NASA on each try. Defaults to 60.
        get: A function that makes the web request, such as ``requests.get``
            (the default). Pass your own to add retries, logging or custom
            headers. It is called as ``get(url, timeout=seconds)``.

    Returns:
        A GeoJSON feature collection with one point for each hotspot.

    Examples:
        >>> data = get_modis(region="usa-hawaii", time_range="48h")
        >>> data = get_modis(get=my_get)
    """
    return get_hotspots(Satellite.MODIS, region, time_range, verbose, timeout, get=get)


def get_viirs_suomi(
    region: str = "global",
    time_range: str = "24h",
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    *,
    get: Fetcher | None = None,
) -> geojson.FeatureCollection:
    """Hotspots detected by the VIIRS Suomi-NPP (S-NPP) satellite.

    The Suomi-NPP satellite has been decommissioned. NASA's files for it have
    a header and no rows, so this returns an empty feature collection. It is
    kept so older code keeps running. Use `get_viirs_noaa` or `get_hotspots`
    with "viirs-noaa21" for current data.

    Defaults to the world in a recent 24-hour period.

    Args:
        region: The region to download. Defaults to "global".
        time_range: The time range to download. Defaults to "24h".
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for NASA on each try. Defaults to 60.
        get: A function that makes the web request, such as ``requests.get``
            (the default). Pass your own to add retries, logging or custom
            headers. It is called as ``get(url, timeout=seconds)``.

    Returns:
        A GeoJSON feature collection with one point for each hotspot.

    Examples:
        >>> data = get_viirs_suomi(region="canada")
    """
    return get_hotspots(
        Satellite.VIIRS_SUOMI, region, time_range, verbose, timeout, get=get
    )


def get_viirs_noaa(
    region: str = "global",
    time_range: str = "24h",
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    *,
    get: Fetcher | None = None,
) -> geojson.FeatureCollection:
    """Hotspots detected by the VIIRS NOAA-20 satellite.

    Defaults to the world in a recent 24-hour period.

    Args:
        region: The region to download. Defaults to "global".
        time_range: The time range to download. Defaults to "24h".
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for NASA on each try. Defaults to 60.
        get: A function that makes the web request, such as ``requests.get``
            (the default). Pass your own to add retries, logging or custom
            headers. It is called as ``get(url, timeout=seconds)``.

    Returns:
        A GeoJSON feature collection with one point for each hotspot.

    Examples:
        >>> data = get_viirs_noaa(region="europe", time_range="7d")
    """
    return get_hotspots(
        Satellite.VIIRS_NOAA, region, time_range, verbose, timeout, get=get
    )


def get_viirs_noaa21(
    region: str = "global",
    time_range: str = "24h",
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    *,
    get: Fetcher | None = None,
) -> geojson.FeatureCollection:
    """Hotspots detected by the VIIRS NOAA-21 satellite.

    Defaults to the world in a recent 24-hour period.

    Args:
        region: The region to download. Defaults to "global".
        time_range: The time range to download. Defaults to "24h".
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for NASA on each try. Defaults to 60.
        get: A function that makes the web request, such as ``requests.get``
            (the default). Pass your own to add retries, logging or custom
            headers. It is called as ``get(url, timeout=seconds)``.

    Returns:
        A GeoJSON feature collection with one point for each hotspot.

    Examples:
        >>> data = get_viirs_noaa21(region="australia-newzealand")
    """
    return get_hotspots(
        Satellite.VIIRS_NOAA21, region, time_range, verbose, timeout, get=get
    )


def _get_features(
    csv_path: str,
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    *,
    get: Fetcher | None = None,
) -> list[geojson.Feature]:
    """Download one of NASA's hotspot CSV files and reformat it as GeoJSON.

    Args:
        csv_path: The path to the CSV file to download.
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for NASA on each try. Defaults to 60.
        get: A function that makes the web request, such as ``requests.get``
            (the default). Pass your own to add retries, logging or custom
            headers. It is called as ``get(url, timeout=seconds)``.
        timeout: Seconds to wait for NASA on each try. Defaults to 60.
        get: A function that makes the web request, such as ``requests.get``
            (the default). Pass your own to add retries, logging or custom
            headers. It is called as ``get(url, timeout=seconds)``.

    Returns:
        One GeoJSON point feature for each row, with the row's columns as
        properties.
    """
    features = []
    for row in download_rows(csv_path, verbose=verbose, timeout=timeout, get=get):
        coords = map(float, [row["longitude"], row["latitude"]])
        f = geojson.Feature(geometry=geojson.Point(coords), properties=row)
        features.append(f)
    return features
