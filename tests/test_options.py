"""Offline checks of the region and time range options."""

from nasa_wildfires import REGION_LIST, Satellite, options


def test_region_list_matches_options():
    """The public region list is the keys of the options table."""
    assert REGION_LIST == list(options.REGION_DICT)
    assert "global" in REGION_LIST


def test_time_ranges():
    """The three time ranges NASA publishes are offered."""
    assert options.TIME_RANGE_LIST == ["24h", "48h", "7d"]


def test_satellite_labels():
    """Every satellite has a plain-language name."""
    assert Satellite.VIIRS_NOAA.label == "VIIRS NOAA-20"
    assert all(satellite.label for satellite in Satellite)
