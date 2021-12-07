import csv
import geojson
import requests


def get_modis(region="Global"):
    """
    Hotspots detected by the MODIS satellite in a recent 24-hour period.

    Returns GeoJSON.
    """
    base_url = 'https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_{}_24h.csv'
    url = base_url.format(region)
    features = _get_features(url)


    return geojson.FeatureCollection(features)

def get_viirs_suomi():
    """
    Hotspots detected by the VIIRS Suomi-NPP (S-NPP) satellite in a recent 24-hour period.

    Returns GeoJSON.
    """
    base_url = 'https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_{}'
    url_list = [
        base_url.format('USA_contiguous_and_Hawaii_24h.csv'),
        base_url.format('Alaska_24h.csv')
    ]
    features = [_get_features(u) for u in url_list]
    return geojson.FeatureCollection(_flatten(features))


def get_viirs_noaa():
    """
    Hotspots detected by the VIIRS NOAA-20 satellite in a recent 24-hour period.

    Returns GeoJSON.
    """
    base_url = 'https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_{}'
    url_list = [
        base_url.format('USA_contiguous_and_Hawaii_24h.csv'),
        base_url.format('Alaska_24h.csv')
    ]
    features = [_get_features(u) for u in url_list]
    return geojson.FeatureCollection(_flatten(features))


def _flatten(list_of_lists):
    """
    Flattens the provided list of lists.
    """
    return [val for sublist in list_of_lists for val in sublist]


def _get_features(url):
    """
    Generic function for downloading data from NASA and formatting to geojson
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
