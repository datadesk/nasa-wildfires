from enum import StrEnum

REGION_DICT = {
    "global": "Global",
    "canada": "Canada",
    "alaska": "Alaska",
    "usa-hawaii": "USA_contiguous_and_Hawaii",
    "central-america": "Central_America",
    "south-america": "South_America",
    "europe": "Europe",
    "north-central-africa": "Northern_and_Central_Africa",
    "southern-africa": "Southern_Africa",
    "russia-asia": "Russia_Asia",
    "south-asia": "South_Asia",
    "southeast-asia": "SouthEast_Asia",
    "australia-newzealand": "Australia_NewZealand",
}

TIME_RANGE_LIST = ["24h", "48h", "7d"]


class Satellite(StrEnum):
    """A satellite instrument whose fire detections NASA FIRMS publishes.

    Each member's value is the short name used on the command line.

    Examples:
        >>> Satellite("viirs-noaa21")
        <Satellite.VIIRS_NOAA21: 'viirs-noaa21'>
        >>> Satellite.MODIS.csv_path("Global", "24h")
        'modis-c6.1/csv/MODIS_C6_1_Global_24h.csv'
    """

    MODIS = "modis"
    VIIRS_SUOMI = "viirs-suomi"
    VIIRS_NOAA = "viirs-noaa"
    VIIRS_NOAA21 = "viirs-noaa21"

    @property
    def label(self) -> str:
        """A plain-language name for the satellite and instrument.

        Returns:
            The name, such as "VIIRS NOAA-20".

        Examples:
            >>> Satellite.VIIRS_NOAA.label
            'VIIRS NOAA-20'
        """
        return _SATELLITE_LABELS[self]

    def csv_path(self, region_name: str, time_range: str) -> str:
        """Build the path of NASA's CSV file for this satellite.

        Args:
            region_name: NASA's name for the region, which is a value of
                ``REGION_DICT``, such as "USA_contiguous_and_Hawaii".
            time_range: One of ``TIME_RANGE_LIST``, such as "24h".

        Returns:
            The path of the file, relative to NASA's active fire data folder.

        Examples:
            >>> Satellite.VIIRS_NOAA21.csv_path("Alaska", "7d")
            'noaa-21-viirs-c2/csv/J2_VIIRS_C2_Alaska_7d.csv'
        """
        folder, prefix = _SATELLITE_FILES[self]
        return f"{folder}/csv/{prefix}_{region_name}_{time_range}.csv"


_SATELLITE_LABELS = {
    Satellite.MODIS: "MODIS",
    Satellite.VIIRS_SUOMI: "VIIRS Suomi-NPP",
    Satellite.VIIRS_NOAA: "VIIRS NOAA-20",
    Satellite.VIIRS_NOAA21: "VIIRS NOAA-21",
}

_SATELLITE_FILES = {
    Satellite.MODIS: ("modis-c6.1", "MODIS_C6_1"),
    Satellite.VIIRS_SUOMI: ("suomi-npp-viirs-c2", "SUOMI_VIIRS_C2"),
    Satellite.VIIRS_NOAA: ("noaa-20-viirs-c2", "J1_VIIRS_C2"),
    Satellite.VIIRS_NOAA21: ("noaa-21-viirs-c2", "J2_VIIRS_C2"),
}

SATELLITE_LIST = [s.value for s in Satellite]
