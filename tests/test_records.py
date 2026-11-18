"""Offline tests of the typed hotspot records."""

import csv
import dataclasses
import doctest
from datetime import UTC, datetime
from io import StringIO

import pytest

import nasa_wildfires
from nasa_wildfires import Hotspot, Satellite, records


def first_row(sample_csv, name):
    """Read the first row of a saved sample as a dictionary."""
    return next(csv.DictReader(StringIO(sample_csv(name).decode())))


def test_records_doctests():
    """The examples in the records module's docstrings are correct."""
    assert doctest.testmod(records).failed == 0


def test_modis_record(sample_csv):
    """MODIS rows have a number for confidence and the brightness columns."""
    hotspot = Hotspot.from_row(first_row(sample_csv, "modis.csv"), Satellite.MODIS)
    assert hotspot.latitude == -14.51802
    assert hotspot.longitude == 127.9279
    assert hotspot.brightness == 327.18
    assert hotspot.brightness_2 == 300.26
    assert hotspot.scan == 1.09
    assert hotspot.track == 1.04
    assert hotspot.frp == 19.15
    assert hotspot.confidence_percent == 0
    assert hotspot.confidence_level is None
    assert hotspot.is_daytime is True
    assert hotspot.platform == "Terra"
    assert hotspot.version == "6.1NRT"
    assert hotspot.acquired_at == datetime(2026, 11, 16, 0, 0, tzinfo=UTC)


def test_viirs_record(sample_csv):
    """VIIRS rows have a word for confidence and different brightness columns."""
    hotspot = Hotspot.from_row(
        first_row(sample_csv, "viirs-noaa.csv"), Satellite.VIIRS_NOAA
    )
    assert hotspot.brightness == 367.0
    assert hotspot.brightness_2 == 292.93
    assert hotspot.confidence_percent is None
    assert hotspot.confidence_level == "high"
    assert hotspot.is_daytime is False
    assert hotspot.platform == "NOAA-20"
    assert hotspot.acquired_at == datetime(2026, 11, 16, 0, 2, tzinfo=UTC)


def test_time_is_utc_and_aware(sample_csv):
    """The time carries a UTC zone, so it never gets mistaken for local time."""
    hotspot = Hotspot.from_row(
        first_row(sample_csv, "viirs-noaa21.csv"), Satellite.VIIRS_NOAA21
    )
    assert hotspot.acquired_at.tzinfo is UTC
    assert hotspot.acquired_at.utcoffset().total_seconds() == 0


def test_afternoon_time():
    """A time such as 1437 is read as 14:37."""
    assert records._parse_time("2026-11-17", "1437") == datetime(
        2026, 11, 17, 14, 37, tzinfo=UTC
    )


def test_unknown_satellite_code_is_kept(sample_csv):
    """A satellite code this package has not heard of is passed through."""
    row = first_row(sample_csv, "viirs-noaa21.csv") | {"satellite": "N99"}
    assert Hotspot.from_row(row, Satellite.VIIRS_NOAA21).platform == "N99"


def test_missing_column_is_clear(sample_csv):
    """A missing column is named in the error."""
    row = first_row(sample_csv, "modis.csv")
    del row["frp"]
    with pytest.raises(ValueError, match="frp"):
        Hotspot.from_row(row, Satellite.MODIS)


def test_bad_number_is_clear(sample_csv):
    """A value that is not a number gives a plain error."""
    row = first_row(sample_csv, "modis.csv") | {"scan": "wide"}
    with pytest.raises(ValueError, match="Could not read"):
        Hotspot.from_row(row, Satellite.MODIS)


def test_record_is_frozen(sample_csv):
    """Records cannot be changed after they are made."""
    hotspot = Hotspot.from_row(first_row(sample_csv, "modis.csv"), Satellite.MODIS)
    with pytest.raises(dataclasses.FrozenInstanceError):
        hotspot.frp = 1.0  # type: ignore[misc]


def test_get_hotspot_records(fake_nasa):
    """The download function gives one record per row."""
    fake_nasa.sample = "viirs-noaa21.csv"
    found = nasa_wildfires.get_hotspot_records("viirs-noaa21", region="alaska")
    assert len(found) == 3
    assert all(isinstance(h, Hotspot) for h in found)
    assert fake_nasa.urls[0].endswith("J2_VIIRS_C2_Alaska_24h.csv")


def test_geojson_stays_as_text(fake_nasa):
    """The GeoJSON properties are still NASA's original text."""
    fake_nasa.sample = "modis.csv"
    feature = nasa_wildfires.get_modis()["features"][0]
    assert feature["properties"]["acq_time"] == "0000"
    assert feature["properties"]["confidence"] == "0"


@pytest.mark.parametrize("value", ["x", "", "DN"])
def test_bad_day_night_flag_is_clear(sample_csv, value):
    """A day or night flag that is not D or N is refused, and blank is too."""
    row = first_row(sample_csv, "modis.csv") | {"daynight": value}
    with pytest.raises(ValueError, match="daynight should be D or N"):
        Hotspot.from_row(row, Satellite.MODIS)


def test_day_night_flag_ignores_case_and_spaces(sample_csv):
    """A lowercase flag with stray spaces still reads as night."""
    row = first_row(sample_csv, "modis.csv") | {"daynight": " n "}
    assert Hotspot.from_row(row, Satellite.MODIS).is_daytime is False


def test_word_confidence_is_kept_as_level(sample_csv):
    """A confidence written as a word becomes a level with no percent."""
    row = first_row(sample_csv, "viirs-noaa.csv") | {"confidence": " Nominal "}
    hotspot = Hotspot.from_row(row, Satellite.VIIRS_NOAA)
    assert hotspot.confidence_level == "nominal"
    assert hotspot.confidence_percent is None
