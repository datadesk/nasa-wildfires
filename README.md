Download wildfire data from NASA satellites

Hourly scrapes powered by a GitHub Action are stored in the `data` directory.

## Installation

```bash
pipenv install nasa-wildfires
```

## Command-line usage

```bash
Usage: nasawildfires [OPTIONS] COMMAND [ARGS]...

  A command-line interface for downloading wildfire data from NASA
  satellites.

  Returns world GeoJSON. For regional GeoJSON see options.

Options:
  --help  Show this message and exit.

Commands:
  modis  Hotspots detected by the MODIS satellite in a recent 24-hour period
  viirs_suomi  Hotspots detected by the VIRRS S-NPP satellite in a recent 24-hour period
  viirs_noaa  Hotspots detected by the VIRRS NOAA-20 satellite in a recent 24-hour period
```

Download a GeoJSON of hotspots detected by the MODIS satellite in a recent 24-hour period.

```bash
nasawildfires modis
```

Download a GeoJSON of hotspots detected by the VIIRS S-NPP satellite in a recent 24-hour period.

```bash
nasawildfires viirs-suomi
```

Download a GeoJSON of hotspots detected by the VIIRS NOAA-20 satellite in a recent 24-hour period.

```bash
nasawildfires viirs-noaa
```

## Python usage

Import the library.

```python
>>> import nasa_wildfires
```

View list of available regions
```python
>>> nasa_wildfires.REGION_LIST
['global', 'canada', 'alaska', 'usa-hawaii', 'central-america', 'south-america', 'europe', 'north-central-africa', 'southern-africa', 'russia-asia', 'south-asia', 'southeast-asia', 'australia-newzealand']
```

Download a GeoJSON of hotspots detected by the MODIS satellite in a recent 24-hour period. Returns GeoJSON.

```python
>>> data = nasa_wildfires.get_modis()
```

Download a regional GeoJSON of hotspots detected by the MODIS satellite in a recent 24-hour period.

```python
>>> data = nasa_wildfires.get_modis('usa-hawaii')
```

Download a GeoJSON of hotspots detected by the VIIRS S-NPP satellite in a recent 24-hour period. Returns GeoJSON.

```python
>>> data = nasa_wildfires.get_viirs_suomi()
```

Download a GeoJSON of hotspots detected by the VIIRS NOAA-20 satellite in a recent 24-hour period. Returns GeoJSON.

```python
>>> data = nasa_wildfires.get_viirs_noaa()
```

## Contributing

Install dependencies for development.

```bash
pipenv install --dev
```

Run tests.

```bash
make test
```

Shipping new version to PyPI.

```bash
make ship
```

## Developing the CLI

The command-line interface is implemented using Click and setuptools. To install it locally for development inside your virtual environment, run the following installation command, as [prescribed by the Click documentation](https://click.palletsprojects.com/en/7.x/setuptools/#setuptools-integration).

```bash
pip install --editable .
```
