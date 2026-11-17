"""Offline checks of the region and time range options."""

from nasa_wildfires import REGION_LIST, options


def test_region_list_matches_options():
    """The public region list is the keys of the options table."""
    assert REGION_LIST == list(options.REGION_DICT)
    assert "global" in REGION_LIST


def test_time_ranges():
    """The three time ranges NASA publishes are offered."""
    assert options.TIME_RANGE_LIST == ["24h", "48h", "7d"]
