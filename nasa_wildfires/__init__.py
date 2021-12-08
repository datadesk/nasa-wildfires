import csv
import geojson
import requests
from .options import REGION_DICT, TIME_RANGE

REGION_LIST = list(REGION_DICT.keys())
TIME_LIST = TIME_RANGE


def get_modis(region="global", time="24h"):
    """
    Hotspots detected by the MODIS satellite. Defaults to the world in a recent 24-hour period.

    Returns GeoJSON.
    """
    base_url = 'https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_{}_{}.csv'
    name = REGION_DICT[region]
    url = base_url.format(name, time)
    features = _get_features(url)
    return geojson.FeatureCollection(features)


def get_viirs_suomi(region="global", time="24h"):
    """
    Hotspots detected by the VIIRS Suomi-NPP (S-NPP) satellite. Defaults to the world in a recent 24-hour period.

    Returns GeoJSON.
    """
    base_url = 'https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_{}_{}.csv'
    name = REGION_DICT[region]
    url = base_url.format(name, time)
    features = _get_features(url)
    return geojson.FeatureCollection(features)


def get_viirs_noaa(region="global", time="24h"):
    """
    Hotspots detected by the VIIRS NOAA-20 satellite. Defaults to the world in a recent 24-hour period.

    Returns GeoJSON.
    """
    base_url = 'https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_{}_{}.csv'
    name = REGION_DICT[region]
    url = base_url.format(name, time)
    features = _get_features(url)
    return geojson.FeatureCollection(features)


def _get_features(url):
    """
    Generic function for downloading data from NASA and reformatting as GeoJSON.
    """
    download = requests.get(url)
    decoded_content = download.content.decode('utf-8')
    reader = csv.DictReader(decoded_content.splitlines(), delimiter=',')
    features = []
    for r in reader:
        coords = map(float, [r['longitude'], r['latitude']])
        f = geojson.Feature(
            geometry=geojson.Point(coords),
            properties=r
        )
        features.append(f)
    return features
