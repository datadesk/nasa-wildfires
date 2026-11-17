"""Offline tests of the download functions and the command line."""

import geojson
import pytest
from click.testing import CliRunner

import nasa_wildfires
from nasa_wildfires import Satellite
from nasa_wildfires.cli import cmd

SAMPLES = {
    Satellite.MODIS: "modis.csv",
    Satellite.VIIRS_SUOMI: "viirs-suomi.csv",
    Satellite.VIIRS_NOAA: "viirs-noaa.csv",
    Satellite.VIIRS_NOAA21: "viirs-noaa21.csv",
}
PATHS = {
    Satellite.MODIS: "modis-c6.1/csv/MODIS_C6_1_Global_24h.csv",
    Satellite.VIIRS_SUOMI: "suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Global_24h.csv",
    Satellite.VIIRS_NOAA: "noaa-20-viirs-c2/csv/J1_VIIRS_C2_Global_24h.csv",
    Satellite.VIIRS_NOAA21: "noaa-21-viirs-c2/csv/J2_VIIRS_C2_Global_24h.csv",
}


@pytest.mark.parametrize("satellite", list(Satellite))
def test_get_hotspots(fake_nasa, satellite):
    """Every satellite asks for its own file and returns a feature collection."""
    fake_nasa.sample = SAMPLES[satellite]
    data = nasa_wildfires.get_hotspots(satellite)
    assert isinstance(data, geojson.FeatureCollection)
    assert len(data["features"]) >= 1
    assert fake_nasa.urls[0].split("/data/active_fire/")[1] == PATHS[satellite]
    feature = data["features"][0]
    assert feature["geometry"]["type"] == "Point"
    assert "acq_date" in feature["properties"]


def test_short_name_and_region(fake_nasa):
    """A short name works, and the region and time range reach the address."""
    fake_nasa.sample = "viirs-noaa21.csv"
    nasa_wildfires.get_hotspots("viirs-noaa21", region="alaska", time_range="7d")
    assert fake_nasa.urls[0].endswith("noaa-21-viirs-c2/csv/J2_VIIRS_C2_Alaska_7d.csv")


def test_coordinates_are_longitude_then_latitude(fake_nasa):
    """GeoJSON points put longitude first."""
    fake_nasa.sample = "viirs-noaa21.csv"
    first = nasa_wildfires.get_viirs_noaa21()["features"][0]
    assert first["geometry"]["coordinates"] == [-155.29007, 19.40542]


def test_empty_file(fake_nasa):
    """A file with only a header gives an empty collection."""
    fake_nasa.sample = "empty.csv"
    assert nasa_wildfires.get_modis()["features"] == []


@pytest.mark.parametrize(
    ("func", "satellite"),
    [
        (nasa_wildfires.get_modis, Satellite.MODIS),
        (nasa_wildfires.get_viirs_suomi, Satellite.VIIRS_SUOMI),
        (nasa_wildfires.get_viirs_noaa, Satellite.VIIRS_NOAA),
        (nasa_wildfires.get_viirs_noaa21, Satellite.VIIRS_NOAA21),
    ],
)
def test_old_functions_match_new_one(fake_nasa, func, satellite):
    """The old functions give the same answer as get_hotspots."""
    fake_nasa.sample = SAMPLES[satellite]
    assert func("canada", "48h") == nasa_wildfires.get_hotspots(
        satellite, "canada", "48h"
    )


@pytest.mark.parametrize(
    "args",
    [
        ["modis"],
        ["viirs-suomi"],
        ["viirs-noaa"],
        ["viirs-noaa21"],
        ["hotspots", "--satellite", "viirs-noaa21"],
    ],
)
def test_cli_prints_geojson(fake_nasa, args):
    """Every command prints a GeoJSON feature collection."""
    fake_nasa.sample = "modis.csv"
    result = CliRunner().invoke(
        cmd, [*args, "-r", "alaska", "-t", "48h", "--indent", "2"]
    )
    assert result.exit_code == 0, result.output
    assert geojson.loads(result.output)["type"] == "FeatureCollection"
    assert fake_nasa.urls[0].endswith("_Alaska_48h.csv")


def test_cli_hotspots_needs_a_satellite():
    """The generic command refuses to run without --satellite."""
    result = CliRunner().invoke(cmd, ["hotspots"])
    assert result.exit_code == 2
