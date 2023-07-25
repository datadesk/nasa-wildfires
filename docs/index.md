```{include} _templates/nav.html
```

# nasa-wildfires

Download wildfire hotspots detected by NASA satellites and the [Fire Information for Resource Management System (FIRMS)](https://firms.modaps.eosdis.nasa.gov/active_fire/)

```{contents} Table of contents
:local:
:depth: 2
```

## Installation

```bash
pipenv install nasa-wildfires
```

## Command-line usage

```bash
Usage: nasawildfires [OPTIONS] COMMAND [ARGS]...

  A command-line interface for downloading wildfire data from NASA
  satellites.

  Returns world GeoJSON in a recent 24-hour period. For available regions and time ranges, see options.

Options:
  --help  Show this message and exit.

Commands:
  modis  Hotspots detected by the MODIS satellitel
  viirs_suomi  Hotspots detected by the VIRRS S-NPP satellite.
  viirs_noaa  Hotspots detected by the VIRRS NOAA-20 satellite.
```
Download a GeoJSON of hotspots detected by the MODIS satellite in a recent 24-hour period.

```bash
nasawildfires modis
```

Download a GeoJSON of hotspots detected by the MODIS satellite for USA and Hawaii in a recent 48-hour period.

```bash
nasawildfires modis -r usa-hawaii -t 48h
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
import nasa_wildfires
```

View list of available regions
```python
nasa_wildfires.REGION_LIST
[
    "global",
    "canada",
    "alaska",
    "usa-hawaii",
    "central-america",
    "south-america",
    "europe",
    "north-central-africa",
    "southern-africa",
    "russia-asia",
    "south-asia",
    "southeast-asia",
    "australia-newzealand",
]
```

View list of availabe time ranges
```python
nasa_wildfires.TIME_RANGE_LIST
["24h", "48h", "7d"]
```

Download a GeoJSON of hotspots detected by the MODIS satellite in a recent 24-hour period. Returns GeoJSON.

```python
nasa_wildfires.get_modis()
```

Download a regional GeoJSON of hotspots detected by the MODIS satellite in a recent 24-hour period.

```python
nasa_wildfires.get_modis(region="usa-hawaii")
```

Download a regional GeoJSON of hotspots detected by the MODIS satellite in a recent 7-day period.

```python
nasa_wildfires.get_modis(region="usa-hawaii", time_range="7d")
```

Download a GeoJSON of hotspots detected by the VIIRS S-NPP satellite in a recent 24-hour period. Returns GeoJSON.

```python
nasa_wildfires.get_viirs_suomi()
```

Download a GeoJSON of hotspots detected by the VIIRS NOAA-20 satellite in a recent 24-hour period. Returns GeoJSON.

```python
nasa_wildfires.get_viirs_noaa()
```

## Contributing

Install dependencies for development.

```bash
pipenv install --dev
```

Run tests.

```bash
pipenv run python test.py
```

## Developing the CLI

The command-line interface is implemented using Click and setuptools. To install it locally for development inside your virtual environment, run the following installation command, as [prescribed by the Click documentation](https://click.palletsprojects.com/en/7.x/setuptools/#setuptools-integration).

```bash
pip install --editable .
```

## Links

* Docs: [palewi.re/docs/nasa-wildfires/](https://palewi.re/docs/nasa-wildfires/)
* Issues: [github.com/datadesk/nasa-wildfires/issues](https://github.com/datadesk/nasa-wildfires/issues)
* Packaging: [pypi.python.org/pypi/nasa-wildfires](https://pypi.python.org/pypi/nasa-wildfires)
* Testing: [github.com/datadesk/nasa-wildfires/actions](https://github.com/datadesk/nasa-wildfires/actions)
