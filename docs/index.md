# nasa-wildfires

Download wildfire hotspots detected by NASA satellites and the [Fire Information for Resource Management System (FIRMS)](https://firms.modaps.eosdis.nasa.gov/active_fire/)

```{contents} Table of contents
:local:
:depth: 2
```

## Read this first

**A hotspot is a heat spot seen by a satellite. It is not a confirmed wildfire.**

The satellites only see heat. Many of the spots they report are wildfires, but the list also includes:

* Industrial flares, such as the ones burning off gas at oil and gas fields and refineries.
* Gas burning at landfills, mines and factories.
* Fires lit on purpose, such as prescribed burns and the burning of crop fields.
* Volcanoes, and other hot ground.
* Some false alarms, especially the detections NASA marks with low confidence.

One fire can show up as many hotspots, because each one covers a small patch of ground. A fire can also be missed, for example under thick cloud or when no satellite passes overhead. Check a hotspot against other sources before you call it a wildfire.

## Installation

```bash
uv add nasa-wildfires
```

## Quick start

From the shell, print GeoJSON for the whole world in the last 24 hours.

```bash
nasawildfires modis > modis.json
```

From Python, ask for typed records and read their fields.

```python
import nasa_wildfires

for hotspot in nasa_wildfires.get_hotspot_records("viirs-noaa21", region="alaska"):
    print(hotspot.acquired_at, hotspot.latitude, hotspot.longitude, hotspot.frp)
```

## Satellites

NASA publishes detections from two kinds of instrument. MODIS sees patches of ground about 1 kilometer across. VIIRS is newer and sees patches about 375 meters across, so it picks up smaller fires.

| Short name | Instrument and satellite | Python value |
| --- | --- | --- |
| `modis` | MODIS on the Terra and Aqua satellites | `Satellite.MODIS` |
| `viirs-suomi` | VIIRS on Suomi-NPP (S-NPP), decommissioned and empty | `Satellite.VIIRS_SUOMI` |
| `viirs-noaa` | VIIRS on NOAA-20 | `Satellite.VIIRS_NOAA` |
| `viirs-noaa21` | VIIRS on NOAA-21 | `Satellite.VIIRS_NOAA21` |

```{warning}
The Suomi-NPP satellite has been decommissioned. NASA's Suomi-NPP files now have a header and no rows, in every region and time range, so `viirs-suomi` and `get_viirs_suomi` give you an empty result, not an error. They are kept so older code keeps running. For current VIIRS hotspots, use `viirs-noaa` (NOAA-20) or `viirs-noaa21` (NOAA-21).
```

## Regions and time ranges

Pick a region with `region` in Python or `-r` on the command line. The default is `global`.

| Region | NASA's name |
| --- | --- |
| `global` | Global |
| `canada` | Canada |
| `alaska` | Alaska |
| `usa-hawaii` | USA contiguous and Hawaii |
| `central-america` | Central America |
| `south-america` | South America |
| `europe` | Europe |
| `north-central-africa` | Northern and Central Africa |
| `southern-africa` | Southern Africa |
| `russia-asia` | Russia and Asia |
| `south-asia` | South Asia |
| `southeast-asia` | Southeast Asia |
| `australia-newzealand` | Australia and New Zealand |

Pick a time range with `time_range` or `-t`. The default is `24h`.

| Time range | What you get |
| --- | --- |
| `24h` | The last 24 hours |
| `48h` | The last 48 hours |
| `7d` | The last 7 days |

The lists are also in the code as `nasa_wildfires.REGION_LIST`, `nasa_wildfires.TIME_RANGE_LIST` and `nasa_wildfires.SATELLITE_LIST`.

## Command-line usage

```bash
Usage: nasawildfires [OPTIONS] COMMAND [ARGS]...

  A command-line interface for downloading wildfire data from NASA
  satellites.

  Returns GeoJSON.

Options:
  --help  Show this message and exit.

Commands:
  hotspots      Hotspots detected by any satellite, chosen with --satellite
  modis         Hotspots detected by the MODIS satellite
  viirs-noaa    Hotspots detected by the VIIRS satellite (NOAA-20)
  viirs-noaa21  Hotspots detected by the VIIRS satellite (NOAA-21)
  viirs-suomi   Hotspots detected by the VIIRS satellite (S-NPP)
```

Every command prints GeoJSON and takes the same options.

| Option | What it does |
| --- | --- |
| `-r`, `--region` | The region to download. The default is `global`. |
| `-t`, `--time-range` | `24h`, `48h` or `7d`. The default is `24h`. |
| `--indent INTEGER` | How many spaces to indent the output. |
| `--sort-keys / --no-sort-keys` | Sort the properties keys. The default is to sort them. |
| `--timeout FLOAT` | Seconds to wait for NASA on each try. The default is 60. |
| `--verbose` | Print each request to standard error. |

Examples:

```bash
# MODIS hotspots for the world in the last 24 hours
nasawildfires modis

# MODIS hotspots for the United States and Hawaii in the last 48 hours
nasawildfires modis -r usa-hawaii -t 48h

# VIIRS NOAA-20 and NOAA-21 hotspots for Canada in the last 7 days
nasawildfires viirs-noaa -r canada -t 7d > noaa20.json
nasawildfires viirs-noaa21 -r canada -t 7d > noaa21.json

# The same thing, choosing the satellite with an option
nasawildfires hotspots --satellite viirs-noaa21 --region canada --time-range 7d --indent 2
```

A failure prints one line starting with `Error:` and exits with code 1.

## Python usage

Import the package.

```python
import nasa_wildfires
```

### GeoJSON

`get_hotspots` works for any satellite and returns a GeoJSON feature collection. Each feature is a point, and its properties are NASA's columns exactly as NASA wrote them, as text.

```python
data = nasa_wildfires.get_hotspots("viirs-noaa21")
data = nasa_wildfires.get_hotspots("modis", region="usa-hawaii", time_range="7d")
data = nasa_wildfires.get_hotspots(nasa_wildfires.Satellite.VIIRS_NOAA)
```

The older functions still work and give the same results.

```python
nasa_wildfires.get_modis()
nasa_wildfires.get_viirs_suomi(region="alaska")
nasa_wildfires.get_viirs_noaa(region="alaska", time_range="48h")
nasa_wildfires.get_viirs_noaa21()
```

### Typed records

`get_hotspot_records` returns a list of `Hotspot` objects instead. The numbers are already numbers, and the date and time are combined into one `acquired_at` time in UTC that carries its time zone.

```python
records = nasa_wildfires.get_hotspot_records("modis", region="alaska")
hotspot = records[0]
hotspot.acquired_at  # datetime.datetime(2026, 11, 16, 0, 0, tzinfo=datetime.timezone.utc)
hotspot.platform  # "Terra"
hotspot.frp  # 19.15
```

### Errors and retries

Each request waits at most 60 seconds for NASA. A request that cannot reach NASA, times out, or gets a server error (status 500 and up) or "too many requests" (429) is tried again, up to four tries in all, with a longer pause each time. NASA publishes every file on two domains, `firms` and `firms2`, and the tries take turns between them. Other errors, such as "not found", fail right away.

When it still fails, the package raises `nasa_wildfires.NASAError`, which carries the `url` and the `status_code`. If NASA's file arrives but cannot be read, it raises `nasa_wildfires.NASADataError`, which is also a `ValueError`.

```python
try:
    data = nasa_wildfires.get_hotspots("modis", timeout=30)
except nasa_wildfires.NASAError as error:
    print(error)
```

### Use your own request function

Some projects send every web request through their own helper, for shared retries, logging or proxy settings. Pass that helper as `get` and the package will use it instead of `requests.get`. It is called like `get(url, timeout=seconds)` and must return something with a `status_code` and the file's `content` as bytes. The timeout, the retries and the switching between NASA's two domains all still work, and failures still raise `NASAError`.

```python
import requests

import nasa_wildfires
from nasa_wildfires import Reply


def my_get(url: str, *, timeout: float) -> Reply:
    print("Asking for", url)
    return requests.get(url, timeout=timeout, headers={"User-Agent": "my-project"})


data = nasa_wildfires.get_hotspots("modis", get=my_get)
```

The `Fetcher` and `Reply` types describe this, so a type checker can confirm your function fits. If your function raises one of the `requests` library's errors, such as a timeout, the package tries again just as it does for its own requests. Any other error is passed on to you.

## Field reference

These are the columns NASA publishes, with the matching `Hotspot` field. MODIS and VIIRS use slightly different columns.

| NASA column | `Hotspot` field | What it means |
| --- | --- | --- |
| `latitude`, `longitude` | `latitude`, `longitude` | The center of the patch of ground that looked hot, in degrees. Latitude is negative in the south and longitude is negative in the west. |
| `brightness` (MODIS) or `bright_ti4` (VIIRS) | `brightness` | How hot the spot looked in the main heat channel, as a brightness temperature in kelvin. Higher is hotter. It is not the temperature of the fire itself, because the fire fills only part of the patch. |
| `bright_t31` (MODIS) or `bright_ti5` (VIIRS) | `brightness_2` | A second brightness reading from a longer wavelength, in kelvin. It mostly shows the temperature of the surroundings, and scientists compare it with the first reading. |
| `scan` | `scan` | How wide the patch is across the satellite's path, in kilometers. Patches are larger toward the edge of the satellite's view. |
| `track` | `track` | How tall the patch is along the satellite's path, in kilometers. |
| `acq_date`, `acq_time` | `acquired_at` | When the satellite saw the spot. The date is `YYYY-MM-DD` and the time is `HHMM`, both in UTC. The record joins them into one time. |
| `satellite` | `platform` | The satellite: `T` is Terra, `A` is Aqua, `N` is Suomi-NPP, `N20` is NOAA-20 and `N21` is NOAA-21. A code this package does not know is kept as NASA wrote it. |
| `confidence` | `confidence_percent` or `confidence_level` | How sure NASA is that the spot is a real hot spot. For MODIS it is a number from 0 to 100, and NASA treats 0 to 29 as low, 30 to 79 as nominal and 80 to 100 as high. For VIIRS it is a word: `low`, `nominal` or `high`. Only one of the two fields is filled in. |
| `version` | `version` | NASA's processing version, such as `6.1NRT`. NRT means near real time: the numbers come out within hours and may be refined later. |
| `frp` | `frp` | Fire radiative power, in megawatts. It is a measure of how much heat the fire gives off, and a rough sign of how big and intense it is. Spots with a very small value can be weak fires or false alarms. |
| `daynight` | `is_daytime` | `D` (true) if the satellite passed over in daylight, `N` (false) if at night. Daytime detections can be more likely to be false alarms from sunlit bare ground, and nighttime ones are easier to see. |

The record also has `satellite`, the `Satellite` value you asked for.

## Acknowledgement

NASA asks that anyone who provides FIRMS data to a third party includes this acknowledgement:

> We acknowledge the use of data and/or imagery from NASA's Fire Information for Resource Management System (FIRMS) (https://earthdata.nasa.gov/firms), part of NASA's Land, Atmosphere Near real-time Capability for Earth observations (LANCE) (https://earthdata.nasa.gov/lance) and NASA's Earth Science Data and Information System (ESDIS).

The text comes from [NASA's FIRMS page](https://www.earthdata.nasa.gov/data/tools/firms).

## Data terms

NASA supports full and open sharing of its data. The data is provided "as is", and users bear all responsibility and liability for their use of it. Read the disclaimer on [NASA's FIRMS page](https://www.earthdata.nasa.gov/data/tools/firms) before you publish anything built on it. This package only downloads the data. It is not made by NASA and is not endorsed by NASA.

## About this package

AI tools assisted in writing this package's code, tests and documentation. A person directed and reviewed the work.

## Contributing

Install dependencies for development.

```bash
uv sync --all-groups
```

Run the offline tests, the linter and the type checker.

```bash
make check
```

The tests also measure test coverage, counting branches, and fail if it drops below 95%. Run `make test-fast` for a quicker run without coverage.

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
