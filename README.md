# nasa-wildfires

Download wildfire hotspots detected by NASA satellites, from the [Fire Information for Resource Management System (FIRMS)](https://firms.modaps.eosdis.nasa.gov/active_fire/), as GeoJSON or typed Python records.

**A hotspot is a heat spot seen by a satellite. It is not a confirmed wildfire.** Industrial flares, gas burning, fires lit on purpose and some false alarms show up too.

## Install

```sh
uv add nasa-wildfires
```

## Use it from the command line

```sh
nasawildfires modis > modis.json
nasawildfires viirs-noaa21 -r alaska -t 48h
nasawildfires hotspots --satellite viirs-noaa --region canada --time-range 7d
```

The commands are `modis`, `viirs-suomi`, `viirs-noaa`, `viirs-noaa21` and `hotspots`. Regions are `global`, `canada`, `alaska`, `usa-hawaii` and nine more. Time ranges are `24h`, `48h` and `7d`.

## Use it from Python

```python
import nasa_wildfires

data = nasa_wildfires.get_hotspots("viirs-noaa21", region="alaska")  # GeoJSON
records = nasa_wildfires.get_hotspot_records("modis", time_range="7d")  # typed records
print(records[0].acquired_at, records[0].frp)
```

`get_modis`, `get_viirs_suomi` and `get_viirs_noaa` still work. The Suomi-NPP satellite has been decommissioned, so `get_viirs_suomi` and the `viirs-suomi` command now return no hotspots. Use NOAA-20 or NOAA-21 instead.

## Use your own request function

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

## Working on the code

This repository's full history is about 19 GB, because the scraped data files were saved to it for years. Copy only the latest version:

```bash
git clone --depth 1 https://github.com/datadesk/nasa-wildfires.git
```

The automated checks do the same, so the version number comes from a tag only on a tagged release.

## Things to know

* **Detections are not confirmed wildfires.** The documentation explains each column, including `confidence` and `frp` (fire radiative power, in megawatts).
* **Downloads retry.** A request waits 60 seconds, then tries again on network errors and server errors, and raises `nasa_wildfires.NASAError` if it still fails.
* **The data comes from NASA.** It is shared under NASA's full and open data policy and is provided "as is". The code is MIT.
* **Acknowledge NASA.** NASA asks you to include its FIRMS acknowledgement when you share the data. The text is in the documentation.
* **AI helped write this package.** AI tools assisted in writing its code, tests and documentation. A person directed and reviewed the work.

The documentation has the full field reference, the list of regions and the acknowledgement text.

### Links

* Docs: [palewi.re/docs/nasa-wildfires/](https://palewi.re/docs/nasa-wildfires/)
* Issues: [github.com/datadesk/nasa-wildfires/issues](https://github.com/datadesk/nasa-wildfires/issues)
* Packaging: [pypi.python.org/pypi/nasa-wildfires](https://pypi.python.org/pypi/nasa-wildfires)
* Testing: [github.com/datadesk/nasa-wildfires/actions](https://github.com/datadesk/nasa-wildfires/actions)
