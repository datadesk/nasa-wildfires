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

  Returns GeoJSON.

Options:
  --help  Show this message and exit.

Commands:
  modis  Hotspots detected by the MODIS satellite in a recent 24-hour period
  viirs  Hotspots detected by the VIRRS satellite in a recent 24-hour period
```

Download a GeoJSON of hotspots detected by the MODIS satellite in a recent 24-hour period.

```bash
nasawildfires modis
```

Download a GeoJSON of hotspots detected by the VIIRS satellite in a recent 24-hour period.

```bash
nasawildfires viirs
```

## Python usage

Import the library.

```python
>>> import nasa_wildfires
```

Download a GeoJSON of hotspots detected by the MODIS satellite in a recent 24-hour period. Returns GeoJSON.

```python
>>> data = nasa_wildfires.get_modis()
```

Download a GeoJSON of hotspots detected by the VIIRS satellite in a recent 24-hour period. Returns GeoJSON.

```python
>>> data = nasa_wildfires.get_modis()
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
