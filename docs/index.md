# nasa-wildfires

Download wildfire hotspots detected by NASA satellites and the [Fire Information for Resource Management System (FIRMS)](https://firms.modaps.eosdis.nasa.gov/active_fire/)

```{contents} Table of contents
:local:
:depth: 2
```

## Installation

```bash
uv add nasa-wildfires
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
  hotspots      Hotspots detected by any satellite, chosen with --satellite
  modis         Hotspots detected by the MODIS satellite
  viirs-noaa    Hotspots detected by the VIIRS satellite (NOAA-20)
  viirs-noaa21  Hotspots detected by the VIIRS satellite (NOAA-21)
  viirs-suomi   Hotspots detected by the VIIRS satellite (S-NPP)
```

Download a GeoJSON of hotspots detected by the VIIRS NOAA-21 satellite in a recent 24-hour period.

```bash
nasawildfires viirs-noaa21
```

Pick the satellite with an option instead.

```bash
nasawildfires hotspots --satellite viirs-noaa21 --region alaska --time-range 7d
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

Download hotspots from the VIIRS NOAA-21 satellite. Returns GeoJSON.

```python
nasa_wildfires.get_viirs_noaa21()
```

Or use one function for any satellite. The satellite can be a short name or a `nasa_wildfires.Satellite` value.

```python
nasa_wildfires.get_hotspots("viirs-noaa21", region="alaska", time_range="7d")
nasa_wildfires.get_hotspots(nasa_wildfires.Satellite.MODIS)
nasa_wildfires.SATELLITE_LIST
["modis", "viirs-suomi", "viirs-noaa", "viirs-noaa21"]
```

## Contributing

Install dependencies for development.

```bash
uv sync --all-groups
```

Run the offline tests, the linter and the type checker.

```bash
make check
```

The tests that call NASA's real website are skipped by default. Run them with `make test-live`.

## Developing the CLI

The command-line interface is implemented using Click. `uv sync` installs the package in editable form, so the `nasawildfires` command is ready to use with `uv run`.

```bash
uv run nasawildfires --help
```

## Other resources

* Issues: [github.com/datadesk/nasa-wildfires/issues](https://github.com/datadesk/nasa-wildfires/issues)
* Packaging: [pypi.python.org/pypi/nasa-wildfires](https://pypi.python.org/pypi/nasa-wildfires)
* Testing: [github.com/datadesk/nasa-wildfires/actions](https://github.com/datadesk/nasa-wildfires/actions)
