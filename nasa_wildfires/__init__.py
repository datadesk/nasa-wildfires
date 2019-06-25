import csv
import requests
from geojson import Feature, FeatureCollection, Point


def get_modis():
    """
    Download latest 24hr MODIS data. Returns geojson file.
    """
    base_url = 'https://firms.modaps.eosdis.nasa.gov/data/active_fire/c6/csv/{}'
    contiguous_url = 'MODIS_C6_USA_contiguous_and_Hawaii_24h.csv'
    alaska_url = 'MODIS_C6_Alaska_24h.csv'
    return _download_and_format(base_url, contiguous_url, alaska_url, 'MODIS')


def get_viirs():
    """
    Download latest 24hr VIIRS data. Returns geojson file.
    """
    base_url = 'https://firms.modaps.eosdis.nasa.gov/data/active_fire/viirs/csv/VNP14IMGTDL_NRT_{}'
    contiguous_url = 'USA_contiguous_and_Hawaii_24h.csv'
    alaska_url = 'Alaska_24h.csv'
    return _download_and_format(base_url, contiguous_url, alaska_url, 'VIIRS')


def _download_and_format(base_url, contiguous_url, alaska_url, filename):
    """
    Generic function for downloading data from NASA and formatting to geojson
    """
    features = []
    with requests.Session() as s:
        for url in [contiguous_url, alaska_url]:
            download = s.get(base_url.format(url))
            decoded_content = download.content.decode('utf-8')
            cr = csv.DictReader(decoded_content.splitlines(), delimiter=',')
            for r in cr:
                features.append(
                    Feature(
                        geometry=Point((float(r['longitude']), float(r['latitude']))),
                        properties=r
                    )
                )
    return FeatureCollection(features)
